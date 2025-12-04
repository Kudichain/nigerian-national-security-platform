"""Test feature extractors."""

import pytest
import pandas as pd
from datetime import datetime
from features.netflow_features import NetFlowFeatureExtractor
from features.log_features import LogFeatureExtractor
from features.phishing_features import PhishingFeatureExtractor
from features.auth_features import AuthFeatureExtractor


def test_netflow_feature_extraction():
    """Test network flow feature extraction."""
    extractor = NetFlowFeatureExtractor()
    
    flow = {
        'bytes': 1024,
        'packets': 10,
        'duration_ms': 500,
        'protocol': 'TCP',
        'dst_port': 443,
    }
    
    features = extractor.extract_flow_features(flow)
    
    assert 'bytes' in features
    assert 'bytes_per_packet' in features
    assert features['bytes_per_packet'] == 102.4
    assert features['protocol_tcp'] == 1.0


def test_log_feature_extraction():
    """Test log feature extraction."""
    extractor = LogFeatureExtractor()
    
    logs = pd.DataFrame([
        {'ts': datetime.now(), 'host': 'web01', 'event_type': 'AUTH_FAIL', 
         'user': 'admin', 'message': 'Failed login'},
        {'ts': datetime.now(), 'host': 'web01', 'event_type': 'AUTH_SUCCESS', 
         'user': 'admin', 'message': 'Successful login'},
    ])
    
    features = extractor.extract_session_features(logs, 'web01', 'host')
    
    assert 'total_events' in features
    assert features['total_events'] == 2.0
    assert 'failed_auth_count' in features


def test_phishing_feature_extraction():
    """Test phishing feature extraction."""
    extractor = PhishingFeatureExtractor()
    
    email = {
        'from_addr': 'attacker@evil.com',
        'to_addrs': ['victim@company.com'],
        'subject': 'URGENT: Verify now!',
        'body_text': 'Click here immediately.',
        'urls': ['http://phishing-site.xyz'],
        'spf_result': 'fail',
    }
    
    features = extractor.extract_email_features(email)
    
    assert 'url_count' in features
    assert features['url_count'] == 1.0
    assert 'spf_fail' in features
    assert features['spf_fail'] == 1.0


def test_auth_feature_extraction():
    """Test auth feature extraction."""
    extractor = AuthFeatureExtractor()
    
    event = {
        'user_id': 'user123',
        'ip': '192.168.1.100',
        'event_type': 'login_success',
        'mfa_used': False,
    }
    
    features = extractor.extract_auth_features(event)
    
    assert 'is_login' in features
    assert features['is_login'] == 1.0
    assert 'mfa_used' in features
    assert features['mfa_used'] == 0.0
