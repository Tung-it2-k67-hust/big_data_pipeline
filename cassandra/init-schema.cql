-- Create keyspace for big data pipeline
CREATE KEYSPACE IF NOT EXISTS bigdata_pipeline
WITH replication = {
    'class': 'SimpleStrategy',
    'replication_factor': 1
};

USE bigdata_pipeline;

-- Table for raw events
CREATE TABLE IF NOT EXISTS events (
    event_id UUID,
    event_type TEXT,
    user_id TEXT,
    product_id TEXT,
    price DECIMAL,
    quantity INT,
    region TEXT,
    device TEXT,
    timestamp TIMESTAMP,
    PRIMARY KEY ((event_type, region), timestamp, event_id)
) WITH CLUSTERING ORDER BY (timestamp DESC)
AND default_time_to_live = 2592000; -- 30 days retention

-- Table for aggregated metrics by region
CREATE TABLE IF NOT EXISTS metrics_by_region (
    region TEXT,
    window_start TIMESTAMP,
    window_end TIMESTAMP,
    event_type TEXT,
    total_events BIGINT,
    total_revenue DECIMAL,
    avg_price DECIMAL,
    PRIMARY KEY ((region), window_start, event_type)
) WITH CLUSTERING ORDER BY (window_start DESC);

-- Table for aggregated metrics by device
CREATE TABLE IF NOT EXISTS metrics_by_device (
    device TEXT,
    window_start TIMESTAMP,
    window_end TIMESTAMP,
    event_type TEXT,
    total_events BIGINT,
    total_revenue DECIMAL,
    avg_price DECIMAL,
    PRIMARY KEY ((device), window_start, event_type)
) WITH CLUSTERING ORDER BY (window_start DESC);

-- Table for product performance
CREATE TABLE IF NOT EXISTS product_metrics (
    product_id TEXT,
    date DATE,
    total_views BIGINT,
    total_clicks BIGINT,
    total_purchases BIGINT,
    total_revenue DECIMAL,
    PRIMARY KEY ((product_id), date)
) WITH CLUSTERING ORDER BY (date DESC);

-- Table for user activity
CREATE TABLE IF NOT EXISTS user_activity (
    user_id TEXT,
    date DATE,
    total_events BIGINT,
    total_purchases BIGINT,
    total_spent DECIMAL,
    PRIMARY KEY ((user_id), date)
) WITH CLUSTERING ORDER BY (date DESC);
