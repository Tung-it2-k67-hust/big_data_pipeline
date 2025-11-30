#!/bin/bash
# =============================================================================
# Script: gke-setup-cluster.sh
# Mô tả: Tạo GKE cluster từ đầu
# Cách dùng: ./scripts/gke-setup-cluster.sh PROJECT_ID [REGION] [CLUSTER_NAME]
# =============================================================================

set -e

# Kiểm tra tham số
if [ -z "$1" ]; then
    echo "❌ Lỗi: Thiếu GCP Project ID"
    echo ""
    echo "Cách dùng:"
    echo "  ./scripts/gke-setup-cluster.sh PROJECT_ID [REGION] [CLUSTER_NAME]"
    echo ""
    echo "Ví dụ:"
    echo "  ./scripts/gke-setup-cluster.sh my-project-123"
    echo "  ./scripts/gke-setup-cluster.sh my-project-123 asia-southeast1 my-cluster"
    exit 1
fi

PROJECT_ID="$1"
REGION="${2:-asia-southeast1}"          # Default: Singapore
CLUSTER_NAME="${3:-bigdata-cluster}"    # Default: bigdata-cluster

echo "=============================================="
echo "🚀 Thiết lập GKE Cluster"
echo "=============================================="
echo "Project ID: $PROJECT_ID"
echo "Region: $REGION"
echo "Cluster Name: $CLUSTER_NAME"
echo ""

# Kiểm tra gcloud đã đăng nhập chưa
echo "📋 Bước 1/6: Kiểm tra gcloud authentication..."
if ! gcloud auth print-access-token > /dev/null 2>&1; then
    echo "❌ Chưa đăng nhập gcloud."
    echo ""
    echo "Chạy lệnh sau:"
    echo "  gcloud auth login"
    exit 1
fi
echo "✅ Đã authenticate"
echo ""

# Set project
echo "📋 Bước 2/6: Thiết lập project..."
gcloud config set project $PROJECT_ID
echo "✅ Project đã được set: $PROJECT_ID"
echo ""

# Enable APIs
echo "📋 Bước 3/6: Enable các APIs cần thiết..."
gcloud services enable container.googleapis.com --quiet
gcloud services enable containerregistry.googleapis.com --quiet
gcloud services enable cloudbuild.googleapis.com --quiet
gcloud services enable compute.googleapis.com --quiet
echo "✅ Các APIs đã được enable"
echo ""

# Kiểm tra billing
echo "📋 Bước 4/6: Kiểm tra billing..."
BILLING_ACCOUNT=$(gcloud billing projects describe $PROJECT_ID --format="value(billingAccountName)" 2>/dev/null || echo "")
if [ -z "$BILLING_ACCOUNT" ]; then
    echo "⚠️  CẢNH BÁO: Project chưa được liên kết với billing account"
    echo "   Vào https://console.cloud.google.com/billing để liên kết"
    echo ""
    read -p "Bạn đã liên kết billing account chưa? (y/N): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
else
    echo "✅ Billing account đã được liên kết"
fi
echo ""

# Tạo GKE cluster
echo "📋 Bước 5/6: Tạo GKE cluster (có thể mất 5-10 phút)..."
echo ""

gcloud container clusters create $CLUSTER_NAME \
    --project=$PROJECT_ID \
    --region=$REGION \
    --machine-type=e2-standard-4 \
    --num-nodes=1 \
    --enable-autoscaling \
    --min-nodes=1 \
    --max-nodes=3 \
    --disk-size=100GB \
    --disk-type=pd-standard \
    --enable-ip-alias \
    --workload-pool=$PROJECT_ID.svc.id.goog

echo ""
echo "✅ GKE cluster đã được tạo"
echo ""

# Lấy credentials
echo "📋 Bước 6/6: Lấy credentials cho kubectl..."
gcloud container clusters get-credentials $CLUSTER_NAME \
    --region=$REGION \
    --project=$PROJECT_ID
echo "✅ kubectl đã được cấu hình"
echo ""

# Kiểm tra kết nối
echo "=============================================="
echo "📋 Kiểm tra kết nối cluster"
echo "=============================================="
kubectl cluster-info
echo ""
kubectl get nodes
echo ""

echo "=============================================="
echo "✅ THIẾT LẬP HOÀN TẤT!"
echo "=============================================="
echo ""
echo "📌 Bước tiếp theo:"
echo ""
echo "1. Build và push Docker images:"
echo "   ./scripts/gke-build-push.sh $PROJECT_ID"
echo ""
echo "2. Cập nhật image paths:"
echo "   ./scripts/gke-update-images.sh $PROJECT_ID"
echo ""
echo "3. Deploy lên GKE:"
echo "   ./scripts/gke-deploy.sh"
echo ""
echo "=============================================="
echo "📝 Thông tin cluster"
echo "=============================================="
echo "Project ID: $PROJECT_ID"
echo "Region: $REGION"
echo "Cluster: $CLUSTER_NAME"
echo ""
echo "Để kết nối lại sau này:"
echo "  gcloud container clusters get-credentials $CLUSTER_NAME --region=$REGION --project=$PROJECT_ID"
echo ""
