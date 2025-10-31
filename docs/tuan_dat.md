# README - Kỹ Sư Data Storage

## 👋 Chào bạn! Bạn là Kỹ Sư Data Storage

Bạn chịu trách nhiệm quản lý và tối ưu hóa hệ thống lưu trữ dữ liệu (Elasticsearch + Cassandra).

## 📥 Đầu Vào Của Bạn

### Nguồn Dữ Liệu
- **Từ**: Kỹ Sư Data Processing
- **Elasticsearch**:
  - Indices: `football-matches` (raw), `football-aggregated` (processed)
  - Endpoint: `elasticsearch:9200`
- **Cassandra**:
  - Keyspace: `football_analytics`
  - Tables: matches, team_stats_by_league, league_performance, match_results
  - Endpoint: `cassandra:9042`

## 🔧 Những Việc Bạn Cần Làm

### 1. Setup Và Quản Lý Elasticsearch

#### Cấu Hình Cluster
```bash
# Kiểm tra cluster health
curl http://localhost:9200/_cluster/health?pretty

# Xem indices
curl http://localhost:9200/_cat/indices?v
```

#### Tối Ưu Hóa Performance
- **Heap size**: 50% RAM available (max 32GB)
- **Refresh interval**: Điều chỉnh cho write-heavy workload
- **Shards và replicas**: Cấu hình cho high availability
- **Index lifecycle**: Setup ILM policies

### 2. Setup Và Quản Lý Cassandra

#### Khởi Tạo Schema
```bash
# Kết nối vào Cassandra
kubectl exec -it cassandra-0 -n big-data-pipeline -- cqlsh

# Kiểm tra keyspace
DESCRIBE KEYSPACES;

# Kiểm tra tables
USE football_analytics;
DESCRIBE TABLES;
```

#### Tối Ưu Hóa Performance
- **JVM Heap**: 8GB-16GB cho production
- **Compaction Strategy**: STCS cho time-series football data
- **TTL Settings**: 1 năm cho match data (365 ngày)
- **Replication Factor**: Tăng lên 3 cho production
- **Partition Key**: Theo league và season để query hiệu quả

### 3. Monitoring Storage Systems

#### Elasticsearch Monitoring
```bash
# Cluster stats
curl http://localhost:9200/_cluster/stats?pretty

# Index stats
curl http://localhost:9200/events/_stats?pretty
```

#### Cassandra Monitoring
```bash
# Check node status
kubectl exec -it cassandra-0 -n big-data-pipeline -- nodetool status

# Table stats
kubectl exec -it cassandra-0 -n big-data-pipeline -- nodetool tablestats football_analytics.matches
```

## 📤 Đầu Ra Của Bạn

### Hệ Thống Storage Sẵn Sàng
- **Elasticsearch**: Cluster healthy, indices optimized
- **Cassandra**: Keyspace và tables sẵn sàng, schema validated
- **Performance**: Systems tuned cho workload hiện tại
- **Monitoring**: Metrics và alerts được setup

### Thông Tin Truyền Cho Người Tiếp Theo
- **Người nhận**: Kỹ Sư Data Visualization
- **Thông tin cần cung cấp**:
  - Elasticsearch endpoints và indices (football-matches, football-aggregated)
  - Cassandra contact points và keyspace (football_analytics)
  - Query patterns và best practices cho football analytics
  - Performance benchmarks
  - Monitoring dashboards access

## 🔍 Monitoring & Troubleshooting

### Elasticsearch Issues
```bash
# Check cluster health
curl http://localhost:9200/_cluster/health

# View error logs
kubectl logs deployment/elasticsearch -n big-data-pipeline
```

### Cassandra Issues
```bash
# Check node status
nodetool status

# Repair inconsistencies
nodetool repair

# View logs
kubectl logs cassandra-0 -n big-data-pipeline
```

### Performance Tuning
- **Elasticsearch**: Monitor query latency, indexing rate
- **Cassandra**: Monitor read/write latency, compaction stats

## ✅ Tiêu Chí Hoàn Thành

- [ ] Elasticsearch cluster healthy và optimized
- [ ] Cassandra cluster healthy với schema đúng
- [ ] Data được lưu trữ thành công từ processing layer
- [ ] Performance metrics đạt yêu cầu
- [ ] Monitoring và alerting được setup
- [ ] Query patterns được document
- [ ] Access info được cung cấp cho Visualization Engineer

## 📞 Liên Hệ

Khi hoàn thành, báo cáo cho **Project Manager (Tung)** và cung cấp storage access info cho **Data Visualization Engineer**.
