#!/usr/bin/env python3
"""
Local testing script for the Pet Store Agent
Run this to test the agent locally before deploying to AgentCore
"""

import os
import json
import sys
import ldclient
from pet_store_agent_full_ld import PetStoreAgent

def main():
    # Set environment variables if not already set
    if not os.getenv("LAUNCHDARKLY_SDK_KEY"):
        print("Error: LAUNCHDARKLY_SDK_KEY environment variable is required")
        print("Set it with: export LAUNCHDARKLY_SDK_KEY='your-sdk-key'")
        sys.exit(1)

    # Optional: Set AWS profile
    if not os.getenv("AWS_PROFILE"):
        os.environ["AWS_PROFILE"] = "bedrock-demo"
        print("Using AWS Profile: bedrock-demo")

    # Create agent instance
    print("Initializing Pet Store Agent...")
    try:
        agent = PetStoreAgent()
        print("✅ Agent initialized successfully\n")
    except Exception as e:
        print(f"❌ Failed to initialize agent: {e}")
        sys.exit(1)

    # Test queries
    test_queries = [
        {
            "prompt": "What is the price of Doggy Delights?",
            "user_ctx": {"user_id": "test_user", "subscription_status": "active"}
        },
        {
            "prompt": "Tell me about cat products",
            "user_ctx": {"user_id": "test_user", "subscription_status": "guest"}
        },
        {
            "prompt": "How often should I bathe a Chihuahua?",
            "user_ctx": {"user_id": "test_user", "subscription_status": "active"}
        }
    ]

    # Interactive mode or test mode or single query
    if len(sys.argv) > 1:
        if sys.argv[1] == "--interactive":
            print("Interactive mode - type 'exit' to quit\n")
            while True:
                prompt = input("Query> ").strip()
                if prompt.lower() in ['exit', 'quit']:
                    break

                print("\n🤔 Processing...")
                response = agent.invoke(prompt, {"user_id": "interactive_user"})

                try:
                    response_json = json.loads(response)
                    print("\n📝 Response:")
                    print(json.dumps(response_json, indent=2))
                except:
                    print("\n📝 Response:")
                    print(response)
                print("\n" + "-"*50 + "\n")
        else:
            # Single query mode - just run the provided query
            query = " ".join(sys.argv[1:])
            print(f"Running query: {query}\n")
            response = agent.invoke(query, {"user_id": "test_user", "subscription_status": "active"})

            try:
                response_json = json.loads(response)
                print("Response:")
                print(json.dumps(response_json, indent=2))
            except:
                print("Response:")
                print(response)
    else:
        # Run test queries
        print("Running test queries...\n")
        for i, test in enumerate(test_queries, 1):
            print(f"Test {i}: {test['prompt']}")
            print(f"User context: {test['user_ctx']}")

            response = agent.invoke(test['prompt'], test['user_ctx'])

            try:
                response_json = json.loads(response)
                print("Response:")
                print(json.dumps(response_json, indent=2))
            except:
                print("Response:")
                print(response)

            print("\n" + "-"*50 + "\n")

        print("\nTo run in interactive mode, use: python query_agent.py --interactive")

    # Flush metrics to LaunchDarkly before exiting
    ld_client = ldclient.get()
    if ld_client.is_initialized():
        ld_client.flush()
        import time
        time.sleep(1)

if __name__ == "__main__":
    main()