# LaunchDarkly Setup Verification Tool

Automated verification tool for checking LaunchDarkly AI Experimentation setup steps via REST API.

## Quick Start

### 1. Install Dependencies

```bash
pip install requests python-dotenv
```

### 2. Set Up Environment Variables

Create a `.env` file from the example:

```bash
cp .env.example .env
```

Edit `.env` and add your LaunchDarkly API token:

```bash
# Required
LD_API_TOKEN=api-xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx

# Optional (defaults shown)
LD_PROJECT_KEY=pet-store-agent
LD_ENV_KEY=production
LD_AI_CONFIG_KEY=pet-store-agent
```

### 3. Run Verification

**Option A: Using .env file (Recommended)**
```bash
python3 verify_launchdarkly_setup.py
```

**Option B: Using Configuration File**
```bash
# Edit verify_config.json with your settings
python3 verify_launchdarkly_setup.py --config verify_config.json
```

**Option C: Using Command-Line Arguments**
```bash
python3 verify_launchdarkly_setup.py \
  --api-token api-xxx \
  --project my-project-key \
  --env production \
  --ai-config my-ai-config \
  --verbose
```

## Configuration Options

### Environment Variables (.env file)

The script automatically loads variables from a `.env` file in the same directory.

| Variable | Description | Default |
|----------|-------------|---------|
| `LD_API_TOKEN` | API access token (required) | - |
| `LD_PROJECT_KEY` | Project key | `pet-store-agent` |
| `LD_ENV_KEY` | Environment key | `production` |
| `LD_AI_CONFIG_KEY` | AI Config key | `pet-store-agent` |

**Priority:** Command-line args > Environment variables (.env) > Config file > Defaults

### Configuration File (`verify_config.json`)

The configuration file allows you to customize verification behavior for different setups:

```json
{
  "api_token": "api-your-token-here",
  "project_key": "your-project",
  "env_key": "production",
  "ai_config_key": "your-ai-config",

  "optional_checks": {
    "tools": {
      "enabled": true,
      "expected_tools": [
        "your-tool-1",
        "your-tool-2"
      ]
    },
    "experiments": {
      "enabled": true,
      "expected_experiment_key": null
    },
    "targeting": {
      "require_enabled": true,
      "require_rules": false
    }
  },

  "verbose": false
}
```

**Key Configuration Points:**

- **`api_token`**: Your LaunchDarkly API access token (can leave empty if using env var)
- **`project_key`**: Your specific project key (not necessarily `pet-store-agent`)
- **`ai_config_key`**: Your AI Config key (can be any name you chose)
- **`optional_checks.tools.expected_tools`**: List your specific tool names (for LlamaIndex, Bedrock KB, or custom tools)
- **`verbose`**: Set to `true` to see detailed API response data

### Adapting for Different Setups

**Example 1: Using Bedrock Knowledge Bases**
```json
{
  "project_key": "ecommerce-agent",
  "ai_config_key": "product-assistant",
  "optional_checks": {
    "tools": {
      "enabled": true,
      "expected_tools": [
        "ProductInformation",
        "PetCaringKnowledge",
        "get_inventory",
        "get_user_by_id"
      ]
    }
  }
}
```

**Example 2: Using LlamaIndex RAG**
```json
{
  "project_key": "support-bot",
  "ai_config_key": "customer-support-agent",
  "optional_checks": {
    "tools": {
      "enabled": true,
      "expected_tools": [
        "search_product_catalog",
        "search_pet_care",
        "rerank_results"
      ]
    }
  }
}
```

**Example 3: Using Different Models (No Tool Checking)**
```json
{
  "project_key": "my-hackathon-project",
  "ai_config_key": "llama-vs-claude-experiment",
  "optional_checks": {
    "tools": {
      "enabled": false
    }
  }
}
```

## What Gets Checked

### ✅ Step 1: Account Setup
- API Token exists with correct permissions
- SDK Key exists for target environment

### ✅ Step 2: AI Config
- AI Config exists with correct key and mode
- Variations are configured with models and instructions
- Tools are attached (if applicable)
- Custom parameters are set

