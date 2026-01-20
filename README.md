# Pet Store Agent - AWS Clash Competition

LaunchDarkly AI-powered agent for Virtual Pet Store customer service, built with LangGraph and deployed to AWS Bedrock AgentCore.

## Quick Start

```bash
# Clone and setup
git clone <repo-url>
cd aws_clash
python3 -m venv venv
source venv/bin/activate
pip install -r agent/pet_store_agent/requirements.txt

# Configure environment
export LAUNCHDARKLY_SDK_KEY='your-sdk-key'
export AWS_PROFILE='your-profile'
export AWS_DEFAULT_REGION='us-east-1'

# Test locally
cd agent/pet_store_agent
python query_agent.py "What is the price of Doggy Delights?"
```

## Repository Structure

```
aws_clash/
├── README.md                           # This file
├── agent/
│   ├── pet_store_agent/               # Main agent implementation
│   │   ├── README.md                  # Agent documentation & configuration
│   │   ├── pet_store_agent_full_ld.py # LaunchDarkly AI SDK integration
│   │   ├── tool_registry.py           # Tool definitions (5 tools)
│   │   ├── query_agent.py             # Local testing CLI
│   │   ├── storage/                   # Product catalog RAG index
│   │   └── data/                      # Source PDFs for RAG
│   └── knowledge_bases/
│       ├── README.md                  # PDF documentation
│       └── *.pdf                      # Product catalog PDFs
├── .env.example                       # Environment template
└── venv/                              # Python virtual environment
```

## Key Features

✅ **LaunchDarkly AI Configs** - Dynamic model switching without redeployment
✅ **LlamaIndex RAG** - Product catalog retrieval from local PDFs
✅ **LangGraph ReAct Agent** - Tool orchestration with reasoning
✅ **AWS Bedrock** - Nova Pro & Claude models
✅ **5 Tools** - 2 RAG + 3 Lambda/Mock
✅ **Flexible Configuration** - All params via LaunchDarkly custom config

## Architecture

```
User Request
    ↓
LaunchDarkly AI Config (dynamic model selection)
    ↓
LangGraph ReAct Agent
    ├─→ retrieve_product_info (LlamaIndex RAG)
    ├─→ retrieve_pet_care (LlamaIndex RAG)
    ├─→ get_inventory (Lambda/Mock)
    ├─→ get_user_by_email (Lambda/Mock)
    └─→ get_user_by_id (Lambda/Mock)
    ↓
AWS Bedrock (Nova Pro / Claude)
    ↓
JSON Response
```

## Configuration

All configuration managed through **LaunchDarkly Agent API** custom parameters:

```json
{
  "aws_region": "us-west-2",
  "temperature": 0.7,
  "max_tokens": 4096,
  "use_real_lambda": true,
  "lambda_inventory_function": "team-PetStoreInventoryFunction-XXX",
  "lambda_user_function": "team-PetStoreUserFunction-XXX",
  "llamaindex_storage_dir": "./storage",
  "llamaindex_petcare_storage_dir": "./storage_petcare",
  "llamaindex_similarity_top_k": 5
}
```

See **[agent/pet_store_agent/README.md](./agent/pet_store_agent/README.md)** for complete parameter reference and configuration details.

## LaunchDarkly Setup

1. **Create AI Config** at https://app.launchdarkly.com
   - Key: `pet-store-agent`
   - Provider: AWS Bedrock
   - Model: `amazon.nova-pro-v1:0`

2. **Add Tools** (in LaunchDarkly UI):
   - `retrieve_product_info`
   - `retrieve_pet_care`
   - `get_inventory`
   - `get_user_by_email`
   - `get_user_by_id`

3. **Configure Custom Parameters** (see above)

4. **Add Instructions** (system prompt)

5. **Enable Targeting** → Default rule → Select variation → Save

## Deployment

### Local Testing

```bash
cd agent/pet_store_agent
python query_agent.py "What is the price of Doggy Delights?"
python query_agent.py --interactive  # Interactive mode
```

### AWS AgentCore Deployment

```bash
# Build Docker image for ARM64
docker build --platform linux/arm64 -t petstore-agent:latest \
  -f agent/Dockerfile agent/

# Push to ECR
aws ecr get-login-password --region us-east-1 | \
  docker login --username AWS --password-stdin <account>.dkr.ecr.us-east-1.amazonaws.com
docker tag petstore-agent:latest <account>.dkr.ecr.us-east-1.amazonaws.com/petstore-agent:latest
docker push <account>.dkr.ecr.us-east-1.amazonaws.com/petstore-agent:latest

# Deploy to AgentCore
cd agent
python deploy_to_agentcore.py
```

## Competition Strategy

**Key Advantage:** Update configuration in LaunchDarkly without redeployment!

```
Submit ARN → Get Score → Update LaunchDarkly Config → Retest → Resubmit
```

No container rebuild or redeployment needed - iterate on:
- Model selection (Nova Pro / Claude Sonnet / Claude Haiku)
- Temperature and max_tokens
- System prompt/instructions
- Tool parameters

## Testing

**Local:**
```bash
cd agent/pet_store_agent
python query_agent.py "query here"
```

**Interactive:**
```bash
python query_agent.py --interactive
```

**Deployed:**
```bash
aws bedrock-agentcore invoke-agent-runtime \
  --agent-runtime-arn "arn:aws:bedrock-agentcore:us-east-1:<account>:runtime/<id>" \
  --qualifier DEFAULT \
  --content-type application/json \
  --payload '{"prompt":"What is the price of Doggy Delights?"}' \
  --region us-east-1 \
  response.json
```

## Documentation

- **[agent/pet_store_agent/README.md](./agent/pet_store_agent/README.md)** - Agent implementation, configuration, and parameters
- **[agent/knowledge_bases/README.md](./agent/knowledge_bases/README.md)** - PDF documentation
- **[.env.example](./.env.example)** - Environment variable template

## Monitoring

- **CloudWatch Logs:** `aws logs tail agents/petstore-agent-logs --follow`
- **LaunchDarkly Dashboard:** AI Config metrics, token usage, errors
- **AWS Console:** AgentCore runtime status and health

## Troubleshooting

**Agent not responding?**
```bash
aws bedrock-agentcore-control get-agent-runtime \
  --agent-runtime-id <runtime-id> --region us-east-1
```

**LaunchDarkly connection failed?**
- Check SDK key in environment variables
- Verify CloudWatch logs for initialization errors
- Ensure network mode is PUBLIC in runtime config

**Import errors?**
```bash
pip install -r agent/pet_store_agent/requirements.txt
```

## Built With

- **LaunchDarkly AI SDK** - Dynamic AI configuration
- **LangGraph** - ReAct agent framework
- **LlamaIndex** - Local RAG implementation
- **AWS Bedrock** - Nova Pro & Claude models
- **AWS AgentCore** - Containerized runtime

---

**For detailed implementation and configuration:** [agent/pet_store_agent/README.md](./agent/pet_store_agent/README.md)
