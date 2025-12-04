"""
Advanced Threat Detection and Behavioral Analysis Module

Provides specialized threat detection capabilities including:
1. Anomaly detection for network behavior
2. Attack pattern recognition
3. Command and control (C2) detection
4. Data exfiltration analysis
5. Lateral movement detection
6. Advanced Persistent Threat (APT) indicators
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Tuple, Optional, Any
import re
from datetime import datetime, timedelta
import json
from collections import defaultdict, deque
import statistics
import logging

# Machine Learning
from sklearn.ensemble import IsolationForest
from sklearn.cluster import DBSCAN
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA

# Network Analysis
try:
    import dpkt
    import socket
    DPKT_AVAILABLE = True
except ImportError:
    DPKT_AVAILABLE = False

logger = logging.getLogger(__name__)


class AnomalyDetector:
    """Advanced anomaly detection for security events"""
    
    def __init__(self, contamination: float = 0.1):
        self.contamination = contamination
        self.isolation_forest = IsolationForest(
            contamination=contamination,
            random_state=42,
            n_estimators=100
        )
        self.scaler = StandardScaler()
        self.is_trained = False
        self.baseline_stats = {}
    
    def train_baseline(self, normal_data: pd.DataFrame, features: List[str]) -> None:
        """Train anomaly detection on normal baseline data"""
        logger.info("Training anomaly detection baseline...")
        
        # Prepare features
        X = normal_data[features].fillna(0)
        X_scaled = self.scaler.fit_transform(X)
        
        # Train isolation forest
        self.isolation_forest.fit(X_scaled)
        
        # Calculate baseline statistics
        for feature in features:
            self.baseline_stats[feature] = {
                'mean': normal_data[feature].mean(),
                'std': normal_data[feature].std(),
                'median': normal_data[feature].median(),
                'percentile_95': normal_data[feature].quantile(0.95),
                'percentile_99': normal_data[feature].quantile(0.99)
            }
        
        self.is_trained = True
        logger.info("Baseline training complete")
    
    def detect_anomalies(self, data: pd.DataFrame, features: List[str]) -> pd.DataFrame:
        """Detect anomalies in new data"""
        if not self.is_trained:
            raise ValueError("Detector must be trained before detecting anomalies")
        
        # Prepare features
        X = data[features].fillna(0)
        X_scaled = self.scaler.transform(X)
        
        # Predict anomalies
        anomaly_scores = self.isolation_forest.decision_function(X_scaled)
        anomaly_labels = self.isolation_forest.predict(X_scaled)
        
        # Add results to dataframe
        result_df = data.copy()
        result_df['anomaly_score'] = anomaly_scores
        result_df['is_anomaly'] = anomaly_labels == -1
        result_df['anomaly_severity'] = self._calculate_severity(anomaly_scores)
        
        return result_df
    
    def _calculate_severity(self, scores: np.ndarray) -> List[str]:
        """Calculate anomaly severity based on scores"""
        severity = []
        
        # Calculate thresholds based on score distribution
        score_25 = np.percentile(scores, 25)
        score_10 = np.percentile(scores, 10)
        score_1 = np.percentile(scores, 1)
        
        for score in scores:
            if score >= score_25:
                severity.append('low')
            elif score >= score_10:
                severity.append('medium')
            elif score >= score_1:
                severity.append('high')
            else:
                severity.append('critical')
        
        return severity


class AttackPatternDetector:
    """Detect known attack patterns and signatures"""
    
    def __init__(self):
        self.attack_patterns = {
            'sql_injection': [
                r"(\bUNION\b.*\bSELECT\b)",
                r"(\bOR\b.*=.*)",
                r"(';.*--)",
                r"(\bdrop\s+table\b)",
                r"(\bexec\s*\()"
            ],
            'xss': [
                r"(<script[^>]*>.*</script>)",
                r"(javascript:)",
                r"(onload\s*=)",
                r"(onerror\s*=)",
                r"(<iframe[^>]*>)"
            ],
            'command_injection': [
                r"(;\s*(cat|ls|pwd|whoami|id)\b)",
                r"(`.*`)",
                r"(\$\(.*\))",
                r"(\|.*\|)",
                r"(&&|;|\|)"
            ],
            'directory_traversal': [
                r"(\.\./){3,}",
                r"(\.\.\\){3,}",
                r"(/etc/passwd)",
                r"(\\windows\\system32)",
                r"(boot\.ini)"
            ],
            'brute_force': [
                # Detected by behavioral analysis rather than patterns
            ],
            'port_scan': [
                # Detected by connection patterns
            ]
        }
        
        self.compiled_patterns = {}
        for attack_type, patterns in self.attack_patterns.items():
            self.compiled_patterns[attack_type] = [
                re.compile(pattern, re.IGNORECASE) for pattern in patterns
            ]
    
    def detect_patterns(self, text_data: str, url: str = "", user_agent: str = "") -> Dict[str, Any]:
        """Detect attack patterns in text data"""
        detections = {
            'total_detections': 0,
            'attack_types': [],
            'confidence_scores': {},
            'matched_patterns': {}
        }
        
        # Combine all text for analysis
        combined_text = f"{text_data} {url} {user_agent}"
        
        for attack_type, patterns in self.compiled_patterns.items():
            matches = 0
            matched_patterns = []
            
            for pattern in patterns:
                pattern_matches = pattern.findall(combined_text)
                if pattern_matches:
                    matches += len(pattern_matches)
                    matched_patterns.extend(pattern_matches)
            
            if matches > 0:
                detections['attack_types'].append(attack_type)
                detections['confidence_scores'][attack_type] = min(matches * 0.2, 1.0)
                detections['matched_patterns'][attack_type] = matched_patterns
                detections['total_detections'] += matches
        
        return detections
    
    def analyze_connection_patterns(self, connections: pd.DataFrame) -> Dict[str, Any]:
        """Analyze connection patterns for attack detection"""
        analysis = {
            'port_scan_detected': False,
            'brute_force_detected': False,
            'ddos_detected': False,
            'suspicious_patterns': []
        }
        
        if connections.empty:
            return analysis
        
        # Group by source IP
        src_groups = connections.groupby('src_ip')
        
        for src_ip, group in src_groups:
            # Port scan detection
            unique_ports = group['dst_port'].nunique()
            unique_hosts = group['dst_ip'].nunique()
            
            if unique_ports > 50 and len(group) > 100:
                analysis['port_scan_detected'] = True
                analysis['suspicious_patterns'].append({
                    'type': 'port_scan',
                    'src_ip': src_ip,
                    'unique_ports': unique_ports,
                    'connections': len(group)
                })
            
            # Brute force detection (many connections to same port)
            port_groups = group.groupby(['dst_ip', 'dst_port'])
            for (dst_ip, dst_port), port_group in port_groups:
                if len(port_group) > 20 and dst_port in [22, 21, 23, 3389, 443, 80]:
                    analysis['brute_force_detected'] = True
                    analysis['suspicious_patterns'].append({
                        'type': 'brute_force',
                        'src_ip': src_ip,
                        'dst_ip': dst_ip,
                        'dst_port': dst_port,
                        'attempts': len(port_group)
                    })
        
        # DDoS detection (high volume from multiple sources to same target)
        dst_groups = connections.groupby(['dst_ip', 'dst_port'])
        for (dst_ip, dst_port), group in dst_groups:
            unique_sources = group['src_ip'].nunique()
            total_connections = len(group)
            
            if unique_sources > 10 and total_connections > 1000:
                analysis['ddos_detected'] = True
                analysis['suspicious_patterns'].append({
                    'type': 'ddos',
                    'dst_ip': dst_ip,
                    'dst_port': dst_port,
                    'unique_sources': unique_sources,
                    'total_connections': total_connections
                })
        
        return analysis


class C2CommunicationDetector:
    """Detect Command and Control (C2) communication patterns"""
    
    def __init__(self):
        self.beacon_threshold = 0.8  # Regularity threshold for beaconing
        self.min_beacon_count = 5
    
    def detect_beaconing(self, connections: pd.DataFrame) -> Dict[str, Any]:
        """Detect beaconing behavior indicating C2 communication"""
        detections = {
            'beaconing_detected': False,
            'beacon_pairs': [],
            'suspicious_regularity': []
        }
        
        if connections.empty:
            return detections
        
        # Group by source-destination pairs
        pair_groups = connections.groupby(['src_ip', 'dst_ip', 'dst_port'])
        
        for (src_ip, dst_ip, dst_port), group in pair_groups:
            if len(group) < self.min_beacon_count:
                continue
            
            # Analyze timing patterns
            timestamps = pd.to_datetime(group['timestamp']).sort_values()
            intervals = timestamps.diff().dt.total_seconds().dropna()
            
            if len(intervals) < 3:
                continue
            
            # Calculate regularity metrics
            regularity_score = self._calculate_regularity(intervals)
            
            if regularity_score > self.beacon_threshold:
                detections['beaconing_detected'] = True
                detections['beacon_pairs'].append({
                    'src_ip': src_ip,
                    'dst_ip': dst_ip,
                    'dst_port': dst_port,
                    'regularity_score': regularity_score,
                    'connection_count': len(group),
                    'avg_interval': intervals.mean(),
                    'interval_std': intervals.std()
                })
        
        # Detect suspicious domain patterns
        if 'hostname' in connections.columns:
            suspicious_domains = self._detect_suspicious_domains(connections)
            detections['suspicious_domains'] = suspicious_domains
        
        return detections
    
    def _calculate_regularity(self, intervals: pd.Series) -> float:
        """Calculate regularity score for intervals"""
        if len(intervals) < 3:
            return 0.0
        
        # Calculate coefficient of variation (lower = more regular)
        cv = intervals.std() / intervals.mean() if intervals.mean() > 0 else float('inf')
        
        # Convert to regularity score (0-1, higher = more regular)
        regularity = 1 / (1 + cv) if cv != float('inf') else 0
        
        return regularity
    
    def _detect_suspicious_domains(self, connections: pd.DataFrame) -> List[Dict[str, Any]]:
        """Detect suspicious domain patterns"""
        suspicious = []
        
        if 'hostname' not in connections.columns:
            return suspicious
        
        domain_groups = connections.groupby('hostname')
        
        for domain, group in domain_groups:
            if pd.isna(domain) or domain == '':
                continue
            
            # Check for DGA-like domains
            dga_score = self._calculate_dga_score(domain)
            if dga_score > 0.7:
                suspicious.append({
                    'domain': domain,
                    'type': 'dga',
                    'score': dga_score,
                    'connections': len(group)
                })
            
            # Check for suspicious TLDs
            if any(domain.endswith(tld) for tld in ['.tk', '.ml', '.ga', '.cf']):
                suspicious.append({
                    'domain': domain,
                    'type': 'suspicious_tld',
                    'connections': len(group)
                })
        
        return suspicious
    
    def _calculate_dga_score(self, domain: str) -> float:
        """Calculate Domain Generation Algorithm score"""
        if not domain or '.' not in domain:
            return 0.0
        
        subdomain = domain.split('.')[0]
        score = 0.0
        
        # Length penalty
        if len(subdomain) > 12:
            score += 0.3
        
        # Character entropy
        if len(subdomain) > 0:
            char_counts = {}
            for char in subdomain:
                char_counts[char] = char_counts.get(char, 0) + 1
            
            entropy = -sum((count / len(subdomain)) * np.log2(count / len(subdomain)) 
                          for count in char_counts.values())
            score += min(entropy / 4.0, 0.4)
        
        # Vowel/consonant ratio
        vowels = sum(1 for c in subdomain.lower() if c in 'aeiou')
        consonants = sum(1 for c in subdomain.lower() if c.isalpha() and c not in 'aeiou')
        
        if vowels == 0 or consonants == 0:
            score += 0.3
        
        return min(score, 1.0)


class DataExfiltrationDetector:
    """Detect data exfiltration patterns and indicators"""
    
    def __init__(self):
        self.upload_threshold = 1024 * 1024  # 1 MB
        self.time_window = 3600  # 1 hour
    
    def detect_exfiltration(self, connections: pd.DataFrame, files: pd.DataFrame = None) -> Dict[str, Any]:
        """Detect potential data exfiltration"""
        detections = {
            'exfiltration_detected': False,
            'large_uploads': [],
            'suspicious_transfers': [],
            'file_access_anomalies': []
        }
        
        # Analyze network transfers
        if not connections.empty:
            upload_analysis = self._analyze_uploads(connections)
            detections.update(upload_analysis)
        
        # Analyze file access patterns
        if files is not None and not files.empty:
            file_analysis = self._analyze_file_access(files)
            detections['file_access_anomalies'] = file_analysis
        
        return detections
    
    def _analyze_uploads(self, connections: pd.DataFrame) -> Dict[str, Any]:
        """Analyze upload patterns for exfiltration indicators"""
        analysis = {
            'exfiltration_detected': False,
            'large_uploads': [],
            'suspicious_transfers': []
        }
        
        if 'bytes_out' not in connections.columns:
            return analysis
        
        # Group by source IP and time windows
        connections['timestamp'] = pd.to_datetime(connections['timestamp'])
        connections = connections.sort_values('timestamp')
        
        src_groups = connections.groupby('src_ip')
        
        for src_ip, group in src_groups:
            # Large individual uploads
            large_uploads = group[group['bytes_out'] > self.upload_threshold]
            
            for _, upload in large_uploads.iterrows():
                analysis['large_uploads'].append({
                    'src_ip': src_ip,
                    'dst_ip': upload['dst_ip'],
                    'dst_port': upload['dst_port'],
                    'bytes_out': upload['bytes_out'],
                    'timestamp': upload['timestamp']
                })
                analysis['exfiltration_detected'] = True
            
            # Cumulative uploads in time windows
            for i in range(len(group) - 1):
                window_start = group.iloc[i]['timestamp']
                window_end = window_start + timedelta(seconds=self.time_window)
                
                window_data = group[
                    (group['timestamp'] >= window_start) & 
                    (group['timestamp'] <= window_end)
                ]
                
                total_upload = window_data['bytes_out'].sum()
                
                if total_upload > self.upload_threshold * 5:  # 5 MB in window
                    analysis['suspicious_transfers'].append({
                        'src_ip': src_ip,
                        'window_start': window_start,
                        'window_end': window_end,
                        'total_bytes': total_upload,
                        'connection_count': len(window_data)
                    })
                    analysis['exfiltration_detected'] = True
        
        return analysis
    
    def _analyze_file_access(self, files: pd.DataFrame) -> List[Dict[str, Any]]:
        """Analyze file access patterns for anomalies"""
        anomalies = []
        
        if 'user' not in files.columns or 'file_path' not in files.columns:
            return anomalies
        
        # Group by user
        user_groups = files.groupby('user')
        
        for user, group in user_groups:
            # Unusual file access patterns
            file_types = group['file_path'].str.extract(r'\.([^.]+)$')[0].value_counts()
            
            # Check for access to sensitive file types
            sensitive_extensions = ['key', 'pem', 'p12', 'pfx', 'sql', 'db', 'mdb']
            for ext in sensitive_extensions:
                if ext in file_types.index:
                    anomalies.append({
                        'type': 'sensitive_file_access',
                        'user': user,
                        'file_extension': ext,
                        'count': file_types[ext]
                    })
            
            # Check for bulk file access
            if len(group) > 100:  # More than 100 files accessed
                anomalies.append({
                    'type': 'bulk_file_access',
                    'user': user,
                    'file_count': len(group),
                    'unique_files': group['file_path'].nunique()
                })
        
        return anomalies


class ThreatIntelligenceCorrelator:
    """Correlate events with threat intelligence data"""
    
    def __init__(self):
        # This would typically integrate with threat intel feeds
        self.known_bad_ips = set()
        self.known_bad_domains = set()
        self.attack_signatures = {}
        self.ioc_database = {}
    
    def correlate_indicators(self, events: pd.DataFrame) -> Dict[str, Any]:
        """Correlate events with known indicators of compromise (IOCs)"""
        correlations = {
            'ioc_matches': [],
            'threat_score': 0.0,
            'recommendations': []
        }
        
        # IP-based correlations
        if 'src_ip' in events.columns:
            for ip in events['src_ip'].unique():
                if ip in self.known_bad_ips:
                    correlations['ioc_matches'].append({
                        'type': 'malicious_ip',
                        'value': ip,
                        'confidence': 'high'
                    })
                    correlations['threat_score'] += 0.3
        
        # Domain-based correlations
        if 'hostname' in events.columns:
            for domain in events['hostname'].dropna().unique():
                if domain in self.known_bad_domains:
                    correlations['ioc_matches'].append({
                        'type': 'malicious_domain',
                        'value': domain,
                        'confidence': 'high'
                    })
                    correlations['threat_score'] += 0.4
        
        # Generate recommendations based on correlations
        if correlations['threat_score'] > 0.5:
            correlations['recommendations'].extend([
                'Block identified malicious IPs at firewall',
                'Review logs for additional indicators',
                'Consider isolating affected systems'
            ])
        
        correlations['threat_score'] = min(correlations['threat_score'], 1.0)
        
        return correlations


class ComprehensiveThreatDetector:
    """Unified threat detection system combining all detectors"""
    
    def __init__(self):
        self.anomaly_detector = AnomalyDetector()
        self.pattern_detector = AttackPatternDetector()
        self.c2_detector = C2CommunicationDetector()
        self.exfiltration_detector = DataExfiltrationDetector()
        self.threat_correlator = ThreatIntelligenceCorrelator()
    
    def analyze_security_events(self, 
                               network_data: pd.DataFrame,
                               file_data: pd.DataFrame = None,
                               web_logs: pd.DataFrame = None) -> Dict[str, Any]:
        """Comprehensive security analysis"""
        
        analysis_results = {
            'timestamp': datetime.now().isoformat(),
            'anomaly_detection': {},
            'attack_patterns': {},
            'c2_communication': {},
            'data_exfiltration': {},
            'threat_correlation': {},
            'overall_threat_level': 'low',
            'security_recommendations': []
        }
        
        try:
            # Anomaly detection
            if not network_data.empty and len(network_data) > 100:
                # Use first 80% for training, rest for testing
                train_size = int(len(network_data) * 0.8)
                train_data = network_data.iloc[:train_size]
                test_data = network_data.iloc[train_size:]
                
                numeric_columns = network_data.select_dtypes(include=[np.number]).columns.tolist()
                if numeric_columns:
                    self.anomaly_detector.train_baseline(train_data, numeric_columns)
                    anomaly_results = self.anomaly_detector.detect_anomalies(test_data, numeric_columns)
                    analysis_results['anomaly_detection'] = {
                        'anomalies_detected': anomaly_results['is_anomaly'].sum(),
                        'total_events': len(anomaly_results),
                        'anomaly_rate': anomaly_results['is_anomaly'].mean()
                    }
            
            # Attack pattern detection
            if web_logs is not None and not web_logs.empty:
                pattern_results = []
                for _, log in web_logs.iterrows():
                    patterns = self.pattern_detector.detect_patterns(
                        text_data=log.get('request', ''),
                        url=log.get('url', ''),
                        user_agent=log.get('user_agent', '')
                    )
                    if patterns['total_detections'] > 0:
                        pattern_results.append(patterns)
                
                analysis_results['attack_patterns'] = {
                    'total_attacks_detected': len(pattern_results),
                    'attack_types': list(set().union(*(r['attack_types'] for r in pattern_results))),
                    'patterns': pattern_results[:10]  # Limit output
                }
            
            # Connection pattern analysis
            if not network_data.empty:
                conn_patterns = self.pattern_detector.analyze_connection_patterns(network_data)
                analysis_results['attack_patterns'].update(conn_patterns)
            
            # C2 communication detection
            if not network_data.empty:
                c2_results = self.c2_detector.detect_beaconing(network_data)
                analysis_results['c2_communication'] = c2_results
            
            # Data exfiltration detection
            if not network_data.empty:
                exfil_results = self.exfiltration_detector.detect_exfiltration(network_data, file_data)
                analysis_results['data_exfiltration'] = exfil_results
            
            # Threat intelligence correlation
            threat_corr = self.threat_correlator.correlate_indicators(network_data)
            analysis_results['threat_correlation'] = threat_corr
            
            # Calculate overall threat level
            threat_level = self._calculate_threat_level(analysis_results)
            analysis_results['overall_threat_level'] = threat_level
            
            # Generate security recommendations
            recommendations = self._generate_recommendations(analysis_results)
            analysis_results['security_recommendations'] = recommendations
        
        except Exception as e:
            logger.error(f"Error in threat analysis: {e}")
            analysis_results['error'] = str(e)
        
        return analysis_results
    
    def _calculate_threat_level(self, results: Dict[str, Any]) -> str:
        """Calculate overall threat level"""
        score = 0
        
        # Anomaly detection score
        if 'anomaly_detection' in results:
            anomaly_rate = results['anomaly_detection'].get('anomaly_rate', 0)
            score += anomaly_rate * 0.3
        
        # Attack patterns score
        if 'attack_patterns' in results:
            attack_count = results['attack_patterns'].get('total_attacks_detected', 0)
            score += min(attack_count * 0.1, 0.3)
        
        # C2 communication score
        if 'c2_communication' in results and results['c2_communication'].get('beaconing_detected'):
            score += 0.4
        
        # Data exfiltration score
        if 'data_exfiltration' in results and results['data_exfiltration'].get('exfiltration_detected'):
            score += 0.5
        
        # Threat correlation score
        if 'threat_correlation' in results:
            threat_score = results['threat_correlation'].get('threat_score', 0)
            score += threat_score * 0.4
        
        # Determine threat level
        if score >= 0.8:
            return 'critical'
        elif score >= 0.6:
            return 'high'
        elif score >= 0.3:
            return 'medium'
        else:
            return 'low'
    
    def _generate_recommendations(self, results: Dict[str, Any]) -> List[str]:
        """Generate security recommendations based on analysis results"""
        recommendations = []
        
        if results.get('anomaly_detection', {}).get('anomaly_rate', 0) > 0.1:
            recommendations.append("Investigate anomalous network behavior patterns")
        
        if results.get('attack_patterns', {}).get('total_attacks_detected', 0) > 0:
            recommendations.append("Review and update web application security controls")
        
        if results.get('c2_communication', {}).get('beaconing_detected'):
            recommendations.append("Investigate potential C2 communication for malware infection")
        
        if results.get('data_exfiltration', {}).get('exfiltration_detected'):
            recommendations.append("Review data loss prevention controls and user access privileges")
        
        if results.get('threat_correlation', {}).get('threat_score', 0) > 0.3:
            recommendations.append("Cross-reference with threat intelligence feeds for additional context")
        
        if results.get('overall_threat_level') in ['high', 'critical']:
            recommendations.extend([
                "Consider activating incident response procedures",
                "Review security monitoring and alerting configurations",
                "Validate backup and recovery procedures"
            ])
        
        return recommendations


if __name__ == "__main__":
    # Example usage
    detector = ComprehensiveThreatDetector()
    
    # Create sample network data
    sample_network_data = pd.DataFrame({
        'src_ip': ['192.168.1.100', '10.0.0.5', '172.16.1.50'] * 100,
        'dst_ip': ['8.8.8.8', '1.1.1.1', '208.67.222.222'] * 100,
        'dst_port': [53, 443, 80] * 100,
        'bytes_out': np.random.randint(100, 10000, 300),
        'bytes_in': np.random.randint(100, 5000, 300),
        'timestamp': pd.date_range('2025-11-28 00:00:00', periods=300, freq='1min')
    })
    
    # Analyze security events
    results = detector.analyze_security_events(sample_network_data)
    
    print("Security Analysis Results:")
    print(f"Overall Threat Level: {results['overall_threat_level']}")
    print(f"Recommendations: {results['security_recommendations']}")