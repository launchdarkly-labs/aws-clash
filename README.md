# Pet Store Agent with LaunchDarkly for AWS Clash Competition

A production-ready AI agent for Virtual Pet Store customer service, built with LangGraph and LaunchDarkly AI Configs, deployed to AWS Bedrock AgentCore.

## 🎯 Overview

This repository demonstrates a **complete LaunchDarkly AI solution** for the AWS Clash competition. The agent handles customer inquiries, product information, inventory management, and order processing with dynamic model configuration via LaunchDarkly.

### Key Features

- ✅ **LaunchDarkly AI Configs**: Dynamic model switching and A/B testing
- ✅ **LlamaIndex RAG**: Advanced retrieval from PDF knowledge bases
- ✅ **LangGraph Agent**: ReAct-style reasoning with tool orchestration
- ✅ **AWS Bedrock**: Nova Pro and Claude models via Amazon Bedrock
- ✅ **AgentCore Deployment**: Containerized runtime on ARM64
- ✅ **OpenTelemetry**: Full observability and tracing
- ✅ **Competition Ready**: Handles all 11 evaluation prompts

---

## 📁 Repository Structure

```
.
├── README.md                      # This file - complete solution guide
├── agent/                         # Agent code and deployment
│   ├── pet_store_agent/          # Main agent implementation
│   │   ├── pet_store_agent_full_ld.py  # LaunchDarkly + LlamaIndex agent
│   │   ├── agentcore_entrypoint.py     # AgentCore entry point
│   │   ├── requirements.txt            # Python dependencies
│   │   ├── llamaindex_retrieval.py     # LlamaIndex RAG implementation
│   │   ├── inventory_management.py     # Inventory management (Lambda)
│   │   ├── user_management.py          # User lookup (Lambda)
│   │   └── data/                       # PDF documents for LlamaIndex
│   ├── knowledge_bases/          # KB PDFs for AWS Knowledge Bases
│   │   ├── Pet Store Product Catalog.pdf
│   │   └── Pet Store Product Content.pdf
│   ├── deploy_to_agentcore.py    # Deployment script
│   ├── test_deployment.py        # Interactive CLI to test deployed agent
│   ├── setup_launchdarkly.py     # LaunchDarkly configuration helper
│   ├── Dockerfile                # Docker configuration
│   └── requirements.txt          # Build dependencies
└── clash_documents/               # Workshop materials
    ├── LAUNCHDARKLY.md           # LaunchDarkly integration guide
    └── images/                    # Screenshots and diagrams
```

---

## 🚀 Quick Start

### Prerequisites

- **AWS Account** with Bedrock access (us-east-1)
- **LaunchDarkly Account** with AI Configs enabled
- **Docker** installed locally
- **Python 3.12+**
- **AWS CLI** configured with appropriate credentials

### 1. Clone and Setup

```bash
git clone <your-repo-url>
cd aws_clash

# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r agent/requirements.txt
```

### 2. Configure Environment

Create or update `.env` file:

```env
AWS_PROFILE=bedrock-demo
AWS_DEFAULT_REGION=us-east-1
LAUNCHDARKLY_SDK_KEY=your-sdk-key-here
```

### 3. Test Locally

```bash
cd agent/pet_store_agent
export AWS_PROFILE=bedrock-demo
export AWS_DEFAULT_REGION=us-east-1
python query_agent.py "What is the price of Doggy Delights?"
```

Expected output: Valid JSON response with product details.

### 4. Build & Deploy

```bash
cd agent

# Build Docker image for ARM64
docker build --platform linux/arm64 -t petstore-ld-agent:latest -f Dockerfile .

# Login to ECR
export AWS_PROFILE=bedrock-demo
aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin <account-id>.dkr.ecr.us-east-1.amazonaws.com

# Tag and push
docker tag petstore-ld-agent:latest <account-id>.dkr.ecr.us-east-1.amazonaws.com/petstore-ld-agent-repo:latest
docker push <account-id>.dkr.ecr.us-east-1.amazonaws.com/petstore-ld-agent-repo:latest

# Deploy to AgentCore
python deploy_to_agentcore.py
```

