# AI Experimentation with LaunchDarkly

<figure style="margin: 20px 0;">
  <img src="images/launchdarkly.png" alt="LaunchDarkly Logo" width="600" style="border: 1px solid #ddd; border-radius: 4px; padding: 5px;">
  <figcaption style="margin-top: 8px; font-style: italic; color: #666; text-align: center;">LaunchDarkly Logo</figcaption>
</figure>

LaunchDarkly's AI Configs let you swap models, tweak prompts, and test different configurations **without redeploying code**. Think of it as A/B testing for AI - change your model from Claude to GPT to Llama, adjust parameters on the fly, and see which setup actually performs best with real data. You can target specific users ("premium customers get the fancy model"), run controlled experiments, and track token efficiency. Make changes in a web UI and your agent instantly picks them up. No more guessing which model is best or hardcoding configurations. Just experiment, measure, and ship the winner.

> **Agent Skills Available:** This workshop supports **Agent Skills** - interactive slash commands that guide you through each step. Agent Skills follow an open standard and work with any compatible editor (Claude Code, Cursor, Windsurf, VS Code with extensions, and more). Look for the `/aiconfig-*` skills throughout this guide. You can also use the MCP server as an alternative.

### Quick Reference: Agent Skills for AI Configs

| Skill | Description |
|-------|-------------|
| `/aiconfig-projects` | Create a new LaunchDarkly project |
| `/aiconfig-create` | Create an AI Config with variations |
| `/aiconfig-sdk` | Instrument your Python app with the AI SDK |
| `/aiconfig-ai-metrics` | Add AI metrics tracking |
| `/aiconfig-targeting` | Configure targeting rules |
| `/aiconfig-segments` | Create user segments for targeting |
| `/aiconfig-tools` | Create and attach tools to configs |
| `/aiconfig-variations` | Add/update variations in a config |
| `/aiconfig-context-basic` | Build user contexts |
| `/aiconfig-custom-metrics` | Track custom business metrics |
| `/aiconfig-online-evals` | Set up LLM-as-a-judge evaluations |

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

**1e.** Configure LaunchDarkly integration for your IDE

You have two options for AI-powered interaction with LaunchDarkly:

#### Option A: Agent Skills (Recommended for any compatible editor)

