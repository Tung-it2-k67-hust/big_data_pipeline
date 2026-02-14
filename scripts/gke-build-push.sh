#!/bin/bash
# =============================================================================
# Script: gke-build-push.sh
# Mô tả: Build và push Docker images lên Google Container Registry (GCR)
# Cách dùng: ./scripts/gke-build-push.sh YOUR_PROJECT_ID
# =============================================================================

set -e

# Kiểm tra tham số
if [ -z "$1" ]; then
    echo "❌ Lỗi: Thiếu GCP Project ID"
    echo ""
    echo "Cách dùng:"
    echo "  ./scripts/gke-build-push.sh YOUR_PROJECT_ID"
    echo ""
    echo "Ví dụ:"
    echo "  ./scripts/gke-build-push.sh my-bigdata-project-123"
    exit 1
fi

PROJECT_ID="$1"
REGISTRY="gcr.io/$PROJECT_ID"

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

echo "=============================================="
echo "🚀 Build và Push Docker Images lên GCR"
echo "=============================================="
echo "Project ID: $PROJECT_ID"
echo "Registry: $REGISTRY"
echo ""

# Kiểm tra gcloud đã đăng nhập chưa
echo "📋 Kiểm tra gcloud authentication..."
if ! gcloud auth print-access-token > /dev/null 2>&1; then
    echo "❌ Chưa đăng nhập gcloud. Chạy: gcloud auth login"
    exit 1
fi
echo "✅ gcloud đã được authenticate"

# Cấu hình Docker để push lên GCR
echo ""
echo "🔧 Cấu hình Docker authentication cho GCR..."
gcloud auth configure-docker --quiet
echo "✅ Docker đã được cấu hình cho GCR"

# Build và push Kafka Producer
echo ""
echo "=============================================="
echo "📦 1/3 Building Kafka Producer..."
echo "=============================================="
cd "$PROJECT_ROOT/kafka-producer"
docker build -t kafka-producer:latest .
docker tag kafka-producer:latest "$REGISTRY/kafka-producer:latest"
echo "⬆️  Pushing kafka-producer lên GCR..."
docker push "$REGISTRY/kafka-producer:latest"
echo "✅ Kafka Producer đã push thành công!"

# Build và push Spark Streaming
echo ""
echo "=============================================="
echo "📦 2/3 Building Spark Streaming..."
echo "=============================================="
cd "$PROJECT_ROOT/spark-streaming"
docker build -t spark-streaming:latest .
docker tag spark-streaming:latest "$REGISTRY/spark-streaming:latest"
echo "⬆️  Pushing spark-streaming lên GCR..."
docker push "$REGISTRY/spark-streaming:latest"
echo "✅ Spark Streaming đã push thành công!"

# Build và push Streamlit Dashboard
echo ""
echo "=============================================="
echo "📦 3/3 Building Streamlit Dashboard..."
echo "=============================================="
cd "$PROJECT_ROOT/streamlit-dashboard"
docker build -t streamlit-dashboard:latest .
docker tag streamlit-dashboard:latest "$REGISTRY/streamlit-dashboard:latest"
echo "⬆️  Pushing streamlit-dashboard lên GCR..."
docker push "$REGISTRY/streamlit-dashboard:latest"
echo "✅ Streamlit Dashboard đã push thành công!"

# Quay lại thư mục gốc
cd "$PROJECT_ROOT"

echo ""
echo "=============================================="
echo "✅ TẤT CẢ IMAGES ĐÃ BUILD VÀ PUSH THÀNH CÔNG!"
echo "=============================================="
echo ""
echo "Images trong GCR:"
echo "  - $REGISTRY/kafka-producer:latest"
echo "  - $REGISTRY/spark-streaming:latest"
echo "  - $REGISTRY/streamlit-dashboard:latest"
echo ""
echo "Kiểm tra images:"
echo "  gcloud container images list --repository=$REGISTRY"
echo ""
echo "📌 Bước tiếp theo: Cập nhật image paths trong k8s/gke/"
echo "  Chạy: ./scripts/gke-update-images.sh $PROJECT_ID"