**Note:** Update the deployment script with your specific values:
- IAM Role ARN
- ECR Repository URI
- LaunchDarkly SDK Key

### 5. Submit to Competition

Use the AgentCore Runtime ARN from the deployment output:

```
arn:aws:bedrock-agentcore:us-east-1:<account-id>:runtime/<runtime-id>
```

---

## 🎨 LaunchDarkly Configuration

### 1. Create AI Config

Go to https://app.launchdarkly.com and create a new AI Config:

- **Name:** Pet Store Agent
- **Key:** `pet-store-agent`
- **Type:** Agent-based
- **Provider:** AWS Bedrock
- **Model:** `us.amazon.nova-pro-v1:0`
- **Temperature:** 0.3
- **Max Tokens:** 3000

### 2. Set Instructions

Add your agent instructions directly in the LaunchDarkly AI Config UI.

**Instructions should include:**
- Execution plan with parallel operations
- Business rules (pricing, discounts, shipping)
- Reject conditions (non-cat/dog pets, malicious input)
- Error handling patterns
- JSON response format

**Note:** All instructions are managed in LaunchDarkly - no hardcoded prompts in code.

### 3. Enable Targeting

1. Go to **Targeting** tab
2. Click **Edit** on Default rule
3. Select your variation
4. Type "Production" to confirm
5. Click **Save**

### 4. Create Experiments (Optional)

Test different models for optimal performance:

- **Control:** Nova Pro (cost-effective baseline)
- **Treatment A:** Claude Sonnet (high quality)
- **Treatment B:** Claude Haiku (speed optimized)

Track metrics: Success rate, latency, cost per invocation

---

## 📊 Architecture

```
User Request
    ↓
AgentCore Runtime (ARM64 Container)
    ↓
LaunchDarkly AI Config ← Dynamic model selection
    ↓
LangGraph ReAct Agent
    ├─→ LlamaIndex RAG (Product Info from PDFs)
    ├─→ LlamaIndex RAG (Pet Care from PDFs)
    ├─→ get_inventory (Lambda)
    ├─→ get_user_by_id / get_user_by_email (Lambda)
    └─→ AWS Bedrock Titan Embeddings
    ↓
AWS Bedrock (Nova Pro / Claude)
    ↓
JSON Response
```

### LlamaIndex RAG Implementation

This solution uses **LlamaIndex** for retrieval-augmented generation (RAG):

- **Local vector store** built from PDF documents
- **Amazon Titan Embeddings** (amazon.titan-embed-text-v2:0) for vectorization
- **Chunking strategy**: 512 tokens with 100 token overlap
- **Top-k retrieval**: Returns 5 most similar document chunks
- **Automatic index building** on first run from `agent/pet_store_agent/data/` directory

The LlamaIndex implementation provides:
- **Product information** from Pet Store Product Catalog and Content PDFs
- **Pet care advice** from curated pet care documents
- **Better context** for the agent's decision-making
- **No external dependencies** on AWS Knowledge Bases (fully self-contained)

### Lambda Functions for External Systems

The agent integrates with two AWS Lambda functions for business logic:

#### 1. Inventory Management (`inventory_management.py`)
**Purpose:** Real-time product inventory queries

**What it does:**
- Queries product stock levels
- Returns availability status (in_stock, low_stock, out_of_stock)
- Provides reorder levels for inventory replenishment
- Supports single product or full catalog queries

**Current Implementation:**
```python
# agent/pet_store_agent/inventory_management.py
def get_inventory(product_id: str, function_name: str) -> str:
    """Invokes Lambda function for inventory lookup"""
    lambda_client = boto3.client('lambda')
    response = lambda_client.invoke(
        FunctionName=function_name,
        Payload=json.dumps({
            "function": "getInventory",
            "parameters": [{"name": "product_code", "value": product_id}]
        })
    )
```

**Deployed Lambda:** `PetStoreInventoryManagement` (us-east-1:955116512041)

