"""
Ứng dụng Spark Streaming xử lý dữ liệu bóng đá thời gian thực
Đọc từ Kafka -> Xử lý -> Ghi xuống Cassandra và Elasticsearch
"""
from pyspark.sql import SparkSession
from pyspark.sql.functions import (
    col, expr, when, lit, count,
    sum as spark_sum, avg,
    current_timestamp, to_date, to_timestamp, from_json,
    md5, concat_ws, udf, from_utc_timestamp, coalesce
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
# Cấu hình Logging
# --------------------------------------------------
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)
# Thêm FileHandler để ghi log ra file
file_handler = logging.FileHandler('/tmp/spark_app.log')
file_handler.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)

# --------------------------------------------------
# Khởi tạo Spark Session
# --------------------------------------------------
def create_spark_session(app_name="FootballStreamingToCassandraAndES"):
    """
    Tạo và cấu hình Spark Session với các connector cần thiết
    """
    # Lấy danh sách node Elasticsearch từ biến môi trường
    es_nodes = os.getenv("ELASTICSEARCH_NODES", "elasticsearch")
    
    spark = SparkSession.builder \
        .appName(app_name) \
        .config("spark.sql.shuffle.partitions", "4") \
        .config("spark.es.nodes", es_nodes) \
        .config("spark.es.port", "9200") \
        .config("spark.es.nodes.wan.only", "true") \
        .config("spark.es.index.auto.create", "true") \
        .config("spark.streaming.stopGracefullyOnShutdown", "true") \
        .config("spark.driver.bindAddress", "0.0.0.0") \
        .config("spark.ui.port", "4040") \
        .config("spark.kafka.consumer.cache.enabled", "false") \
        .config("spark.scheduler.mode", "FAIR") \
        .getOrCreate()

    spark.sparkContext.setLogLevel("WARN")
    logger.info(f"Spark session đã được tạo. Kết nối đến ES nodes: {es_nodes}")
    return spark

# --------------------------------------------------
# Định nghĩa Schema
# --------------------------------------------------
def define_schema():
    """
    Định nghĩa cấu trúc dữ liệu (Schema) cho dữ liệu trận đấu
    """
    return StructType([
        StructField("Season", StringType()),      # Mùa giải
        StructField("Div", StringType()),         # Hạng đấu
        StructField("Date", StringType()),        # Ngày thi đấu
        StructField("HomeTeam", StringType()),    # Đội nhà
        StructField("AwayTeam", StringType()),    # Đội khách
        StructField("FTHG", IntegerType()),       # Bàn thắng đội nhà (Full Time)
        StructField("FTAG", IntegerType()),       # Bàn thắng đội khách (Full Time)
        StructField("FTR", StringType()),         # Kết quả (H=Home Win, A=Away Win, D=Draw)
        StructField("HTHG", IntegerType()),       # Bàn thắng đội nhà (Half Time)
        StructField("HTAG", IntegerType()),       # Bàn thắng đội khách (Half Time)
        StructField("HTR", StringType()),         # Kết quả hiệp 1
        StructField("HS", IntegerType()),         # Cú sút đội nhà
        StructField("AS", IntegerType()),         # Cú sút đội khách
        StructField("HST", IntegerType()),        # Cú sút trúng đích đội nhà
        StructField("AST", IntegerType()),        # Cú sút trúng đích đội khách
        StructField("HF", IntegerType()),         # Phạm lỗi đội nhà
        StructField("AF", IntegerType()),         # Phạm lỗi đội khách
        StructField("HC", IntegerType()),         # Phạt góc đội nhà
        StructField("AC", IntegerType()),         # Phạt góc đội khách
        StructField("HY", IntegerType()),         # Thẻ vàng đội nhà
        StructField("AY", IntegerType()),         # Thẻ vàng đội khách
        StructField("HR", IntegerType()),         # Thẻ đỏ đội nhà
        StructField("AR", IntegerType()),         # Thẻ đỏ đội khách
        StructField("PSH", DoubleType()),         # Tỷ lệ cược đội nhà thắng
        StructField("PSD", DoubleType()),         # Tỷ lệ cược hòa
        StructField("PSA", DoubleType())          # Tỷ lệ cược đội khách thắng
    ])

# --------------------------------------------------
# Hàm hỗ trợ (Helper Functions)
# --------------------------------------------------
def format_uuid_string(uuid_str):
    """Định dạng chuỗi UUID cho đúng chuẩn"""
    if uuid_str and len(uuid_str) == 32:
        try:
            return str(uuid.UUID(uuid_str)) 
        except ValueError:
            return None
    return uuid_str

