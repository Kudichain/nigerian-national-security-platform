"""Authentication event collector."""

import json
import logging
from typing import Optional
from datetime import datetime
from kafka import KafkaProducer
from schemas.config import get_config
from schemas.data_schemas import AuthEvent

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class AuthCollector:
    """Collects authentication events for risk scoring."""
    
    def __init__(self) -> None:
        """Initialize auth collector."""
        config = get_config()
        self.kafka_producer = KafkaProducer(
            bootstrap_servers=config.kafka.bootstrap_servers,
            value_serializer=lambda v: json.dumps(v).encode('utf-8')
        )
        self.topic = config.kafka.topic_auth
        logger.info(f"Auth collector initialized, sending to topic: {self.topic}")
    
    def collect_auth_event(
        self,
        user_id: str,
        ip: str,
        event_type: str,
        device_id: Optional[str] = None,
        geo: Optional[str] = None,
        user_agent: Optional[str] = None,
        mfa_used: bool = False,
    ) -> None:
        """
        Collect and send authentication event.
        
        Args:
            user_id: User identifier
            ip: Source IP address
            event_type: Event type (login_success/login_fail/token_refresh)
            device_id: Optional device fingerprint
            geo: Optional country code
            user_agent: Optional user agent string
            mfa_used: Whether MFA was used
        """
        auth_event = AuthEvent(
            ts=datetime.utcnow(),
            user_id=user_id,
            ip=ip,
            event_type=event_type,
            device_id=device_id,
            geo=geo,
            ua=user_agent,
            mfa_used=mfa_used,
            risk_score=None,
            label=None
        )
        
        self.kafka_producer.send(self.topic, auth_event.model_dump(mode='json'))
        logger.debug(f"Sent auth event: {event_type} for user {user_id}")
    
    def close(self) -> None:
        """Close Kafka producer."""
        self.kafka_producer.flush()
        self.kafka_producer.close()
        logger.info("Auth collector closed")


if __name__ == "__main__":
    # Example usage
    collector = AuthCollector()
    
    # Simulate suspicious login from new location
    collector.collect_auth_event(
        user_id="user12345",
        ip="198.51.100.42",
        event_type="login_success",
        device_id="new_device_fingerprint",
        geo="RU",  # New country
        user_agent="Mozilla/5.0...",
        mfa_used=False,  # Suspicious: no MFA
    )
    
    collector.close()
