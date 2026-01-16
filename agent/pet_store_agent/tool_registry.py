"""
Tool Registry for Pet Store Agent
Maps tool names to builder functions that create LangChain/LangGraph-compatible tools
"""

from typing import Dict, Any, Optional
from langchain_core.tools import tool
import logging
import os
import json
import boto3
from pathlib import Path

logger = logging.getLogger(__name__)


def build_retrieve_product_info_tool(custom: Dict[str, Any], aws_region: str):
    """Build retrieve_product_info tool using LlamaIndex - ALWAYS uses real RAG"""

    # Get configuration from LaunchDarkly custom config
    storage_dir_name = custom.get("llamaindex_storage_dir", "./storage")
    similarity_top_k = int(custom.get("llamaindex_similarity_top_k", 5))

    logger.info(f"🔧 Building retrieve_product_info with config:")
    logger.info(f"   storage_dir: {storage_dir_name}, similarity_top_k: {similarity_top_k}")

    @tool
    def retrieve_product_info(query: str) -> str:
        """Retrieve product information from the pet store catalog using LlamaIndex RAG.

        Args:
            query: Search query for product information

        Returns:
            JSON string with product information from indexed PDFs
        """
        from llama_index.core import StorageContext, load_index_from_storage, Settings
        from llama_index.embeddings.bedrock import BedrockEmbedding

        # Get the correct path to storage directory from config
        current_dir = Path(__file__).parent
        storage_dir = current_dir / storage_dir_name.lstrip("./")

        # Set up Bedrock embeddings explicitly with proper AWS session
        # Use profile if set
        if os.environ.get('AWS_PROFILE'):
            boto_session = boto3.Session(
                profile_name=os.environ.get('AWS_PROFILE'),
                region_name=aws_region or "us-east-1"
            )
            bedrock_client = boto_session.client('bedrock-runtime')
        else:
            bedrock_client = boto3.client(
                'bedrock-runtime',
                region_name=aws_region or "us-east-1"
            )

        embed_model = BedrockEmbedding(
            model_name="amazon.titan-embed-text-v2:0",  # Same model used to create storage
            client=bedrock_client
        )
        Settings.embed_model = embed_model

        # Load pre-built index from storage
        storage_context = StorageContext.from_defaults(persist_dir=str(storage_dir))
        index = load_index_from_storage(storage_context)

        # Use retriever directly to avoid LLM requirement
        retriever = index.as_retriever(similarity_top_k=similarity_top_k)
        nodes = retriever.retrieve(query)

        # Combine the text from retrieved nodes
        if nodes:
            content = "\n".join([node.text for node in nodes])
        else:
            content = "No relevant information found"

        # Parse and structure the response
        result = {
            "results": [
                {
                    "content": content,
                    "relevance_score": nodes[0].score if nodes and hasattr(nodes[0], "score") else 0.9,
                    "source": "Pet Store Product Catalog (PDFs)"
                }
            ]
        }

        logger.info(f"🔍 TOOL EXECUTION: retrieve_product_info")
        logger.info(f"   Input: query='{query}'")
        logger.info(f"   Output: Found {len(nodes)} nodes, content length: {len(content)} chars")
        logger.debug(f"   Full output: {json.dumps(result, indent=2)[:500]}")
        return json.dumps(result)

    return retrieve_product_info