#### 2. User Management (`user_management.py`)
**Purpose:** Customer profile and subscription lookups

**What it does:**
- Retrieves user information by ID or email
- Checks subscription status (active/expired)
- Returns transaction history
- Determines customer eligibility for benefits (pet care advice, discounts)

**Current Implementation:**
```python
# agent/pet_store_agent/user_management.py
def get_user_by_id(user_id: str, function_name: str) -> str:
    """Invokes Lambda function for user lookup by ID"""

def get_user_by_email(email: str, function_name: str) -> str:
    """Invokes Lambda function for user lookup by email"""
```

**Deployed Lambda:** `PetStoreUserManagement` (us-east-1:955116512041)

### How to Swap Lambda Functions for Alternatives

The Lambda functions are **pluggable** - you can replace them with other implementations without changing the agent code:

#### Option 1: Use Different Lambda Functions
Update LaunchDarkly custom parameters:
```json
{
  "lambda_inventory_function": "MyCustomInventoryFunction",
  "lambda_user_function": "MyCustomUserFunction"
}
```

#### Option 2: Direct Database Access
Replace Lambda calls with direct database queries:

**1. Update `inventory_management.py`:**
```python
import psycopg2  # or your database library

def get_inventory(product_id: str, function_name: str = None) -> str:
    """Query inventory directly from PostgreSQL"""
    conn = psycopg2.connect(os.environ['DATABASE_URL'])
    cursor = conn.cursor()
    cursor.execute(
        "SELECT product_code, name, quantity, status FROM inventory WHERE product_code = %s",
        (product_id,)
    )
    result = cursor.fetchone()
    return json.dumps({
        "product_code": result[0],
        "name": result[1],
        "quantity": result[2],
        "status": result[3]
    })
```

**2. Update Dockerfile to include database driver:**
```dockerfile
RUN pip install psycopg2-binary
```

#### Option 3: Mock/Testing Implementation
For local testing without AWS resources:

**Create `mock_inventory.py`:**
```python
MOCK_INVENTORY = {
    "DD006": {"name": "Doggy Delights", "quantity": 200, "status": "in_stock"},
    "BP010": {"name": "Water Bottles", "quantity": 150, "status": "in_stock"}
}

def get_inventory(product_id: str, function_name: str = None) -> str:
    """Returns mock inventory data"""
    if product_id in MOCK_INVENTORY:
        return json.dumps(MOCK_INVENTORY[product_id])
    return json.dumps({"error": "Product not found"})
```

**Update agent to use mock:**
```python
# In pet_store_agent_full_ld.py
if os.environ.get('USE_MOCK_DATA') == 'true':
    from mock_inventory import get_inventory
else:
    from inventory_management import get_inventory
```

#### Option 4: AWS Knowledge Bases (Competition Environment)
The competition provides pre-configured Lambda functions:

**Pattern:**
```
team-PetStoreInventoryManagementFunction-<random>
team-PetStoreUserManagementFunction-<random>
```

**Update LaunchDarkly:**
```json
{
  "lambda_inventory_function": "team-PetStoreInventoryManagementFunction-xyz123",
  "lambda_user_function": "team-PetStoreUserManagementFunction-abc789"
}
```

#### Option 5: API Gateway + External Service
Call external APIs instead of Lambda:

**Update `inventory_management.py`:**
```python
import requests

def get_inventory(product_id: str, function_name: str = None) -> str:
    """Call external inventory API"""
    api_url = os.environ.get('INVENTORY_API_URL')
    response = requests.get(f"{api_url}/inventory/{product_id}")
    return response.text
```

### Lambda Function Configuration in LaunchDarkly

All Lambda function names are configured via **LaunchDarkly custom parameters** - no code changes required:

```json
{
  "lambda_inventory_function": "PetStoreInventoryManagement",
  "lambda_user_function": "PetStoreUserManagement",
  "retrieval_backend": "llamaindex",
  "retrieval_num_results": 8
}
```

