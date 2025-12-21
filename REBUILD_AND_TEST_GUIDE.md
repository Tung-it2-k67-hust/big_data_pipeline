# Hướng dẫn Rebuild, Deploy và Test Big Data Pipeline trên GKE

Tài liệu này tổng hợp các câu lệnh cần thiết để quản lý vòng đời của dự án trên Google Cloud Platform (GKE), từ việc xóa cluster để tiết kiệm chi phí đến việc dựng lại và kiểm thử toàn bộ hệ thống.

## 1. Xóa Cluster (Tiết kiệm chi phí)

Khi không sử dụng, hãy xóa cluster để tránh bị trừ tiền (credits).

```bash
# Thay thế tên cluster và zone của bạn
# Mặc định trong script setup là: CLUSTER_NAME="${USER_NAME}-cluster" và ZONE="asia-northeast1-c"
# Ví dụ: gcloud container clusters delete tung-cluster --zone asia-northeast1-c --quiet

gcloud container clusters delete <YOUR_CLUSTER_NAME> --zone asia-northeast1-c --quiet
```

## 2. Dựng lại Cluster & Môi trường

Khi muốn làm việc lại, hãy chạy script setup để tạo cluster mới.

```bash
./scripts/setup-gke-cluster.sh
```

Sau khi cluster đã sẵn sàng, hãy đảm bảo bạn đã kết nối `kubectl` với cluster (thường script trên đã làm rồi, nhưng đây là lệnh thủ công nếu cần):

```bash
gcloud container clusters get-credentials <YOUR_CLUSTER_NAME> --zone asia-northeast1-c
```

## 3. Build & Push Workloads (Images)

Sử dụng script `push-to-gke.sh` để build lại toàn bộ Docker images và đẩy lên Google Artifact Registry.

```bash
./scripts/push-to-gke.sh
```

*Lưu ý: Nếu bạn chỉ sửa một service cụ thể (ví dụ `kafka-producer`), bạn có thể chạy lệnh riêng lẻ:*

```bash
# Ví dụ cho Kafka Producer
cd kafka-producer
gcloud builds submit --config=cloudbuild.yaml --substitutions=_PROJECT_ID=<YOUR_PROJECT_ID> .
cd ..
```

## 4. Deploy Workloads

Sử dụng script `deploy-gke.sh` để triển khai toàn bộ hệ thống lên Kubernetes.

```bash
./scripts/deploy-gke.sh
```

## 5. Quy trình Test từng thành phần (Pipeline Testing)

Sau khi deploy, hãy kiểm tra từng thành phần theo thứ tự dữ liệu chảy qua pipeline.

### Bước 1: Kiểm tra trạng thái chung
Đảm bảo tất cả Pods đều ở trạng thái `Running`.

```bash
kubectl get pods -n big-data-pipeline
```

### Bước 2: Test Kafka Producer (Nguồn dữ liệu)
Kiểm tra xem Producer có đang gửi dữ liệu vào Kafka không.

```bash
kubectl logs -l app=kafka-producer -n big-data-pipeline --tail=20 -f
```
**Kết quả mong đợi:** Bạn sẽ thấy các dòng log như `Sent: {...}` hoặc thông báo gửi tin nhắn thành công.

### Bước 3: Test Spark Streaming (Xử lý dữ liệu)
Kiểm tra xem Spark có nhận được dữ liệu từ Kafka và xử lý không.

```bash
kubectl logs -l app=spark-streaming -n big-data-pipeline --tail=20 -f
```
**Kết quả mong đợi:** Bạn sẽ thấy các batch processing logs, ví dụ: `Batch: 0`, `Batch: 1` và output của các dataframe.

### Bước 4: Test Streamlit Dashboard (Hiển thị)
Lấy địa chỉ IP Public của Dashboard để truy cập.

```bash
kubectl get svc streamlit -n big-data-pipeline
```
**Kết quả mong đợi:** Copy `EXTERNAL-IP` (ví dụ: `34.x.x.x`) và mở trên trình duyệt với port 8501 (hoặc 80 tùy cấu hình service). Ví dụ: `http://34.123.456.78:8501`.

## 6. Test End-to-End (Kiểm tra hoạt động thực tế)

Để kiểm tra xem pipeline có thực sự hoạt động (dữ liệu mới có được cập nhật không), hãy thực hiện:

1.  Mở log của **Kafka Producer** ở một terminal:
    ```bash
    kubectl logs -l app=kafka-producer -n big-data-pipeline -f
    ```
2.  Mở **Streamlit Dashboard** trên trình duyệt.
3.  Quan sát: Khi Producer gửi tin nhắn mới (log chạy), biểu đồ trên Dashboard có thay đổi hoặc dữ liệu mới xuất hiện sau vài giây không.

**Câu lệnh "Test cuối" (Quick Check):**
Nếu bạn muốn một câu lệnh nhanh để xem dữ liệu có đang chảy qua Spark không:

```bash
# Kiểm tra log của Spark Streaming và tìm từ khóa "Batch" để xem nó có đang xử lý các batch mới không
kubectl logs -l app=spark-streaming -n big-data-pipeline --tail=100 | grep "Batch"
```
