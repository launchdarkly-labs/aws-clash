#!/usr/bin/env python3
"""
LaunchDarkly Setup Verification Script

Verifies LaunchDarkly AI Experimentation setup by checking:
- API tokens and SDK keys
- AI Config with variations
- Tool definitions
- Metrics tracking (tokens, duration, success)
- Targeting rules
- Experiments

Usage:
    python verify_launchdarkly_setup.py                    # Use .env file
    python verify_launchdarkly_setup.py --verbose          # Show detailed output
    python verify_launchdarkly_setup.py --project my-proj  # Override project
"""

import os
import sys
import json
import argparse
import requests
import time
from enum import Enum
from dataclasses import dataclass
from typing import Dict, List

# Load .env file if python-dotenv is installed
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass


class Status(Enum):
    """Check status indicators"""
    PASS = "✅"
    FAIL = "❌"
    WARN = "⚠️"


@dataclass
class Check:
    """Result of a verification check"""
    name: str           # Display name with section number
    status: Status      # Pass/Fail/Warning
    message: str        # Human-readable result
    points: int         # Points earned (0 if failed)
    details: Dict = None  # Additional info for verbose mode


class Verifier:
    """Verifies LaunchDarkly setup via REST API"""

    API_BASE = "https://app.launchdarkly.com/api/v2"

    def __init__(self, api_token: str, project: str, env: str, ai_config: str, verbose: bool = False):
        self.project = project
        self.env = env
        self.ai_config = ai_config
        self.verbose = verbose
        self.headers = {"Authorization": api_token, "Content-Type": "application/json"}
        self.results: List[Check] = []

    def _api(self, method: str, endpoint: str, **kwargs) -> tuple[int, Dict]:
        """Make API request and return (status_code, json_data)"""
        try:
            r = requests.request(method, f"{self.API_BASE}{endpoint}", headers=self.headers, **kwargs)
            return r.status_code, r.json() if r.content else {}
        except Exception as e:
            return 0, {"error": str(e)}

    def _check(self, name: str, status: Status, message: str, points: int, details: Dict = None):
        """Record a check result"""
        self.results.append(Check(name, status, message, points, details))

    # ========================================================================
    # STEP 1: Account Setup
    # ========================================================================

    def check_api_token(self):
        """[1b] Verify API token has correct permissions"""
        code, data = self._api("GET", "/tokens")

        if code == 200 and data.get("items"):
            self._check("[1b] API Token", Status.PASS, "API token is valid", 10,
                       {"count": len(data["items"])})
        elif code == 200:
            self._check("[1b] API Token", Status.WARN, "Token works but no items returned", 5)
        else:
            self._check("[1b] API Token", Status.FAIL, f"Invalid token (HTTP {code})", 0,
                       {"error": data.get("error", "Unknown")})

    def check_sdk_key(self):
        """[1c] Verify SDK key exists for the environment"""
        code, data = self._api("GET", f"/projects/{self.project}/environments/{self.env}")

        if code == 200 and data.get("apiKey", "").startswith("sdk-"):
            self._check("[1c] SDK Key", Status.PASS,
                       f"SDK key found for '{self.env}'", 10,
                       {"key": data["apiKey"][:15] + "..."})
        elif code == 200:
            self._check("[1c] SDK Key", Status.WARN, "Key found but invalid format", 5)
        else:
            self._check("[1c] SDK Key", Status.FAIL, f"Not found (HTTP {code})", 0)

    # ========================================================================
    # STEP 2: AI Config
    # ========================================================================

    def check_ai_config(self):
        """[2a] Verify AI Config exists with correct mode"""
        code, data = self._api("GET", f"/projects/{self.project}/ai-configs/{self.ai_config}")

        if code != 200:
            self._check("[2a] AI Config", Status.FAIL, f"Not found (HTTP {code})", 0)
            return

        name = data.get("name", data.get("key"))
        mode = data.get("mode")
        var_count = len(data.get("variations", []))

        if mode in ["agent", "completion", "judge"]:
            self._check("[2a] AI Config", Status.PASS,
                       f"Config '{name}' found with mode '{mode}' and {var_count} variation(s)", 15,
                       {"name": name, "mode": mode, "variations": var_count})
        else:
            self._check("[2a] AI Config", Status.WARN,
                       f"Config found but mode is '{mode}'", 10, {"mode": mode})

    def check_variations(self):
        """[2a] Verify variations have required fields (model, instructions/messages, tools)"""
        code, data = self._api("GET", f"/projects/{self.project}/ai-configs/{self.ai_config}",
                              params={"expand": "variations"})

        if code != 200:
            self._check("[2a] Variations", Status.FAIL, f"Cannot retrieve (HTTP {code})", 0)
            return

        config_name = data.get("name", self.ai_config)
        variations = data.get("variations", [])

        if not variations:
            self._check("[2a] Variations", Status.FAIL, f"Config '{config_name}' has no variations", 0)
            return

        # Check each variation for required fields
        var_details = []
        issues = []

        for v in variations:
            name = v.get("name", v.get("key"))
            missing = []

            # Required: model, instructions OR messages, at least one tool
            if not v.get("modelConfigKey"):
                missing.append("model")
            if not v.get("instructions") and not v.get("messages"):
                missing.append("instructions or messages")
            if len(v.get("tools", [])) == 0:
                missing.append("at least one tool")

            var_details.append({
                "name": name,
                "tools": len(v.get("tools", [])),
                "missing": missing
            })

            if missing:
                issues.append(f"'{name}' missing: {', '.join(missing)}")

        # Award points based on completeness
        if len(variations) >= 2 and not issues:
            # Perfect: 2+ complete variations for A/B testing
            summary = ", ".join([f"{v['name']} ({v['tools']} tools)" for v in var_details])
            self._check("[2a] Variations (2+)", Status.PASS,
                       f"Config '{config_name}' has {len(variations)} complete variations: {summary}", 20,
                       {"config": config_name, "variations": var_details})
        elif len(variations) == 1 and not issues:
            # Partial credit: 1 complete variation
            v = var_details[0]
            self._check("[2a] Variations (1)", Status.PASS,
                       f"Config '{config_name}' has 1 complete variation: {v['name']} ({v['tools']} tools). Add another for A/B testing!", 10,
                       {"config": config_name, "variations": var_details})
        else:
            # Has variations but incomplete
            self._check("[2a] Variations", Status.WARN,
                       f"Config '{config_name}' has {len(variations)} variation(s) but: {'; '.join(issues)}", 5,
                       {"config": config_name, "variations": var_details})

    # ========================================================================
    # STEP 2B: Tools (Optional for Bedrock Agents)
    # ========================================================================

    def check_tools(self):
        """[2b] Verify tool definitions exist in LaunchDarkly library"""
        code, data = self._api("GET", f"/projects/{self.project}/ai-tools")

        if code == 200 and data.get("items"):
            tools = data["items"]
            # Tool name can be None, so use key as fallback
            names = [t.get("name") or t.get("key") for t in tools]
            self._check("[2b] Tool Definitions", Status.PASS,
                       f"Found {len(tools)} tool(s): {', '.join(names)}", 10,
                       {"count": len(tools), "tools": names})
        else:
            # Not an error - Bedrock Agents use Action Groups instead
            self._check("[2b] Tool Definitions", Status.FAIL,
                       "No tools found (OK if using Bedrock Action Groups)", 0)

    # ========================================================================
    # STEP 3 & 5: Agent Code Instrumentation & Metrics
    # ========================================================================

    def check_metrics_tracking(self):
        """[3/5] Verify agent is tracking metrics (tokens, duration, success) using track_tokens() and track_duration_of()"""
        code, data = self._api("GET", f"/metrics/{self.project}")

        if code != 200:
            self._check("[3/5] Agent Instrumentation", Status.FAIL,
                       f"Cannot retrieve metrics (HTTP {code})", 0)
            return

        # Look for AI metrics that should exist if agent is instrumented
        metrics = {
            "input_tokens": None,
            "output_tokens": None,
            "total_tokens": None,
            "duration": None,
            "success": None
        }

        for m in data.get("items", []):
            key = m.get("key", "")
            last_seen = m.get("lastSeen")

            if "ai-input-tokens" in key:
                metrics["input_tokens"] = last_seen
            elif "ai-output-tokens" in key:
                metrics["output_tokens"] = last_seen
            elif "ai-total-tokens" in key:
                metrics["total_tokens"] = last_seen
            elif "ai-completion-duration" in key and "p9" not in key:  # Exclude p95/p99
                metrics["duration"] = last_seen
            elif "ai-completion-success" in key:
                metrics["success"] = last_seen

        tracked = {k: v for k, v in metrics.items() if v is not None}

        if len(tracked) >= 3:
            # Check if metrics have recent activity (last 24 hours)
            now = time.time() * 1000
            recent_threshold = 24 * 60 * 60 * 1000
            recent = [k for k, v in tracked.items() if (now - v) < recent_threshold]

            if recent:
                self._check("[3/5] Agent Instrumentation", Status.PASS,
                           f"Tracking {len(tracked)}/5 metrics ({len(recent)} recent). Using track_duration_of() and track_tokens().", 20,
                           {"tracked": list(tracked.keys()), "recent": recent})
            else:
                self._check("[3/5] Agent Instrumentation", Status.WARN,
                           f"Metrics exist ({len(tracked)}/5) but no recent activity. Run test queries.", 10,
                           {"tracked": list(tracked.keys())})
        else:
            self._check("[3/5] Agent Instrumentation", Status.FAIL,
                       f"Only {len(tracked)}/5 metrics tracked. Add tracker.track_tokens() and tracker.track_duration_of() to agent code.", 0,
                       {"tracked": list(tracked.keys())})

    def check_ai_config_metrics(self):
        """[5] Verify AI Config has generation metrics (requires agent usage)"""
        # Get last 24 hours of metrics
        now = int(time.time() * 1000)
        from_time = now - (24 * 60 * 60 * 1000)

        code, data = self._api("GET",
            f"/projects/{self.project}/ai-configs/{self.ai_config}/metrics?from={from_time}&to={now}&env={self.env}")

        if code != 200:
            self._check("[5] Metrics Collection", Status.FAIL,
                       f"Cannot retrieve AI Config metrics (HTTP {code})", 0)
            return

        generations = data.get("generationCount", 0)
        success = data.get("generationSuccessCount", 0)
        tokens = data.get("totalTokens", 0)
        duration = data.get("durationMs", 0)

        if generations > 0:
            self._check("[5] Metrics Collection", Status.PASS,
                       f"AI Config has {generations} generations ({success} successful), {tokens:,} tokens, {duration:,}ms duration", 15,
                       {"generations": generations, "success": success, "tokens": tokens, "duration": duration})
        else:
            self._check("[5] Metrics Collection", Status.WARN,
                       "No metrics data yet. Run test queries through agent.", 0)

    # ========================================================================
    # STEP 4: Targeting
    # ========================================================================

    def check_targeting(self):
        """[4] Verify targeting rules are configured"""
        code, data = self._api("GET", f"/projects/{self.project}/ai-configs/{self.ai_config}/targeting")

        if code != 200:
            self._check("[4] Targeting", Status.FAIL, f"Cannot retrieve (HTTP {code})", 0)
            return

        # Extract environment-specific targeting
        env_targeting = data.get("environments", {}).get(self.env, {})
        enabled = env_targeting.get("enabled", False)
        rules = env_targeting.get("rules", [])
        fallthrough = env_targeting.get("fallthrough", {})

        if not enabled:
            self._check("[4] Targeting", Status.WARN, f"Targeting disabled for '{self.env}'", 0)
            return

        # Check if experiment is controlling targeting
        experiment_rules = [r for r in rules if "experiment" in r.get("description", "").lower()]

        if experiment_rules:
            self._check("[4] Targeting", Status.PASS,
                       f"Targeting controlled by experiment with {len(experiment_rules)} experiment rule(s)", 15,
                       {"enabled": True, "experiment_controlled": True})
        elif rules or "variation" in fallthrough:
            self._check("[4] Targeting", Status.PASS,
                       f"Targeting enabled with {len(rules)} custom rule(s) + default fallthrough", 15,
                       {"enabled": True, "rules": len(rules), "has_fallthrough": "variation" in fallthrough})
        else:
            self._check("[4] Targeting", Status.WARN,
                       "Targeting enabled but no rules configured", 5)

    # ========================================================================
    # STEP 6: Experiments
    # ========================================================================

    def check_experiments(self):
        """[6] Verify experiments are configured (doesn't need to be running)"""
        code, data = self._api("GET", f"/projects/{self.project}/environments/{self.env}/experiments")

        if code != 200:
            self._check("[6] Experiments", Status.WARN, "Cannot retrieve experiments (optional)", 0)
            return

        experiments = data.get("items", [])

        if experiments:
            exp_info = []
            for e in experiments:
                status = e.get("currentIteration", {}).get("status", "unknown")
                exp_info.append({
                    "name": e.get("name"),
                    "status": status,
                    "key": e.get("key")
                })

            summary = ", ".join([f"{e['name']} ({e['status']})" for e in exp_info])
            self._check("[6] Experiments", Status.PASS,
                       f"Found {len(experiments)} experiment(s): {summary}", 15,
                       {"experiments": exp_info})
        else:
            self._check("[6] Experiments", Status.WARN,
                       "No experiments found (optional - create one to demonstrate A/B testing)", 0)

    # ========================================================================
    # Run All Checks
    # ========================================================================

    def run(self):
        """Execute all verification checks"""
        print("\n" + "=" * 70)
        print("LaunchDarkly Setup Verification")
        print("=" * 70)
        print(f"Project: {self.project}")
        print(f"Environment: {self.env}")
        print(f"AI Config: {self.ai_config}")
        print("=" * 70 + "\n")

        # Run checks in order of setup steps
        print("Step 1: Account Setup")
        self.check_api_token()
        self.check_sdk_key()

        print("\nStep 2: AI Config")
        self.check_ai_config()
        self.check_variations()
        self.check_tools()

        print("\nStep 3: Agent Code & Step 5: Monitoring")
        self.check_metrics_tracking()
        self.check_ai_config_metrics()

        print("\nStep 4: Targeting")
        self.check_targeting()

        print("\nStep 6: Experiments")
        self.check_experiments()

        return self.print_summary()

    def print_summary(self) -> bool:
        """Print results and score. Returns True if passing."""
        print("\n" + "=" * 70)
        print("VERIFICATION SUMMARY")
        print("=" * 70 + "\n")

        # Print each result
        for r in self.results:
            print(f"{r.status.value} {r.name}: {r.message}")

            # Show points earned
            if r.status == Status.PASS:
                print(f"   Points: {r.points}")
            elif r.status == Status.WARN and r.points > 0:
                print(f"   Points: {r.points} (partial credit)")

            # Show details in verbose mode
            if r.details and self.verbose:
                print(f"   Details: {json.dumps(r.details, indent=6)}")
            print()

        # Calculate score (warnings get half credit)
        total_points = sum(r.points for r in self.results)
        earned = sum(r.points for r in self.results if r.status == Status.PASS)
        earned += sum(r.points // 2 for r in self.results if r.status == Status.WARN and r.points > 0)
        percentage = (earned / total_points * 100) if total_points > 0 else 0

        # Count by status
        passed = sum(1 for r in self.results if r.status == Status.PASS)
        failed = sum(1 for r in self.results if r.status == Status.FAIL)
        warnings = sum(1 for r in self.results if r.status == Status.WARN)

        # Print stats
        print("-" * 70)
        print(f"Total Checks: {len(self.results)}")
        print(f"  {Status.PASS.value} Passed:   {passed}")
        print(f"  {Status.FAIL.value} Failed:   {failed}")
        print(f"  {Status.WARN.value} Warnings: {warnings}")
        print("-" * 70)
        print(f"\n🏆 SCORE: {earned}/{total_points} points ({percentage:.1f}%)")
        print("-" * 70)

        # Grade the result
        if percentage >= 90:
            print(f"\n✅ EXCELLENT - {percentage:.1f}% - Great job!")
            return True
        elif percentage >= 70:
            print(f"\n✅ GOOD - {percentage:.1f}% - Most features working!")
            return True
        elif percentage >= 50:
            print(f"\n⚠️  PARTIAL - {percentage:.1f}% - Some features need work")
            return True
        else:
            print(f"\n⚠️  INCOMPLETE - {percentage:.1f}% - Several features missing")
            return False


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description="Verify LaunchDarkly AI Experimentation setup",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python verify_launchdarkly_setup.py                    # Use .env file
  python verify_launchdarkly_setup.py --verbose          # Show details
  python verify_launchdarkly_setup.py --project my-proj  # Override config
        """
    )

    parser.add_argument("--api-token", help="LaunchDarkly API access token")
    parser.add_argument("--project", help="Project key (default: pet-store-agent)")
    parser.add_argument("--env", help="Environment key (default: production)")
    parser.add_argument("--ai-config", help="AI Config key (default: pet-store-agent)")
    parser.add_argument("--verbose", "-v", action="store_true", help="Show detailed output")

    args = parser.parse_args()

    # Priority: CLI args > .env file > defaults
    api_token = args.api_token or os.getenv("LD_API_TOKEN") or os.getenv("LD_API_KEY") or ""
    project = args.project or os.getenv("LD_PROJECT_KEY") or "pet-store-agent"
    env = args.env or os.getenv("LD_ENV_KEY") or "production"
    ai_config = args.ai_config or os.getenv("LD_AI_CONFIG_KEY") or "pet-store-agent"

    # Validate required config
    if not api_token:
        print("❌ ERROR: LD_API_TOKEN is required")
        print("\nProvide via:")
        print("  1. .env file: LD_API_TOKEN=api-xxx")
        print("  2. CLI flag: --api-token api-xxx")
        print("  3. Environment: export LD_API_TOKEN='api-xxx'")
        sys.exit(1)

    # Run verification
    verifier = Verifier(api_token, project, env, ai_config, verbose=args.verbose)
    success = verifier.run()

    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
