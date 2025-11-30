#!/bin/bash
# =============================================================================
# Script: gke-deploy.sh
# Mô tả: Deploy toàn bộ Big Data Pipeline lên GKE theo thứ tự đúng
# Cách dùng: ./scripts/gke-deploy.sh
# =============================================================================

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
GKE_DIR="$PROJECT_ROOT/k8s/gke"

echo "=============================================="
echo "🚀 Deploy Big Data Pipeline lên GKE"
echo "=============================================="
echo ""

# Kiểm tra kubectl đã kết nối với cluster chưa
echo "📋 Kiểm tra kết nối với GKE cluster..."
if ! kubectl cluster-info > /dev/null 2>&1; then
    echo "❌ Không kết nối được với Kubernetes cluster"
    echo ""
    echo "Chạy lệnh sau để kết nối:"
    echo "  gcloud container clusters get-credentials CLUSTER_NAME --region REGION --project PROJECT_ID"
    exit 1
fi
echo "✅ Đã kết nối với cluster"
kubectl cluster-info | head -1
echo ""

# Kiểm tra image paths đã được cập nhật chưa
if grep -q "YOUR_PROJECT_ID" "$GKE_DIR/05-kafka-producer.yaml"; then
    echo "⚠️  CẢNH BÁO: Image paths chưa được cập nhật!"
    echo "   Chạy: ./scripts/gke-update-images.sh YOUR_PROJECT_ID"
    echo ""
    read -p "Bạn có muốn tiếp tục không? (y/N): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

# Deploy theo thứ tự
echo "=============================================="
echo "📁 Bước 1/10: Tạo Namespace"
echo "=============================================="
kubectl apply -f "$GKE_DIR/00-namespace.yaml"
echo "✅ Namespace đã tạo"
echo ""

echo "=============================================="
echo "🐘 Bước 2/10: Deploy Zookeeper"
echo "=============================================="
kubectl apply -f "$GKE_DIR/01-zookeeper.yaml"
echo "⏳ Đợi Zookeeper ready..."
kubectl wait --for=condition=ready pod -l app=zookeeper -n big-data-pipeline --timeout=300s
echo "✅ Zookeeper đã ready"
echo ""

echo "=============================================="
echo "📨 Bước 3/10: Deploy Kafka"
echo "=============================================="
kubectl apply -f "$GKE_DIR/02-kafka.yaml"
echo "⏳ Đợi Kafka ready..."
kubectl wait --for=condition=ready pod -l app=kafka -n big-data-pipeline --timeout=300s
echo "✅ Kafka đã ready"
echo ""

echo "=============================================="
echo "🔍 Bước 4/10: Deploy Elasticsearch"
echo "=============================================="
kubectl apply -f "$GKE_DIR/03-elasticsearch.yaml"
echo "⏳ Đợi Elasticsearch ready (có thể mất 3-5 phút)..."
kubectl wait --for=condition=ready pod -l app=elasticsearch -n big-data-pipeline --timeout=600s
echo "✅ Elasticsearch đã ready"
echo ""

echo "=============================================="
echo "💾 Bước 5/10: Deploy Cassandra"
echo "=============================================="
kubectl apply -f "$GKE_DIR/09-cassandra.yaml"
echo "⏳ Đợi Cassandra ready (có thể mất 5-10 phút)..."
kubectl wait --for=condition=ready pod -l app=cassandra -n big-data-pipeline --timeout=600s
echo "✅ Cassandra đã ready"
echo ""

echo "=============================================="
echo "📊 Bước 6/10: Deploy Kibana"
echo "=============================================="
kubectl apply -f "$GKE_DIR/04-kibana.yaml"
echo "⏳ Đợi Kibana ready..."
kubectl wait --for=condition=ready pod -l app=kibana -n big-data-pipeline --timeout=300s
echo "✅ Kibana đã ready"
echo ""

echo "=============================================="
echo "📤 Bước 7/10: Deploy Kafka Producer"
echo "=============================================="
kubectl apply -f "$GKE_DIR/05-kafka-producer.yaml"
echo "✅ Kafka Producer đã deploy"
echo ""

echo "=============================================="
echo "⚡ Bước 8/10: Deploy Spark Streaming"
echo "=============================================="
kubectl apply -f "$GKE_DIR/06-spark-streaming.yaml"
echo "✅ Spark Streaming đã deploy"
echo ""

echo "=============================================="
echo "📈 Bước 9/10: Deploy Streamlit Dashboard"
echo "=============================================="
kubectl apply -f "$GKE_DIR/07-streamlit.yaml"
echo "⏳ Đợi Streamlit ready..."
kubectl wait --for=condition=ready pod -l app=streamlit -n big-data-pipeline --timeout=300s
echo "✅ Streamlit đã ready"
echo ""

echo "=============================================="
echo "📉 Bước 10/10: Deploy Monitoring Stack"
echo "=============================================="
kubectl apply -f "$GKE_DIR/08-monitoring.yaml"
echo "⏳ Đợi Prometheus ready..."
kubectl wait --for=condition=ready pod -l app=prometheus -n big-data-pipeline --timeout=300s
echo "⏳ Đợi Grafana ready..."
kubectl wait --for=condition=ready pod -l app=grafana -n big-data-pipeline --timeout=300s
echo "✅ Monitoring stack đã ready"
echo ""

echo "=============================================="
echo "✅ DEPLOY HOÀN TẤT!"
echo "=============================================="
echo ""
echo "📋 Trạng thái tất cả pods:"
kubectl get pods -n big-data-pipeline
echo ""
echo "🌐 Trạng thái services (đợi External IP):"
kubectl get services -n big-data-pipeline
echo ""
echo "=============================================="
echo "📌 HƯỚNG DẪN TRUY CẬP"
echo "=============================================="
echo ""
echo "🔹 Cách 1: Port Forward (cho development)"
echo "   kubectl port-forward svc/kibana 5601:5601 -n big-data-pipeline"
echo "   kubectl port-forward svc/streamlit 8501:8501 -n big-data-pipeline"
echo "   kubectl port-forward svc/grafana 3000:3000 -n big-data-pipeline"
echo ""
echo "🔹 Cách 2: External IP (đợi 1-2 phút để có IP)"
echo "   kubectl get svc -n big-data-pipeline -w"
echo ""
echo "🔹 Kiểm tra logs:"
echo "   kubectl logs -f deployment/kafka-producer -n big-data-pipeline"
echo "   kubectl logs -f deployment/spark-streaming -n big-data-pipeline"
echo ""
