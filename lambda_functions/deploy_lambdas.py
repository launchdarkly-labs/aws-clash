#!/usr/bin/env python3
"""
Deploy Pet Store Lambda Functions to AWS
Creates the inventory and user management Lambda functions
"""
import boto3
import json
import zipfile
import os
import time
from pathlib import Path

def create_lambda_zip(source_file, zip_file):
    """Create a deployment package for Lambda"""
    with zipfile.ZipFile(zip_file, 'w', zipfile.ZIP_DEFLATED) as zipf:
        zipf.write(source_file, os.path.basename(source_file))
    print(f"✅ Created deployment package: {zip_file}")

def create_lambda_role(iam_client, role_name):
    """Create IAM role for Lambda execution"""

    trust_policy = {
        "Version": "2012-10-17",
        "Statement": [
            {
                "Effect": "Allow",
                "Principal": {
                    "Service": "lambda.amazonaws.com"
                },
                "Action": "sts:AssumeRole"
            }
        ]
    }

    try:
        response = iam_client.create_role(
            RoleName=role_name,
            AssumeRolePolicyDocument=json.dumps(trust_policy),
            Description='Execution role for Pet Store Lambda functions'
        )
        role_arn = response['Role']['Arn']
        print(f"✅ Created IAM role: {role_name}")

        # Attach basic Lambda execution policy
        iam_client.attach_role_policy(
            RoleName=role_name,
            PolicyArn='arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole'
        )
        print(f"✅ Attached execution policy to role")

        # Wait for role to be available
        print("⏳ Waiting for IAM role to propagate (10 seconds)...")
        time.sleep(10)

        return role_arn

    except iam_client.exceptions.EntityAlreadyExistsException:
        print(f"ℹ️  IAM role {role_name} already exists, using existing role")
        response = iam_client.get_role(RoleName=role_name)
        return response['Role']['Arn']

def deploy_lambda_function(lambda_client, function_name, zip_file, handler, role_arn, description):
    """Deploy or update a Lambda function"""

    with open(zip_file, 'rb') as f:
        zip_content = f.read()

    try:
        # Try to create new function
        response = lambda_client.create_function(
            FunctionName=function_name,
            Runtime='python3.11',
            Role=role_arn,
            Handler=handler,
            Code={'ZipFile': zip_content},
            Description=description,
            Timeout=30,
            MemorySize=128,
            Publish=True
        )
        print(f"✅ Created Lambda function: {function_name}")
        return response['FunctionArn']

    except lambda_client.exceptions.ResourceConflictException:
        # Function exists, update it
        print(f"ℹ️  Function {function_name} exists, updating code...")
        response = lambda_client.update_function_code(
            FunctionName=function_name,
            ZipFile=zip_content,
            Publish=True
        )
        print(f"✅ Updated Lambda function: {function_name}")
        return response['FunctionArn']

def main():
    """Main deployment function"""

    print("\n" + "="*80)
    print("🚀 DEPLOYING PET STORE LAMBDA FUNCTIONS")
    print("="*80 + "\n")

    # Get AWS profile from environment
    aws_profile = os.environ.get('AWS_PROFILE', 'bedrock-demo')
    aws_region = os.environ.get('AWS_DEFAULT_REGION', 'us-east-1')

    print(f"📍 AWS Profile: {aws_profile}")
    print(f"📍 AWS Region: {aws_region}\n")

    # Create boto3 session
    session = boto3.Session(profile_name=aws_profile, region_name=aws_region)
    lambda_client = session.client('lambda')
    iam_client = session.client('iam')

    # Get script directory
    script_dir = Path(__file__).parent

    # Step 1: Create IAM role
    print("\n📋 Step 1: Creating IAM Role")
    print("-" * 80)
    role_name = 'PetStoreLambdaExecutionRole'
    role_arn = create_lambda_role(iam_client, role_name)

    # Step 2: Create deployment packages
    print("\n📦 Step 2: Creating Deployment Packages")
    print("-" * 80)

    inventory_zip = script_dir / 'inventory_lambda.zip'
    user_zip = script_dir / 'user_lambda.zip'

    create_lambda_zip(script_dir / 'inventory_lambda.py', inventory_zip)
    create_lambda_zip(script_dir / 'user_lambda.py', user_zip)

    # Step 3: Deploy Lambda functions
    print("\n🚀 Step 3: Deploying Lambda Functions")
    print("-" * 80)

    inventory_function_name = 'PetStoreInventoryManagement'
    user_function_name = 'PetStoreUserManagement'

    inventory_arn = deploy_lambda_function(
        lambda_client,
        inventory_function_name,
        inventory_zip,
        'inventory_lambda.lambda_handler',
        role_arn,
        'Pet Store inventory management function'
    )

    user_arn = deploy_lambda_function(
        lambda_client,
        user_function_name,
        user_zip,
        'user_lambda.lambda_handler',
        role_arn,
        'Pet Store user management function'
    )

    # Clean up zip files
    inventory_zip.unlink()
    user_zip.unlink()
    print("\n🧹 Cleaned up deployment packages")

    # Print summary
    print("\n" + "="*80)
    print("✅ DEPLOYMENT COMPLETE!")
    print("="*80)
    print(f"\n📋 Add these to your LaunchDarkly custom params:\n")
    print(json.dumps({
        "lambda_inventory_function": inventory_function_name,
        "lambda_user_function": user_function_name
    }, indent=2))
    print(f"\n🔗 Function ARNs:")
    print(f"   Inventory: {inventory_arn}")
    print(f"   User:      {user_arn}")
    print("\n" + "="*80 + "\n")

if __name__ == "__main__":
    main()
