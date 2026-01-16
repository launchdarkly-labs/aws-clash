# LaunchDarkly Custom Parameters Guide

## ✅ All Custom Parameters Now Being Used

After updating the code, **ALL** custom parameters are now properly utilized.

## MCP Server Configuration Format

When creating AI Configs via the MCP server, use this format:

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
    "modelConfigKey": "Bedrock.amazon.nova-pro-v1:0",
    "instructions": "<full prompt>",
    "tools": [
      {"key": "retrieve_product_info", "version": 1},
      {"key": "retrieve_pet_care", "version": 1},
      {"key": "get_inventory", "version": 1},
      {"key": "get_user_by_id", "version": 1},
      {"key": "get_user_by_email", "version": 1}
    ],
    "customParameters": {
      // === AWS Configuration ===
      "aws_region": "us-west-2",                    // ✅ Used by all tools and LLM

      // === Model Parameters ===
      "temperature": 0.7,                           // ✅ Model temperature
      "max_tokens": 4096,                           // ✅ Max output tokens

      // === Lambda Configuration ===
      "use_real_lambda": true,                      // ✅ Switch between real Lambda vs mock data
      "lambda_inventory_function": "team-PetStoreInventoryManagementFunction-XXX",  // ✅ Inventory Lambda
      "lambda_user_function": "team-PetStoreUserManagementFunction-XXX",            // ✅ User Lambda

      // === LlamaIndex RAG Configuration ===
      "llamaindex_storage_dir": "./storage",                        // ✅ Product catalog vector store path
      "llamaindex_petcare_storage_dir": "./storage_petcare",        // ✅ Pet care vector store path (optional)
      "llamaindex_similarity_top_k": 5                              // ✅ Number of similar docs to retrieve
    }
  }
}
```

### Bedrock Knowledge Bases Version

```json
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
```

## How Each Parameter is Used

### AWS Configuration
**File:** `pet_store_agent_full_ld.py`
- **`aws_region`** (lines 177, 236)
  - Passed to all tool builders
  - Used for Bedrock client initialization
  - Used for Lambda client initialization
  - Default: `"us-east-1"` or `AWS_DEFAULT_REGION` env var

### Lambda Tool Configuration
**File:** `tool_registry.py`
- **`use_real_lambda`** (lines 184-186, 333-335, 419-421)
  - `true` = Calls real AWS Lambda functions
  - `false` = Uses mock data for local testing
  - Default: `false`
  
- **`lambda_inventory_function`** (lines 189-192)
  - Lambda function name for inventory operations
  - Used by: `get_inventory` tool
  - Fallback: `INVENTORY_LAMBDA` env var or `"team-PetStoreInventoryManagementFunction"`
  
- **`lambda_user_function`** (lines 338-341, 424-427)
  - Lambda function name for user management
  - Used by: `get_user_by_email`, `get_user_by_id` tools
  - Fallback: `USER_LAMBDA` env var or `"team-PetStoreUserManagementFunction"`

### LlamaIndex RAG Configuration
**File:** `tool_registry.py`
- **`llamaindex_storage_dir`** (lines 21, 42, 102, 127)
  - Path to main vector store (product catalog)
  - Used by: `retrieve_product_info`, `retrieve_pet_care` (as fallback)
  - Default: `"./storage"`
  - **NOW CONFIGURABLE** via LaunchDarkly
  
- **`llamaindex_petcare_storage_dir`** (lines 103, 126)
  - Path to pet care-specific vector store
  - Used by: `retrieve_pet_care` (if exists, otherwise uses main storage)
  - Default: `"./storage_petcare"`
  - **NEW PARAMETER** - now configurable
  
- **`llamaindex_similarity_top_k`** (lines 22, 69, 104, 162)
  - Number of similar documents to retrieve from vector store
  - Used by: `retrieve_product_info`, `retrieve_pet_care`
  - Default: `5`
  - **NOW CONFIGURABLE** via LaunchDarkly (was hardcoded to 3)

### LLM Configuration
**File:** `pet_store_agent_full_ld.py`
- **`temperature`** (line 233)
  - Controls randomness of model output (0.0 = deterministic, 1.0 = creative)
  - Default: `0.7`
  - Can be set in `custom` or `parameters` (custom takes precedence)
  
- **`max_tokens`** (line 234)
  - Maximum tokens in model output
  - Default: `4096`
  - Can be set in `custom` or `parameters` (custom takes precedence)

## Tool-Specific Configuration

### RAG Tools (retrieve_product_info, retrieve_pet_care)
These tools read:
- `aws_region` → for Bedrock embeddings client
- `llamaindex_storage_dir` → main vector store path
- `llamaindex_petcare_storage_dir` → pet care vector store path
- `llamaindex_similarity_top_k` → number of results to retrieve

### Lambda Tools (get_inventory, get_user_by_id, get_user_by_email)
These tools read:
- `aws_region` → for Lambda client
- `use_real_lambda` → switch between real/mock
- `lambda_inventory_function` → for get_inventory
- `lambda_user_function` → for get_user_by_id, get_user_by_email

## Example Configurations

### Local Testing (Mock Data)
```json
"custom": {
  "aws_region": "us-west-2",
  "use_real_lambda": false,
  "llamaindex_storage_dir": "./storage",
  "llamaindex_similarity_top_k": 5
}
```

### Production (Real Lambda)
```json
"custom": {
  "aws_region": "us-west-2",
  "use_real_lambda": true,
  "lambda_inventory_function": "team-PetStoreInventoryManagementFunction-ABC123",
  "lambda_user_function": "team-PetStoreUserManagementFunction-DEF456",
  "llamaindex_storage_dir": "./storage",
  "llamaindex_similarity_top_k": 5
}
```

### High Precision RAG
```json
"custom": {
  "aws_region": "us-west-2",
  "llamaindex_storage_dir": "./storage",
  "llamaindex_similarity_top_k": 10,  // More context
  "temperature": 0.3,                   // More deterministic
  "max_tokens": 2048
}
```

## Summary of Changes

✅ **Now using** `llamaindex_storage_dir` (was hardcoded to `./storage`)
✅ **Now using** `llamaindex_similarity_top_k` (was hardcoded to `3`)
✅ **Added new** `llamaindex_petcare_storage_dir` parameter for separate pet care index

All parameters are now dynamically configurable through LaunchDarkly AI Config! 🎉
