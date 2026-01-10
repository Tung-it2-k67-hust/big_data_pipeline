# Hướng Dẫn Chạy Local (Docker Compose)

Tài liệu này hướng dẫn chi tiết cách chạy toàn bộ hệ thống Big Data Pipeline trên máy local sử dụng Docker Compose.

## 1. Yêu Cầu Hệ Thống (Prerequisites)

Trước khi bắt đầu, hãy đảm bảo máy tính của bạn đã cài đặt:

*   **Docker Desktop**: [Tải về tại đây](https://www.docker.com/products/docker-desktop)
*   **Git**: Để clone mã nguồn.
*   **RAM**: Tối thiểu 8GB (khuyến nghị 16GB vì chạy nhiều dịch vụ nặng như Kafka, Spark, Elasticsearch).

## 2. Cấu Trúc Dự Án

```
big_data_pipeline/
├── kafka-producer/          # Code Python tạo dữ liệu giả lập
├── spark-streaming/         # Code Spark xử lý dữ liệu
├── streamlit-dashboard/     # Code Dashboard hiển thị
├── docker-compose.yml       # File cấu hình chạy toàn bộ hệ thống
└── archive/                 # Chứa file dữ liệu full_dataset.csv
```

## 3. Các Bước Chạy Hệ Thống

### Bước 1: Clone Repository

Mở terminal (PowerShell hoặc CMD) và chạy:

```bash
git clone https://github.com/Tung-it2-k67-hust/big_data_pipeline.git
cd big_data_pipeline
```

### Bước 2: Chuẩn Bị Dữ Liệu

Đảm bảo file dữ liệu `full_dataset.csv` đã có trong thư mục `archive/`. Nếu chưa có, hãy tải về và đặt vào đó.

### Bước 3: Khởi Động Các Dịch Vụ

Chạy lệnh sau để build và khởi động tất cả các container:

```bash
docker-compose up -d --build
```

*   `-d`: Chạy ngầm (detached mode).
*   `--build`: Build lại các image nếu có thay đổi code.

Quá trình này có thể mất 5-10 phút trong lần đầu tiên để tải các image (Kafka, Spark, Elastic...) về máy.

### Bước 4: Kiểm Tra Trạng Thái

Kiểm tra xem các container đã chạy chưa:

```bash
docker-compose ps
```

Bạn sẽ thấy danh sách các dịch vụ như `zookeeper`, `kafka`, `spark-streaming`, `elasticsearch`, `kibana`, `streamlit`, v.v. Trạng thái nên là `Up`.

## 4. Truy Cập Các Dịch Vụ

Sau khi hệ thống khởi động thành công, bạn có thể truy cập các giao diện sau trên trình duyệt:

| Dịch Vụ | URL | Mô Tả |
| :--- | :--- | :--- |
| **Streamlit Dashboard** | [http://localhost:8501](http://localhost:8501) | Xem biểu đồ phân tích dữ liệu bóng đá. |
| **Kibana** | [http://localhost:5601](http://localhost:5601) | Quản lý và visualize dữ liệu trong Elasticsearch. |
| **Kafka UI** | [http://localhost:8080](http://localhost:8080) | Xem topic, message trong Kafka. |
| **Spark UI** | [http://localhost:4040](http://localhost:4040) | Xem job Spark đang chạy (chỉ khi job đang active). |
| **Grafana** | [http://localhost:3000](http://localhost:3000) | Giám sát hệ thống (User/Pass: admin/admin). |
| **Prometheus** | [http://localhost:9090](http://localhost:9090) | Thu thập metrics. |

## 5. Cách Hoạt Động

1.  **Kafka Producer**: Đọc file `archive/full_dataset.csv` và gửi từng dòng dữ liệu vào Kafka topic `football-stream`.
2.  **Spark Streaming**: Đọc dữ liệu từ Kafka topic `football-stream`, xử lý (tính toán, format), sau đó ghi xuống:
    *   **Cassandra**: Lưu trữ lâu dài.
    *   **Elasticsearch**: Lưu trữ để tìm kiếm và hiển thị lên Dashboard.
3.  **Streamlit Dashboard**: Query dữ liệu từ Elasticsearch và vẽ biểu đồ.

## 6. Dừng Hệ Thống

Khi không sử dụng nữa, hãy dừng và xóa các container để giải phóng tài nguyên:

```bash
docker-compose down
```

Nếu muốn xóa cả dữ liệu (volumes) để chạy lại từ đầu sạch sẽ:

```bash
docker-compose down -v
```

## 7. Xử Lý Sự Cố Thường Gặp

*   **Lỗi kết nối Elasticsearch**: Nếu Dashboard báo lỗi không kết nối được ES, hãy đợi thêm vài phút. Elasticsearch khởi động khá lâu.
*   **Lỗi Spark**: Nếu Spark container bị exit, hãy kiểm tra log: `docker-compose logs spark-streaming`.
*   **Không thấy dữ liệu trên Dashboard**:
    *   Kiểm tra Kafka Producer có đang chạy không: `docker-compose logs kafka-producer`.
    *   Kiểm tra Kafka UI (localhost:8080) xem có message vào topic `football-stream` không.

Chúc bạn thành công!
