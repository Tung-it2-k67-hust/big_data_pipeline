# README - Kỹ Sư Data Ingestion

## 👋 Chào bạn! Bạn là Kỹ Sư Data Ingestion

Bạn chịu trách nhiệm về việc thu thập và gửi dữ liệu vào hệ thống. Bạn là người khởi đầu của toàn bộ pipeline.

## 📥 Đầu Vào Của Bạn

### Nguồn Dữ Liệu
- **File dữ liệu gốc**: `D:\2025.1_monhoc\big_data_pipeline\archive\full_dataset.csv`
- **Định dạng**: CSV chứa dữ liệu các trận bóng đá
- **Cấu trúc dữ liệu**:
  - Date: Ngày diễn ra trận đấu
  - HomeTeam, AwayTeam: Tên đội nhà và đội khách
  - FTHG, FTAG: Bàn thắng cuối trận đội nhà/đội khách
  - FTR: Kết quả cuối trận (H/D/A)
  - HTHG, HTAG: Bàn thắng hiệp 1 đội nhà/đội khách
  - HTR: Kết quả hiệp 1
  - HS, AS: Tổng số cú sút đội nhà/đội khách
  - HST, AST: Cú sút trúng đích đội nhà/đội khách
  - HF, AF: Số lỗi phạm đội nhà/đội khách
  - HC, AC: Phạt góc đội nhà/đội khách
  - HY, AY: Thẻ vàng đội nhà/đội khách
  - HR, AR: Thẻ đỏ đội nhà/đội khách
  - PSH, PSD, PSA: Tỷ lệ kèo Pinnacle (Home/Draw/Away)
  - Div: Tên giải đấu

## 🔧 Những Việc Bạn Cần Làm

### 1. Setup Môi Trường
```bash
# Kích hoạt virtual environment chung
.\venv\Scripts\activate.ps1

# Di chuyển vào thư mục kafka-producer
cd kafka-producer
```

### 2. Cấu Hình Kafka Producer
- **File chính**: `src/producer.py`
- **Cấu hình kết nối**:
  - Kafka Bootstrap Servers: `kafka:9092` (Docker) hoặc `localhost:9092` (local)
  - Topic: `football-matches`
  - Tốc độ gửi: 1 trận đấu/giây (có thể cấu hình)

### 3. Chạy Data Producer
```bash
# Trong môi trường Docker Compose
docker-compose up -d kafka-producer

# Hoặc chạy local
python src/producer.py
```

### 4. Kiểm Tra Dữ Liệu
```bash
# Kiểm tra Kafka topic
kubectl exec -it kafka-0 -n big-data-pipeline -- kafka-console-consumer \
  --bootstrap-server localhost:9092 \
  --topic football-matches \
  --from-beginning
```

## 📤 Đầu Ra Của Bạn

### Dữ Liệu Gửi Đến
- **Đích đến**: Kafka topic `football-matches`
- **Định dạng**: JSON messages
- **Tốc độ**: Real-time streaming (1 trận đấu/second)
- **Độ tin cậy**: At-least-once delivery

### Thông Tin Truyền Cho Người Tiếp Theo
- **Người nhận**: Kỹ Sư Data Processing
- **Thông tin cần cung cấp**:
  - Kafka topic name: `football-matches`
  - Schema của dữ liệu JSON (football match data)
  - Tốc độ streaming hiện tại
  - Sample messages để test

## 🔍 Monitoring & Troubleshooting

### Các Vấn Đề Thường Gặp
1. **Kafka connection failed**: Kiểm tra Kafka cluster đang chạy
2. **Data format errors**: Validate CSV file format
3. **Performance issues**: Điều chỉnh batch size và rate limiting

### Logs Quan Trọng
```bash
# Xem logs producer
kubectl logs deployment/kafka-producer -n big-data-pipeline -f
```

## ✅ Tiêu Chí Hoàn Thành

- [ ] Producer chạy ổn định không lỗi
- [ ] Dữ liệu được gửi vào Kafka topic thành công
- [ ] Rate streaming đạt yêu cầu (1 event/sec)
- [ ] Schema dữ liệu được document rõ ràng
- [ ] Thông tin kết nối được truyền cho Data Processing Engineer

## 📞 Liên Hệ

Khi hoàn thành, báo cáo cho **Project Manager (Tung)** và cung cấp thông tin kết nối cho **Data Processing Engineer**.
