from pyspark.sql import SparkSession
from pyspark.sql.functions import (
    col, expr, when, lit, count,
    sum as spark_sum, avg,
    current_timestamp, to_date
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
def create_spark_session(app_name="FootballStreamingToCassandra"):
    spark = SparkSession.builder \
        .appName(app_name) \
        .config(
            "spark.jars.packages",
            "org.apache.spark:spark-sql-kafka-0-10_2.12:3.3.0,"
            "com.datastax.spark:spark-cassandra-connector_2.12:3.3.0"
        ) \
        .config("spark.sql.shuffle.partitions", "4") \
        .getOrCreate()

    spark.sparkContext.setLogLevel("WARN")
    logger.info("Spark session created")
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
    parsed = df.select(
        expr("from_json(cast(value as string), '{}')".format(schema.json())).alias("data")
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
# Cassandra Writer
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

        logger.info(f"Written batch {batch_id} to {keyspace}.{table}")

    return df.writeStream \
        .foreachBatch(write_batch) \
        .outputMode("append") \
        .option("checkpointLocation", f"/tmp/checkpoint/{table}") \
        .start()

# --------------------------------------------------
# Prepare matches
# --------------------------------------------------
def prepare_matches(df):
    return df.select(
        expr("uuid()").alias("match_id"),
        col("Season").alias("season"),
        col("Div").alias("div"),
        col("match_date").alias("date"),
        col("HomeTeam").alias("hometeam"),
        col("AwayTeam").alias("awayteam"),
        col("FTHG").alias("fthg"),
        col("FTAG").alias("ftag"),
        col("FTR").alias("ftr"),
        col("HTHG").alias("hthg"),
        col("HTAG").alias("htag"),
        col("HTR").alias("htr"),
        col("HS").alias("hs"),
        col("AS").alias("as"),
        col("HST").alias("hst"),
        col("AST").alias("ast"),
        col("HF").alias("hf"),
        col("AF").alias("af"),
        col("HC").alias("hc"),
        col("AC").alias("ac"),
        col("HY").alias("hy"),
        col("AY").alias("ay"),
        col("HR").alias("hr"),
        col("AR").alias("ar"),
        col("PSH").alias("psh"),
        col("PSD").alias("psd"),
        col("PSA").alias("psa")
    )

# --------------------------------------------------
# season_metrics
# --------------------------------------------------
def prepare_season_metrics(df):
    return df.groupBy("Season", "Div").agg(
        count("*").alias("total_matches"),
        spark_sum("TotalGoals").alias("total_goals"),
        avg("TotalGoals").alias("avg_goals"),
        spark_sum("HomeWinFlag").alias("home_wins"),
        spark_sum("AwayWinFlag").alias("away_wins"),
        spark_sum("DrawFlag").alias("draws")
    ).select(
        col("Season").alias("season"),
        col("Div").alias("div"),
        "total_matches",
        "total_goals",
        "avg_goals",
        "home_wins",
        "away_wins",
        "draws"
    )

# --------------------------------------------------
# odds_metrics
# --------------------------------------------------
def prepare_odds_metrics(df):
    return df.groupBy("Season", "Div", "match_date").agg(
        avg("PSH").alias("avg_psh"),
        avg("PSD").alias("avg_psd"),
        avg("PSA").alias("avg_psa")
    ).select(
        col("Season").alias("season"),
        col("Div").alias("div"),
        col("match_date").alias("date"),
        "avg_psh",
        "avg_psd",
        "avg_psa"
    )

# --------------------------------------------------
# team_metrics
# --------------------------------------------------
def prepare_team_metrics(df):
    home = df.select(
        col("HomeTeam").alias("team"),
        col("match_date").alias("date"),
        col("Season").alias("season"),
        col("FTHG").alias("total_goals_for"),
        col("FTAG").alias("total_goals_against"),
        col("HS").alias("shots"),
        col("HST").alias("shots_on_target"),
        col("HF").alias("fouls"),
        col("HC").alias("corners"),
        col("HY").alias("yellow"),
        col("HR").alias("red"),
        when(col("FTR") == "H", 1).otherwise(0).alias("wins"),
        when(col("FTR") == "D", 1).otherwise(0).alias("draws"),
        when(col("FTR") == "A", 1).otherwise(0).alias("losses")
    )

    away = df.select(
        col("AwayTeam").alias("team"),
        col("match_date").alias("date"),
        col("Season").alias("season"),
        col("FTAG").alias("total_goals_for"),
        col("FTHG").alias("total_goals_against"),
        col("AS").alias("shots"),
        col("AST").alias("shots_on_target"),
        col("AF").alias("fouls"),
        col("AC").alias("corners"),
        col("AY").alias("yellow"),
        col("AR").alias("red"),
        when(col("FTR") == "A", 1).otherwise(0).alias("wins"),
        when(col("FTR") == "D", 1).otherwise(0).alias("draws"),
        when(col("FTR") == "H", 1).otherwise(0).alias("losses")
    )

    daily = home.unionByName(away)

    return daily.groupBy("team", "date", "season").agg(
        spark_sum("total_goals_for").alias("total_goals_for"),
        spark_sum("total_goals_against").alias("total_goals_against"),
        spark_sum("wins").alias("wins"),
        spark_sum("draws").alias("draws"),
        spark_sum("losses").alias("losses"),
        spark_sum("shots").alias("shots"),
        spark_sum("shots_on_target").alias("shots_on_target"),
        spark_sum("fouls").alias("fouls"),
        spark_sum("corners").alias("corners"),
        spark_sum("yellow").alias("yellow"),
        spark_sum("red").alias("red")
    )

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

    q1 = write_to_cassandra(
        prepare_matches(processed),
        "football_stats",
        "matches"
    )

    q2 = write_to_cassandra(
        prepare_season_metrics(processed),
        "football_stats",
        "season_metrics"
    )

    q3 = write_to_cassandra(
        prepare_odds_metrics(processed),
        "football_stats",
        "odds_metrics"
    )

    q4 = write_to_cassandra(
        prepare_team_metrics(processed),
        "football_stats",
        "team_metrics"
    )

    spark.streams.awaitAnyTermination()

# --------------------------------------------------
if __name__ == "__main__":
    main()
