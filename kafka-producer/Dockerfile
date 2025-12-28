FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY src/ ./src/

# Copy dataset into image
# COPY full_dataset.csv /app/data/full_dataset.csv

# CSV file will be mounted as volume in docker-compose
# from ./archive/full_dataset.csv to /app/archive/full_dataset.csv

ENV KAFKA_BOOTSTRAP_SERVERS=kafka:9092
ENV KAFKA_TOPIC=data-stream
ENV PRODUCER_INTERVAL=1
ENV CSV_FILE_PATH=/app/archive/full_dataset.csv

CMD ["python", "src/producer.py"]
