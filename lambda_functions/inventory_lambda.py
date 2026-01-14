"""
AWS Lambda function for Pet Store Inventory Management
This function handles inventory queries and returns product stock information
"""
import json
from datetime import datetime

# Mock inventory database
INVENTORY_DB = {
    "DD006": {
        "product_code": "DD006",
        "name": "Doggy Delights",
        "quantity": 200,
        "last_updated": "2026-01-12T10:00:00Z",
        "status": "in_stock",
        "reorder_level": 50
    },
    "BP010": {
        "product_code": "BP010",
        "name": "Bark Park Buddy Water Bottles",
        "quantity": 150,
        "last_updated": "2026-01-12T10:00:00Z",
        "status": "in_stock",
        "reorder_level": 30
    },
    "KC015": {
        "product_code": "KC015",
        "name": "Kitty Comfort Cat Tower",
        "quantity": 45,
        "last_updated": "2026-01-12T10:00:00Z",
        "status": "low_stock",
        "reorder_level": 40
    },
    "PP020": {
        "product_code": "PP020",
        "name": "Purrfect Playtime Cat Toys Set",
        "quantity": 180,
        "last_updated": "2026-01-12T10:00:00Z",
        "status": "in_stock",
        "reorder_level": 50
    },
    "CM001": {
        "product_code": "CM001",
        "name": "Meow Munchies",
        "quantity": 150,
        "last_updated": "2026-01-12T10:00:00Z",
        "status": "in_stock",
        "reorder_level": 50
    },
    "PM015": {
        "product_code": "PM015",
        "name": "Paw-ty Mix",
        "quantity": 85,
        "last_updated": "2026-01-12T10:00:00Z",
        "status": "in_stock",
        "reorder_level": 80
    },
    "DB002": {
        "product_code": "DB002",
        "name": "Doggy Bites",
        "quantity": 120,
        "last_updated": "2026-01-12T10:00:00Z",
        "status": "in_stock",
        "reorder_level": 40
    },
    "PT003": {
        "product_code": "PT003",
        "name": "Premium Treats",
        "quantity": 95,
        "last_updated": "2026-01-12T10:00:00Z",
        "status": "in_stock",
        "reorder_level": 30
    }
}


def lambda_handler(event, context):
    """
    Lambda handler for inventory management

    Expected input format:
    {
        "function": "getInventory",
        "parameters": [
            {
                "name": "product_code",
                "value": "CM001"
            }
        ]
    }
    """
    try:
        print(f"Received event: {json.dumps(event)}")

        # Extract function name
        function_name = event.get("function")

        if function_name != "getInventory":
            return {
                "statusCode": 400,
                "body": json.dumps({"error": f"Unknown function: {function_name}"})
            }

        # Extract parameters
        parameters = event.get("parameters", [])
        product_code = None

        for param in parameters:
            if param.get("name") == "product_code":
                product_code = param.get("value")
                break

        # Build response based on whether product_code was provided
        if product_code:
            # Return specific product
            if product_code in INVENTORY_DB:
                response_body = INVENTORY_DB[product_code]
            else:
                response_body = {
                    "error": f"Product {product_code} not found",
                    "product_code": product_code,
                    "status": "not_found"
                }
        else:
            # Return all products
            response_body = list(INVENTORY_DB.values())

        # Match the expected response structure from Bedrock Agent
        return {
            "response": {
                "functionResponse": {
                    "responseBody": {
                        "TEXT": {
                            "body": json.dumps(response_body)
                        }
                    }
                }
            }
        }

    except Exception as e:
        print(f"Error: {str(e)}")
        return {
            "statusCode": 500,
            "body": json.dumps({"error": str(e)})
        }
