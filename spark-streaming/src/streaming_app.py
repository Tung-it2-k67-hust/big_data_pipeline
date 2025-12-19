from pyspark.sql import SparkSession
from pyspark.sql.functions import col, window, count, sum as spark_sum, avg, to_timestamp, expr, when, lit, concat_ws
from pyspark.sql.types import StructType, StructField, StringType, IntegerType, DoubleType, TimestampType
import logging
import os

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(_name_)


def create_spark_session(app_name="FootballDataPipeline"):
    """Create and configure Spark session"""
    # ... (Không thay đổi, giữ nguyên cấu hình cơ bản)
    spark = SparkSession.builder \
        .appName(app_name) \
        .config("spark.jars.packages", 
                "org.apache.spark:spark-sql-kafka-0-10_2.12:3.3.0,"
                "org.elasticsearch:elasticsearch-spark-30_2.12:8.4.3,"
                "com.datastax.spark:spark-cassandra-connector_2.12:3.3.0") \
        .config("spark.streaming.stopGracefullyOnShutdown", "true") \
        .config("spark.sql.streaming.checkpointLocation", "/tmp/checkpoint") \
        .getOrCreate()
    
    spark.sparkContext.setLogLevel("WARN")
    logger.info("Spark session created")
    return spark


def define_schema():
    """Define schema for incoming football match data"""
    # Dựa trên các cột trong hình ảnh dataset
    return StructType([
        StructField("Season", StringType(), True), # Sử dụng String để dễ dàng xử lý năm hoặc chu kỳ giải đấu
        StructField("Div", StringType(), True),
        StructField("Date", StringType(), True), # Giữ là String để xử lý định dạng ngày tháng sau
        StructField("HomeTeam", StringType(), True),
        StructField("AwayTeam", StringType(), True),
        StructField("FTHG", IntegerType(), True), # Full Time Home Goals
        StructField("FTAG", IntegerType(), True), # Full Time Away Goals
        StructField("FTR", StringType(), True), # Full Time Result (H, D, A)
        StructField("HTHG", IntegerType(), True),
        StructField("HTAG", IntegerType(), True),
        StructField("HTR", StringType(), True),
        StructField("HS", IntegerType(), True), # Home Shots
        StructField("AS", IntegerType(), True), # Away Shots
        StructField("HST", IntegerType(), True), # Home Shots on Target
        StructField("AST", IntegerType(), True), # Away Shots on Target
        StructField("HF", IntegerType(), True), # Home Fouls
        StructField("AF", IntegerType(), True), # Away Fouls
        StructField("HC", IntegerType(), True), # Home Corners
        StructField("AC", IntegerType(), True), # Away Corners
        StructField("HY", IntegerType(), True), # Home Yellow Cards
        StructField("AY", IntegerType(), True), # Away Yellow Cards
        StructField("HR", IntegerType(), True), # Home Red Cards
        StructField("AR", IntegerType(), True), # Away Red Cards
        StructField("PSH", DoubleType(), True), # Pre-Match odds: Home Win
        StructField("PSD", DoubleType(), True), # Pre-Match odds: Draw
        StructField("PSA", DoubleType(), True)  # Pre-Match odds: Away Win
    ])


def read_from_kafka(spark, kafka_servers, topic):
    """Read streaming data from Kafka"""
    # ... (Không thay đổi)
    logger.info(f"Reading from Kafka topic: {topic}")
    
    df = spark.readStream \
        .format("kafka") \
        .option("kafka.bootstrap.servers", kafka_servers) \
        .option("subscribe", topic) \
        .option("startingOffsets", "latest") \
        .load()
    
    return df


