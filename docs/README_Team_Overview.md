# 📋 Danh Sách README Theo Vai Trò

Dự án Big Data Pipeline được chia thành 5 vai trò chính, mỗi vai trò có README riêng để hướng dẫn công việc cụ thể.

## 👥 Các Vai Trò Và File README

### 1. **Data Ingestion Engineer**
- **File**: `docs/README_Data_Ingestion_Engineer.md`
- **Trách nhiệm**: Thu thập dữ liệu từ CSV vào Kafka
- **Đầu vào**: `archive/full_dataset.csv`
- **Đầu ra**: Kafka topic `es`

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
2. **Đã học lý thuyết** - giờ tập trung CODE THỰC TẾ
3. **Làm việc PARALLEL** theo kế hoạch tuần trong `QUICK_START_STUDENT.md`
4. **Project Manager** hỗ trợ coding và debug
5. **Báo cáo tiến độ** linh hoạt, focus working code

## 📅 **KẾ HOẠCH CHO SINH VIÊN - ĐÃ HỌC LÝ THUYẾT**

### **Tuần 1-2: Code Cơ Bản**
- **Tất cả**: Code basic functionality, không cần học lý thuyết
- **Setup**: Environment hoàn chỉnh, basic code running
- **Goal**: Mỗi người có working code cho component của mình

### **Tuần 3-4: Development Nâng Cao**
- **Data Ingestion**: Optimize producer, error handling
- **Data Processing**: Advanced analytics, performance
- **Data Storage**: Schema optimization, monitoring
- **Data Visualization**: Rich dashboards, interactivity
- **Goal**: Features complete, ready for integration

### **Tuần 5-6: Integration & Testing**
- **Tất cả**: Kết nối components, comprehensive testing
- **Testing**: End-to-end, load testing, bug fixing
- **Goal**: System stable, performance optimized

### **Tuần 7-8: Production & Presentation**
- **Production**: Deploy to production environment
- **Documentation**: Complete docs, user guides
- **Presentation**: Demo for teachers, final report
- **Goal**: Project complete, defend successfully

## 🎯 Mục Tiêu Chung

- Xây dựng hệ thống Big Data Pipeline hoàn chỉnh
- Xử lý real-time dữ liệu **bóng đá** (football matches)
- Dual storage với Elasticsearch + Cassandra
- Dashboards cho **football analytics**
- **Quan trọng nhất: CODE WORKING và HỌC ĐƯỢC DEBUGGING!**

---

**Chúc team thành công!** 🚀