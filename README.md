# Big Data Analytics Pipeline on Kubernetes

A complete big data analytics and visualization pipeline deployed on Kubernetes. This project demonstrates a scalable, real-time data processing system using modern big data technologies.

## 🏗️ Architecture

```
┌─────────────────┐
│ Kafka Producer  │ ──► Generate sample data
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Kafka Cluster   │ ──► Message broker for data streaming
│   + Zookeeper   │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Spark Streaming │ ──► Real-time data processing
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Elasticsearch   │ ──► Data storage and indexing
└────────┬────────┘
         │
         ├──► Kibana (Visualization)
         │
         └──► Streamlit (Custom Dashboard)
```

## 📦 Components

- **Kafka Producer**: Python-based data generator that produces sample e-commerce events
- **Kafka + Zookeeper**: Distributed streaming platform for data ingestion
- **Spark Streaming**: Real-time data processing engine for analytics
- **Elasticsearch**: Search and analytics engine for data storage
- **Kibana**: Data visualization and exploration tool
- **Streamlit**: Custom Python dashboard for real-time analytics
- **Prometheus + Grafana**: Monitoring and alerting stack

## 📁 Project Structure

```
big_data_pipeline/
├── kafka-producer/          # Python Kafka producer
│   ├── src/
│   │   └── producer.py     # Data generation and streaming
│   ├── Dockerfile
│   └── requirements.txt
├── spark-streaming/         # Spark Streaming application
│   ├── src/
│   │   └── streaming_app.py # Real-time processing logic
│   ├── Dockerfile
│   └── requirements.txt
├── streamlit-dashboard/     # Custom visualization dashboard
│   ├── app.py              # Streamlit dashboard application
│   ├── Dockerfile
│   └── requirements.txt
├── k8s/                    # Kubernetes manifests
│   ├── 00-namespace.yaml
│   ├── 01-zookeeper.yaml
│   ├── 02-kafka.yaml
│   ├── 03-elasticsearch.yaml
│   ├── 04-kibana.yaml
│   ├── 05-kafka-producer.yaml
│   ├── 06-spark-streaming.yaml
│   ├── 07-streamlit.yaml
│   └── 08-monitoring.yaml
├── monitoring/             # Monitoring configuration
│   └── prometheus.yml
├── scripts/               # Automation scripts
│   ├── build-images.sh   # Build Docker images
│   ├── deploy.sh         # Deploy to Kubernetes
│   ├── cleanup.sh        # Clean up resources
│   └── status.sh         # Check deployment status
├── docker-compose.yml     # Local development setup
└── README.md
```

## 🚀 Quick Start

### Prerequisites

- Docker and Docker Compose
- Kubernetes cluster (Minikube, Kind, or cloud provider)
- kubectl configured
- Python 3.9+ (for local development)

### Local Development with Docker Compose

1. **Clone the repository**
   ```bash
   git clone https://github.com/Tung-it2-k67-hust/big_data_pipeline.git
   cd big_data_pipeline
   ```

2. **Start all services**
   ```bash
   docker-compose up -d
   ```

3. **Access the dashboards**
   - Kibana: http://localhost:5601
   - Streamlit: http://localhost:8501
   - Prometheus: http://localhost:9090
   - Grafana: http://localhost:3000 (admin/admin)

4. **Stop services**
   ```bash
   docker-compose down
   ```

### Kubernetes Deployment

1. **Build Docker images**
   ```bash
   ./scripts/build-images.sh
   ```

2. **Deploy to Kubernetes**
   ```bash
   ./scripts/deploy.sh
   ```

3. **Check deployment status**
   ```bash
   ./scripts/status.sh
   # or
   kubectl get pods -n big-data-pipeline
   ```

4. **Access services via NodePort**
   - Kibana: http://<node-ip>:30561
   - Streamlit: http://<node-ip>:30851
   - Prometheus: http://<node-ip>:30909
   - Grafana: http://<node-ip>:30300

5. **Clean up**
   ```bash
   ./scripts/cleanup.sh
   ```

## 🔧 Configuration

### Environment Variables

#### Kafka Producer
- `KAFKA_BOOTSTRAP_SERVERS`: Kafka broker address (default: `kafka:9092`)
- `KAFKA_TOPIC`: Topic name for data streaming (default: `data-stream`)
- `PRODUCER_INTERVAL`: Interval between messages in seconds (default: `1`)

