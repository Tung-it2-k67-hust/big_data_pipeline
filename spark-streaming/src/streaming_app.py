from pyspark.sql import SparkSession
from pyspark.sql.functions import (
    col, expr, when, lit, count,
    sum as spark_sum, avg,
    current_timestamp, to_date, to_timestamp, from_json,
    md5, concat_ws, udf, from_utc_timestamp, coalesce  # <-- Thêm hàm này
)
from pyspark.sql.types import (
    StructType, StructField,
    StringType, IntegerType, DoubleType
)
import logging
import os
import uuid
import time

# --------------------------------------------------
# Logging
# --------------------------------------------------
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# --------------------------------------------------
# Spark Session
# --------------------------------------------------
def create_spark_session(app_name="FootballStreamingToCassandraAndES"):
    # Sử dụng ELASTICSEARCH_NODES để khớp với file YAML Deployment của bạn
    es_nodes = os.getenv("ELASTICSEARCH_NODES", "elasticsearch")
    
    spark = SparkSession.builder \
        .appName(app_name) \
        .config("spark.jars.packages", 
                "org.apache.spark:spark-sql-kafka-0-10_2.12:3.3.3,"
                "com.datastax.spark:spark-cassandra-connector_2.12:3.3.0,"
                "org.elasticsearch:elasticsearch-spark-30_2.12:8.11.0") \
        .config("spark.sql.shuffle.partitions", "4") \
        .config("spark.es.nodes", es_nodes) \
        .config("spark.es.port", "9200") \
        .config("spark.es.nodes.wan.only", "true") \
        .config("spark.es.index.auto.create", "true") \
        .config("spark.streaming.stopGracefullyOnShutdown", "true") \
        .config("spark.driver.bindAddress", "0.0.0.0") \
        .config("spark.ui.port", "4040") \
        .config("spark.kafka.consumer.cache.enabled", "false") \
        .getOrCreate()

    spark.sparkContext.setLogLevel("WARN")
    logger.info(f"Spark session created. Connecting to ES nodes: {es_nodes}")
    return spark

# --------------------------------------------------
# Schema
# --------------------------------------------------
def define_schema():
    return StructType([
        StructField("Season", StringType()),
        StructField("Div", StringType()),
        StructField("Date", StringType()),
        StructField("HomeTeam", StringType()),
        StructField("AwayTeam", StringType()),
        StructField("FTHG", IntegerType()),
        StructField("FTAG", IntegerType()),
        StructField("FTR", StringType()),
        StructField("HTHG", IntegerType()),
        StructField("HTAG", IntegerType()),
        StructField("HTR", StringType()),
        StructField("HS", IntegerType()),
        StructField("AS", IntegerType()),
        StructField("HST", IntegerType()),
        StructField("AST", IntegerType()),
        StructField("HF", IntegerType()),
        StructField("AF", IntegerType()),
        StructField("HC", IntegerType()),
        StructField("AC", IntegerType()),
        StructField("HY", IntegerType()),
        StructField("AY", IntegerType()),
        StructField("HR", IntegerType()),
        StructField("AR", IntegerType()),
        StructField("PSH", DoubleType()),
        StructField("PSD", DoubleType()),
        StructField("PSA", DoubleType())
    ])

# --------------------------------------------------
# Helper Functions
# --------------------------------------------------
def format_uuid_string(uuid_str):
    if uuid_str and len(uuid_str) == 32:
        try:
            # Thư viện uuid của Python sẽ tự động thêm gạch ngang khi in ra str()
            return str(uuid.UUID(uuid_str)) 
        except ValueError:
            return None
    return uuid_str # Trả về nguyên gốc nếu đã có format đúng hoặc null

# --------------------------------------------------
# Kafka Source
# --------------------------------------------------
def read_from_kafka(spark, servers, topic):
    return spark.readStream \
        .format("kafka") \
        .option("kafka.bootstrap.servers", servers) \
        .option("subscribe", topic) \
        .option("startingOffsets", "earliest") \
        .option("failOnDataLoss", "false") \
        .option("kafka.request.timeout.ms", "60000") \
        .option("kafka.session.timeout.ms", "30000") \
        .load()

