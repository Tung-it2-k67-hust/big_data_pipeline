from kafka import KafkaConsumer
import json
import time
import os

# Lấy EXTERNAL_IP từ env (sẽ set khi chạy script)
EXTERNAL_IP = os.getenv('KAFKA_EXTERNAL_IP', 'localhost')  # Mặc định localhost nếu không set

# Cấu hình consumer
consumer = KafkaConsumer(
    'data-stream',  # Tên topic
    bootstrap_servers=[f'{EXTERNAL_IP}:9094'],  # Sử dụng IP từ env
    auto_offset_reset='earliest',
    enable_auto_commit=True,
    group_id='test-group',
    value_deserializer=lambda x: json.loads(x.decode('utf-8'))
)

print(f"Consumer đang lắng nghe topic 'data-stream' trên {EXTERNAL_IP}:9094...")

# Lắng nghe và in message
for message in consumer:
    print(f"Nhận được: {message.value}")
    time.sleep(1)