#### Spark Streaming
- `KAFKA_BOOTSTRAP_SERVERS`: Kafka broker address
- `KAFKA_TOPIC`: Topic to consume from
- `ELASTICSEARCH_NODES`: Elasticsearch cluster address
- `ELASTICSEARCH_INDEX`: Index for raw events (default: `events`)
- `ELASTICSEARCH_AGG_INDEX`: Index for aggregated data (default: `events-aggregated`)

#### Streamlit Dashboard
- `ELASTICSEARCH_HOST`: Elasticsearch host (default: `elasticsearch`)
- `ELASTICSEARCH_PORT`: Elasticsearch port (default: `9200`)

## 📊 Data Flow

1. **Data Generation**: Kafka producer generates sample e-commerce events (clicks, views, purchases, searches)
2. **Ingestion**: Events are published to Kafka topic `data-stream`
3. **Processing**: Spark Streaming consumes events, performs real-time aggregations
4. **Storage**: Processed data is stored in Elasticsearch indices
5. **Visualization**: Kibana and Streamlit provide interactive dashboards

### Sample Event Schema

```json
{
  "timestamp": "2024-01-01T12:00:00.000000",
  "user_id": 1234,
  "event_type": "purchase",
  "product_id": 567,
  "price": 99.99,
  "quantity": 2,
  "session_id": 54321,
  "region": "US",
  "device": "mobile"
}
```

## 📈 Monitoring

### Prometheus Metrics

Prometheus collects metrics from:
- Kafka brokers
- Elasticsearch cluster
- Kubernetes pods

Access Prometheus at http://localhost:30909 (K8s) or http://localhost:9090 (Docker Compose)

### Grafana Dashboards

Grafana provides visualization for:
- System metrics
- Application performance
- Resource utilization

Default credentials: `admin/admin`

## 🛠️ Development

### Running Components Locally

#### Kafka Producer
```bash
cd kafka-producer
pip install -r requirements.txt
export KAFKA_BOOTSTRAP_SERVERS=localhost:9092
python src/producer.py
```

#### Spark Streaming
```bash
cd spark-streaming
pip install -r requirements.txt
export KAFKA_BOOTSTRAP_SERVERS=localhost:9092
export ELASTICSEARCH_NODES=localhost
spark-submit --packages org.apache.spark:spark-sql-kafka-0-10_2.12:3.3.0,org.elasticsearch:elasticsearch-spark-30_2.12:8.4.3 src/streaming_app.py
```

#### Streamlit Dashboard
```bash
cd streamlit-dashboard
pip install -r requirements.txt
export ELASTICSEARCH_HOST=localhost
streamlit run app.py
```

## 🧪 Testing

### Manual Testing

1. Check if Kafka is receiving messages:
   ```bash
   kubectl exec -it kafka-0 -n big-data-pipeline -- kafka-console-consumer \
     --bootstrap-server localhost:9092 \
     --topic data-stream \
     --from-beginning
   ```

2. Check Elasticsearch indices:
   ```bash
   curl http://localhost:9200/_cat/indices?v
   ```

3. Query data from Elasticsearch:
   ```bash
   curl http://localhost:9200/events/_search?pretty
   ```

## 🔍 Troubleshooting

### Common Issues

1. **Pods not starting**: Check resource limits and availability
   ```bash
   kubectl describe pod <pod-name> -n big-data-pipeline
   ```

2. **Kafka connection issues**: Ensure Zookeeper is running and healthy
   ```bash
   kubectl logs kafka-0 -n big-data-pipeline
   ```

3. **Elasticsearch disk space**: Monitor disk usage
   ```bash
   curl http://localhost:9200/_cluster/health?pretty
   ```

4. **Spark Streaming errors**: Check logs
   ```bash
   kubectl logs deployment/spark-streaming -n big-data-pipeline
   ```

## 📝 Customization

### Adding New Data Sources

1. Modify `kafka-producer/src/producer.py` to generate different data
2. Update schema in `spark-streaming/src/streaming_app.py`
3. Adjust dashboard visualizations in `streamlit-dashboard/app.py`

### Scaling

- **Kafka**: Increase replicas in `k8s/02-kafka.yaml`
- **Spark**: Adjust resources and replicas in `k8s/06-spark-streaming.yaml`
- **Elasticsearch**: Scale nodes in `k8s/03-elasticsearch.yaml`

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## 📄 License

This project is open source and available under the MIT License.

## 👥 Authors

- Tung-it2-k67-hust

## 🙏 Acknowledgments

- Apache Kafka
- Apache Spark
- Elastic Stack
- Streamlit
- Kubernetes Community