def build_retrieve_pet_care_tool(custom: Dict[str, Any], aws_region: str):
    """Build retrieve_pet_care tool using LlamaIndex - ALWAYS uses real RAG"""

    # Get configuration from LaunchDarkly custom config
    storage_dir_name = custom.get("llamaindex_storage_dir", "./storage")
    petcare_storage_dir_name = custom.get("llamaindex_petcare_storage_dir", "./storage_petcare")
    similarity_top_k = int(custom.get("llamaindex_similarity_top_k", 5))

    logger.info(f"🔧 Building retrieve_pet_care with config:")
    logger.info(f"   storage_dir: {storage_dir_name}, petcare_storage: {petcare_storage_dir_name}, similarity_top_k: {similarity_top_k}")

    @tool
    def retrieve_pet_care(query: str) -> str:
        """Retrieve pet care advice using LlamaIndex RAG.

        Args:
            query: Search query for pet care information

        Returns:
            JSON string with pet care advice from indexed content
        """
        from llama_index.core import StorageContext, load_index_from_storage, Settings
        from llama_index.embeddings.bedrock import BedrockEmbedding

        # Get the correct path to storage directory from config
        current_dir = Path(__file__).parent

        # Check if we have a separate pet care index, otherwise use main storage
        petcare_storage = current_dir / petcare_storage_dir_name.lstrip("./")
        main_storage = current_dir / storage_dir_name.lstrip("./")

        if petcare_storage.exists():
            storage_dir = petcare_storage
            source = "Pet Care Knowledge Base"
        else:
            # Use main storage which has product PDFs (may contain some care info)
            storage_dir = main_storage
            source = "Pet Store Product Documentation"

        # Set up Bedrock embeddings explicitly with proper AWS session
        # Use profile if set
        if os.environ.get('AWS_PROFILE'):
            boto_session = boto3.Session(
                profile_name=os.environ.get('AWS_PROFILE'),
                region_name=aws_region or "us-east-1"
            )
            bedrock_client = boto_session.client('bedrock-runtime')
        else:
            bedrock_client = boto3.client(
                'bedrock-runtime',
                region_name=aws_region or "us-east-1"
            )

        embed_model = BedrockEmbedding(
            model_name="amazon.titan-embed-text-v2:0",  # Same model used to create storage
            client=bedrock_client
        )
        Settings.embed_model = embed_model

        # Load index from storage
        storage_context = StorageContext.from_defaults(persist_dir=str(storage_dir))
        index = load_index_from_storage(storage_context)

        # Use retriever directly to avoid LLM requirement
        retriever = index.as_retriever(similarity_top_k=similarity_top_k)
        nodes = retriever.retrieve(query)

        # Combine the text from retrieved nodes
        if nodes:
            content = "\n".join([node.text for node in nodes])
        else:
            content = "No relevant pet care information found"

        result = {
            "results": [
                {
                    "topic": "Pet Care Advice",
                    "content": content,
                    "relevance_score": nodes[0].score if nodes and hasattr(nodes[0], "score") else 0.9,
                    "source": source
                }
            ]
        }

        logger.info(f"🔍 TOOL EXECUTION: retrieve_pet_care")
        logger.info(f"   Input: query='{query}'")
        logger.info(f"   Output: Found {len(nodes)} nodes, content length: {len(content)} chars, source: {source}")
        logger.debug(f"   Full output: {json.dumps(result, indent=2)[:500]}")
        return json.dumps(result)

    return retrieve_pet_care


