# LaunchDarkly Setup Verification

Automated verification for LaunchDarkly AI Config setup steps. Checks API tokens, AI configs, variations, targeting, experiments, and metrics.

## Quick Start

```bash
# Install dependencies
pip install requests python-dotenv

# Create .env file
cp .env.example .env
# Edit .env and add your LD_API_TOKEN

# Run verification
python3 verify_launchdarkly_setup.py
```

## Configuration

Set in `.env` file or use command-line flags:

```bash
LD_API_TOKEN=api-xxxxxxxx        # Required
LD_PROJECT_KEY=pet-store-agent   # Optional (default)
LD_ENV_KEY=production            # Optional (default)
LD_AI_CONFIG_KEY=pet-store-agent # Optional (default)
```

## Options

```bash
python3 verify_launchdarkly_setup.py --verbose              # Detailed output
python3 verify_launchdarkly_setup.py --output results.json  # Export JSON
python3 verify_launchdarkly_setup.py --project my-project   # Custom project
```

## Scoring

All checks are optional - partial credit awarded. Maximum 130 points.

See [LAUNCHDARKLY.md](./LAUNCHDARKLY.md) for setup instructions.
