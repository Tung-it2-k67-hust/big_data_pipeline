# 🌐 Hướng Dẫn Sử Dụng Web UI - Big Data Pipeline

## 📋 Tổng Quan Các Web UI Có Sẵn

| Service | URL | Mục đích | Trạng thái |
|---------|-----|----------|------------|
| **Kafka UI** | http://localhost:8080 | Quản lý Kafka Topics, xem messages, consumer groups | ✅ Đã cấu hình |
| **Spark UI** | http://localhost:4040 | Xem Spark jobs, streaming statistics | ✅ Đã expose port |
| **Kibana** | http://localhost:5601 | Quản lý Elasticsearch, query data, tạo dashboards | ✅ Đã có sẵn |
| **Streamlit** | http://localhost:8501 | Dashboard analytics realtime | ✅ Đang chạy |
| **Prometheus** | http://localhost:9090 | Metrics & monitoring | ✅ Đã có sẵn |
| **Grafana** | http://localhost:3000 | Visualization & alerting | ✅ Đã có sẵn |

---

## 1️⃣ Kafka UI - Quản Lý Kafka Topics

### 📍 Truy cập: http://localhost:8080

### ✨ Chức năng chính:

#### **A. Xem Topics**
1. Vào tab **Topics** → Chọn **`data-stream`**
2. Bạn sẽ thấy:
   - **Messages**: Tổng số messages trong topic
   - **Partitions**: Số lượng partitions
   - **Replication Factor**: Số bản sao

#### **B. Xem Messages Realtime**
1. Click vào topic **`data-stream`**
2. Click tab **Messages**
3. Chọn **Live Mode** để xem messages đang được gửi realtime
4. Bạn sẽ thấy:
   ```json
   {
     "Date": "1993-08-14",
     "HomeTeam": "Liverpool",
     "AwayTeam": "Sheffield Weds",
     "FTHG": 2,
     "FTAG": 0,
     "FTR": "H"
   }
   ```

#### **C. Kiểm Tra Producer**
- Vào **Brokers** → Xem **Messages In/Sec**
- Nếu thấy số > 0 → Producer đang hoạt động ✅
- Nếu = 0 → Producer có vấn đề ❌

#### **D. Consumer Groups**
1. Vào tab **Consumers**
2. Tìm consumer group của Spark Streaming
3. Xem **Lag** (số messages chưa được consume)
   - Lag = 0 → Spark đang xử lý kịp ✅
   - Lag tăng cao → Spark xử lý chậm ❌

---

## 2️⃣ Spark UI - Xem Streaming Jobs

### 📍 Truy cập: http://localhost:4040

### ✨ Chức năng chính:

#### **A. Streaming Tab**
1. Click tab **Streaming**
2. Xem các metrics:
   - **Input Rate**: Số records/giây Spark nhận từ Kafka
     - Nên thấy ~1,666 records/sec (500 records mỗi 0.3s)
   - **Processing Time**: Thời gian xử lý mỗi batch
   - **Scheduling Delay**: Độ trễ scheduling

#### **B. Jobs Tab**
- Xem tất cả các jobs đã chạy
- Click vào job để xem chi tiết stages

#### **C. Executors Tab**
- Xem memory & CPU usage của Spark executors

### ⚠️ Lưu ý:
- **Spark UI chỉ available khi Spark đang chạy**
- Nếu không truy cập được:
  ```bash
  docker logs spark-streaming --tail 50
  ```
  Tìm dòng: `Bound SparkUI to 0.0.0.0, port 4040`

---

## 3️⃣ Kibana - Quản Lý Elasticsearch

### 📍 Truy cập: http://localhost:5601

### ✨ Chức năng chính:

#### **A. Dev Tools (Query Console)**
1. Vào **☰ Menu** → **Dev Tools**
2. Chạy query để xem data:
   ```json
   GET /football-matches/_count
   
   GET /football-matches/_search
   {
     "size": 10,
     "sort": [{"match_date": "desc"}]
   }
   ```

#### **B. Index Management**
1. Vào **☰ Menu** → **Stack Management** → **Index Management**
2. Xem index **`football-matches`**
3. Kiểm tra:
   - **Docs count**: Số documents
   - **Store size**: Dung lượng
   - **Health**: yellow/green

