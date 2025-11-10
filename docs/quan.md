# README - Kỹ Sư Data Visualization

## 👋 Chào bạn! Bạn là Kỹ Sư Data Visualization

Bạn chịu trách nhiệm tạo dashboards và visualizations để hiển thị insights từ dữ liệu đã xử lý.

## 📥 Đầu Vào Của Bạn

### Nguồn Dữ Liệu
- **Từ**: Kỹ Sư Data Storage
- **Elasticsearch**:
  - Indices: `es`, `football-aggregated`
  - Endpoint: `elasticsearch:9200`
- **Cassandra**:
  - Keyspace: `football_analytics`
  - Endpoint: `cassandra:9042`

## 🔧 Những Việc Bạn Cần Làm

### 1. Setup Kibana Dashboards

#### Kết Nối Elasticsearch
```bash
# Truy cập Kibana
# Docker: http://localhost:5601
# K8s: http://localhost:30561

# Tạo index patterns
# - events* cho raw data
# - events-aggregated* cho aggregated data
```

#### Tạo Visualizations
- **Match results**: Thống kê thắng/thua/hòa theo đội
- **Goal analysis**: Phân tích bàn thắng, sút trúng đích
- **League performance**: Hiệu suất các giải đấu theo thời gian
- **Team statistics**: Thống kê chi tiết từng đội (fouls, cards, corners)
- **Betting odds**: Phân tích tỷ lệ kèo và kết quả thực tế
- **Season trends**: Xu hướng theo mùa giải

### 2. Setup Streamlit Dashboard

#### Cấu Hình Kết Nối
```bash
# Kích hoạt virtual environment
.\venv\Scripts\activate.ps1

# Di chuyển vào thư mục dashboard
cd streamlit-dashboard
```

#### Phát Triển Dashboard
- **File chính**: `app.py`
- **Libraries**: Streamlit, Plotly, Pandas, Elasticsearch client
- **Features cần có**:
  - Live match results và statistics
  - Team performance comparisons
  - League standings và trends
  - Betting odds analysis
  - Interactive charts cho match analysis
  - Historical data exploration

#### Chạy Dashboard
```bash
# Local development
streamlit run app.py

# Docker
docker-compose up -d streamlit

# K8s
kubectl port-forward svc/streamlit 8501:8501 -n big-data-pipeline
```

### 3. Tạo Custom Analytics

#### Query Patterns
```python
# Elasticsearch queries
from elasticsearch import Elasticsearch
es = Elasticsearch(['elasticsearch:9200'])

# Team performance by league
query = {
    "aggs": {
        "team_performance": {
            "terms": {"field": "HomeTeam"},
            "aggs": {"avg_goals": {"avg": {"field": "FTHG"}}}
        }
    }
}
```

#### Cassandra Analytics
```python
# Cassandra queries
from cassandra.cluster import Cluster
cluster = Cluster(['cassandra'])
session = cluster.connect('football_analytics')

# Recent matches by league
query = "SELECT * FROM matches WHERE div=? LIMIT 100 ALLOW FILTERING"
```

## 📤 Đầu Ra Của Bạn

### Dashboards Hoàn Chỉnh
- **Kibana**: Production-ready dashboards với:
  - Real-time monitoring views
  - Business intelligence reports
  - Custom visualizations
  - Saved searches và filters

- **Streamlit**: Interactive web dashboard với:
  - Live data updates
  - Custom analytics
  - Export capabilities
  - User-friendly interface

### Thông Tin Truyền Cho Người Tiếp Theo
- **Người nhận**: Project Manager (Tung) - báo cáo hoàn thành
- **Thông tin cần cung cấp**:
  - Dashboard URLs và access credentials
  - Key metrics và KPIs
  - User guide cho business users
  - Maintenance procedures

## 🔍 Monitoring & Troubleshooting

### Kibana Issues
```bash
# Check Kibana logs
kubectl logs deployment/kibana -n big-data-pipeline

# Verify Elasticsearch connection
curl http://localhost:5601/api/status
```

### Streamlit Issues
```bash
# Check app logs
kubectl logs deployment/streamlit -n big-data-pipeline

# Test connectivity
curl http://localhost:8501/healthz
```

### Performance Optimization
- **Query optimization**: Use aggregations thay vì raw queries
- **Caching**: Implement data caching cho real-time views
- **Pagination**: Handle large datasets efficiently

## ✅ Tiêu Chí Hoàn Thành

- [ ] Kibana dashboards được tạo và configured
- [ ] Streamlit dashboard chạy ổn định
- [ ] Real-time data visualization hoạt động
- [ ] Business metrics được hiển thị rõ ràng
- [ ] User interface intuitive và responsive
- [ ] Documentation cho end users
- [ ] Performance optimized cho concurrent users

## 📞 Liên Hệ

Khi hoàn thành, báo cáo cho **Project Manager (Tung)** với demo của các dashboards và hướng dẫn sử dụng.
