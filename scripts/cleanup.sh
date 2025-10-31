#!/bin/bash
# Clean up and delete all resources from Kubernetes

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
K8S_DIR="$PROJECT_ROOT/k8s"

echo "Cleaning up Big Data Pipeline from Kubernetes..."

# Delete in reverse order
kubectl delete -f "$K8S_DIR/08-monitoring.yaml" --ignore-not-found=true
kubectl delete -f "$K8S_DIR/07-streamlit.yaml" --ignore-not-found=true
kubectl delete -f "$K8S_DIR/06-spark-streaming.yaml" --ignore-not-found=true
kubectl delete -f "$K8S_DIR/05-kafka-producer.yaml" --ignore-not-found=true
kubectl delete -f "$K8S_DIR/04-kibana.yaml" --ignore-not-found=true
kubectl delete -f "$K8S_DIR/09-cassandra.yaml" --ignore-not-found=true
kubectl delete -f "$K8S_DIR/03-elasticsearch.yaml" --ignore-not-found=true
kubectl delete -f "$K8S_DIR/02-kafka.yaml" --ignore-not-found=true
kubectl delete -f "$K8S_DIR/01-zookeeper.yaml" --ignore-not-found=true
kubectl delete -f "$K8S_DIR/00-namespace.yaml" --ignore-not-found=true

echo "Cleanup complete!"
