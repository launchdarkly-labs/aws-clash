# Pet Store Agent

A LangGraph-based conversational AI agent for a virtual pet store, featuring RAG capabilities via LlamaIndex and dynamic configuration through LaunchDarkly.

## Features

- **RAG-based Product Information**: Uses LlamaIndex to retrieve product details from indexed PDFs
- **Dynamic Configuration**: LaunchDarkly integration for feature flags and real-time config updates
- **AWS Bedrock Integration**: Leverages AWS Nova Pro model for LLM capabilities
- **Tool-based Architecture**: Modular tools for inventory, user management, and pet care advice
- **AgentCore Ready**: Deployable to AWS AgentCore runtime

## Project Structure

```
pet_store_agent/
├── data/                                 # RAG data files (PDFs)
├── storage/                              # LlamaIndex vector storage
├── pet_store_agent_full_ld.py          # Main agent implementation
├── tool_registry.py                     # Tool definitions and builders
├── query_agent.py                       # Local testing script
├── run_local.sh                         # Shell wrapper for local testing
├── agentcore_entrypoint.py             # AgentCore entry point
├── agentcore_handler.py                # AgentCore Lambda handler
├── requirements.txt                     # Python dependencies
├── Dockerfile                           # Container definition for AgentCore
├── test_buildspec.yml                  # AWS CodeBuild spec
└── deploy-langgraph-agent-to-agentcore.ipynb  # Deployment notebook
```

## Setup

### Prerequisites

1. AWS credentials configured (`AWS_PROFILE=bedrock-demo`)
2. LaunchDarkly SDK key in `.env` file
3. Python 3.9+ with virtual environment
4. Docker for containerization

### Environment Variables

Create a `.env` file in the parent directory:
```bash
LAUNCHDARKLY_SDK_KEY=your-sdk-key-here
AWS_PROFILE=bedrock-demo
AWS_DEFAULT_REGION=us-east-1
```

### Installation

```bash
# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

## Usage

### Running Tests

**Default test suite (3 test queries):**
```bash
./run_local.sh
```

**Interactive mode:**
```bash
./run_local.sh --interactive
```

**Single query:**
```bash
./run_local.sh "What is the price of Doggy Delights?"
```

**Debug mode (verbose output):**
```bash
DEBUG_MODE=true ./run_local.sh
```

### Available Tools

1. **retrieve_product_info**: RAG-based product search
2. **retrieve_pet_care**: Pet care advice retrieval
3. **get_inventory**: Product inventory lookup
4. **get_user_by_email**: User information by email
5. **get_user_by_id**: User information by ID

### Configuration

The agent pulls configuration from LaunchDarkly, including:
- Model parameters (temperature, max_tokens)
- Tool configurations (Lambda ARNs, RAG settings)
- Feature flags (use_real_lambda)

Key configuration fields:
- `lambda_inventory_function`: Inventory Lambda function name
- `lambda_user_function`: User management Lambda function name
- `llamaindex_storage_dir`: RAG vector storage directory
- `llamaindex_similarity_top_k`: Number of RAG results to return

## Deployment

### Local Docker Build

```bash
docker build -t pet-store-agent:latest --platform linux/arm64 .
```

### Deploy to AgentCore

Use the Jupyter notebook for step-by-step deployment:
```bash
jupyter notebook deploy-langgraph-agent-to-agentcore.ipynb
```

## Logging

The agent provides detailed logging for debugging:
- Tool configuration parameters from LaunchDarkly
- Tool execution inputs and outputs
- LLM interactions and token usage

Enable debug logging:
```bash
export DEBUG_MODE=true
```

## Testing

The test suite covers:
- Product pricing queries
- Product information retrieval
- Pet care advice
- Different user subscription statuses
- Tool execution paths

## Troubleshooting

Common issues and solutions:

1. **ImportError for LlamaIndex**: Ensure all dependencies in requirements.txt are installed
2. **Embedding dimension mismatch**: Agent uses `amazon.titan-embed-text-v2:0` (1024 dimensions)
3. **AWS credentials**: Set `AWS_PROFILE=bedrock-demo` or configure boto3 session
4. **LaunchDarkly SDK key**: Must be set in environment or `.env` file

## License

Proprietary - AWS re:Invent 2024 Competition