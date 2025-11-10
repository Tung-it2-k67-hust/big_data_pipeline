# README - Project Manager (Tung)

## 👑 Chào Boss! Bạn là Project Manager

Bạn chịu trách nhiệm tổng thể dự án Big Data Pipeline. Bạn là người giám sát, điều phối và đảm bảo dự án hoàn thành đúng tiến độ và chất lượng.

## 📋 Tổng Quan Dự Án

### Mục Tiêu
Xây dựng hệ thống Big Data Pipeline hoàn chỉnh để xử lý dữ liệu bóng đá real-time với:
- **Data Ingestion**: Thu thập dữ liệu trận đấu từ CSV vào Kafka
- **Data Processing**: Xử lý real-time với Spark Streaming
- **Data Storage**: Lưu trữ dual (Elasticsearch + Cassandra)
- **Data Visualization**: Dashboards cho football analytics
- **Monitoring**: Prometheus + Grafana

### Kiến Trúc Tổng Thể
```
CSV Dataset → Kafka Producer → Kafka → Spark Streaming → Elasticsearch + Cassandra → Kibana + Streamlit
                                                            ↓
                                                       Prometheus + Grafana
```

### Data Schema
**Football Match Data:**
- `Date`: Ngày diễn ra trận đấu (YYYY-MM-DD)
- `HomeTeam`: Tên đội chủ nhà
- `AwayTeam`: Tên đội khách
- `FTHG`: Số bàn thắng đội chủ nhà
- `FTAG`: Số bàn thắng đội khách
- `FTR`: Kết quả trận đấu (H/A/D)
- `HTHG`: Bàn thắng hiệp 1 đội chủ nhà
- `HTAG`: Bàn thắng hiệp 1 đội khách
- `HS`: Số cú sút đội chủ nhà
- `AS`: Số cú sút đội khách
- `HST`: Số cú sút trúng đích đội chủ nhà
- `AST`: Số cú sút trúng đích đội khách
- `HF`: Số pha phạm lỗi đội chủ nhà
- `AF`: Số pha phạm lỗi đội khách

## 👥 Team Structure

### 1. Data Ingestion Engineer
- **Nhiệm vụ**: Thu thập dữ liệu từ `archive/full_dataset.csv` vào Kafka
- **Đầu ra**: Kafka topic `es` với JSON messages
- **Thời gian**: 2-3 ngày

### 2. Data Processing Engineer
- **Nhiệm vụ**: Xử lý real-time với Spark Streaming
- **Đầu ra**: Dữ liệu processed lưu vào ES và Cassandra
- **Thời gian**: 4-5 ngày

### 3. Data Storage Engineer
- **Nhiệm vụ**: Quản lý và tối ưu hóa ES + Cassandra
- **Đầu ra**: Storage systems healthy và optimized
- **Thời gian**: 3-4 ngày

### 4. Data Visualization Engineer
- **Nhiệm vụ**: Tạo dashboards Kibana + Streamlit
- **Đầu ra**: Dashboards hoàn chỉnh cho business users
- **Thời gian**: 4-5 ngày

## 📅 Lộ Trình Triển Khai

### Phase 1: Infrastructure Setup (Ngày 1-2)
- [ ] Setup Kubernetes cluster
- [ ] Deploy base services (Kafka, Zookeeper)
- [ ] Configure monitoring (Prometheus, Grafana)

### Phase 2: Data Ingestion (Ngày 3-5)
- [ ] Data Ingestion Engineer hoàn thành Kafka Producer
- [ ] Test data flow vào Kafka
- [ ] Validate message format và rate

### Phase 3: Data Processing (Ngày 6-10)
- [ ] Data Processing Engineer hoàn thành Spark Streaming
- [ ] Deploy Elasticsearch và Cassandra
- [ ] Test end-to-end data flow

### Phase 4: Data Storage (Ngày 11-14)
- [ ] Data Storage Engineer optimize storage systems
- [ ] Setup backup và monitoring
- [ ] Performance testing

### Phase 5: Data Visualization (Ngày 15-19)
- [ ] Data Visualization Engineer tạo dashboards
- [ ] User acceptance testing
- [ ] Documentation hoàn chỉnh

### Phase 6: Production Ready (Ngày 20-22)
- [ ] Security hardening
- [ ] Load testing
- [ ] Deployment scripts
- [ ] Final documentation

---

## 📅 **KẾ HOẠCH CHO SINH VIÊN - CHẬM RÃI HỌC HỎI**

### **Tuần 1-2: Học Hỏi & Setup Cơ Bản**
**Focus**: Học công nghệ mới, setup environment thoải mái

#### **Data Ingestion Engineer (Anh Tài)**
- **Tuần 1**: Học Kafka concepts, chạy Docker containers
- **Tuần 2**: Setup development environment, thử import CSV
- **Goal**: Hiểu Kafka, có thể chạy infrastructure