# --------------------------------------------------
# Process Stream
# --------------------------------------------------
def process_stream(df, schema):
    # 1. Parse JSON từ Kafka
    json_df = df.selectExpr("CAST(value AS STRING) as json_payload")
    parsed = json_df.select(
        from_json(col("json_payload"), schema).alias("data")
    ).select("data.*")

    # 2. Thêm các cột tính toán (DÙNG NGOẶC ĐƠN ĐỂ BAO QUANH)
    processed = (parsed
        .withColumn("processing_ts", from_utc_timestamp(current_timestamp(), "Asia/Ho_Chi_Minh"))
        .withColumn("totalgoals", col("FTHG") + col("FTAG"))
        .withColumn("homewinflag", when(col("FTR") == "H", 1).otherwise(0))
        .withColumn("awaywinflag", when(col("FTR") == "A", 1).otherwise(0))
        .withColumn("drawflag", when(col("FTR") == "D", 1).otherwise(0))
    )

    # 3. Chuyển tên cột thành chữ thường
    final_df = processed.toDF(*[c.lower() for c in processed.columns])
    
    # 4. Tạo match_id
    final_df = final_df.withColumn("match_id", 
        md5(concat_ws("-", col("season"), col("hometeam"), col("awayteam"), col("date"))))

    # 5. Format UUID
    uuid_formatter = udf(format_uuid_string, StringType())
    final_df = final_df.withColumn("match_id", uuid_formatter(col("match_id")))

    return final_df

# --------------------------------------------------
# Writers
# --------------------------------------------------
def write_to_cassandra(df, keyspace, table):
    def write_batch(batch_df, batch_id):
        # Chọn đúng các cột có trong bảng Cassandra
        # Convert Date string to proper date format for Cassandra
        cassandra_df = batch_df.select(
            col("season"), col("div"), 
            to_date(col("date"), "yyyy-MM-dd").alias("date"), 
            col("hometeam"), col("awayteam"),
            col("fthg"), col("ftag"), col("ftr"),
            col("hthg"), col("htag"), col("htr"),
            col("hs"), col("as"), col("hst"), col("ast"),
            col("hf"), col("af"), col("hc"), col("ac"),
            col("hy"), col("ay"), col("hr"), col("ar"),
            col("psh"), col("psd"), col("psa"),
            col("match_id")
        )

        # --- FIX: Filter null dates to prevent Cassandra write failure ---
        # Cassandra Primary Key columns cannot be null
        cassandra_df = cassandra_df.filter(col("date").isNotNull())
        
        cassandra_df.write \
            .format("org.apache.spark.sql.cassandra") \
            .mode("append") \
            .option("keyspace", keyspace) \
            .option("table", table) \
            .option("spark.cassandra.connection.host", os.getenv("CASSANDRA_HOST", "cassandra")) \
            .save()
            
    # Thêm query name để dễ quản lý trong Spark UI
    return df.writeStream.queryName(f"Writer_{table}") \
             .option("checkpointLocation", f"/tmp/checkpoint/cassandra_{table}") \
             .foreachBatch(write_batch).outputMode("append").start()

def write_to_elasticsearch(df, index_name):
    return df.writeStream \
        .format("es") \
        .queryName(f"Writer_{index_name}") \
        .option("checkpointLocation", f"/tmp/checkpoint/es_{index_name}") \
        .start(index_name)

# --------------------------------------------------
# Main
# --------------------------------------------------
def main():
    try:
        spark = create_spark_session()
        schema = define_schema()

        # Lấy cấu hình từ env để khớp với file 06-spark-streaming.yaml
        kafka_bootstrap = os.getenv("KAFKA_BOOTSTRAP_SERVERS", "kafka:9092")
        # Đảm bảo topic khớp với Producer (football-stream)
        kafka_topic = os.getenv("KAFKA_TOPIC", "football-stream")
        # Đảm bảo index khớp với Dashboard (football-matches)
        es_index = os.getenv("ELASTICSEARCH_INDEX", "football-matches")

        logger.info(f"Starting stream from {kafka_bootstrap} topic {kafka_topic}")

        kafka_df = read_from_kafka(spark, kafka_bootstrap, kafka_topic)
        processed = process_stream(kafka_df, schema)

        # Ghi song song
        q1 = write_to_cassandra(processed, "football_stats", "matches")
        q_es = write_to_elasticsearch(processed, es_index)

        spark.streams.awaitAnyTermination()
    except Exception as e:
        logger.error("❌ CRITICAL ERROR: Spark App Crashed!")
        logger.error(str(e))
        # Giữ container sống để xem log và UI (nếu UI đã lên)
        while True:
            time.sleep(60)

if __name__ == "__main__":
    main()