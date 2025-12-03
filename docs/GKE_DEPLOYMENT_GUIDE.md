# 🚀 Hướng Dẫn Deploy Big Data Pipeline Lên Google Kubernetes Engine (GKE)

## 📚 Mục Lục
1. [Giới Thiệu Tổng Quan](#giới-thiệu-tổng-quan)
2. [Kubernetes Là Gì?](#kubernetes-là-gì)
3. [Quy Trình Deploy Tổng Quát](#quy-trình-deploy-tổng-quát)
4. [Yêu Cầu Cần Có](#yêu-cầu-cần-có)
5. [Bước 1: Chuẩn Bị GCP Project](#bước-1-chuẩn-bị-gcp-project)
6. [Bước 2: Tạo GKE Cluster](#bước-2-tạo-gke-cluster)
7. [Bước 3: Build và Push Docker Images](#bước-3-build-và-push-docker-images)
8. [Bước 4: Deploy Từng Service](#bước-4-deploy-từng-service)
9. [Bước 5: Truy Cập Services](#bước-5-truy-cập-services)
10. [Kiểm Tra và Monitoring](#kiểm-tra-và-monitoring)
11. [Troubleshooting](#troubleshooting)
12. [Chi Phí Ước Tính](#chi-phí-ước-tính)
13. [Dọn Dẹp Resources](#dọn-dẹp-resources)

---

## Giới Thiệu Tổng Quan

### Dự án Big Data Pipeline của bạn gồm những gì?

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         BIG DATA PIPELINE ARCHITECTURE                       │
│                                                                              │
│   ┌──────────────┐    ┌──────────────┐    ┌──────────────────────────────┐  │
│   │   Kafka      │───▶│    Kafka     │───▶│    Spark Streaming           │  │
│   │   Producer   │    │   Cluster    │    │    (Xử lý real-time)         │  │
│   │              │    │              │    │                              │  │
│   │ (Sinh dữ liệu│    │  (Message    │    │                              │  │
│   │  mẫu)        │    │   Broker)    │    │                              │  │
│   └──────────────┘    └──────────────┘    └──────────┬───────────────────┘  │
│                              │                       │                       │
│                              │                       ├───────────────────┐   │
│                              │                       │                   │   │
│                              │                       ▼                   ▼   │
│                              │            ┌──────────────────┐  ┌─────────┐  │
│                              │            │   Elasticsearch  │  │Cassandra│  │
│                              │            │   (Tìm kiếm)     │  │(Storage)│  │
│                              │            └────────┬─────────┘  └─────────┘  │
│                              │                     │                         │
│                              │         ┌───────────┼───────────┐             │
│                              │         ▼           ▼           ▼             │
│                              │    ┌────────┐  ┌────────┐  ┌────────┐         │
│                              │    │ Kibana │  │Streamlit│ │Grafana │         │
│                              │    │(Charts)│  │(Custom) │ │(Metrics)│        │
│                              │    └────────┘  └────────┘  └────────┘         │
│                              │                                               │
│   ┌──────────────┐           │                                               │
│   │  Zookeeper   │◀──────────┘                                               │
│   │ (Quản lý     │                                                           │
│   │  Kafka)      │           ┌──────────────┐                                │
│   └──────────────┘           │  Prometheus  │                                │
│                              │  (Thu thập   │                                │
│                              │   metrics)   │                                │
│                              └──────────────┘                                │
└─────────────────────────────────────────────────────────────────────────────┘
```

### Mỗi service làm gì?

| Service | Vai Trò | Ví dụ đời thực |
|---------|---------|----------------|
| **Kafka Producer** | Sinh dữ liệu mẫu (events e-commerce) | Như camera ghi lại hoạt động người dùng |
| **Zookeeper** | Quản lý, điều phối Kafka cluster | Như người quản lý nhà kho |
| **Kafka** | Hàng đợi tin nhắn, nhận và gửi dữ liệu | Như băng chuyền trong nhà máy |
| **Spark Streaming** | Xử lý dữ liệu real-time | Như công nhân xử lý hàng trên băng chuyền |
| **Elasticsearch** | Lưu trữ và tìm kiếm dữ liệu | Như thư viện với mục lục tìm kiếm |
| **Cassandra** | Lưu trữ dữ liệu time-series | Như kho hàng lớn lưu trữ lâu dài |
| **Kibana** | Trực quan hóa dữ liệu từ Elasticsearch | Như màn hình dashboard |
| **Streamlit** | Dashboard tùy chỉnh | Như app báo cáo riêng của bạn |
| **Prometheus** | Thu thập metrics hệ thống | Như sensor đo nhịp tim hệ thống |
| **Grafana** | Hiển thị metrics đẹp mắt | Như màn hình theo dõi sức khỏe |

---

## Kubernetes Là Gì?

### So sánh: Docker vs Docker Compose vs Kubernetes

| Khía cạnh | Docker | Docker Compose | Kubernetes |
|-----------|--------|----------------|------------|
| **Quy mô** | 1 container | Nhiều container trên 1 máy | Nhiều container trên NHIỀU máy |
| **Ví dụ** | Chạy 1 app | Chạy website + database | Chạy hệ thống lớn như Netflix |
| **Self-healing** | ❌ | ❌ | ✅ (Tự khởi động lại khi lỗi) |
| **Scale** | Manual | Manual | Tự động |
| **Load balancing** | Manual | Manual | Tự động |

### Các khái niệm quan trọng trong Kubernetes

```
┌─────────────────────────────────────────────────────────────────────┐
│                          KUBERNETES CLUSTER                          │
│                                                                      │
│  ┌────────────────────────────────────────────────────────────────┐ │
│  │                        NAMESPACE                                │ │
│  │                   (big-data-pipeline)                           │ │
│  │                                                                 │ │
│  │  ┌─────────────────────────────────────────────────────────┐   │ │
│  │  │                         POD                              │   │ │
│  │  │  (Đơn vị nhỏ nhất - chứa 1 hoặc nhiều containers)       │   │ │
│  │  │                                                          │   │ │
│  │  │   ┌─────────────┐   ┌─────────────┐                     │   │ │
│  │  │   │  Container  │   │  Container  │                     │   │ │
│  │  │   │   (App)     │   │  (Sidecar)  │                     │   │ │
│  │  │   └─────────────┘   └─────────────┘                     │   │ │
│  │  └─────────────────────────────────────────────────────────┘   │ │
│  │                                                                 │ │
│  │  ┌─────────────────────────────────────────────────────────┐   │ │
│  │  │                     DEPLOYMENT                           │   │ │
│  │  │  (Quản lý nhiều PODs giống nhau - cho stateless apps)   │   │ │
│  │  │                                                          │   │ │
│  │  │   POD 1 ──── POD 2 ──── POD 3                           │   │ │
│  │  └─────────────────────────────────────────────────────────┘   │ │
│  │                                                                 │ │
│  │  ┌─────────────────────────────────────────────────────────┐   │ │
│  │  │                    STATEFULSET                           │   │ │
│  │  │  (Quản lý nhiều PODs - cho stateful apps như database)  │   │ │
│  │  │                                                          │   │ │
│  │  │   kafka-0 ──── kafka-1 ──── kafka-2                     │   │ │
│  │  │      │            │            │                         │   │ │
│  │  │   PVC-0        PVC-1        PVC-2    (Lưu trữ riêng)    │   │ │
│  │  └─────────────────────────────────────────────────────────┘   │ │
│  │                                                                 │ │
│  │  ┌─────────────────────────────────────────────────────────┐   │ │
│  │  │                      SERVICE                             │   │ │
│  │  │  (Cung cấp địa chỉ cố định để các PODs nói chuyện)      │   │ │
│  │  │                                                          │   │ │
│  │  │   ClusterIP ─ Nội bộ cluster                            │   │ │
│  │  │   NodePort ── Mở cổng trên Node                         │   │ │
│  │  │   LoadBalancer ─ Tạo IP public (cloud)                  │   │ │
│  │  └─────────────────────────────────────────────────────────┘   │ │
│  └────────────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────────┘
```

### Tại sao dùng Kubernetes trên GCP (GKE)?

| Lợi ích | Giải thích |
|---------|------------|
| **Managed Control Plane** | Google quản lý master node, bạn không lo |
| **Auto-scaling** | Tự động tăng/giảm nodes khi cần |
| **Tích hợp GCP** | Dễ dàng dùng với Cloud Storage, BigQuery, ... |
| **99.95% SLA** | Google đảm bảo uptime |
| **Updates tự động** | K8s tự động được update bảo mật |

---

## Quy Trình Deploy Tổng Quát

```
┌─────────────────────────────────────────────────────────────────────────┐
│                     QUY TRÌNH DEPLOY LÊN GKE                            │
│                                                                         │
│   BƯỚC 1          BƯỚC 2           BƯỚC 3          BƯỚC 4              │
│   ┌─────┐        ┌─────────┐      ┌──────────┐    ┌───────────┐        │
│   │ GCP │   ──▶  │  GKE    │  ──▶ │ Registry │ ──▶│  Deploy   │        │
│   │Setup│        │ Cluster │      │  (GCR)   │    │ Services  │        │
│   └─────┘        └─────────┘      └──────────┘    └───────────┘        │
│      │                │                │               │                │
│      ▼                ▼                ▼               ▼                │
│   - Tạo account   - Chọn region    - Build images  - Namespace        │
│   - Enable APIs   - Chọn node      - Tag images    - StatefulSets     │
│   - Cài gcloud    - Tạo cluster    - Push to GCR   - Deployments      │
│   - Tạo project                                    - Services          │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## Yêu Cầu Cần Có

### Từ phía bạn, tôi cần những thông tin sau:

| Thông tin | Mô tả | Ví dụ |
|-----------|-------|-------|
| **GCP Project ID** | ID dự án trên GCP | `my-bigdata-project-123` |
| **Region** | Vùng deploy | `asia-southeast1` (Singapore) |
| **Billing Account** | Tài khoản thanh toán đã liên kết | Cần credit card hoặc GCP credits |

### Phần mềm cần cài trên máy local:

```bash
# 1. Google Cloud SDK (gcloud CLI)
# Download từ: https://cloud.google.com/sdk/docs/install

# 2. kubectl
# Sẽ cài thông qua gcloud

# 3. Docker
# Download từ: https://www.docker.com/get-started

# 4. Git
git --version
```

### Kiểm tra phần mềm đã cài:

```bash
# Kiểm tra gcloud
gcloud version

# Kiểm tra docker
docker --version

# Kiểm tra kubectl
kubectl version --client
```

---

## Bước 1: Chuẩn Bị GCP Project

### 1.1. Tạo tài khoản GCP (nếu chưa có)

1. Truy cập: https://console.cloud.google.com/
2. Đăng ký với email Google
3. GCP cho **$300 credits miễn phí trong 90 ngày** cho người mới!

### 1.2. Cài đặt Google Cloud SDK

**Windows:**
```powershell
# Download installer từ:
# https://dl.google.com/dl/cloudsdk/channels/rapid/GoogleCloudSDKInstaller.exe
# Chạy installer và làm theo hướng dẫn
```

**Linux/Mac:**
```bash
# Cài qua curl
curl https://sdk.cloud.google.com | bash

# Restart terminal và chạy
gcloud init
```

### 1.3. Đăng nhập và thiết lập project

```bash
# Đăng nhập vào GCP
gcloud auth login
# --> Sẽ mở trình duyệt để đăng nhập

# Tạo project mới (thay YOUR_PROJECT_ID bằng tên bạn muốn)
gcloud projects create YOUR_PROJECT_ID --name="Big Data Pipeline"

# Ví dụ:
gcloud projects create bigdata-pipeline-2024 --name="Big Data Pipeline"

# Set project mặc định
gcloud config set project YOUR_PROJECT_ID

# Liên kết billing account (QUAN TRỌNG - không có billing thì không deploy được)
# 1. Vào: https://console.cloud.google.com/billing
# 2. Tạo hoặc chọn billing account
# 3. Liên kết với project của bạn
```

### 1.4. Enable các APIs cần thiết

```bash
# Enable tất cả APIs cần thiết
gcloud services enable container.googleapis.com
gcloud services enable containerregistry.googleapis.com
gcloud services enable cloudbuild.googleapis.com
gcloud services enable compute.googleapis.com

# Kiểm tra đã enable
gcloud services list --enabled
```

### 1.5. Cài kubectl

```bash
# Cài kubectl thông qua gcloud
gcloud components install kubectl

# Kiểm tra
kubectl version --client
```

---

## Bước 2: Tạo GKE Cluster

### 2.1. Chọn cấu hình cluster

#### Đề xuất cấu hình cho dự án này:

| Thành phần | Giá trị đề xuất | Lý do |
|------------|-----------------|-------|
| **Region** | `asia-southeast1` (Singapore) | Gần Việt Nam, độ trễ thấp |
| **Machine type** | `e2-standard-4` | 4 vCPU, 16GB RAM - đủ cho Spark/ES |
| **Số nodes** | 3 | Đảm bảo HA (High Availability) |
| **Disk size** | 100GB | Đủ cho Elasticsearch, Cassandra data |

### 2.2. Tạo cluster

```bash
# Thiết lập biến môi trường (thay đổi theo nhu cầu)
export PROJECT_ID="YOUR_PROJECT_ID"        # Project ID của bạn
export REGION="asia-southeast1"            # Region bạn chọn
export CLUSTER_NAME="bigdata-cluster"      # Tên cluster

# Tạo GKE cluster
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

# Lệnh này mất khoảng 5-10 phút
# Output sẽ hiện thông tin cluster khi hoàn thành
```

### 2.3. Kết nối kubectl với cluster

```bash
# Lấy credentials để kubectl kết nối với cluster
gcloud container clusters get-credentials $CLUSTER_NAME \
    --region=$REGION \
    --project=$PROJECT_ID

# Kiểm tra kết nối
kubectl cluster-info

# Xem các nodes
kubectl get nodes

# Output mong đợi:
# NAME                                             STATUS   ROLES    AGE   VERSION
# gke-bigdata-cluster-default-pool-xxxxx-xxxx     Ready    <none>   5m    v1.27.x
```

---

## Bước 3: Build và Push Docker Images

### 3.1. Hiểu về Google Container Registry (GCR)

```
┌─────────────────────────────────────────────────────────────────┐
│                    DOCKER IMAGE FLOW                             │
│                                                                  │
│   Local Machine              Google Cloud                        │
│   ┌─────────────┐           ┌─────────────────────────┐         │
│   │             │           │  Google Container       │         │
│   │  Dockerfile │──build──▶ │  Registry (GCR)        │         │
│   │     +       │           │                         │         │
│   │  Source     │           │  gcr.io/PROJECT_ID/    │         │
│   │  Code       │──push───▶ │    kafka-producer      │         │
│   │             │           │    spark-streaming     │         │
│   │             │           │    streamlit-dashboard │         │
│   └─────────────┘           └──────────┬──────────────┘         │
│                                         │                        │
│                                         │ pull                   │
│                                         ▼                        │
│                             ┌─────────────────────┐              │
│                             │   GKE Cluster       │              │
│                             │   (Kubernetes)      │              │
│                             └─────────────────────┘              │
└─────────────────────────────────────────────────────────────────┘
```

### 3.2. Cấu hình Docker để push lên GCR

```bash
# Cấu hình Docker authentication cho GCR
gcloud auth configure-docker

# Hoặc cho Artifact Registry (phiên bản mới hơn của GCR)
gcloud auth configure-docker asia-southeast1-docker.pkg.dev
```

### 3.3. Build và Push images

#### Cách 1: Sử dụng script tự động (khuyến nghị)

```bash
# Di chuyển vào thư mục dự án
cd /path/to/big_data_pipeline

# Sử dụng script đã chuẩn bị sẵn
./scripts/gke-build-push.sh YOUR_PROJECT_ID
```

#### Cách 2: Build từng image thủ công

```bash
# Thiết lập biến
export PROJECT_ID="YOUR_PROJECT_ID"
export REGISTRY="gcr.io/$PROJECT_ID"

# ===== 1. BUILD KAFKA PRODUCER =====
echo "Building Kafka Producer..."
cd kafka-producer

# Build image
docker build -t kafka-producer:latest .

# Tag cho GCR
docker tag kafka-producer:latest $REGISTRY/kafka-producer:latest

# Push lên GCR
docker push $REGISTRY/kafka-producer:latest

echo "✅ Kafka Producer đã push xong!"

# ===== 2. BUILD SPARK STREAMING =====
echo "Building Spark Streaming..."
cd ../spark-streaming

docker build -t spark-streaming:latest .
docker tag spark-streaming:latest $REGISTRY/spark-streaming:latest
docker push $REGISTRY/spark-streaming:latest

echo "✅ Spark Streaming đã push xong!"

# ===== 3. BUILD STREAMLIT DASHBOARD =====
echo "Building Streamlit Dashboard..."
cd ../streamlit-dashboard

docker build -t streamlit-dashboard:latest .
docker tag streamlit-dashboard:latest $REGISTRY/streamlit-dashboard:latest
docker push $REGISTRY/streamlit-dashboard:latest

echo "✅ Streamlit Dashboard đã push xong!"

# Quay lại thư mục gốc
cd ..
```

### 3.4. Kiểm tra images đã push

```bash
# Liệt kê images trong GCR
gcloud container images list --repository=gcr.io/$PROJECT_ID

# Output mong đợi:
# NAME
# gcr.io/YOUR_PROJECT_ID/kafka-producer
# gcr.io/YOUR_PROJECT_ID/spark-streaming
# gcr.io/YOUR_PROJECT_ID/streamlit-dashboard
```

---

## Bước 4: Deploy Từng Service

### Hiểu về thứ tự deploy

```
┌─────────────────────────────────────────────────────────────────────────┐
│                     THỨ TỰ DEPLOY (QUAN TRỌNG!)                         │
│                                                                         │
│   Bước 1: Infrastructure (Hạ tầng)                                      │
│   ┌─────────────────────────────────────────────────────────────────┐   │
│   │  Namespace  ──▶  Zookeeper  ──▶  Kafka  ──▶  Elasticsearch       │   │
│   │     │              │              │              │               │   │
│   │     │              │              │              │               │   │
│   │    00           01            02             03                 │   │
│   └─────────────────────────────────────────────────────────────────┘   │
│                              │                                          │
│                              ▼                                          │
│   Bước 2: Database                                                      │
│   ┌─────────────────────────────────────────────────────────────────┐   │
│   │  Cassandra                                                       │   │
│   │     │                                                            │   │
│   │    09                                                            │   │
│   └─────────────────────────────────────────────────────────────────┘   │
│                              │                                          │
│                              ▼                                          │
│   Bước 3: Applications (Ứng dụng)                                       │
│   ┌─────────────────────────────────────────────────────────────────┐   │
│   │  Kibana  ──▶  Kafka Producer  ──▶  Spark Streaming  ──▶ Streamlit│   │
│   │    │              │                    │                   │     │   │
│   │   04             05                   06                  07     │   │
│   └─────────────────────────────────────────────────────────────────┘   │
│                              │                                          │
│                              ▼                                          │
│   Bước 4: Monitoring                                                    │
│   ┌─────────────────────────────────────────────────────────────────┐   │
│   │  Prometheus + Grafana                                            │   │
│   │         │                                                        │   │
│   │        08                                                        │   │
│   └─────────────────────────────────────────────────────────────────┘   │
│                                                                         │
│   ⚠️  PHẢI ĐỢI service trước READY mới deploy service sau!              │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

### 4.1. Tạo Namespace

```bash
# Di chuyển vào thư mục k8s/gke
cd k8s/gke

# Deploy namespace
kubectl apply -f 00-namespace.yaml

# Kiểm tra
kubectl get namespaces
# Output: big-data-pipeline   Active   5s
```

### 4.2. Deploy Zookeeper

```bash
# Deploy Zookeeper
kubectl apply -f 01-zookeeper.yaml

# Đợi Zookeeper ready (QUAN TRỌNG!)
kubectl wait --for=condition=ready pod -l app=zookeeper \
    -n big-data-pipeline --timeout=300s

# Kiểm tra trạng thái
kubectl get pods -n big-data-pipeline -l app=zookeeper

# Output mong đợi:
# NAME          READY   STATUS    RESTARTS   AGE
# zookeeper-0   1/1     Running   0          2m

# Xem logs nếu cần debug
kubectl logs zookeeper-0 -n big-data-pipeline
```

**Giải thích file `01-zookeeper.yaml`:**
```yaml
# Service: Tạo DNS name "zookeeper" để các pod khác kết nối
apiVersion: v1
kind: Service
metadata:
  name: zookeeper                    # Tên service
  namespace: big-data-pipeline       # Namespace
spec:
  clusterIP: None                    # Headless service cho StatefulSet
  ports:
    - port: 2181                     # Port Zookeeper
      name: client
  selector:
    app: zookeeper                   # Chọn pods có label app=zookeeper

---
# StatefulSet: Quản lý Zookeeper pod
apiVersion: apps/v1
kind: StatefulSet
metadata:
  name: zookeeper
spec:
  serviceName: zookeeper             # Liên kết với service ở trên
  replicas: 1                        # Số lượng pods
  template:
    spec:
      containers:
        - name: zookeeper
          image: confluentinc/cp-zookeeper:7.4.0  # Image từ Docker Hub
          env:
            - name: ZOOKEEPER_CLIENT_PORT
              value: "2181"          # Port client kết nối
```

### 4.3. Deploy Kafka

```bash
# Deploy Kafka
kubectl apply -f 02-kafka.yaml

# Đợi Kafka ready
kubectl wait --for=condition=ready pod -l app=kafka \
    -n big-data-pipeline --timeout=300s

# Kiểm tra
kubectl get pods -n big-data-pipeline -l app=kafka

# Test Kafka bằng cách tạo topic
kubectl exec -it kafka-0 -n big-data-pipeline -- \
    kafka-topics --create --topic test-topic \
    --bootstrap-server localhost:9092 \
    --partitions 1 --replication-factor 1

# Liệt kê topics
kubectl exec -it kafka-0 -n big-data-pipeline -- \
    kafka-topics --list --bootstrap-server localhost:9092
```

### 4.4. Deploy Elasticsearch

```bash
# Deploy Elasticsearch
kubectl apply -f 03-elasticsearch.yaml

# Đợi ready (Elasticsearch khởi động chậm, có thể mất 3-5 phút)
kubectl wait --for=condition=ready pod -l app=elasticsearch \
    -n big-data-pipeline --timeout=600s

# Kiểm tra
kubectl get pods -n big-data-pipeline -l app=elasticsearch

# Test Elasticsearch
kubectl exec -it elasticsearch-0 -n big-data-pipeline -- \
    curl -s http://localhost:9200/_cluster/health?pretty

# Output mong đợi:
# {
#   "cluster_name" : "docker-cluster",
#   "status" : "green",
#   ...
# }
```

### 4.5. Deploy Cassandra

```bash
# Deploy Cassandra
kubectl apply -f 09-cassandra.yaml

# Đợi ready (Cassandra khởi động rất chậm, có thể mất 5-10 phút)
kubectl wait --for=condition=ready pod -l app=cassandra \
    -n big-data-pipeline --timeout=600s

# Kiểm tra
kubectl get pods -n big-data-pipeline -l app=cassandra

# Test Cassandra
kubectl exec -it cassandra-0 -n big-data-pipeline -- \
    cqlsh -e "describe cluster"

# Kiểm tra schema đã được tạo chưa
kubectl exec -it cassandra-0 -n big-data-pipeline -- \
    cqlsh -e "describe keyspaces"
```

### 4.6. Deploy Kibana

```bash
# Deploy Kibana
kubectl apply -f 04-kibana.yaml

# Kiểm tra
kubectl get pods -n big-data-pipeline -l app=kibana

# Đợi ready
kubectl wait --for=condition=ready pod -l app=kibana \
    -n big-data-pipeline --timeout=300s
```

### 4.7. Deploy Kafka Producer

```bash
# Deploy Kafka Producer
kubectl apply -f 05-kafka-producer.yaml

# Kiểm tra
kubectl get pods -n big-data-pipeline -l app=kafka-producer

# Xem logs để đảm bảo đang gửi messages
kubectl logs -f deployment/kafka-producer -n big-data-pipeline
# Output: Sending message to topic data-stream...
```

### 4.8. Deploy Spark Streaming

```bash
# Deploy Spark Streaming
kubectl apply -f 06-spark-streaming.yaml

# Kiểm tra
kubectl get pods -n big-data-pipeline -l app=spark-streaming

# Xem logs
kubectl logs -f deployment/spark-streaming -n big-data-pipeline
```

### 4.9. Deploy Streamlit Dashboard

```bash
# Deploy Streamlit
kubectl apply -f 07-streamlit.yaml

# Kiểm tra
kubectl get pods -n big-data-pipeline -l app=streamlit

# Đợi ready
kubectl wait --for=condition=ready pod -l app=streamlit \
    -n big-data-pipeline --timeout=300s
```

### 4.10. Deploy Monitoring Stack

```bash
# Deploy Prometheus và Grafana
kubectl apply -f 08-monitoring.yaml

# Kiểm tra
kubectl get pods -n big-data-pipeline | grep -E "prometheus|grafana"
```

### 4.11. Deploy tất cả cùng lúc (Script tự động)

```bash
# Sử dụng script deploy tự động cho GKE
./scripts/gke-deploy.sh

# Script sẽ tự động:
# 1. Apply từng file theo thứ tự
# 2. Đợi mỗi service ready trước khi tiếp tục
# 3. In ra trạng thái cuối cùng
```

---

## Bước 5: Truy Cập Services

### 5.1. Các cách truy cập services trên GKE

```
┌─────────────────────────────────────────────────────────────────────────┐
│               CÁC CÁCH TRUY CẬP SERVICES TRÊN GKE                        │
│                                                                         │
│   CÁCH 1: Port Forward (Development - Miễn phí)                         │
│   ┌─────────────────────────────────────────────────────────────────┐   │
│   │  kubectl port-forward                                            │   │
│   │       │                                                          │   │
│   │       ▼                                                          │   │
│   │  localhost:8080 ────────▶ pod-in-cluster:80                     │   │
│   │  (Máy bạn)                (GKE)                                  │   │
│   └─────────────────────────────────────────────────────────────────┘   │
│                                                                         │
│   CÁCH 2: LoadBalancer Service (Production - Có phí)                    │
│   ┌─────────────────────────────────────────────────────────────────┐   │
│   │  Internet ────▶ External IP ────▶ Load Balancer ────▶ Pods      │   │
│   │                 (34.xxx.xxx.xxx)                                 │   │
│   └─────────────────────────────────────────────────────────────────┘   │
│                                                                         │
│   CÁCH 3: NodePort (Testing)                                            │
│   ┌─────────────────────────────────────────────────────────────────┐   │
│   │  Node IP:NodePort ────▶ Pods                                    │   │
│   │  (34.xxx.xxx.xxx:30561)                                         │   │
│   └─────────────────────────────────────────────────────────────────┘   │
│                                                                         │
│   CÁCH 4: Ingress (Production - Khuyến nghị)                            │
│   ┌─────────────────────────────────────────────────────────────────┐   │
│   │  Domain ────▶ Ingress Controller ────▶ Services ────▶ Pods      │   │
│   │  (app.example.com)     (Routing)                                │   │
│   └─────────────────────────────────────────────────────────────────┘   │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

### 5.2. Cách 1: Port Forward (Dùng cho development)

```bash
# ===== KIBANA =====
# Mở terminal 1:
kubectl port-forward svc/kibana 5601:5601 -n big-data-pipeline
# Truy cập: http://localhost:5601

# ===== STREAMLIT =====
# Mở terminal 2:
kubectl port-forward svc/streamlit 8501:8501 -n big-data-pipeline
# Truy cập: http://localhost:8501

# ===== GRAFANA =====
# Mở terminal 3:
kubectl port-forward svc/grafana 3000:3000 -n big-data-pipeline
# Truy cập: http://localhost:3000 (admin/admin)

# ===== PROMETHEUS =====
# Mở terminal 4:
kubectl port-forward svc/prometheus 9090:9090 -n big-data-pipeline
# Truy cập: http://localhost:9090

# ===== ELASTICSEARCH =====
# Mở terminal 5:
kubectl port-forward svc/elasticsearch 9200:9200 -n big-data-pipeline
# Test: curl http://localhost:9200
```

### 5.3. Cách 2: LoadBalancer (Dùng cho production)

```bash
# File k8s/gke/ đã được cấu hình sẵn với LoadBalancer
# Sau khi deploy, lấy External IP:

kubectl get services -n big-data-pipeline

# Output:
# NAME           TYPE           CLUSTER-IP     EXTERNAL-IP      PORT(S)
# kibana         LoadBalancer   10.x.x.x       34.xxx.xxx.xxx   5601:30561/TCP
# streamlit      LoadBalancer   10.x.x.x       34.xxx.xxx.xxx   8501:30851/TCP
# grafana        LoadBalancer   10.x.x.x       34.xxx.xxx.xxx   3000:30300/TCP

# Truy cập qua EXTERNAL-IP:
# Kibana: http://34.xxx.xxx.xxx:5601
# Streamlit: http://34.xxx.xxx.xxx:8501
# Grafana: http://34.xxx.xxx.xxx:3000

# ⚠️ LƯU Ý: External IP mất khoảng 1-2 phút để được cấp
# Nếu thấy <pending>, đợi thêm và chạy lại lệnh
```

### 5.4. Cách 3: Sử dụng Ingress với domain

```bash
# 1. Enable Ingress trên GKE (nếu chưa)
gcloud container clusters update $CLUSTER_NAME \
    --region=$REGION \
    --update-addons=HttpLoadBalancing=ENABLED

# 2. Apply ingress configuration
kubectl apply -f k8s/gke/10-ingress.yaml

# 3. Lấy IP của Ingress
kubectl get ingress -n big-data-pipeline

# 4. Cập nhật DNS hoặc /etc/hosts:
# 34.xxx.xxx.xxx kibana.bigdata.local streamlit.bigdata.local grafana.bigdata.local
```

---

## Kiểm Tra và Monitoring

### Các lệnh kiểm tra cơ bản

```bash
# Xem tất cả pods
kubectl get pods -n big-data-pipeline -o wide

# Xem chi tiết pod
kubectl describe pod <pod-name> -n big-data-pipeline

# Xem logs của pod
kubectl logs <pod-name> -n big-data-pipeline

# Xem logs liên tục (follow)
kubectl logs -f <pod-name> -n big-data-pipeline

# Xem logs của container cụ thể trong pod
kubectl logs <pod-name> -c <container-name> -n big-data-pipeline

# Xem tất cả services
kubectl get services -n big-data-pipeline

# Xem PersistentVolumeClaims (storage)
kubectl get pvc -n big-data-pipeline

# Xem resource usage
kubectl top pods -n big-data-pipeline
kubectl top nodes
```

### Kiểm tra từng service

```bash
# ===== KAFKA =====
# Test produce message
kubectl exec -it kafka-0 -n big-data-pipeline -- \
    bash -c "echo 'test message' | kafka-console-producer \
    --bootstrap-server localhost:9092 --topic test-topic"

# Test consume message
kubectl exec -it kafka-0 -n big-data-pipeline -- \
    kafka-console-consumer --bootstrap-server localhost:9092 \
    --topic data-stream --from-beginning --max-messages 5

# ===== ELASTICSEARCH =====
# Kiểm tra cluster health
kubectl exec -it elasticsearch-0 -n big-data-pipeline -- \
    curl -s http://localhost:9200/_cluster/health?pretty

# Liệt kê indices
kubectl exec -it elasticsearch-0 -n big-data-pipeline -- \
    curl -s http://localhost:9200/_cat/indices?v

# ===== CASSANDRA =====
# Kiểm tra node status
kubectl exec -it cassandra-0 -n big-data-pipeline -- nodetool status

# Query dữ liệu
kubectl exec -it cassandra-0 -n big-data-pipeline -- \
    cqlsh -e "SELECT * FROM bigdata_pipeline.events LIMIT 5"
```

---

## Troubleshooting

### Các lỗi thường gặp và cách khắc phục

#### 1. Pod stuck ở trạng thái Pending

```bash
# Kiểm tra lý do
kubectl describe pod <pod-name> -n big-data-pipeline

# Các nguyên nhân thường gặp:
# - Insufficient CPU/memory: Tăng node hoặc giảm resource requests
# - PVC pending: Kiểm tra StorageClass
# - Image pull failed: Kiểm tra image name và registry access
```

#### 2. Pod CrashLoopBackOff

```bash
# Xem logs để tìm lỗi
kubectl logs <pod-name> -n big-data-pipeline --previous

# Kiểm tra events
kubectl get events -n big-data-pipeline --sort-by='.lastTimestamp'
```

#### 3. Service không có External IP

```bash
# Kiểm tra service
kubectl describe svc <service-name> -n big-data-pipeline

# Đảm bảo type là LoadBalancer
# Đợi 1-2 phút cho IP được cấp
```

#### 4. Kafka Producer không connect được Kafka

```bash
# Kiểm tra Kafka service
kubectl get svc kafka -n big-data-pipeline

# Kiểm tra endpoints
kubectl get endpoints kafka -n big-data-pipeline

# Đảm bảo env KAFKA_BOOTSTRAP_SERVERS đúng
kubectl describe pod <kafka-producer-pod> -n big-data-pipeline | grep KAFKA
```

#### 5. Elasticsearch Out of Memory

```bash
# Kiểm tra memory
kubectl top pods -n big-data-pipeline

# Tăng memory trong yaml:
# resources:
#   requests:
#     memory: "2Gi"
#   limits:
#     memory: "4Gi"

# Re-apply
kubectl apply -f k8s/gke/03-elasticsearch.yaml
```

---

## Chi Phí Ước Tính

### Chi phí GKE hàng tháng (ước tính)

| Thành phần | Cấu hình | Chi phí/tháng (USD) |
|------------|----------|---------------------|
| **GKE Cluster** | Management fee (free tier) | $0 (1 cluster miễn phí) |
| **Nodes** | 3x e2-standard-4 (4 vCPU, 16GB) | ~$300 |
| **Persistent Disks** | 200GB SSD total | ~$34 |
| **Network** | Egress (50GB estimate) | ~$6 |
| **Load Balancer** | 4 services | ~$72 |
| **Total** | | **~$412/tháng** |

### Cách tiết kiệm chi phí

1. **Preemptible VMs**: Giảm ~80% chi phí nodes
```bash
gcloud container clusters create $CLUSTER_NAME \
    --preemptible \
    ... # các options khác
```

2. **Committed Use Discounts**: Cam kết 1-3 năm, giảm 37-55%

3. **Dùng miễn phí 90 ngày đầu**: $300 credits

4. **Scale down khi không dùng**:
```bash
# Scale xuống 0 nodes (giữ cluster)
gcloud container clusters resize $CLUSTER_NAME \
    --num-nodes=0 --region=$REGION
```

---

## Dọn Dẹp Resources

### Xóa tất cả resources trong namespace

```bash
# Xóa tất cả trong namespace
kubectl delete namespace big-data-pipeline

# Hoặc xóa từng resource
kubectl delete -f k8s/gke/ --all
```

### Xóa GKE Cluster

```bash
# Xóa cluster (QUAN TRỌNG: mất hết dữ liệu!)
gcloud container clusters delete $CLUSTER_NAME \
    --region=$REGION \
    --project=$PROJECT_ID

# Xác nhận: y
```

### Xóa images trong GCR

```bash
# Xóa từng image
gcloud container images delete gcr.io/$PROJECT_ID/kafka-producer --force-delete-tags
gcloud container images delete gcr.io/$PROJECT_ID/spark-streaming --force-delete-tags
gcloud container images delete gcr.io/$PROJECT_ID/streamlit-dashboard --force-delete-tags
```

### Xóa project (xóa tất cả)

```bash
# ⚠️ CẢNH BÁO: Xóa hết tất cả resources!
gcloud projects delete $PROJECT_ID
```

---

## Tổng Kết Checklist

### ✅ Checklist deploy lên GKE

- [ ] Tạo GCP account và liên kết billing
- [ ] Cài đặt gcloud CLI và kubectl
- [ ] Tạo GCP project và enable APIs
- [ ] Tạo GKE cluster
- [ ] Build và push Docker images lên GCR
- [ ] Deploy Namespace
- [ ] Deploy Zookeeper và đợi ready
- [ ] Deploy Kafka và đợi ready
- [ ] Deploy Elasticsearch và đợi ready
- [ ] Deploy Cassandra và đợi ready
- [ ] Deploy Kibana
- [ ] Deploy Kafka Producer
- [ ] Deploy Spark Streaming
- [ ] Deploy Streamlit
- [ ] Deploy Monitoring (Prometheus + Grafana)
- [ ] Cấu hình truy cập (Port Forward hoặc LoadBalancer)
- [ ] Kiểm tra tất cả services hoạt động

---

## Liên Hệ Hỗ Trợ

Nếu bạn gặp vấn đề, hãy:
1. Kiểm tra logs: `kubectl logs <pod-name> -n big-data-pipeline`
2. Mô tả pod: `kubectl describe pod <pod-name> -n big-data-pipeline`
3. Xem events: `kubectl get events -n big-data-pipeline`
4. Tạo issue trên GitHub repo

---

**Chúc bạn deploy thành công! 🎉**
