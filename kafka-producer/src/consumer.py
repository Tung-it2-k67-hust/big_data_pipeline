from kafka import KafkaConsumer
import json
import time
import os

# Lấy EXTERNAL_IP từ env (sẽ set khi chạy script)
EXTERNAL_IP = os.getenv('KAFKA_EXTERNAL_IP', 'localhost')  # Mặc định localhost nếu không set

# Cấu hình consumer
consumer = KafkaConsumer(
    'football-stream',  # Khớp với producer.py
    bootstrap_servers=[f'{EXTERNAL_IP}:29092'],  # Khớp với KAFKA_ADVERTISED_LISTENERS trong docker-compose
    auto_offset_reset='earliest',
    enable_auto_commit=True,
    group_id='test-group',
    value_deserializer=lambda x: json.loads(x.decode('utf-8'))
)

print(f"Consumer đang lắng nghe topic 'football-stream' trên {EXTERNAL_IP}:29092...")

# Lắng nghe và in message
for message in consumer:
    print(f"Nhận được: {message.value}")
    time.sleep(1)