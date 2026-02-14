#!/bin/bash
# =============================================================================
# Script: gke-cleanup.sh
# Mô tả: Xóa toàn bộ resources của Big Data Pipeline trên GKE
# Cách dùng: ./scripts/gke-cleanup.sh [-f|--force]
# Flags:
#   -f, --force : Bỏ qua xác nhận và xóa ngay lập tức
# =============================================================================

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
GKE_DIR="$PROJECT_ROOT/k8s/gke"

echo "=============================================="
echo "🗑️  Cleanup Big Data Pipeline trên GKE"
echo "=============================================="
echo ""
echo "⚠️  CẢNH BÁO: Lệnh này sẽ xóa TẤT CẢ resources trong namespace big-data-pipeline"
echo "   Bao gồm: Pods, Services, StatefulSets, Deployments, PVCs, ..."
echo ""

# Hỗ trợ non-interactive mode với flag -f/--force
if [[ "$1" == "-f" ]] || [[ "$1" == "--force" ]]; then
    echo "   (Tiếp tục tự động do flag -f/--force)"
else
    read -p "Bạn có chắc chắn muốn tiếp tục? (y/N): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo "❌ Đã hủy"
        exit 1
    fi
fi

echo ""
echo "🗑️  Xóa tất cả resources..."

# Xóa theo thứ tự ngược (applications trước, infrastructure sau)
echo "Xóa Monitoring..."
kubectl delete -f "$GKE_DIR/08-monitoring.yaml" --ignore-not-found

echo "Xóa Streamlit..."
kubectl delete -f "$GKE_DIR/07-streamlit.yaml" --ignore-not-found

echo "Xóa Spark Streaming..."
kubectl delete -f "$GKE_DIR/06-spark-streaming.yaml" --ignore-not-found

echo "Xóa Kafka Producer..."
kubectl delete -f "$GKE_DIR/05-kafka-producer.yaml" --ignore-not-found

echo "Xóa Kibana..."
kubectl delete -f "$GKE_DIR/04-kibana.yaml" --ignore-not-found

echo "Xóa Cassandra..."
kubectl delete -f "$GKE_DIR/09-cassandra.yaml" --ignore-not-found

echo "Xóa Elasticsearch..."
kubectl delete -f "$GKE_DIR/03-elasticsearch.yaml" --ignore-not-found

echo "Xóa Kafka..."
kubectl delete -f "$GKE_DIR/02-kafka.yaml" --ignore-not-found

echo "Xóa Zookeeper..."
kubectl delete -f "$GKE_DIR/01-zookeeper.yaml" --ignore-not-found

echo "Xóa Ingress (nếu có)..."
kubectl delete -f "$GKE_DIR/10-ingress.yaml" --ignore-not-found 2>/dev/null || true

# Xóa PVCs còn lại
echo ""
echo "🗑️  Xóa PersistentVolumeClaims..."
kubectl delete pvc --all -n big-data-pipeline --ignore-not-found 2>/dev/null || true

# Xóa namespace (sẽ xóa tất cả resources còn lại)
echo ""
echo "🗑️  Xóa Namespace..."
kubectl delete -f "$GKE_DIR/00-namespace.yaml" --ignore-not-found

echo ""
echo "=============================================="
echo "✅ CLEANUP HOÀN TẤT!"
echo "=============================================="
echo ""
echo "📌 Để xóa GKE cluster hoàn toàn:"
echo "   gcloud container clusters delete CLUSTER_NAME --region REGION --project PROJECT_ID"
echo ""
echo "📌 Để xóa images trong GCR:"
echo "   gcloud container images delete gcr.io/PROJECT_ID/kafka-producer --force-delete-tags"
echo "   gcloud container images delete gcr.io/PROJECT_ID/spark-streaming --force-delete-tags"
echo "   gcloud container images delete gcr.io/PROJECT_ID/streamlit-dashboard --force-delete-tags"
