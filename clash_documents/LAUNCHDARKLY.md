# LaunchDarkly AI Configs Setup & Optimization Challenge

## Workshop Tasks

### Task 1: Sign Up and Create Tokens
**Points: [POINTS]** | Estimated Time: 15 minutes

#### Objective
Sign up to LaunchDarkly, create tokens for MCP server and API calls (for score validation). Add token to MCP configuration in IDE and secrets manager.

#### Reference
- [LaunchDarkly MCP Server Documentation](https://launchdarkly.com/docs/home/getting-started/mcp)

#### Steps:

1. **Create LaunchDarkly Account**
   - Navigate to [LaunchDarkly signup](https://launchdarkly.com)
   - Complete registration process
   - Verify email and log in

2. **Generate Tokens**

   **A. API Access Token (for MCP Server):**
   - Navigate to **Organization Settings** (gear icon) → **Authorization**
   - In "Access tokens" section, click **Create token**

   ![Create API Token](images/api-token-create.png)

   - Name: `workshop-mcp-token`
   - Role: Select **Writer** or **LaunchDarkly Developer**
   - Use default API version (latest)
   - Leave "This is a service token" unchecked

   ![Name API Token](images/api-token-name.png)

   - Click **Save token**
   - **IMPORTANT**: Copy the token immediately - it's only shown once!

   ![Copy API Token](images/api-token-copy.png)

   - Save the API access token (starts with `api-`)
   - This will be used in your MCP server configuration

   **B. SDK Key (for Agent Code):**
   - Navigate to your project settings
   - Go to **Environments** → **Production**
   - Copy the SDK key (starts with `sdk-`)
   - This will be used in your agent code as `LAUNCHDARKLY_SDK_KEY`

   ![SDK Key Location](images/sdk-key.png)

3. **Configure MCP Server in IDE**
   - For Cursor: Update `~/.cursor/mcp.json`
   - For Claude Desktop: Update `claude_desktop_config.json`

   ```json
   {
     "mcpServers": {
       "LaunchDarkly": {
         "command": "npx",
         "args": [
           "-y", "--package", "@launchdarkly/mcp-server", "--", "mcp", "start",
           "--api-key", "api-xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx"
         ]
       }
     }
   }
   ```

   - Replace `api-xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx` with your API access token
   - Restart your AI client after updating
   - Enable the LaunchDarkly MCP server in your client settings

4. **Add SDK Key to AWS Secrets Manager**
   ```bash
   aws secretsmanager create-secret \
     --name "launchdarkly-sdk-key" \
     --secret-string "sdk-xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx" \
     --description "LaunchDarkly SDK key for workshop agent code"
   ```

#### Validation Checkpoint
- LaunchDarkly account active
- API access token generated (for MCP server)
- SDK key generated (for agent code)
- MCP server configured in IDE with API token
- SDK key stored in AWS Secrets Manager

---

### Task 2: Create New LD AI Config with Single Variation
**Points: [POINTS]** | Estimated Time: 20 minutes

#### Objective
Create a new LaunchDarkly AI config with a single variation. You can choose either the MCP approach (using your IDE) or the UI approach (using the web console).

#### Reference
- [MCP Getting Started Guide](https://launchdarkly.com/docs/home/getting-started/mcp)
- [AI Configs Documentation](https://docs.launchdarkly.com/ai)

Choose your preferred approach:

<details>
<summary><b>Option A: Using MCP Server in IDE</b> (Recommended for developers)</summary>

#### MCP Approach Steps:

1. **Ensure MCP Server is Running**
   - Verify your MCP server is configured in your IDE (from Task 1)
   - Check that LaunchDarkly MCP is connected

2. **Create AI Config via MCP**

   In your IDE, use this command:
   ```
   Create an AI Config in project pet-store-agent called "Pet Store Agent" with key pet-store-agent. Make it agent-based with a variation named base-config. Use AWS Bedrock with model us.amazon.nova-pro-v1:0, temperature 0.7, and max tokens 4096. Set the instructions to: "You are an online pet store assistant for staff. Your job is to analyze customer inputs, use the provided external tools and data sources as required, and then respond in json-only format following the schema. Always maintain a warm and friendly tone in user message and pet advice fields." Then enable targeting in the production environment to serve the base-config variation by default.
   ```

3. **Verify Creation**
   - The MCP server should confirm the AI Config was created
   - You can check the LaunchDarkly dashboard to verify

4. **Test with MCP**
   - Send test prompt through MCP:
   ```
   Test the pet-store-agent config with: "A new user is asking about the price of Doggy Delights?"
   ```
   - Verify the response format

</details>

<details>
<summary><b>Option B: Using LaunchDarkly UI</b> (Visual approach)</summary>

#### UI Approach Steps:

1. **Access AI Configs**
   - In LaunchDarkly dashboard sidebar, navigate to **AI Configs**
   - Click **Create AI Config**
   - Select `🤖 Agent-based` configuration type to enter instructions

2. **Configure Your AI Config**
   - **Name**: Pet Store Agent
   - **Variation name**: `base-config`
   - **Key**: `pet-store-agent` (this will be the key you reference in your code)

3. **Set Model Configuration**
   - **Model provider**: Select `AWS Bedrock`
   - **Model**: Choose `us.amazon.nova-pro-v1:0`
   - **Parameters**:
     - Click **Add parameters**
     - Temperature: `0.7`
     - Max tokens: `4096`

4. **Configure Agent Instructions**
   In the **Goal or task** field, enter:
   ```
   You are an online pet store assistant for staff. Your job is to analyze customer inputs, use the provided external tools and data sources as required, and then respond in json-only format following the schema. Always maintain a warm and friendly tone in user message and pet advice fields.
   ```

5. **Review and Save**
   - Click **Review and save**
   - Verify all settings are correct
   - Click **Save**

6. **Enable the AI Config**
   - Switch to the **Targeting** tab
   - Click **Edit** on the Default rule
   - Change it to serve your `base-config` variation
   - Add a note like "Enabling pet store agent config"
   - Type "Production" to confirm
   - Click **Save**

7. **Test in Console**
   - Navigate to the **Test** tab in your AI Config
   - Enter test prompt: "A new user is asking about the price of Doggy Delights?"
   - Click **Test** and verify response

</details>

#### Validation Checkpoint
- AI Config created in LaunchDarkly
- Single variation configured and enabled
- Default rule serving your variation
- Successful test through MCP

---

### Task 3: Create New LD AI Config Variation with Different Model
**Points: [POINTS]** | Estimated Time: 15 minutes

#### Objective
Add new variations to your AI Config with different models. You can choose either the MCP approach (using your IDE) or the UI approach (using the web console).

#### Reference
- [AI Config Variations](https://docs.launchdarkly.com/ai#variations)
- [Percentage Rollouts](https://docs.launchdarkly.com/home/flags/rollouts)

Choose your preferred approach:

<details>
<summary><b>Option A: Using MCP Server in IDE</b> (Recommended for developers)</summary>

#### MCP Approach Steps:

1. **Add Claude Sonnet Variation via MCP**

   In your IDE, use this command:
   ```
   Add a variation to the pet-store-agent config called claude-sonnet. Use AWS Bedrock with model anthropic.claude-3-sonnet-20240229-v1:0, temperature 0.5, and max tokens 4096. Keep the same instructions as the base variation.
   ```

2. **Add Claude Haiku Variation via MCP**

   Continue with:
   ```
   Add another variation to the pet-store-agent config called claude-haiku. Use AWS Bedrock with model anthropic.claude-3-haiku-20240307-v1:0, temperature 0.3, and max tokens 1000 for cost optimization. Keep the same instructions.
   ```

3. **Configure Percentage Rollout via MCP**

   Set up the distribution:
   ```
   Update the pet-store-agent config targeting in production. Set the default rule to percentage rollout with: base-config at 50%, claude-sonnet at 30%, and claude-haiku at 20%.
   ```

4. **Test Variations via MCP**

   Send multiple test prompts to verify distribution:
   ```
   Test the pet-store-agent config 10 times with: "What products do you have for cats?" and tell me which variation was used each time.
   ```

5. **Verify in Dashboard**
   - Check the LaunchDarkly dashboard to confirm variations
   - View the Monitoring tab for distribution metrics

</details>

<details>
<summary><b>Option B: Using LaunchDarkly UI</b> (Visual approach)</summary>

#### UI Approach Steps:

1. **Navigate to Your AI Config**
   - In LaunchDarkly dashboard, go to **AI Configs**
   - Click on your `pet-store-agent` config
   - Click the **Variations** tab

2. **Add Claude Sonnet Variation**
   - Click **+ Add variation**
   - **Variation name**: `claude-sonnet`
   - **Model provider**: Select `Anthropic` (or `AWS Bedrock`)
   - **Model**: Choose `anthropic.claude-3-sonnet-20240229-v1:0`
   - **Parameters**:
     - Click **Add parameters**
     - Temperature: `0.5`
     - Max tokens: `4096`
   - Keep the same Goal/Task instructions from base variation
   - Click **Save variation**

3. **Add Claude Haiku Variation**
   - Click **+ Add variation** again
   - **Variation name**: `claude-haiku`
   - **Model provider**: Select `Anthropic` (or `AWS Bedrock`)
   - **Model**: Choose `anthropic.claude-3-haiku-20240307-v1:0`
   - **Parameters**:
     - Click **Add parameters**
     - Temperature: `0.3` (lower for more consistent responses)
     - Max tokens: `1000` (cost optimization)
   - Keep the same Goal/Task instructions
   - Click **Save variation**

4. **Configure Percentage Rollout**
   - Switch to the **Targeting** tab
   - Click **Edit** on the Default rule
   - Change from single variation to **Percentage rollout**
   - Set allocation:
     - `base-config` (Nova Pro): 50%
     - `claude-sonnet`: 30%
     - `claude-haiku`: 20%
   - Add note: "Testing model performance distribution"
   - Type "Production" to confirm
   - Click **Save**

5. **Test Different Variations**
   - Navigate to the **Test** tab
   - Send multiple test prompts (at least 10)
   - Note which variation is used each time
   - Check the **Monitoring** tab to see variation distribution

</details>

#### Validation Checkpoint
- Three variations created with different models
- Each variation has distinct parameters
- Percentage rollout configured and active
- Traffic being distributed according to percentages

---

### Task 4: Update Target LD AI Config
**Points: [POINTS]** | Estimated Time: 20 minutes

#### Objective
Update target LaunchDarkly AI Config with advanced targeting rules using IDE agent + MCP. Learn more about [targeting in the LaunchDarkly AI Configs documentation](https://docs.launchdarkly.com/ai).

#### Steps:

1. **Navigate to Targeting**
   - Open your `pet-store-agent` AI Config
   - Click the **Targeting** tab
   - You'll see the Default rule from Task 3

2. **Add Premium Users Rule**
   - Click **+ Add rule** above the Default rule
   - **Name**: "Premium Users"
   - Click **+ Add condition**
   - Configure:
     - **Attribute**: `subscription_status`
     - **Operator**: `is one of`
     - **Values**: Enter `premium` and press Enter
   - **Serve**: Select `claude-sonnet` variation
   - Click **Save**

3. **Add Simple Queries Rule**
   - Click **+ Add rule** again
   - **Name**: "Simple Queries"
   - Click **+ Add condition**
   - Configure:
     - **Attribute**: `query_complexity`
     - **Operator**: `is one of`
     - **Values**: Enter `simple` and press Enter
   - **Serve**: Select `claude-haiku` variation
   - Click **Save**

4. **Add High Complexity Rule**
   - Click **+ Add rule**
   - **Name**: "High Complexity Paid Users"
   - Click **+ Add condition** (First condition):
     - **Attribute**: `query_complexity`
     - **Operator**: `is one of`
     - **Values**: Enter `high`
   - Click **+ Add condition** (Second condition):
     - **Attribute**: `subscription_status`
     - **Operator**: `is one of`
     - **Values**: Enter `active` and `premium`
   - **Condition logic**: Ensure it's set to "AND"
   - **Serve**: Select `claude-sonnet` variation
   - Click **Save**

5. **Verify Rule Order**
   Rules are evaluated top to bottom:
   1. Premium Users → `claude-sonnet`
   2. Simple Queries → `claude-haiku`
   3. High Complexity Paid Users → `claude-sonnet`
   4. Default → Percentage rollout

6. **Test with Different Contexts**
   ```python
   # Test contexts for your agent code
   contexts = [
     {"key": "user-1", "subscription_status": "premium"},
     {"key": "user-2", "query_complexity": "simple"},
     {"key": "user-3", "subscription_status": "active", "query_complexity": "high"},
     {"key": "user-4", "subscription_status": "guest"}
   ]
   ```

#### Validation Checkpoint
- Three targeting rules created above default
- Rules evaluate user attributes
- Each rule serves specific variation
- Default rule handles all other cases

---

### Task 5: Instrument Agent with LD AI Configs SDK
**Points: [POINTS]** | Estimated Time: 30 minutes

#### Objective
Instrument [LangGraph](https://python.langchain.com/docs/langgraph)/[LlamaIndex](https://docs.llamaindex.ai/)/Custom agent with LaunchDarkly AI Configs SDK using coding agent of your IDE choice.

#### Steps:

1. **Choose Your Implementation**
   - [ ] [LangGraph Agent](https://python.langchain.com/docs/langgraph) - Multi-agent orchestration
   - [ ] [LlamaIndex Agent](https://docs.llamaindex.ai/) - RAG-focused agent
   - [ ] Custom Agent - Your own implementation

2. **Install Dependencies**
   ```bash
   pip install launchdarkly-server-sdk launchdarkly-ai
   ```

3. **Implement LaunchDarkly Integration**

   Choose the integration approach that matches your agent framework:

<details>
<summary><b>Basic Integration Example</b> (Simple LLM wrapper)</summary>

```python
import os
import ldclient
from ldclient import Context
from ldai.client import LDAIClient
from ldai.tracker import TokenUsage

class SimpleAgent:
    def __init__(self):
        # Initialize LaunchDarkly
        sdk_key = os.environ.get('LAUNCHDARKLY_SDK_KEY')
        config = ldclient.Config(sdk_key)
        ldclient.set_config(config)
        self.ld_client = ldclient.get()

        # Wait for initialization
        if self.ld_client.wait_for_initialization(5):
            self.ai_client = LDAIClient(self.ld_client)
            print("LaunchDarkly initialized successfully")

    def process_request(self, prompt: str, user_context: dict):
        # Build LaunchDarkly context
        context_builder = Context.builder(user_context.get("user_id", "anonymous"))

        for key, value in user_context.items():
            if key != "user_id":
                context_builder.set(key, value)

        ld_context = context_builder.build()

        # Get AI configuration
        config, tracker = self.ai_client.config(
            "pet-store-agent",
            ld_context,
            fallback_config={"enabled": True, "model": {"name": "us.amazon.nova-pro-v1:0"}}
        )

        # Use configuration to process request
        response = self.generate_response(prompt, config)

        # Track metrics
        tracker.track_success()
        tracker.track_tokens(TokenUsage(input=100, output=200, total=300))

        return response
```

</details>

<details>
<summary><b>Production LangGraph Agent Integration</b> (Competition-ready implementation)</summary>

```python
import os
import json
import logging
from dataclasses import dataclass
from typing import Any, Dict, Optional, List, Set
from uuid import uuid4

import boto3
import ldclient
from ldclient import Context
from ldclient.config import Config as LDConfig

from ldai.client import LDAIClient, AIAgentConfigDefault, ModelConfig, ProviderConfig
from ldai.tracker import TokenUsage

from langchain_aws import ChatBedrockConverse
from langchain_core.messages import HumanMessage, AIMessage
from langgraph.prebuilt import create_react_agent
from langgraph.checkpoint.memory import MemorySaver

# Import your tool builders
from tool_registry import TOOL_BUILDERS

logger = logging.getLogger(__name__)

AGENT_KEY = os.getenv("LAUNCHDARKLY_AGENT_KEY", "pet-store-agent")

DEFAULT_AGENT = AIAgentConfigDefault(
    enabled=False,
    model=ModelConfig("ERROR_MODEL_NOT_CONFIGURED"),
    provider=ProviderConfig("ERROR_PROVIDER_NOT_CONFIGURED"),
    instructions="ERROR: LaunchDarkly AI Config not found or disabled.",
)

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

class PetStoreAgent:
    def __init__(self) -> None:
        sdk_key = os.environ.get("LAUNCHDARKLY_SDK_KEY")
        if not sdk_key:
            raise RuntimeError("LAUNCHDARKLY_SDK_KEY is required")

        ldclient.set_config(LDConfig(sdk_key))
        self.ld = ldclient.get()
        if not self.ld.is_initialized():
            raise RuntimeError("LaunchDarkly SDK failed to initialize")

        self.ai = LDAIClient(self.ld)
        self.checkpointer = MemorySaver()

    def resolve(self, user_ctx: Optional[Dict[str, Any]] = None) -> RuntimeConfig:
        """Resolve LaunchDarkly configuration for the current context"""
        # Build context with user attributes
        key = (user_ctx or {}).get("user_id", "anonymous")
        b = Context.builder(key).kind("user")

        for k, v in (user_ctx or {}).items():
            if v is not None and k != "user_id":
                b.set(k, v)

        if "email" in (user_ctx or {}):
            b.private("email")  # Mark email as private

        ctx = b.build()

        # Variables for prompt templates
        variables = {
            "customerType": "Subscribed" if (user_ctx or {}).get("subscription_status") in ("active", "premium") else "Guest",
            "userId": key,
        }

        # Get agent configuration from LaunchDarkly
        agent = self.ai.agent_config(
            AGENT_KEY,
            ctx,
            default_value=DEFAULT_AGENT,
            variables=variables,
        )

        # Extract configuration from agent
        agent_dict = agent.to_dict() if hasattr(agent, 'to_dict') else {}
        model_config = agent_dict.get("model", {})
        parameters = model_config.get("parameters", {})
        custom = model_config.get("custom", {})

        # Log available tools
        if parameters.get("tools"):
            logger.info(f"✅ Found {len(parameters.get('tools', []))} tools in LaunchDarkly config")
            for tool in parameters.get("tools", []):
                if isinstance(tool, dict) and tool.get("name"):
                    logger.info(f"   - Tool: {tool.get('name')}")

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
        """Build LangChain tools from LaunchDarkly configuration"""
        tool_configs = rc.parameters.get("tools", [])
        aws_region = rc.custom.get("aws_region", os.getenv("AWS_DEFAULT_REGION", "us-east-1"))

        tools: List[Any] = []

        for tool_config in tool_configs:
            if not isinstance(tool_config, dict):
                continue

            name = tool_config.get("name")
            if not name or name not in TOOL_BUILDERS:
                continue

            # Merge configurations: global custom + tool-specific
            tool_custom = tool_config.get("custom", {})
            tool_params = tool_config.get("parameters", {})
            merged_config = {**rc.custom, **tool_params, **tool_custom}

            # Build the tool with merged configuration
            tools.append(TOOL_BUILDERS[name](merged_config, aws_region))

            logger.info(f"✅ Built tool '{name}'")

            # Log Lambda configuration for Lambda-based tools
            if name == "get_inventory":
                logger.info(f"   Lambda: {merged_config.get('lambda_inventory_function', 'Not configured')}")
            elif name in ["get_user_by_email", "get_user_by_id"]:
                logger.info(f"   Lambda: {merged_config.get('lambda_user_function', 'Not configured')}")
            else:
                # RAG tools
                logger.info(f"   Storage: {merged_config.get('llamaindex_storage_dir', './storage')}")

        return tools

    def build_llm(self, rc: RuntimeConfig):
        """Build LLM from LaunchDarkly configuration"""
        temperature = rc.parameters.get("temperature", 0.7)
        max_tokens = rc.parameters.get("max_tokens", 4096)
        aws_region = rc.custom.get("aws_region", "us-east-1")

        logger.info(f"Initializing LLM: {rc.model_name} via {rc.provider_name}")

        if rc.provider_name.lower() == "bedrock":
            # Use AWS Bedrock
            bedrock_client = boto3.client(
                service_name='bedrock-runtime',
                region_name=aws_region
            )

            return ChatBedrockConverse(
                model=rc.model_name,
                client=bedrock_client,
                temperature=temperature,
                max_tokens=max_tokens
            )
        else:
            # Use other providers via init_chat_model
            from langchain.chat_models import init_chat_model
            return init_chat_model(
                rc.model_name,
                model_provider=rc.provider_name,
                temperature=temperature,
                max_tokens=max_tokens,
            )

    def invoke(self, prompt: str, user_ctx: Optional[Dict[str, Any]] = None) -> str:
        """Process a request using the LangGraph agent"""
        # Get configuration from LaunchDarkly
        rc = self.resolve(user_ctx)
        if not rc.enabled:
            return json.dumps({"status": "Error", "message": "Service temporarily unavailable."})

        # Build tools and LLM from configuration
        tools = self.build_tools(rc)
        llm = self.build_llm(rc)

        # Create LangGraph ReAct agent
        graph = create_react_agent(
            llm,
            tools,
            prompt=rc.instructions,  # Instructions from LaunchDarkly
            checkpointer=self.checkpointer,
        )

        # Execute the agent
        thread_id = (user_ctx or {}).get("thread_id") or f"thread-{uuid4().hex}"
        input_ = {"messages": [HumanMessage(content=prompt)]}
        config = {"configurable": {"thread_id": thread_id}}

        tracker = rc.tracker
        try:
            # Track execution duration
            result = tracker.track_duration_of(lambda: graph.invoke(input_, config))
            tracker.track_success()

            # Collect and track token usage
            usage = self._collect_token_usage(result.get("messages", []))
            if usage:
                tracker.track_tokens(usage)

            # Extract last AI message as JSON response
            msgs = result.get("messages", [])
            last_ai = next((m for m in reversed(msgs) if isinstance(m, AIMessage)), None)

            return self._safe_json(last_ai.content if last_ai else "{}")

        except Exception as e:
            logger.error(f"Error during agent invocation: {str(e)}", exc_info=True)
            tracker.track_error()
            return json.dumps({"status": "Error", "message": "Temporary technical difficulties."})

    def _collect_token_usage(self, messages: List[Any]) -> Optional[TokenUsage]:
        """Collect token usage from LangChain messages"""
        inp = out = total = 0
        for m in messages:
            usage = getattr(m, "usage_metadata", None) or {}
            inp += int(usage.get("input_tokens", 0) or 0)
            out += int(usage.get("output_tokens", 0) or 0)
            total += int(usage.get("total_tokens", 0) or 0)

        return TokenUsage(input=inp, output=out, total=total) if total else None

    def _safe_json(self, text: str) -> str:
        """Ensure response is valid JSON"""
        try:
            json.loads(text)
            return text
        except:
            # Try to extract JSON from text
            start = text.find("{")
            end = text.rfind("}")
            if start != -1 and end != -1:
                candidate = text[start:end+1]
                try:
                    json.loads(candidate)
                    return candidate
                except:
                    pass
            return json.dumps({"status": "Error", "message": "Invalid JSON response."})
```

**Key Features of This Implementation:**
- ✅ Dynamic tool configuration from LaunchDarkly
- ✅ Model selection based on targeting rules
- ✅ Instructions/prompts from AI Config
- ✅ Token usage tracking
- ✅ Error tracking and metrics
- ✅ Thread/conversation management
- ✅ Support for Lambda functions and RAG tools
- ✅ Fallback configuration when LD is unavailable

</details>

4. **Test the Integration**
   - Run your agent with test prompts
   - Verify LaunchDarkly configuration is being retrieved
   - Check that different contexts receive appropriate variations

#### Validation Checkpoint
- Agent instrumented with LaunchDarkly SDK
- Configuration retrieval working
- Metrics tracking implemented

---

### Task 6: Send Prompt Messages and Check Monitoring (Optional)
**Points: [POINTS]** | Estimated Time: 15 minutes

#### Objective
Send prompt messages using different contexts and check LaunchDarkly AI Config Monitoring in console.

#### Steps:

1. **Execute Test Prompts**
   ```python
   test_cases = [
       {
           "prompt": "A new user is asking about the price of Doggy Delights?",
           "context": {
               "user_id": "guest-001",
               "subscription_status": "guest",
               "query_complexity": "simple"
           }
       },
       {
           "prompt": "I need detailed care instructions for a Chihuahua puppy",
           "context": {
               "user_id": "premium-001",
               "subscription_status": "premium",
               "query_complexity": "high"
           }
       },
       {
           "prompt": "Do you have cat toys in stock?",
           "context": {
               "user_id": "regular-001",
               "subscription_status": "active",
               "query_complexity": "medium"
           }
       }
   ]

   for test in test_cases:
       response = agent.process_request(test["prompt"], test["context"])
       print(f"User: {test['context']['user_id']}")
       print(f"Response: {response[:200]}...\n")
   ```

2. **Check Monitoring Dashboard**
   - Navigate to LaunchDarkly → AI Configs → `pet-store-agent`
   - Click **Monitoring** tab
   - Observe:
     - Request volume by variation
     - Token usage per model
     - Response times
     - Error rates

3. **Verify Targeting**
   - Check that premium users got Claude Sonnet
   - Verify simple queries used Claude Haiku
   - Confirm default users got percentage rollout

#### Validation Checkpoint
- Test prompts executed successfully
- Metrics visible in monitoring dashboard
- Targeting rules working as expected

---

### Task 7: Create a LaunchDarkly AI Experiment
**Points: [POINTS]** | Estimated Time: 20 minutes

#### Objective
Create a LaunchDarkly AI Experiment to compare model performance. Learn more about [LaunchDarkly experiments in the documentation](https://docs.launchdarkly.com/home/experimentation).

#### Steps:

1. **Navigate to Your AI Config**
   - Open your `pet-store-agent` AI Config
   - In the right navigation menu, click the **+** sign next to **Experiments**
   - Select **Create new experiment**

2. **Configure Experiment Design**
   - **Experiment type**: Keep `Feature change` selected
   - **Name**: `Pet Store Agent Model Performance`
   - **Hypothesis**:
     ```
     Claude Sonnet will provide higher quality responses than Nova Pro for complex queries, justifying the higher cost with improved user satisfaction
     ```

3. **Set Up Metrics**
   - **Randomize by**: Select `user`
   - Click **Select metrics or metric groups**
   - Add metrics in this order:
     1. `Positive feedback rate` (set as Primary by adding first)
     2. `Negative feedback rate`
     3. `p95_total_user_latency` (if configured)
     4. `ai_cost_per_request` (if configured)

4. **Configure Audience Targeting**
   - **Flag or AI Config**: Should auto-select `pet-store-agent`
   - **Targeting rule**: Select **Default rule**
   - This ensures all users participate in the experiment

5. **Set Audience Allocation**
   - **Variations served outside experiment**: `base-config`
   - **Sample size**: `100%` of users in experiment
   - Click **Edit** on Variations split:
     - First, scroll down and set **Control** to `base-config`
     - Then allocate:
       - `base-config` (Nova Pro): `50%`
       - `claude-sonnet`: `50%`
       - `claude-haiku`: `0%`

6. **Configure Success Criteria**
   - **Statistical approach**: `Bayesian`
   - **Threshold**: `90%` (or `95%` for higher confidence)
   - This means you need 90% confidence that the treatment is better

7. **Launch Experiment**
   - Click **Save**
   - Review all settings
   - Click **Start experiment**
   - Confirm by typing the environment name

#### Validation Checkpoint
- Experiment created and running
- Metrics properly configured with primary metric
- 50/50 split between control and treatment
- Bayesian analysis enabled

---

### Task 8: Send Messages and Check Experiment Metrics (Optional)
**Points: [POINTS]** | Estimated Time: 20 minutes

#### Objective
Send prompt messages and check LaunchDarkly AI Experiment metrics in console for end-to-end testing.

#### Steps:

1. **Generate Experiment Traffic**
   ```python
   import random
   import time
   from ldclient import Context

   # Assuming you have initialized your agent
   agent = PetStoreAgent()  # or PetStoreAgentFullLD()

   # Generate varied test traffic
   for i in range(50):
       user_id = f"experiment-user-{i:03d}"

       # Randomly assign user attributes
       subscription = random.choice(["guest", "active", "premium"])
       complexity = random.choice(["simple", "medium", "high"])

       user_context = {
           "user_id": user_id,
           "subscription_status": subscription,
           "query_complexity": complexity,
           "experiment_participant": True
       }

       # Varied prompts (matching competition requirements)
       prompts = [
           "What's the price of Doggy Delights?",
           "How should I care for a new kitten?",
           "Tell me about your cat products",
           "I need food for my dog",
           "How often should I bathe my Chihuahua?"
       ]

       prompt = random.choice(prompts)

       # Invoke the agent
       response = agent.invoke(prompt, user_context)

       # Build LaunchDarkly context for tracking
       ld_context = Context.builder(user_id).kind("user")
       for key, value in user_context.items():
           if key != "user_id":
               ld_context.set(key, value)
       ld_context = ld_context.build()

       # Parse response to determine quality
       try:
           import json
           response_json = json.loads(response)

           # Quality score based on response status and content
           if response_json.get("status") == "Accept":
               # Higher quality if response has items or advice
               if response_json.get("items") or response_json.get("petAdvice"):
                   quality_score = random.uniform(0.8, 1.0)
               else:
                   quality_score = random.uniform(0.7, 0.9)
           elif response_json.get("status") == "Reject":
               # Correct rejection (e.g., for bird/guinea pig requests)
               if any(x in prompt.lower() for x in ["bird", "guinea pig"]):
                   quality_score = 1.0  # Correct rejection
               else:
                   quality_score = 0.3  # Incorrect rejection
           else:
               quality_score = 0.1  # Error response

       except:
           quality_score = 0.1  # Failed to parse response

       # Track experiment metric using the agent's LD client
       agent.ld.track(
           "response_quality_score",
           ld_context,
           {"score": quality_score, "prompt": prompt[:100]},
           quality_score
       )

       # Also track response time (simulated)
       response_time = random.uniform(0.5, 2.5)  # seconds
       agent.ld.track(
           "response_time_ms",
           ld_context,
           {"time_ms": response_time * 1000},
           response_time * 1000
       )

       print(f"User {i+1}/50: Quality={quality_score:.2f}, Response Time={response_time:.2f}s")

       time.sleep(1)  # Rate limiting
   ```

2. **Monitor Experiment Progress**
   - Navigate to your experiment in LaunchDarkly
   - Check **Results** tab
   - Monitor:
     - Sample size accumulation
     - Metric trends
     - Statistical significance
     - Confidence intervals

3. **Analyze Results**
   - **Performance Comparison**:
     - Control vs Treatment quality scores
     - Token usage differences
     - Response time variations

   - **Statistical Analysis**:
     - P-value for significance
     - Confidence intervals
     - Effect size

4. **Document Findings**
   - Winner: [Model Name]
   - Quality improvement: X%
   - Cost impact: $Y per 1000 requests
   - Recommendation: [Roll out / Iterate / Abandon]

#### Validation Checkpoint
- 50+ experiment samples collected
- Metrics visible in experiment dashboard
- Statistical analysis available
- Clear winner or learning identified

---

## Bonus Objectives

### Advanced Features (Points TBD per feature)
- [ ] Implement automatic fallback for model failures
- [ ] Add custom quality scoring based on response analysis
- [ ] Create real-time monitoring dashboard
- [ ] Implement cost optimization based on query complexity
- [ ] Setup alerting for performance degradation
- [ ] Build A/B testing framework for prompt variations using [LaunchDarkly's Multi-Agent Tutorial](https://github.com/launchdarkly-labs/devrel-agents-tutorial)

---

## Resources & Documentation

### Essential Documentation
- **[LaunchDarkly AI Configs](https://docs.launchdarkly.com/ai)** - Complete guide to AI configuration management
- **[Quickstart for AI Configs](https://docs.launchdarkly.com/ai/quickstart)** - Get started with LaunchDarkly AI Configs
- **[MCP Server Setup](https://launchdarkly.com/docs/home/getting-started/mcp)** - Model Context Protocol integration guide
- **[AWS Bedrock Models](https://docs.aws.amazon.com/bedrock/)** - Available models and pricing

### Workshops & Tutorials
- **[LaunchDarkly AI Config with Amazon Bedrock Workshop](https://catalog.workshops.aws/launchdarkly-ai-config-bedrock/en-US)** - AWS Workshop Studio hands-on lab
  - Dynamic prompt building with Amazon Bedrock
  - Step-by-step implementation guide
  - Available for customer instances on request
- **[Multi-Agent Tutorial Repository](https://github.com/launchdarkly-labs/devrel-agents-tutorial)** - Complete working examples
- **[AWS Clash Pet Store Agent](https://github.com/launchdarkly-labs/aws-clash)** - Production-ready LangGraph agent
  - Full agent implementation with dynamic configuration
  - Tool registry pattern for modular tools
  - LlamaIndex RAG integration
  - AgentCore deployment notebook

### Blog Posts & Articles
- **[Creating Better Runtime Control with LaunchDarkly and AWS](https://launchdarkly.com/blog/runtime-control-launchdarkly-aws/)** - Ship bold AI changes without the guesswork

### Framework Documentation
- **[LangGraph Documentation](https://python.langchain.com/docs/langgraph)** - Multi-agent orchestration framework
- **[LlamaIndex Documentation](https://docs.llamaindex.ai/)** - RAG and retrieval framework

### Additional Resources
- **[LaunchDarkly + AWS One Pager](https://launchdarkly.com/resources)** - Quick overview of integration benefits
- **[LaunchDarkly Experimentation](https://docs.launchdarkly.com/home/experimentation)** - A/B testing and experiment setup