"""NetFlow parser for normalizing network flow data."""

import json
import logging
from typing import Dict, Any, Optional
from datetime import datetime
from schemas.data_schemas import NetworkFlow

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class NetFlowParser:
    """Parse and normalize NetFlow/IPFIX records."""
    
    @staticmethod
    def parse_netflow_v9(raw_record: Dict[str, Any]) -> Optional[NetworkFlow]:
        """
        Parse NetFlow v9 record to normalized schema.
        
        Args:
            raw_record: Raw NetFlow v9 record
            
        Returns:
            Normalized NetworkFlow object or None if invalid
        """
        try:
            return NetworkFlow(
                ts=datetime.fromtimestamp(raw_record.get('unix_secs', 0)),
                src_ip=raw_record['IPV4_SRC_ADDR'],
                dst_ip=raw_record['IPV4_DST_ADDR'],
                src_port=raw_record.get('L4_SRC_PORT', 0),
                dst_port=raw_record.get('L4_DST_PORT', 0),
                protocol=NetFlowParser._protocol_number_to_name(
                    raw_record.get('PROTOCOL', 0)
                ),
                bytes=raw_record.get('IN_BYTES', 0),
                packets=raw_record.get('IN_PKTS', 0),
                duration_ms=raw_record.get('LAST_SWITCHED', 0) - 
                           raw_record.get('FIRST_SWITCHED', 0),
                flow_type=NetFlowParser._detect_flow_type(
                    raw_record.get('L4_DST_PORT', 0)
                ),
                ja3=None,
                asn_src=None,
                asn_dst=None,
                geo_src=None,
                geo_dst=None,
                label=None
            )
        except (KeyError, ValueError) as e:
            logger.error(f"Failed to parse NetFlow record: {e}")
            return None
    
    @staticmethod
    def parse_ipfix(raw_record: Dict[str, Any]) -> Optional[NetworkFlow]:
        """
        Parse IPFIX record to normalized schema.
        
        Args:
            raw_record: Raw IPFIX record
            
        Returns:
            Normalized NetworkFlow object or None if invalid
        """
        try:
            return NetworkFlow(
                ts=datetime.fromisoformat(raw_record['flowStartMilliseconds']),
                src_ip=raw_record['sourceIPv4Address'],
                dst_ip=raw_record['destinationIPv4Address'],
                src_port=raw_record.get('sourceTransportPort', 0),
                dst_port=raw_record.get('destinationTransportPort', 0),
                protocol=NetFlowParser._protocol_number_to_name(
                    raw_record.get('protocolIdentifier', 0)
                ),
                bytes=raw_record.get('octetDeltaCount', 0),
                packets=raw_record.get('packetDeltaCount', 0),
                duration_ms=int(
                    (datetime.fromisoformat(raw_record['flowEndMilliseconds']) -
                     datetime.fromisoformat(raw_record['flowStartMilliseconds']))
                    .total_seconds() * 1000
                ),
                flow_type=None,
                ja3=None,
                asn_src=None,
                asn_dst=None,
                geo_src=None,
                geo_dst=None,
                label=None
            )
        except (KeyError, ValueError) as e:
            logger.error(f"Failed to parse IPFIX record: {e}")
            return None
    
    @staticmethod
    def _protocol_number_to_name(protocol_num: int) -> str:
        """Convert protocol number to name."""
        protocol_map = {
            1: 'ICMP',
            6: 'TCP',
            17: 'UDP',
            47: 'GRE',
            50: 'ESP',
            51: 'AH',
        }
        return protocol_map.get(protocol_num, f'PROTOCOL_{protocol_num}')
    
    @staticmethod
    def _detect_flow_type(dst_port: int) -> Optional[str]:
        """Detect flow type based on destination port."""
        port_map = {
            53: 'DNS',
            80: 'HTTP',
            443: 'HTTPS',
            22: 'SSH',
            21: 'FTP',
            25: 'SMTP',
            3389: 'RDP',
        }
        return port_map.get(dst_port)


# Kafka consumer integration
def consume_and_parse_netflow(kafka_topic: str = "raw.netflow") -> None:
    """
    Consume raw NetFlow from Kafka and publish normalized events.
    
    Args:
        kafka_topic: Kafka topic with raw NetFlow data
    """
    from kafka import KafkaConsumer, KafkaProducer
    from schemas.config import get_config
    
    config = get_config()
    
    consumer = KafkaConsumer(
        kafka_topic,
        bootstrap_servers=config.kafka.bootstrap_servers,
        value_deserializer=lambda m: json.loads(m.decode('utf-8')),
        group_id='netflow-parser',
    )
    
    producer = KafkaProducer(
        bootstrap_servers=config.kafka.bootstrap_servers,
        value_serializer=lambda v: json.dumps(v).encode('utf-8')
    )
    
    parser = NetFlowParser()
    
    for message in consumer:
        raw_record = message.value
        
        # Try parsing as NetFlow v9 first, then IPFIX
        flow = parser.parse_netflow_v9(raw_record)
        if not flow:
            flow = parser.parse_ipfix(raw_record)
        
        if flow:
            producer.send(config.kafka.topic_netflow, flow.model_dump(mode='json'))
            logger.debug(f"Parsed and sent flow: {flow.src_ip} -> {flow.dst_ip}")


if __name__ == "__main__":
    logger.info("Starting NetFlow parser...")
    consume_and_parse_netflow()