#### **Data Processing Engineer (Long)**
- **Tuần 1**: Học Spark Streaming, PySpark basics
- **Tuần 2**: Setup environment, test connections
- **Goal**: Hiểu streaming concepts, environment ready

#### **Data Storage Engineer (Quan)**
- **Tuần 1**: Học Elasticsearch & Cassandra
- **Tuần 2**: Setup storage systems, basic queries
- **Goal**: Hiểu storage concepts, systems running

#### **Data Visualization Engineer (Tuấn Đạt)**
- **Tuần 1**: Học Kibana & Streamlit
- **Tuần 2**: Setup visualization tools, hello world
- **Goal**: Hiểu visualization, basic dashboards

#### **Project Manager (Tung)**
- **Tuần 1-2**: Setup communication, track learning progress
- **Goal**: Team coordination, support learning

---

### **Tuần 3-4: Development Cơ Bản**
**Focus**: Code cơ bản, không quá phức tạp

#### **Data Ingestion Engineer (Anh Tài)**
- **Tuần 3**: Kafka Producer đơn giản
- **Tuần 4**: Basic data ingestion, error handling
- **Goal**: Producer gửi được data vào Kafka

#### **Data Processing Engineer (Long)**
- **Tuần 3**: Spark Streaming job cơ bản
- **Tuần 4**: Basic aggregations, storage output
- **Goal**: Processing pipeline hoạt động

#### **Data Storage Engineer (Quan)**
- **Tuần 3**: Setup indices, keyspaces
- **Tuần 4**: Basic schemas, monitoring
- **Goal**: Storage systems optimized

#### **Data Visualization Engineer (Tuấn Đạt)**
- **Tuần 3**: Kibana visualizations
- **Tuần 4**: Streamlit dashboard cơ bản
- **Goal**: Basic dashboards working

#### **Project Manager (Tung)**
- **Tuần 3-4**: Monitor development, help debugging
- **Goal**: Team progress tracking

---

### **Tuần 5-6: Integration & Testing**
**Focus**: Kết nối components, fix bugs

#### **All Engineers**
- **Tuần 5**: Integration testing từng phần
- **Tuần 6**: End-to-end testing, bug fixes
- **Goal**: Pipeline hoạt động từ đầu đến cuối

#### **Project Manager (Tung)**
- **Tuần 5-6**: Coordinate testing, manage blockers
- **Goal**: Successful integration

---

### **Tuần 7-8: Production & Presentation**
**Focus**: Production deployment, báo cáo

#### **All Engineers**
- **Tuần 7**: Production deployment
- **Tuần 8**: Documentation, final presentation
- **Goal**: Project hoàn thành, demo được

#### **Project Manager (Tung)**
- **Tuần 7-8**: Final coordination, presentation prep
- **Goal**: Successful project delivery

---

## 🎓 **MINDSET CHO SINH VIÊN**

### **Learning First:**
- **Không stress deadline**: Học hỏi là quan trọng nhất
- **Ask questions freely**: Không biết thì hỏi
- **Trial & error**: Sai cũng được, học từ lỗi
- **Take breaks**: Mệt thì nghỉ, không ép buộc

### **Team Support:**
- **Help each other**: Share knowledge, pair programming
- **Celebrate progress**: Khen nhau khi đạt milestone
- **Be patient**: Mọi người học với tốc độ khác nhau
- **Positive attitude**: "We're learning together!"

### **Technical Approach:**
- **Start small**: Hello world trước, complex sau
- **Iterate**: Code chạy được rồi tối ưu
- **Debug together**: Stuck thì hỏi team
- **Learn from docs**: Documentation là bạn

---

## 🔄 **WEEKLY CHECK-IN (Mỗi Thứ 7) - KHÔNG ÁP LỰC**

### **Format thoải mái:**
1. **Tuần này học gì hay?** (chia sẻ kiến thức)
2. **Gặp khó khăn gì?** (technical/learning)
3. **Tuần sau focus gì?** (plan đơn giản)
4. **Cần support gì?** (từ team/PM/thầy cô)

### **Không mandatory:**
- Có thể skip nếu bận
- Không phạt nếu miss
- Tập trung encourage và support

---

## ✅ **SUCCESS CRITERIA - THỰC TẾ**

### **Learning Outcomes:**
- [ ] Học được công nghệ mới
- [ ] Biết cách debug và fix issues
- [ ] Hiểu được Big Data concepts
- [ ] Có thể explain project cho người khác

### **Technical Delivery:**
- [ ] Pipeline hoạt động end-to-end
- [ ] Code quality acceptable
- [ ] Documentation đầy đủ
- [ ] Demo được cho thầy cô