#### **C. Discover (Explore Data)**
1. Vào **☰ Menu** → **Discover**
2. Tạo Data View:
   - Name: `Football Matches`
   - Index pattern: `football-matches`
   - Time field: `match_date`
3. Explore data với filters và time range

#### **D. Create Visualizations**
1. Vào **☰ Menu** → **Visualize Library**
2. Create visualization:
   - Pie chart: Match results distribution
   - Line chart: Matches over time
   - Bar chart: Top teams

---

## 4️⃣ Streamlit Dashboard - Analytics

### 📍 Truy cập: http://localhost:8501

### ✨ Tính năng:

- **Overview & Results**: Phân phối kết quả trận đấu
- **Attack Stats**: Thống kê shots, corners
- **Discipline**: Fouls, cards
- **Betting Market**: Odds analysis
- **Raw Data**: Xem và filter data với pagination

### 💡 Tips:
- Bật **Auto Refresh** để xem data update realtime
- Điều chỉnh **Refresh Interval** (5-60s)

---

## 5️⃣ Prometheus - Metrics Monitoring

### 📍 Truy cập: http://localhost:9090

### ✨ Queries hữu ích:

```promql
# CPU usage của containers
container_cpu_usage_seconds_total

# Memory usage
container_memory_usage_bytes

# Kafka metrics (nếu có exporter)
kafka_server_brokertopicmetrics_messagesin_total
```

---

## 6️⃣ Grafana - Dashboards

### 📍 Truy cập: http://localhost:3000
- **Username**: admin
- **Password**: admin (thay đổi lần đầu login)

### ✨ Setup:

1. **Add Data Source**:
   - Type: Prometheus
   - URL: http://prometheus:9090

2. **Import Dashboards**:
   - Docker monitoring
   - Kafka monitoring
   - System metrics

---

## 🔧 Troubleshooting

### ❌ Kafka UI không hiện data
**Kiểm tra:**
```bash
docker logs kafka-ui --tail 50
docker logs kafka --tail 50
```

**Fix:**
```bash
docker-compose restart kafka-ui
```

### ❌ Spark UI không truy cập được
**Lý do**: Spark container chưa khởi động hoặc đang restart

**Fix:**
```bash
docker logs spark-streaming --tail 100
docker-compose restart spark-streaming
```

### ❌ Kibana không load
**Lý do**: Elasticsearch chưa sẵn sàng

**Fix:**
```bash
# Kiểm tra Elasticsearch
curl http://localhost:9200/_cluster/health

# Restart Kibana
docker-compose restart kibana
```

---

## 📊 Demo Workflow - Kiểm Tra Pipeline Hoạt Động

### Bước 1: Kafka UI
1. Mở http://localhost:8080
2. Vào **Topics** → **data-stream**
3. Xem **Messages In/Sec** > 0 ✅

### Bước 2: Spark UI
1. Mở http://localhost:4040
2. Vào **Streaming** tab
3. Xem **Input Rate** ~1,666 records/sec ✅

### Bước 3: Kibana
1. Mở http://localhost:5601/app/dev_tools
2. Chạy: `GET /football-matches/_count`
3. Thấy count tăng dần ✅

### Bước 4: Streamlit
1. Mở http://localhost:8501
2. Bật **Auto Refresh**
3. Xem số liệu update realtime ✅

---

## 🚀 Deploy lên GKE - Port Forwarding

Khi deploy lên GKE, dùng `kubectl port-forward` để truy cập UI:

```bash
# Kafka UI
kubectl port-forward service/kafka-ui 8080:8080 -n big-data-pipeline

# Spark UI
kubectl port-forward deployment/spark-streaming 4040:4040 -n big-data-pipeline

# Kibana
kubectl port-forward service/kibana 5601:5601 -n big-data-pipeline

# Streamlit
kubectl port-forward service/streamlit 8501:8501 -n big-data-pipeline
```

Sau đó truy cập như local: `http://localhost:8080`, v.v.

---

## 📝 Tóm Tắt Quick Access

```bash
# Mở tất cả UI trong browser
start http://localhost:8080   # Kafka UI
start http://localhost:4040   # Spark UI  
start http://localhost:5601   # Kibana
start http://localhost:8501   # Streamlit
start http://localhost:9090   # Prometheus
start http://localhost:3000   # Grafana
```

---

**Chúc bạn demo thành công! 🎉**
