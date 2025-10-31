# 📋 Danh Sách README Theo Vai Trò

Dự án Big Data Pipeline được chia thành 5 vai trò chính, mỗi vai trò có README riêng để hướng dẫn công việc cụ thể.

## 👥 Các Vai Trò Và File README

### 1. **Data Ingestion Engineer**
- **File**: `docs/README_Data_Ingestion_Engineer.md`
- **Trách nhiệm**: Thu thập dữ liệu từ CSV vào Kafka
- **Đầu vào**: `archive/full_dataset.csv`
- **Đầu ra**: Kafka topic `data-stream`

### 2. **Data Processing Engineer**
- **File**: `docs/README_Data_Processing_Engineer.md`
- **Trách nhiệm**: Xử lý real-time với Spark Streaming
- **Đầu vào**: Kafka topics từ Ingestion Engineer
- **Đầu ra**: Dữ liệu processed vào Elasticsearch + Cassandra

### 3. **Data Storage Engineer**
- **File**: `docs/README_Data_Storage_Engineer.md`
- **Trách nhiệm**: Quản lý Elasticsearch + Cassandra
- **Đầu vào**: Processed data từ Processing Engineer
- **Đầu ra**: Storage systems optimized và healthy

### 4. **Data Visualization Engineer**
- **File**: `docs/README_Data_Visualization_Engineer.md`
- **Trách nhiệm**: Tạo dashboards Kibana + Streamlit
- **Đầu vào**: Stored data từ Storage Engineer
- **Đầu ra**: Dashboards hoàn chỉnh cho business users

### 5. **Project Manager (Tung)**
- **File**: `docs/README_Project_Manager_Tung.md`
- **Trách nhiệm**: Giám sát tổng thể dự án
- **Công việc**: Điều phối team, theo dõi tiến độ, quản lý risks

## 🔄 Data Flow Pipeline

```
Data Ingestion Engineer
        ↓
Data Processing Engineer
        ↓
Data Storage Engineer
        ↓
Data Visualization Engineer
        ↓
Project Manager (Review & Sign-off)
```

## 📚 Cách Sử Dụng

1. **Mỗi engineer** đọc file README của mình để hiểu nhiệm vụ
2. **Làm việc theo thứ tự** từ Ingestion → Processing → Storage → Visualization
3. **Project Manager** giám sát và điều phối toàn bộ process
4. **Báo cáo tiến độ** daily/weekly theo hướng dẫn trong từng file

## 🎯 Mục Tiêu Chung

- Xây dựng hệ thống Big Data Pipeline hoàn chỉnh
- Xử lý real-time dữ liệu e-commerce
- Dual storage với Elasticsearch + Cassandra
- Dashboards cho business intelligence
- Production-ready với monitoring và scaling

---

**Chúc team thành công!** 🚀