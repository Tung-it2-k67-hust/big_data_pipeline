#!/bin/bash
# Script deploy toàn bộ hệ thống lên GKE

set -e

echo "🚀 Bắt đầu deploy hệ thống Big Data Pipeline lên GKE..."

# 1. Tạo namespace
echo "📦 Tạo namespace..."
kubectl apply -f k8s/00-namespace.yaml

# 2. Tạo ConfigMap cho CSV data (Upload file CSV lên K8s)
echo "📄 Upload CSV data..."
kubectl create configmap football-csv-data \
    --from-file=full_dataset.csv=archive/full_dataset.csv \
    -n big-data-pipeline \
    --dry-run=client -o yaml | kubectl apply -f -

# 3. Deploy Infrastructure (Elasticsearch, Cassandra)
echo "🏗️ Deploy Infrastructure..."
kubectl apply -f k8s/03-elasticsearch.yaml
kubectl apply -f k8s/04-kibana.yaml
kubectl apply -f k8s/09-cassandra.yaml

# 4. Deploy Applications
echo "🚀 Deploy Applications..."
kubectl apply -f k8s/05-kafka-producer.yaml
kubectl apply -f k8s/06-spark-streaming.yaml
kubectl apply -f k8s/07-streamlit.yaml

echo "✅ Deploy hoàn tất! Kiểm tra trạng thái pods:"
kubectl get pods -n big-data-pipeline
