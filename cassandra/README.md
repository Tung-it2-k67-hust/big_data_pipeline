# Cassandra Data Storage

This folder contains Cassandra configuration and schema initialization files for the big data pipeline.

## Schema Design

The Cassandra schema is optimized for:
- Time-series data with TTL (30 days for raw events)
- Query patterns based on region, device, product, and user dimensions
- Fast writes for real-time streaming data
- Efficient range queries with clustering keys

## Tables

### events
Raw event data partitioned by event_type and region, ordered by timestamp.

### metrics_by_region
Aggregated metrics partitioned by region for regional analysis.

### metrics_by_device
Aggregated metrics partitioned by device for device-based analysis.

### product_metrics
Daily product performance metrics for product analysis.

### user_activity
Daily user activity and spending patterns for user analysis.

## Access Cassandra

### Using cqlsh in Kubernetes
```bash
kubectl exec -it cassandra-0 -n big-data-pipeline -- cqlsh
```

### Using cqlsh in Docker Compose
```bash
docker exec -it cassandra cqlsh
```

### Query Examples

```sql
-- View recent events by region
USE bigdata_pipeline;
SELECT * FROM events WHERE event_type='purchase' AND region='North America' LIMIT 10;

-- View metrics by region
SELECT * FROM metrics_by_region WHERE region='Europe' LIMIT 10;

-- View product performance
SELECT * FROM product_metrics WHERE product_id='PROD-001' LIMIT 10;
```

## Performance Tuning

For production:
- Increase replication_factor to 3
- Adjust compaction strategy based on workload
- Configure appropriate gc_grace_seconds
- Monitor with nodetool and DataStax OpsCenter