### **Team Experience:**
- [ ] Support nhau tốt
- [ ] Communication open
- [ ] Fun learning experience
- [ ] No one left behind

---

## 🚨 **SUPPORT SYSTEM**

### **Khi gặp khó:**
1. **Tự thử trước**: Google, documentation
2. **Hỏi team**: Slack/Teams
3. **PM help**: Tung coordinate
4. **Thầy cô**: Khi thực sự stuck

### **Time management:**
1. **Ưu tiên học**: Learning > deadline
2. **Break down tasks**: Chia nhỏ công việc
3. **Take breaks**: Học mệt thì nghỉ
4. **Adjust scope**: Nếu quá khó thì giảm requirement

---

## 🎯 **FINAL GOAL**

**KHÔNG PHẢI** hoàn thành project nhanh nhất  
**MÀ LÀ** học được nhiều thứ mới, teamwork tốt, và có project để defend!

---

**🎓 TEAM SINH VIÊN: HỌC HỎI CHẬM RÃI, THƯỞNG THỨC QUÁ TRÌNH! 📚🚀**

## 🔍 Giám Sát Tiến Độ

### Daily Standup Checklist
- [ ] **Data Ingestion**: Status của Kafka Producer
- [ ] **Data Processing**: Spark Streaming performance
- [ ] **Data Storage**: ES/Cassandra health metrics
- [ ] **Data Visualization**: Dashboard completion %
- [ ] **Infrastructure**: System monitoring alerts

### Key Metrics Theo Dõi
```bash
# System Health
kubectl get pods -n big-data-pipeline
kubectl get pvc -n big-data-pipeline

# Data Flow
kubectl exec -it kafka-0 -n big-data-pipeline -- kafka-consumer-groups --bootstrap-server localhost:9092 --group spark-streaming --describe

# Storage Health
curl http://localhost:9200/_cluster/health
kubectl exec -it cassandra-0 -n big-data-pipeline -- nodetool status
```

### Risk Management
- **High Risk**: Data loss, system downtime
- **Medium Risk**: Performance issues, integration problems
- **Low Risk**: UI/UX issues, documentation gaps

## 🛠️ Công Cụ Quản Lý

### Development Environment
```bash
# Shared virtual environment
.\venv\Scripts\activate.ps1

# Build all images
make build

# Deploy to k8s
make deploy

# Check status
make status
```

### Monitoring Dashboards
- **Grafana**: http://localhost:30300 (admin/admin)
- **Prometheus**: http://localhost:30909
- **Kibana**: http://localhost:30561
- **Streamlit**: http://localhost:30851

## 📊 Báo Cáo Tiến Độ

### Daily Reports
Mỗi ngày nhận báo cáo từ 4 engineers:
1. **Completed tasks** trong ngày
2. **Blockers/Issues** gặp phải
3. **Next steps** cho ngày mai
4. **Risk assessment** nếu có

### Weekly Reviews
- **Monday**: Sprint planning
- **Wednesday**: Mid-week check-in
- **Friday**: Sprint review + retrospective

## ✅ Tiêu Chí Thành Công

### Technical Requirements
- [ ] Data pipeline xử lý 1000+ trận đấu/minute
- [ ] Latency < 5 seconds từ ingestion đến visualization
- [ ] 99.9% uptime cho production
- [ ] Auto-scaling cho peak loads

### Business Requirements
- [ ] Real-time dashboards cho football analytics
- [ ] Historical data retention 30+ days
- [ ] Multi-region deployment capability
- [ ] Cost-effective scaling

### Quality Assurance
- [ ] Unit tests cho tất cả components
- [ ] Integration tests end-to-end
- [ ] Performance benchmarks documented
- [ ] Security audit passed

## 🚨 Emergency Procedures

### System Down
1. Check pod status: `kubectl get pods -n big-data-pipeline`
2. View logs: `kubectl logs <pod-name> -n big-data-pipeline`
3. Restart services: `kubectl rollout restart deployment/<name> -n big-data-pipeline`

### Data Loss
1. Check backups in persistent volumes
2. Restore from latest backup
3. Validate data integrity
4. Update monitoring alerts

## 📞 Communication Plan

### Internal Communication
- **Daily standups**: 9:00 AM via Teams/Slack
- **Issue escalation**: Immediate notification
- **Success celebration**: Team lunch khi milestone đạt

### External Communication
- **Stakeholders**: Weekly progress reports
- **Business users**: Demo sessions khi có major updates
- **DevOps team**: Infrastructure requirements

## 🎯 Success Metrics

- **On-time delivery**: 95%+ tasks completed đúng deadline
- **Quality score**: < 5% production bugs
- **Team satisfaction**: Average rating > 4/5
- **System performance**: Meet all SLAs
- **Documentation**: 100% coverage

---

**Remember**: "Fail fast, learn faster, deliver better!" 🚀
