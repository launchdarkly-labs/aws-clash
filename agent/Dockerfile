FROM --platform=linux/arm64 public.ecr.aws/docker/library/python:3.12-slim-bookworm@sha256:28cf028e5a544e92dbe11450debd93dd5eb70eaf3179a9e878cfaee426556b3b

WORKDIR /app

# Copy requirements and install dependencies
COPY pet_store_agent/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Additional packages not in requirements.txt
RUN pip install aws-opentelemetry-distro

# Copy agent code and tools
COPY pet_store_agent/*.py ./

# Copy data directory with PDFs for LlamaIndex (source documents)
COPY pet_store_agent/data/ ./data/

# Copy pre-built LlamaIndex storage (vector store)
COPY pet_store_agent/storage/ ./storage/

# Set default AWS region
ENV AWS_DEFAULT_REGION=${AWS_DEFAULT_REGION}

# LaunchDarkly SDK Key (will be set at runtime)
ENV LAUNCHDARKLY_SDK_KEY=${LAUNCHDARKLY_SDK_KEY}

# Set agent resources variables (optional - can be empty if using mock tools)
ENV KNOWLEDGE_BASE_1_ID=${KNOWLEDGE_BASE_1_ID:-""}
ENV KNOWLEDGE_BASE_2_ID=${KNOWLEDGE_BASE_2_ID:-""}
ENV SYSTEM_FUNCTION_1_NAME=${SYSTEM_FUNCTION_1_NAME:-""}
ENV SYSTEM_FUNCTION_2_NAME=${SYSTEM_FUNCTION_2_NAME:-""}

# OpenTelemetry Configuration for AWS CloudWatch GenAI Observability
ENV OTEL_PYTHON_DISTRO=aws_distro
ENV OTEL_PYTHON_CONFIGURATOR=aws_configurator
ENV OTEL_EXPORTER_OTLP_PROTOCOL=http/protobuf
ENV OTEL_TRACES_EXPORTER=otlp
ENV OTEL_EXPORTER_OTLP_LOGS_HEADERS=x-aws-log-group=agents/langgraph-ld-agent-logs,x-aws-log-stream=default,x-aws-metric-namespace=agents
ENV OTEL_RESOURCE_ATTRIBUTES=service.name=langgraph-ld-agent
ENV AGENT_OBSERVABILITY_ENABLED=true

# Expose the port that AgentCore Runtime expects
EXPOSE 8080

# Run the agent (using new handler that doesn't need bedrock-agentcore)
CMD ["python", "agentcore_handler.py"]
