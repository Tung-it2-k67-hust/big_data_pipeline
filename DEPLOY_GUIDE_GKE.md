Dưới đây là hướng dẫn cô đọng và thực tế để bạn đưa vào báo cáo hoặc tài liệu hướng dẫn.

Phần 1 là **Quy trình cập nhật code (CI/CD thủ công)** khi bạn sửa file Python.
Phần 2 là **Kịch bản Demo (Showcase)** để trình bày kết quả cho các thầy cô, chứng minh hệ thống hoạt động thực tế.

-----

### PHẦN 1: QUY TRÌNH CẬP NHẬT CODE (UPDATE PIPELINE)

Khi bạn sửa bất kỳ file `.py` nào (ví dụ: sửa logic Spark, sửa giao diện Streamlit), bạn **BẮT BUỘC** phải thực hiện 3 bước: **Build -\> Push -\> Restart Deployment**.

**Biến môi trường chung (Chạy lệnh này trước mỗi lần làm việc):**

```bash
export PROJECT_ID="robust-magpie-479807-f1"
export NAMESPACE="big-data-pipeline"
```

#### 1\. Nếu sửa Kafka Producer (`producer.py`)

Dùng khi bạn muốn thay đổi tốc độ gửi tin, hoặc thay đổi dữ liệu đầu vào.

```bash
# 1. Di chuyển vào thư mục code
cd kafka-producer

# 2. Build và Push image mới lên Cloud (sử dụng Cloud Build)
echo "📦 Building & Pushing Kafka Producer..."
gcloud builds submit --config=cloudbuild.yaml --substitutions=_PROJECT_ID=$PROJECT_ID .

# 3. Cập nhật Deployment trên Kubernetes (Kéo image mới về)
echo "🔄 Rolling Update Kafka Producer..."
kubectl rollout restart deployment kafka-producer -n $NAMESPACE

# 4. Kiểm tra logs để chắc chắn code mới chạy ổn
echo "🔍 Checking Logs..."
kubectl logs -l app=kafka-producer -n $NAMESPACE --follow
```

#### 2\. Nếu sửa Spark Streaming (`streaming_app.py`)

Dùng khi bạn sửa logic tính toán, aggregation, watermark, hoặc logic ghi vào DB.

```bash
# 1. Di chuyển vào thư mục code
cd spark-streaming

# 2. Build và Push image mới
echo "📦 Building & Pushing Spark Streaming..."
gcloud builds submit --config=cloudbuild.yaml --substitutions=_PROJECT_ID=$PROJECT_ID .

# 3. Cập nhật Deployment (Spark sẽ dừng xử lý cũ và chạy xử lý mới)
echo "🔄 Rolling Update Spark Streaming..."
kubectl rollout restart deployment spark-streaming -n $NAMESPACE

# 4. Kiểm tra logs (Quan trọng: xem có lỗi logic không)
echo "🔍 Checking Logs..."
kubectl logs -l app=spark-streaming -n $NAMESPACE --follow
```

#### 3\. Nếu sửa Streamlit Dashboard (`app.py`)

Dùng khi bạn chỉnh sửa biểu đồ, màu sắc, hoặc cách hiển thị dữ liệu.

```bash
# 1. Di chuyển vào thư mục code
cd streamlit-dashboard

# 2. Build và Push image mới
echo "📦 Building & Pushing Streamlit..."
gcloud builds submit --config=cloudbuild.yaml --substitutions=_PROJECT_ID=$PROJECT_ID .

# 3. Cập nhật Deployment
echo "🔄 Rolling Update Streamlit..."
kubectl rollout restart deployment streamlit -n $NAMESPACE

# 4. Lấy lại địa chỉ IP (nếu cần, thường IP không đổi)
kubectl get svc streamlit -n $NAMESPACE
```

-----

### PHẦN 2: KẾT QUẢ CẦN SHOW CHO GIÁO VIÊN (DEMO SCRIPT)

Khi báo cáo đồ án, bạn cần chứng minh được luồng dữ liệu đi từ đầu đến cuối (**End-to-End Pipeline**). Hãy mở sẵn các cửa sổ sau:

#### 1\. Show Hạ tầng (Chứng minh hệ thống Distributed)

Mở một terminal và chạy lệnh này để cho thấy tất cả các thành phần đang chạy trên Kubernetes (Cluster).

  * **Lệnh:** `kubectl get pods -n big-data-pipeline`
  * **Điểm nhấn:**
      * Chỉ vào **Kafka, Zookeeper** (Message Queue).
      * Chỉ vào **Elasticsearch, Cassandra** (NoSQL Databases).
      * Chỉ vào **Spark Streaming** (Processing Engine).
      * Trạng thái tất cả phải là **Running**.

#### 2\. Show Luồng Dữ liệu Real-time (Logs)

Đây là phần "kỹ thuật" nhất, chứng minh Spark đang xử lý từng giây.

  * **Lệnh:** `kubectl logs -l app=spark-streaming -n big-data-pipeline --follow`
  * **Giải thích:** "Đây là logs của Spark Streaming. Các thầy có thể thấy nó đang xử lý theo từng Batch (lô dữ liệu). Dòng `Batch ... completed` hiện ra liên tục nghĩa là dữ liệu đang chảy từ Kafka qua Spark và được ghi xuống Database."

#### 3\. Show Kết quả Trực quan (Streamlit Dashboard)

Đây là phần quan trọng nhất để người xem dễ hình dung.

  * **Truy cập:** Trình duyệt web `http://[EXTERNAL-IP]:8501`
  * **Điểm nhấn:**
      * Chỉ vào các biểu đồ tự động cập nhật (nếu bạn để auto-refresh) hoặc bấm nút refresh.
      * Giải thích dữ liệu này lấy từ **Elasticsearch/Cassandra**, nơi mà Spark vừa ghi dữ liệu vào.
      * **Quan trọng:** Nếu có thể, hãy để Kafka Producer chạy chậm lại một chút để thầy cô thấy số lượng events tăng dần trên biểu đồ theo thời gian thực.

#### 4\. (Tùy chọn) Show Dữ liệu Gốc trong Database

Nếu thầy cô hỏi sâu "Dữ liệu lưu vào database trông như thế nào?", bạn dùng lệnh này:

  * **Cassandra:**
    ```bash
    kubectl exec -it cassandra-0 -n big-data-pipeline -- cqlsh -e "SELECT * FROM bigdata_pipeline.events LIMIT 5;"
    ```
  * **Giải thích:** "Đây là dữ liệu thô đã được chuẩn hóa và lưu trữ bền vững trong Cassandra."

-----

### 📝 Tóm tắt Kịch bản Demo:

1.  **Mở đầu:** "Hệ thống bao gồm các thành phần..." -\> Show **Terminal `kubectl get pods`**.
2.  **Input:** "Kafka Producer đang đọc file CSV từ Google Cloud Storage và bắn vào hệ thống..." -\> (Optional: Show log Producer).
3.  **Process:** "Spark Streaming đọc từ Kafka, tổng hợp dữ liệu..." -\> Show **Terminal Log Spark**.
4.  **Output:** "Kết quả cuối cùng được hiển thị tại đây..." -\> Show **Web Dashboard**.