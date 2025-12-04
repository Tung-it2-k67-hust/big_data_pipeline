# ============================================
# HƯỚNG DẪN DEPLOY BIG DATA PIPELINE LÊN GOOGLE KUBERNETES ENGINE (GKE)
# Dành cho teammate test riêng các service: Kafka, Spark Streaming, Cassandra, Elasticsearch, Streamlit
# ============================================

# ============================================
# PHẦN 1: SETUP MÔI TRƯỜNG (Chỉ làm 1 lần)
# ============================================

# 1. Cài đặt Google Cloud SDK trên Ubuntu WSL
curl https://sdk.cloud.google.com | bash
exec -l $SHELL

# 2. Đăng nhập Google Cloud
gcloud init
# → Chọn account Google của bạn
# → Tạo hoặc chọn project (ví dụ: my-bigdata-project-123)
# → Chọn region mặc định: asia-northeast1

# 3. Cài kubectl và plugin GKE
gcloud components install kubectl
gcloud components install gke-gcloud-auth-plugin

# 4. Bật các API cần thiết
gcloud services enable container.googleapis.com
gcloud services enable artifactregistry.googleapis.com
gcloud services enable cloudbuild.googleapis.com

# ============================================
# PHẦN 2: TẠO GKE CLUSTER (Mỗi người 1 cluster riêng)
# ============================================

# 5. Tạo cluster GKE của riêng bạn
# Thay [YOUR_NAME] bằng tên của bạn (ví dụ: tung-cluster, dat-cluster)
gcloud container clusters create [YOUR_NAME]-cluster \
  --zone asia-northeast1-c \
  --num-nodes 3 \
  --machine-type e2-standard-4 \
  --disk-size 50 \
  --enable-autoscaling \
  --min-nodes 1 \
  --max-nodes 5 \
  --enable-autorepair \
  --enable-autoupgrade

# 6. Kết nối kubectl với cluster
gcloud container clusters get-credentials [YOUR_NAME]-cluster \
  --zone asia-northeast1-c \
  --project [YOUR_PROJECT_ID]

# 7. Kiểm tra kết nối
kubectl config current-context
kubectl get nodes

# ============================================
# PHẦN 3: DEPLOY KAFKA KRAFT (Message Broker)
# ============================================

# 8. Tạo namespace cho Kafka
kubectl create namespace kafka

# 9. Cài đặt Strimzi Operator
kubectl create -f 'https://strimzi.io/install/latest?namespace=kafka' -n kafka

# 10. Chờ Operator khởi động
kubectl get pods -n kafka -w
# Chờ đến khi strimzi-cluster-operator Running

# 11. Deploy Kafka KRaft cluster
kubectl apply -f kafka-kraft.yaml

# 12. Chờ Kafka cluster khởi động (5-10 phút)
kubectl get pods -n kafka -w
# Chờ đến khi my-cluster-dual-role-0, my-cluster-dual-role-1, my-cluster-dual-role-2 Running

# 13. Lấy EXTERNAL-IP của Kafka
kubectl get svc -n kafka | grep external-bootstrap
# Lưu lại EXTERNAL-IP (ví dụ: 34.180.65.245)

# 14. Test Kafka với Producer/Consumer
export KAFKA_EXTERNAL_IP=[IP_TỪ_BƯỚC_13]
export KAFKA_BOOTSTRAP_SERVERS=$KAFKA_EXTERNAL_IP:9094

# Tạo venv và cài thư viện
cd kafka-producer
python3 -m venv venv
source venv/bin/activate
pip install kafka-python

# Chạy Producer
cd src
python producer.py

# Mở terminal mới, chạy Consumer
cd kafka-producer
source venv/bin/activate
export KAFKA_EXTERNAL_IP=[IP_TỪ_BƯỚC_13]
cd src
python consumer.py

# ============================================
# PHẦN 4: BUILD & PUSH DOCKER IMAGES LÊN GOOGLE CLOUD
# ============================================

# 15. Tạo Artifact Registry
gcloud artifacts repositories create my-repo \
  --repository-format=docker \
  --location=asia-northeast1 \
  --description="Docker repository for Big Data Pipeline"

# 16. Build và Push images bằng Cloud Build
cd /path/to/big_data_pipeline
./scripts/push-to-gke.sh

# Hoặc build từng service riêng:
cd kafka-producer
gcloud builds submit --config=cloudbuild.yaml --substitutions=_PROJECT_ID=[YOUR_PROJECT_ID] .

cd ../spark-streaming
gcloud builds submit --config=cloudbuild.yaml --substitutions=_PROJECT_ID=[YOUR_PROJECT_ID] .

cd ../streamlit-dashboard
gcloud builds submit --config=cloudbuild.yaml --substitutions=_PROJECT_ID=[YOUR_PROJECT_ID] .

# 17. Kiểm tra images đã push thành công
gcloud artifacts docker images list \
  asia-northeast1-docker.pkg.dev/[YOUR_PROJECT_ID]/my-repo \
  --include-tags

# ============================================
# PHẦN 5: DEPLOY HẠ TẦNG (Elasticsearch, Cassandra)
# ============================================

# 18. Tạo namespace cho big data pipeline
kubectl create namespace big-data-pipeline

# 19. Deploy Elasticsearch
kubectl apply -f k8s/03-elasticsearch.yaml

# 20. Deploy Kibana (optional)
kubectl apply -f k8s/04-kibana.yaml

# 21. Deploy Cassandra
kubectl apply -f k8s/09-cassandra.yaml

# 22. Chờ các pods khởi động
kubectl get pods -n big-data-pipeline -w
# Chờ đến khi elasticsearch-0, cassandra-0 Running

