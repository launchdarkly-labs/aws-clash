import os
import json
import logging
from dataclasses import dataclass
from typing import Any, Dict, Optional, Iterable, List, Set
from uuid import uuid4

import boto3
import ldclient
from ldclient import Context
from ldclient.config import Config as LDConfig

from ldai.client import LDAIClient, AIAgentConfigRequest, AIAgentConfigDefault
from ldai.tracker import TokenUsage

from langchain.chat_models import init_chat_model
from langchain_core.messages import HumanMessage, AIMessage
from langgraph.prebuilt import create_react_agent
from langgraph.checkpoint.memory import MemorySaver

# Tools are defined elsewhere; these should return LangChain/LangGraph-compatible tools
# Example: TOOL_BUILDERS["get_inventory"](custom, aws_region) -> BaseTool
from tool_registry import TOOL_BUILDERS

logger = logging.getLogger(__name__)
logging.basicConfig(
    level=logging.DEBUG if os.getenv("DEBUG_MODE", "false").lower() == "true" else logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

AGENT_KEY = os.getenv("LAUNCHDARKLY_AGENT_KEY", "pet-store-agent")

DEFAULT_AGENT = AIAgentConfigDefault(enabled=False)

@dataclass(frozen=True)
class RuntimeConfig:
    enabled: bool
    instructions: str
    model_name: str
    provider_name: str
    parameters: Dict[str, Any]
    custom: Dict[str, Any]
    variation_key: str
    tracker: Any  # LDAIConfigTracker

def _build_ld_context(user_ctx: Optional[Dict[str, Any]]) -> Context:
    user_ctx = user_ctx or {}
    key = user_ctx.get("user_id") or user_ctx.get("customer_id") or "anonymous"

    b = Context.builder(key).kind("user")
    for k, v in user_ctx.items():
        if v is None or k in ("user_id", "customer_id"):
            continue
        b.set(k, v)

    # If you pass email/etc, consider marking private in the SDK config or builder.
    if "email" in user_ctx:
        b.private("email")

    return b.build()

def _enabled_tool_names(rc: RuntimeConfig) -> Set[str]:
    # Prefer Agent API tool definitions in model.parameters.tools if present.
    tools = rc.parameters.get("tools") or []
    names = {t.get("name") for t in tools if isinstance(t, dict)}
    names.discard(None)

    # Allow an explicit override list in custom if you want it.
    if rc.custom.get("enabled_tools"):
        return set(rc.custom["enabled_tools"])
    return names

def _collect_token_usage(messages: List[Any]) -> Optional[TokenUsage]:
    inp = out = total = 0
    for m in messages:
        usage = getattr(m, "usage_metadata", None) or {}
        inp += int(usage.get("input_tokens", 0) or 0)
        out += int(usage.get("output_tokens", 0) or 0)
        total += int(usage.get("total_tokens", 0) or 0)

    return TokenUsage(input=inp, output=out, total=total) if total else None

def _safe_json(text: str) -> str:
    # Minimal “be forgiving” JSON wrapper; keep it simple.
    try:
        json.loads(text)
        return text
    except Exception:
        pass

    # Try to extract the first {...} block.
    start = text.find("{")
    end = text.rfind("}")
    if start != -1 and end != -1 and end > start:
        candidate = text[start : end + 1].strip()
        try:
            json.loads(candidate)
            return candidate
        except Exception:
            pass

    return json.dumps({"status": "Error", "message": "Invalid JSON response from model."})

class PetStoreAgent:
    def __init__(self) -> None:
        sdk_key = os.environ.get("LAUNCHDARKLY_SDK_KEY")
        if not sdk_key:
            raise RuntimeError("LAUNCHDARKLY_SDK_KEY is required (no fallback mode).")

        ldclient.set_config(LDConfig(sdk_key))
        self.ld = ldclient.get()
        if not self.ld.is_initialized():
            raise RuntimeError("LaunchDarkly SDK failed to initialize.")

        self.ai = LDAIClient(self.ld)
        self.checkpointer = MemorySaver()

    def resolve(self, user_ctx: Optional[Dict[str, Any]] = None) -> RuntimeConfig:
        ctx = _build_ld_context(user_ctx)

        # Keep variables tiny and deterministic.
        variables = {
            "customerType": "Subscribed" if (user_ctx or {}).get("subscription_status") in ("active", "premium") else "Guest",
            "userId": (user_ctx or {}).get("user_id") or "anonymous",
        }

        agent = self.ai.agent(
            AIAgentConfigRequest(
                key=AGENT_KEY,
                default_value=DEFAULT_AGENT,
                variables=variables
            ),
            ctx
        )

        # Access agent attributes directly as per LaunchDarkly Python AI SDK best practices
        # The agent object provides: enabled, instructions, model, provider, tracker
        # Model config uses private attributes _parameters and _custom
        parameters = agent.model._parameters if agent.model else {}
        custom = agent.model._custom if agent.model else {}

        # Log the custom config to see what's available
        logger.info(f"🔧 Global custom config from LaunchDarkly: {json.dumps(custom, default=str)[:500]}")

        # Log what we found for debugging
        if parameters.get("tools"):
            logger.info(f"✅ Found {len(parameters.get('tools', []))} tools in LaunchDarkly config")
            for tool in parameters.get("tools", []):
                if isinstance(tool, dict) and tool.get("name"):
                    logger.info(f"   - Tool: {tool.get('name')}")
        else:
            logger.warning("⚠️ No tools found in LaunchDarkly config at model.parameters.tools")

        return RuntimeConfig(
            enabled=bool(agent.enabled),
            instructions=agent.instructions or "",
            model_name=agent.model.name,
            provider_name=agent.provider.name,
            parameters=parameters,
            custom=custom,
            variation_key=getattr(agent, "variation_key", "default"),
            tracker=agent.tracker,
        )

    def build_tools(self, rc: RuntimeConfig) -> List[Any]:
        # Get tools configuration from LaunchDarkly parameters
        tool_configs = rc.parameters.get("tools", [])
        aws_region = rc.custom.get("aws_region", os.getenv("AWS_DEFAULT_REGION", "us-east-1"))

        tools: List[Any] = []

        # Build tools with their specific configurations from LaunchDarkly
        for tool_config in tool_configs:
            if not isinstance(tool_config, dict):
                continue

            name = tool_config.get("name")
            if not name:
                continue

            builder = TOOL_BUILDERS.get(name)
            if builder:
                # Log the full tool config to understand structure
                logger.debug(f"Full tool config for {name}: {json.dumps(tool_config, default=str)[:500]}")

                # Extract tool-specific parameters - they might be at different levels
                tool_custom = tool_config.get("custom", {})
                tool_params = tool_config.get("parameters", {})

                # Merge all configs: global custom, tool params, tool custom
                merged_config = {**rc.custom, **tool_params, **tool_custom}

                # Log detailed configuration
                logger.info(f"✅ Built tool '{name}'")
                logger.info(f"   Tool parameters: {json.dumps(tool_params, default=str)[:200] if tool_params else 'None'}")
                logger.info(f"   Tool custom: {json.dumps(tool_custom, default=str)[:200] if tool_custom else 'None'}")

                # Log specific important fields
                if name == "get_inventory":
                    logger.info(f"   Lambda config: use_real={merged_config.get('use_real_lambda')}, "
                               f"function={merged_config.get('lambda_inventory_function', 'Not set')}")
                elif name in ["get_user_by_email", "get_user_by_id"]:
                    logger.info(f"   Lambda config: use_real={merged_config.get('use_real_lambda')}, "
                               f"function={merged_config.get('lambda_user_function', 'Not set')}")
                else:
                    logger.info(f"   RAG config: storage_dir={merged_config.get('llamaindex_storage_dir')}, "
                               f"similarity_top_k={merged_config.get('llamaindex_similarity_top_k')}")

                tools.append(builder(merged_config, aws_region))

        if not tools:
            logger.warning("No tools enabled for this variation. Using fallback tools for testing.")
            # Add fallback tools for local testing
            if os.getenv("ENABLE_FALLBACK_TOOLS", "true").lower() == "true":
                logger.info("Enabling fallback tools with mock data")
                # Pass empty config for fallback mode (uses mock data)
                tools.append(TOOL_BUILDERS["get_inventory"]({}, aws_region))
                if "retrieve_product_info" in TOOL_BUILDERS:
                    tools.append(TOOL_BUILDERS["retrieve_product_info"]({}, aws_region))
        return tools

    def build_llm(self, rc: RuntimeConfig):
        # Keep provider mapping in one place if you need it (like your example does).
        temperature = rc.custom.get("temperature", rc.parameters.get("temperature", 0.7))
        max_tokens = rc.custom.get("max_tokens", rc.parameters.get("max_tokens", 4096))
        # Use AWS_DEFAULT_REGION if set, otherwise fall back to config or default
        aws_region = os.getenv("AWS_DEFAULT_REGION") or rc.custom.get("aws_region", "us-east-1")

        logger.info(f"Initializing LLM with model={rc.model_name}, provider={rc.provider_name}, region={aws_region}")

        # Handle Bedrock provider specially to ensure proper AWS credentials
        if rc.provider_name.lower() == "bedrock":
            from langchain_aws import ChatBedrockConverse

            # For Bedrock models, add cross-region inference profile prefix if needed
            model_id = rc.model_name
            if not model_id.startswith("us.") and not model_id.startswith("eu."):
                # Add cross-region prefix based on region
                if aws_region.startswith("us-"):
                    model_id = f"us.{model_id}"
                    logger.info(f"Added cross-region prefix: {model_id}")
                elif aws_region.startswith("eu-"):
                    model_id = f"eu.{model_id}"
                    logger.info(f"Added cross-region prefix: {model_id}")

            # Create boto3 session with explicit profile if set
            if os.environ.get('AWS_PROFILE'):
                logger.info(f"Using AWS Profile: {os.environ.get('AWS_PROFILE')}")
                boto_session = boto3.Session(
                    profile_name=os.environ.get('AWS_PROFILE'),
                    region_name=aws_region
                )
                bedrock_client = boto_session.client(
                    service_name='bedrock-runtime',
                    region_name=aws_region
                )
            else:
                # Use default credential chain
                bedrock_client = boto3.client(
                    service_name='bedrock-runtime',
                    region_name=aws_region
                )

            # Use ChatBedrockConverse directly with the configured client
            return ChatBedrockConverse(
                model=model_id,
                client=bedrock_client,
                temperature=temperature,
                max_tokens=max_tokens
            )
        else:
            # Use init_chat_model for other providers
            return init_chat_model(
                rc.model_name,
                model_provider=rc.provider_name,
                temperature=temperature,
                max_tokens=max_tokens,
                region_name=aws_region,
            )

    def invoke(self, prompt: str, user_ctx: Optional[Dict[str, Any]] = None) -> str:
        rc = self.resolve(user_ctx)
        if not rc.enabled:
            return json.dumps({"status": "Error", "message": "Service temporarily unavailable."})

        tools = self.build_tools(rc)
        llm = self.build_llm(rc)

        graph = create_react_agent(
            llm,
            tools,
            prompt=rc.instructions,
            checkpointer=self.checkpointer,  # enables thread_id persistence :contentReference[oaicite:6]{index=6}
        )

        thread_id = (user_ctx or {}).get("thread_id") or f"thread-{uuid4().hex}"
        input_ = {"messages": [HumanMessage(content=prompt)]}
        config = {"configurable": {"thread_id": thread_id}}

        tracker = rc.tracker
        try:
            logger.info(f"Invoking agent with {len(tools)} tools available")

            # Track duration manually as per LaunchDarkly Python AI SDK best practices
            import time
            start_time = time.time()
            result = graph.invoke(input_, config)
            duration_ms = int((time.time() - start_time) * 1000)

            tracker.track_duration(duration_ms)
            tracker.track_success()

            usage = _collect_token_usage(result.get("messages", []))
            if usage:
                tracker.track_tokens(usage)

            # Return last AI message as JSON (competition-style)
            msgs = result.get("messages", [])
            last_ai = next((m for m in reversed(msgs) if isinstance(m, AIMessage)), None)
            return _safe_json(last_ai.content if last_ai else "{}")
        except Exception as e:
            logger.error(f"Error during agent invocation: {str(e)}", exc_info=True)
            tracker.track_error()
            return json.dumps({"status": "Error", "message": "Temporary technical difficulties."})

# Alias for compatibility with query_agent.py
PetStoreAgentFullLD = PetStoreAgent

# Only create agent instance when handler is called (for Lambda)
_agent = None

def get_agent():
    global _agent
    if _agent is None:
        _agent = PetStoreAgent()
    return _agent

def handler(event, _context):
    prompt = event.get("prompt", "A new user is asking about the price of Doggy Delights?")
    user_ctx = {
        "user_id": event.get("user_id", "anonymous"),
        "customer_id": event.get("customer_id"),
        "subscription_status": event.get("subscription_status", "unknown"),
        "request_type": event.get("request_type", "product_inquiry"),
        "email": event.get("email"),
    }

    body = get_agent().invoke(prompt, user_ctx)

    # Flush analytics events for short-lived Lambda contexts
    # This ensures metrics are delivered to LaunchDarkly before the Lambda terminates
    ldclient.get().flush()

    return {"statusCode": 200, "body": body}
