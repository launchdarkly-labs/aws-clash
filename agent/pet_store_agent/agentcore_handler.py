#!/usr/bin/env python3
"""
AgentCore handler without bedrock-agentcore package
Uses a simple HTTP server to handle Agent Core requests
"""
import os
import json
import logging
from http.server import HTTPServer, BaseHTTPRequestHandler
import sys

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    stream=sys.stderr
)
logger = logging.getLogger(__name__)

# Import the actual agent
try:
    from pet_store_agent_full_ld import get_agent
    logger.info("✅ Successfully imported pet_store_agent_full_ld")
except ImportError as e:
    logger.error(f"❌ Failed to import pet_store_agent_full_ld: {e}")
    raise

# Check if LlamaIndex storage exists
if os.path.exists('./storage'):
    logger.info(f"✅ Storage directory found: {os.listdir('./storage')}")
else:
    logger.warning("⚠️ Storage directory not found - RAG tools may not work")

class AgentCoreHandler(BaseHTTPRequestHandler):
    """HTTP handler for Agent Core requests"""

    def do_POST(self):
        """Handle POST requests from Agent Core"""
        try:
            # Read request body
            content_length = int(self.headers['Content-Length'])
            body = self.rfile.read(content_length)
            payload = json.loads(body)

            logger.info(f"Received request: {json.dumps(payload)[:200]}...")

            # Extract prompt
            prompt = payload.get('prompt', 'A new user is asking about the price of Doggy Delights?')

            # Extract user context for LaunchDarkly
            user_context = {
                "user_id": payload.get("user_id", "anonymous"),
                "customer_id": payload.get("customer_id"),
                "request_type": payload.get("request_type", "product_inquiry"),
                "subscription_status": payload.get("subscription_status", "unknown"),
                "query_complexity": payload.get("query_complexity", "medium")
            }

            # Remove None values
            user_context = {k: v for k, v in user_context.items() if v is not None}

            # Get the agent and process request
            logger.info("Processing with LaunchDarkly-enhanced agent...")
            agent = get_agent()
            result = agent.invoke(prompt, user_context)

            logger.info(f"Agent response: {result[:200]}...")

            # Send response
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            self.wfile.write(result.encode())

        except Exception as e:
            logger.error(f"Error handling request: {e}", exc_info=True)

            # Send error response
            error_response = json.dumps({
                "status": "Error",
                "message": f"Agent error: {str(e)}"
            })

            self.send_response(500)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            self.wfile.write(error_response.encode())

    def log_message(self, format, *args):
        """Override to log to our logger instead of stderr"""
        logger.info("%s - %s" % (self.address_string(), format % args))

def main():
    """Start the HTTP server for Agent Core"""
    port = 8080
    server_address = ('0.0.0.0', port)

    logger.info(f"Starting Agent Core handler on port {port}...")
    logger.info(f"LaunchDarkly SDK Key: {os.environ.get('LAUNCHDARKLY_SDK_KEY', 'Not set')[:10]}...")
    logger.info(f"AWS Region: {os.environ.get('AWS_DEFAULT_REGION', 'Not set')}")

    httpd = HTTPServer(server_address, AgentCoreHandler)
    logger.info(f"Server listening on {server_address[0]}:{server_address[1]}")

    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        logger.info("Server stopped by user")
    except Exception as e:
        logger.error(f"Server error: {e}", exc_info=True)
        raise

if __name__ == "__main__":
    main()