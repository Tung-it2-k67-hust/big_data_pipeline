# README - Kỹ Sư Data Processing

## 👋 Chào bạn! Bạn là Kỹ Sư Data Processing

Bạn chịu trách nhiệm xử lý dữ liệu real-time từ Kafka và chuyển đổi thành dạng có thể lưu trữ và phân tích.

## 📥 Đầu Vào Của Bạn

### Nguồn Dữ Liệu
- **Từ**: Kỹ Sư Data Ingestion
- **Kafka Topic**: `data-stream`
- **Schema dữ liệu**:
```json
{
  "Date": "2024-01-01",
  "HomeTeam": "Manchester United",
  "AwayTeam": "Liverpool",
  "FTHG": 2,
  "FTAG": 1,
  "FTR": "H",
  "HTHG": 1,
  "HTAG": 0,
  "HTR": "H",
  "HS": 15,
  "AS": 12,
  "HST": 7,
  "AST": 5,
  "HF": 12,
  "AF": 15,
  "HC": 8,
  "AC": 5,
  "HY": 2,
  "AY": 3,
  "HR": 0,
  "AR": 0,
  "PSH": 2.5,
  "PSD": 3.2,
  "PSA": 3.0,
  "Div": "EPL"
}
```

## 🔧 Những Việc Bạn Cần Làm

### 1. Setup Môi Trường
```bash
# Kích hoạt virtual environment chung
.\venv\Scripts\activate.ps1

# Di chuyển vào thư mục spark-streaming
cd spark-streaming
```

### 2. Cấu Hình Spark Streaming
- **File chính**: `src/streaming_app.py`
- **Cấu hình kết nối**:
  - Kafka: `kafka:9092` (Docker) hoặc `localhost:9092` (local)
  - Elasticsearch: `elasticsearch:9200`
  - Cassandra: `cassandra:9042`, keyspace: `football_analytics`

### 3. Xử Lý Dữ Liệu
**Các phép biến đổi cần thực hiện:**
- Parse JSON messages từ Kafka
- Thêm timestamp processing
- Tính toán các metrics: total goals, shots accuracy, fouls ratio
- Tạo aggregations theo thời gian (1-minute windows)
- Aggregate theo league (Div), theo đội, theo mùa giải
- Tính toán win/loss/draw statistics
- Phân tích hiệu suất đội bóng

### 4. Chạy Spark Streaming
```bash
# Trong Docker Compose
docker-compose up -d spark-streaming

# Hoặc chạy local với packages
spark-submit --packages org.apache.spark:spark-sql-kafka-0-10_2.12:3.3.0,org.elasticsearch:elasticsearch-spark-30_2.12:8.4.3,com.datastax.spark:spark-cassandra-connector_2.12:3.3.0 src/streaming_app.py
```

## 📤 Đầu Ra Của Bạn

### Dữ Liệu Lưu Vào 2 Nơi

#### 1. Elasticsearch
- **Index raw data**: `events`
- **Index aggregated**: `events-aggregated`
- **Schema**: JSON documents với full-text search capability

#### 2. Cassandra
- **Keyspace**: `football_analytics`
- **Tables**:
  - `matches`: Raw match data với TTL 1 năm
  - `team_stats_by_league`: Thống kê đội theo giải đấu
  - `league_performance`: Hiệu suất giải đấu theo thời gian
  - `match_results`: Kết quả trận đấu theo ngày

### Thông Tin Truyền Cho Người Tiếp Theo
- **Người nhận**: Kỹ Sư Data Storage + Kỹ Sư Data Visualization
- **Thông tin cần cung cấp**:
  - Elasticsearch indices: `es`, `football-aggregated`
  - Cassandra keyspace: `football_analytics`
  - Schema của các tables (matches, team stats, league performance)
  - Sample queries để test

## 🔍 Monitoring & Troubleshooting

### Các Vấn Đề Thường Gặp
1. **Kafka consumer lag**: Kiểm tra consumer group status
2. **Spark job failures**: Check executor memory và cores
3. **Storage connection errors**: Verify ES và Cassandra endpoints

### Metrics Quan Trọng
```bash
# Check Spark streaming statistics
kubectl logs deployment/spark-streaming -n big-data-pipeline -f
```

## ✅ Tiêu Chí Hoàn Thành

- [ ] Spark streaming job chạy ổn định
- [ ] Dữ liệu được xử lý real-time từ Kafka
- [ ] Raw data được lưu vào Elasticsearch
- [ ] Aggregated data được lưu vào cả ES và Cassandra
- [ ] Schema và endpoints được document đầy đủ
- [ ] Thông tin kết nối được truyền cho Storage và Visualization Engineers

## 📞 Liên Hệ

Khi hoàn thành, báo cáo cho **Project Manager (Tung)** và cung cấp thông tin storage cho **Data Storage Engineer** và **Data Visualization Engineer**.