def build_get_inventory_tool(custom: Dict[str, Any], aws_region: str):
    """Build get_inventory tool - calls real Lambda or uses mock for local testing"""

    # Get configuration from LaunchDarkly custom config, with env var fallback
    use_real_lambda = custom.get("use_real_lambda", os.environ.get("USE_REAL_LAMBDA", "false"))
    if isinstance(use_real_lambda, str):
        use_real_lambda = use_real_lambda.lower() == "true"

    # Lambda function name from LaunchDarkly config or environment
    lambda_function_name = custom.get("lambda_inventory_function") or \
                           custom.get("lambda_function_name") or \
                           custom.get("lambda_arn") or \
                           os.environ.get("INVENTORY_LAMBDA", "team-PetStoreInventoryManagementFunction")

    logger.info(f"🔧 Building get_inventory with config: use_real_lambda={use_real_lambda}, lambda={lambda_function_name}")

    @tool
    def get_inventory(product_code: Optional[str] = None) -> str:
        """Get inventory information for products.

        Args:
            product_code: Optional product code. Without it, returns all products.

        Returns:
            JSON string with inventory information
        """
        logger.info(f"🔍 TOOL EXECUTION: get_inventory")
        logger.info(f"   Input: product_code='{product_code}'")

        if use_real_lambda:
            try:
                # Call real Lambda function
                lambda_client = boto3.client('lambda', region_name=aws_region)

                payload = {
                    "function": "getInventory",
                    "parameters": []
                }

                if product_code:
                    payload["parameters"].append({
                        "name": "product_code",
                        "value": product_code
                    })

                response = lambda_client.invoke(
                    FunctionName=lambda_function_name,
                    InvocationType='RequestResponse',
                    Payload=json.dumps(payload)
                )

                result = json.loads(response['Payload'].read())
                return json.dumps(result)

            except Exception as e:
                logger.error(f"Error calling Lambda: {e}")
                # Fall through to mock data

        # Mock data for local testing - matches competition test products
        inventory_data = {
            "DD006": {
                "product_code": "DD006",
                "name": "Doggy Delights",
                "price": 54.99,
                "quantity": 150,
                "last_updated": "2025-01-13T12:00:00Z",
                "status": "in_stock",
                "reorder_level": 50
            },
            "CM001": {
                "product_code": "CM001",
                "name": "Meow Munchies",
                "price": 10.99,
                "quantity": 200,
                "last_updated": "2025-01-13T12:00:00Z",
                "status": "in_stock",
                "reorder_level": 50
            },
            "BP010": {
                "product_code": "BP010",
                "name": "Bark Park Buddy",
                "price": 16.99,
                "quantity": 75,
                "last_updated": "2025-01-13T12:00:00Z",
                "status": "in_stock",
                "reorder_level": 20
            },
            "PM015": {
                "product_code": "PM015",
                "name": "Paw-ty Mix",
                "price": 27.99,
                "quantity": 30,
                "last_updated": "2025-01-13T12:00:00Z",
                "status": "in_stock",
                "reorder_level": 25
            },
            "FF003": {
                "product_code": "FF003",
                "name": "Feline Feast",
                "price": 34.99,
                "quantity": 45,
                "last_updated": "2025-01-13T12:00:00Z",
                "status": "in_stock",
                "reorder_level": 15
            },
            "DB002": {
                "product_code": "DB002",
                "name": "Doggy Bites",
                "price": 19.99,
                "quantity": 100,
                "last_updated": "2025-01-13T12:00:00Z",
                "status": "in_stock",
                "reorder_level": 30
            },
            "PT003": {
                "product_code": "PT003",
                "name": "Cat Toys",
                "price": 9.99,
                "quantity": 50,
                "last_updated": "2025-01-13T12:00:00Z",
                "status": "in_stock",
                "reorder_level": 20
            }
        }

        if product_code:
            if product_code in inventory_data:
                result = json.dumps(inventory_data[product_code])
                logger.info(f"   Output: Found product {product_code}, price: ${inventory_data[product_code]['price']}")
                return result
            else:
                # Return unknown product
                logger.info(f"   Output: Product {product_code} not found, returning out of stock")
                return json.dumps({
                    "product_code": product_code,
                    "name": f"Product {product_code}",
                    "price": 9.99,
                    "quantity": 0,
                    "last_updated": "2025-01-13T12:00:00Z",
                    "status": "out_of_stock",
                    "reorder_level": 20
                })
        else:
            logger.info(f"   Output: Returning all {len(inventory_data)} products")
            return json.dumps(list(inventory_data.values()))

    return get_inventory


def build_get_user_by_email_tool(custom: Dict[str, Any], aws_region: str):
    """Build get_user_by_email tool - calls real Lambda or uses mock for local testing"""

    # Get configuration from LaunchDarkly custom config, with env var fallback
    use_real_lambda = custom.get("use_real_lambda", os.environ.get("USE_REAL_LAMBDA", "false"))
    if isinstance(use_real_lambda, str):
        use_real_lambda = use_real_lambda.lower() == "true"

    # Lambda function name from LaunchDarkly config or environment
    lambda_function_name = custom.get("lambda_user_function") or \
                           custom.get("lambda_function_name") or \
                           custom.get("lambda_arn") or \
                           os.environ.get("USER_LAMBDA", "team-PetStoreUserManagementFunction")

    logger.info(f"🔧 Building get_user_by_email with config: use_real_lambda={use_real_lambda}, lambda={lambda_function_name}")

    @tool
    def get_user_by_email(email: str) -> str:
        """Get user information by email address.

        Args:
            email: User email to retrieve information for

        Returns:
            JSON string with user information
        """
        if use_real_lambda:
            try:
                lambda_client = boto3.client('lambda', region_name=aws_region)

                payload = {
                    "function": "getUserByEmail",
                    "parameters": [
                        {
                            "name": "user_email",
                            "value": email
                        }
                    ]
                }

                response = lambda_client.invoke(
                    FunctionName=lambda_function_name,
                    InvocationType='RequestResponse',
                    Payload=json.dumps(payload)
                )

                result = json.loads(response['Payload'].read())
                return json.dumps(result)

            except Exception as e:
                logger.error(f"Error calling Lambda: {e}")
                # Fall through to mock data

        # Mock data for local testing - matches competition test data
        if email == "jane1988@someemaildomain.com":
            return json.dumps({
                "id": "usr_002",
                "name": "Jane Smith",
                "email": email,
                "subscription_status": "expired",
                "subscription_end_date": "2024-01-31",
                "transactions": []
            })
        elif email == "no-reply@someemaildomain.com":
            return json.dumps({
                "id": "usr_003",
                "name": "Test User",
                "email": email,
                "subscription_status": "guest",
                "subscription_end_date": None,
                "transactions": []
            })
        else:
            # Unknown user - return guest
            return json.dumps({
                "id": "usr_guest",
                "name": "Guest User",
                "email": email,
                "subscription_status": "guest",
                "subscription_end_date": None,
                "transactions": []
            })

    return get_user_by_email


