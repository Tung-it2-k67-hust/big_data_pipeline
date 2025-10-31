#!/bin/bash
# Build all Docker images for the big data pipeline

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

echo "Building Docker images..."

# Build Kafka Producer
echo "Building Kafka Producer..."
cd "$PROJECT_ROOT/kafka-producer"
docker build -t kafka-producer:latest .

# Build Spark Streaming
echo "Building Spark Streaming..."
cd "$PROJECT_ROOT/spark-streaming"
docker build -t spark-streaming:latest .

# Build Streamlit Dashboard
echo "Building Streamlit Dashboard..."
cd "$PROJECT_ROOT/streamlit-dashboard"
docker build -t streamlit-dashboard:latest .

echo "All Docker images built successfully!"
