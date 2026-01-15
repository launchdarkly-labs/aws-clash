# AI Experimentation with LaunchDarkly

![LaunchDarkly Logo](images/launchdarkly.png)

LaunchDarkly revolutionizes how builders and engineers approach AI development by bringing sophisticated experimentation capabilities directly into production environments. With LaunchDarkly's AI Configs, you gain unprecedented control over your AI systems through a specialized runtime management system that lets you dynamically control model selection and parameters from a central hub, target specific user segments with tailored AI configurations, run live experiments comparing different AI setups, and collect real-time feedback and metrics to continuously optimize performance. This isn't just feature flagging — it's a complete AI experimentation platform that empowers you to iterate fearlessly in production, test hypotheses with real users, and make data-driven decisions about which models and parameters deliver the best results. Whether you're fine-tuning prompt strategies, comparing models, or optimizing temperature settings for different user personas, LaunchDarkly gives you the confidence to experiment boldly while maintaining full control over your AI's behavior in production.

## Scenario

You are tasked to experiment between different AI models to determine which works best for Pet Store agents based on performance, cost, and user experience metrics.

## Success Criteria and Score Validation

- LaunchDarkly account configured with proper tokens
- AI Config created with multiple model variations
- MCP server integrated with your IDE for configuration management
- Agent successfully instrumented to use LaunchDarkly AI Configs
- Experiment running with measurable metrics
- Data-driven decision on optimal model configuration

## Build Your First AI Experiment: LaunchDarkly Demo

**PLACEHOLDER FOR SCARLETT'S VIDEO**

---

## Steps

### 1. Sign Up to LaunchDarkly and Configure Access

**Estimated Time: 15 minutes**

#### Understanding Token Types

LaunchDarkly uses two types of keys that serve different purposes:

- **API Access Token** (starts with `api-`): Used by the MCP server in your IDE to create and manage AI Configs programmatically
- **SDK Key** (starts with `sdk-`): Used in your agent code to retrieve AI configurations at runtime

Both are needed for the complete workflow.

#### Create Your LaunchDarkly Account

