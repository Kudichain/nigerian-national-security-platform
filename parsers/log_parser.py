"""Log parser for normalizing various log formats to ECS schema."""

import json
import re
import logging
from typing import Dict, Any, Optional
from datetime import datetime
from schemas.data_schemas import LogEvent

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class LogParser:
    """Parse and normalize logs from various sources to ECS-compatible schema."""
    
    @staticmethod
    def parse_windows_event(raw_log: Dict[str, Any]) -> Optional[LogEvent]:
        """
        Parse Windows Event Log to normalized schema.
        
        Args:
            raw_log: Raw Windows Event Log record
            
        Returns:
            Normalized LogEvent or None if invalid
        """
        try:
            return LogEvent(
                ts=datetime.fromisoformat(raw_log['TimeCreated']),
                host=raw_log.get('Computer', 'unknown'),
                event_id=str(raw_log['EventID']),
                event_type=LogParser._map_windows_event_type(raw_log['EventID']),
                message=raw_log.get('Message', ''),
                user=raw_log.get('UserData', {}).get('TargetUserName'),
                src_ip=raw_log.get('UserData', {}).get('IpAddress'),
                status=LogParser._map_windows_status(raw_log.get('Keywords')),
                process=None,
                cmdline=None,
                dst_ip=None,
                session_id=None,
                label=None
            )
        except (KeyError, ValueError) as e:
            logger.error(f"Failed to parse Windows event: {e}")
            return None
    
    @staticmethod
    def parse_syslog(raw_log: str) -> Optional[LogEvent]:
        """
        Parse syslog message to normalized schema.
        
        Args:
            raw_log: Raw syslog string
            
        Returns:
            Normalized LogEvent or None if invalid
        """
        # Simple syslog pattern (RFC 3164)
        pattern = r'<(\d+)>(\w+\s+\d+\s+\d+:\d+:\d+)\s+(\S+)\s+(\S+):\s+(.+)'
        match = re.match(pattern, raw_log)
        
        if not match:
            logger.error(f"Failed to parse syslog: {raw_log[:100]}")
            return None
        
        try:
            priority, timestamp_str, host, process, message = match.groups()
            
            # Parse timestamp (simplified - assumes current year)
            ts = datetime.strptime(
                f"{datetime.now().year} {timestamp_str}",
                "%Y %b %d %H:%M:%S"
            )
            
            return LogEvent(
                ts=ts,
                host=host,
                event_id=f"syslog_{priority}",
                event_type=LogParser._map_syslog_facility(int(priority)),
                process=process,
                message=message,
                user=None,
                cmdline=None,
                status=None,
                src_ip=None,
                dst_ip=None,
                session_id=None,
                label=None
            )
        except (ValueError, IndexError) as e:
            logger.error(f"Failed to parse syslog timestamp: {e}")
            return None
    
    @staticmethod
    def parse_json_log(raw_log: Dict[str, Any]) -> Optional[LogEvent]:
        """
        Parse JSON-formatted log (e.g., from containers, modern apps).
        
        Args:
            raw_log: Raw JSON log record
            
        Returns:
            Normalized LogEvent or None if invalid
        """
        try:
            return LogEvent(
                ts=datetime.fromisoformat(raw_log.get('timestamp', 
                                          raw_log.get('time', datetime.utcnow().isoformat()))),
                host=raw_log.get('host', raw_log.get('hostname', 'unknown')),
                event_id=raw_log.get('event_id', 'json_log'),
                event_type=raw_log.get('level', raw_log.get('severity', 'INFO')),
                message=raw_log.get('message', raw_log.get('msg', '')),
                user=raw_log.get('user'),
                process=raw_log.get('process', raw_log.get('service')),
                cmdline=raw_log.get('command'),
                src_ip=raw_log.get('src_ip'),
                dst_ip=raw_log.get('dst_ip'),
                session_id=raw_log.get('session_id'),
                status=None,
                label=None
            )
        except (KeyError, ValueError) as e:
            logger.error(f"Failed to parse JSON log: {e}")
            return None
    
    @staticmethod
    def _map_windows_event_type(event_id: int) -> str:
        """Map Windows Event ID to event type."""
        event_map = {
            4624: 'AUTH_SUCCESS',
            4625: 'AUTH_FAIL',
            4634: 'LOGOFF',
            4648: 'EXPLICIT_CRED',
            4720: 'USER_CREATED',
            4726: 'USER_DELETED',
            4732: 'USER_ADDED_TO_GROUP',
            4756: 'USER_ADDED_TO_GLOBAL_GROUP',
        }
        return event_map.get(event_id, f'WINDOWS_{event_id}')
    
    @staticmethod
    def _map_windows_status(keywords: Optional[str]) -> str:
        """Map Windows event keywords to status."""
        if not keywords:
            return 'unknown'
        keywords = keywords.lower()
        if 'audit success' in keywords or 'success' in keywords:
            return 'success'
        if 'audit failure' in keywords or 'failure' in keywords:
            return 'failure'
        return 'unknown'
    
    @staticmethod
    def _map_syslog_facility(priority: int) -> str:
        """Map syslog priority to facility."""
        facility = priority >> 3
        facility_map = {
            0: 'KERNEL',
            1: 'USER',
            2: 'MAIL',
            3: 'DAEMON',
            4: 'AUTH',
            5: 'SYSLOG',
            10: 'AUTHPRIV',
        }
        return facility_map.get(facility, f'FACILITY_{facility}')


if __name__ == "__main__":
    # Example usage
    parser = LogParser()
    
    # Parse Windows event
    windows_log = {
        'TimeCreated': '2025-11-27T10:30:00',
        'Computer': 'DC01',
        'EventID': 4625,
        'Message': 'An account failed to log on',
        'UserData': {'TargetUserName': 'admin', 'IpAddress': '192.168.1.100'},
        'Keywords': 'Audit Failure',
    }
    event = parser.parse_windows_event(windows_log)
    print(f"Parsed Windows event: {event}")
    
    # Parse syslog
    syslog_msg = '<34>Nov 27 10:30:00 web01 nginx: Connection from 192.168.1.50'
    event = parser.parse_syslog(syslog_msg)
    print(f"Parsed syslog: {event}")
