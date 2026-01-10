"""
Kafka Producer cho Big Data Pipeline
Đọc dữ liệu bóng đá từ file CSV và gửi đến Kafka topic
"""
import json
import time
import os
import csv
import logging
from pathlib import Path
from kafka import KafkaProducer
from kafka.errors import KafkaError

# Cấu hình logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class FootballDataProducer:
    """Lớp Producer để đọc CSV và gửi dữ liệu trận đấu bóng đá đến Kafka"""
    
    def __init__(self, bootstrap_servers=None, topic='football-stream', csv_file_path=None):
        """
        Khởi tạo Kafka producer
        
        Args:
            bootstrap_servers (str): Địa chỉ Kafka bootstrap servers
            topic (str): Tên Kafka topic
            csv_file_path (str): Đường dẫn đến file CSV
        """
        self.topic = topic
        self.csv_file_path = csv_file_path or self._get_csv_path()
        
        # Lấy bootstrap servers từ biến môi trường hoặc dùng mặc định
        if bootstrap_servers is None:
            # Ưu tiên biến KAFKA_BOOTSTRAP_SERVERS, sau đó đến KAFKA_EXTERNAL_IP cho tương thích ngược
            bootstrap_servers = os.getenv('KAFKA_BOOTSTRAP_SERVERS')
            if not bootstrap_servers:
                kafka_ip = os.getenv('KAFKA_EXTERNAL_IP', 'localhost')
                bootstrap_servers = f'{kafka_ip}:9094'
        
        logger.info(f"Đang kết nối đến Kafka tại: {bootstrap_servers}")
        
        # Khởi tạo Kafka producer với cơ chế thử lại (retry)
        max_retries = 10
        retry_delay = 5
        
        for attempt in range(max_retries):
            try:
                self.producer = KafkaProducer(
                    bootstrap_servers=bootstrap_servers,
                    value_serializer=lambda v: json.dumps(v).encode('utf-8'),
                    key_serializer=lambda k: k.encode('utf-8') if k else None,
                    # Cấu hình retry và timeout
                    retries=3,
                    acks='all',  # Đợi tất cả replicas xác nhận
                    max_in_flight_requests_per_connection=1,  # Đảm bảo thứ tự
                    enable_idempotence=True,  # Đảm bảo exactly-once semantics
                    metadata_max_age_ms=30000,
                    request_timeout_ms=30000,
                    retry_backoff_ms=1000
                )
                logger.info("Kết nối Kafka thành công")
                break
            except KafkaError as e:
                if attempt < max_retries - 1:
                    logger.warning(f"Kết nối Kafka thất bại (Lần {attempt+1}/{max_retries}): {e}. Thử lại sau {retry_delay}s...")
                    time.sleep(retry_delay)
                else:
                    logger.error(f"Không thể kết nối đến Kafka sau {max_retries} lần thử")
                    raise e
        logger.info(f"Kafka Producer đã khởi tạo cho topic: {topic}")
        logger.info(f"Đường dẫn file CSV: {self.csv_file_path}")
    
    def _get_csv_path(self):
        """Lấy đường dẫn file CSV từ biến môi trường hoặc tìm kiếm mặc định"""
        # Kiểm tra biến môi trường trước
        env_path = os.getenv('CSV_FILE_PATH')
        if env_path and os.path.exists(env_path):
            return os.path.abspath(env_path)
        
        # Lấy thư mục chứa script hiện tại
        script_dir = os.path.dirname(os.path.abspath(__file__))
        # Lên 2 cấp: src -> kafka-producer -> project root
        project_root = os.path.abspath(os.path.join(script_dir, '../..'))
        
        # Các đường dẫn có thể
        possible_paths = [
            os.path.join(project_root, 'archive', 'full_dataset.csv'),
            os.path.join(os.path.dirname(script_dir), '..', 'archive', 'full_dataset.csv'),
            'archive/full_dataset.csv',
            '/app/archive/full_dataset.csv',
        ]
        
        for path in possible_paths:
            abs_path = os.path.abspath(path) if not os.path.isabs(path) else path
            if os.path.exists(abs_path):
                logger.info(f"Tìm thấy file CSV tại: {abs_path}")
                return abs_path
        
        # Nếu không tìm thấy
        raise FileNotFoundError(
            f"Không tìm thấy file CSV.\n"
            f"Đã tìm tại: {possible_paths}\n"
            f"Vui lòng đặt biến môi trường CSV_FILE_PATH hoặc đặt file vào thư mục archive/"
        )
    
    def _parse_row(self, row):
        """
        Phân tích dòng CSV và chuyển đổi sang định dạng JSON
        Xử lý giá trị rỗng và chuyển đổi kiểu dữ liệu phù hợp
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
        
        # Loại bỏ các giá trị None để giữ JSON sạch
        return {k: v for k, v in match_data.items() if v is not None}
    
    def _safe_int(self, value):
        """Chuyển đổi an toàn sang int, trả về None nếu lỗi"""
        if not value or value.strip() == '':
            return None
        try:
            return int(float(value))
        except (ValueError, TypeError):
            return None
    
    def _safe_float(self, value):
        """Chuyển đổi an toàn sang float, trả về None nếu lỗi"""
        if not value or value.strip() == '':
            return None
        try:
            return float(value)
        except (ValueError, TypeError):
            return None
    
    def read_csv_file(self):
        """Đọc và yield từng bản ghi trận đấu từ file CSV"""
        if not os.path.exists(self.csv_file_path):
            raise FileNotFoundError(f"Không tìm thấy file CSV: {self.csv_file_path}")
        
        logger.info(f"Đang đọc file CSV: {self.csv_file_path}")
        record_count = 0
        
        with open(self.csv_file_path, 'r', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)
            
            for row in reader:
                # Bỏ qua dòng trống
                if not row.get('HomeTeam') or not row.get('AwayTeam'):
                    continue
                
                match_data = self._parse_row(row)
                
                # Chỉ yield nếu có đủ thông tin đội nhà và đội khách
                if match_data.get('HomeTeam') and match_data.get('AwayTeam'):
                    record_count += 1
                    yield match_data
        
        logger.info(f"Tổng số bản ghi đã đọc: {record_count}")
    
    def send_message(self, key, value):
        """
        Gửi message đến Kafka topic
        
        Args:
            key (str): Message key (ví dụ: match_id hoặc tổ hợp tên đội)
            value (dict): Message value (dữ liệu trận đấu)
        """
        try:
            future = self.producer.send(self.topic, key=key, value=value)
            record_metadata = future.get(timeout=10)
            logger.debug(
                f"Đã gửi message đến topic={record_metadata.topic} "
                f"partition={record_metadata.partition} "
                f"offset={record_metadata.offset}"
            )
            return True
        except KafkaError as e:
            logger.error(f"Gửi message thất bại: {e}")
            return False
    
    def run(self, batch_size=500, sleep_time=0.3, loop=False):
        """
        Bắt đầu gửi message đến Kafka theo lô (giả lập streaming)
            
        Args:
            batch_size (int): Số lượng message gửi trong mỗi lô
            sleep_time (float): Thời gian nghỉ giữa các lô (giây)
            loop (bool): Có lặp lại file CSV khi đọc hết không
        """
        logger.info("Bắt đầu giả lập streaming với chế độ gửi theo lô...")
        logger.info(f"Cấu hình: batch_size={batch_size}, sleep_time={sleep_time}s, loop={loop}")
        
        message_count = 0
        batch_count = 0
        
        try:
            while True:
                for match_data in self.read_csv_file():
                    # Tạo key từ thông tin trận đấu để phân chia partition
                    key = f"{match_data.get('Date', '')}_{match_data.get('HomeTeam', '')}_{match_data.get('AwayTeam', '')}"
                    
                    # Gửi bất đồng bộ (không đợi xác nhận ngay lập tức)
                    self.producer.send(self.topic, key=key, value=match_data)
                    message_count += 1
                    
                    # Mỗi khi đủ batch_size message
                    if message_count % batch_size == 0:
                        batch_count += 1
                        
                        # Flush để đẩy lô message đi
                        self.producer.flush()
                        
                        logger.info(
                            f"📦 Lô {batch_count} đã gửi "
                            f"(Tổng: {message_count} messages) - "
                            f"Cuối: {match_data.get('HomeTeam')} vs {match_data.get('AwayTeam')}"
                        )

                        # Nghỉ để giả lập tốc độ streaming
                        time.sleep(sleep_time)
                
                # Flush lần cuối cho các message còn lại
                if message_count % batch_size != 0:
                    self.producer.flush()
                    batch_count += 1
                    logger.info(f"📦 Lô cuối {batch_count} đã gửi (Tổng: {message_count} messages)")
                
                if not loop:
                    logger.info(f"✅ Đã gửi xong toàn bộ {message_count} messages trong {batch_count} lô")
                    logger.info("Producer sẽ kết thúc.")
                    break
                else:
                    logger.info("🔄 Lặp lại từ đầu file CSV...")
                    message_count = 0
                    batch_count = 0
                    
        except KeyboardInterrupt:
            logger.info("Đang dừng producer...")
        except Exception as e:
            logger.error(f"Lỗi trong producer: {e}", exc_info=True)
        finally:
            self.producer.flush()  # Đảm bảo gửi hết message
            self.producer.close()
            logger.info("Producer đã đóng")


def main():
    """Hàm chính"""
    import os
    
    # Lấy cấu hình từ biến môi trường
    bootstrap_servers = os.getenv('KAFKA_BOOTSTRAP_SERVERS', 'kafka:9092')
    topic = os.getenv('KAFKA_TOPIC', 'football-stream')
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
        logger.error(f"Lỗi file CSV: {e}")
        logger.error("Vui lòng đặt biến môi trường CSV_FILE_PATH hoặc đặt file vào thư mục archive/")
        exit(1)
    except Exception as e:
        logger.error(f"Không thể khởi động producer: {e}", exc_info=True)
        exit(1)


if __name__ == '__main__':
    main()
