"""Auth event feature extraction for risk scoring."""

import pandas as pd
from typing import Dict, Any, Optional
from datetime import datetime, timedelta
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class AuthFeatureExtractor:
    """Extract features from authentication events for risk scoring."""
    
    def __init__(self, user_history: Optional[Dict[str, Any]] = None) -> None:
        """
        Initialize auth feature extractor.
        
        Args:
            user_history: Historical user behavior data
        """
        self.user_history = user_history or {}
    
    def extract_auth_features(
        self,
        auth_event: Dict[str, Any],
        recent_events: Optional[pd.DataFrame] = None
    ) -> Dict[str, float]:
        """
        Extract features from an authentication event.
        
        Args:
            auth_event: Current auth event
            recent_events: Recent auth events for velocity features
            
        Returns:
            Dictionary of extracted features
        """
        user_id = auth_event['user_id']
        
        features = {
            # Event type
            'is_login': 1.0 if 'login' in auth_event.get('event_type', '') else 0.0,
            'is_failure': 1.0 if 'fail' in auth_event.get('event_type', '') else 0.0,
            
            # MFA
            'mfa_used': 1.0 if auth_event.get('mfa_used', False) else 0.0,
            
            # Device features
            'device_is_new': self._is_new_device(user_id, auth_event.get('device_id', '')),
            
            # Location features
            'country_is_new': self._is_new_country(user_id, auth_event.get('geo', '')),
            
            # IP features
            'ip_is_new': self._is_new_ip(user_id, auth_event.get('ip')),
        }
        
        # Velocity features from recent events
        if recent_events is not None and len(recent_events) > 0:
            features.update(self._extract_velocity_features(
                user_id, recent_events
            ))
        
        return features
    
    def _is_new_device(self, user_id: str, device_id: str) -> float:
        """Check if device is new for this user."""
        if not device_id:
            return 0.0
        
        user_devices = self.user_history.get(user_id, {}).get('devices', set())
        return 1.0 if device_id not in user_devices else 0.0
    
    def _is_new_country(self, user_id: str, country: str) -> float:
        """Check if country is new for this user."""
        if not country:
            return 0.0
        
        user_countries = self.user_history.get(user_id, {}).get('countries', set())
        return 1.0 if country not in user_countries else 0.0
    
    def _is_new_ip(self, user_id: str, ip: str) -> float:
        """Check if IP is new for this user."""
        if not ip:
            return 0.0
        
        user_ips = self.user_history.get(user_id, {}).get('ips', set())
        return 1.0 if ip not in user_ips else 0.0
    
    def _extract_velocity_features(
        self,
        user_id: str,
        recent_events: pd.DataFrame
    ) -> Dict[str, float]:
        """Extract velocity features from recent events."""
        user_events = recent_events[recent_events['user_id'] == user_id]
        
        # Time windows
        now = datetime.utcnow()
        last_1h = now - timedelta(hours=1)
        last_24h = now - timedelta(hours=24)
        
        events_1h = user_events[pd.to_datetime(user_events['ts']) > last_1h]
        events_24h = user_events[pd.to_datetime(user_events['ts']) > last_24h]
        
        features = {
            # Event counts
            'events_last_1h': float(len(events_1h)),
            'events_last_24h': float(len(events_24h)),
            
            # Failure counts
            'failures_last_1h': float(
                len(events_1h[events_1h['event_type'].str.contains('fail', case=False, na=False)])
            ),
            'failures_last_24h': float(
                len(events_24h[events_24h['event_type'].str.contains('fail', case=False, na=False)])
            ),
            
            # Device/location diversity
            'unique_devices_24h': float(events_24h['device_id'].nunique()) if 'device_id' in events_24h.columns else 0.0,
            'unique_countries_24h': float(events_24h['geo'].nunique()) if 'geo' in events_24h.columns else 0.0,
            'unique_ips_24h': float(events_24h['ip'].nunique()) if 'ip' in events_24h.columns else 0.0,
        }
        
        return features


if __name__ == "__main__":
    extractor = AuthFeatureExtractor()
    
    auth_event = {
        'user_id': 'user123',
        'ip': '198.51.100.42',
        'device_id': 'new_device',
        'geo': 'RU',
        'event_type': 'login_success',
        'mfa_used': False,
    }
    
    features = extractor.extract_auth_features(auth_event)
    print("Auth features:", features)