def process_stream(df, schema):
    """Process the streaming football match data"""
    
    # Giả định dữ liệu Kafka đến dưới dạng chuỗi CSV (value)
    # Cần split chuỗi 'value' và áp dụng schema.
    # Tuy nhiên, cách tốt nhất cho Spark Structured Streaming là dữ liệu đến dưới dạng JSON.
    # Tôi sẽ điều chỉnh lại logic để xử lý JSON, và giả định dữ liệu đã được đẩy vào Kafka dưới dạng JSON 
    # với các trường tương ứng với schema mới.

    # Nếu dữ liệu thực sự là CSV/chuỗi: cần dùng UDF hoặc xử lý phức tạp hơn
    # Nếu dữ liệu là JSON (Cách tiếp cận tiêu chuẩn):
    
    # 1. Parse JSON data
    parsed_df = df.select(
        col("value").cast("string").alias("value_string"),
        col("timestamp").alias("kafka_timestamp")
    )
    
    # Phân tích chuỗi JSON
    parsed_df = parsed_df.select(
        expr("from_json(value_string, '{}')".format(schema.json())).alias("data"),
        col("kafka_timestamp")
    ).select("data.*", "kafka_timestamp")
    
    # 2. Thêm timestamp xử lý
    from pyspark.sql.functions import current_timestamp, to_date
    processed_df = parsed_df.withColumn("processing_timestamp", current_timestamp())
    
    # 3. Chuyển đổi cột 'Date' sang kiểu Timestamp
    # *Lưu ý: Bạn cần biết định dạng ngày tháng cụ thể của cột 'Date' (ví dụ: dd/MM/yy, MM/dd/yyyy,...)
    # CSV format is yyyy-MM-dd (e.g., 1993-07-23)
    date_formats = ["yyyy-MM-dd", "dd/MM/yyyy", "M/d/yyyy", "dd/MM/yy", "M/d/yy"] 
    
    # Thử chuyển đổi 'Date' thành kiểu Date/Timestamp, dùng to_date/to_timestamp
    # Sử dụng 'to_date' với danh sách các định dạng có thể
    date_col = to_date(col("Date"), date_formats[0])
    for fmt in date_formats[1:]:
        date_col = when(col("Date").isNotNull(), to_date(col("Date"), fmt)).otherwise(date_col)

    processed_df = processed_df.withColumn("match_date", date_col)

    # Extract Month and Year for visualization
    from pyspark.sql.functions import year, month
    processed_df = processed_df.withColumn("Year", year(col("match_date"))) \
                               .withColumn("Month", month(col("match_date")))
    
    # 4. Tính toán Total Goals và Win/Loss/Draw flags
    processed_df = processed_df.withColumn("TotalGoals", expr("FTHG + FTAG")) \
                               .withColumn("HomeWinFlag", when(col("FTR") == lit("H"), lit(1)).otherwise(lit(0))) \
                               .withColumn("AwayWinFlag", when(col("FTR") == lit("A"), lit(1)).otherwise(lit(0))) \
                               .withColumn("DrawFlag", when(col("FTR") == lit("D"), lit(1)).otherwise(lit(0)))

    return processed_df


def create_aggregations(df):
    """Create real-time aggregations (e.g., total goals per division/season)"""
    
    # Aggregate by Division and Season over a tumbling window (e.g., 1 day) based on match_date
    agg_df = df.groupBy(
        window(col("match_date"), "1 day", "1 day").alias("time_window"), # Cửa sổ trượt 1 ngày, trượt mỗi ngày
        col("Div"),
        col("Season")
    ).agg(
        count("*").alias("match_count"),
        spark_sum("TotalGoals").alias("total_goals"),
        spark_sum("HomeWinFlag").alias("home_wins"),
        spark_sum("AwayWinFlag").alias("away_wins"),
        spark_sum("DrawFlag").alias("draws"),
        avg("TotalGoals").alias("avg_goals_per_match"),
        avg("PSH").alias("avg_odds_home"),
        avg("PSD").alias("avg_odds_draw"),
        avg("PSA").alias("avg_odds_away")
    )
    
    return agg_df


def write_to_elasticsearch(df, es_nodes, index_name):
    """Write streaming data to Elasticsearch"""
    # ... (Giữ nguyên)
    logger.info(f"Writing to Elasticsearch index: {index_name}")
    
    # Cần đảm bảo DataFrame có cột timestamp hoặc id duy nhất cho ES.
    # Cột 'kafka_timestamp' hoặc 'processing_timestamp' có thể được sử dụng.
    
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
    # ... (Giữ nguyên)
    query = df.writeStream \
        .outputMode("append") \
        .format("console") \
        .queryName(query_name) \
        .option("truncate", "false") \
        .start()
    
    return query


