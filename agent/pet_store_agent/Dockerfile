
FROM --platform=linux/arm64 public.ecr.aws/docker/library/python:3.12-slim-bookworm

WORKDIR /app

# Copy requirements and install dependencies
COPY ./requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
RUN pip install bedrock-agentcore
RUN pip install aws-opentelemetry-distro

# Copy agent code and tools
COPY ./*.py ./

# Copy LlamaIndex storage directory if it exists
COPY ./storage ./storage
COPY ./data ./data

# Set default AWS region
ENV AWS_DEFAULT_REGION=${AWS_DEFAULT_REGION}

# LaunchDarkly Configuration
ENV LAUNCHDARKLY_SDK_KEY=${LAUNCHDARKLY_SDK_KEY}
ENV LAUNCHDARKLY_AGENT_KEY=${LAUNCHDARKLY_AGENT_KEY}

# LlamaIndex Configuration
ENV LLAMAINDEX_STORAGE_DIR=${LLAMAINDEX_STORAGE_DIR}
ENV LLAMAINDEX_DATA_DIR=${LLAMAINDEX_DATA_DIR}

# Optional Lambda Function Names (can be overridden by LaunchDarkly at runtime)
ENV INVENTORY_LAMBDA=${INVENTORY_LAMBDA}
ENV USER_LAMBDA=${USER_LAMBDA}

# Enable fallback tools for local testing
ENV ENABLE_FALLBACK_TOOLS=${ENABLE_FALLBACK_TOOLS}

# OpenTelemetry Configuration for AWS CloudWatch GenAI Observability
ENV OTEL_PYTHON_DISTRO=aws_distro
ENV OTEL_PYTHON_CONFIGURATOR=aws_configurator
ENV OTEL_EXPORTER_OTLP_PROTOCOL=http/protobuf
ENV OTEL_TRACES_EXPORTER=otlp
ENV OTEL_EXPORTER_OTLP_LOGS_HEADERS=x-aws-log-group=agents/langgraph-agent-logs,x-aws-log-stream=default,x-aws-metric-namespace=agents
ENV OTEL_RESOURCE_ATTRIBUTES=service.name=langgraph-agent
ENV AGENT_OBSERVABILITY_ENABLED=true

# Expose the port that AgentCore Runtime expects
EXPOSE 8080

# Run the agent
CMD ["opentelemetry-instrument", "python", "agentcore_entrypoint.py"]