**Benefits:**
- ✅ Swap implementations without redeploying container
- ✅ A/B test different backends (mock vs production)
- ✅ Point to different environments (dev/staging/prod)
- ✅ Disable features by removing function name

### Agent Decision Flow

1. **Parse Input:** Extract user ID, email, product requests
2. **Parallel Execution:**
   - Check user status (subscribed vs guest)
   - Query product information
3. **Inventory Check:** Verify stock availability
4. **Business Rules:** Apply discounts, shipping costs
5. **JSON Response:** Structured output with all details

---

## 🧪 Testing

### Local Testing

```bash
cd agent/pet_store_agent
export AWS_PROFILE=bedrock-demo
export AWS_DEFAULT_REGION=us-east-1
python pet_store_agent_full_ld.py
```

The main agent file includes 8 built-in test scenarios covering:
- Basic pricing queries
- Subscription customer orders with pet care advice
- Security/injection attempts
- Non-cat/dog pet rejection (parrots, reptiles)
- Bundle discounts and bulk orders
- Free shipping thresholds
- Unavailable product handling
- Inventory checks

### Test Deployed Agent (Interactive CLI)

```bash
cd agent
python test_deployment.py
```

**Interactive Mode:**
- Select 1-8 to run sample prompts
- Type `c` for custom prompt
- Type `l` to list all prompts
- Type `s` to check runtime status
- Type `q` to quit

**Quick Test:**
```bash
python test_deployment.py quick
```

**Single Prompt:**
```bash
python test_deployment.py "What is the price of Doggy Delights?"
```

**Batch Mode:**
```bash
python test_deployment.py batch
# Or with custom prompts file:
python test_deployment.py batch prompts.txt
```

### Remote Testing (AgentCore via AWS CLI)

```bash
export AWS_PROFILE=bedrock-demo

aws bedrock-agentcore invoke-agent-runtime \
  --agent-runtime-arn "arn:aws:bedrock-agentcore:us-east-1:<account>:runtime/<id>" \
  --qualifier DEFAULT \
  --content-type application/json \
  --payload '{"prompt":"A new user is asking about the price of Doggy Delights?"}' \
  --region us-east-1 \
  response.json

cat response.json
```

---

## 📈 Monitoring

### CloudWatch Logs

View agent execution logs:

```bash
aws logs tail agents/petstore-ld-agent-logs --follow --region us-east-1
```

### LaunchDarkly Dashboard

Monitor AI Config performance:
- Request volume and errors
- Model usage distribution
- Token consumption
- Response times
- A/B test results

### AWS Console

View AgentCore Runtime:
- Status and health checks
- Invocation metrics
- Container logs
- Resource utilization

---

## 🔧 Configuration

### Environment Variables

Set in AgentCore Runtime:

```env
AWS_DEFAULT_REGION=us-east-1
LAUNCHDARKLY_SDK_KEY=sdk-xxxxx
OTEL_PYTHON_DISTRO=aws_distro
OTEL_PYTHON_CONFIGURATOR=aws_configurator
AGENT_OBSERVABILITY_ENABLED=true
```

### LaunchDarkly Custom Parameters

Add these to your AI Config custom parameters for Lambda functions:

```json
{
  "lambda_inventory_function": "PetStoreInventoryManagement",
  "lambda_user_function": "PetStoreUserManagement",
  "retrieval_backend": "llamaindex",
  "retrieval_num_results": 8,
  "llamaindex_storage_dir": "./storage"
}
```

### IAM Permissions

**Required for AgentCore Deployment Role** (used by CodeBuild):

All permissions listed below must be attached to the IAM role used for deployment (e.g., `PetStoreAgentCoreDeploymentRole`).

**Bedrock Access:**
- `bedrock:InvokeModel`
- `bedrock:InvokeModelWithResponseStream`

**CloudWatch Logs:**
- `logs:CreateLogGroup`
- `logs:CreateLogStream`
- `logs:PutLogEvents`

