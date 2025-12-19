from pyspark.sql import SparkSession
from pyspark.sql.functions import (
    col, expr, when, lit, count,
    sum as spark_sum, avg,
    current_timestamp, to_date, from_json
)
from pyspark.sql.types import (
    StructType, StructField,
    StringType, IntegerType, DoubleType
)
import logging
import os

# --------------------------------------------------
# Logging
# --------------------------------------------------
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# --------------------------------------------------
# Spark Session
# --------------------------------------------------
def create_spark_session(app_name="FootballStreamingToCassandraAndES"):
    # Đảm bảo các dòng .config không bị ngắt bởi comment sai chỗ
    spark = SparkSession.builder \
        .appName(app_name) \
        .config("spark.jars.packages", 
                "org.apache.spark:spark-sql-kafka-0-10_2.12:3.3.0,"
                "com.datastax.spark:spark-cassandra-connector_2.12:3.3.0,"
                "org.elasticsearch:elasticsearch-spark-30_2.12:8.4.3") \
        .config("spark.sql.shuffle.partitions", "4") \
        .config("spark.es.nodes", os.getenv("ELASTICSEARCH_HOST", "elasticsearch")) \
        .config("spark.es.port", "9200") \
        .config("spark.es.nodes.wan.only", "true") \
        .config("spark.es.index.auto.create", "true") \
        .getOrCreate()

    spark.sparkContext.setLogLevel("WARN")
    logger.info("Spark session created with dual-sink support")
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
# Kafka Source
# --------------------------------------------------
def read_from_kafka(spark, servers, topic):
    return spark.readStream \
        .format("kafka") \
        .option("kafka.bootstrap.servers", servers) \
        .option("subscribe", topic) \
        .option("startingOffsets", "latest") \
        .load()

# --------------------------------------------------
# Process Stream
# --------------------------------------------------
def process_stream(df, schema):
    # Bước chuyển đổi quan trọng để tránh lỗi cú pháp parse JSON
    json_df = df.selectExpr("CAST(value AS STRING) as json_payload")
    
    parsed = json_df.select(
        from_json(col("json_payload"), schema).alias("data")
    ).select("data.*")

    processed = parsed \
        .withColumn("processing_ts", current_timestamp()) \
        .withColumn("match_date", to_date(col("Date"), "dd/MM/yyyy")) \
        .withColumn("TotalGoals", col("FTHG") + col("FTAG")) \
        .withColumn("HomeWinFlag", when(col("FTR") == "H", 1).otherwise(0)) \
        .withColumn("AwayWinFlag", when(col("FTR") == "A", 1).otherwise(0)) \
        .withColumn("DrawFlag", when(col("FTR") == "D", 1).otherwise(0))

    return processed

# --------------------------------------------------
# Writers
# --------------------------------------------------
def write_to_cassandra(df, keyspace, table):
    def write_batch(batch_df, batch_id):
        batch_df.write \
            .format("org.apache.spark.sql.cassandra") \
            .mode("append") \
            .option("keyspace", keyspace) \
            .option("table", table) \
            .option("spark.cassandra.connection.host", os.getenv("CASSANDRA_HOST", "cassandra")) \
            .save()
    # Thêm query name để dễ quản lý trong Spark UI
    return df.writeStream.queryName(f"Writer_{table}") \
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
    spark = create_spark_session()
    schema = define_schema()

    kafka_df = read_from_kafka(
        spark,
        os.getenv("KAFKA_BOOTSTRAP_SERVERS", "kafka:9092"),
        os.getenv("KAFKA_TOPIC", "football-stream")
    )

    processed = process_stream(kafka_df, schema)

    # Khởi chạy các luồng song song
    q1 = write_to_cassandra(processed, "football_stats", "matches")
    q_es = write_to_elasticsearch(processed, "football-matches")

    spark.streams.awaitAnyTermination()

if __name__ == "__main__":
    main()