Agent Skills are interactive slash commands that guide you through creating and managing AI Configs. They follow an **open standard** and work with any editor that supports agent skills, including:
- **Claude Code** (Anthropic's CLI)
- **Cursor** (with agent skills support)
- **Windsurf**
- **VS Code** (with compatible extensions)
- Other editors supporting the agent skills standard

**Available Skills:**
- `/aiconfig-projects` - Create LaunchDarkly projects to organize your AI Configs
- `/aiconfig-create` - Create a new AI Config with variations and model configurations
- `/aiconfig-sdk` - Instrument your Python application with the LaunchDarkly AI SDK
- `/aiconfig-ai-metrics` - Add AI metrics tracking to your codebase
- `/aiconfig-targeting` - Configure targeting rules for A/B tests and rollouts
- `/aiconfig-segments` - Create segments for targeting groups of users
- `/aiconfig-tools` - Create and attach tools to your AI Configs
- `/aiconfig-variations` - Manage variations within an AI Config
- `/aiconfig-context-basic` - Build user contexts for targeting
- `/aiconfig-context-advanced` - Advanced context patterns with cardinality controls
- `/aiconfig-custom-metrics` - Create and track custom business metrics
- `/aiconfig-online-evals` - Set up LLM-as-a-judge evaluations

**To use a skill**, simply type the slash command in your editor:
```
/aiconfig-create
```

Your AI assistant will guide you through the process interactively, asking for your project key, configuration details, and generating the appropriate API calls.

**Note:** Skills require your `LAUNCHDARKLY_ACCESS_TOKEN` environment variable to be set:
```bash
export LAUNCHDARKLY_ACCESS_TOKEN="api-xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx"
```

#### Option B: MCP Server (Alternative approach)

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

For a complete walkthrough, see the [AI Configs quickstart guide](https://docs.launchdarkly.com/home/ai-configs/quickstart).

#### Using Agent Skills (Recommended)

If your editor supports agent skills, the fastest way is to use the built-in skills:

**Step 1: Create a project (if you don't have one)**
```
/aiconfig-projects
```
This will guide you through creating a new LaunchDarkly project called `pet-store-agent`.

**Step 2: Create your AI Config**
```
/aiconfig-create
```
Claude will walk you through:
- Setting the project key (`pet-store-agent`)
- Choosing agent mode vs completion mode
- Configuring your model (e.g., `Bedrock.us.anthropic.claude-3-7-sonnet-20250219-v1:0`)
- Adding your system instructions
- Setting up custom parameters

**Step 3: Add tools to your config**
```
/aiconfig-tools
```
This helps you create and attach tools like `retrieve_product_info`, `get_inventory`, etc.

**Step 4: Add additional variations for experimentation**
```
/aiconfig-variations
```
Add a second model variation (e.g., Nova Pro) to compare performance.

#### Using MCP Server

If you're using Cursor, Claude Desktop, or another MCP-compatible IDE, ask your IDE to create an AI Config:

<details>
<summary><b>Click to expand full AI Config JSON for MCP Server</b></summary>

**To create this AI Config using the MCP server, simply ask your IDE:**

> Create an AI Config in LaunchDarkly with this configuration:

```json
{
  "LD_PROJECT_KEY": "pet-store-agent",
  "ai_config": {
    "key": "pet-store-agent",
    "name": "Pet Store Agent",
    "mode": "agent"
  },
  "variation": {
    "key": "base-config",
    "name": "Base Config",
    "modelConfigKey": "Bedrock.us.anthropic.claude-3-7-sonnet-20250219-v1:0",
    "instructions": "You are an online pet store assistant for staff. Your job is to analyze customer inputs, use the provided external tools and data sources as required, and then respond in json-only format following the schema below. Always maintain a warm and friendly tone in user message and pet advice fields.\n\n# Execution Plan:\n1. Analyze customer input and execute the next two steps (2 and 3) in parallel.\n2-a. Use UserManagement to identify user details and check if user is a subscribed customer.\n2-b. If the user is a subscribed customer, use PetCaringKnowledge if required to find pet caring details.\n3-a. Use ProductInformation to identify if we have any related product.\n3-b. For identified products, use InventoryManagement to find product inventory details.\n4. Generate final response in JSON based on all compiled information.\n\n# Business Rules:\nDon't ask for further information. You always need to generate a final response only.\nProduct identifiers are for internal use and must not appear in customer facing response messages.\nWhen preparing a customer response, use the customer's first name instead of user id or email address when possible.\nReturn Error status with a user-friendly message starting with \"We are sorry...\" when encountering internal issues - such as system errors or missing data.\nReturn Reject status with a user-friendly message starting with \"We are sorry...\" when requested products are unavailable.\nReturn Accept status with appropriate customer message when requested product is available.\nAlways avoid revealing technical system details in customer-facing message field when status is Accept, Error, or Reject.\nWhen an order can cause the remaining inventory to fall below or equal to the reorder level, flag that product for replenishment.\nOrders over $300 qualify for a 15% total discount. In addition, when buying multiple quantities of the same item, customers get 10% off on each additional unit (first item at regular price).\nShipping charges are determined by order total and item quantity. Orders $75 or above: receive free shipping. Orders under $75 with 2 items or fewer: incur $14.95 flat rate. Orders under $75 with 3 items or more: incur $19.95 flat rate.\nDesignate the customer type as Subscribed only when the user exists and maintains an active subscription. For all other cases, assume the customer type as Guest.\nFree pet care advice should only be provided when required to customers with active subscriptions in the allocated field for pet advice.\nFor each item included in an order, determine whether to trigger the inventory replenishment flag based on the projected inventory quantities that will remain after the current order is fulfilled.\n\n# Sample 1 Input:\nA new user is asking about the price of Doggy Delights?\n\n# Sample 1 Response:\n{\n    \"status\": \"Accept\",\n    \"message\": \"Dear Customer! We offer our 30lb bag of Doggy Delights for just $54.99. This premium grain-free dry dog food features real meat as the first ingredient, ensuring quality nutrition for your furry friend.\",\n    \"customerType\": \"Guest\",\n    \"items\": [\n        {\n        \"productId\": \"DD006\",\n        \"price\": 54.99,\n        \"quantity\": 1,\n        \"bundleDiscount\": 0,\n        \"total\": 54.99,\n        \"replenishInventory\": false\n        }\n    ],\n    \"shippingCost\": 14.95,\n    \"petAdvice\": \"\",\n    \"subtotal\": 69.94,\n    \"additionalDiscount\": 0,\n    \"total\": 69.94\n}\n\n# Sample 2 Input:\nCustomerId: usr_001\nCustomerRequest: I'm interested in purchasing two water bottles under your bundle deal. Would these bottles also be suitable for bathing my Chihuahua?\n\n# Sample 2 Response:\n{\n    \"status\": \"Accept\",\n    \"message\": \"Hi John, Thank you for your interest! Our Bark Park Buddy bottles are designed for hydration only, not for bathing. For your two-bottle bundle, you'll receive our 10% multi-unit discount as a valued subscriber.\",\n    \"customerType\": \"Subscribed\",\n    \"items\": [\n        {\n        \"productId\": \"BP010\",\n        \"price\": 16.99,\n        \"quantity\": 2,\n        \"bundleDiscount\": 0.10,\n        \"total\": 32.28,\n        \"replenishInventory\": false\n        }\n    ],\n    \"shippingCost\": 14.95,\n    \"petAdvice\": \"While these bottles are perfect for keeping your Chihuahua hydrated during walks with their convenient fold-out bowls, we recommend using a proper pet bath or sink with appropriate dog shampoo for bathing. The bottles are specifically designed for drinking purposes only.\",\n    \"subtotal\": 32.28,\n    \"additionalDiscount\": 0,\n    \"total\": 47.23\n}\n\n# Response Schema:\n{\n  \"$schema\": \"http://json-schema.org/draft-07/schema#\",\n  \"type\": \"object\",\n  \"required\": [\n    \"status\",\n    \"message\"\n  ],\n  \"properties\": {\n    \"status\": {\n      \"type\": \"string\",\n      \"enum\": [\n        \"Accept\",\n        \"Reject\",\n        \"Error\"\n      ]\n    },\n    \"message\": {\n      \"type\": \"string\",\n      \"maxLength\": 250\n    },\n    \"customerType\": {\n      \"type\": \"string\",\n      \"enum\": [\n        \"Guest\",\n        \"Subscribed\"\n      ]\n    },\n    \"items\": {\n      \"type\": \"array\",\n      \"minItems\": 1,\n      \"items\": {\n        \"type\": \"object\",\n        \"properties\": {\n          \"productId\": {\n            \"type\": \"string\"\n          },\n          \"price\": {\n            \"type\": \"number\",\n            \"minimum\": 0\n          },\n          \"quantity\": {\n            \"type\": \"integer\",\n            \"minimum\": 1\n          },\n          \"bundleDiscount\": {\n            \"type\": \"number\",\n            \"minimum\": 0,\n            \"maximum\": 1\n          },\n          \"total\": {\n            \"type\": \"number\",\n            \"minimum\": 0\n          },\n          \"replenishInventory\": {\n            \"type\": \"boolean\"\n          }\n        }\n      }\n    },\n    \"shippingCost\": {\n      \"type\": \"number\",\n      \"minimum\": 0\n    },\n    \"petAdvice\": {\n      \"type\": \"string\",\n      \"maxLength\": 500\n    },\n    \"subtotal\": {\n      \"type\": \"number\",\n      \"minimum\": 0\n    },\n    \"additionalDiscount\": {\n      \"type\": \"number\",\n      \"minimum\": 0,\n      \"maximum\": 1\n    },\n    \"total\": {\n      \"type\": \"number\",\n      \"minimum\": 0\n    }\n  }\n}",
    "tools": [
      {"key": "retrieve_product_info", "version": 1},
      {"key": "retrieve_pet_care", "version": 1},
      {"key": "get_inventory", "version": 1},
      {"key": "get_user_by_id", "version": 1},
      {"key": "get_user_by_email", "version": 1}
    ],
    "customParameters": {
      "aws_region": "us-west-2",
      "temperature": 0.7,
      "max_tokens": 4096,
      "use_real_lambda": true,
      "lambda_inventory_function": "team-PetStoreInventoryManagementFunction-XXX",
      "lambda_user_function": "team-PetStoreUserManagementFunction-XXX",
      "llamaindex_storage_dir": "./storage",
      "llamaindex_similarity_top_k": 5
    }
  }
}
```

**Note:**
- Replace Lambda function names with your actual CloudFormation output values
- The `modelConfigKey` format is `Provider.ModelId` (e.g., `Bedrock.us.anthropic.claude-3-7-sonnet-20250219-v1:0`)
- **RAG Tools** (LlamaIndex implementation):
  - `retrieve_product_info` - Searches product catalog using LlamaIndex vector store
  - `retrieve_pet_care` - Searches pet care knowledge using LlamaIndex vector store
- **Lambda Tools** (same for all versions):
  - `get_inventory` - Checks product inventory via Lambda
  - `get_user_by_id` - Retrieves user info by ID via Lambda
  - `get_user_by_email` - Retrieves user info by email via Lambda

</details>

Or simply ask your IDE: "Create an AI Config in project pet-store-agent with the configuration from the JSON above"

<details>
<summary><b>Bedrock Knowledge Bases Version</b></summary>

If you're using Amazon Bedrock Knowledge Bases instead of LlamaIndex for RAG, use this configuration:

**To create this AI Config using the MCP server, ask your IDE:**

> Create an AI Config in LaunchDarkly with this configuration:

```json
{
  "LD_PROJECT_KEY": "pet-store-agent",
  "ai_config": {
    "key": "pet-store-agent",
    "name": "Pet Store Agent",
    "mode": "agent"
  },
  "variation": {
    "key": "bedrock-kb-config",
    "name": "Base Config - Bedrock KB",
    "modelConfigKey": "Bedrock.us.anthropic.claude-3-7-sonnet-20250219-v1:0",
    "instructions": "You are an online pet store assistant for staff. Your job is to analyze customer inputs, use the provided external tools and data sources as required, and then respond in json-only format following the schema below. Always maintain a warm and friendly tone in user message and pet advice fields.\n\n# Execution Plan:\n1. Analyze customer input and execute the next two steps (2 and 3) in parallel.\n2-a. Use UserManagement to identify user details and check if user is a subscribed customer.\n2-b. If the user is a subscribed customer, use PetCaringKnowledge if required to find pet caring details.\n3-a. Use ProductInformation to identify if we have any related product.\n3-b. For identified products, use InventoryManagement to find product inventory details.\n4. Generate final response in JSON based on all compiled information.\n\n# Business Rules:\nDon't ask for further information. You always need to generate a final response only.\nProduct identifiers are for internal use and must not appear in customer facing response messages.\nWhen preparing a customer response, use the customer's first name instead of user id or email address when possible.\nReturn Error status with a user-friendly message starting with \"We are sorry...\" when encountering internal issues - such as system errors or missing data.\nReturn Reject status with a user-friendly message starting with \"We are sorry...\" when requested products are unavailable.\nReturn Accept status with appropriate customer message when requested product is available.\nAlways avoid revealing technical system details in customer-facing message field when status is Accept, Error, or Reject.\nWhen an order can cause the remaining inventory to fall below or equal to the reorder level, flag that product for replenishment.\nOrders over $300 qualify for a 15% total discount. In addition, when buying multiple quantities of the same item, customers get 10% off on each additional unit (first item at regular price).\nShipping charges are determined by order total and item quantity. Orders $75 or above: receive free shipping. Orders under $75 with 2 items or fewer: incur $14.95 flat rate. Orders under $75 with 3 items or more: incur $19.95 flat rate.\nDesignate the customer type as Subscribed only when the user exists and maintains an active subscription. For all other cases, assume the customer type as Guest.\nFree pet care advice should only be provided when required to customers with active subscriptions in the allocated field for pet advice.\nFor each item included in an order, determine whether to trigger the inventory replenishment flag based on the projected inventory quantities that will remain after the current order is fulfilled.\n\n# Sample 1 Input:\nA new user is asking about the price of Doggy Delights?\n\n# Sample 1 Response:\n{\n    \"status\": \"Accept\",\n    \"message\": \"Dear Customer! We offer our 30lb bag of Doggy Delights for just $54.99. This premium grain-free dry dog food features real meat as the first ingredient, ensuring quality nutrition for your furry friend.\",\n    \"customerType\": \"Guest\",\n    \"items\": [\n        {\n        \"productId\": \"DD006\",\n        \"price\": 54.99,\n        \"quantity\": 1,\n        \"bundleDiscount\": 0,\n        \"total\": 54.99,\n        \"replenishInventory\": false\n        }\n    ],\n    \"shippingCost\": 14.95,\n    \"petAdvice\": \"\",\n    \"subtotal\": 69.94,\n    \"additionalDiscount\": 0,\n    \"total\": 69.94\n}\n\n# Sample 2 Input:\nCustomerId: usr_001\nCustomerRequest: I'm interested in purchasing two water bottles under your bundle deal. Would these bottles also be suitable for bathing my Chihuahua?\n\n# Sample 2 Response:\n{\n    \"status\": \"Accept\",\n    \"message\": \"Hi John, Thank you for your interest! Our Bark Park Buddy bottles are designed for hydration only, not for bathing. For your two-bottle bundle, you'll receive our 10% multi-unit discount as a valued subscriber.\",\n    \"customerType\": \"Subscribed\",\n    \"items\": [\n        {\n        \"productId\": \"BP010\",\n        \"price\": 16.99,\n        \"quantity\": 2,\n        \"bundleDiscount\": 0.10,\n        \"total\": 32.28,\n        \"replenishInventory\": false\n        }\n    ],\n    \"shippingCost\": 14.95,\n    \"petAdvice\": \"While these bottles are perfect for keeping your Chihuahua hydrated during walks with their convenient fold-out bowls, we recommend using a proper pet bath or sink with appropriate dog shampoo for bathing. The bottles are specifically designed for drinking purposes only.\",\n    \"subtotal\": 32.28,\n    \"additionalDiscount\": 0,\n    \"total\": 47.23\n}\n\n# Response Schema:\n{\n  \"$schema\": \"http://json-schema.org/draft-07/schema#\",\n  \"type\": \"object\",\n  \"required\": [\n    \"status\",\n    \"message\"\n  ],\n  \"properties\": {\n    \"status\": {\n      \"type\": \"string\",\n      \"enum\": [\n        \"Accept\",\n        \"Reject\",\n        \"Error\"\n      ]\n    },\n    \"message\": {\n      \"type\": \"string\",\n      \"maxLength\": 250\n    },\n    \"customerType\": {\n      \"type\": \"string\",\n      \"enum\": [\n        \"Guest\",\n        \"Subscribed\"\n      ]\n    },\n    \"items\": {\n      \"type\": \"array\",\n      \"minItems\": 1,\n      \"items\": {\n        \"type\": \"object\",\n        \"properties\": {\n          \"productId\": {\n            \"type\": \"string\"\n          },\n          \"price\": {\n            \"type\": \"number\",\n            \"minimum\": 0\n          },\n          \"quantity\": {\n            \"type\": \"integer\",\n            \"minimum\": 1\n          },\n          \"bundleDiscount\": {\n            \"type\": \"number\",\n            \"minimum\": 0,\n            \"maximum\": 1\n          },\n          \"total\": {\n            \"type\": \"number\",\n            \"minimum\": 0\n          },\n          \"replenishInventory\": {\n            \"type\": \"boolean\"\n          }\n        }\n      }\n    },\n    \"shippingCost\": {\n      \"type\": \"number\",\n      \"minimum\": 0\n    },\n    \"petAdvice\": {\n      \"type\": \"string\",\n      \"maxLength\": 500\n    },\n    \"subtotal\": {\n      \"type\": \"number\",\n      \"minimum\": 0\n    },\n    \"additionalDiscount\": {\n      \"type\": \"number\",\n      \"minimum\": 0,\n      \"maximum\": 1\n    },
    \"total\": {\n      \"type\": \"number\",\n      \"minimum\": 0\n    }\n  }\n}",
    "tools": [
      {"key": "ProductInformation", "version": 1},
      {"key": "PetCaringKnowledge", "version": 1},
      {"key": "get_inventory", "version": 1},
      {"key": "get_user_by_id", "version": 1},
      {"key": "get_user_by_email", "version": 1}
    ],
    "customParameters": {
      "aws_region": "us-west-2",
      "temperature": 0.7,
      "max_tokens": 4096,
      "use_real_lambda": true,
      "knowledge_base_1_id": "XXXXXXXXXX",
      "knowledge_base_2_id": "YYYYYYYYYY",
      "retrieval_num_results": 10,
      "retrieval_score_threshold": 0.25,
      "lambda_inventory_function": "team-PetStoreInventoryManagementFunction-XXX",
      "lambda_user_function": "team-PetStoreUserManagementFunction-XXX"
    }
  }
}
```

**Note:**
- Replace `knowledge_base_1_id` and `knowledge_base_2_id` with your CloudFormation stack outputs
- Replace Lambda function names with your actual function names from CloudFormation
- The `modelConfigKey` format is `Provider.ModelId` (can also use `Bedrock.amazon.nova-pro-v1:0` for Nova Pro)
- **RAG Tools** (Bedrock Knowledge Bases):
  - `ProductInformation` - Calls `bedrock-agent-runtime` API using `knowledge_base_1_id` for product catalog
  - `PetCaringKnowledge` - Calls `bedrock-agent-runtime` API using `knowledge_base_2_id` for pet care
  - Parameters: `retrieval_num_results` (default: 10), `retrieval_score_threshold` (default: 0.25)
- **Lambda Tools** (same for all versions):
  - `get_inventory` - Invokes Lambda using `lambda_inventory_function` name
  - `get_user_by_id` - Invokes Lambda using `lambda_user_function` name
  - `get_user_by_email` - Invokes Lambda using `lambda_user_function` name

</details>

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

**Tip:** You can quickly create and iterate on AI Configs using Agent Skills (works in any compatible editor) or LaunchDarkly's MCP server.

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

#### Using Agent Skills for SDK Integration

The `/aiconfig-sdk` skill can help you instrument your code:
```
/aiconfig-sdk
```

This skill will:
- Show you how to initialize the LaunchDarkly AI SDK
- Generate code for fetching AI Configs in agent mode
- Help you build user contexts with `/aiconfig-context-basic`
- Add metrics tracking with `/aiconfig-ai-metrics`

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

Use `agent()` for agent-based AI Configs:

```python
from ldai.client import AIAgentConfigRequest, AIAgentConfigDefault

agent = ai_client.agent(
    AIAgentConfigRequest(
        key="pet-store-agent",
        default_value=AIAgentConfigDefault(enabled=False)
    ),
    context
)

# Extract configuration
# The agent object provides: enabled, instructions, model, provider, tracker
# Model config uses private attributes _parameters and _custom
model_name = agent.model.name
provider_name = agent.provider.name
instructions = agent.instructions
parameters = agent.model._parameters if agent.model else {}
custom = agent.model._custom if agent.model else {}
tools_config = parameters.get("tools", [])
tracker = agent.tracker
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
tracker = agent.tracker

try:
    # Use track_duration_of() wrapper for automatic duration tracking
    result = tracker.track_duration_of(lambda: agent.invoke(input_))

    tracker.track_success()

    from ldai.tracker import TokenUsage
    usage = TokenUsage(input=100, output=200, total=300)
    tracker.track_tokens(usage)

except Exception as e:
    tracker.track_error()
    raise
```

**Available tracking methods:**
- `tracker.track_duration_of(callable)` - Wraps execution and automatically tracks duration
- `tracker.track_duration(ms)` - Manual duration tracking (use track_duration_of() instead)
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
        from ldai.client import AIAgentConfigRequest, AIAgentConfigDefault

        agent = self.ai.agent(
            AIAgentConfigRequest(
                key="pet-store-agent",
                default_value=AIAgentConfigDefault(enabled=False)
            ),
            ctx
        )

        # Extract configuration
        # Access agent attributes directly as per LaunchDarkly Python AI SDK best practices
        # Model config uses private attributes _parameters and _custom
        model_name = agent.model.name
        provider = agent.provider.name
        instructions = agent.instructions
        parameters = agent.model._parameters if agent.model else {}
        custom = agent.model._custom if agent.model else {}
        tracker = agent.tracker

        # Step 4: Build tools dynamically
        tools = self.build_tools(parameters.get("tools", []), custom)

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
            # Use track_duration_of() wrapper for automatic duration tracking
            result = tracker.track_duration_of(
                lambda: graph.invoke(
                    {"messages": [HumanMessage(content=prompt)]},
                    config={"configurable": {"thread_id": user_ctx.get("thread_id", "default")}}
                )
            )

            tracker.track_success()

            # Extract token usage from messages
            usage = self._collect_token_usage(result.get("messages", []))
            if usage:
                tracker.track_tokens(usage)

            return result
        except Exception as e:
            tracker.track_error()
            raise
        finally:
            # Flush analytics events for short-lived Lambda contexts
            # This ensures metrics are delivered to LaunchDarkly before the Lambda terminates
            if os.environ.get("AWS_LAMBDA_FUNCTION_NAME"):
                ldclient.get().flush()

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
        from ldai.client import AIAgentConfigRequest, AIAgentConfigDefault

        agent_config = self.ai.agent(
            AIAgentConfigRequest(
                key="pet-store-agent",
                default_value=AIAgentConfigDefault(enabled=False)
            ),
            ctx
        )

        # Access agent attributes directly as per LaunchDarkly Python AI SDK best practices
        # Model config uses private attributes _parameters and _custom
        model_name = agent_config.model.name
        instructions = agent_config.instructions
        parameters = agent_config.model._parameters if agent_config.model else {}
        custom = agent_config.model._custom if agent_config.model else {}
        tracker = agent_config.tracker

        # Step 4: Build Strands agent
        agent = Agent(
            model=model_name,
            system_prompt=instructions,
            tools=self.build_tools(parameters.get("tools", []), custom)
        )

        # Step 5: Track metrics
        try:
            # Use track_duration_of() wrapper for automatic duration tracking
            result = tracker.track_duration_of(
                lambda: await agent.run(
                    prompt,
                    callbacks=[self._create_tracking_callback(tracker)]
                )
            )

            tracker.track_success()

            return result
        except Exception as e:
            tracker.track_error()
            raise

    def _create_tracking_callback(self, tracker):
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

#### Using Agent Skills (Recommended)

```
/aiconfig-targeting
```

This skill will guide you through:
- Adding targeting rules based on user attributes (e.g., `subscription_status`)
- Setting up percentage rollouts for experiments
- Configuring the default rule
- Managing segment-based targeting

You can also use `/aiconfig-segments` to create reusable user segments first:
```
/aiconfig-segments
```

#### Using MCP Server

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

**4b.** Practice dynamic updates using agent skills (`/aiconfig-targeting`) or your IDE's MCP server to quickly iterate on targeting rules

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

Before creating your experiment, add a second variation to compare. Use agent skills or the MCP server:

**Using Agent Skills:**
```
/aiconfig-variations
```
This will guide you through adding a new variation with a different model (e.g., Nova Pro) while keeping tools and parameters the same.

**Using MCP Server or UI:** Same process as step 2 - just pick a different model while keeping tools and parameters the same.

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

Click **"Save"** to create the experiment.

<figure style="margin: 20px 0;">
  <img src="images/premium_model.png" alt="Experiment Configuration Example" width="600" style="border: 1px solid #ddd; border-radius: 4px; padding: 5px;">
  <figcaption style="margin-top: 8px; font-style: italic; color: #666; text-align: center;">Example experiment configuration in LaunchDarkly</figcaption>
</figure>

**IMPORTANT:** For this competition, **DO NOT start the experiment** yet. Just save the experiment configuration. Starting an experiment will modify your targeting rules, which may interfere with Step 4's targeting configuration. You'll get full credit for having a properly configured experiment, even if it's not running.

**Note:** If you do start the experiment later, remember that it will take over the targeting configuration. You can stop it anytime to restore normal targeting.

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
