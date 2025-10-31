"""
Spark Streaming Application for Real-time Data Processing
Consumes data from Kafka, processes it, and sends to Elasticsearch
"""
from pyspark.sql import SparkSession
from pyspark.sql.functions import from_json, col, window, count, sum as spark_sum, avg
from pyspark.sql.types import StructType, StructField, StringType, IntegerType, DoubleType, TimestampType
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def create_spark_session(app_name="BigDataPipeline"):
    """Create and configure Spark session"""
    spark = SparkSession.builder \
        .appName(app_name) \
        .config("spark.jars.packages", 
                "org.apache.spark:spark-sql-kafka-0-10_2.12:3.3.0,"
                "org.elasticsearch:elasticsearch-spark-30_2.12:8.4.3") \
        .config("spark.streaming.stopGracefullyOnShutdown", "true") \
        .config("spark.sql.streaming.checkpointLocation", "/tmp/checkpoint") \
        .getOrCreate()
    
    spark.sparkContext.setLogLevel("WARN")
    logger.info("Spark session created")
    return spark


def define_schema():
    """Define schema for incoming data"""
    return StructType([
        StructField("timestamp", StringType(), True),
        StructField("user_id", IntegerType(), True),
        StructField("event_type", StringType(), True),
        StructField("product_id", IntegerType(), True),
        StructField("price", DoubleType(), True),
        StructField("quantity", IntegerType(), True),
        StructField("session_id", IntegerType(), True),
        StructField("region", StringType(), True),
        StructField("device", StringType(), True)
    ])


def read_from_kafka(spark, kafka_servers, topic):
    """Read streaming data from Kafka"""
    logger.info(f"Reading from Kafka topic: {topic}")
    
    df = spark.readStream \
        .format("kafka") \
        .option("kafka.bootstrap.servers", kafka_servers) \
        .option("subscribe", topic) \
        .option("startingOffsets", "latest") \
        .load()
    
    return df


def process_stream(df, schema):
    """Process the streaming data"""
    # Parse JSON data
    parsed_df = df.select(
        from_json(col("value").cast("string"), schema).alias("data"),
        col("timestamp").alias("kafka_timestamp")
    ).select("data.*", "kafka_timestamp")
    
    # Add processing timestamp
    from pyspark.sql.functions import current_timestamp
    processed_df = parsed_df.withColumn("processing_timestamp", current_timestamp())
    
    # Calculate revenue
    from pyspark.sql.functions import expr
    processed_df = processed_df.withColumn("revenue", expr("price * quantity"))
    
    return processed_df


def create_aggregations(df):
    """Create real-time aggregations"""
    # Convert string timestamp to timestamp type
    from pyspark.sql.functions import to_timestamp
    df = df.withColumn("event_time", to_timestamp(col("timestamp")))
    
    # Aggregate by event type and region
    agg_df = df.groupBy(
        window(col("event_time"), "1 minute"),
        col("event_type"),
        col("region")
    ).agg(
        count("*").alias("event_count"),
        spark_sum("revenue").alias("total_revenue"),
        avg("price").alias("avg_price")
    )
    
    return agg_df


def write_to_elasticsearch(df, es_nodes, index_name):
    """Write streaming data to Elasticsearch"""
    logger.info(f"Writing to Elasticsearch index: {index_name}")
    
    query = df.writeStream \
        .outputMode("append") \
        .format("org.elasticsearch.spark.sql") \
        .option("es.nodes", es_nodes) \
        .option("es.port", "9200") \
        .option("es.resource", index_name) \
        .option("checkpointLocation", f"/tmp/checkpoint/{index_name}") \
        .start()
    
    return query


def write_to_console(df, query_name="console_output"):
    """Write streaming data to console for debugging"""
    query = df.writeStream \
        .outputMode("append") \
        .format("console") \
        .queryName(query_name) \
        .option("truncate", "false") \
        .start()
    
    return query


def main():
    """Main entry point"""
    import os
    
    # Configuration from environment variables
    kafka_servers = os.getenv('KAFKA_BOOTSTRAP_SERVERS', 'kafka:9092')
    kafka_topic = os.getenv('KAFKA_TOPIC', 'data-stream')
    es_nodes = os.getenv('ELASTICSEARCH_NODES', 'elasticsearch')
    es_index = os.getenv('ELASTICSEARCH_INDEX', 'events')
    es_agg_index = os.getenv('ELASTICSEARCH_AGG_INDEX', 'events-aggregated')
    
    # Create Spark session
    spark = create_spark_session()
    
    # Define schema
    schema = define_schema()
    
    # Read from Kafka
    kafka_df = read_from_kafka(spark, kafka_servers, kafka_topic)
    
    # Process stream
    processed_df = process_stream(kafka_df, schema)
    
    # Create aggregations
    agg_df = create_aggregations(processed_df)
    
    # Write raw data to Elasticsearch
    query1 = write_to_elasticsearch(processed_df, es_nodes, es_index)
    
    # Write aggregated data to Elasticsearch
    query2 = write_to_elasticsearch(agg_df, es_nodes, es_agg_index)
    
    # Also write to console for monitoring
    query3 = write_to_console(processed_df.limit(10), "raw_data")
    
    logger.info("Spark Streaming application started")
    
    # Wait for termination
    spark.streams.awaitAnyTermination()


if __name__ == '__main__':
    main()