### ✅ Step 2b: Tool Definitions (Optional)
- Tool definitions exist in LaunchDarkly library
- Expected tools are present (configurable)

### ✅ Step 4: Targeting
- Targeting rules are configured
- Default fallthrough is set

### ✅ Step 6: Experiments
- Experiments exist and status
- Experiment treatments are configured
- Metric data collection (if running)

### ✅ Step 5 & 7: Monitoring
- AI Config has evaluation activity
- Metrics are being tracked

## Command-Line Options

```bash
usage: verify_launchdarkly_setup.py [-h] [--config CONFIG]
                                     [--api-token API_TOKEN]
                                     [--project PROJECT_KEY]
                                     [--env ENV_KEY]
                                     [--ai-config AI_CONFIG_KEY]
                                     [--verbose]
                                     [--output OUTPUT]

optional arguments:
  -h, --help            Show this help message and exit
  --config, -c          Path to configuration JSON file
  --api-token           LaunchDarkly API access token
  --project             Project key
  --env                 Environment key
  --ai-config           AI Config key
  --verbose, -v         Show detailed output with API response data
  --output, -o          Export results to JSON file
```

## Examples

### Basic Verification
```bash
# After setting up .env file
python3 verify_launchdarkly_setup.py
```

### Verbose Output
```bash
python3 verify_launchdarkly_setup.py --verbose
```

### Custom Project and Export Results
```bash
python3 verify_launchdarkly_setup.py \
  --project my-custom-project \
  --ai-config my-agent-config \
  --output verification_results.json
```

### Using Different Environment
```bash
python3 verify_launchdarkly_setup.py \
  --env test \
  --verbose
```

## Output

### Console Output

The script provides color-coded output:

```
✅ Check Name
   Success message

❌ Check Name
   Failure message

⚠️  Check Name
   Warning message

⏭️  Check Name
   Skipped message
```

### JSON Export

Use `--output` to export detailed results:

```bash
python3 verify_launchdarkly_setup.py --output results.json
```

Output format:
```json
{
  "project_key": "pet-store-agent",
  "environment_key": "production",
  "ai_config_key": "pet-store-agent",
  "timestamp": "2025-01-22T10:30:00",
  "summary": {
    "total": 10,
    "passed": 8,
    "failed": 0,
    "warnings": 2,
    "skipped": 0
  },
  "checks": [
    {
      "name": "API Token Verification",
      "status": "PASSED",
      "message": "Found 1 API token(s) with appropriate permissions",
      "details": {"token_count": 1}
    }
  ]
}
```

## Exit Codes

- `0`: All checks passed (warnings are acceptable)
- `1`: One or more critical failures detected

## Troubleshooting

### "API Token verification failed"
- Verify your API token is correct and starts with `api-`
- Check token has Writer or Admin role in LaunchDarkly
- Ensure token hasn't expired

### "AI Config not found"
- Verify `project_key` and `ai_config_key` match your LaunchDarkly setup
- Check you're using the correct environment

### "No tool definitions found"
- This is a warning, not an error
- If using Bedrock Agents, tools are configured as Action Groups (not in LaunchDarkly)
- If using LlamaIndex/LangGraph, create tools in LaunchDarkly Library
- You can disable tool checking in `verify_config.json`

### "No experiments found"
- Experiments are optional
- Create an experiment in LaunchDarkly to compare model variations

## Integration with CI/CD

You can use this script in CI/CD pipelines:

```yaml
# GitHub Actions example
- name: Verify LaunchDarkly Setup
  env:
    LD_API_TOKEN: ${{ secrets.LD_API_TOKEN }}
  run: |
    pip install requests python-dotenv
    python3 verify_launchdarkly_setup.py --output results.json

- name: Upload Results
  uses: actions/upload-artifact@v3
  with:
    name: launchdarkly-verification
    path: results.json
```

## Notes

- The `.env` file is automatically ignored by git (see `.gitignore`)
- Never commit your `.env` file with real credentials
- Use `.env.example` as a template for team members

## Support

For issues or questions:
- Check the [LaunchDarkly API Documentation](https://apidocs.launchdarkly.com/)
- Ensure your setup follows the steps in [LAUNCHDARKLY.md](./LAUNCHDARKLY.md)
