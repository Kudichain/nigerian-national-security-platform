"""
Advanced Security Feature Engineering for AI Security Platform

Provides comprehensive security-focused feature extraction including:
1. Network packet analysis and protocol detection
2. Cryptographic analysis and entropy calculations
3. Malware static analysis and PE file inspection
4. Domain/IP reputation and geolocation features
5. Protocol anomaly detection and fingerprinting
6. Behavioral analysis for threat detection
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Tuple, Optional, Any
import hashlib
import base64
import json
from datetime import datetime, timedelta
import logging

# Network Analysis
try:
    from scapy.all import *
    from scapy.layers.inet import IP, TCP, UDP, ICMP
    from scapy.layers.http import HTTP
    SCAPY_AVAILABLE = True
except ImportError:
    SCAPY_AVAILABLE = False
    logging.warning("Scapy not available. Network packet analysis features disabled.")

# Cryptography and Security
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.fernet import Fernet
import secrets

# Malware Analysis
try:
    import pefile
    import ssdeep  # type: ignore
    MALWARE_ANALYSIS_AVAILABLE = True
except ImportError:
    MALWARE_ANALYSIS_AVAILABLE = False
    logging.warning("Malware analysis packages not available.")

# Network Intelligence
try:
    import dns.resolver
    import whois
    import geoip2.database
    import maxminddb
    NETWORK_INTEL_AVAILABLE = True
except ImportError:
    NETWORK_INTEL_AVAILABLE = False
    logging.warning("Network intelligence packages not available.")

# Protocol Analysis
import struct
import socket
from urllib.parse import urlparse, parse_qs
import re

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class NetworkProtocolAnalyzer:
    """Advanced network protocol analysis and feature extraction"""
    
    def __init__(self):
        self.protocol_signatures = {
            'HTTP': [b'GET ', b'POST ', b'PUT ', b'HEAD ', b'OPTIONS '],
            'HTTPS': [b'\x16\x03\x01', b'\x16\x03\x02', b'\x16\x03\x03'],  # TLS handshake
            'SSH': [b'SSH-2.0', b'SSH-1.99'],
            'FTP': [b'220 ', b'USER ', b'PASS '],
            'DNS': [b'\x01\x00\x00\x01\x00\x00\x00\x00\x00\x00'],  # DNS query
            'SMB': [b'\xffSMB', b'\xfeSMB'],
            'SMTP': [b'220 ', b'HELO ', b'EHLO '],
            'POP3': [b'+OK ', b'USER ', b'PASS '],
            'IMAP': [b'* OK', b'A001 LOGIN'],
        }
    
    def extract_protocol_features(self, packet_data: bytes) -> Dict[str, Any]:
        """Extract protocol-specific features from packet data"""
        features = {
            'packet_size': len(packet_data),
            'entropy': self._calculate_entropy(packet_data),
            'protocol_detected': 'unknown',
            'has_encryption': False,
            'suspicious_patterns': 0,
            'header_anomalies': 0
        }
        
        # Protocol detection
        for protocol, signatures in self.protocol_signatures.items():
            if any(sig in packet_data[:100] for sig in signatures):
                features['protocol_detected'] = protocol
                break
        
        # Encryption indicators
        if self._detect_encryption(packet_data):
            features['has_encryption'] = True
        
        # Suspicious pattern detection
        features['suspicious_patterns'] = self._detect_suspicious_patterns(packet_data)
        
        # Header anomaly detection
        if len(packet_data) >= 20:  # Minimum for IP header
            features['header_anomalies'] = self._detect_header_anomalies(packet_data)
        
        return features
    
    def _calculate_entropy(self, data: bytes) -> float:
        """Calculate Shannon entropy of data"""
        if not data:
            return 0.0
        
        byte_counts = np.bincount(np.frombuffer(data, dtype=np.uint8), minlength=256)
        probabilities = byte_counts / len(data)
        probabilities = probabilities[probabilities > 0]
        return -np.sum(probabilities * np.log2(probabilities))
    
    def _detect_encryption(self, data: bytes) -> bool:
        """Detect potential encryption in data"""
        entropy = self._calculate_entropy(data)
        return entropy > 7.0  # High entropy suggests encryption
    
    def _detect_suspicious_patterns(self, data: bytes) -> int:
        """Detect suspicious patterns in packet data"""
        suspicious_count = 0
        
        # Check for common exploit patterns
        patterns = [
            b'../../../',  # Directory traversal
            b'<script>',   # XSS
            b'SELECT * FROM',  # SQL injection
            b'\x90\x90\x90\x90',  # NOP sled
            b'cmd.exe',    # Windows command execution
            b'/bin/sh',    # Unix shell
        ]
        
        for pattern in patterns:
            if pattern.lower() in data.lower():
                suspicious_count += 1
        
        return suspicious_count
    
    def _detect_header_anomalies(self, data: bytes) -> int:
        """Detect anomalies in packet headers"""
        anomalies = 0
        
        try:
            # Basic IP header checks
            if len(data) >= 20:
                version = (data[0] >> 4) & 0x0F
                ihl = data[0] & 0x0F
                total_length = struct.unpack('!H', data[2:4])[0]
                
                # Check version
                if version not in [4, 6]:
                    anomalies += 1
                
                # Check header length
                if version == 4 and ihl < 5:
                    anomalies += 1
                
                # Check total length
                if total_length != len(data):
                    anomalies += 1
        
        except (struct.error, IndexError):
            anomalies += 1
        
        return anomalies


class CryptographicAnalyzer:
    """Cryptographic analysis and security feature extraction"""
    
    def __init__(self):
        self.hash_algorithms = {
            'md5': hashlib.md5,
            'sha1': hashlib.sha1,
            'sha256': hashlib.sha256,
            'sha512': hashlib.sha512
        }
    
    def extract_crypto_features(self, data: bytes) -> Dict[str, Any]:
        """Extract cryptographic features from data"""
        features = {
            'file_hashes': self._calculate_hashes(data),
            'entropy': self._calculate_entropy(data),
            'compression_ratio': self._calculate_compression_ratio(data),
            'has_base64': self._detect_base64(data),
            'cert_features': self._extract_certificate_features(data),
            'crypto_constants': self._detect_crypto_constants(data)
        }
        
        return features
    
    def _calculate_hashes(self, data: bytes) -> Dict[str, str]:
        """Calculate multiple hash values"""
        hashes = {}
        for name, hasher in self.hash_algorithms.items():
            hashes[name] = hasher(data).hexdigest()
        return hashes
    
    def _calculate_entropy(self, data: bytes) -> float:
        """Calculate Shannon entropy"""
        if not data:
            return 0.0
        
        byte_counts = np.bincount(np.frombuffer(data, dtype=np.uint8), minlength=256)
        probabilities = byte_counts / len(data)
        probabilities = probabilities[probabilities > 0]
        return -np.sum(probabilities * np.log2(probabilities))
    
    def _calculate_compression_ratio(self, data: bytes) -> float:
        """Calculate compression ratio as indicator of randomness"""
        try:
            import zlib
            compressed = zlib.compress(data, level=9)
            return len(compressed) / len(data) if len(data) > 0 else 1.0
        except:
            return 1.0
    
    def _detect_base64(self, data: bytes) -> bool:
        """Detect base64 encoded content"""
        try:
            text = data.decode('ascii', errors='ignore')
            # Look for base64 patterns
            base64_pattern = re.compile(r'[A-Za-z0-9+/]{4,}={0,2}')
            matches = base64_pattern.findall(text)
            return len(matches) > 0 and any(len(m) > 20 for m in matches)
        except:
            return False
    
    def _extract_certificate_features(self, data: bytes) -> Dict[str, Any]:
        """Extract features from SSL/TLS certificates"""
        features = {
            'has_certificate': False,
            'cert_version': None,
            'signature_algorithm': None,
            'validity_period': None
        }
        
        # Look for certificate markers
        if b'-----BEGIN CERTIFICATE-----' in data or b'\x30\x82' in data:
            features['has_certificate'] = True
            # Additional certificate parsing would go here
        
        return features
    
    def _detect_crypto_constants(self, data: bytes) -> int:
        """Detect common cryptographic constants"""
        constants = [
            b'\x67\x45\x23\x01',  # MD5 constant
            b'\x01\x23\x45\x67',  # SHA-1 constant  
            b'\x6a\x09\xe6\x67',  # SHA-256 constant
            b'RSA',               # RSA markers
            b'AES',               # AES markers
            b'DES',               # DES markers
        ]
        
        count = 0
        for constant in constants:
            if constant in data:
                count += 1
        
        return count


class MalwareAnalysisFeatures:
    """Static malware analysis feature extraction"""
    
    def __init__(self):
        self.suspicious_imports = [
            'CreateRemoteThread', 'VirtualAllocEx', 'WriteProcessMemory',
            'SetWindowsHookEx', 'FindWindow', 'RegSetValueEx',
            'WinExec', 'ShellExecute', 'CreateProcess'
        ]
    
    def extract_pe_features(self, file_path: str) -> Dict[str, Any]:
        """Extract features from PE files"""
        features = {
            'is_pe_file': False,
            'imports_count': 0,
            'sections_count': 0,
            'suspicious_imports': 0,
            'packed': False,
            'entropy_sections': [],
            'timestamp': None,
            'file_size': 0
        }
        
        if not MALWARE_ANALYSIS_AVAILABLE:
            return features
        
        try:
            pe = pefile.PE(file_path)
            features['is_pe_file'] = True
            features['sections_count'] = len(pe.sections)
            features['timestamp'] = pe.FILE_HEADER.TimeDateStamp
            
            # Analyze imports
            if hasattr(pe, 'DIRECTORY_ENTRY_IMPORT'):
                imports_count = 0
                suspicious_count = 0
                
                for entry in pe.DIRECTORY_ENTRY_IMPORT:
                    for function in entry.imports:
                        imports_count += 1
                        if function.name and function.name.decode('utf-8', errors='ignore') in self.suspicious_imports:
                            suspicious_count += 1
                
                features['imports_count'] = imports_count
                features['suspicious_imports'] = suspicious_count
            
            # Calculate section entropy
            for section in pe.sections:
                entropy = self._calculate_section_entropy(section)
                features['entropy_sections'].append({
                    'name': section.Name.decode('utf-8', errors='ignore').rstrip('\x00'),
                    'entropy': entropy,
                    'size': section.SizeOfRawData
                })
                
                # High entropy in executable sections suggests packing
                if entropy > 7.0 and section.Characteristics & 0x20000000:  # IMAGE_SCN_MEM_EXECUTE
                    features['packed'] = True
            
            pe.close()
            
        except Exception as e:
            logger.debug(f"PE analysis failed: {e}")
        
        return features
    
    def _calculate_section_entropy(self, section) -> float:
        """Calculate entropy of PE section"""
        try:
            data = section.get_data()
            if not data:
                return 0.0
            
            byte_counts = np.bincount(np.frombuffer(data, dtype=np.uint8), minlength=256)
            probabilities = byte_counts / len(data)
            probabilities = probabilities[probabilities > 0]
            return -np.sum(probabilities * np.log2(probabilities))
        except:
            return 0.0
    
    def calculate_fuzzy_hash(self, file_path: str) -> str:
        """Calculate ssdeep fuzzy hash for similarity detection"""
        if not MALWARE_ANALYSIS_AVAILABLE:
            return ""
        
        try:
            return ssdeep.hash_from_file(file_path)
        except:
            return ""


class NetworkIntelligenceFeatures:
    """Network intelligence and reputation analysis"""
    
    def __init__(self):
        self.dns_resolver = dns.resolver.Resolver() if NETWORK_INTEL_AVAILABLE else None
        self.geoip_reader = None
    
    def extract_domain_features(self, domain: str) -> Dict[str, Any]:
        """Extract features from domain names"""
        features = {
            'domain_length': len(domain),
            'subdomain_count': domain.count('.'),
            'has_numbers': any(c.isdigit() for c in domain),
            'entropy': self._calculate_string_entropy(domain),
            'suspicious_tld': self._check_suspicious_tld(domain),
            'dga_score': self._calculate_dga_score(domain),
            'dns_records': self._get_dns_records(domain),
            'whois_info': self._get_whois_info(domain)
        }
        
        return features
    
    def extract_ip_features(self, ip: str) -> Dict[str, Any]:
        """Extract features from IP addresses"""
        features = {
            'is_private': self._is_private_ip(ip),
            'is_reserved': self._is_reserved_ip(ip),
            'geo_location': self._get_geolocation(ip),
            'asn_info': self._get_asn_info(ip),
            'reverse_dns': self._get_reverse_dns(ip),
            'reputation_score': 0  # Would integrate with threat intel APIs
        }
        
        return features
    
    def _calculate_string_entropy(self, text: str) -> float:
        """Calculate entropy of string"""
        if not text:
            return 0.0
        
        char_counts = {}
        for char in text:
            char_counts[char] = char_counts.get(char, 0) + 1
        
        probabilities = [count / len(text) for count in char_counts.values()]
        return -sum(p * np.log2(p) for p in probabilities)
    
    def _check_suspicious_tld(self, domain: str) -> bool:
        """Check for suspicious top-level domains"""
        suspicious_tlds = ['.tk', '.ml', '.ga', '.cf', '.bit', '.onion']
        return any(domain.endswith(tld) for tld in suspicious_tlds)
    
    def _calculate_dga_score(self, domain: str) -> float:
        """Calculate Domain Generation Algorithm (DGA) score"""
        score = 0.0
        
        # High entropy suggests DGA
        entropy = self._calculate_string_entropy(domain.split('.')[0])
        score += min(entropy / 4.0, 1.0) * 0.4
        
        # Long subdomains suggest DGA
        subdomain = domain.split('.')[0]
        if len(subdomain) > 12:
            score += 0.3
        
        # Excessive consonants or vowels
        vowels = sum(1 for c in subdomain.lower() if c in 'aeiou')
        consonants = sum(1 for c in subdomain.lower() if c.isalpha() and c not in 'aeiou')
        
        if vowels == 0 or consonants == 0:
            score += 0.3
        
        return min(score, 1.0)
    
    def _get_dns_records(self, domain: str) -> Dict[str, List[str]]:
        """Get DNS records for domain"""
        records = {}
        
        if not NETWORK_INTEL_AVAILABLE or not self.dns_resolver:
            return records
        
        record_types = ['A', 'AAAA', 'CNAME', 'MX', 'TXT', 'NS']
        
        for record_type in record_types:
            try:
                answers = self.dns_resolver.resolve(domain, record_type)
                records[record_type] = [str(answer) for answer in answers]
            except:
                records[record_type] = []
        
        return records
    
    def _get_whois_info(self, domain: str) -> Dict[str, Any]:
        """Get WHOIS information for domain"""
        info = {
            'creation_date': None,
            'expiration_date': None,
            'registrar': None,
            'organization': None
        }
        
        if not NETWORK_INTEL_AVAILABLE:
            return info
        
        try:
            w = whois.whois(domain)
            info['creation_date'] = w.creation_date
            info['expiration_date'] = w.expiration_date
            info['registrar'] = w.registrar
            info['organization'] = getattr(w, 'org', None)
        except:
            pass
        
        return info
    
    def _is_private_ip(self, ip: str) -> bool:
        """Check if IP is in private range"""
        try:
            import ipaddress
            addr = ipaddress.ip_address(ip)
            return addr.is_private
        except:
            return False
    
    def _is_reserved_ip(self, ip: str) -> bool:
        """Check if IP is in reserved range"""
        try:
            import ipaddress
            addr = ipaddress.ip_address(ip)
            return addr.is_reserved or addr.is_multicast or addr.is_loopback
        except:
            return False
    
    def _get_geolocation(self, ip: str) -> Dict[str, Any]:
        """Get geolocation for IP address"""
        geo_info = {
            'country': None,
            'city': None,
            'latitude': None,
            'longitude': None
        }
        
        # Would integrate with MaxMind GeoIP database here
        return geo_info
    
    def _get_asn_info(self, ip: str) -> Dict[str, Any]:
        """Get ASN information for IP"""
        return {
            'asn': None,
            'organization': None
        }
    
    def _get_reverse_dns(self, ip: str) -> str:
        """Get reverse DNS for IP"""
        try:
            return socket.gethostbyaddr(ip)[0]
        except:
            return None


class SecurityFeatureExtractor:
    """Unified security feature extractor combining all analyzers"""
    
    def __init__(self):
        self.protocol_analyzer = NetworkProtocolAnalyzer()
        self.crypto_analyzer = CryptographicAnalyzer()
        self.malware_analyzer = MalwareAnalysisFeatures()
        self.network_intel = NetworkIntelligenceFeatures()
    
    def extract_comprehensive_features(self, 
                                       network_data: Optional[bytes] = None,
                                       file_path: Optional[str] = None,
                                       domains: Optional[List[str]] = None,
                                       ips: Optional[List[str]] = None) -> Dict[str, Any]:
        """Extract comprehensive security features from various data sources"""
        
        features = {
            'timestamp': datetime.now().isoformat(),
            'protocol_features': {},
            'crypto_features': {},
            'malware_features': {},
            'network_intel_features': {}
        }
        
        # Network protocol analysis
        if network_data:
            features['protocol_features'] = self.protocol_analyzer.extract_protocol_features(network_data)
        
        # Cryptographic analysis
        if network_data:
            features['crypto_features'] = self.crypto_analyzer.extract_crypto_features(network_data)
        
        # Malware analysis
        if file_path:
            features['malware_features'] = self.malware_analyzer.extract_pe_features(file_path)
            features['malware_features']['fuzzy_hash'] = self.malware_analyzer.calculate_fuzzy_hash(file_path)
        
        # Network intelligence
        if domains:
            features['network_intel_features']['domains'] = []
            for domain in domains:
                domain_features = self.network_intel.extract_domain_features(domain)
                features['network_intel_features']['domains'].append({
                    'domain': domain,
                    'features': domain_features
                })
        
        if ips:
            features['network_intel_features']['ips'] = []
            for ip in ips:
                ip_features = self.network_intel.extract_ip_features(ip)
                features['network_intel_features']['ips'].append({
                    'ip': ip,
                    'features': ip_features
                })
        
        return features


if __name__ == "__main__":
    # Example usage
    extractor = SecurityFeatureExtractor()
    
    # Example network data (would be real packet data)
    sample_data = b"GET /admin HTTP/1.1\r\nHost: example.com\r\n\r\n"
    
    features = extractor.extract_comprehensive_features(
        network_data=sample_data,
        domains=['suspicious-domain.tk', 'legitimate-site.com'],
        ips=['192.168.1.1', '8.8.8.8']
    )
    
    print(json.dumps(features, indent=2, default=str))