def write_to_cassandra(df, keyspace, table):
    """Write streaming data to Cassandra"""
    # ... (Giữ nguyên)
    logger.info(f"Writing to Cassandra keyspace: {keyspace}, table: {table}")
    
    def write_batch_to_cassandra(batch_df, batch_id):
        """Function to write each batch to Cassandra"""
        cassandra_host = os.getenv('CASSANDRA_HOST', 'cassandra')
        cassandra_port = os.getenv('CASSANDRA_PORT', '9042')
        
        # Đảm bảo các cột cần thiết cho bảng Cassandra có sẵn và đúng kiểu dữ liệu
        
        batch_df.write \
            .format("org.apache.spark.sql.cassandra") \
            .mode("append") \
            .option("spark.cassandra.connection.host", cassandra_host) \
            .option("spark.cassandra.connection.port", cassandra_port) \
            .option("keyspace", keyspace) \
            .option("table", table) \
            .save()
        
        logger.info(f"Batch {batch_id} written to Cassandra table {keyspace}.{table}")
    
    query = df.writeStream \
        .outputMode("append") \
        .foreachBatch(write_batch_to_cassandra) \
        .option("checkpointLocation", f"/tmp/checkpoint/cassandra_{table}") \
        .start()
    
    return query


def prepare_cassandra_events(df):
    """Prepare DataFrame for Cassandra 'matches' table (raw data)"""
    from pyspark.sql.functions import expr
    
    cassandra_df = df.select(
        expr("uuid()").alias("match_id"),
        col("Season"),
        col("Div"),
        col("match_date").alias("date"),
        col("HomeTeam"),
        col("AwayTeam"),
        col("FTHG"),
        col("FTAG"),
        col("FTR"),
        col("TotalGoals"),
        concat_ws(" vs ", col("HomeTeam"), col("AwayTeam")).alias("match_title")
    ).withColumn(
        "processed_timestamp", col("processing_timestamp")
    )
    
    return cassandra_df


def prepare_cassandra_metrics(agg_df):
    """Prepare aggregated DataFrame for Cassandra 'metrics_by_division_season' table"""
    
    # Chuẩn bị metrics theo Division và Season
    metrics_by_region = agg_df.select(
        concat_ws("-", col("Div"), col("Season")).alias("division_season_key"), # Khóa chính
        col("Div").alias("division"),
        col("Season").alias("season"),
        col("time_window.start").alias("window_start"),
        col("time_window.end").alias("window_end"),
        col("match_count"),
        col("total_goals").cast("bigint").alias("total_goals"),
        col("avg_goals_per_match").cast("decimal(4,2)").alias("avg_goals_per_match"),
        col("home_wins"),
        col("away_wins"),
        col("draws")
    )
    
    return metrics_by_region


def main():
    """Main entry point"""
    # ... (Giữ nguyên cấu hình và luồng xử lý)
    
    # Configuration from environment variables
    kafka_servers = os.getenv('KAFKA_BOOTSTRAP_SERVERS', 'kafka:9092')
    kafka_topic = os.getenv('KAFKA_TOPIC', 'football-stream') # Đổi tên topic
    es_nodes = os.getenv('ELASTICSEARCH_NODES', 'elasticsearch')
    es_index = os.getenv('ELASTICSEARCH_INDEX', 'football-matches')
    es_agg_index = os.getenv('ELASTICSEARCH_AGG_INDEX', 'football-metrics')
    cassandra_keyspace = os.getenv('CASSANDRA_KEYSPACE', 'bigdata_pipeline')
    
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
    
    # Prepare and write to Cassandra
    cassandra_events = prepare_cassandra_events(processed_df)
    query4 = write_to_cassandra(cassandra_events, cassandra_keyspace, "matches") # Đổi tên bảng
    
    # Prepare and write aggregated metrics to Cassandra
    cassandra_metrics = prepare_cassandra_metrics(agg_df)
    query5 = write_to_cassandra(cassandra_metrics, cassandra_keyspace, "metrics_by_division_season") # Đổi tên bảng
    
    # Also write to console for monitoring
    query3 = write_to_console(processed_df.limit(10), "raw_match_data")
    
    logger.info("Spark Streaming application for Football Data started with Elasticsearch and Cassandra sinks")
    
    # Wait for termination
    spark.streams.awaitAnyTermination()


if _name_ == '_main_':
    main()
Long
from pyspark.sql import SparkSession
from pyspark.sql.functions import col, window, count, sum as spark_sum, avg, to_timestamp, expr, when, lit, concat_ws
from pyspark.sql.types import StructType, StructField, StringType, IntegerType, DoubleType, TimestampType
import logging
import os

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(_name_)


