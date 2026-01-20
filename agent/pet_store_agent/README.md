# Pet Store Agent

LaunchDarkly AI-powered agent for a virtual pet store, featuring RAG, Lambda integration, and dynamic configuration.

## Quick Start

### Prerequisites
- Python 3.9+
- LaunchDarkly SDK Key
- AWS credentials (for Bedrock and Lambda)

### Installation

```bash
cd agent/pet_store_agent
pip install -r requirements.txt
```

### Environment Variables

```bash
export LAUNCHDARKLY_SDK_KEY='your-sdk-key'
export AWS_PROFILE='your-profile'  # or AWS credentials
export DEBUG_MODE=false
```

### Running Locally

```bash
# Single query
python query_agent.py "What is the price of Doggy Delights?"

# Interactive mode
python query_agent.py --interactive
```

## Architecture

### Components

- **Main Agent** (`pet_store_agent_full_ld.py`) - LaunchDarkly AI SDK integration, LangGraph ReAct agent
- **Tool Registry** (`tool_registry.py`) - 5 tools (2 RAG + 3 Lambda)

### Tools

| Tool | Type | Purpose |
|------|------|---------|
| `retrieve_product_info` | RAG | Search product catalog using LlamaIndex |
| `retrieve_pet_care` | RAG | Retrieve pet care advice |
| `get_inventory` | Lambda/Mock | Get product inventory data |
| `get_user_by_email` | Lambda/Mock | Look up user by email |
| `get_user_by_id` | Lambda/Mock | Look up user by ID |

## Configuration Parameters

All configuration managed through LaunchDarkly Agent API `custom` parameters:

```json
{
  "aws_region": "us-west-2",
  "temperature": 0.7,
  "max_tokens": 4096,
  "use_real_lambda": true,
  "lambda_inventory_function": "team-PetStoreInventoryManagementFunction-XXX",
  "lambda_user_function": "team-PetStoreUserManagementFunction-XXX",
  "llamaindex_storage_dir": "./storage",
  "llamaindex_petcare_storage_dir": "./storage_petcare",
  "llamaindex_similarity_top_k": 5
}
```

### Parameter Reference

| Parameter | Type | Default | Purpose |
|-----------|------|---------|---------|
| `aws_region` | string | `us-east-1` | AWS region for all services |
| `temperature` | float | `0.7` | LLM randomness (0.0-1.0) |
| `max_tokens` | int | `4096` | Max LLM response tokens |
| `use_real_lambda` | bool | `false` | Real Lambda vs mock data |
| `lambda_inventory_function` | string | See below* | Inventory Lambda function |
| `lambda_user_function` | string | See below* | User Lambda function |
| `llamaindex_storage_dir` | string | `./storage` | Product catalog index path |
| `llamaindex_petcare_storage_dir` | string | `./storage_petcare` | Pet care index path |
| `llamaindex_similarity_top_k` | int | `5` | RAG results count |

\* Defaults: `team-PetStoreInventoryManagementFunction`, `team-PetStoreUserManagementFunction`

### Configuration Precedence

**LLM Parameters** (`temperature`, `max_tokens`):
1. `custom` config (highest)
2. `parameters` config
3. Default values

**Tool Parameters**: `custom` → environment variables → defaults

### Example Configurations

**Local Development:**
```json
{
  "aws_region": "us-west-2",
  "use_real_lambda": false,
  "llamaindex_similarity_top_k": 5
}
```

**Production:**
```json
{
  "aws_region": "us-west-2",
  "temperature": 0.7,
  "use_real_lambda": true,
  "lambda_inventory_function": "prod-PetStoreInventory-ABC",
  "lambda_user_function": "prod-PetStoreUser-DEF"
}
```

**High Precision RAG:**
```json
{
  "temperature": 0.3,
  "llamaindex_similarity_top_k": 10
}
```

## LaunchDarkly Integration

Uses LaunchDarkly AI SDK for dynamic configuration:
- Agent enable/disable
- Model and provider selection
- Tool management
- Runtime parameter tuning
- Metrics tracking (tokens, duration, success/errors)

### Creating AI Config via MCP Server

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
    "modelConfigKey": "Bedrock.amazon.nova-pro-v1:0",
    "instructions": "Your system prompt...",
    "tools": [
      {"key": "retrieve_product_info", "version": 1},
      {"key": "retrieve_pet_care", "version": 1},
      {"key": "get_inventory", "version": 1},
      {"key": "get_user_by_id", "version": 1},
      {"key": "get_user_by_email", "version": 1}
    ],
    "customParameters": { /* parameters from above */ }
  }
}
```

## Files

```
pet_store_agent/
├── pet_store_agent_full_ld.py  # Main agent class
├── tool_registry.py             # Tool builders
├── query_agent.py               # Local testing CLI
├── agentcore_handler.py         # AWS Lambda handler
├── storage/                     # Product catalog index
├── storage_petcare/             # Pet care index
└── data/                        # Source documents
```

## Key Features

✅ Dynamic configuration via LaunchDarkly
✅ Mock/Real Lambda toggle
✅ RAG with LlamaIndex + Bedrock
✅ 5 tools with flexible config
✅ Clean, production-ready code
✅ All 9 parameters actively used
