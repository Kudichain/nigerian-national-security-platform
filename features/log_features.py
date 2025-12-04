"""Log event feature extraction for anomaly detection."""

import pandas as pd
import numpy as np
from typing import Dict, Any, List
from collections import Counter
from datetime import datetime, timedelta
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class LogFeatureExtractor:
    """Extract features from log events for anomaly detection."""
    
    def __init__(self, window_minutes: int = 5) -> None:
        """
        Initialize log feature extractor.
        
        Args:
            window_minutes: Time window for aggregation
        """
        self.window_minutes = window_minutes
    
    def extract_session_features(
        self,
        logs: pd.DataFrame,
        entity: str,
        entity_type: str = 'host'
    ) -> Dict[str, float]:
        """
        Extract features from a session (time window) of logs.
        
        Args:
            logs: DataFrame of log events
            entity: Entity identifier (host, user, session_id)
            entity_type: Type of entity ('host', 'user', 'session')
            
        Returns:
            Dictionary of extracted features
        """
        # Filter logs for this entity
        entity_logs = logs[logs[entity_type] == entity]
        
        if len(entity_logs) == 0:
            return {}
        
        features = {
            # Event volume features
            'total_events': float(len(entity_logs)),
            'unique_event_types': float(entity_logs['event_type'].nunique()),
            'unique_users': float(entity_logs['user'].nunique()) if 'user' in entity_logs.columns else 0.0,
            'unique_processes': float(entity_logs['process'].nunique()) if 'process' in entity_logs.columns else 0.0,
            
            # Event type distribution
            **self._extract_event_type_features(entity_logs),
            
            # Temporal features
            'events_per_minute': float(len(entity_logs) / self.window_minutes),
            'event_time_variance': self._compute_time_variance(entity_logs),
            
            # Authentication features
            'failed_auth_count': float(
                len(entity_logs[entity_logs['event_type'].str.contains('FAIL|ERROR', case=False, na=False)])
            ),
            'success_auth_count': float(
                len(entity_logs[entity_logs['event_type'].str.contains('SUCCESS', case=False, na=False)])
            ),
            
            # Process features
            **self._extract_process_features(entity_logs),
            
            # Network features
            **self._extract_network_features(entity_logs),
            
            # Text features
            **self._extract_text_features(entity_logs),
        }
        
        # Compute derived features
        features['failed_auth_ratio'] = self._safe_divide(
            features['failed_auth_count'],
            features['failed_auth_count'] + features['success_auth_count']
        )
        
        return features
    
    def _extract_event_type_features(self, logs: pd.DataFrame) -> Dict[str, float]:
        """Extract features based on event type distribution."""
        event_counts = logs['event_type'].value_counts()
        
        features = {}
        # Top event types
        common_types = ['AUTH_FAIL', 'AUTH_SUCCESS', 'PROCESS_CREATE', 
                       'FILE_ACCESS', 'NETWORK_CONN', 'ERROR']
        
        for event_type in common_types:
            features[f'count_{event_type.lower()}'] = float(
                event_counts.get(event_type, 0)
            )
        
        # Event type entropy (diversity measure)
        features['event_type_entropy'] = self._compute_entropy(event_counts)
        
        return features
    
    def _extract_process_features(self, logs: pd.DataFrame) -> Dict[str, float]:
        """Extract process-related features."""
        if 'process' not in logs.columns or logs['process'].isna().all():
            return {}
        
        process_logs = logs[logs['process'].notna()]
        
        features = {
            'unique_process_count': float(process_logs['process'].nunique()),
            
            # Suspicious process indicators
            'powershell_count': float(
                len(process_logs[process_logs['process'].str.contains('powershell', case=False, na=False)])
            ),
            'cmd_count': float(
                len(process_logs[process_logs['process'].str.contains('cmd', case=False, na=False)])
            ),
            'script_execution_count': float(
                len(process_logs[process_logs['process'].str.contains(
                    r'\.(ps1|vbs|js|bat|sh)', case=False, na=False, regex=True
                )])
            ),
        }
        
        # Command line features
        if 'cmdline' in logs.columns:
            cmdline_logs = logs[logs['cmdline'].notna()]
            features['avg_cmdline_length'] = float(
                cmdline_logs['cmdline'].str.len().mean() if len(cmdline_logs) > 0 else 0
            )
            features['base64_in_cmdline'] = float(
                len(cmdline_logs[cmdline_logs['cmdline'].str.contains(
                    r'[A-Za-z0-9+/]{20,}={0,2}', na=False, regex=True
                )])
            )
        
        return features
    
    def _extract_network_features(self, logs: pd.DataFrame) -> Dict[str, float]:
        """Extract network-related features from logs."""
        if 'src_ip' not in logs.columns and 'dst_ip' not in logs.columns:
            return {}
        
        features = {}
        
        if 'src_ip' in logs.columns:
            src_ip_logs = logs[logs['src_ip'].notna()]
            features['unique_src_ips'] = float(src_ip_logs['src_ip'].nunique())
            features['events_with_src_ip'] = float(len(src_ip_logs))
        
        if 'dst_ip' in logs.columns:
            dst_ip_logs = logs[logs['dst_ip'].notna()]
            features['unique_dst_ips'] = float(dst_ip_logs['dst_ip'].nunique())
            features['events_with_dst_ip'] = float(len(dst_ip_logs))
        
        return features
    
    def _extract_text_features(self, logs: pd.DataFrame) -> Dict[str, float]:
        """Extract features from log message text."""
        if 'message' not in logs.columns:
            return {}
        
        messages = logs['message'].dropna()
        
        if len(messages) == 0:
            return {}
        
        features = {
            'avg_message_length': float(messages.str.len().mean()),
            'max_message_length': float(messages.str.len().max()),
            
            # Keyword detection
            'error_keyword_count': float(
                messages.str.contains('error|fail|exception', case=False, na=False).sum()
            ),
            'warning_keyword_count': float(
                messages.str.contains('warning|warn', case=False, na=False).sum()
            ),
            'access_denied_count': float(
                messages.str.contains('denied|forbidden|unauthorized', case=False, na=False).sum()
            ),
        }
        
        return features
    
    @staticmethod
    def _compute_time_variance(logs: pd.DataFrame) -> float:
        """Compute variance in event timing."""
        if len(logs) < 2 or 'ts' not in logs.columns:
            return 0.0
        
        # Convert to timestamps and compute inter-event times
        timestamps = pd.to_datetime(logs['ts']).sort_values()
        inter_event_times = timestamps.diff().dt.total_seconds().dropna()
        
        if len(inter_event_times) == 0:
            return 0.0
        
        variance = inter_event_times.var()
        return float(variance) if hasattr(variance, '__float__') else 0.0
    
    @staticmethod
    def _compute_entropy(value_counts: pd.Series) -> float:
        """Compute Shannon entropy of a distribution."""
        if len(value_counts) == 0:
            return 0.0
        
        probabilities = value_counts / value_counts.sum()
        entropy = -np.sum(probabilities * np.log2(probabilities + 1e-10))
        
        return float(entropy)
    
    @staticmethod
    def _safe_divide(numerator: float, denominator: float) -> float:
        """Safe division avoiding division by zero."""
        return numerator / denominator if denominator != 0 else 0.0


if __name__ == "__main__":
    # Example usage
    extractor = LogFeatureExtractor(window_minutes=5)
    
    # Create sample log data
    logs_data = pd.DataFrame([
        {'ts': datetime.now(), 'host': 'web01', 'event_type': 'AUTH_FAIL', 
         'user': 'admin', 'message': 'Failed login attempt'},
        {'ts': datetime.now(), 'host': 'web01', 'event_type': 'AUTH_FAIL', 
         'user': 'admin', 'message': 'Failed login attempt'},
        {'ts': datetime.now(), 'host': 'web01', 'event_type': 'AUTH_SUCCESS', 
         'user': 'admin', 'message': 'Successful login'},
    ])
    
    features = extractor.extract_session_features(logs_data, 'web01', 'host')
    print("Log features:", features)
