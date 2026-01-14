from bedrock_agentcore.runtime import BedrockAgentCoreApp
from pet_store_agent_full_ld import get_agent
import logging

logger = logging.getLogger()
logger.setLevel(logging.INFO)

app = BedrockAgentCoreApp()

@app.entrypoint
def handler(payload):
    """AgentCore handler function with LaunchDarkly integration"""
    prompt = payload.get('prompt', 'A new user is asking about the price of Doggy Delights?')

    # Extract user context for LaunchDarkly targeting
    user_context = {
        "user_id": payload.get("user_id", "anonymous"),
        "customer_id": payload.get("customer_id"),
        "request_type": payload.get("request_type", "product_inquiry"),
        "subscription_status": payload.get("subscription_status", "unknown"),
        "query_complexity": payload.get("query_complexity", "medium")
    }

    # Remove None values
    user_context = {k: v for k, v in user_context.items() if v is not None}

    # Process with LaunchDarkly-enhanced agent
    agent = get_agent()
    return agent.invoke(prompt, user_context)

if __name__ == "__main__":
    app.run()