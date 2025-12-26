"""
Kafka Producer for Big Data Pipeline
Reads football match data from CSV and sends to Kafka topic
"""
import json
import time
import os
import csv
import logging
from pathlib import Path
from kafka import KafkaProducer
from kafka.errors import KafkaError

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class FootballDataProducer:
    """Producer class for reading CSV and sending football match data to Kafka"""
    
    def __init__(self, bootstrap_servers=None, topic='data-stream', csv_file_path=None):
        """
        Initialize Kafka producer
        
        Args:
            bootstrap_servers (str): Kafka bootstrap servers
            topic (str): Kafka topic name
            csv_file_path (str): Path to CSV file
        """
        self.topic = topic
        self.csv_file_path = csv_file_path or self._get_csv_path()
        
        # Get bootstrap servers from env or use default
        if bootstrap_servers is None:
            kafka_ip = os.getenv('KAFKA_EXTERNAL_IP', 'localhost')
            bootstrap_servers = f'{kafka_ip}:9094'
        
        logger.info(f"Connecting to Kafka at: {bootstrap_servers}")
        
        # Initialize Kafka producer
        self.producer = KafkaProducer(
            bootstrap_servers=bootstrap_servers,
            value_serializer=lambda v: json.dumps(v).encode('utf-8'),
            key_serializer=lambda k: k.encode('utf-8') if k else None,
            # Add retry and timeout configurations
            retries=3,
            acks='all',  # Wait for all replicas to acknowledge
            max_in_flight_requests_per_connection=1,  # Ensure ordering
            enable_idempotence=True,  # Ensure exactly-once semantics
            # Wait for metadata to be available
            metadata_max_age_ms=30000,
            # Increase timeout for topic creation
            request_timeout_ms=30000,
            # Retry on topic not available
            retry_backoff_ms=1000
        )
        logger.info(f"Kafka Producer initialized for topic: {topic}")
        logger.info(f"CSV file path: {self.csv_file_path}")
        # Topic will be auto-created when first message is sent
    
    def _get_csv_path(self):
        """Get CSV file path from environment or use default"""
        # First check environment variable
        env_path = os.getenv('CSV_FILE_PATH')
        if env_path and os.path.exists(env_path):
            return os.path.abspath(env_path)
        
        # Get the directory of this script
        script_dir = os.path.dirname(os.path.abspath(__file__))
        # Go up 2 levels: src -> kafka-producer -> project root
        project_root = os.path.abspath(os.path.join(script_dir, '../..'))
        
        # Try multiple possible paths
        possible_paths = [
            os.path.join(project_root, 'archive', 'full_dataset.csv'),  # From project root (most likely)
            os.path.join(os.path.dirname(script_dir), '..', 'archive', 'full_dataset.csv'),  # Alternative
            '../archive/full_dataset.csv',  # Relative from kafka-producer/src
            '../../archive/full_dataset.csv',  # From kafka-producer
            'archive/full_dataset.csv',  # From current working directory
            '/app/full_dataset.csv',  # Docker path
        ]
        
        for path in possible_paths:
            # Convert to absolute path
            if os.path.isabs(path):
                abs_path = path
            else:
                # Try relative to project root first
                abs_path = os.path.join(project_root, path)
                if not os.path.exists(abs_path):
                    # Try relative to current working directory
                    abs_path = os.path.abspath(path)
            
            if os.path.exists(abs_path):
                logger.info(f"Found CSV file at: {abs_path}")
                return abs_path
        
        # If not found, raise error with helpful message
        current_dir = os.getcwd()
        error_msg = (
            f"CSV file not found.\n"
            f"Current working directory: {current_dir}\n"
            f"Script directory: {script_dir}\n"
            f"Project root: {project_root}\n"
            f"Expected path: {os.path.join(project_root, 'archive', 'full_dataset.csv')}\n"
            f"Please set CSV_FILE_PATH environment variable or place file in archive/ directory"
        )
        raise FileNotFoundError(error_msg)
    
    def _parse_row(self, row):
        """
        Parse CSV row and convert to JSON format
        Handles empty values and converts types appropriately
        """
        match_data = {
            'Season': row.get('Season', '').strip(),
            'Div': row.get('Div', '').strip(),
            'Date': row.get('Date', '').strip(),
            'HomeTeam': row.get('HomeTeam', '').strip(),
            'AwayTeam': row.get('AwayTeam', '').strip(),
            'FTHG': self._safe_float(row.get('FTHG')),
            'FTAG': self._safe_float(row.get('FTAG')),
            'FTR': row.get('FTR', '').strip(),
            'HTHG': self._safe_float(row.get('HTHG')),
            'HTAG': self._safe_float(row.get('HTAG')),
            'HTR': row.get('HTR', '').strip(),
            'HS': self._safe_int(row.get('HS')),
            'AS': self._safe_int(row.get('AS')),
            'HST': self._safe_int(row.get('HST')),
            'AST': self._safe_int(row.get('AST')),
            'HF': self._safe_int(row.get('HF')),
            'AF': self._safe_int(row.get('AF')),
            'HC': self._safe_int(row.get('HC')),
            'AC': self._safe_int(row.get('AC')),
            'HY': self._safe_int(row.get('HY')),
            'AY': self._safe_int(row.get('AY')),
            'HR': self._safe_int(row.get('HR')),
            'AR': self._safe_int(row.get('AR')),
            'PSH': self._safe_float(row.get('PSH')),
            'PSD': self._safe_float(row.get('PSD')),
            'PSA': self._safe_float(row.get('PSA'))
        }
        
        # Remove None values to keep JSON clean
        return {k: v for k, v in match_data.items() if v is not None}
    
    def _safe_int(self, value):
        """Safely convert value to int, return None if empty or invalid"""
        if not value or value.strip() == '':
            return None
        try:
            # Handle float strings like "1.0"
            return int(float(value))
        except (ValueError, TypeError):
            return None
    
    def _safe_float(self, value):
        """Safely convert value to float, return None if empty or invalid"""
        if not value or value.strip() == '':
            return None
        try:
            return float(value)
        except (ValueError, TypeError):
            return None
    
    def read_csv_file(self):
        """Read and yield football match records from CSV file"""
        if not os.path.exists(self.csv_file_path):
            raise FileNotFoundError(f"CSV file not found: {self.csv_file_path}")
        
        logger.info(f"Reading CSV file: {self.csv_file_path}")
        record_count = 0
        
        with open(self.csv_file_path, 'r', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)
            
            for row in reader:
                # Skip empty rows
                if not row.get('HomeTeam') or not row.get('AwayTeam'):
                    continue
                
                match_data = self._parse_row(row)
                
                # Only yield if we have at least HomeTeam and AwayTeam
                if match_data.get('HomeTeam') and match_data.get('AwayTeam'):
                    record_count += 1
                    yield match_data
        
        logger.info(f"Total records read from CSV: {record_count}")
    
    def send_message(self, key, value):
        """
        Send message to Kafka topic
        
        Args:
            key (str): Message key (e.g., match_id or team combination)
            value (dict): Message value (match data)
        """
        try:
            future = self.producer.send(self.topic, key=key, value=value)
            record_metadata = future.get(timeout=10)
            logger.debug(
                f"Message sent to topic={record_metadata.topic} "
                f"partition={record_metadata.partition} "
                f"offset={record_metadata.offset}"
            )
            return True
        except KafkaError as e:
            logger.error(f"Failed to send message: {e}")
            return False
    
    def run(self, batch_size=500, sleep_time=0.3, loop=False):
        """
        Start sending messages to Kafka in burst batches (simulated realtime streaming)
        
        Args:
            batch_size (int): Number of messages to send in each burst batch
            sleep_time (float): Time to pause between batches (seconds)
            loop (bool): Whether to loop through the CSV file continuously
        """
        logger.info("Starting simulated realtime producer with burst batches...")
        logger.info(f"Configuration: batch_size={batch_size}, sleep_time={sleep_time}s, loop={loop}")
        
        message_count = 0
        batch_count = 0
        
        try:
            while True:
                for match_data in self.read_csv_file():
                    # Create a key from match info for partitioning
                    key = f"{match_data.get('Date', '')}_{match_data.get('HomeTeam', '')}_{match_data.get('AwayTeam', '')}"
                    
                    # Send async (no waiting for acknowledgment within batch)
                    self.producer.send(self.topic, key=key, value=match_data)
                    message_count += 1
                    
                    # Every batch_size messages
                    if message_count % batch_size == 0:
                        batch_count += 1
                        
                        # Flush to push batch to broker
                        self.producer.flush()
                        
                        logger.info(
                            f"📦 Batch {batch_count} sent "
                            f"({message_count} messages total) - "
                            f"Last: {match_data.get('HomeTeam')} vs {match_data.get('AwayTeam')}"
                        )
                        
                        # Pause to simulate realtime streaming with burst pattern
                        time.sleep(sleep_time)
                
                # Final flush for remaining messages
                if message_count % batch_size != 0:
                    self.producer.flush()
                    batch_count += 1
                    logger.info(f"📦 Final batch {batch_count} sent (total: {message_count} messages)")
                
                if not loop:
                    logger.info(f"✅ Finished sending all {message_count} messages in {batch_count} batches")
                    logger.info("All data has been sent. Producer will exit gracefully.")
                    break
                else:
                    logger.info("🔄 Looping back to start of CSV file...")
                    message_count = 0
                    batch_count = 0
                    
        except KeyboardInterrupt:
            logger.info("Shutting down producer...")
        except Exception as e:
            logger.error(f"Error in producer: {e}", exc_info=True)
        finally:
            self.producer.flush()  # Ensure all messages are sent
            self.producer.close()
            logger.info("Producer closed")


def main():
    """Main entry point"""
    import os
    
    bootstrap_servers = os.getenv('KAFKA_BOOTSTRAP_SERVERS', 'kafka:9092')
    topic = os.getenv('KAFKA_TOPIC', 'data-stream')
    batch_size = int(os.getenv('BATCH_SIZE', '500'))
    sleep_time = float(os.getenv('SLEEP_TIME', '0.3'))
    csv_file_path = os.getenv('CSV_FILE_PATH')
    loop = os.getenv('PRODUCER_LOOP', 'false').lower() == 'true'
    
    try:
        producer = FootballDataProducer(
            bootstrap_servers=bootstrap_servers,
            topic=topic,
            csv_file_path=csv_file_path
        )
        producer.run(batch_size=batch_size, sleep_time=sleep_time, loop=loop)
    except FileNotFoundError as e:
        logger.error(f"CSV file not found: {e}")
        logger.error("Please set CSV_FILE_PATH environment variable or place file in archive/ directory")
        exit(1)
    except Exception as e:
        logger.error(f"Failed to start producer: {e}", exc_info=True)
        exit(1)


if __name__ == '__main__':
    main()
