#!/bin/bash
# Script to run the pet store agent locally with all required environment variables

# Load environment variables from .env file
if [ -f "../../.env" ]; then
    export $(cat ../../.env | grep -v '^#' | xargs)
    echo "✅ Loaded environment variables from .env"
else
    echo "❌ .env file not found at ../../.env"
    exit 1
fi

# Set AWS configuration
export AWS_PROFILE=bedrock-demo
export AWS_DEFAULT_REGION=us-east-1
echo "✅ AWS Profile: $AWS_PROFILE"
echo "✅ AWS Region: $AWS_DEFAULT_REGION"

# Check if LaunchDarkly SDK key is set
if [ -z "$LAUNCHDARKLY_SDK_KEY" ]; then
    echo "❌ LAUNCHDARKLY_SDK_KEY not set"
    exit 1
else
    echo "✅ LaunchDarkly SDK key configured"
fi

# Run the query agent
if [ $# -eq 0 ]; then
    # No arguments, run in interactive mode
    echo ""
    echo "Starting interactive mode..."
    python3 query_agent.py --interactive
else
    # Run with the provided query
    echo ""
    echo "Running query: $@"
    python3 query_agent.py "$@"
fi