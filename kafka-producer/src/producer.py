"""
Kafka Producer for Big Data Pipeline
Generates and sends sample data to Kafka topics
"""
import json
import time
import random
from datetime import datetime
from kafka import KafkaProducer
from kafka.errors import KafkaError
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class DataProducer:
    """Producer class for generating and sending data to Kafka"""
    
    def __init__(self, bootstrap_servers='kafka:9092', topic='data-stream'):
        """
        Initialize Kafka producer
        
        Args:
            bootstrap_servers (str): Kafka bootstrap servers
            topic (str): Kafka topic name
        """
        self.topic = topic
        self.producer = KafkaProducer(
            bootstrap_servers=bootstrap_servers,
            value_serializer=lambda v: json.dumps(v).encode('utf-8'),
            key_serializer=lambda k: k.encode('utf-8') if k else None
        )
        logger.info(f"Kafka Producer initialized for topic: {topic}")
    
    def generate_sample_data(self):
        """Generate sample data for the pipeline"""
        data = {
            'timestamp': datetime.utcnow().isoformat(),
            'user_id': random.randint(1000, 9999),
            'event_type': random.choice(['click', 'view', 'purchase', 'search']),
            'product_id': random.randint(100, 999),
            'price': round(random.uniform(10.0, 1000.0), 2),
            'quantity': random.randint(1, 5),
            'session_id': random.randint(10000, 99999),
            'region': random.choice(['US', 'EU', 'ASIA', 'SA']),
            'device': random.choice(['mobile', 'desktop', 'tablet'])
        }
        return data
    
    def send_message(self, key, value):
        """
        Send message to Kafka topic
        
        Args:
            key (str): Message key
            value (dict): Message value
        """
        try:
            future = self.producer.send(self.topic, key=key, value=value)
            record_metadata = future.get(timeout=10)
            logger.debug(f"Message sent to {record_metadata.topic} partition {record_metadata.partition}")
            return True
        except KafkaError as e:
            logger.error(f"Failed to send message: {e}")
            return False
    
    def run(self, interval=1):
        """
        Run the producer continuously
        
        Args:
            interval (int): Interval between messages in seconds
        """
        logger.info("Starting data production...")
        message_count = 0
        
        try:
            while True:
                data = self.generate_sample_data()
                key = f"event_{data['user_id']}"
                
                if self.send_message(key, data):
                    message_count += 1
                    if message_count % 100 == 0:
                        logger.info(f"Sent {message_count} messages")
                
                time.sleep(interval)
        except KeyboardInterrupt:
            logger.info("Shutting down producer...")
        finally:
            self.producer.close()


def main():
    """Main entry point"""
    import os
    
    bootstrap_servers = os.getenv('KAFKA_BOOTSTRAP_SERVERS', 'kafka:9092')
    topic = os.getenv('KAFKA_TOPIC', 'data-stream')
    interval = float(os.getenv('PRODUCER_INTERVAL', '1'))
    
    producer = DataProducer(bootstrap_servers=bootstrap_servers, topic=topic)
    producer.run(interval=interval)


if __name__ == '__main__':
    main()