def create_spark_session(app_name="FootballDataPipeline"):
    """Create and configure Spark session"""
    spark = SparkSession.builder \
        .appName(app_name) \
        .config("spark.jars.packages", 
                "org.apache.spark:spark-sql-kafka-0-10_2.12:3.3.0,"
                "org.elasticsearch:elasticsearch-spark-30_2.12:8.4.3,"
                "com.datastax.spark:spark-cassandra-connector_2.12:3.3.0") \
        .config("spark.streaming.stopGracefullyOnShutdown", "true") \
        .config("spark.sql.streaming.checkpointLocation", "/tmp/checkpoint") \
        .getOrCreate()
    
    spark.sparkContext.setLogLevel("WARN")
    logger.info("Spark session created")
    return spark


def define_schema():
    """Define schema for incoming football match data"""
    return StructType([
        StructField("Season", StringType(), True),
        StructField("Div", StringType(), True),
        StructField("Date", StringType(), True), 
        StructField("HomeTeam", StringType(), True),
        StructField("AwayTeam", StringType(), True),
        StructField("FTHG", IntegerType(), True), # Full Time Home Goals
        StructField("FTAG", IntegerType(), True), # Full Time Away Goals
        StructField("FTR", StringType(), True), # Full Time Result (H, D, A)
        StructField("HTHG", IntegerType(), True),
        StructField("HTAG", IntegerType(), True),
        StructField("HTR", StringType(), True),
        StructField("HS", IntegerType(), True), # Home Shots
        StructField("AS", IntegerType(), True), # Away Shots
        StructField("HST", IntegerType(), True), # Home Shots on Target
        StructField("AST", IntegerType(), True), # Away Shots on Target
        StructField("HF", IntegerType(), True), # Home Fouls
        StructField("AF", IntegerType(), True), # Away Fouls
        StructField("HC", IntegerType(), True), # Home Corners
        StructField("AC", IntegerType(), True), # Away Corners
        StructField("HV", StringType(), True), # Home Yellow Cards 
        StructField("AV", StringType(), True), # Away Yellow Cards
        StructField("HR", StringType(), True), # Home Red Cards
        StructField("AR", StringType(), True), # Away Red Cards
        StructField("PSH", DoubleType(), True), # Pre-Match odds: Home Win
        StructField("PSD", DoubleType(), True), # Pre-Match odds: Draw
        StructField("PSA", DoubleType(), True)  # Pre-Match odds: Away Win
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
    """Process the streaming football match data"""
    parsed_df = df.select(
        col("value").cast("string").alias("value_string"),
        col("timestamp").alias("kafka_timestamp")
    )
    parsed_df = parsed_df.select(
        expr("from_json(value_string, '{}')".format(schema.json())).alias("data"),
        col("kafka_timestamp")
    ).select("data.*", "kafka_timestamp")
    
    from pyspark.sql.functions import current_timestamp, to_date
    processed_df = parsed_df.withColumn("processing_timestamp", current_timestamp())
    
    date_formats = ["dd/MM/yyyy", "M/d/yyyy", "dd/MM/yy", "M/d/yy"] 
    
    date_col = to_date(col("Date"), date_formats[0])
    for fmt in date_formats[1:]:
        date_col = when(col("Date").isNotNull(), to_date(col("Date"), fmt)).otherwise(date_col)

    processed_df = processed_df.withColumn("match_date", date_col)
    
    processed_df = processed_df.withColumn("TotalGoals", expr("FTHG + FTAG")) \
                               .withColumn("HomeWinFlag", when(col("FTR") == lit("H"), lit(1)).otherwise(lit(0))) \
                               .withColumn("AwayWinFlag", when(col("FTR") == lit("A"), lit(1)).otherwise(lit(0))) \
                               .withColumn("DrawFlag", when(col("FTR") == lit("D"), lit(1)).otherwise(lit(0)))

    return processed_df


def create_aggregations(df):
    """Create real-time aggregations (e.g., total goals per division/season)"""
    
    # Aggregate by Division and Season over a tumbling window (e.g., 1 day) based on match_date
    agg_df = df.groupBy(
        window(col("match_date"), "1 day", "1 day").alias("time_window"), 
        col("Div"),
        col("Season")
    ).agg(
        count("*").alias("match_count"),
        spark_sum("TotalGoals").alias("total_goals"),
        spark_sum("HomeWinFlag").alias("home_wins"),
        spark_sum("AwayWinFlag").alias("away_wins"),
        spark_sum("DrawFlag").alias("draws"),
        avg("TotalGoals").alias("avg_goals_per_match"),
        avg("PSH").alias("avg_odds_home"),
        avg("PSD").alias("avg_odds_draw"),
        avg("PSA").alias("avg_odds_away")
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


def write_to_cassandra(df, keyspace, table):
    """Write streaming data to Cassandra"""
    logger.info(f"Writing to Cassandra keyspace: {keyspace}, table: {table}")
    
    def write_batch_to_cassandra(batch_df, batch_id):
        """Function to write each batch to Cassandra"""
        cassandra_host = os.getenv('CASSANDRA_HOST', 'cassandra')
        cassandra_port = os.getenv('CASSANDRA_PORT', '9042')  
        
        batch_df.write \
            .format("org.apache.spark.sql.cassandra") \
            .mode("append") \
            .option("spark.cassandra.connection.host", cassandra_host) \
            .option("spark.cassandra.connection.port", cassandra_port) \
            .option("keyspace", keyspace) \
            .option("table", table) \
            .save()
        
        logger.info(f"Batch {batch_id} written to Cassandra table {keyspace}.{table}")
    
    query = df.writeStream \
        .outputMode("append") \
        .foreachBatch(write_batch_to_cassandra) \
        .option("checkpointLocation", f"/tmp/checkpoint/cassandra_{table}") \
        .start()
    
    return query


def prepare_cassandra_events(df):
    """Prepare DataFrame for Cassandra 'matches' table (raw data)"""
    from pyspark.sql.functions import expr
    
    cassandra_df = df.select(
        expr("uuid()").alias("match_id"),
        col("Season"),
        col("Div"),
        col("match_date").alias("date"),
        col("HomeTeam"),
        col("AwayTeam"),
        col("FTHG"),
        col("FTAG"),
        col("FTR"),
        col("TotalGoals"),
        concat_ws(" vs ", col("HomeTeam"), col("AwayTeam")).alias("match_title")
    ).withColumn(
        "processed_timestamp", col("processing_timestamp")
    )
    
    return cassandra_df


def prepare_cassandra_metrics(agg_df):
    """Prepare aggregated DataFrame for Cassandra 'metrics_by_division_season' table"""
    
    metrics_by_region = agg_df.select(
        concat_ws("-", col("Div"), col("Season")).alias("division_season_key"),
        col("Div").alias("division"),
        col("Season").alias("season"),
        col("time_window.start").alias("window_start"),
        col("time_window.end").alias("window_end"),
        col("match_count"),
        col("total_goals").cast("bigint").alias("total_goals"),
        col("avg_goals_per_match").cast("decimal(4,2)").alias("avg_goals_per_match"),
        col("home_wins"),
        col("away_wins"),
        col("draws")
    )
    
    return metrics_by_region


def main():
    """Main entry point"""
    
    # Configuration from environment variables
    kafka_servers = os.getenv('KAFKA_BOOTSTRAP_SERVERS', 'kafka:9092')
    kafka_topic = os.getenv('KAFKA_TOPIC', 'football-stream')
    es_nodes = os.getenv('ELASTICSEARCH_NODES', 'elasticsearch')
    es_index = os.getenv('ELASTICSEARCH_INDEX', 'football-matches')
    es_agg_index = os.getenv('ELASTICSEARCH_AGG_INDEX', 'football-metrics')
    cassandra_keyspace = os.getenv('CASSANDRA_KEYSPACE', 'bigdata_pipeline')
    
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
    
    # Prepare and write to Cassandra
    cassandra_events = prepare_cassandra_events(processed_df)
    query4 = write_to_cassandra(cassandra_events, cassandra_keyspace, "matches")
    
    # Prepare and write aggregated metrics to Cassandra
    cassandra_metrics = prepare_cassandra_metrics(agg_df)
    query5 = write_to_cassandra(cassandra_metrics, cassandra_keyspace, "metrics_by_division_season")
    
    # Also write to console for monitoring
    query3 = write_to_console(processed_df.limit(10), "raw_match_data")
    
    logger.info("Spark Streaming application for Football Data started with Elasticsearch and Cassandra sinks")
    
    # Wait for termination
    spark.streams.awaitAnyTermination()


if __name__ == '__main__':
    main()