"""
Security Operations Utilities for AI Security Platform

Provides practical security tools and utilities including:
1. Log parsing and normalization
2. Threat intelligence feeds integration
3. Security metrics calculation
4. Report generation
5. Real-time alerting
6. Forensics helpers
"""

import pandas as pd
import numpy as np
import json
import hashlib
import base64
from typing import Dict, List, Tuple, Optional, Any, Union
from datetime import datetime, timedelta
import re
import logging
from collections import defaultdict, Counter
import asyncio
import aiohttp
import requests
from pathlib import Path

# Configuration management
import yaml
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

import os

# Monitoring and alerting
try:
    from prometheus_client import Counter as PrometheusCounter, Histogram, Gauge, generate_latest
    PROMETHEUS_AVAILABLE = True
except ImportError:
    PROMETHEUS_AVAILABLE = False

# Database connections
try:
    import redis
    import elasticsearch
    from sqlalchemy import create_engine, text
    DATABASE_AVAILABLE = True
except ImportError:
    DATABASE_AVAILABLE = False

logger = logging.getLogger(__name__)


class LogParser:
    """Universal log parser for various security log formats"""
    
    def __init__(self):
        self.parsers = {
            'apache': self._parse_apache_log,
            'nginx': self._parse_nginx_log,
            'windows_security': self._parse_windows_security_log,
            'syslog': self._parse_syslog,
            'firewall': self._parse_firewall_log,
            'dns': self._parse_dns_log,
            'json': self._parse_json_log
        }
        
        # Common regex patterns
        self.patterns = {
            'ip_address': re.compile(r'\b(?:[0-9]{1,3}\.){3}[0-9]{1,3}\b'),
            'timestamp': re.compile(r'\d{4}-\d{2}-\d{2}\s+\d{2}:\d{2}:\d{2}'),
            'http_method': re.compile(r'\b(GET|POST|PUT|DELETE|HEAD|OPTIONS|PATCH)\b'),
            'status_code': re.compile(r'\s([1-5][0-9][0-9])\s'),
            'user_agent': re.compile(r'"([^"]*)"$'),
            'domain': re.compile(r'\b[a-zA-Z0-9]([a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?(\.[a-zA-Z0-9]([a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?)*\b')
        }
    
    def parse_logs(self, log_data: Union[str, List[str]], log_type: str) -> pd.DataFrame:
        """Parse logs based on type"""
        if isinstance(log_data, str):
            log_lines = log_data.strip().split('\n')
        else:
            log_lines = log_data
        
        if log_type not in self.parsers:
            raise ValueError(f"Unsupported log type: {log_type}")
        
        parsed_logs = []
        parser = self.parsers[log_type]
        
        for line in log_lines:
            try:
                parsed = parser(line)
                if parsed:
                    parsed_logs.append(parsed)
            except Exception as e:
                logger.warning(f"Failed to parse log line: {line[:100]}... Error: {e}")
        
        return pd.DataFrame(parsed_logs)
    
    def _parse_apache_log(self, line: str) -> Optional[Dict[str, Any]]:
        """Parse Apache Common/Combined log format"""
        # Apache Combined Log Format
        pattern = r'^(\S+) \S+ \S+ \[([\w:/]+\s[+\-]\d{4})\] "(\S+) (\S+) (\S+)" (\d{3}) (\d+|-) "([^"]*)" "([^"]*)"'
        match = re.match(pattern, line)
        
        if match:
            return {
                'timestamp': match.group(2),
                'src_ip': match.group(1),
                'method': match.group(3),
                'url': match.group(4),
                'protocol': match.group(5),
                'status_code': int(match.group(6)),
                'response_size': int(match.group(7)) if match.group(7) != '-' else 0,
                'referrer': match.group(8),
                'user_agent': match.group(9),
                'log_type': 'apache'
            }
        return None
    
    def _parse_nginx_log(self, line: str) -> Optional[Dict[str, Any]]:
        """Parse Nginx log format"""
        # Similar to Apache but with some differences
        pattern = r'^(\S+) - \S+ \[([\w:/]+\s[+\-]\d{4})\] "(\S+) (\S+) (\S+)" (\d{3}) (\d+) "([^"]*)" "([^"]*)"'
        match = re.match(pattern, line)
        
        if match:
            return {
                'timestamp': match.group(2),
                'src_ip': match.group(1),
                'method': match.group(3),
                'url': match.group(4),
                'protocol': match.group(5),
                'status_code': int(match.group(6)),
                'response_size': int(match.group(7)),
                'referrer': match.group(8),
                'user_agent': match.group(9),
                'log_type': 'nginx'
            }
        return None
    
    def _parse_windows_security_log(self, line: str) -> Optional[Dict[str, Any]]:
        """Parse Windows Security Event Log"""
        # Simplified Windows event log parsing
        if 'Event ID' in line or 'EventID' in line:
            event_id_match = re.search(r'Event ID[:\s]+(\d+)', line)
            timestamp_match = re.search(r'(\d{1,2}/\d{1,2}/\d{4}\s+\d{1,2}:\d{2}:\d{2}\s+[AP]M)', line)
            user_match = re.search(r'Account Name[:\s]+(\S+)', line)
            
            return {
                'timestamp': timestamp_match.group(1) if timestamp_match else None,
                'event_id': int(event_id_match.group(1)) if event_id_match else None,
                'user': user_match.group(1) if user_match else None,
                'log_type': 'windows_security',
                'raw_log': line
            }
        return None
    
    def _parse_syslog(self, line: str) -> Optional[Dict[str, Any]]:
        """Parse standard syslog format"""
        # RFC 3164 syslog format
        pattern = r'^<(\d+)>(\w{3}\s+\d{1,2}\s+\d{2}:\d{2}:\d{2})\s+(\S+)\s+(\S+)(\[\d+\])?:\s+(.*)$'
        match = re.match(pattern, line)
        
        if match:
            priority = int(match.group(1))
            facility = priority >> 3
            severity = priority & 0x07
            
            return {
                'timestamp': match.group(2),
                'hostname': match.group(3),
                'program': match.group(4),
                'message': match.group(6),
                'facility': facility,
                'severity': severity,
                'log_type': 'syslog'
            }
        return None
    
    def _parse_firewall_log(self, line: str) -> Optional[Dict[str, Any]]:
        """Parse firewall log format"""
        # Generic firewall log parsing
        parts = line.split()
        if len(parts) >= 8:
            return {
                'timestamp': ' '.join(parts[:2]),
                'action': parts[2] if parts[2] in ['ACCEPT', 'DROP', 'REJECT'] else 'UNKNOWN',
                'protocol': parts[3] if parts[3] in ['TCP', 'UDP', 'ICMP'] else 'UNKNOWN',
                'src_ip': parts[4] if self._is_valid_ip(parts[4]) else None,
                'src_port': int(parts[5]) if parts[5].isdigit() else None,
                'dst_ip': parts[6] if self._is_valid_ip(parts[6]) else None,
                'dst_port': int(parts[7]) if parts[7].isdigit() else None,
                'log_type': 'firewall'
            }
        return None
    
    def _parse_dns_log(self, line: str) -> Optional[Dict[str, Any]]:
        """Parse DNS query log format"""
        # DNS query log parsing
        pattern = r'(\d{4}-\d{2}-\d{2}\s+\d{2}:\d{2}:\d{2})\s+(\S+)\s+(\S+)\s+(\S+)\s+(\S+)'
        match = re.match(pattern, line)
        
        if match:
            return {
                'timestamp': match.group(1),
                'client_ip': match.group(2),
                'query_name': match.group(3),
                'query_type': match.group(4),
                'response_code': match.group(5),
                'log_type': 'dns'
            }
        return None
    
    def _parse_json_log(self, line: str) -> Optional[Dict[str, Any]]:
        """Parse JSON-formatted logs"""
        try:
            log_data = json.loads(line)
            log_data['log_type'] = 'json'
            return log_data
        except json.JSONDecodeError:
            return None
    
    def _is_valid_ip(self, ip: str) -> bool:
        """Validate IP address format"""
        parts = ip.split('.')
        if len(parts) != 4:
            return False
        
        try:
            return all(0 <= int(part) <= 255 for part in parts)
        except ValueError:
            return False


