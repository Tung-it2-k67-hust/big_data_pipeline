#!/bin/bash
# Script tự động setup GKE cluster cho teammate
# Chạy trên Ubuntu WSL

set -e

echo "🚀 BIG DATA PIPELINE - GKE SETUP SCRIPT"
echo "========================================"

# Yêu cầu nhập thông tin
read -p "Nhập tên của bạn (ví dụ: tung, dat): " USER_NAME
read -p "Nhập Project ID (ví dụ: my-bigdata-123): " PROJECT_ID
read -p "Nhập Region (mặc định: asia-northeast1): " REGION
REGION=${REGION:-asia-northeast1}

CLUSTER_NAME="${USER_NAME}-cluster"
ZONE="${REGION}-c"

echo ""
echo "📋 Thông tin setup:"
echo "  - Cluster name: $CLUSTER_NAME"
echo "  - Project ID: $PROJECT_ID"
echo "  - Zone: $ZONE"
echo ""
read -p "Xác nhận? (y/n): " CONFIRM

if [ "$CONFIRM" != "y" ]; then
    echo "Hủy bỏ."
    exit 1
fi

# 1. Set project
echo "🔧 Setting project..."
gcloud config set project $PROJECT_ID

# 2. Enable APIs
echo "🔧 Enabling required APIs..."
gcloud services enable container.googleapis.com
gcloud services enable artifactregistry.googleapis.com
gcloud services enable cloudbuild.googleapis.com

# 3. Tạo cluster
echo "🏗️ Creating GKE cluster (mất khoảng 5-10 phút)..."
gcloud container clusters create $CLUSTER_NAME \
  --zone $ZONE \
  --num-nodes 3 \
  --machine-type e2-standard-4 \
  --disk-size 50 \
  --enable-autoscaling \
  --min-nodes 1 \
  --max-nodes 5 \
  --enable-autorepair \
  --enable-autoupgrade

# 4. Get credentials
echo "🔑 Getting cluster credentials..."
gcloud container clusters get-credentials $CLUSTER_NAME \
  --zone $ZONE \
  --project $PROJECT_ID

# 5. Verify
echo "✅ Kiểm tra kết nối..."
kubectl config current-context
kubectl get nodes

# 6. Tạo namespaces
echo "📦 Tạo namespaces..."
kubectl create namespace kafka || true
kubectl create namespace big-data-pipeline || true

# 7. Install Strimzi Operator
echo "📦 Cài đặt Strimzi Operator cho Kafka..."
kubectl create -f 'https://strimzi.io/install/latest?namespace=kafka' -n kafka

# 8. Tạo Artifact Registry
echo "📦 Tạo Artifact Registry..."
gcloud artifacts repositories create my-repo \
  --repository-format=docker \
  --location=$REGION \
  --description="Docker repository for Big Data Pipeline" || true

echo ""
echo "✅ ======================================"
echo "✅ SETUP HOÀN TẤT!"
echo "✅ ======================================"
echo ""
echo "📋 Thông tin cluster của bạn:"
echo "  - Cluster: $CLUSTER_NAME"
echo "  - Zone: $ZONE"
echo "  - Project: $PROJECT_ID"
echo ""
echo "🎯 Bước tiếp theo:"
echo "  1. Chạy: kubectl get nodes"
echo "  2. Deploy Kafka: kubectl apply -f kafka-kraft.yaml"
echo "  3. Xem hướng dẫn chi tiết trong: DEPLOY_GUIDE_GKE.md"
echo ""
echo "💡 Lưu ý:"
echo "  - Cluster đang chạy sẽ tốn phí (~$3-5/ngày)"
echo "  - Khi test xong, chạy: gcloud container clusters delete $CLUSTER_NAME --zone $ZONE"
echo ""
