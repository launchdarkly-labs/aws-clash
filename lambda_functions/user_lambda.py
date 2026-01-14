"""
AWS Lambda function for Pet Store User Management
This function handles user queries and returns customer information
"""
import json
from datetime import datetime

# Mock user database
USERS_DB = {
    "usr_001": {
        "id": "usr_001",
        "name": "John Doe",
        "email": "john.doe@virtualpetstore.com",
        "subscription_status": "active",
        "subscription_end_date": "2027-01-12T00:00:00Z",
        "transactions": [
            {
                "id": "txn_001",
                "amount": 29.99,
                "date": "2025-12-12T10:00:00Z",
                "description": "Monthly subscription"
            },
            {
                "id": "txn_002",
                "amount": 54.99,
                "date": "2025-11-15T14:30:00Z",
                "description": "Doggy Delights purchase"
            }
        ]
    },
    "usr_002": {
        "id": "usr_002",
        "name": "Jane Smith",
        "email": "jane.smith@example.com",
        "subscription_status": "active",
        "subscription_end_date": "2026-06-30T00:00:00Z",
        "transactions": [
            {
                "id": "txn_003",
                "amount": 29.99,
                "date": "2025-12-01T10:00:00Z",
                "description": "Monthly subscription"
            }
        ]
    },
    "usr_003": {
        "id": "usr_003",
        "name": "Bob Johnson",
        "email": "bob.johnson@example.com",
        "subscription_status": "expired",
        "subscription_end_date": "2025-06-30T00:00:00Z",
        "transactions": [
            {
                "id": "txn_004",
                "amount": 27.99,
                "date": "2025-05-15T10:00:00Z",
                "description": "Product purchase"
            }
        ]
    }
}

# Email to user ID mapping
EMAIL_TO_USER = {
    "john.doe@virtualpetstore.com": "usr_001",
    "jane.smith@example.com": "usr_002",
    "jane1988@someemaildomain.com": "usr_002",  # Alternate email for usr_002
    "bob.johnson@example.com": "usr_003",
    "no-reply@someemaildomain.com": None  # Guest user
}


def lambda_handler(event, context):
    """
    Lambda handler for user management

    Expected input formats:
    1. getUserById:
    {
        "function": "getUserById",
        "parameters": [
            {
                "name": "user_id",
                "value": "usr_001"
            }
        ]
    }

    2. getUserByEmail:
    {
        "function": "getUserByEmail",
        "parameters": [
            {
                "name": "user_email",
                "value": "john.doe@virtualpetstore.com"
            }
        ]
    }
    """
    try:
        print(f"Received event: {json.dumps(event)}")

        # Extract function name
        function_name = event.get("function")

        if function_name not in ["getUserById", "getUserByEmail"]:
            return {
                "statusCode": 400,
                "body": json.dumps({"error": f"Unknown function: {function_name}"})
            }

        # Extract parameters
        parameters = event.get("parameters", [])

        if function_name == "getUserById":
            user_id = None
            for param in parameters:
                if param.get("name") == "user_id":
                    user_id = param.get("value")
                    break

            if not user_id:
                return {
                    "statusCode": 400,
                    "body": json.dumps({"error": "user_id parameter required"})
                }

            # Look up user by ID
            if user_id in USERS_DB:
                response_body = USERS_DB[user_id]
            else:
                response_body = {
                    "error": f"User {user_id} not found",
                    "id": user_id
                }

        elif function_name == "getUserByEmail":
            user_email = None
            for param in parameters:
                if param.get("name") == "user_email":
                    user_email = param.get("value")
                    break

            if not user_email:
                return {
                    "statusCode": 400,
                    "body": json.dumps({"error": "user_email parameter required"})
                }

            # Look up user by email
            user_id = EMAIL_TO_USER.get(user_email)
            if user_id and user_id in USERS_DB:
                response_body = USERS_DB[user_id]
            else:
                response_body = {
                    "error": f"User with email {user_email} not found",
                    "email": user_email
                }

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
