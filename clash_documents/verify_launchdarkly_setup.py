#!/usr/bin/env python3
"""
LaunchDarkly Setup Verification Script

This script verifies all steps of the LaunchDarkly AI Experimentation setup
by making API calls to check account configuration, AI configs, tools, targeting,
experiments, and metrics collection.

Usage:
    # Using .env file (recommended)
    python verify_launchdarkly_setup.py

    # Using environment variables
    export LD_API_TOKEN='api-xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx'
    export LD_PROJECT_KEY='your-project-key'
    export LD_AI_CONFIG_KEY='your-ai-config-key'
    python verify_launchdarkly_setup.py

    # With verbose output
    python verify_launchdarkly_setup.py --verbose

    # Override with command line arguments
    python verify_launchdarkly_setup.py --api-token api-xxx --project my-project

Configuration:
    Create a .env file or set environment variables:
    - LD_API_TOKEN: LaunchDarkly API access token (required)
    - LD_PROJECT_KEY: Project key (default: pet-store-agent)
    - LD_ENV_KEY: Environment key (default: production)
    - LD_AI_CONFIG_KEY: AI Config key (default: pet-store-agent)
"""

import os
import sys
import json
import argparse
import requests
import time
from pathlib import Path
from typing import Dict, Any, List, Optional
from dataclasses import dataclass
from enum import Enum

# Try to load dotenv if available
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    # dotenv not installed, will use environment variables directly
    pass


class CheckStatus(Enum):
    """Status of a verification check"""
    PASSED = "✅"
    FAILED = "❌"
    WARNING = "⚠️"
    SKIPPED = "⏭️"


@dataclass
class CheckResult:
    """Result of a verification check"""
    name: str
    status: CheckStatus
    message: str
    details: Optional[Dict[str, Any]] = None
    required: bool = False  # All checks are optional for partial credit
    points: int = 10  # Points awarded for passing this check


