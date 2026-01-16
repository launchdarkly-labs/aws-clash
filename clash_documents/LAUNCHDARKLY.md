# AI Experimentation with LaunchDarkly

<figure style="margin: 20px 0;">
  <img src="images/launchdarkly.png" alt="LaunchDarkly Logo" width="600" style="border: 1px solid #ddd; border-radius: 4px; padding: 5px;">
  <figcaption style="margin-top: 8px; font-style: italic; color: #666; text-align: center;">LaunchDarkly Logo</figcaption>
</figure>

LaunchDarkly's AI Configs let you swap models, tweak prompts, and test different configurations **without redeploying code**. Think of it as A/B testing for AI - change your model from Claude to GPT to Llama, adjust parameters on the fly, and see which setup actually performs best with real data. You can target specific users ("premium customers get the fancy model"), run controlled experiments, and track token efficiency. Make changes in a web UI and your agent instantly picks them up. No more guessing which model is best or hardcoding configurations. Just experiment, measure, and ship the winner. 🚀

## What You'll Build

Your mission: Figure out which AI model is most token-efficient for your Pet Store agent. Instead of guessing, you'll run a proper experiment with real data. Set up two (or more!) model variations, split traffic between them, and let the metrics tell you which one uses tokens more efficiently.

## What Success Looks Like

By the end, you'll have:
- ✅ LaunchDarkly account hooked up and ready to roll
- ✅ An AI Config with at least 2 different model variations
- ✅ Your agent code instrumented to grab configs from LaunchDarkly
- ✅ A live experiment collecting real token usage data
- ✅ Actual metrics showing which model is more efficient

**Pro tip:** This is one of the more straightforward competition sections - most of the code patterns are already written for you. Plus, you get to play with multiple AI models without writing a ton of code. Win-win!

## Build Your First AI Experiment: LaunchDarkly Demo

**PLACEHOLDER FOR SCARLETT'S VIDEO**

---

## Steps

### 1. Get Your LaunchDarkly Account Set Up

#### Quick Token Explainer

You'll need two kinds of keys (don't worry, it's simple):
- **API Access Token** (starts with `api-`): Lets your IDE talk to LaunchDarkly to create and edit AI Configs
- **SDK Key** (starts with `sdk-`): Your agent uses this to fetch configs at runtime

Grab both and you're golden. 👍

