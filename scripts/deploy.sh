#!/bin/bash
# Deploy the big data pipeline to Kubernetes

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
K8S_DIR="$PROJECT_ROOT/k8s"

echo "Deploying Big Data Pipeline to Kubernetes..."

# Apply Kubernetes manifests in order
echo "Creating namespace..."
kubectl apply -f "$K8S_DIR/00-namespace.yaml"

echo "Deploying Zookeeper..."
kubectl apply -f "$K8S_DIR/01-zookeeper.yaml"

echo "Waiting for Zookeeper to be ready..."
kubectl wait --for=condition=ready pod -l app=zookeeper -n big-data-pipeline --timeout=300s

echo "Deploying Kafka..."
kubectl apply -f "$K8S_DIR/02-kafka.yaml"

echo "Waiting for Kafka to be ready..."
kubectl wait --for=condition=ready pod -l app=kafka -n big-data-pipeline --timeout=300s

echo "Deploying Elasticsearch..."
kubectl apply -f "$K8S_DIR/03-elasticsearch.yaml"

echo "Waiting for Elasticsearch to be ready..."
kubectl wait --for=condition=ready pod -l app=elasticsearch -n big-data-pipeline --timeout=300s

echo "Deploying Cassandra..."
kubectl apply -f "$K8S_DIR/09-cassandra.yaml"

echo "Waiting for Cassandra to be ready..."
kubectl wait --for=condition=ready pod -l app=cassandra -n big-data-pipeline --timeout=300s

echo "Deploying Kibana..."
kubectl apply -f "$K8S_DIR/04-kibana.yaml"

echo "Deploying Kafka Producer..."
kubectl apply -f "$K8S_DIR/05-kafka-producer.yaml"

echo "Deploying Spark Streaming..."
kubectl apply -f "$K8S_DIR/06-spark-streaming.yaml"

echo "Deploying Streamlit Dashboard..."
kubectl apply -f "$K8S_DIR/07-streamlit.yaml"

echo "Deploying Monitoring Stack..."
kubectl apply -f "$K8S_DIR/08-monitoring.yaml"

echo "Deployment complete!"
echo ""
echo "Access the services:"
echo "  Kibana: http://localhost:30561"
echo "  Streamlit: http://localhost:30851"
echo "  Prometheus: http://localhost:30909"
echo "  Grafana: http://localhost:30300 (admin/admin)"
echo "  Cassandra CQL: kubectl exec -it cassandra-0 -n big-data-pipeline -- cqlsh"
echo ""
echo "Check deployment status:"
echo "  kubectl get pods -n big-data-pipeline"
