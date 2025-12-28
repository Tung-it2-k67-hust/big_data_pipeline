#!/bin/bash
# Script CLI hoàn chỉnh để deploy toàn bộ Big Data Pipeline lên GKE và expose public các thành phần

set -e

echo "🚀 BIG DATA PIPELINE - FULL DEPLOY TO GKE WITH PUBLIC EXPOSURE"
echo "============================================================"

# Yêu cầu nhập thông tin
read -p "Nhập tên Cluster (ví dụ: cluster-1): " CLUSTER_NAME
read -p "Nhập Project ID (ví dụ: my-bigdata-123): " PROJECT_ID
read -p "Nhập Region (mặc định: asia-northeast1): " REGION
REGION=${REGION:-asia-northeast1}

# Validate Cluster Name
if [[ ! "$CLUSTER_NAME" =~ ^[a-z0-9-]+$ ]]; then
    echo "❌ Error: Tên Cluster chứa ký tự không hợp lệ. Chỉ sử dụng chữ thường, số và dấu gạch ngang."
    exit 1
fi

# CLUSTER_NAME="${USER_NAME}-cluster"
ZONE="${REGION}-c"
REPO_NAME="my-repo"

echo ""
echo "📋 Thông tin setup:"
echo "  - Cluster name: $CLUSTER_NAME"
echo "  - Project ID: $PROJECT_ID"
echo "  - Zone: $ZONE"
echo "  - Repo: $REPO_NAME"
echo ""
read -p "Xác nhận? (y/n): " CONFIRM

if [ "$CONFIRM" != "y" ]; then
    echo "Hủy bỏ."
    exit 1
fi

# 1. Set project và enable APIs
echo "🔧 Setting project và enabling APIs..."
gcloud config set project $PROJECT_ID
gcloud services enable container.googleapis.com
gcloud services enable artifactregistry.googleapis.com
gcloud services enable cloudbuild.googleapis.com

# 2. Tạo cluster nếu chưa có
echo "🏗️ Creating GKE cluster (mất khoảng 5-10 phút)..."
gcloud container clusters create $CLUSTER_NAME \
  --zone $ZONE \
  --num-nodes 3 \
  --machine-type e2-standard-2 \
  --disk-size 30 \
  --enable-autoscaling \
  --min-nodes 1 \
  --max-nodes 5 \
  --enable-autorepair \
  --enable-autoupgrade || echo "Cluster đã tồn tại, bỏ qua tạo mới."

# 3. Get credentials
echo "🔑 Getting cluster credentials..."
gcloud container clusters get-credentials $CLUSTER_NAME \
  --zone $ZONE \
  --project $PROJECT_ID

# 4. Verify kết nối
echo "✅ Kiểm tra kết nối..."
kubectl config current-context
kubectl get nodes

# 5. Tạo namespaces
echo "📦 Tạo namespaces..."
kubectl create namespace kafka --dry-run=client -o yaml | kubectl apply -f -
kubectl create namespace big-data-pipeline --dry-run=client -o yaml | kubectl apply -f -

# 6. Install Strimzi Operator
echo "📦 Cài đặt Strimzi Operator cho Kafka..."
kubectl create -f 'https://strimzi.io/install/latest?namespace=kafka' -n kafka || echo "Strimzi đã cài đặt."

# 7. Tạo Artifact Registry
echo "📦 Tạo Artifact Registry..."
gcloud artifacts repositories create $REPO_NAME \
  --repository-format=docker \
  --location=$REGION \
  --description="Docker repository for Big Data Pipeline" || echo "Repository đã tồn tại."

# 8. Build & Push images
echo "🏗️ Building và pushing images..."

# Kafka Producer
echo "  - Building Kafka Producer..."
# Copy dataset to build context
cp archive/full_dataset.csv kafka-producer/full_dataset.csv
cd kafka-producer
gcloud builds submit --config=cloudbuild.yaml --substitutions=_PROJECT_ID=$PROJECT_ID . --quiet
# Clean up
rm full_dataset.csv
cd ..

# Spark Streaming
echo "  - Building Spark Streaming..."
cd spark-streaming
gcloud builds submit --config=cloudbuild.yaml --substitutions=_PROJECT_ID=$PROJECT_ID . --quiet
cd ..

