#!/bin/bash
# =============================================================================
# Script: gke-update-images.sh
# Mô tả: Cập nhật image paths trong k8s/gke/ với GCP Project ID của bạn
# Cách dùng: ./scripts/gke-update-images.sh YOUR_PROJECT_ID
# =============================================================================

set -e

# Kiểm tra tham số
if [ -z "$1" ]; then
    echo "❌ Lỗi: Thiếu GCP Project ID"
    echo ""
    echo "Cách dùng:"
    echo "  ./scripts/gke-update-images.sh YOUR_PROJECT_ID"
    echo ""
    echo "Ví dụ:"
    echo "  ./scripts/gke-update-images.sh my-bigdata-project-123"
    exit 1
fi

PROJECT_ID="$1"

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
GKE_DIR="$PROJECT_ROOT/k8s/gke"

echo "=============================================="
echo "🔧 Cập nhật image paths với Project ID"
echo "=============================================="
echo "Project ID: $PROJECT_ID"
echo "Thư mục: $GKE_DIR"
echo ""

# Tạo backup trước khi thay đổi
echo "📁 Tạo backup files..."
cp "$GKE_DIR/05-kafka-producer.yaml" "$GKE_DIR/05-kafka-producer.yaml.bak"
cp "$GKE_DIR/06-spark-streaming.yaml" "$GKE_DIR/06-spark-streaming.yaml.bak"
cp "$GKE_DIR/07-streamlit.yaml" "$GKE_DIR/07-streamlit.yaml.bak"

# Cập nhật các file YAML
echo "📝 Cập nhật 05-kafka-producer.yaml..."
sed -i "s|gcr.io/YOUR_PROJECT_ID/|gcr.io/$PROJECT_ID/|g" "$GKE_DIR/05-kafka-producer.yaml"

echo "📝 Cập nhật 06-spark-streaming.yaml..."
sed -i "s|gcr.io/YOUR_PROJECT_ID/|gcr.io/$PROJECT_ID/|g" "$GKE_DIR/06-spark-streaming.yaml"

echo "📝 Cập nhật 07-streamlit.yaml..."
sed -i "s|gcr.io/YOUR_PROJECT_ID/|gcr.io/$PROJECT_ID/|g" "$GKE_DIR/07-streamlit.yaml"

echo ""
echo "=============================================="
echo "✅ CẬP NHẬT HOÀN TẤT!"
echo "=============================================="
echo ""
echo "Các file đã được cập nhật:"
echo "  - $GKE_DIR/05-kafka-producer.yaml"
echo "  - $GKE_DIR/06-spark-streaming.yaml"
echo "  - $GKE_DIR/07-streamlit.yaml"
echo ""
echo "📁 Backup files đã được tạo (*.bak) để khôi phục nếu cần"
echo "   Để khôi phục: mv file.yaml.bak file.yaml"
echo ""
echo "📌 Bước tiếp theo: Deploy lên GKE"
echo "  Chạy: ./scripts/gke-deploy.sh"