**ECR (Container Registry):**
- `ecr:GetAuthorizationToken`
- `ecr:BatchCheckLayerAvailability`
- `ecr:GetDownloadUrlForLayer`
- `ecr:BatchGetImage`

**S3 (Build Artifacts):**
- `s3:PutObject`
- `s3:GetObject`
- `s3:ListBucket`

**CodeBuild:**
- `codebuild:CreateProject`
- `codebuild:StartBuild`
- `codebuild:BatchGetBuilds`

**AgentCore:**
- `bedrock-agentcore:CreateAgentRuntime`
- `bedrock-agentcore:UpdateAgentRuntime`
- `bedrock-agentcore:GetAgentRuntime`

**IAM Pass Role:**
- `iam:PassRole` (to pass the AgentCore runtime role)

**Quick Fix for Missing Permissions:**

If deployment fails due to CloudWatch Logs permissions, run:

```bash
cd agent
./fix_iam_permissions.sh
```

This script automatically adds the required CloudWatch Logs policy to your deployment role.

---

## 🎯 Competition Strategy

### Multiple Submissions

The LaunchDarkly integration allows you to:

1. Submit your AgentCore Runtime ARN
2. Get competition score
3. **Update model/prompt in LaunchDarkly** (no redeployment!)
4. Submit again with same ARN
5. Optimize iteratively

### Optimization Loop

```
Submit → Score → Analyze Failures → Update LD Config → Retest → Submit
```

No need to rebuild or redeploy the container!

### A/B Testing

Run experiments to find optimal configuration:

- **Model Selection:** Balance cost vs quality
- **Temperature:** Control creativity vs consistency
- **Prompt Engineering:** Iterate on system prompt
- **Targeting Rules:** Different configs for different scenarios

---

## 🐛 Troubleshooting

### Agent Not Responding

Check runtime status:
```bash
aws bedrock-agentcore-control get-agent-runtime \
  --agent-runtime-id <runtime-id> \
  --region us-east-1
```

### LaunchDarkly Connection Failed

1. Verify SDK key in environment variables
2. Check CloudWatch logs for initialization errors
3. Ensure network mode is PUBLIC in runtime config

### Product Not Found Errors

This is expected behavior when:
- Product database not configured
- Product name spelling doesn't match inventory
- Knowledge bases not attached

Configure product data in:
- AWS Knowledge Bases, OR
- Local data files in `agent/pet_store_agent/data/`

### Build Failures

- Ensure Docker daemon is running
- Check platform: Must be `linux/arm64` for AgentCore
- Verify ECR repository exists
- Check AWS credentials are valid

---

## 📚 Additional Resources

### Documentation

- **Test Validation Report:** `TEST_VALIDATION_REPORT.md`
- **Repository Changes:** `CHANGES_2026-01-12.md`
- **LaunchDarkly Integration Guide:** `clash_documents/LAUNCHDARKLY.md`

### AWS References

- [AWS Bedrock AgentCore Docs](https://docs.aws.amazon.com/bedrock-agentcore/)
- [AWS Bedrock Models](https://docs.aws.amazon.com/bedrock/latest/userguide/models-supported.html)
- [Amazon ECR User Guide](https://docs.aws.amazon.com/AmazonECR/latest/userguide/)

### LaunchDarkly References

- [LaunchDarkly AI Configs](https://docs.launchdarkly.com/home/ai-configs)
- [Python Server SDK](https://docs.launchdarkly.com/sdk/server-side/python)
- [AI SDK for LangChain](https://github.com/launchdarkly/python-server-sdk-ai/tree/main/packages/ai-providers/server-ai-langchain)

### LangGraph Resources

- [LangGraph Documentation](https://langchain-ai.github.io/langgraph/)
- [ReAct Pattern](https://langchain-ai.github.io/langgraph/concepts/agentic_concepts/#react-implementation)
- [Tool Calling](https://langchain-ai.github.io/langgraph/concepts/tool_calling/)

---

## 📝 License

This project is for the AWS Clash competition. Please refer to competition terms and conditions.

---

**Built with LaunchDarkly, LangGraph, and AWS Bedrock**
