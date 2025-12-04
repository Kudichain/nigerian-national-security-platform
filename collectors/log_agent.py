"""Log collector agent for SIEM integration."""

import json
import logging
from typing import Optional
from datetime import datetime
from kafka import KafkaProducer
from schemas.config import get_config
from schemas.data_schemas import LogEvent

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class LogCollector:
    """Collects logs from various sources and sends to Kafka."""
    
    def __init__(self) -> None:
        """Initialize log collector."""
        config = get_config()
        self.kafka_producer = KafkaProducer(
            bootstrap_servers=config.kafka.bootstrap_servers,
            value_serializer=lambda v: json.dumps(v).encode('utf-8')
        )
        self.topic = config.kafka.topic_logs
        logger.info(f"Log collector initialized, sending to topic: {self.topic}")
    
    def collect_event(
        self,
        host: str,
        event_id: str,
        event_type: str,
        message: str,
        user: Optional[str] = None,
        process: Optional[str] = None,
        cmdline: Optional[str] = None,
        status: Optional[str] = None,
        src_ip: Optional[str] = None,
        dst_ip: Optional[str] = None,
        session_id: Optional[str] = None,
    ) -> None:
        """
        Collect and send log event.
        
        Args:
            host: Source hostname
            event_id: Event identifier
            event_type: Event type/category
            message: Log message
            user: Optional username
            process: Optional process name
            cmdline: Optional command line
            status: Optional status (success/failure)
            src_ip: Optional source IP
            dst_ip: Optional destination IP
            session_id: Optional session ID
        """
        log_event = LogEvent(
            ts=datetime.utcnow(),
            host=host,
            event_id=event_id,
            event_type=event_type,
            message=message,
            user=user,
            process=process,
            cmdline=cmdline,
            status=status,
            src_ip=src_ip,
            dst_ip=dst_ip,
            session_id=session_id,
            label=None,
        )
        
        self.kafka_producer.send(self.topic, log_event.model_dump(mode='json'))
        logger.debug(f"Sent log event: {event_type} from {host}")
    
    def close(self) -> None:
        """Close Kafka producer."""
        self.kafka_producer.flush()
        self.kafka_producer.close()
        logger.info("Log collector closed")


if __name__ == "__main__":
    # Example usage
    collector = LogCollector()
    
    # Simulate collecting a login failure
    collector.collect_event(
        host="webserver-01",
        event_id="4625",
        event_type="AUTH_FAIL",
        message="Failed login attempt for user admin",
        user="admin",
        src_ip="203.0.113.42",
        status="failure",
    )
    
    collector.close()