1. Navigate to [LaunchDarkly signup](https://launchdarkly.com)
2. Complete registration and verify your email
3. Log in to your new account

#### Generate API Access Token (for MCP Server)

The API access token allows your IDE to communicate with LaunchDarkly to create and manage AI Configs.

1. Navigate to **Organization Settings** (gear icon) → **Authorization**
2. In the "Access tokens" section, click **Create token**

![Create API Token](images/api-token-create.png)

3. Configure the token:
   - **Name**: `workshop-mcp-token` (or any descriptive name)
   - **Role**: Select **Writer** or **LaunchDarkly Developer**
   - **API version**: Use default (latest)
   - Leave "This is a service token" unchecked

![Name API Token](images/api-token-name.png)

4. Click **Save token**
5. **IMPORTANT**: Copy the token immediately - it's only shown once!

![Copy API Token](images/api-token-copy.png)

6. Save this token securely - you'll use it in your MCP configuration

#### Retrieve SDK Key (for Agent Code)

The SDK key allows your agent code to retrieve AI configurations at runtime.

1. Navigate to **Project settings** (gear icon in sidebar)

![Access Project Settings](images/project_settings.png)

2. Go to **Environments** → Select your environment (Test or Production)
3. Copy the **SDK key** (starts with `sdk-`)

![SDK Key Location](images/sdk-key.png)

4. Save this key - you'll use it as `LAUNCHDARKLY_SDK_KEY` in your environment variables

#### Configure MCP Server in Your IDE

The Model Context Protocol (MCP) server enables your IDE to interact with LaunchDarkly using natural language.

**Initial Setup:**

Choose your IDE and create/update the appropriate configuration file:

- **For Cursor**: `~/.cursor/mcp.json`
- **For Claude Desktop**: `claude_desktop_config.json`
- **For other IDEs**: Check your IDE's MCP configuration documentation

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

Replace `api-xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx` with your actual API access token.

**To Edit/Update MCP Configuration:**

1. Open your MCP configuration file in your IDE
2. Modify the `--api-key` value to update your token
3. You can also add additional parameters like `--project` to specify a default project
4. Save the file and restart your IDE/AI client
5. Verify the LaunchDarkly MCP server appears in your IDE's MCP server list

#### Store SDK Key Securely

For the agent code, store the SDK key in AWS Secrets Manager:

```bash
aws secretsmanager create-secret \
  --name "launchdarkly-sdk-key" \
  --secret-string "sdk-xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx" \
  --description "LaunchDarkly SDK key for pet store agent"
```

Or set it as an environment variable:

```bash
export LAUNCHDARKLY_SDK_KEY="sdk-xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx"
```

**Validation Checkpoint:**
- ✅ LaunchDarkly account created
- ✅ API access token generated and saved
- ✅ SDK key retrieved and stored
- ✅ MCP server configured in IDE
- ✅ IDE recognizes LaunchDarkly MCP server

---

### 2. Create Your First AI Config

**Estimated Time: 20 minutes**

#### Using MCP Server (Recommended)

With the MCP server configured, you can create AI Configs using natural language directly in your IDE.

**Example Command:**

```
Create an AI Config in project pet-store-agent called "Pet Store Agent" with key pet-store-agent. Make it agent-based with a variation named base-config. Select a model provider and model of your choice, set temperature to 0.7, and max tokens to 4096. Set the instructions to: [Your agent instructions here]. Then enable targeting in the production environment to serve the base-config variation by default.
```

The MCP server will:
- Create the AI Config
- Configure the variation
- Enable targeting
- Confirm completion

**Verify Creation:**
- Check your IDE for MCP server confirmation
- Visit LaunchDarkly dashboard to see the new AI Config

<details>
<summary><b>Alternative: Using LaunchDarkly UI</b></summary>

1. **Access AI Configs**
   - In LaunchDarkly dashboard sidebar, navigate to **AI Configs**
   - Click **Create AI Config**
   - Select `🤖 Agent-based` configuration type

![Create Agent Config](images/create_agent.png)

2. **Configure Basic Settings**
   - **Name**: Pet Store Agent
   - **Key**: `pet-store-agent` (this is what you'll reference in code)
   - **Variation name**: `base-config`

3. **Set Model Configuration**
   - **Model provider**: Select your preferred provider (e.g., AWS Bedrock, Anthropic, OpenAI)
   - **Model**: Select your preferred model
   - **Parameters**:
     - Click **Add parameters**
     - Temperature: `0.7`
     - Max tokens: `4096`

4. **Configure Agent Instructions**
   - In the **Goal or task** field, enter your agent's system prompt
   - This defines how your agent behaves and responds
   - You can include business rules, execution plans, and response schemas

5. **Review and Save**
   - Click **Review and save**
   - Verify all settings
   - Click **Save**

6. **Enable the AI Config**
   - Switch to the **Targeting** tab
   - Click **Edit** on the Default rule
   - Select your `base-config` variation
   - Add a note: "Initial pet store agent config"
   - Type your environment name to confirm
   - Click **Save**

![Serve Base Config](images/serve_base_config.png)

</details>

**Validation Checkpoint:**
- ✅ AI Config created successfully
- ✅ Base variation configured with model and parameters
- ✅ Targeting enabled in your environment
- ✅ Default rule serving your variation

---

### 3. Instrument Your Agent with LaunchDarkly SDK

**Estimated Time: 30 minutes**

Now integrate LaunchDarkly into your agent code to dynamically retrieve AI configurations at runtime.

#### Install Dependencies

```bash
pip install launchdarkly-server-sdk launchdarkly-server-sdk-ai
```

#### Core Instrumentation Pattern

Every agent follows these 5 steps, regardless of framework or tools:

**1. Initialize LaunchDarkly SDK (once at startup)**

```python
import ldclient
from ldclient import Context
from ldai.client import LDAIClient

# Initialize SDK
ldclient.set_config(ldclient.Config(os.environ.get('LAUNCHDARKLY_SDK_KEY')))
ld_client = ldclient.get()
ai_client = LDAIClient(ld_client)
```

**2. Build Context (per request)**

```python
# Build context with user attributes for targeting
context = Context.builder("user-123") \
    .set("subscription_status", "premium") \
    .set("query_complexity", "high") \
    .build()
```

**3. Retrieve AI Configuration from LaunchDarkly**

Use the **Agent-based API** (`agent_config()`) for full agent configuration:

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

# Extract everything you need
model_name = agent_config.model.name
instructions = agent_config.instructions
parameters = agent_config.model.parameters  # temperature, max_tokens, etc.
tools_config = parameters.get("tools", [])  # Tool definitions from LaunchDarkly
tracker = agent_config.tracker
```

**4. Build Tools Dynamically from Configuration**

Tools are defined in LaunchDarkly AI Config and built dynamically in your code:

```python
def build_tools_from_config(tools_config, global_config, aws_region):
    """Build tools dynamically from LaunchDarkly configuration"""
    tools = []

    for tool_config in tools_config:
        tool_name = tool_config.get("name")

        # Merge global config with tool-specific config
        tool_custom = tool_config.get("custom", {})
        tool_params = tool_config.get("parameters", {})
        merged_config = {**global_config, **tool_params, **tool_custom}

        # Get tool builder and create tool
        if tool_name in TOOL_BUILDERS:
            tool = TOOL_BUILDERS[tool_name](merged_config, aws_region)
            tools.append(tool)

    return tools

# Example: Tool builders handle different implementations
TOOL_BUILDERS = {
    "retrieve_product_info": build_rag_tool,  # Works with Bedrock KB or LlamaIndex
    "get_inventory": build_inventory_tool,     # Works with Lambda or mock data
    "get_user_by_id": build_user_tool,         # Adapts based on config
}
```

**Key insight:** LaunchDarkly stores tool configurations, your code builds actual tool objects based on those configs.

**5. Track Metrics Manually**

Always use manual tracking methods (not provider-specific):

```python
tracker = agent_config.tracker

try:
    # Track execution time
    import time
    start_time = time.time()
    result = agent.invoke(input_)
    duration_ms = int((time.time() - start_time) * 1000)

    tracker.track_duration(duration_ms)
    tracker.track_success()

    # Track token usage (extract from your model's response)
    from ldai.tracker import TokenUsage
    usage = TokenUsage(input=100, output=200, total=300)
    tracker.track_tokens(usage)

except Exception as e:
    tracker.track_error()
    raise
```

**Available tracking methods:**
- `tracker.track_duration(ms)` - Track execution duration
- `tracker.track_success()` - Track successful completions
- `tracker.track_error()` - Track errors
- `tracker.track_tokens(TokenUsage(...))` - Track token usage
- `tracker.track_time_to_first_token(ms)` - Track latency

#### Reference Implementations

Complete working examples for different frameworks:

- **LangGraph + Agent-based API:** [aws_clash/agent/pet_store_agent/pet_store_agent_full_ld.py](https://github.com/launchdarkly-labs/aws-clash)
- **Strands + Config API:** [ai_config_strands/teacher_orchestrator.py](https://github.com/launchdarkly-labs/ai_config_strands)

These examples demonstrate the 5-step pattern applied to production agents with full tool configuration and tracking.

**Validation Checkpoint:**
- ✅ LaunchDarkly SDK integrated
- ✅ Configuration retrieval working (`agent_config` API)
- ✅ Tools built dynamically from LaunchDarkly configuration
- ✅ Manual metrics tracking implemented
- ✅ Agent successfully uses dynamic configuration

---

### 4. Update Targeting Configuration

**Estimated Time: 10 minutes**

Practice updating your AI Config's targeting to dynamically control which users receive your AI configuration.

#### Understanding Targeting

Targeting rules let you:
- Serve configurations to specific user segments
- Create custom rules based on user attributes
- Enable/disable configs for testing
- Control rollout percentages

#### Using MCP Server

```
Update the pet-store-agent config targeting. Add a rule that serves base-config to users where subscription_status is "premium". Set the default rule to also serve base-config.
```

<details>
<summary><b>Alternative: Using LaunchDarkly UI</b></summary>

1. Navigate to your AI Config → **Targeting** tab
2. Click **+ Add rule**
3. Configure a test rule:
   - **Name**: "Premium Users"
   - **Condition**: `subscription_status` is one of `premium`
   - **Serve**: `base-config` variation
4. Ensure Default rule serves `base-config`
5. **Save changes**

![Save Targeting Changes](images/save_changes_to_targeting.png)

</details>

**Note:** You'll add more variations and advanced targeting rules when you create your experiment in Step 6.

**Validation Checkpoint:**
- ✅ Targeting rules created and modified
- ✅ Understand how to use both MCP and UI for updates
- ✅ Configuration actively serving to users
- ✅ Ready to add tracking and monitoring

---

### 5. Test AI Config and Monitor Performance (Optional)

**Estimated Time: 10 minutes**

Send test prompts and observe real-time behavior in the LaunchDarkly console.

#### Test Different User Contexts

```python
test_cases = [
    {
        "prompt": "What's the price of Doggy Delights?",
        "context": {"user_id": "guest-001", "subscription_status": "guest"}
    },
    {
        "prompt": "I need detailed care instructions for a puppy",
        "context": {"user_id": "premium-001", "subscription_status": "premium"}
    },
    {
        "prompt": "Do you have cat toys?",
        "context": {"user_id": "user-001", "query_complexity": "simple"}
    }
]

for test in test_cases:
    response = agent.invoke(test["prompt"], test["context"])
    print(f"Context: {test['context']}")
    print(f"Response: {response}\n")
```

#### Check Monitoring Dashboard

1. Navigate to LaunchDarkly → AI Configs → `pet-store-agent`
2. Click **Monitoring** tab
3. Observe:
   - Request volume by variation
   - Token usage per model
   - Response times
   - Error rates
   - Cost per variation

**Validation Checkpoint:**
- ✅ Test prompts executed successfully
- ✅ Metrics visible in dashboard
- ✅ Targeting rules working as expected
- ✅ Real-time monitoring active

---

### 6. Create an AI Experiment

**Estimated Time: 25 minutes**

Now compare model performance scientifically using LaunchDarkly's experimentation platform. First, add additional model variations, then set up the experiment.

#### Add Model Variations

Before experimenting, add alternative models to compare:

**Using MCP Server:**
```
Add a variation to the pet-store-agent config called model-variant-2. Select a different model provider and model than your base-config. Adjust temperature and max tokens as needed. Keep the same instructions.
```

<details>
<summary><b>Alternative: Using LaunchDarkly UI</b></summary>

- Go to **Variations** tab → **+ Add variation**
- Create a new variation with a different model (different provider or model)
- Adjust parameters (temperature, max tokens) for comparison
- Optionally add additional variations to test

</details>

#### Set Up the Experiment

1. **Navigate to Your AI Config**
   - Open `pet-store-agent`
   - In right navigation, click **+** next to **Experiments**
   - Select **Create new experiment**

2. **Configure Experiment Design**
   - **Type**: `Feature change`
   - **Name**: `Pet Store Agent Model Performance`
   - **Hypothesis**:
     ```
     The alternative model will provide higher quality responses
     for complex queries, justifying potential cost differences with
     improved user satisfaction and fewer errors.
     ```

3. **Set Up Metrics**
   - **Randomize by**: `user`
   - **Select metrics**:
     1. `Positive feedback rate` (Primary - add first)
     2. `Negative feedback rate`
     3. `Response latency` (p95)
     4. `Cost per request`

4. **Configure Audience**
   - **AI Config**: `pet-store-agent`
   - **Targeting rule**: **Default rule**
   - This ensures all users can participate

5. **Set Audience Allocation**
   - **Control variation**: `base-config` (your original model)
   - **Sample size**: `100%` of users
   - **Variation split**:
     - `base-config`: 50% (control)
     - `model-variant-2`: 50% (treatment)
     - Exclude other variations: 0%

6. **Configure Success Criteria**
   - **Statistical approach**: `Bayesian`
   - **Confidence threshold**: `90%` (or `95%`)
   - This determines when you have a winner

7. **Launch**
   - Click **Save**
   - Review all settings
   - Click **Start experiment**
   - Confirm by typing environment name

**Validation Checkpoint:**
- ✅ Experiment created and running
- ✅ Primary metric configured
- ✅ 50/50 control vs treatment split
- ✅ Bayesian analysis enabled

---

### 7. Run End-to-End Testing and Analyze Results (Optional)

**Estimated Time: 20 minutes**

Generate traffic and analyze experiment results.

#### Generate Experiment Traffic

Run your agent with varied prompts and user contexts:

```python
import random

for i in range(50):
    user_id = f"experiment-user-{i:03d}"

    # Vary user attributes
    context = {
        "user_id": user_id,
        "subscription_status": random.choice(["guest", "active", "premium"]),
        "query_complexity": random.choice(["simple", "medium", "high"])
    }

    # Test with competition-relevant prompts
    prompts = [
        "What's the price of Doggy Delights?",
        "How should I care for a new kitten?",
        "Tell me about your cat products",
        "I need food for my dog"
    ]

    response = agent.invoke(random.choice(prompts), context)
```

#### Monitor Experiment Progress

1. Navigate to your experiment in LaunchDarkly
2. Check **Results** tab
3. Monitor:
   - Sample size accumulation
   - Primary metric trends
   - Statistical significance
   - Confidence intervals
   - Winning variation probability

#### Analyze and Make Decisions

**Performance Comparison:**
- Which variation has higher positive feedback?
- What's the cost difference between variations?
- Are response times acceptable?
- Is there a clear winner?

**Statistical Analysis:**
- Has statistical significance been reached?
- What's the confidence level?
- What's the effect size?

**Business Decision:**
- **Roll out winner**: If one variation clearly wins with acceptable cost
- **Iterate**: If results are inconclusive, adjust parameters and retest
- **Test new models**: If no clear winner, try different model combinations

**Validation Checkpoint:**
- ✅ Sufficient traffic generated (50+ samples)
- ✅ Experiment metrics populated
- ✅ Statistical analysis available
- ✅ Clear decision or learning identified

---

## Troubleshooting

### MCP Server Not Connecting
- Verify API token has correct permissions (Writer or Developer role)
- Check that MCP configuration file has correct syntax
- Restart your IDE after configuration changes
- Verify LaunchDarkly MCP server appears in IDE's server list

### SDK Key Not Working
- Confirm you're using SDK key (starts with `sdk-`), not API token
- Verify key is from correct environment (Test/Production)
- Check environment variable is set correctly
- Ensure SDK has time to initialize before first request

### AI Config Not Returning Expected Variation
- Check targeting rules order (rules evaluate top to bottom)
- Verify context attributes match rule conditions exactly
- Confirm variation is enabled in the environment
- Use LaunchDarkly debugger to trace evaluation

### Experiment Not Collecting Data
- Verify experiment is in "Running" status
- Ensure metrics are being tracked in agent code
- Check that user contexts are being created correctly
- Confirm traffic is reaching the default rule being experimented on

---

## Additional Resources

### Documentation
- [LaunchDarkly AI Configs](https://docs.launchdarkly.com/ai)
- [LaunchDarkly MCP Server](https://launchdarkly.com/docs/home/getting-started/mcp)
- [LaunchDarkly Experimentation](https://docs.launchdarkly.com/home/experimentation)
- [Tracking AI Metrics](https://docs.launchdarkly.com/sdk/features/tracking-ai-metrics)

### Workshops & Tutorials
- [LaunchDarkly AI Config with Amazon Bedrock Workshop](https://catalog.workshops.aws/launchdarkly-ai-config-bedrock/en-US)
- [LaunchDarkly Multi-Agent Tutorial](https://github.com/launchdarkly-labs/devrel-agents-tutorial)

### Blog Posts
- [Creating Better Runtime Control with LaunchDarkly and AWS](https://launchdarkly.com/blog/runtime-control-launchdarkly-aws/)
