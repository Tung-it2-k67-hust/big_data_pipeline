# Sử dụng Base Image ổn định
FROM apache/spark:3.3.3

USER root

WORKDIR /app

# Cài đặt các thư viện Python từ requirements.txt
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy toàn bộ source code
COPY . /app

# Tạo thư mục cache và cấp quyền (Đoạn bạn vừa yêu cầu thêm)
RUN mkdir -p /home/spark/.ivy2/cache && \
    chmod -R 777 /home/spark/.ivy2

USER spark

# Câu lệnh chạy Spark Streaming (Đã sửa tên file script thành src/streaming_app.py)
CMD ["/opt/spark/bin/spark-submit", \
     "--master", "local[*]", \
     "--packages", "org.apache.spark:spark-sql-kafka-0-10_2.12:3.3.3,com.datastax.spark:spark-cassandra-connector_2.12:3.3.0,org.elasticsearch:elasticsearch-spark-30_2.12:8.11.0", \
     "src/streaming_app.py"]