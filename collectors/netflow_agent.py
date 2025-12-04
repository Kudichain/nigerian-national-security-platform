"""NetFlow/IPFIX collector agent for network traffic."""

import json
import logging
from typing import Optional
from datetime import datetime
from kafka import KafkaProducer
from schemas.config import get_config
from schemas.data_schemas import NetworkFlow

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class NetFlowCollector:
    """Collects NetFlow/IPFIX data and sends to Kafka."""
    
    def __init__(self) -> None:
        """Initialize NetFlow collector."""
        config = get_config()
        self.kafka_producer = KafkaProducer(
            bootstrap_servers=config.kafka.bootstrap_servers,
            value_serializer=lambda v: json.dumps(v).encode('utf-8')
        )
        self.topic = config.kafka.topic_netflow
        logger.info(f"NetFlow collector initialized, sending to topic: {self.topic}")
    
    def collect_flow(
        self,
        src_ip: str,
        dst_ip: str,
        src_port: int,
        dst_port: int,
        protocol: str,
        bytes_transferred: int,
        packets: int,
        duration_ms: int,
        flow_type: Optional[str] = None,
        ja3: Optional[str] = None,
        asn_src: Optional[int] = None,
        asn_dst: Optional[int] = None,
        geo_src: Optional[str] = None,
        geo_dst: Optional[str] = None,
    ) -> None:
        """
        Collect and send network flow event.
        
        Args:
            src_ip: Source IP address
            dst_ip: Destination IP address
            src_port: Source port
            dst_port: Destination port
            protocol: Protocol (TCP/UDP/ICMP)
            bytes_transferred: Total bytes
            packets: Total packets
            duration_ms: Flow duration in milliseconds
            flow_type: Optional flow type (DNS/HTTP/TLS)
            ja3: Optional JA3 fingerprint
            asn_src: Source ASN
            asn_dst: Destination ASN
            geo_src: Source country code
            geo_dst: Destination country code
        """
        flow = NetworkFlow(
            ts=datetime.utcnow(),
            src_ip=src_ip,
            dst_ip=dst_ip,
            src_port=src_port,
            dst_port=dst_port,
            protocol=protocol,
            bytes=bytes_transferred,
            packets=packets,
            duration_ms=duration_ms,
            flow_type=flow_type,
            ja3=ja3,
            asn_src=asn_src,
            asn_dst=asn_dst,
            geo_src=geo_src,
            geo_dst=geo_dst,
            label=None
        )
        
        self.kafka_producer.send(self.topic, flow.model_dump(mode='json'))
        logger.debug(f"Sent flow: {src_ip}:{src_port} -> {dst_ip}:{dst_port}")
    
    def close(self) -> None:
        """Close Kafka producer."""
        self.kafka_producer.flush()
        self.kafka_producer.close()
        logger.info("NetFlow collector closed")


if __name__ == "__main__":
    # Example usage
    collector = NetFlowCollector()
    
    # Simulate collecting a flow
    collector.collect_flow(
        src_ip="192.168.1.100",
        dst_ip="8.8.8.8",
        src_port=54321,
        dst_port=53,
        protocol="UDP",
        bytes_transferred=512,
        packets=2,
        duration_ms=50,
        flow_type="DNS",
        geo_src="US",
        geo_dst="US",
    )
    
    collector.close()
