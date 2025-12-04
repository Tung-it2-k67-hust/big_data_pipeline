# Quick Start Guide - Deploy Big Data Pipeline lên GKE

## Yêu cầu trước khi bắt đầu
- Ubuntu WSL hoặc Linux terminal
- Tài khoản Google Cloud với billing enabled
- Credit card đã liên kết (hoặc dùng $300 free credit)

## Bước 1: Setup ban đầu (5 phút)

```bash
# Clone repository
git clone https://github.com/Tung-it2-k67-hust/big_data_pipeline.git
cd big_data_pipeline

# Cài Google Cloud SDK
curl https://sdk.cloud.google.com | bash
exec -l $SHELL

# Đăng nhập
gcloud init
```

## Bước 2: Tạo cluster tự động (10 phút)

```bash
# Cấp quyền thực thi
chmod +x scripts/setup-gke-cluster.sh

# Chạy script
./scripts/setup-gke-cluster.sh
```

Script sẽ hỏi:
- Tên của bạn → Nhập: `tung` (hoặc tên khác)
- Project ID → Nhập: project ID từ Google Cloud Console
- Region → Enter để dùng mặc định `asia-northeast1`

## Bước 3: Deploy Kafka (15 phút)

```bash
# Deploy Kafka KRaft
kubectl apply -f kafka-kraft.yaml

# Chờ pods Running
kubectl get pods -n kafka -w

# Lấy EXTERNAL-IP
kubectl get svc -n kafka | grep external-bootstrap
```

## Bước 4: Build & Push Images (20 phút)

```bash
# Build và push tất cả images
./scripts/push-to-gke.sh
```

## Bước 5: Deploy toàn bộ hệ thống (10 phút)

```bash
# Deploy infrastructure
kubectl apply -f k8s/03-elasticsearch.yaml
kubectl apply -f k8s/09-cassandra.yaml

# Deploy applications
kubectl apply -f k8s/05-kafka-producer.yaml
kubectl apply -f k8s/06-spark-streaming.yaml
kubectl apply -f k8s/07-streamlit.yaml

# Xem pods
kubectl get pods -n big-data-pipeline
```

## Bước 6: Truy cập Dashboard

```bash
# Lấy IP của Streamlit
kubectl get svc streamlit -n big-data-pipeline

# Truy cập: http://[EXTERNAL-IP]:8501
```

## Test từng service riêng

### Test Kafka:
```bash
cd kafka-producer
python3 -m venv venv
source venv/bin/activate
pip install kafka-python
export KAFKA_BOOTSTRAP_SERVERS=[KAFKA_IP]:9094
cd src && python producer.py
```

### Test Cassandra:
```bash
kubectl exec -it cassandra-0 -n big-data-pipeline -- cqlsh
```

### Test Elasticsearch:
```bash
kubectl port-forward -n big-data-pipeline svc/elasticsearch 9200:9200
curl http://localhost:9200
```

## Cleanup khi xong

```bash
# Xóa deployments
kubectl delete namespace big-data-pipeline
kubectl delete namespace kafka

# Xóa cluster (tiết kiệm chi phí!)
gcloud container clusters delete [YOUR_NAME]-cluster --zone asia-northeast1-c
```

## Troubleshooting

### ImagePullBackOff:
```bash
kubectl describe pod [POD_NAME] -n [NAMESPACE]
# Kiểm tra image đã push lên Artifact Registry chưa
```

### Pod Pending:
```bash
kubectl get events -n [NAMESPACE] --sort-by='.lastTimestamp'
# Scale cluster nếu thiếu resources
```

### Không kết nối được Kafka:
```bash
# Test connection
telnet [KAFKA_IP] 9094
# Kiểm tra firewall rules
```

## Cost Estimation

- **GKE Cluster (3 nodes e2-standard-4):** ~$3-5/ngày
- **Persistent Disks:** ~$0.5/ngày
- **LoadBalancer:** ~$0.5/ngày
- **Total:** ~$4-6/ngày

**💡 Tip:** Tắt cluster khi không dùng để tiết kiệm!

## Support

- Đọc chi tiết: `DEPLOY_GUIDE_GKE.md`
- Issues: GitHub Issues
- Slack: #big-data-pipeline channel
