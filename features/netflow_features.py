"""Network flow feature extraction for NIDS."""

import pandas as pd
import numpy as np
from typing import Dict, Any, List
from datetime import datetime, timedelta
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class NetFlowFeatureExtractor:
    """Extract features from network flow data for anomaly detection."""
    
    def __init__(self, window_minutes: int = 5) -> None:
        """
        Initialize feature extractor.
        
        Args:
            window_minutes: Time window for aggregation features
        """
        self.window_minutes = window_minutes
        self.baseline_cache: Dict[str, Any] = {}
    
    def extract_flow_features(self, flow: Dict[str, Any]) -> Dict[str, float]:
        """
        Extract features from a single network flow.
        
        Args:
            flow: Network flow record
            
        Returns:
            Dictionary of extracted features
        """
        features = {
            # Basic flow metrics
            'bytes': float(flow.get('bytes', 0)),
            'packets': float(flow.get('packets', 0)),
            'duration_ms': float(flow.get('duration_ms', 0)),
            
            # Derived metrics
            'bytes_per_packet': self._safe_divide(
                flow.get('bytes', 0),
                flow.get('packets', 1)
            ),
            'packets_per_second': self._safe_divide(
                flow.get('packets', 0) * 1000,
                flow.get('duration_ms', 1)
            ),
            'bytes_per_second': self._safe_divide(
                flow.get('bytes', 0) * 1000,
                flow.get('duration_ms', 1)
            ),
            
            # Protocol encoding
            'protocol_tcp': 1.0 if flow.get('protocol') == 'TCP' else 0.0,
            'protocol_udp': 1.0 if flow.get('protocol') == 'UDP' else 0.0,
            'protocol_icmp': 1.0 if flow.get('protocol') == 'ICMP' else 0.0,
            
            # Port analysis
            'dst_port': float(flow.get('dst_port', 0)),
            'is_well_known_port': 1.0 if flow.get('dst_port', 0) < 1024 else 0.0,
            'is_ephemeral_port': 1.0 if flow.get('dst_port', 0) >= 49152 else 0.0,
            
            # Geographic features
            'is_international': 1.0 if (
                flow.get('geo_src') != flow.get('geo_dst') and
                flow.get('geo_src') and flow.get('geo_dst')
            ) else 0.0,
        }
        
        return features
    
    def extract_window_features(
        self,
        flows: pd.DataFrame,
        host_ip: str
    ) -> Dict[str, float]:
        """
        Extract time-window aggregated features for a host.
        
        Args:
            flows: DataFrame of flows within time window
            host_ip: IP address to compute features for
            
        Returns:
            Dictionary of aggregated features
        """
        host_flows = flows[
            (flows['src_ip'] == host_ip) | (flows['dst_ip'] == host_ip)
        ]
        
        if len(host_flows) == 0:
            return {}
        
        features = {
            # Connection counts
            'total_flows': float(len(host_flows)),
            'unique_dst_ips': float(host_flows['dst_ip'].nunique()),
            'unique_dst_ports': float(host_flows['dst_port'].nunique()),
            'unique_protocols': float(host_flows['protocol'].nunique()),
            
            # Traffic volume
            'total_bytes_sent': float(
                host_flows[host_flows['src_ip'] == host_ip]['bytes'].sum()
            ),
            'total_bytes_received': float(
                host_flows[host_flows['dst_ip'] == host_ip]['bytes'].sum()
            ),
            'total_packets': float(host_flows['packets'].sum()),
            
            # Statistical features
            'avg_bytes_per_flow': float(host_flows['bytes'].mean()),
            'std_bytes_per_flow': float(host_flows['bytes'].std()),
            'max_bytes_per_flow': float(host_flows['bytes'].max()),
            
            'avg_duration_ms': float(host_flows['duration_ms'].mean()),
            'std_duration_ms': float(host_flows['duration_ms'].std()),
            
            # Behavioral features
            'dns_query_count': float(
                len(host_flows[host_flows['dst_port'] == 53])
            ),
            'http_request_count': float(
                len(host_flows[host_flows['dst_port'].isin([80, 8080])])
            ),
            'https_request_count': float(
                len(host_flows[host_flows['dst_port'] == 443])
            ),
            'ssh_connection_count': float(
                len(host_flows[host_flows['dst_port'] == 22])
            ),
            
            # Anomaly indicators
            'failed_connection_ratio': self._compute_failed_ratio(host_flows),
            'port_scan_score': self._compute_port_scan_score(host_flows),
        }
        
        return features
    
    def compute_baseline_deviation(
        self,
        current_features: Dict[str, float],
        host_ip: str
    ) -> Dict[str, float]:
        """
        Compute deviation from baseline behavior.
        
        Args:
            current_features: Current feature values
            host_ip: Host IP address
            
        Returns:
            Dictionary of deviation scores
        """
        baseline = self.baseline_cache.get(host_ip, {})
        
        if not baseline:
            return {}
        
        deviations = {}
        for key, current_val in current_features.items():
            baseline_val = baseline.get(key, current_val)
            baseline_std = baseline.get(f"{key}_std", 1.0)
            
            # Z-score deviation
            deviation = abs(current_val - baseline_val) / max(baseline_std, 0.001)
            deviations[f"{key}_deviation"] = deviation
        
        return deviations
    
    @staticmethod
    def _safe_divide(numerator: float, denominator: float) -> float:
        """Safe division avoiding division by zero."""
        return numerator / denominator if denominator != 0 else 0.0
    
    @staticmethod
    def _compute_failed_ratio(flows: pd.DataFrame) -> float:
        """Compute ratio of failed connections (heuristic)."""
        # Heuristic: very short duration indicates failed connection
        if len(flows) == 0:
            return 0.0
        
        failed = len(flows[flows['duration_ms'] < 10])
        return failed / len(flows)
    
    @staticmethod
    def _compute_port_scan_score(flows: pd.DataFrame) -> float:
        """
        Compute port scanning score.
        
        High score indicates scanning behavior (many ports, few packets each).
        """
        if len(flows) == 0:
            return 0.0
        
        unique_ports = flows['dst_port'].nunique()
        avg_packets = flows['packets'].mean()
        
        # High port diversity with low packet count = scanning
        if unique_ports > 10 and avg_packets < 5:
            return min(unique_ports / 100.0, 1.0)
        
        return 0.0


if __name__ == "__main__":
    # Example usage
    extractor = NetFlowFeatureExtractor(window_minutes=5)
    
    # Single flow features
    flow = {
        'bytes': 1024,
        'packets': 10,
        'duration_ms': 500,
        'protocol': 'TCP',
        'dst_port': 443,
        'geo_src': 'US',
        'geo_dst': 'DE',
    }
    
    features = extractor.extract_flow_features(flow)
    print("Flow features:", features)
