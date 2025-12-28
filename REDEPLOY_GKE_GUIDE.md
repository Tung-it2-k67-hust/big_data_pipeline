# 🚀 HƯỚNG DẪN DEPLOY LẠI HỆ THỐNG TRÊN GKE (WSL/UBUNTU)

Tài liệu này dành cho việc copy-paste nhanh để deploy lại toàn bộ hệ thống sau khi đã xóa.

---

## 📂 BƯỚC 1: DI CHUYỂN VÀO THƯ MỤC DỰ ÁN

Mở terminal Ubuntu (WSL) và chạy:

```bash
cd /mnt/e/2025.1_monhoc/big_data_pipeline
```

---

## 🔧 BƯỚC 2: CẤU HÌNH KẾT NỐI CLOUD

Thiết lập project và kết nối tới cluster hiện có (`cluster-1` tại `australia-southeast1-c`):

```bash
# 1. Đăng nhập (nếu cần)
gcloud auth login

# 2. Thiết lập Project ID
gcloud config set project robust-magpie-479807-f1

# 3. Kết nối tới cluster
gcloud container clusters get-credentials cluster-1 --zone australia-southeast1-c

# 4. Kiểm tra kết nối
kubectl get nodes
```

---

## 🚀 BƯỚC 3: CHẠY SCRIPT DEPLOY TỰ ĐỘNG

Script này sẽ build lại images, push lên Registry và deploy toàn bộ K8s resources.

```bash
# Cấp quyền thực thi
chmod +x deploy-full-gke.sh

# Chạy script
./deploy-full-gke.sh
```

**Khi script hỏi, hãy nhập:**
- **Tên:** `cluster-1`
- **Project ID:** `robust-magpie-479807-f1`
- **Region:** `australia-southeast1`

---

## 📊 BƯỚC 4: KIỂM TRA TRẠNG THÁI & LẤY IP PUBLIC

Sau khi script chạy xong, đợi khoảng 2-3 phút để LoadBalancer cấp IP.

```bash
# 1. Xem tất cả Pods (Chờ đến khi tất cả là Running)
kubectl get pods -n big-data-pipeline

# 2. Lấy IP Streamlit Dashboard (Truy cập qua trình duyệt: http://<IP>:8501)
kubectl get svc streamlit -n big-data-pipeline

# 3. Lấy IP Kafka External (Dùng cho Producer/Consumer bên ngoài)
kubectl get svc my-cluster-kafka-external-bootstrap -n kafka

# 4. Lấy IP Spark UI (Monitor jobs: http://<IP>:4040)
kubectl get svc spark-streaming-external -n big-data-pipeline
```

---

## 🎬 BƯỚC 5: CÁC LỆNH DEMO "ĂN TIỀN" (DÀNH CHO VIDEO)

Sử dụng các lệnh này trong lúc quay video để chứng minh hệ thống hoạt động:

```bash
# 1. Scale Spark Streaming (Chứng minh Live Control)
kubectl scale deployment spark-streaming --replicas=2 -n big-data-pipeline

# 2. Theo dõi quá trình scale
kubectl get pods -n big-data-pipeline -w

# 3. Xem log Kafka Producer (Chứng minh dữ liệu đang gửi)
kubectl logs -l app=kafka-producer -n big-data-pipeline --tail=20

# 4. Xem log Spark Streaming (Chứng minh dữ liệu đang được xử lý)
kubectl logs -l app=spark-streaming -n big-data-pipeline --tail=50
```

---

## 🧹 BƯỚC 6: DỌN DẸP (KHI KẾT THÚC)

Để tránh tốn phí khi không sử dụng:

```bash
# Xóa toàn bộ resources trong namespace
kubectl delete namespace big-data-pipeline kafka

# HOẶC xóa luôn cluster (Triệt để nhất)
gcloud container clusters delete cluster-1 --zone australia-southeast1-c
```