# Streamlit Dashboard
echo "  - Building Streamlit Dashboard..."
cd streamlit-dashboard
gcloud builds submit --config=cloudbuild.yaml --substitutions=_PROJECT_ID=$PROJECT_ID . --quiet
cd ..

echo "✅ Images đã build và push thành công."

# 9. Deploy Kafka KRaft
echo "🍺 Deploy Kafka KRaft cluster..."
kubectl apply -f kafka-kraft.yaml

# 10. Deploy toàn bộ hệ thống
echo "🚀 Deploy toàn bộ hệ thống Big Data Pipeline..."

# Tạo namespace
kubectl apply -f k8s/00-namespace.yaml

# Upload CSV data
# echo "📄 Upload CSV data..."
# kubectl create configmap football-csv-data \
#     --from-file=full_dataset.csv=archive/full_dataset.csv \
#     -n big-data-pipeline \
#     --dry-run=client -o yaml | kubectl apply -f -

# Deploy Infrastructure
echo "🏗️ Deploy Infrastructure..."
kubectl apply -f k8s/03-elasticsearch.yaml
kubectl apply -f k8s/04-kibana.yaml
kubectl apply -f k8s/09-cassandra.yaml

# Deploy Zookeeper (nếu cần)
kubectl apply -f k8s/01-zookeeper.yaml

# Deploy Kafka (nếu dùng custom)
# kubectl apply -f k8s/02-kafka.yaml

# Deploy Monitoring
kubectl apply -f k8s/08-monitoring.yaml

# Deploy Applications
echo "🚀 Deploy Applications..."
kubectl apply -f k8s/05-kafka-producer.yaml
kubectl apply -f k8s/06-spark-streaming.yaml
kubectl apply -f k8s/07-streamlit.yaml

# 11. Chờ pods running
echo "⏳ Chờ tất cả pods running (có thể mất vài phút)..."
kubectl wait --for=condition=ready pod --all -n big-data-pipeline --timeout=600s || echo "Một số pods chưa ready, kiểm tra thủ công."

# 12. Switch to Port-Forwarding (Save Quota)
echo "🌐 Cấu hình truy cập qua Port-Forwarding (do giới hạn Quota IP)..."

# Patch existing services to ClusterIP to stop pending state
echo "🔧 Patching services to ClusterIP..."
kubectl patch svc streamlit -n big-data-pipeline -p '{"spec": {"type": "ClusterIP"}}' || true
kubectl patch svc my-cluster-kafka-external-bootstrap -n kafka -p '{"spec": {"type": "ClusterIP"}}' || true

# Spark Streaming Service (ClusterIP)
echo "🔧 Creating service for Spark Streaming..."
cat <<EOF | kubectl apply -f -
apiVersion: v1
kind: Service
metadata:
  name: spark-streaming-external
  namespace: big-data-pipeline
spec:
  type: ClusterIP
  ports:
    - port: 4040
      targetPort: 4040
      name: spark-ui
  selector:
    app: spark-streaming
EOF

# 13. Hiển thị trạng thái cuối cùng
echo ""
echo "✅ ======================================"
echo "✅ DEPLOY HOÀN TẤT!"
echo "✅ ======================================"
echo ""
echo "📋 Trạng thái pods:"
kubectl get pods -n big-data-pipeline
echo ""
echo "🎯 HƯỚNG DẪN TRUY CẬP (Port Forwarding):"
echo "----------------------------------------"
echo "1. Streamlit Dashboard (Web UI):"
echo "   👉 Lệnh: kubectl port-forward svc/streamlit -n big-data-pipeline 8501:8501"
echo "   👉 Truy cập: http://localhost:8501"
echo ""
echo "2. Spark UI (Monitoring):"
echo "   👉 Lệnh: kubectl port-forward svc/spark-streaming-external -n big-data-pipeline 4040:4040"
echo "   👉 Truy cập: http://localhost:4040"
echo ""
echo "💡 Lưu ý:"
echo "  - Cluster đang chạy sẽ tốn phí (~$3-5/ngày)"
echo "  - Khi test xong, xóa: gcloud container clusters delete $CLUSTER_NAME --zone $ZONE"
echo "  - Để scale: kubectl scale deployment spark-streaming --replicas=2 -n big-data-pipeline"
echo ""

echo "🎉 Hoàn thành deploy! Chúc mừng!"