# --------------------------------------------------
# Nguồn dữ liệu Kafka
# --------------------------------------------------
def read_from_kafka(spark, servers, topic):
    """Đọc luồng dữ liệu từ Kafka"""
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
# Xử lý luồng dữ liệu (Process Stream)
# --------------------------------------------------
def process_stream(df, schema):
    """
    Xử lý dữ liệu thô từ Kafka:
    1. Parse JSON
    2. Tính toán thêm các chỉ số
    3. Chuẩn hóa tên cột
    4. Tạo ID duy nhất cho mỗi trận đấu
    """
    # 1. Parse JSON từ Kafka value
    json_df = df.selectExpr("CAST(value AS STRING) as json_payload")
    parsed = json_df.select(
        from_json(col("json_payload"), schema).alias("data")
    ).select("data.*")

    # 2. Thêm các cột tính toán
    processed = (parsed
        .withColumn("processing_ts", from_utc_timestamp(current_timestamp(), "Asia/Ho_Chi_Minh"))
        .withColumn("totalgoals", col("FTHG") + col("FTAG"))
        .withColumn("homewinflag", when(col("FTR") == "H", 1).otherwise(0))
        .withColumn("awaywinflag", when(col("FTR") == "A", 1).otherwise(0))
        .withColumn("drawflag", when(col("FTR") == "D", 1).otherwise(0))
    )

    # 3. Chuyển tên cột thành chữ thường để tương thích tốt hơn với các DB
    final_df = processed.toDF(*[c.lower() for c in processed.columns])
    
    # 4. Tạo match_id duy nhất dựa trên thông tin trận đấu
    final_df = final_df.withColumn("match_id", 
        md5(concat_ws("-", col("season"), col("hometeam"), col("awayteam"), col("date"))))

    # 5. Format UUID
    uuid_formatter = udf(format_uuid_string, StringType())
    final_df = final_df.withColumn("match_id", uuid_formatter(col("match_id")))

    return final_df

# --------------------------------------------------
# Ghi dữ liệu (Writers)
# --------------------------------------------------
def write_to_cassandra(df, keyspace, table):
    """Ghi dữ liệu vào Cassandra"""
    def write_batch(batch_df, batch_id):
        # Chọn đúng các cột có trong bảng Cassandra
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

        # Lọc bỏ các bản ghi có ngày null (Cassandra Primary Key không được null)
        cassandra_df = cassandra_df.filter(col("date").isNotNull())
        
        cassandra_df.write \
            .format("org.apache.spark.sql.cassandra") \
            .mode("append") \
            .option("keyspace", keyspace) \
            .option("table", table) \
            .option("spark.cassandra.connection.host", os.getenv("CASSANDRA_HOST", "cassandra")) \
            .save()
            
    return df.writeStream.queryName(f"Writer_{table}") \
             .option("checkpointLocation", f"/tmp/checkpoint/cassandra_{table}") \
             .foreachBatch(write_batch).outputMode("append").start()

def write_to_elasticsearch(df, index_name):
    """Ghi dữ liệu vào Elasticsearch"""
    return df.writeStream \
        .format("es") \
        .queryName(f"Writer_{index_name}") \
        .option("checkpointLocation", f"/tmp/checkpoint/es_{index_name}") \
        .start(index_name)

# --------------------------------------------------
# Hàm chính (Main)
# --------------------------------------------------
def main():
    logger.info("Application starting...")
    try:
        logger.info("Creating Spark session...")
        spark = create_spark_session()
        logger.info("Spark session created successfully.")

        # Cấu hình scheduler pool để tránh cảnh báo KAFKA-1894
        spark.sparkContext.setLocalProperty("spark.scheduler.pool", "uninterruptible")
        logger.info("Scheduler pool set to 'uninterruptible'.")

        schema = define_schema()

        # Lấy cấu hình từ biến môi trường
        kafka_bootstrap = os.getenv("KAFKA_BOOTSTRAP_SERVERS", "kafka:9092")
        kafka_topic = os.getenv("KAFKA_TOPIC", "football-stream")
        es_index = os.getenv("ELASTICSEARCH_INDEX", "football-matches")
        cassandra_keyspace = os.getenv("CASSANDRA_KEYSPACE", "football_stats")

        logger.info(f"Bắt đầu stream từ {kafka_bootstrap}, topic: {kafka_topic}")
        
        logger.info("Reading from Kafka...")
        kafka_df = read_from_kafka(spark, kafka_bootstrap, kafka_topic)
        logger.info("Kafka stream read successfully.")

        logger.info("Processing stream...")
        processed = process_stream(kafka_df, schema)
        logger.info("Stream processing defined.")

        # Ghi song song xuống Cassandra và Elasticsearch
        logger.info("Starting Cassandra write stream...")
        q1 = write_to_cassandra(processed, cassandra_keyspace, "matches")
        logger.info("Cassandra write stream started.")

        logger.info("Starting Elasticsearch write stream...")
        q_es = write_to_elasticsearch(processed, es_index)
        logger.info("Elasticsearch write stream started.")

        logger.info("Awaiting termination of any stream...")
        spark.streams.awaitAnyTermination()
        logger.info("Stream terminated.")
    except Exception as e:
        logger.error("❌ LỖI NGHIÊM TRỌNG: Ứng dụng Spark bị dừng đột ngột!")
        logger.error(str(e))
        # Giữ container sống để debug
        while True:
            time.sleep(60)

if __name__ == "__main__":
    main()