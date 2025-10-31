# Architecture Overview

## System Components

### Data Ingestion Layer
- **Kafka Producer**: Generates synthetic e-commerce event data
  - Events: clicks, views, purchases, searches
  - Rate: Configurable (default 1 event/second)
  - Data includes: user_id, product_id, price, quantity, region, device

### Streaming Layer
- **Apache Kafka**: Distributed event streaming platform
  - Topic: data-stream
  - Partitions: Configurable
  - Replication: Single replica (configurable for production)

- **Apache Zookeeper**: Coordination service for Kafka
  - Manages Kafka cluster metadata
  - Leader election

### Processing Layer
- **Apache Spark Streaming**: Real-time data processing
  - Consumes from Kafka topics
  - Performs aggregations and transformations
  - Calculates revenue metrics
  - Time-windowed aggregations (1-minute windows)

### Storage Layer
- **Elasticsearch**: Document store and search engine
  - Index: events (raw data)
  - Index: events-aggregated (aggregated metrics)
  - Supports full-text search and analytics

### Visualization Layer
- **Kibana**: Elastic's visualization platform
  - Pre-built dashboards
  - Custom visualizations
  - Data exploration

- **Streamlit**: Custom Python dashboard
  - Real-time metrics
  - Interactive charts
  - Custom analytics

### Monitoring Layer
- **Prometheus**: Metrics collection
  - Scrapes metrics from all components
  - Time-series database
  - Alert manager

- **Grafana**: Metrics visualization
  - System dashboards
  - Performance monitoring
  - Alert visualization

## Data Flow

```
Producer → Kafka → Spark → Elasticsearch → Visualization
                                         ↓
                                    Monitoring
```

## Deployment Architecture

### Kubernetes Resources

1. **Namespace**: big-data-pipeline
   - Isolates all pipeline resources

2. **StatefulSets**:
   - Zookeeper (1 replica)
   - Kafka (1 replica, scalable)
   - Elasticsearch (1 replica, scalable)

3. **Deployments**:
   - Kafka Producer
   - Spark Streaming
   - Kibana
   - Streamlit
   - Prometheus
   - Grafana

4. **Services**:
   - Headless services for StatefulSets
   - NodePort services for external access

5. **Persistent Volumes**:
   - Zookeeper data
   - Kafka logs
   - Elasticsearch indices

## Scalability Considerations

### Horizontal Scaling
- **Kafka**: Increase replicas and partitions
- **Spark**: Add more Spark worker nodes
- **Elasticsearch**: Add more data nodes

### Vertical Scaling
- Adjust resource requests/limits in K8s manifests
- Increase heap sizes for JVM-based components

## High Availability

### Current Setup (Development)
- Single replica for each component
- Suitable for development and testing

### Production Recommendations
- 3+ Zookeeper nodes
- 3+ Kafka brokers
- 3+ Elasticsearch nodes
- 2+ Spark workers
- Load balancer for external services

## Security Considerations

### Current State
- No authentication/authorization (development)
- No encryption at rest or in transit

### Production Recommendations
- Enable Kafka SASL authentication
- Enable Elasticsearch X-Pack security
- Use TLS for all connections
- Implement RBAC in Kubernetes
- Use secrets management (HashiCorp Vault, etc.)
- Network policies for pod-to-pod communication

## Performance Tuning

### Kafka
- Adjust `log.retention.hours`
- Configure `num.partitions` based on throughput
- Tune `replica.lag.time.max.ms`

### Spark
- Configure executor memory and cores
- Adjust batch interval
- Tune checkpoint interval
- Configure shuffle partitions

### Elasticsearch
- Tune heap size (50% of available memory, max 32GB)
- Configure refresh interval
- Adjust number of shards and replicas
- Enable index lifecycle management
