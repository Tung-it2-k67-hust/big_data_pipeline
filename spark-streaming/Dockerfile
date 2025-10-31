FROM bitnami/spark:3.3.0

USER root

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY src/ ./src/

ENV KAFKA_BOOTSTRAP_SERVERS=kafka:9092
ENV KAFKA_TOPIC=data-stream
ENV ELASTICSEARCH_NODES=elasticsearch
ENV ELASTICSEARCH_INDEX=events
ENV ELASTICSEARCH_AGG_INDEX=events-aggregated

CMD ["spark-submit", "--packages", "org.apache.spark:spark-sql-kafka-0-10_2.12:3.3.0,org.elasticsearch:elasticsearch-spark-30_2.12:8.4.3", "src/streaming_app.py"]