# 23. Kiểm tra Cassandra đã init schema chưa
kubectl logs -n big-data-pipeline job/cassandra-schema-init

# 24. Test kết nối Cassandra
kubectl exec -it cassandra-0 -n big-data-pipeline -- cqlsh
# Trong cqlsh:
DESCRIBE KEYSPACES;
USE bigdata_pipeline;
DESCRIBE TABLES;
exit

# ============================================
# PHẦN 6: DEPLOY ỨNG DỤNG (Producer, Spark, Streamlit)
# ============================================

# 25. Deploy Kafka Producer
kubectl apply -f k8s/05-kafka-producer.yaml

# 26. Deploy Spark Streaming
kubectl apply -f k8s/06-spark-streaming.yaml

# 27. Deploy Streamlit Dashboard
kubectl apply -f k8s/07-streamlit.yaml

# 28. Kiểm tra tất cả pods
kubectl get pods -n big-data-pipeline
kubectl get pods -n kafka

# 29. Xem logs của từng service
kubectl logs -n big-data-pipeline deployment/kafka-producer --follow
kubectl logs -n big-data-pipeline deployment/spark-streaming --follow
kubectl logs -n big-data-pipeline deployment/streamlit --follow

# ============================================
# PHẦN 7: TRUY CẬP CÁC SERVICE
# ============================================

# 30. Lấy EXTERNAL-IP của Streamlit Dashboard
kubectl get svc streamlit -n big-data-pipeline
# Truy cập: http://[EXTERNAL-IP]:8501

# 31. Lấy EXTERNAL-IP của Kibana (nếu deploy)
kubectl get svc kibana -n big-data-pipeline
# Truy cập: http://[EXTERNAL-IP]:5601

# 32. Port-forward Elasticsearch (nếu muốn truy cập từ local)
kubectl port-forward -n big-data-pipeline svc/elasticsearch 9200:9200
# Truy cập: http://localhost:9200

# ============================================
# PHẦN 8: MONITORING & DEBUG
# ============================================

# 33. Xem tất cả services
kubectl get svc --all-namespaces

# 34. Xem events của namespace
kubectl get events -n big-data-pipeline --sort-by='.lastTimestamp'

# 35. Describe pod nếu có lỗi
kubectl describe pod [POD_NAME] -n big-data-pipeline

# 36. Exec vào container để debug
kubectl exec -it [POD_NAME] -n big-data-pipeline -- /bin/bash

# 37. Xem logs real-time
kubectl logs -n big-data-pipeline [POD_NAME] --follow --tail=100

# 38. Xem resource usage
kubectl top nodes
kubectl top pods -n big-data-pipeline

# ============================================
# PHẦN 9: SCALE & AUTOSCALING
# ============================================

# 39. Scale số replicas của service
kubectl scale deployment kafka-producer --replicas=3 -n big-data-pipeline

# 40. Enable autoscaling cho cluster
gcloud container node-pools update default-pool \
  --cluster=[YOUR_NAME]-cluster \
  --zone=asia-northeast1-c \
  --enable-autoscaling \
  --min-nodes=1 \
  --max-nodes=5

# 41. Enable Horizontal Pod Autoscaler (HPA)
kubectl autoscale deployment spark-streaming \
  --cpu-percent=80 \
  --min=1 \
  --max=5 \
  -n big-data-pipeline

# ============================================
# PHẦN 10: CLEANUP (Khi test xong)
# ============================================

# 42. Xóa toàn bộ deployments trong namespace
kubectl delete namespace big-data-pipeline
kubectl delete namespace kafka

# 43. Xóa cluster (tiết kiệm chi phí)
gcloud container clusters delete [YOUR_NAME]-cluster \
  --zone asia-northeast1-c \
  --quiet

# 44. Xóa Artifact Registry repository
gcloud artifacts repositories delete my-repo \
  --location=asia-northeast1 \
  --quiet

# ============================================
# PHẦN 11: TROUBLESHOOTING COMMON ISSUES
# ============================================

# Lỗi ImagePullBackOff:
# → Kiểm tra image đã push lên Artifact Registry chưa
# → Kiểm tra imagePullPolicy trong YAML

# Lỗi CrashLoopBackOff:
# → Xem logs: kubectl logs [POD_NAME] -n [NAMESPACE]
# → Kiểm tra resources limits/requests
# → Kiểm tra dependencies (Kafka, Cassandra có sẵn chưa)

# Pod Pending:
# → Xem events: kubectl describe pod [POD_NAME]
# → Kiểm tra node có đủ resources không
# → Scale cluster nếu cần

# Không kết nối được Kafka:
# → Kiểm tra KAFKA_BOOTSTRAP_SERVERS đúng chưa
# → Kiểm tra firewall rules cho port 9094
# → Test: telnet [KAFKA_IP] 9094

# ============================================
# PHẦN 12: TIPS & BEST PRACTICES
# ============================================

# 1. Luôn dùng namespace riêng cho mỗi môi trường (dev, staging, prod)
# 2. Set resource limits để tránh một pod chiếm hết tài nguyên
# 3. Enable monitoring với Prometheus/Grafana
# 4. Backup dữ liệu Cassandra định kỳ
# 5. Dùng ConfigMap/Secret cho configuration thay vì hardcode
# 6. Tag images với version cụ thể thay vì :latest
# 7. Test kỹ trên local trước khi deploy production
# 8. Monitor cost trên Google Cloud Console
# 9. Tắt cluster khi không dùng để tiết kiệm chi phí
# 10. Đọc logs thường xuyên để phát hiện lỗi sớm

# ============================================
# KẾT THÚC - CHÚC BẠN DEPLOY THÀNH CÔNG! 🚀
# ============================================
