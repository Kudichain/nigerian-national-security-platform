"""Email collector for phishing detection."""

import json
import logging
from typing import List, Optional
from datetime import datetime
from kafka import KafkaProducer
from schemas.config import get_config
from schemas.data_schemas import EmailMessage

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class EmailCollector:
    """Collects emails for phishing analysis."""
    
    def __init__(self) -> None:
        """Initialize email collector."""
        config = get_config()
        self.kafka_producer = KafkaProducer(
            bootstrap_servers=config.kafka.bootstrap_servers,
            value_serializer=lambda v: json.dumps(v).encode('utf-8')
        )
        self.topic = config.kafka.topic_email
        logger.info(f"Email collector initialized, sending to topic: {self.topic}")
    
    def collect_email(
        self,
        msg_id: str,
        from_addr: str,
        to_addrs: List[str],
        subject: str,
        body_text: Optional[str] = None,
        body_html: Optional[str] = None,
        attachments: Optional[List[str]] = None,
        spf_result: Optional[str] = None,
        dkim_result: Optional[str] = None,
        dmarc_result: Optional[str] = None,
        urls: Optional[List[str]] = None,
    ) -> None:
        """
        Collect and send email for analysis.
        
        Args:
            msg_id: Unique message ID
            from_addr: Sender address
            to_addrs: Recipient addresses
            subject: Email subject
            body_text: Plain text body
            body_html: HTML body
            attachments: List of attachment hashes
            spf_result: SPF check result
            dkim_result: DKIM check result
            dmarc_result: DMARC check result
            urls: Extracted URLs
        """
        email = EmailMessage(
            msg_id=msg_id,
            ts=datetime.utcnow(),
            **{"from": from_addr},
            to=to_addrs,
            subject=subject,
            body_text=body_text or "",
            body_html=body_html,
            attachments=attachments or [],
            spf_result=spf_result,
            dkim_result=dkim_result,
            dmarc_result=dmarc_result,
            urls=urls or [],
            label=None
        )
        
        self.kafka_producer.send(self.topic, email.model_dump(mode='json'))
        logger.debug(f"Sent email: {msg_id} from {from_addr}")
    
    def close(self) -> None:
        """Close Kafka producer."""
        self.kafka_producer.flush()
        self.kafka_producer.close()
        logger.info("Email collector closed")


if __name__ == "__main__":
    # Example usage
    collector = EmailCollector()
    
    # Simulate collecting a suspicious email
    collector.collect_email(
        msg_id="<12345@example.com>",
        from_addr="admin@paypa1.com",  # Note: suspicious domain
        to_addrs=["user@company.com"],
        subject="Urgent: Verify your account",
        body_text="Click here to verify your account or it will be suspended.",
        urls=["http://paypa1-verify.xyz/login"],
        spf_result="fail",
        dkim_result="none",
        dmarc_result="fail",
    )
    
    collector.close()