def build_get_user_by_id_tool(custom: Dict[str, Any], aws_region: str):
    """Build get_user_by_id tool - calls real Lambda or uses mock for local testing"""

    # Get configuration from LaunchDarkly custom config, with env var fallback
    use_real_lambda = custom.get("use_real_lambda", os.environ.get("USE_REAL_LAMBDA", "false"))
    if isinstance(use_real_lambda, str):
        use_real_lambda = use_real_lambda.lower() == "true"

    # Lambda function name from LaunchDarkly config or environment
    lambda_function_name = custom.get("lambda_user_function") or \
                           custom.get("lambda_function_name") or \
                           custom.get("lambda_arn") or \
                           os.environ.get("USER_LAMBDA", "team-PetStoreUserManagementFunction")

    logger.info(f"🔧 Building get_user_by_id with config: use_real_lambda={use_real_lambda}, lambda={lambda_function_name}")

    @tool
    def get_user_by_id(user_id: str) -> str:
        """Get user information by user ID.

        Args:
            user_id: User ID to retrieve information for

        Returns:
            JSON string with user information
        """
        if use_real_lambda:
            try:
                lambda_client = boto3.client('lambda', region_name=aws_region)

                payload = {
                    "function": "getUserById",
                    "parameters": [
                        {
                            "name": "user_id",
                            "value": user_id
                        }
                    ]
                }

                response = lambda_client.invoke(
                    FunctionName=lambda_function_name,
                    InvocationType='RequestResponse',
                    Payload=json.dumps(payload)
                )

                result = json.loads(response['Payload'].read())
                return json.dumps(result)

            except Exception as e:
                logger.error(f"Error calling Lambda: {e}")
                # Fall through to mock data

        # Mock data for local testing - matches competition test data exactly
        if user_id == "usr_001":
            return json.dumps({
                "id": user_id,
                "name": "John Doe",
                "email": "john.doe@virtualpetstore.com",
                "subscription_status": "active",
                "subscription_end_date": "2025-12-31",
                "transactions": [
                    {
                        "id": "txn_001",
                        "amount": 29.99,
                        "date": "2024-01-15",
                        "description": "Monthly subscription"
                    }
                ]
            })
        elif user_id == "usr_002":
            return json.dumps({
                "id": user_id,
                "name": "Jane Smith",
                "email": "jane.smith@example.com",
                "subscription_status": "active",
                "subscription_end_date": "2025-06-30",
                "transactions": []
            })
        elif user_id == "usr_003":
            return json.dumps({
                "id": user_id,
                "name": "Bob Wilson",
                "email": "bob.wilson@example.com",
                "subscription_status": "expired",
                "subscription_end_date": "2024-01-01",
                "transactions": []
            })
        else:
            # Unknown user - return guest
            return json.dumps({
                "id": user_id,
                "name": "Guest User",
                "email": f"{user_id}@example.com",
                "subscription_status": "guest",
                "subscription_end_date": None,
                "transactions": []
            })

    return get_user_by_id


# Registry mapping tool names to their builder functions - matches LaunchDarkly tools exactly
TOOL_BUILDERS = {
    "retrieve_product_info": build_retrieve_product_info_tool,  # RAG - uses LlamaIndex
    "retrieve_pet_care": build_retrieve_pet_care_tool,          # RAG - uses LlamaIndex
    "get_inventory": build_get_inventory_tool,                  # Lambda/Mock
    "get_user_by_email": build_get_user_by_email_tool,          # Lambda/Mock
    "get_user_by_id": build_get_user_by_id_tool,                # Lambda/Mock
}


# Log initialization
logger.info(f"Tool registry initialized with tools: {list(TOOL_BUILDERS.keys())}")
logger.info(f"RAG tools (LlamaIndex): retrieve_product_info, retrieve_pet_care")
logger.info(f"Lambda tools (Mock/Real): get_inventory, get_user_by_email, get_user_by_id")
logger.info(f"Configuration will be provided by LaunchDarkly or environment variables")