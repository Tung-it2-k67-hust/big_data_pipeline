# 📅 **README - NHIỆM VỤ TUẦN 1-2: Setup & Code Cơ Bản**

## 🎓 **SINH VIÊN ĐÃ HỌC LÝ THUYẾT - BÂY GIỜ CODE THỰC TẾ!**

**Thời gian**: Tuần 1-2 (2 tuần để setup và code cơ bản)  
**Mục tiêu**: Setup environment hoàn chỉnh, code được basic functionality  
**Tâm lý**: Đã hiểu lý thuyết, giờ tập trung thực hành!

---

## 👥 **NHIỆM VỤ CODE THỰC TẾ THEO VAI TRÒ**

### **1. DATA INGESTION ENGINEER (ANH TÁI)**

#### **Tuần 1: Kafka Producer Cơ Bản**
- [ ] Clone project và setup Python venv
- [ ] Chạy `docker-compose up` để start Kafka cluster
- [ ] Tạo Kafka Producer script đơn giản (`kafka-producer/src/producer.py`)
- [ ] Implement CSV reader cho `archive/full_dataset.csv`
- [ ] Send sample data (5-10 records) vào Kafka topic `football-matches`
- [ ] Test với Kafka console consumer

#### **Tuần 2: Producer Hoàn Chỉnh**
- [ ] Add error handling cho CSV parsing
- [ ] Convert football data thành JSON format
- [ ] Implement batch sending (nhiều records cùng lúc)
- [ ] Add logging và monitoring cơ bản
- [ ] Test với full dataset (100 records)
- [ ] Document setup steps

**Deliverables:**
- ✅ Kafka Producer script working
- ✅ Data gửi được vào Kafka topic
- ✅ JSON format đúng chuẩn
- ✅ Error handling cơ bản

---

### **2. DATA PROCESSING ENGINEER (LONG)**

#### **Tuần 1: Spark Streaming Setup**
- [ ] Clone project và setup Python venv
- [ ] Cài đặt PySpark dependencies
- [ ] Tạo Spark Streaming job template
- [ ] Connect với Kafka topic `football-matches`
- [ ] Consume và print messages từ Kafka
- [ ] Test connection với Elasticsearch và Cassandra

#### **Tuần 2: Basic Processing Logic**
- [ ] Parse JSON messages từ Kafka
- [ ] Implement basic aggregations (count matches, sum goals)
- [ ] Setup output format cho storage systems
- [ ] Add data validation (check required fields)
- [ ] Test end-to-end với sample data
- [ ] Debug và fix connection issues

**Deliverables:**
- ✅ Spark Streaming job running
- ✅ Consume được data từ Kafka
- ✅ Basic processing logic working
- ✅ Connections to storage systems

---

### **3. DATA STORAGE ENGINEER (QUAN)**

#### **Tuần 1: Storage Systems Setup**
- [ ] Clone project và setup environment
- [ ] Chạy `docker-compose up` cho ES + Cassandra
- [ ] Test connections với cả hai systems
- [ ] Create basic indices cho Elasticsearch
- [ ] Setup Cassandra keyspace `football_analytics`
- [ ] Test basic CRUD operations

#### **Tuần 2: Schema & Testing**
- [ ] Design Elasticsearch mappings cho football data
- [ ] Create Cassandra tables cho match data
- [ ] Implement data insertion scripts
- [ ] Test với sample football records
- [ ] Setup basic monitoring (health checks)
- [ ] Document schema decisions

**Deliverables:**
- ✅ Elasticsearch indices created
- ✅ Cassandra keyspace/tables ready
- ✅ Sample data inserted successfully
- ✅ Basic monitoring working

---

### **4. DATA VISUALIZATION ENGINEER (TUẤN ĐẠT)**

#### **Tuần 1: Visualization Tools Setup**
- [ ] Clone project và setup Python venv
- [ ] Chạy Kibana và Streamlit containers
- [ ] Test connections với Elasticsearch
- [ ] Create Kibana index patterns
- [ ] Setup basic Streamlit app structure
- [ ] Test data retrieval từ ES

