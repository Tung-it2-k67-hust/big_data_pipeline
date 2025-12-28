# 🎬 KỊCH BẢN QUAY VIDEO DEMO ĐỒ ÁN (GKE)

**Mục tiêu:** Chứng minh hệ thống Big Data Pipeline đã được deploy thành công trên Google Kubernetes Engine (GKE) và bạn có toàn quyền kiểm soát, vận hành hệ thống từ máy cá nhân.

**Thời lượng dự kiến:** 3 - 5 phút.

---

## 🛠️ PHẦN 1: CHUẨN BỊ TRƯỚC KHI BẤM RECORD

1.  **Terminal (VS Code hoặc PowerShell):**
    *   Đã login vào GKE: `gcloud container clusters get-credentials ...`
    *   Gõ sẵn lệnh (nhưng chưa Enter): `kubectl get pods -n big-data-pipeline`
2.  **Trình duyệt Web:** Mở sẵn các tab sau (dùng External IP):
    *   Streamlit Dashboard
    *   Kafka UI
    *   Kibana (Optional)
    *   Google Cloud Console (Trang Workloads - Optional để show trực quan)
3.  **Tâm thế:** Bình tĩnh, nói to, rõ ràng.

---

## 🎥 PHẦN 2: KỊCH BẢN CHI TIẾT (ACTION & SCRIPT)

### 1️⃣ Mở đầu & Giới thiệu (30s)

*   **Hành động:** Quay màn hình Terminal.
*   **Lời thoại:**
    > "Chào thầy và các bạn. Em là [Tên Bạn]. Sau đây em xin demo quá trình vận hành hệ thống Big Data Pipeline xử lý dữ liệu bóng đá Real-time, được deploy trên Google Kubernetes Engine (GKE)."

### 2️⃣ Chứng minh Hạ tầng & Quyền kiểm soát (QUAN TRỌNG NHẤT - 1.5 phút)

*   **Hành động 1:** Show context kết nối.
    *   Gõ: `kubectl config current-context`
    *   **Lời thoại:** "Hiện tại, terminal trên máy local của em đang kết nối trực tiếp tới Cluster GKE trên Cloud."

*   **Hành động 2:** Show các Pods đang chạy.
    *   Gõ: `kubectl get pods -n big-data-pipeline`
    *   **Lời thoại:** "Đây là toàn bộ các services trong pipeline đang ở trạng thái Running, bao gồm Kafka, Spark Streaming, Cassandra, Elasticsearch và các công cụ monitoring."

*   **Hành động 3 (Điểm nhấn):** **Thực hiện Scale để chứng minh Live Control.**
    *   Gõ: `kubectl scale deployment spark-streaming --replicas=2 -n big-data-pipeline`
    *   Ngay sau đó gõ: `kubectl get pods -n big-data-pipeline -w` (hoặc watch)
    *   **Lời thoại:** "Để chứng minh khả năng điều khiển hệ thống real-time, em sẽ thực hiện scale Spark Streaming từ 1 lên 2 replicas ngay lập tức.
    *   *(Chờ 5-10s thấy Pod mới chuyển sang Running)* -> "Như thầy thấy, Kubernetes đã ngay lập tức khởi tạo thêm một worker Spark mới theo lệnh điều khiển của em."

### 3️⃣ Chứng minh Dữ liệu Real-time (Logs) (1 phút)

*   **Hành động 1:** Check log Kafka Producer.
    *   Gõ: `kubectl logs -l app=kafka-producer -n big-data-pipeline --tail=20`
    *   **Lời thoại:** "Kiểm tra logs của Kafka Producer, hệ thống đang giả lập gửi dữ liệu trận đấu liên tục vào topic."

*   **Hành động 2:** Check log Spark Streaming.
    *   Gõ: `kubectl logs -l app=spark-streaming -n big-data-pipeline --tail=50`
    *   **Lời thoại:** "Chuyển sang Spark Streaming, logs cho thấy Spark đang xử lý từng Batch dữ liệu, tính toán và ghi xuống Database thành công."

### 4️⃣ Show Kết quả trên Web UI (1 phút)

*   **Hành động:** Chuyển sang trình duyệt Chrome/Edge.

*   **Tab 1: Kafka UI**
    *   Show topic `football-stream`, message in/sec nhảy số.
    *   **Lời thoại:** "Trên giao diện Kafka UI, ta thấy throughput dữ liệu đang đi vào ổn định."

*   **Tab 2: Streamlit Dashboard**
    *   Bấm nút "Rerun" hoặc để Auto-refresh.
    *   **Lời thoại:** "Và đây là kết quả cuối cùng trên Dashboard. Biểu đồ được cập nhật real-time từ dữ liệu mà Spark vừa xử lý và lưu vào Elasticsearch."

### 5️⃣ Kết thúc (30s)

*   **Hành động:** Quay lại Terminal hoặc màn hình kiến trúc.
*   **Lời thoại:**
    > "Vừa rồi là demo chứng minh hệ thống hoạt động hoàn chỉnh trên môi trường Cloud Production. Cảm ơn thầy đã theo dõi."

---

## 📝 CHEAT SHEET (LỆNH COPY PASTE NHANH)

Để tránh gõ sai khi quay, bạn có thể copy paste các lệnh này:

**1. Kiểm tra kết nối:**
```bash
kubectl config current-context
```

**2. Xem danh sách Pods:**
```bash
kubectl get pods -n big-data-pipeline
```

**3. Scale Spark (Hành động "ăn tiền"):**
```bash
kubectl scale deployment spark-streaming --replicas=2 -n big-data-pipeline
```
*(Sau khi quay xong nhớ scale về 1: `kubectl scale deployment spark-streaming --replicas=1 -n big-data-pipeline`)*

**4. Xem Log Producer:**
```bash
kubectl logs -l app=kafka-producer -n big-data-pipeline --tail=20
```

**5. Xem Log Spark:**
```bash
kubectl logs -l app=spark-streaming -n big-data-pipeline --tail=50
```

**6. Lấy lại IP Web UI (nếu quên):**
```bash
kubectl get svc -n big-data-pipeline
```

---

## 💡 MẸO NHỎ

*   **Font chữ Terminal:** Nên phóng to lên một chút (Ctrl +) để thầy dễ nhìn.
*   **Dọn dẹp Desktop:** Tắt các cửa sổ chat, facebook để video trông chuyên nghiệp.
*   **Lỗi thì sao?** Nếu gõ lệnh bị lỗi, cứ bình tĩnh gõ lại hoặc cắt bỏ đoạn đó khi edit video. Quan trọng là phong thái tự tin.