class LaunchDarklyVerifier:
    """Verifies LaunchDarkly setup via REST API"""

    BASE_URL = "https://app.launchdarkly.com/api/v2"

    def __init__(self, api_token: str, project_key: str, env_key: str, ai_config_key: str,
                 config_options: Optional[Dict[str, Any]] = None):
        self.api_token = api_token
        self.project_key = project_key
        self.env_key = env_key
        self.ai_config_key = ai_config_key
        self.config_options = config_options or {}
        self.headers = {
            "Authorization": api_token,
            "Content-Type": "application/json"
        }
        self.results: List[CheckResult] = []
        self.verbose = self.config_options.get("verbose", False)

    def _make_request(self, method: str, endpoint: str, **kwargs) -> tuple[int, Dict[str, Any]]:
        """Make HTTP request to LaunchDarkly API"""
        url = f"{self.BASE_URL}{endpoint}"
        try:
            response = requests.request(method, url, headers=self.headers, **kwargs)
            data = response.json() if response.content else {}
            return response.status_code, data
        except requests.exceptions.RequestException as e:
            return 0, {"error": str(e)}
        except json.JSONDecodeError:
            return response.status_code, {"error": "Invalid JSON response"}

    def _add_result(self, name: str, status: CheckStatus, message: str, details: Optional[Dict] = None,
                    required: bool = False, points: int = 10):
        """Add a check result"""
        self.results.append(CheckResult(name, status, message, details, required, points))

    # =========================================================================
    # STEP 1: Account Setup Verification
    # =========================================================================

    def verify_api_token(self) -> CheckResult:
        """Step 1b: Verify API access token exists and has correct permissions"""
        status_code, data = self._make_request("GET", "/tokens")

        if status_code == 200 and "items" in data:
            tokens = data.get("items", [])
            if tokens:
                self._add_result(
                    "[1b] API Token",
                    CheckStatus.PASSED,
                    f"API token is valid and working",
                    {"token_count": len(tokens)},
                    required=False,
                    points=10
                )
            else:
                self._add_result(
                    "[1b] API Token",
                    CheckStatus.WARNING,
                    "Token works but no tokens found in response",
                    required=False,
                    points=5
                )
        else:
            self._add_result(
                "[1b] API Token",
                CheckStatus.FAILED,
                f"Failed to retrieve tokens (Status: {status_code})",
                {"error": data.get("error", "Unknown error")},
                required=False,
                points=0
            )

        return self.results[-1]

    def verify_sdk_key(self) -> CheckResult:
        """Step 1c: Verify SDK key exists for the target environment"""
        endpoint = f"/projects/{self.project_key}/environments/{self.env_key}"
        status_code, data = self._make_request("GET", endpoint)

        if status_code == 200 and "apiKey" in data:
            sdk_key = data.get("apiKey", "")
            if sdk_key.startswith("sdk-"):
                self._add_result(
                    "[1c] SDK Key",
                    CheckStatus.PASSED,
                    f"SDK key found for environment '{self.env_key}'",
                    {"sdk_key": sdk_key[:15] + "..."},
                    required=False,
                    points=10
                )
            else:
                self._add_result(
                    "[1c] SDK Key",
                    CheckStatus.WARNING,
                    "SDK key found but doesn't start with 'sdk-'",
                    {"sdk_key": sdk_key},
                    required=False,
                    points=5
                )
        else:
            self._add_result(
                "[1c] SDK Key",
                CheckStatus.FAILED,
                f"Failed to retrieve SDK key (Status: {status_code})",
                {"error": data.get("message", data.get("error", "Unknown error"))},
                required=False,
                points=0
            )

        return self.results[-1]

    # =========================================================================
    # STEP 2: AI Config Verification
    # =========================================================================

    def verify_ai_config_exists(self) -> CheckResult:
        """Step 2a: Verify AI Config exists with correct configuration"""
        endpoint = f"/projects/{self.project_key}/ai-configs/{self.ai_config_key}"
        status_code, data = self._make_request("GET", endpoint)

        if status_code == 200:
            config_key = data.get("key")
            config_name = data.get("name", config_key)
            config_mode = data.get("mode")  # API uses 'mode' not 'kind'
            variations = data.get("variations", [])

            if config_key == self.ai_config_key:
                if config_mode in ["agent", "completion", "judge"]:
                    self._add_result(
                        "[2a] AI Config",
                        CheckStatus.PASSED,
                        f"AI Config '{config_name}' found with mode '{config_mode}' and {len(variations)} variation(s)",
                        {
                            "name": config_name,
                            "mode": config_mode,
                            "variations": [v.get("key") for v in variations]
                        },
                        required=False,
                        points=15
                    )
                else:
                    self._add_result(
                        "[2a] AI Config",
                        CheckStatus.WARNING,
                        f"AI Config found but mode is '{config_mode}' (expected 'agent', 'completion', or 'judge')",
                        {"mode": config_mode},
                        required=False,
                        points=10
                    )
            else:
                self._add_result(
                    "[2a] AI Config",
                    CheckStatus.FAILED,
                    f"Config key mismatch: expected '{self.ai_config_key}', got '{config_key}'",
                    required=False,
                    points=0
                )
        else:
            self._add_result(
                "[2a] AI Config",
                CheckStatus.FAILED,
                f"AI Config not found (Status: {status_code})",
                {"error": data.get("message", data.get("error", "Unknown error"))},
                required=False,
                points=0
            )

        return self.results[-1]

    def verify_ai_config_variations(self) -> CheckResult:
        """Step 2a: Verify AI Config variations have required fields"""
        endpoint = f"/projects/{self.project_key}/ai-configs/{self.ai_config_key}"
        status_code, data = self._make_request("GET", endpoint, params={"expand": "variations"})

        if status_code == 200:
            config_name = data.get("name", self.ai_config_key)
            variations = data.get("variations", [])

            if variations:
                variation_details = []
                issues = []

                for var in variations:
                    var_key = var.get("key")
                    var_name = var.get("name", var_key)
                    model_key = var.get("modelConfigKey")
                    instructions = var.get("instructions")
                    messages = var.get("messages")
                    tools = var.get("tools", [])

                    missing = []

                    # Check for required fields
                    if not model_key:
                        missing.append("model")
                    if not instructions and not messages:
                        missing.append("instructions or messages")
                    if len(tools) == 0:
                        missing.append("at least one tool")

                    var_info = {
                        "name": var_name,
                        "key": var_key,
                        "tool_count": len(tools),
                        "missing": missing
                    }
                    variation_details.append(var_info)

                    if missing:
                        issues.append(f"'{var_name}' missing: {', '.join(missing)}")

                # Award points based on what's configured
                if len(variations) >= 2 and not issues:
                    # Perfect: 2+ variations, all complete
                    var_summary = ", ".join([f"{v['name']} ({v['tool_count']} tools)" for v in variation_details])
                    self._add_result(
                        "[2a] Variations (2+)",
                        CheckStatus.PASSED,
                        f"Config '{config_name}' has {len(variations)} variations: {var_summary}",
                        {"config": config_name, "variations": variation_details},
                        required=False,
                        points=20
                    )
                elif len(variations) == 1 and not issues:
                    # Good: 1 complete variation (partial credit)
                    var_summary = f"{variation_details[0]['name']} ({variation_details[0]['tool_count']} tools)"
                    self._add_result(
                        "[2a] Variations (1)",
                        CheckStatus.PASSED,
                        f"Config '{config_name}' has 1 complete variation: {var_summary}. Add another for A/B testing!",
                        {"config": config_name, "variations": variation_details},
                        required=False,
                        points=10
                    )
                elif issues:
                    # Has variations but incomplete
                    self._add_result(
                        "[2a] Variations",
                        CheckStatus.WARNING,
                        f"Config '{config_name}' has {len(variations)} variations but: {'; '.join(issues)}",
                        {"config": config_name, "variations": variation_details},
                        required=False,
                        points=5
                    )
            else:
                self._add_result(
                    "[2a] Variations",
                    CheckStatus.FAILED,
                    f"Config '{config_name}' has no variations",
                    required=False,
                    points=0
                )
        else:
            self._add_result(
                "[2a] Variations",
                CheckStatus.FAILED,
                f"Failed to retrieve variation details (Status: {status_code})",
                {"error": data.get("message", data.get("error", "Unknown error"))},
                required=False,
                points=0
            )

        return self.results[-1]

    # =========================================================================
    # STEP 2B: Tool Definition Verification
    # =========================================================================

    def verify_tools(self) -> CheckResult:
        """Step 2b: Verify tool definitions exist (optional)"""
        endpoint = f"/projects/{self.project_key}/ai-tools"
        status_code, data = self._make_request("GET", endpoint)

        if status_code == 200:
            items = data.get("items", [])
            if items:
                tool_details = [
                    {
                        "key": tool.get("key"),
                        "name": tool.get("name"),
                        "version_count": len(tool.get("versions", []))
                    }
                    for tool in items
                ]

                tool_names = [t["name"] or t["key"] for t in tool_details]
                self._add_result(
                    "[2b] Tool Definitions",
                    CheckStatus.PASSED,
                    f"Found {len(items)} tool(s): {', '.join(tool_names)}",
                    {"tools": tool_details},
                    required=False,
                    points=10
                )
            else:
                self._add_result(
                    "[2b] Tool Definitions",
                    CheckStatus.FAILED,
                    "No tool definitions found (optional for Bedrock Agents)",
                    {},
                    required=False,
                    points=0
                )
        else:
            self._add_result(
                "[2b] Tool Definitions",
                CheckStatus.FAILED,
                f"Could not retrieve tools (Status: {status_code})",
                {"error": "API request failed"},
                required=False,
                points=0
            )

        return self.results[-1]

    # =========================================================================
    # STEP 3: Agent Code Instrumentation
    # =========================================================================

    def verify_metrics_tracking(self) -> CheckResult:
        """Step 3 & 5: Verify that AI metrics (tokens, duration, success) are being tracked"""
        endpoint = f"/metrics/{self.project_key}"
        status_code, data = self._make_request("GET", endpoint)

        if status_code == 200:
            items = data.get("items", [])

            # Look for AI-specific metrics
            ai_metrics = {
                "input_tokens": None,
                "output_tokens": None,
                "total_tokens": None,
                "duration": None,
                "success": None
            }

            for metric in items:
                key = metric.get("key", "")
                last_seen = metric.get("lastSeen")

                if "ai-input-tokens" in key:
                    ai_metrics["input_tokens"] = last_seen
                elif "ai-output-tokens" in key:
                    ai_metrics["output_tokens"] = last_seen
                elif "ai-total-tokens" in key:
                    ai_metrics["total_tokens"] = last_seen
                elif "ai-completion-duration" in key and "p95" not in key and "p99" not in key:
                    ai_metrics["duration"] = last_seen
                elif "ai-completion-success" in key:
                    ai_metrics["success"] = last_seen

            # Check which metrics have data
            tracked_metrics = {k: v for k, v in ai_metrics.items() if v is not None}

            if len(tracked_metrics) >= 3:  # At least 3 core metrics being tracked
                import datetime
                now = datetime.datetime.now().timestamp() * 1000
                recent_threshold = 24 * 60 * 60 * 1000  # 24 hours in milliseconds

                # Check if any metrics were seen recently
                recent_metrics = [
                    k for k, v in tracked_metrics.items()
                    if (now - v) < recent_threshold
                ]

                if recent_metrics:
                    self._add_result(
                        "[3/5] Agent Instrumentation",
                        CheckStatus.PASSED,
                        f"Agent is tracking {len(tracked_metrics)}/5 metrics ({len(recent_metrics)} recent). Using track_duration_of() and track_tokens().",
                        {
                            "tracked_metrics": list(tracked_metrics.keys()),
                            "recent_metrics": recent_metrics
                        },
                        required=False,
                        points=20
                    )
                else:
                    self._add_result(
                        "[3/5] Agent Instrumentation",
                        CheckStatus.WARNING,
                        f"Metrics exist ({len(tracked_metrics)}/5) but no recent activity. Run agent queries to populate.",
                        {"tracked_metrics": list(tracked_metrics.keys())},
                        required=False,
                        points=10
                    )
            else:
                self._add_result(
                    "[3/5] Agent Instrumentation",
                    CheckStatus.FAILED,
                    f"Only {len(tracked_metrics)}/5 metrics tracked. Ensure tracker.track_tokens() and tracker.track_duration_of() are called in agent code.",
                    {"tracked_metrics": list(tracked_metrics.keys())},
                    required=False,
                    points=0
                )
        else:
            self._add_result(
                "[3/5] Agent Instrumentation",
                CheckStatus.FAILED,
                f"Could not retrieve metrics (Status: {status_code})",
                {"error": data.get("message", data.get("error", "Unknown error"))},
                required=False,
                points=0
            )

        return self.results[-1]

    def verify_ai_config_has_metrics(self) -> CheckResult:
        """Step 5: Verify AI Config has actual metrics data (from agent usage)"""
        # Get last 24 hours of metrics
        now = int(time.time() * 1000)
        from_time = now - (24 * 60 * 60 * 1000)

        endpoint = f"/projects/{self.project_key}/ai-configs/{self.ai_config_key}/metrics?from={from_time}&to={now}&env={self.env_key}"
        status_code, data = self._make_request("GET", endpoint)

        if status_code == 200:
            generation_count = data.get("generationCount", 0)
            success_count = data.get("generationSuccessCount", 0)
            total_tokens = data.get("totalTokens", 0)
            duration_ms = data.get("durationMs", 0)

            if generation_count > 0:
                self._add_result(
                    "[5] Metrics Collection",
                    CheckStatus.PASSED,
                    f"AI Config has {generation_count} generations ({success_count} successful), {total_tokens:,} tokens, {duration_ms:,}ms duration",
                    {
                        "generations": generation_count,
                        "success_count": success_count,
                        "total_tokens": total_tokens,
                        "duration_ms": duration_ms
                    },
                    required=False,
                    points=15
                )
            else:
                self._add_result(
                    "[5] Metrics Collection",
                    CheckStatus.WARNING,
                    "No metrics data yet. Run test queries through your agent to populate metrics.",
                    {},
                    required=False,
                    points=0
                )
        else:
            self._add_result(
                "[5] Metrics Collection",
                CheckStatus.FAILED,
                f"Could not retrieve AI Config metrics (Status: {status_code})",
                {"error": data.get("message", data.get("error", "Unknown error"))},
                required=False,
                points=0
            )

        return self.results[-1]

    # =========================================================================
    # STEP 4: Targeting Configuration Verification
    # =========================================================================

    def verify_targeting_rules(self) -> CheckResult:
        """Step 4: Verify targeting rules are configured"""
        endpoint = f"/projects/{self.project_key}/ai-configs/{self.ai_config_key}/targeting"
        status_code, data = self._make_request("GET", endpoint)

        if status_code == 200:
            # Targeting response has 'environments' object with environment-specific settings
            environments = data.get("environments", {})
            env_targeting = environments.get(self.env_key, {})

            is_on = env_targeting.get("enabled", False)
            rules = env_targeting.get("rules", [])
            fallthrough = env_targeting.get("fallthrough", {})

            if is_on:
                rule_count = len(rules)
                has_fallthrough = "variation" in fallthrough

                # Check if an experiment is controlling targeting
                experiment_rules = [r for r in rules if r.get("description", "").startswith("Included in experiment")]
                has_experiment = len(experiment_rules) > 0

                if has_experiment:
                    self._add_result(
                        "[4] Targeting",
                        CheckStatus.PASSED,
                        f"Targeting controlled by experiment with {len(experiment_rules)} experiment rule(s)",
                        {
                            "enabled": is_on,
                            "environment": self.env_key,
                            "experiment_controlled": True,
                            "experiment_rules": len(experiment_rules)
                        },
                        required=False,
                        points=15
                    )
                elif has_fallthrough or rule_count > 0:
                    self._add_result(
                        "[4] Targeting",
                        CheckStatus.PASSED,
                        f"Targeting enabled for '{self.env_key}' with {rule_count} custom rule(s) + default rule",
                        {
                            "enabled": is_on,
                            "environment": self.env_key,
                            "rule_count": rule_count,
                            "has_fallthrough": has_fallthrough
                        },
                        required=False,
                        points=15
                    )
                else:
                    self._add_result(
                        "[4] Targeting",
                        CheckStatus.WARNING,
                        f"Targeting enabled but no rules or fallthrough configured",
                        {"enabled": is_on, "environment": self.env_key},
                        required=False,
                        points=5
                    )
            else:
                self._add_result(
                    "[4] Targeting",
                    CheckStatus.WARNING,
                    f"Targeting is disabled for environment '{self.env_key}'",
                    {"enabled": is_on, "environment": self.env_key},
                    required=False,
                    points=0
                )
        else:
            self._add_result(
                "[4] Targeting",
                CheckStatus.FAILED,
                f"Failed to retrieve targeting configuration (Status: {status_code})",
                {"error": data.get("message", data.get("error", "Unknown error"))},
                required=False,
                points=0
            )

        return self.results[-1]

    # =========================================================================
    # STEP 6: Experiment Verification
    # =========================================================================

    def verify_experiments(self) -> CheckResult:
        """Step 6: Verify experiments are configured (not necessarily running)"""
        endpoint = f"/projects/{self.project_key}/environments/{self.env_key}/experiments"
        status_code, data = self._make_request("GET", endpoint)

        if status_code == 200:
            items = data.get("items", [])
            if items:
                exp_details = []

                for exp in items:
                    current_iter = exp.get("currentIteration", {})
                    status = current_iter.get("status", "unknown")

                    exp_info = {
                        "key": exp.get("key"),
                        "name": exp.get("name"),
                        "status": status,
                        "flag_key": exp.get("flagKey"),
                        "metric": current_iter.get("primaryMetricKey")
                    }
                    exp_details.append(exp_info)

                # Give credit for having experiments configured, regardless of status
                exp_names = [e["name"] for e in exp_details]
                status_summary = ", ".join([f"{e['name']} ({e['status']})" for e in exp_details])

                self._add_result(
                    "[6] Experiments",
                    CheckStatus.PASSED,
                    f"Found {len(items)} experiment(s): {status_summary}",
                    {"experiments": exp_details},
                    required=False,
                    points=15
                )
            else:
                self._add_result(
                    "[6] Experiments",
                    CheckStatus.WARNING,
                    "No experiments found (optional - create one to demonstrate A/B testing knowledge)",
                    {},
                    required=False,
                    points=0
                )
        else:
            self._add_result(
                "[6] Experiments",
                CheckStatus.WARNING,
                f"Could not retrieve experiments (Status: {status_code})",
                {},
                required=False,
                points=0
            )

        return self.results[-1]

    # =========================================================================
    # Main Verification Runner
    # =========================================================================

    def run_all_checks(self) -> List[CheckResult]:
        """Run all verification checks"""
        print("\n" + "=" * 70)
        print("LaunchDarkly Setup Verification")
        print("=" * 70)
        print(f"Project: {self.project_key}")
        print(f"Environment: {self.env_key}")
        print(f"AI Config: {self.ai_config_key}")
        print("=" * 70 + "\n")

        # Step 1: Get Your LaunchDarkly Account Set Up
        print("Step 1: Account Setup")
        self.verify_api_token()
        self.verify_sdk_key()

        # Step 2: Create Your First AI Config
        print("\nStep 2: AI Config")
        self.verify_ai_config_exists()
        self.verify_ai_config_variations()
        self.verify_tools()

        # Step 3: Hook Up Your Agent Code
        print("\nStep 3: Agent Code & Step 5: Monitoring")
        self.verify_metrics_tracking()
        self.verify_ai_config_has_metrics()

        # Step 4: Update Target Configuration
        print("\nStep 4: Targeting")
        self.verify_targeting_rules()

        # Step 6: Run Your First AI Experiment
        print("\nStep 6: Experiments (Optional)")
        self.verify_experiments()

        return self.results

    def calculate_score(self) -> Dict[str, Any]:
        """Calculate competition score - all checks are optional"""
        total_points = sum(r.points for r in self.results)
        earned_points = sum(r.points for r in self.results if r.status == CheckStatus.PASSED)

        # Also award partial credit for warnings
        earned_points += sum(r.points // 2 for r in self.results if r.status == CheckStatus.WARNING)

        percentage = (earned_points / total_points * 100) if total_points > 0 else 0

        passed_count = sum(1 for r in self.results if r.status == CheckStatus.PASSED)
        total_checks = len(self.results)

        return {
            "earned_points": earned_points,
            "total_points": total_points,
            "percentage": round(percentage, 2),
            "passed_count": passed_count,
            "total_checks": total_checks
        }

    def print_summary(self):
        """Print summary of all checks"""
        print("\n" + "=" * 70)
        print("VERIFICATION SUMMARY")
        print("=" * 70 + "\n")

        # Count by status
        passed = sum(1 for r in self.results if r.status == CheckStatus.PASSED)
        failed = sum(1 for r in self.results if r.status == CheckStatus.FAILED)
        warnings = sum(1 for r in self.results if r.status == CheckStatus.WARNING)
        skipped = sum(1 for r in self.results if r.status == CheckStatus.SKIPPED)
        total = len(self.results)

        # Print results
        for result in self.results:
            print(f"{result.status.value} {result.name}: {result.message}")
            if result.status == CheckStatus.PASSED:
                print(f"   Points: {result.points}")
            elif result.status == CheckStatus.WARNING:
                print(f"   Points: {result.points // 2} (partial credit)")
            if result.details and self.verbose:
                print(f"   Details: {json.dumps(result.details, indent=6)}")
            print()

        # Calculate score
        score = self.calculate_score()

        # Print statistics
        print("-" * 70)
        print(f"Total Checks: {total}")
        print(f"  {CheckStatus.PASSED.value} Passed:   {passed}")
        print(f"  {CheckStatus.FAILED.value} Failed:   {failed}")
        print(f"  {CheckStatus.WARNING.value} Warnings: {warnings}")
        print(f"  {CheckStatus.SKIPPED.value} Skipped:  {skipped}")
        print("-" * 70)
        print(f"\n🏆 SCORE: {score['earned_points']}/{score['total_points']} points ({score['percentage']}%)")
        print("-" * 70)

        if score['percentage'] >= 90:
            print(f"\n✅ EXCELLENT - {score['percentage']}% - Great job!")
            return True
        elif score['percentage'] >= 70:
            print(f"\n✅ GOOD - {score['percentage']}% - Most features working!")
            return True
        elif score['percentage'] >= 50:
            print(f"\n⚠️  PARTIAL - {score['percentage']}% - Some features need work")
            return True
        else:
            print(f"\n⚠️  INCOMPLETE - {score['percentage']}% - Several features missing")
            return False

    def export_results(self, output_file: str):
        """Export results to JSON file with scoring"""
        score = self.calculate_score()

        results_data = {
            "project_key": self.project_key,
            "environment_key": self.env_key,
            "ai_config_key": self.ai_config_key,
            "timestamp": __import__("datetime").datetime.now().isoformat(),
            "score": {
                "earned_points": score['earned_points'],
                "total_points": score['total_points'],
                "percentage": score['percentage'],
                "passed_count": score['passed_count'],
                "total_checks": score['total_checks']
            },
            "summary": {
                "total": len(self.results),
                "passed": sum(1 for r in self.results if r.status == CheckStatus.PASSED),
                "failed": sum(1 for r in self.results if r.status == CheckStatus.FAILED),
                "warnings": sum(1 for r in self.results if r.status == CheckStatus.WARNING),
                "skipped": sum(1 for r in self.results if r.status == CheckStatus.SKIPPED)
            },
            "checks": [
                {
                    "name": r.name,
                    "status": r.status.name,
                    "passed": r.status == CheckStatus.PASSED,
                    "points": r.points,
                    "message": r.message,
                    "details": r.details
                }
                for r in self.results
            ]
        }

        with open(output_file, 'w') as f:
            json.dump(results_data, f, indent=2)

        print(f"\n📄 Results exported to: {output_file}")


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description="Verify LaunchDarkly AI Experimentation setup",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Using .env file (default)
  python verify_launchdarkly_setup.py

  # With command-line arguments
  python verify_launchdarkly_setup.py --api-token api-xxx --project my-project --verbose

  # Export results to JSON
  python verify_launchdarkly_setup.py --output results.json
        """
    )

    parser.add_argument("--api-token", help="LaunchDarkly API access token")
    parser.add_argument("--project", "--project-key", dest="project_key",
                        help="Project key (default: pet-store-agent)")
    parser.add_argument("--env", "--environment", dest="env_key",
                        help="Environment key (default: production)")
    parser.add_argument("--ai-config", dest="ai_config_key",
                        help="AI Config key (default: pet-store-agent)")
    parser.add_argument("--verbose", "-v", action="store_true",
                        help="Show detailed output")
    parser.add_argument("--output", "-o", help="Export results to JSON file")

    args = parser.parse_args()

    # Build configuration with priority: CLI args > env vars (.env file) > defaults
    config = {
        "api_token": (
            args.api_token or
            os.getenv("LD_API_TOKEN") or
            os.getenv("LD_API_KEY") or  # Accept both variable names
            ""
        ),
        "project_key": (
            args.project_key or
            os.getenv("LD_PROJECT_KEY") or
            "pet-store-agent"
        ),
        "env_key": (
            args.env_key or
            os.getenv("LD_ENV_KEY") or
            "production"
        ),
        "ai_config_key": (
            args.ai_config_key or
            os.getenv("LD_AI_CONFIG_KEY") or
            "pet-store-agent"
        )
    }

    # Additional config options
    config_options = {"verbose": args.verbose}

    # Validate required configuration
    if not config["api_token"]:
        print("❌ ERROR: LD_API_TOKEN is required")
        print("\nYou can provide it via:")
        print("  1. .env file in the current directory")
        print("  2. Command line: --api-token api-xxx")
        print("  3. Environment: export LD_API_TOKEN='api-xxx'")
        print("\nRun with --help for more options")
        sys.exit(1)

    # Run verification
    verifier = LaunchDarklyVerifier(
        api_token=config["api_token"],
        project_key=config["project_key"],
        env_key=config["env_key"],
        ai_config_key=config["ai_config_key"],
        config_options=config_options
    )

    verifier.run_all_checks()
    success = verifier.print_summary()

    # Export results if requested
    if args.output:
        verifier.export_results(args.output)

    # Exit with appropriate code
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