#### **Tuần 2: Basic Dashboards**
- [ ] Create Kibana visualizations (tables, bar charts)
- [ ] Build Streamlit dashboard với sample data
- [ ] Implement data filtering và search
- [ ] Add basic UI components (dropdowns, buttons)
- [ ] Test với real football data
- [ ] Style và layout improvements

**Deliverables:**
- ✅ Kibana visualizations working
- ✅ Streamlit dashboard functional
- ✅ Data display correctly
- ✅ Basic interactivity

---

### **5. PROJECT MANAGER (TUNG)**

#### **Tuần 1: Team Coordination**
- [ ] Setup communication channels (Teams/Slack)
- [ ] Help team members với setup issues
- [ ] Create GitHub project board
- [ ] Monitor daily progress
- [ ] Resolve technical blockers

#### **Tuần 2: Progress Tracking**
- [ ] Weekly check-in meetings
- [ ] Track code commits và functionality
- [ ] Help với integration issues
- [ ] Update project documentation
- [ ] Prepare cho tuần 3-4

**Deliverables:**
- ✅ Team communication established
- ✅ Progress tracking system
- ✅ Blockers resolved quickly
- ✅ Documentation updated

---

## 🔄 **WEEKLY CHECK-IN (Mỗi Thứ 7)**

### **Format thực tế:**
1. **Code gì tuần này?** (show working features)
2. **Gặp bug gì?** (technical issues)
3. **Cần help gì tuần sau?** (specific support needed)
4. **Demo gì được?** (show progress)

### **Focus:**
- **Working code** over perfect code
- **Problem solving** over theory
- **Team collaboration** over individual work

---

## ✅ **SUCCESS CRITERIA - CODE WORKING**

### **Technical:**
- [ ] Environment setup hoàn chỉnh
- [ ] Basic functionality working
- [ ] Data flow từ ingestion → processing → storage → visualization
- [ ] No critical bugs blocking progress

### **Code Quality:**
- [ ] Code chạy được không lỗi
- [ ] Basic error handling
- [ ] Logging và debugging
- [ ] Documentation cho setup

### **Team:**
- [ ] Help nhau debug code
- [ ] Share solutions cho common issues
- [ ] Celebrate working features
- [ ] Positive coding experience

---

## 💡 **CODING TIPS CHO TUẦN 1-2**

### **Start Small:**
- **Hello World First**: Test connections trước
- **Sample Data**: Dùng 5-10 records để test
- **Print Debug**: In ra console để check data flow
- **One Feature**: Hoàn thành 1 chức năng rồi mới làm tiếp

### **Debugging:**
- **Check Logs**: Xem Docker logs, application logs
- **Test Connections**: Verify network connectivity
- **Validate Data**: Print data tại mỗi step
- **Ask Team**: Stuck thì hỏi ngay, đừng chật vật lâu

### **Best Practices:**
- **Commit Often**: Code chạy được thì commit
- **Document Setup**: Ghi lại steps để team follow
- **Test Early**: Test ngay khi code xong
- **Clean Code**: Comment và format code

---

## 🚨 **COMMON ISSUES & SOLUTIONS**

### **Docker Issues:**
- **Port conflicts**: Change ports in docker-compose.yml
- **Memory issues**: Increase Docker memory limit
- **Network issues**: Restart Docker daemon

### **Kafka Issues:**
- **Connection refused**: Check Kafka broker address
- **Topic not found**: Create topic manually
- **Messages not sending**: Check producer configuration

### **Elasticsearch Issues:**
- **Index not found**: Create index first
- **Mapping errors**: Check data types
- **Connection timeout**: Verify ES cluster health

### **Code Issues:**
- **Import errors**: Check Python path và venv
- **Syntax errors**: Use IDE linting
- **Logic errors**: Add print statements để debug

---

## 📋 **CHECKLIST HOÀN THÀNH**

### **End of Week 2:**
- [ ] Environment fully setup
- [ ] Basic code working end-to-end
- [ ] Data flows between components
- [ ] Team can demo working features
- [ ] Ready for advanced development Week 3-4

---

**🎯 TUẦN 1-2: ĐÃ HỌC LÝ THUYẾT - BÂY GIỜ CODE THỰC TẾ!** 🚀💻</content>
<parameter name="filePath">d:\2025.1_monhoc\big_data_pipeline\docs\README_Week1-2_Student.md