**1a.** Create your LaunchDarkly account if you don't have one by going to [LaunchDarkly's signup page](https://launchdarkly.com)

**1b.** Generate a LaunchDarkly API Access Token for MCP server and API calls
- Navigate to **Organization Settings** → **Authorization** → **Create token**
- **Name**: `workshop-mcp-token` (or any descriptive name)
- **Role**: Select **Writer** or **LaunchDarkly Developer** 
- Copy and save this token immediately (only shown once)

For detailed instructions, see [Creating API access tokens](https://docs.launchdarkly.com/home/account-security/api-access-tokens#creating-api-access-tokens)

<figure style="margin: 20px 0;">
  <img src="images/api-token-create.png" alt="Create API Token" width="600" style="border: 1px solid #ddd; border-radius: 4px; padding: 5px;">
  <figcaption style="margin-top: 8px; font-style: italic; color: #666; text-align: center;">Creating a new API access token</figcaption>
</figure>

<figure style="margin: 20px 0;">
  <img src="images/api-token-name.png" alt="Name API Token" width="600" style="border: 1px solid #ddd; border-radius: 4px; padding: 5px;">
  <figcaption style="margin-top: 8px; font-style: italic; color: #666; text-align: center;">Configuring token name and role</figcaption>
</figure>

<figure style="margin: 20px 0;">
  <img src="images/api-token-copy.png" alt="Copy API Token" width="600" style="border: 1px solid #ddd; border-radius: 4px; padding: 5px;">
  <figcaption style="margin-top: 8px; font-style: italic; color: #666; text-align: center;">Copying the API token (shown only once)</figcaption>
</figure>

**1c.** Retrieve the LaunchDarkly SDK Key from your environment
- Navigate to **Project settings** → **Environments** → Select your environment
- Copy the **SDK key** (starts with `sdk-`)

For more details, see [Finding your SDK key](https://docs.launchdarkly.com/sdk/concepts/client-side-server-side#keys)

<figure style="margin: 20px 0;">
  <img src="images/project_settings.png" alt="Access Project Settings" width="600" style="border: 1px solid #ddd; border-radius: 4px; padding: 5px;">
  <figcaption style="margin-top: 8px; font-style: italic; color: #666; text-align: center;">Accessing project settings from the sidebar</figcaption>
</figure>

<figure style="margin: 20px 0;">
  <img src="images/image3.png" alt="Environments View" width="600" style="border: 1px solid #ddd; border-radius: 4px; padding: 5px;">
  <figcaption style="margin-top: 8px; font-style: italic; color: #666; text-align: center;">Copy the SDK key from the environment settings</figcaption>
</figure>

**1d.** Store the LaunchDarkly SDK Key securely
- Add to AWS Secrets Manager in your AWS Account, OR
- Set as environment variable: `export LAUNCHDARKLY_SDK_KEY="sdk-xxxxx"`

**1e.** Configure LaunchDarkly MCP server in your IDE (optional but recommended)

The Model Context Protocol (MCP) enables AI-powered IDEs to interact with LaunchDarkly using natural language. Learn more at [LaunchDarkly MCP Documentation](https://docs.launchdarkly.com/home/getting-started/mcp).

**Initial Setup:**

Create/update your IDE's MCP configuration file:
- **For Cursor**: `~/.cursor/mcp.json`
- **For Claude Desktop**: `claude_desktop_config.json`
- **For AWS Kiro**: See [Kiro IDE documentation](https://kiro.dev/)

```json
{
  "mcpServers": {
    "LaunchDarkly": {
      "command": "npx",
      "args": [
        "-y",
        "--package",
        "@launchdarkly/mcp-server",
        "--",
        "mcp",
        "start",
        "--api-key",
        "api-xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx"
      ]
    }
  }
}
```

**To Edit/Update MCP Configuration:**
1. Open your MCP configuration file
2. Update the `--api-key` value with your new token
3. Add additional parameters like `--project` to specify a default project
4. Save and restart your IDE
5. Verify LaunchDarkly MCP server appears in your IDE's server list

---

### 2. Create Your First AI Config (The Fun Part!)

**2a.** Time to create an AI Config! This is basically a template for your agent that includes which model to use, what temperature, system prompts, etc. You can create multiple "variations" and swap between them instantly.

**The fastest way:** Just ask your IDE to do it for you (if you set up the MCP server).

For a complete walkthrough, see the [AI Configs quickstart guide](https://docs.launchdarkly.com/home/ai-configs/quickstart).

**Using MCP Server (Recommended):**

```
Create an AI Config in project pet-store-agent called "Pet Store Agent" with key pet-store-agent.
Make it agent-based with a variation named base-config.
Select a model provider and model of your choice, set temperature to 0.7, and max tokens to 4096.
Include your agent instructions (execution plan, business rules, response format).
Then enable targeting to serve the base-config variation by default.
```

<details>
<summary><b>Alternative: Using LaunchDarkly UI</b></summary>

See detailed instructions: [Creating AI Configs](https://docs.launchdarkly.com/home/ai-configs/create) and [Agent-based configurations](https://docs.launchdarkly.com/home/ai-configs/agents)

1. Navigate to **AI Configs** → **Create AI Config** → Select `🤖 Agent-based`
2. Configure:
   - **Name**: Pet Store Agent
   - **Key**: `pet-store-agent`
   - **Variation name**: `base-config`
3. Set model configuration:
   - **Model provider**: Select your preferred provider
   - **Model**: Select your preferred model
   - **Parameters**: Add temperature (0.7) and max_tokens (4096)
4. **(Optional) Attach tools** if you created them in step 2b:
   - Click **Attach tools**
   - Select relevant tools (e.g., ✅ search_product_catalog, ✅ getInventory, ✅ getUserById)
   - This makes tools available dynamically based on LaunchDarkly configuration
5. Add your agent instructions in the **Goal or task** field
6. Review and save
7. Go to **Targeting** tab → Edit default rule → Select `base-config` → Save

<figure style="margin: 20px 0;">
  <img src="images/create_agent.png" alt="Create Agent Config" width="600" style="border: 1px solid #ddd; border-radius: 4px; padding: 5px;">
  <figcaption style="margin-top: 8px; font-style: italic; color: #666; text-align: center;">Creating a new agent-based AI Config</figcaption>
</figure>

<figure style="margin: 20px 0;">
  <img src="images/serve_base_config.png" alt="Serve Base Config" width="600" style="border: 1px solid #ddd; border-radius: 4px; padding: 5px;">
  <figcaption style="margin-top: 8px; font-style: italic; color: #666; text-align: center;">Enabling targeting to serve base-config variation</figcaption>
</figure>

</details>

**Tip:** You can quickly create and iterate on AI Configs using LaunchDarkly's MCP server in your IDE.

---

### 2b. (Optional) Define Tools in LaunchDarkly

**Do you need this step?** Only if you're using LangGraph, Strands, or other open-source frameworks and want to dynamically configure which tools your agent can use. If you're using Amazon Bedrock Agents with Knowledge Bases and Action Groups, **skip this section** - Bedrock handles tools differently.

#### What Are LaunchDarkly Tools?

LaunchDarkly tools are **schema definitions** that tell your agent code what tools are available and how to call them. Think of them as API contracts - you define the interface in LaunchDarkly, then implement the actual functionality in your code.

**Key difference from Bedrock:**
- **Bedrock Action Groups**: Live integrations with Lambda functions or AWS services - the tool execution happens on AWS
- **LaunchDarkly Tools**: Configuration schemas only - your agent code implements and executes the tools locally

#### Creating a Tool (UI Method)

1. In the LaunchDarkly sidebar, click **Library** in the AI section
2. Click the **Tools** tab
3. Click **Create tool**

<figure style="margin: 20px 0;">
  <img src="images/library_tools.png" alt="AI Library Tools Section" width="600" style="border: 1px solid #ddd; border-radius: 4px; padding: 5px;">
  <figcaption style="margin-top: 8px; font-style: italic; color: #666; text-align: center;">AI Library section with Tools tab</figcaption>
</figure>

4. Fill in the tool configuration using the examples below based on your framework

<details>
<summary><b>🦙 LlamaIndex RAG Tools</b></summary>

If you're using LlamaIndex to build your own RAG pipeline with vector search, create these tool schemas:

#### Tool 1: Search Product Catalog

> **Key:**
> ```
> search_product_catalog
> ```
>
> **Description:**
> ```
> Semantic search across Pet Store Product Catalog and Product Content PDFs using LlamaIndex vector store
> ```
>
> **Schema:**
> ```json
> {
>   "properties": {
>     "query": {
>       "description": "Search query for product information, pricing, descriptions, or specifications",
>       "type": "string"
>     },
>     "top_k": {
>       "description": "Number of results to return (default: 5)",
>       "type": "number"
>     }
>   },
>   "additionalProperties": false,
>   "required": ["query"]
> }
> ```

#### Tool 2: Search Pet Care Knowledge

> **Key:**
> ```
> search_pet_care
> ```
>
> **Description:**
> ```
> Semantic search across pet care knowledge from Wikipedia articles on cat food, cat toys, dog food, and dog grooming
> ```
>
> **Schema:**
> ```json
> {
>   "properties": {
>     "query": {
>       "description": "Question about cat or dog care, nutrition, grooming, or toys",
>       "type": "string"
>     },
>     "pet_type": {
>       "description": "Filter by pet type: 'cat', 'dog', or 'both'",
>       "type": "string",
>       "enum": ["cat", "dog", "both"]
>     },
>     "top_k": {
>       "description": "Number of results to return (default: 3)",
>       "type": "number"
>     }
>   },
>   "additionalProperties": false,
>   "required": ["query"]
> }
> ```

#### Tool 3: Rerank Search Results

> **Key:**
> ```
> rerank_results
> ```
>
> **Description:**
> ```
> Reorders search results by relevance using LlamaIndex reranking or postprocessing
> ```
>
> **Schema:**
> ```json
> {
>   "properties": {
>     "query": {
>       "description": "Original search query for relevance scoring",
>       "type": "string"
>     },
>     "results": {
>       "description": "Array of search result texts to rerank",
>       "type": "array",
>       "items": {
>         "type": "string"
>       }
>     },
>     "top_n": {
>       "description": "Number of top results to return after reranking (default: 3)",
>       "type": "number"
>     }
>   },
>   "additionalProperties": false,
>   "required": ["query", "results"]
> }
> ```

**Implementation Note:** Your agent code would use LlamaIndex's `VectorStoreIndex` and query engines to implement these tools. You'd create separate indexes for the product PDFs and pet care Wikipedia articles, then query them based on which tool is called.

</details>

<details>
<summary><b>📦 Amazon Bedrock Knowledge Bases Tools</b></summary>

If you're using Bedrock Knowledge Bases with open-source frameworks, create these tool schemas in LaunchDarkly:

#### Tool 1: Query Product Information

> **Key:**
> ```
> ProductInformation
> ```
>
> **Description:**
> ```
> Searches the product catalog containing Pet Store Product Catalog and Product Content from the S3 bucket
> ```
>
> **Schema:**
> ```json
> {
>   "properties": {
>     "query": {
>       "description": "Search query for product descriptions, specifications, prices, or features",
>       "type": "string"
>     }
>   },
>   "additionalProperties": false,
>   "required": ["query"]
> }
> ```

#### Tool 2: Query Pet Care Knowledge

> **Key:**
> ```
> PetCaringKnowledge
> ```
>
> **Description:**
> ```
> Searches pet care advice knowledge base containing cat food, cat toys, dog food, and dog grooming information
> ```
>
> **Schema:**
> ```json
> {
>   "properties": {
>     "query": {
>       "description": "Question or topic about cat or dog care",
>       "type": "string"
>     }
>   },
>   "additionalProperties": false,
>   "required": ["query"]
> }
> ```

**Implementation Note:** Your agent code would call Bedrock Knowledge Base APIs using the knowledge base IDs from your CloudFormation stack outputs.

</details>

<details>
<summary><b>⚡ Lambda Function Tools</b></summary>

These tools integrate with the pre-configured Lambda functions in your AWS account:

#### Tool 1: Get Inventory

> **Key:**
> ```
> getInventory
> ```
>
> **Description:**
> ```
> Retrieves product inventory levels and availability status from the inventory management system
> ```
>
> **Schema:**
> ```json
> {
>   "properties": {
>     "product_code": {
>       "description": "Product code to check inventory (e.g., 'CM001', 'DD006'). Leave empty to get all products.",
>       "type": "string"
>     }
>   },
>   "additionalProperties": false,
>   "required": []
> }
> ```

#### Tool 2: Get User by ID

> **Key:**
> ```
> getUserById
> ```
>
> **Description:**
> ```
> Retrieves customer profile, subscription status, and transaction history by user ID
> ```
>
> **Schema:**
> ```json
> {
>   "properties": {
>     "user_id": {
>       "description": "User ID to retrieve (e.g., 'usr_001', 'usr_002')",
>       "type": "string"
>     }
>   },
>   "additionalProperties": false,
>   "required": ["user_id"]
> }
> ```

#### Tool 3: Get User by Email

> **Key:**
> ```
> getUserByEmail
> ```
>
> **Description:**
> ```
> Retrieves customer profile, subscription status, and transaction history by email address
> ```
>
> **Schema:**
> ```json
> {
>   "properties": {
>     "user_email": {
>       "description": "Customer email address to lookup",
>       "type": "string"
>     }
>   },
>   "additionalProperties": false,
>   "required": ["user_email"]
> }
> ```

**Implementation Note:** Your agent code would invoke the Lambda functions:
- `team-PetStoreInventoryManagementFunction-...` for inventory
- `team-PetStoreUserManagementFunction-...` for user lookups

Using boto3's Lambda client with the `team-SolutionAccessRole-...` IAM role.

</details>

5. Click **Save** after entering each tool configuration

#### Attaching Tools to Your AI Config

Once you've created tools, you can attach them to your AI Config:

1. Navigate to your AI Config (e.g., `pet-store-agent`)
2. In the model configuration section, click **Attach tools**
3. Select the tools you want this agent to have access to (e.g., ✅ search_v2, ✅ reranking, ✅ get_inventory)
4. Save your changes

Now your agent code can fetch `agent_config.model.parameters.get("tools", [])` to see which tools are available and dynamically build the tool list based on LaunchDarkly configuration.

**For the hackathon:** If you're using Bedrock Agents, you'll configure Knowledge Bases and Action Groups directly in the Bedrock console instead. LaunchDarkly tools are optional and mainly useful if you want to dynamically enable/disable tools without redeploying code.

---

### 3. Hook Up Your Agent Code

**3a.** Now we connect your agent to LaunchDarkly so it can grab configs at runtime. Sounds scary but it's actually a pretty simple pattern - you'll basically add ~20 lines of code.

**The pattern is the same for every framework:** Initialize LaunchDarkly → Build a user context → Fetch the config → Use it to set up your model → Track some metrics.

For comprehensive SDK documentation, see:
- [Python AI SDK](https://docs.launchdarkly.com/sdk/ai/python)
- [AI Config SDK feature guide](https://docs.launchdarkly.com/sdk/features/ai-config)
- [Tracking AI metrics](https://docs.launchdarkly.com/sdk/features/ai-metrics)

#### Install Dependencies

```bash
pip install launchdarkly-server-sdk launchdarkly-server-sdk-ai
```

#### Universal Instrumentation Pattern

Every agent follows these 5 steps, regardless of framework:

**Step 1: Initialize SDK (once at startup)**

```python
import ldclient
from ldclient import Context
from ldai.client import LDAIClient

ldclient.set_config(ldclient.Config(os.environ.get('LAUNCHDARKLY_SDK_KEY')))
ld_client = ldclient.get()
ai_client = LDAIClient(ld_client)
```

**Step 2: Build Context (per request)**

```python
context = Context.builder("user-123") \
    .set("subscription_status", "premium") \
    .set("query_complexity", "high") \
    .build()
```

**Step 3: Retrieve Configuration**

Use `agent_config()` for full agent configuration:

```python
from ldai.client import AIAgentConfigDefault, ModelConfig, ProviderConfig

agent_config = ai_client.agent_config(
    "pet-store-agent",
    context,
    default_value=AIAgentConfigDefault(
        enabled=False,
        model=ModelConfig("fallback-model"),
        provider=ProviderConfig("bedrock"),
        instructions="Fallback instructions"
    )
)

# Extract configuration
model_name = agent_config.model.name
instructions = agent_config.instructions
parameters = agent_config.model.parameters
tools_config = parameters.get("tools", [])
tracker = agent_config.tracker
```

**Step 4: Build Tools Dynamically**

```python
def build_tools_from_config(tools_config, global_config, aws_region):
    tools = []
    for tool_config in tools_config:
        tool_name = tool_config.get("name")
        tool_custom = tool_config.get("custom", {})
        tool_params = tool_config.get("parameters", {})
        merged_config = {**global_config, **tool_params, **tool_custom}

        if tool_name in TOOL_BUILDERS:
            tool = TOOL_BUILDERS[tool_name](merged_config, aws_region)
            tools.append(tool)
    return tools
```

**Step 5: Track Metrics**

```python
tracker = agent_config.tracker

try:
    import time
    start_time = time.time()
    result = agent.invoke(input_)
    duration_ms = int((time.time() - start_time) * 1000)

    tracker.track_duration(duration_ms)
    tracker.track_success()

    from ldai.tracker import TokenUsage
    usage = TokenUsage(input=100, output=200, total=300)
    tracker.track_tokens(usage)

except Exception as e:
    tracker.track_error()
    raise
```

**Available tracking methods:**
- `tracker.track_duration(ms)` - Execution duration
- `tracker.track_success()` - Successful completions
- `tracker.track_error()` - Errors
- `tracker.track_tokens(TokenUsage(...))` - Token usage
- `tracker.track_time_to_first_token(ms)` - Latency

#### Framework-Specific Instrumentation

<details>
<summary><b>LangGraph Integration Example</b></summary>

```python
from langgraph.prebuilt import create_react_agent
from langgraph.checkpoint.memory import MemorySaver

class PetStoreAgent:
    def __init__(self):
        # Step 1: Initialize LaunchDarkly
        sdk_key = os.environ.get("LAUNCHDARKLY_SDK_KEY")
        ldclient.set_config(LDConfig(sdk_key))
        self.ld = ldclient.get()
        self.ai = LDAIClient(self.ld)
        self.checkpointer = MemorySaver()

    def invoke(self, prompt: str, user_ctx: Optional[Dict[str, Any]] = None):
        # Step 2: Build context
        ctx = Context.builder(user_ctx.get("user_id", "anonymous")) \
            .set("subscription_status", user_ctx.get("subscription_status", "guest")) \
            .build()

        # Step 3: Retrieve configuration
        agent_config = self.ai.agent_config(
            "pet-store-agent",
            ctx,
            default_value=AIAgentConfigDefault(
                enabled=False,
                model=ModelConfig("fallback-model"),
                provider=ProviderConfig("bedrock"),
                instructions="Fallback instructions"
            )
        )

        # Extract configuration
        model_name = agent_config.model.name
        provider = agent_config.provider.name
        instructions = agent_config.instructions
        parameters = agent_config.model.parameters
        tracker = agent_config.tracker

        # Step 4: Build tools dynamically
        tools = self.build_tools(parameters.get("tools", []))

        # Initialize LLM
        llm = init_chat_model(
            model_name,
            model_provider=provider,
            temperature=parameters.get("temperature", 0.7),
            max_tokens=parameters.get("max_tokens", 4096)
        )

        # Create LangGraph agent
        graph = create_react_agent(
            llm,
            tools,
            prompt=instructions,
            checkpointer=self.checkpointer
        )

        # Step 5: Track metrics
        try:
            import time
            start_time = time.time()

            result = graph.invoke(
                {"messages": [HumanMessage(content=prompt)]},
                config={"configurable": {"thread_id": user_ctx.get("thread_id", "default")}}
            )

            duration_ms = int((time.time() - start_time) * 1000)
            tracker.track_duration(duration_ms)
            tracker.track_success()

            # Extract token usage from messages
            usage = self._collect_token_usage(result.get("messages", []))
            if usage:
                tracker.track_tokens(usage)

            return result
        except Exception as e:
            tracker.track_error()
            raise

    def _collect_token_usage(self, messages):
        inp = out = total = 0
        for m in messages:
            usage = getattr(m, "usage_metadata", None) or {}
            inp += int(usage.get("input_tokens", 0) or 0)
            out += int(usage.get("output_tokens", 0) or 0)
            total += int(usage.get("total_tokens", 0) or 0)
        return TokenUsage(input=inp, output=out, total=total) if total else None
```

</details>

<details>
<summary><b>Strands Integration Example</b></summary>

```python
from strands import Agent, Orchestrator

class PetStoreAgent:
    def __init__(self):
        # Step 1: Initialize LaunchDarkly
        sdk_key = os.environ.get("LAUNCHDARKLY_SDK_KEY")
        ldclient.set_config(LDConfig(sdk_key))
        self.ld = ldclient.get()
        self.ai = LDAIClient(self.ld)

    async def invoke(self, prompt: str, user_ctx: Optional[Dict[str, Any]] = None):
        # Step 2: Build context
        ctx = Context.builder(user_ctx.get("user_id", "anonymous")) \
            .set("subscription_status", user_ctx.get("subscription_status", "guest")) \
            .build()

        # Step 3: Retrieve configuration
        config = self.ai.agent_config(
            "pet-store-agent",
            ctx,
            default_value=AIAgentConfigDefault(
                enabled=False,
                model=ModelConfig("fallback-model"),
                provider=ProviderConfig("bedrock"),
                instructions="Fallback instructions"
            )
        )

        model_name = config.model.name
        instructions = config.instructions
        tracker = config.tracker

        # Step 4: Build Strands agent
        agent = Agent(
            model=model_name,
            system_prompt=instructions,
            tools=self.build_tools(config.model.parameters.get("tools", []))
        )

        # Step 5: Track metrics
        start_time = time.time()

        try:
            result = await agent.run(
                prompt,
                callbacks=[self._create_tracking_callback(tracker, start_time)]
            )

            duration_ms = int((time.time() - start_time) * 1000)
            tracker.track_duration(duration_ms)
            tracker.track_success()

            return result
        except Exception as e:
            tracker.track_error()
            raise

    def _create_tracking_callback(self, tracker, start_time):
        """Create callback for token tracking"""
        def on_token_usage(usage_data):
            if usage_data:
                tracker.track_tokens(TokenUsage(
                    input=usage_data.get("input_tokens", 0),
                    output=usage_data.get("output_tokens", 0),
                    total=usage_data.get("total_tokens", 0)
                ))
        return on_token_usage
```

</details>

---

### 4. Update Target Configuration

**4a.** Modify your LaunchDarkly AI Config targeting to dynamically control which users receive configurations

Learn more about [targeting AI Configs](https://docs.launchdarkly.com/home/ai-configs/target)

**Using MCP Server:**

```
Update the pet-store-agent config targeting. Add a rule that serves base-config to users
where subscription_status is "premium". Set the default rule to also serve base-config.
```

<details>
<summary><b>Alternative: Using LaunchDarkly UI</b></summary>

1. Navigate to AI Config → **Targeting** tab
2. Click **+ Add rule**
3. Configure:
   - **Name**: "Premium Users"
   - **Condition**: `subscription_status` is one of `premium`
   - **Serve**: `base-config` variation
4. Ensure Default rule serves `base-config`
5. Save changes

<figure style="margin: 20px 0;">
  <img src="images/save_changes_to_targeting.png" alt="Save Targeting Changes" width="600" style="border: 1px solid #ddd; border-radius: 4px; padding: 5px;">
  <figcaption style="margin-top: 8px; font-style: italic; color: #666; text-align: center;">Saving targeting rule changes</figcaption>
</figure>

</details>

**4b.** Practice dynamic updates using your IDE's MCP server to quickly iterate on targeting rules

---

### 5. Test AI Config and Monitor Performance (Optional)

**5a.** Send prompt messages using different user contexts

```python
test_cases = [
    {"prompt": "What's the price of Doggy Delights?",
     "context": {"user_id": "guest-001", "subscription_status": "guest"}},
    {"prompt": "I need detailed care instructions for a puppy",
     "context": {"user_id": "premium-001", "subscription_status": "premium"}}
]

for test in test_cases:
    response = agent.invoke(test["prompt"], test["context"])
```

**5b.** Monitor AI Config behavior in the LaunchDarkly console
- Navigate to AI Configs → `pet-store-agent` → **Monitoring** tab
- Observe: Request volume, token usage, response times, error rates, cost per variation

For more details, see [Monitoring AI Configs](https://docs.launchdarkly.com/home/ai-configs/monitor)

**5c.** Validate configuration changes in real-time to ensure targeting rules work as expected

---

### 6. Run Your First AI Experiment (This Is Where It Gets Cool!)

**6a.** Here's where the magic happens. You're going to run a proper A/B test between two models and see which one is more token-efficient. It's like science, but for AI. 🧪

**What you'll do:** Create variations with different models, split traffic 50/50, and LaunchDarkly will track token usage automatically.

For detailed guidance, see [Experimenting with AI Configs](https://docs.launchdarkly.com/home/ai-configs/experimentation)

#### Add Model Variations

Before creating your experiment, add a second variation to compare (same process as step 2 - just pick a different model while keeping tools and parameters the same).

#### Configure Experiment

Navigate to **AI Configs → pet-store-agent**. In the right navigation menu, click the **+** (plus) sign next to **Experiments** to create a new experiment.

**Experiment Design:**

**Experiment type:**
- Keep `Feature change` selected (default)

**Name:** `Pet Store Agent Model Performance`

**Hypothesis and Metrics:**

**Hypothesis:** `The alternative model will provide better token efficiency for our pet store queries.`

**Randomize by:** `user`

**Metrics:** Click "Select metrics or metric groups" and add `average_total_user_tokens` (this is automatically tracked when you use `tracker.track_tokens()` in your code)

**Audience Targeting:**

**Flag or AI Config:**
- Click the dropdown and select **pet-store-agent**

**Targeting rule:**
- Click the dropdown and select **Default rule**

**Audience Allocation:**

**Variations served outside of this experiment:**
- `base-config`

**Sample size:** Set to `100%` of users in this experiment

**Variations split:** Click "Edit" and configure:
- `base-config`: `50%` (control)
- `model-variant-2`: `50%` (treatment)
- All other variations: `0%`

**Control:**
- Select `base-config`

**Statistical Approach and Success Criteria:**

**Statistical approach:** `Bayesian`

**Threshold:** `90%` (or 95% for mission-critical features)

Click **"Save"** then **"Start experiment"** to launch.

<figure style="margin: 20px 0;">
  <img src="images/premium_model.png" alt="Experiment Configuration Example" width="600" style="border: 1px solid #ddd; border-radius: 4px; padding: 5px;">
  <figcaption style="margin-top: 8px; font-style: italic; color: #666; text-align: center;">Example experiment configuration in LaunchDarkly</figcaption>
</figure>

**Note:** You may see a "Health warning" indicator after starting the experiment. This is normal when no variations have been exposed yet. The warning will clear once traffic starts flowing.

**6b.** Generate experiment data by sending varied queries through your agent with different user contexts. Monitor the **Results** tab in your experiment to see metrics populate in real-time.

---

### 7. Run End-to-End Testing and Analyze Results (Optional)

**7a.** Send prompt messages through your instrumented agent

Generate varied traffic for your experiment to collect statistically significant data:

```python
import random

for i in range(50):
    user_id = f"experiment-user-{i:03d}"
    context = {
        "user_id": user_id,
        "subscription_status": random.choice(["guest", "active", "premium"])
    }
    prompts = [
        "What's the price of Doggy Delights?",
        "How should I care for a new kitten?",
        "Tell me about your cat products",
        "I need food for my dog"
    ]
    response = agent.invoke(random.choice(prompts), context)
```

**7b.** Check your results in the LaunchDarkly console

Navigate to your experiment and click the **Results** tab to see which model is more token-efficient.

<figure style="margin: 20px 0;">
  <img src="images/premium_results.png" alt="Experiment Results Analysis" width="600" style="border: 1px solid #ddd; border-radius: 4px; padding: 5px;">
  <figcaption style="margin-top: 8px; font-style: italic; color: #666; text-align: center;">Example experiment results showing metrics and statistical analysis</figcaption>
</figure>

---

## You're Done! 🎉

Congrats - you just ran a professional-grade AI experiment! You can now swap models, run tests, and optimize your agent based on real data. Pretty powerful stuff.

**Want to go deeper?** Check out these resources:
- [LaunchDarkly AI Configs docs](https://docs.launchdarkly.com/ai)
- [LaunchDarkly AI Config with Amazon Bedrock Workshop](https://catalog.workshops.aws/launchdarkly-ai-config-bedrock/en-US)
- [Multi-Agent Tutorial](https://github.com/launchdarkly-labs/devrel-agents-tutorial)