class ThreatIntelligence:
    """Threat intelligence feeds integration and management"""
    
    def __init__(self, config: Optional[Dict[str, str]] = None):
        self.config = config or {}
        self.cache = {}
        self.redis_client = None
        
        if DATABASE_AVAILABLE and 'redis_url' in self.config:
            try:
                self.redis_client = redis.from_url(self.config['redis_url'])
            except Exception as e:
                logger.warning(f"Redis connection failed: {e}")
    
    async def lookup_ip_reputation(self, ip: str) -> Dict[str, Any]:
        """Lookup IP reputation from multiple sources"""
        # Check cache first
        cache_key = f"ip_rep:{ip}"
        if self.redis_client:
            cached = self.redis_client.get(cache_key)
            if cached:
                return json.loads(cached)
        
        reputation = {
            'ip': ip,
            'reputation_score': 0.5,  # Neutral
            'categories': [],
            'last_seen': None,
            'sources': []
        }
        
        # Multiple reputation sources would be checked here
        sources = [
            self._check_virustotal_ip,
            self._check_abuseipdb,
            self._check_otx_alienvault
        ]
        
        for source_check in sources:
            try:
                source_data = await source_check(ip)
                if source_data:
                    # Aggregate reputation data
                    if source_data.get('malicious', False):
                        reputation['reputation_score'] = min(reputation['reputation_score'], 0.1)
                    reputation['categories'].extend(source_data.get('categories', []))
                    reputation['sources'].append(source_data.get('source', 'unknown'))
            except Exception as e:
                logger.warning(f"Threat intel source check failed: {e}")
        
        # Cache result
        if self.redis_client:
            self.redis_client.setex(cache_key, 3600, json.dumps(reputation))  # Cache for 1 hour
        
        return reputation
    
    async def _check_virustotal_ip(self, ip: str) -> Optional[Dict[str, Any]]:
        """Check IP against VirusTotal API"""
        api_key = self.config.get('virustotal_api_key')
        if not api_key:
            return None
        
        url = f"https://www.virustotal.com/api/v3/ip_addresses/{ip}"
        headers = {"X-Apikey": api_key}
        
        async with aiohttp.ClientSession() as session:
            async with session.get(url, headers=headers) as response:
                if response.status == 200:
                    data = await response.json()
                    stats = data.get('data', {}).get('attributes', {}).get('last_analysis_stats', {})
                    
                    return {
                        'source': 'virustotal',
                        'malicious': stats.get('malicious', 0) > 0,
                        'suspicious': stats.get('suspicious', 0) > 0,
                        'categories': data.get('data', {}).get('attributes', {}).get('categories', [])
                    }
        
        return None
    
    async def _check_abuseipdb(self, ip: str) -> Optional[Dict[str, Any]]:
        """Check IP against AbuseIPDB"""
        api_key = self.config.get('abuseipdb_api_key')
        if not api_key:
            return None
        
        url = "https://api.abuseipdb.com/api/v2/check"
        headers = {"Key": api_key, "Accept": "application/json"}
        params = {"ipAddress": ip, "maxAgeInDays": 90}
        
        async with aiohttp.ClientSession() as session:
            async with session.get(url, headers=headers, params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    result = data.get('data', {})
                    
                    return {
                        'source': 'abuseipdb',
                        'malicious': result.get('abuseConfidencePercentage', 0) > 50,
                        'categories': result.get('usageType', [])
                    }
        
        return None
    
    async def _check_otx_alienvault(self, ip: str) -> Optional[Dict[str, Any]]:
        """Check IP against AlienVault OTX"""
        api_key = self.config.get('otx_api_key')
        if not api_key:
            return None
        
        url = f"https://otx.alienvault.com/api/v1/indicators/IPv4/{ip}/general"
        headers = {"X-OTX-API-KEY": api_key}
        
        async with aiohttp.ClientSession() as session:
            async with session.get(url, headers=headers) as response:
                if response.status == 200:
                    data = await response.json()
                    
                    return {
                        'source': 'otx',
                        'malicious': len(data.get('pulse_info', {}).get('pulses', [])) > 0,
                        'categories': [pulse.get('name', '') for pulse in data.get('pulse_info', {}).get('pulses', [])[:5]]
                    }
        
        return None


class SecurityMetrics:
    """Calculate and track security metrics"""
    
    def __init__(self):
        self.metrics = defaultdict(list)
        
        # Prometheus metrics if available
        if PROMETHEUS_AVAILABLE:
            self.security_events_counter = PrometheusCounter('security_events_total', 'Total security events', ['event_type', 'severity'])
            self.threat_score_gauge = Gauge('current_threat_score', 'Current threat score')
            self.response_time_histogram = Histogram('security_analysis_duration_seconds', 'Time spent on security analysis')
    
    def calculate_security_posture(self, events: pd.DataFrame) -> Dict[str, Any]:
        """Calculate overall security posture metrics"""
        if events.empty:
            return {'score': 100, 'level': 'unknown', 'metrics': {}}
        
        metrics = {
            'total_events': len(events),
            'unique_sources': events['src_ip'].nunique() if 'src_ip' in events.columns else 0,
            'time_range': self._calculate_time_range(events),
            'event_types': events.get('event_type', pd.Series()).value_counts().to_dict(),
            'severity_distribution': events.get('severity', pd.Series()).value_counts().to_dict(),
            'attack_success_rate': self._calculate_attack_success_rate(events),
            'anomaly_rate': self._calculate_anomaly_rate(events),
            'geographic_distribution': self._calculate_geo_distribution(events)
        }
        
        # Calculate security score (0-100)
        score = self._calculate_security_score(metrics)
        
        # Determine security level
        if score >= 90:
            level = 'excellent'
        elif score >= 75:
            level = 'good'
        elif score >= 50:
            level = 'moderate'
        elif score >= 25:
            level = 'poor'
        else:
            level = 'critical'
        
        return {
            'score': score,
            'level': level,
            'metrics': metrics,
            'recommendations': self._generate_posture_recommendations(score, metrics)
        }
    
    def track_incident_response_time(self, incidents: pd.DataFrame) -> Dict[str, Any]:
        """Track incident response time metrics"""
        if incidents.empty or 'created_time' not in incidents.columns:
            return {}
        
        response_times = []
        if 'resolved_time' in incidents.columns:
            resolved_incidents = incidents[incidents['resolved_time'].notna()]
            for _, incident in resolved_incidents.iterrows():
                created = pd.to_datetime(incident['created_time'])
                resolved = pd.to_datetime(incident['resolved_time'])
                response_time = (resolved - created).total_seconds() / 3600  # Hours
                response_times.append(response_time)
        
        if response_times:
            return {
                'mean_response_time': np.mean(response_times),
                'median_response_time': np.median(response_times),
                'p95_response_time': np.percentile(response_times, 95),
                'total_incidents': len(response_times),
                'sla_compliance': sum(1 for rt in response_times if rt <= 4) / len(response_times)  # 4-hour SLA
            }
        
        return {'total_incidents': len(incidents), 'resolved_incidents': 0}
    
    def _calculate_time_range(self, events: pd.DataFrame) -> Dict[str, Union[str, float]]:
        """Calculate time range of events"""
        if 'timestamp' not in events.columns:
            return {}
        
        timestamps = pd.to_datetime(events['timestamp'])
        return {
            'start': timestamps.min().isoformat(),
            'end': timestamps.max().isoformat(),
            'duration_hours': (timestamps.max() - timestamps.min()).total_seconds() / 3600
        }
    
    def _calculate_attack_success_rate(self, events: pd.DataFrame) -> float:
        """Calculate attack success rate"""
        if 'status_code' in events.columns:
            total_requests = len(events)
            successful_attacks = len(events[events['status_code'] == 200])
            return successful_attacks / total_requests if total_requests > 0 else 0.0
        return 0.0
    
    def _calculate_anomaly_rate(self, events: pd.DataFrame) -> float:
        """Calculate anomaly rate"""
        if 'is_anomaly' in events.columns:
            return events['is_anomaly'].mean()
        return 0.0
    
    def _calculate_geo_distribution(self, events: pd.DataFrame) -> Dict[str, int]:
        """Calculate geographic distribution of events"""
        if 'country' in events.columns:
            return events['country'].value_counts().to_dict()
        return {}
    
    def _calculate_security_score(self, metrics: Dict[str, Any]) -> float:
        """Calculate overall security score"""
        score = 100.0
        
        # Deduct points based on various factors
        if metrics.get('anomaly_rate', 0) > 0.1:
            score -= min(metrics['anomaly_rate'] * 50, 30)
        
        if metrics.get('attack_success_rate', 0) > 0.05:
            score -= min(metrics['attack_success_rate'] * 100, 40)
        
        # High event volume might indicate attacks
        if metrics.get('total_events', 0) > 10000:
            score -= 10
        
        return max(score, 0.0)
    
    def _generate_posture_recommendations(self, score: float, metrics: Dict[str, Any]) -> List[str]:
        """Generate security posture recommendations"""
        recommendations = []
        
        if score < 50:
            recommendations.append("Critical security review required")
        
        if metrics.get('anomaly_rate', 0) > 0.2:
            recommendations.append("Investigate high anomaly rate")
        
        if metrics.get('attack_success_rate', 0) > 0.1:
            recommendations.append("Review and strengthen security controls")
        
        if not recommendations:
            recommendations.append("Continue monitoring current security posture")
        
        return recommendations


class SecurityReporter:
    """Generate security reports and alerts"""
    
    def __init__(self, output_dir: str = "reports"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
    
    def generate_threat_summary_report(self, 
                                      analysis_results: Dict[str, Any],
                                      timeframe: str = "24h") -> Dict[str, Any]:
        """Generate comprehensive threat summary report"""
        
        report = {
            'report_id': hashlib.md5(f"{datetime.now().isoformat()}{timeframe}".encode()).hexdigest()[:8],
            'generated_at': datetime.now().isoformat(),
            'timeframe': timeframe,
            'executive_summary': self._generate_executive_summary(analysis_results),
            'threat_landscape': self._analyze_threat_landscape(analysis_results),
            'security_incidents': self._summarize_incidents(analysis_results),
            'recommendations': self._compile_recommendations(analysis_results),
            'metrics': self._extract_key_metrics(analysis_results),
            'appendix': {
                'methodology': 'AI-powered security analysis using multiple detection algorithms',
                'confidence_level': self._calculate_confidence_level(analysis_results)
            }
        }
        
        # Save report
        report_file = self.output_dir / f"threat_summary_{report['report_id']}.json"
        with open(report_file, 'w') as f:
            json.dump(report, f, indent=2, default=str)
        
        return report
    
    def _generate_executive_summary(self, results: Dict[str, Any]) -> Dict[str, str]:
        """Generate executive summary"""
        threat_level = results.get('overall_threat_level', 'unknown')
        
        summaries = {
            'critical': "Critical threats detected requiring immediate attention. Multiple attack vectors identified with high confidence.",
            'high': "High-risk security events detected. Prompt investigation and response recommended.",
            'medium': "Moderate security concerns identified. Review and monitoring advised.",
            'low': "Low-level security events detected. Routine monitoring continues.",
            'unknown': "Security analysis completed with inconclusive threat assessment."
        }
        
        return {
            'threat_level': threat_level,
            'summary': summaries.get(threat_level, summaries['unknown']),
            'key_findings': f"Analysis processed {results.get('total_events_analyzed', 'unknown')} security events"
        }
    
    def _analyze_threat_landscape(self, results: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze current threat landscape"""
        landscape = {
            'dominant_threats': [],
            'attack_vectors': [],
            'geographic_threats': {},
            'trend_analysis': 'stable'
        }
        
        # Extract threat information from results
        if 'attack_patterns' in results:
            attack_data = results['attack_patterns']
            landscape['attack_vectors'] = attack_data.get('attack_types', [])
        
        if 'c2_communication' in results and results['c2_communication'].get('beaconing_detected'):
            landscape['dominant_threats'].append('Command and Control Communication')
        
        if 'data_exfiltration' in results and results['data_exfiltration'].get('exfiltration_detected'):
            landscape['dominant_threats'].append('Data Exfiltration')
        
        return landscape
    
    def _summarize_incidents(self, results: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Summarize security incidents"""
        incidents = []
        
        # Convert analysis results to incident format
        if results.get('overall_threat_level') in ['high', 'critical']:
            incident = {
                'incident_id': f"INC_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                'severity': results['overall_threat_level'],
                'description': 'Automated threat detection triggered',
                'affected_systems': 'Multiple',
                'status': 'open',
                'created_at': datetime.now().isoformat()
            }
            incidents.append(incident)
        
        return incidents
    
    def _compile_recommendations(self, results: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Compile security recommendations"""
        recommendations = []
        
        base_recommendations = results.get('security_recommendations', [])
        
        for i, rec in enumerate(base_recommendations):
            recommendations.append({
                'id': f"REC_{i+1:03d}",
                'priority': 'high' if i < 3 else 'medium',
                'recommendation': rec,
                'category': 'security_control',
                'effort': 'medium'
            })
        
        return recommendations
    
    def _extract_key_metrics(self, results: Dict[str, Any]) -> Dict[str, Any]:
        """Extract key security metrics"""
        metrics = {
            'events_analyzed': results.get('total_events_analyzed', 0),
            'anomalies_detected': 0,
            'threats_identified': 0,
            'false_positive_rate': 0.05  # Estimated
        }
        
        if 'anomaly_detection' in results:
            metrics['anomalies_detected'] = results['anomaly_detection'].get('anomalies_detected', 0)
        
        if 'attack_patterns' in results:
            metrics['threats_identified'] = results['attack_patterns'].get('total_attacks_detected', 0)
        
        return metrics
    
    def _calculate_confidence_level(self, results: Dict[str, Any]) -> str:
        """Calculate confidence level of analysis"""
        # Simplified confidence calculation
        confidence_score = 0.5
        
        if 'threat_correlation' in results:
            threat_score = results['threat_correlation'].get('threat_score', 0)
            confidence_score += threat_score * 0.3
        
        if results.get('total_events_analyzed', 0) > 1000:
            confidence_score += 0.2
        
        if confidence_score >= 0.8:
            return 'high'
        elif confidence_score >= 0.6:
            return 'medium'
        else:
            return 'low'


class SecurityOperationsCenter:
    """Unified Security Operations Center (SOC) interface"""
    
    def __init__(self, config_path: Optional[str] = None):
        self.config = self._load_config(config_path)
        
        # Initialize components
        self.log_parser = LogParser()
        self.threat_intel = ThreatIntelligence(self.config.get('threat_intel', {}))
        self.metrics = SecurityMetrics()
        self.reporter = SecurityReporter(self.config.get('reports_dir', 'reports'))
        
        # Initialize monitoring
        if PROMETHEUS_AVAILABLE:
            self.monitoring_enabled = True
        else:
            self.monitoring_enabled = False
            logger.warning("Prometheus monitoring not available")
    
    def _load_config(self, config_path: str) -> Dict[str, Any]:
        """Load configuration from file"""
        if config_path and Path(config_path).exists():
            with open(config_path, 'r') as f:
                if config_path.endswith('.yaml') or config_path.endswith('.yml'):
                    return yaml.safe_load(f)
                else:
                    return json.load(f)
        
        # Default configuration
        return {
            'threat_intel': {
                'redis_url': os.getenv('REDIS_URL', 'redis://localhost:6379'),
                'virustotal_api_key': os.getenv('VIRUSTOTAL_API_KEY'),
                'abuseipdb_api_key': os.getenv('ABUSEIPDB_API_KEY'),
                'otx_api_key': os.getenv('OTX_API_KEY')
            },
            'reports_dir': 'reports',
            'alert_thresholds': {
                'critical': 0.9,
                'high': 0.7,
                'medium': 0.5
            }
        }
    
    async def process_security_events(self, 
                                    log_data: str, 
                                    log_type: str,
                                    enrich_with_threat_intel: bool = True) -> Dict[str, Any]:
        """Process security events end-to-end"""
        
        # Parse logs
        parsed_logs = self.log_parser.parse_logs(log_data, log_type)
        
        if parsed_logs.empty:
            return {'error': 'No logs could be parsed', 'parsed_count': 0}
        
        # Enrich with threat intelligence
        if enrich_with_threat_intel and 'src_ip' in parsed_logs.columns:
            for idx, row in parsed_logs.iterrows():
                ip_rep = await self.threat_intel.lookup_ip_reputation(row['src_ip'])
                parsed_logs.at[idx, 'reputation_score'] = ip_rep['reputation_score']  # type: ignore
                parsed_logs.at[idx, 'threat_categories'] = ','.join(ip_rep['categories'])  # type: ignore
        
        # Calculate security metrics
        security_posture = self.metrics.calculate_security_posture(parsed_logs)
        
        # Generate report if threat level is significant
        report = None
        if security_posture['score'] < 75:
            report = self.reporter.generate_threat_summary_report({
                'overall_threat_level': security_posture['level'],
                'security_recommendations': security_posture['recommendations'],
                'total_events_analyzed': len(parsed_logs)
            })
        
        return {
            'parsed_events': len(parsed_logs),
            'security_posture': security_posture,
            'threat_intelligence_enrichment': enrich_with_threat_intel,
            'report_generated': report is not None,
            'report_id': report['report_id'] if report else None
        }


if __name__ == "__main__":
    # Example usage
    async def main():
        soc = SecurityOperationsCenter()
        
        # Sample log data
        sample_logs = '''
        192.168.1.100 - - [28/Nov/2025:10:00:01 +0000] "GET /admin HTTP/1.1" 200 1234 "http://example.com" "Mozilla/5.0"
        192.168.1.101 - - [28/Nov/2025:10:00:02 +0000] "POST /login HTTP/1.1" 401 567 "-" "curl/7.68.0"
        10.0.0.5 - - [28/Nov/2025:10:00:03 +0000] "GET /../../../etc/passwd HTTP/1.1" 404 0 "-" "Malicious Scanner"
        '''
        
        # Process security events
        results = await soc.process_security_events(sample_logs, 'apache', enrich_with_threat_intel=False)
        
        print("Security Operations Results:")
        print(json.dumps(results, indent=2, default=str))
    
    # Run example
    import asyncio
    asyncio.run(main())