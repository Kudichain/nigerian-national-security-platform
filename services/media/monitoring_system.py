"""
Media Monitoring and Information Verification System

World-class AI security for media intelligence and information verification:
- Radio station API for live monitoring and news verification
- Live TV news monitoring and fact-checking
- Social media monitoring and disinformation detection
- Public safety announcement broadcasting
- Emergency alert dissemination
- Cross-platform information correlation
"""

import asyncio
import aiohttp
import numpy as np
import pandas as pd
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime, timedelta
import json
import logging
from dataclasses import dataclass
from enum import Enum
import hashlib
import re
import urllib.parse

# Text processing and NLP
try:
    from textblob import TextBlob
    import nltk
    NLP_AVAILABLE = True
except ImportError:
    NLP_AVAILABLE = False

# Audio processing
try:
    import librosa
    import soundfile as sf
    AUDIO_PROCESSING_AVAILABLE = True
except ImportError:
    AUDIO_PROCESSING_AVAILABLE = False

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class MediaType(Enum):
    RADIO = "radio"
    TELEVISION = "television"
    ONLINE_NEWS = "online_news"
    SOCIAL_MEDIA = "social_media"
    PODCAST = "podcast"
    STREAMING = "streaming"


class ContentCategory(Enum):
    NEWS = "news"
    EMERGENCY_ALERT = "emergency_alert"
    WEATHER = "weather"
    TRAFFIC = "traffic"
    POLITICS = "politics"
    SECURITY = "security"
    HEALTH = "health"
    ENTERTAINMENT = "entertainment"


class VerificationStatus(Enum):
    VERIFIED = "verified"
    UNVERIFIED = "unverified"
    DISPUTED = "disputed"
    FALSE = "false"
    MISLEADING = "misleading"
    PENDING = "pending"


class ThreatLevel(Enum):
    NONE = "none"
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


@dataclass
class MediaSource:
    source_id: str
    name: str
    media_type: MediaType
    frequency_or_url: str
    location: Tuple[float, float]
    language: str
    credibility_score: float  # 0-1 scale
    bias_score: float  # -1 (left) to 1 (right)
    audience_size: int
    last_monitored: Optional[datetime] = None
    status: str = "active"


@dataclass
class MediaContent:
    content_id: str
    source_id: str
    title: str
    content_text: str
    category: ContentCategory
    timestamp: datetime
    duration_seconds: Optional[int] = None
    keywords: Optional[List[str]] = None
    sentiment_score: Optional[float] = None
    verification_status: VerificationStatus = VerificationStatus.UNVERIFIED
    fact_check_results: Optional[Dict[str, Any]] = None


@dataclass
class EmergencyAlert:
    alert_id: str
    alert_type: str
    severity: ThreatLevel
    title: str
    message: str
    affected_areas: List[str]
    issued_by: str
    issue_time: datetime
    expiry_time: datetime
    broadcast_channels: List[str]
    verification_required: bool = True


class RadioMonitoringSystem:
    """Advanced radio monitoring and content analysis system"""
    
    def __init__(self):
        self.radio_stations = {}
        self.monitored_content = []
        self.alert_keywords = [
            'emergency', 'alert', 'warning', 'evacuation', 'lockdown',
            'terrorism', 'attack', 'shooting', 'bomb', 'threat',
            'hurricane', 'tornado', 'flood', 'earthquake', 'fire'
        ]
    
    def register_radio_station(self, station: MediaSource):
        """Register a radio station for monitoring"""
        if station.media_type != MediaType.RADIO:
            raise ValueError("Source must be a radio station")
        
        self.radio_stations[station.source_id] = station
        logger.info(f"Registered radio station: {station.name} ({station.frequency_or_url})")
    
    async def monitor_radio_stream(self, station_id: str, duration_minutes: int = 60) -> List[MediaContent]:
        """Monitor radio station stream for specified duration"""
        
        if station_id not in self.radio_stations:
            logger.error(f"Radio station {station_id} not found")
            return []
        
        station = self.radio_stations[station_id]
        logger.info(f"Starting monitoring of {station.name} for {duration_minutes} minutes")
        
        # Simulate real-time monitoring
        monitored_content = []
        segments_per_hour = 12  # 5-minute segments
        
        for i in range(min(segments_per_hour, duration_minutes // 5)):
            # Simulate audio capture and speech-to-text
            segment_content = await self._process_audio_segment(station_id, i * 5)
            if segment_content:
                monitored_content.append(segment_content)
            
            await asyncio.sleep(0.1)  # Simulate processing time
        
        # Update last monitored time
        station.last_monitored = datetime.now()
        
        return monitored_content
    
    async def _process_audio_segment(self, station_id: str, segment_start_minutes: int) -> Optional[MediaContent]:
        """Process a single audio segment"""
        
        station = self.radio_stations[station_id]
        
        # Mock speech-to-text conversion
        sample_content = self._generate_mock_radio_content(station_id, segment_start_minutes)
        
        if not sample_content:
            return None
        
        # Analyze content
        content = MediaContent(
            content_id=f"RADIO_{station_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{segment_start_minutes}",
            source_id=station_id,
            title=f"Radio Content Segment {segment_start_minutes}min",
            content_text=sample_content,
            category=self._categorize_content(sample_content),
            timestamp=datetime.now() - timedelta(minutes=segment_start_minutes),
            duration_seconds=300,  # 5-minute segments
            keywords=self._extract_keywords(sample_content)
        )
        
        # Perform sentiment analysis
        if NLP_AVAILABLE:
            content.sentiment_score = self._analyze_sentiment(sample_content)
        
        # Check for emergency alerts
        if self._contains_emergency_keywords(sample_content):
            content.verification_status = VerificationStatus.PENDING
            logger.warning(f"Potential emergency content detected in {station.name}")
        
        self.monitored_content.append(content)
        return content
    
    def _generate_mock_radio_content(self, station_id: str, segment: int) -> str:
        """Generate mock radio content for demonstration"""
        
        sample_contents = [
            "Good morning, this is News Radio 101.5. Today's weather will be partly cloudy with temperatures reaching 75 degrees.",
            "Traffic update: Major accident on I-95 southbound near Exit 15. Expect delays of 30 minutes.",
            "Breaking news: City council announces new public safety initiative focusing on neighborhood watch programs.",
            "Weather alert: Thunderstorm warning issued for the metropolitan area. Residents advised to stay indoors.",
            "Emergency broadcast: Police report suspicious activity near downtown train station. Authorities investigating.",
            "Sports update: Local team wins championship game in overtime thriller last night.",
            "Health advisory: County health department reminds residents about flu vaccination availability.",
            "Community announcement: Annual charity drive begins next week to support local food banks."
        ]
        
        # Add some emergency content occasionally
        if segment % 10 == 0:  # Every 10th segment
            emergency_contents = [
                "EMERGENCY ALERT: Severe weather warning in effect. Tornado spotted 15 miles southwest of city center. Take shelter immediately.",
                "BREAKING: Police activity at downtown federal building. Area cordoned off, residents advised to avoid the vicinity.",
                "ALERT: Water main break on Main Street. Boil water advisory in effect for downtown residents."
            ]
            return np.random.choice(emergency_contents)
        
        return np.random.choice(sample_contents)
    
    def _categorize_content(self, content: str) -> ContentCategory:
        """Categorize content based on keywords"""
        
        content_lower = content.lower()
        
        if any(word in content_lower for word in ['emergency', 'alert', 'warning', 'evacuation']):
            return ContentCategory.EMERGENCY_ALERT
        elif any(word in content_lower for word in ['weather', 'temperature', 'storm', 'rain']):
            return ContentCategory.WEATHER
        elif any(word in content_lower for word in ['traffic', 'accident', 'road', 'highway']):
            return ContentCategory.TRAFFIC
        elif any(word in content_lower for word in ['police', 'security', 'crime', 'arrest']):
            return ContentCategory.SECURITY
        elif any(word in content_lower for word in ['health', 'medical', 'hospital', 'vaccine']):
            return ContentCategory.HEALTH
        elif any(word in content_lower for word in ['election', 'political', 'government', 'council']):
            return ContentCategory.POLITICS
        else:
            return ContentCategory.NEWS
    
    def _extract_keywords(self, content: str) -> List[str]:
        """Extract keywords from content"""
        
        # Simple keyword extraction
        words = re.findall(r'\b\w+\b', content.lower())
        
        # Filter out common stop words
        stop_words = {'the', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by', 'is', 'are', 'was', 'were'}
        keywords = [word for word in words if len(word) > 3 and word not in stop_words]
        
        # Return most frequent keywords
        from collections import Counter
        return [word for word, count in Counter(keywords).most_common(10)]
    
    def _analyze_sentiment(self, content: str) -> float:
        """Analyze sentiment of content"""
        try:
            blob = TextBlob(content)
            return blob.sentiment.polarity  # -1 to 1 scale
        except:
            return 0.0  # Neutral if analysis fails
    
    def _contains_emergency_keywords(self, content: str) -> bool:
        """Check if content contains emergency keywords"""
        content_lower = content.lower()
        return any(keyword in content_lower for keyword in self.alert_keywords)


class NewsVerificationEngine:
    """AI-powered news verification and fact-checking system"""
    
    def __init__(self):
        self.verified_sources = set()
        self.fact_check_database = {}
        self.misinformation_patterns = [
            r'according to unnamed sources',
            r'experts say',
            r'many people believe',
            r'it is reported that',
            r'rumors suggest'
        ]
    
    async def verify_news_content(self, content: MediaContent) -> Dict[str, Any]:
        """Comprehensive news verification"""
        
        verification_result = {
            'content_id': content.content_id,
            'verification_timestamp': datetime.now(),
            'overall_credibility': 0.5,
            'verification_checks': {},
            'risk_flags': [],
            'recommendations': []
        }
        
        # 1. Source credibility check
        source_credibility = await self._check_source_credibility(content.source_id)
        verification_result['verification_checks']['source_credibility'] = source_credibility
        
        # 2. Content analysis
        content_analysis = self._analyze_content_quality(content.content_text)
        verification_result['verification_checks']['content_analysis'] = content_analysis
        
        # 3. Cross-reference check
        cross_reference = await self._cross_reference_information(content)
        verification_result['verification_checks']['cross_reference'] = cross_reference
        
        # 4. Pattern matching for misinformation
        misinformation_check = self._check_misinformation_patterns(content.content_text)
        verification_result['verification_checks']['misinformation_check'] = misinformation_check
        
        # Calculate overall credibility
        credibility_score = (
            source_credibility['score'] * 0.4 +
            content_analysis['score'] * 0.3 +
            cross_reference['score'] * 0.2 +
            misinformation_check['score'] * 0.1
        )
        
        verification_result['overall_credibility'] = credibility_score
        
        # Determine verification status
        if credibility_score > 0.8:
            content.verification_status = VerificationStatus.VERIFIED
        elif credibility_score > 0.6:
            content.verification_status = VerificationStatus.UNVERIFIED
        elif credibility_score > 0.4:
            content.verification_status = VerificationStatus.DISPUTED
        else:
            content.verification_status = VerificationStatus.FALSE
        
        # Generate recommendations
        if credibility_score < 0.5:
            verification_result['recommendations'] = [
                'require_additional_verification',
                'flag_for_manual_review',
                'add_disclaimer'
            ]
        elif credibility_score < 0.7:
            verification_result['recommendations'] = [
                'cross_check_with_other_sources',
                'monitor_for_updates'
            ]
        
        content.fact_check_results = verification_result
        return verification_result
    
    async def _check_source_credibility(self, source_id: str) -> Dict[str, Any]:
        """Check credibility of news source"""
        
        # Mock credibility scoring
        credible_sources = ['BBC', 'Reuters', 'AP News', 'NPR', 'PBS']
        questionable_sources = ['UnverifiedNews', 'RumorMill', 'ClickbaitDaily']
        
        # This would normally check against a credibility database
        if any(credible in source_id for credible in credible_sources):
            return {
                'score': 0.9,
                'category': 'highly_credible',
                'factors': ['established_reputation', 'editorial_standards', 'fact_checking_record']
            }
        elif any(questionable in source_id for questionable in questionable_sources):
            return {
                'score': 0.3,
                'category': 'questionable',
                'factors': ['poor_fact_checking_record', 'bias_concerns', 'clickbait_tendencies']
            }
        else:
            return {
                'score': 0.6,
                'category': 'unknown',
                'factors': ['insufficient_data']
            }
    
    def _analyze_content_quality(self, content: str) -> Dict[str, Any]:
        """Analyze content quality indicators"""
        
        quality_score = 0.5
        quality_factors = []
        
        # Check for specific sources and quotes
        if 'according to' in content or 'said' in content:
            quality_score += 0.2
            quality_factors.append('contains_attributions')
        
        # Check for emotional language
        emotional_words = ['shocking', 'unbelievable', 'amazing', 'terrible', 'incredible']
        if any(word in content.lower() for word in emotional_words):
            quality_score -= 0.1
            quality_factors.append('emotional_language_detected')
        
        # Check for specific details (dates, numbers, locations)
        if re.search(r'\d{4}|\d+%|\d+ (people|dollars|miles)', content):
            quality_score += 0.1
            quality_factors.append('specific_details_present')
        
        # Check length (very short articles are often low quality)
        if len(content.split()) < 50:
            quality_score -= 0.1
            quality_factors.append('insufficient_content_length')
        
        return {
            'score': max(0, min(1, quality_score)),
            'factors': quality_factors
        }
    
    async def _cross_reference_information(self, content: MediaContent) -> Dict[str, Any]:
        """Cross-reference information with other sources"""
        
        # Mock cross-referencing
        # In production, this would query multiple news APIs
        
        cross_ref_score = np.random.uniform(0.4, 0.9)
        
        if cross_ref_score > 0.7:
            return {
                'score': cross_ref_score,
                'status': 'corroborated',
                'matching_sources': 3,
                'conflicting_sources': 0
            }
        elif cross_ref_score > 0.5:
            return {
                'score': cross_ref_score,
                'status': 'partially_corroborated',
                'matching_sources': 1,
                'conflicting_sources': 1
            }
        else:
            return {
                'score': cross_ref_score,
                'status': 'not_corroborated',
                'matching_sources': 0,
                'conflicting_sources': 2
            }
    
    def _check_misinformation_patterns(self, content: str) -> Dict[str, Any]:
        """Check for common misinformation patterns"""
        
        pattern_matches = []
        for pattern in self.misinformation_patterns:
            if re.search(pattern, content, re.IGNORECASE):
                pattern_matches.append(pattern)
        
        if pattern_matches:
            return {
                'score': max(0, 1.0 - len(pattern_matches) * 0.2),
                'patterns_detected': pattern_matches,
                'risk_level': 'high' if len(pattern_matches) > 2 else 'medium'
            }
        else:
            return {
                'score': 1.0,
                'patterns_detected': [],
                'risk_level': 'low'
            }


class EmergencyBroadcastSystem:
    """Emergency alert and public safety broadcasting system"""
    
    def __init__(self):
        self.active_alerts = {}
        self.broadcast_channels = {}
        self.alert_history = []
    
    def register_broadcast_channel(self, source: MediaSource):
        """Register a broadcast channel for emergency alerts"""
        self.broadcast_channels[source.source_id] = source
        logger.info(f"Registered broadcast channel: {source.name}")
    
    def create_emergency_alert(self,
                              alert_type: str,
                              severity: ThreatLevel,
                              title: str,
                              message: str,
                              affected_areas: List[str],
                              issuing_authority: str,
                              duration_hours: int = 24) -> str:
        """Create and broadcast emergency alert"""
        
        alert_id = f"EAS_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{len(self.active_alerts):03d}"
        
        alert = EmergencyAlert(
            alert_id=alert_id,
            alert_type=alert_type,
            severity=severity,
            title=title,
            message=message,
            affected_areas=affected_areas,
            issued_by=issuing_authority,
            issue_time=datetime.now(),
            expiry_time=datetime.now() + timedelta(hours=duration_hours),
            broadcast_channels=list(self.broadcast_channels.keys())
        )
        
        self.active_alerts[alert_id] = alert
        self.alert_history.append(alert)
        
        # Broadcast to all registered channels
        self._broadcast_alert(alert)
        
        logger.info(f"Emergency alert created and broadcast: {alert_id}")
        return alert_id
    
    def _broadcast_alert(self, alert: EmergencyAlert):
        """Broadcast alert to all registered channels"""
        
        broadcast_message = f"""
        EMERGENCY ALERT SYSTEM - {alert.severity.value.upper()}
        
        {alert.title}
        
        {alert.message}
        
        Affected Areas: {', '.join(alert.affected_areas)}
        Issued by: {alert.issued_by}
        Time: {alert.issue_time.strftime('%Y-%m-%d %H:%M:%S')}
        
        This alert expires: {alert.expiry_time.strftime('%Y-%m-%d %H:%M:%S')}
        """
        
        for channel_id in alert.broadcast_channels:
            if channel_id in self.broadcast_channels:
                channel = self.broadcast_channels[channel_id]
                logger.info(f"Broadcasting alert {alert.alert_id} to {channel.name}")
                # In production, this would actually send to the broadcast system
    
    def get_active_alerts(self, area: Optional[str] = None) -> List[EmergencyAlert]:
        """Get active emergency alerts"""
        
        now = datetime.now()
        active_alerts = [
            alert for alert in self.active_alerts.values()
            if alert.expiry_time > now
        ]
        
        if area:
            active_alerts = [
                alert for alert in active_alerts
                if area in alert.affected_areas or 'nationwide' in alert.affected_areas
            ]
        
        return active_alerts


class MediaMonitoringSystem:
    """Comprehensive media monitoring and information verification system"""
    
    def __init__(self):
        self.radio_monitor = RadioMonitoringSystem()
        self.news_verifier = NewsVerificationEngine()
        self.emergency_broadcaster = EmergencyBroadcastSystem()
        self.monitored_sources = {}
        self.content_database = []
        self.threat_alerts = []
    
    def register_media_source(self, source: MediaSource):
        """Register a media source for monitoring"""
        self.monitored_sources[source.source_id] = source
        
        if source.media_type == MediaType.RADIO:
            self.radio_monitor.register_radio_station(source)
        
        # Register for emergency broadcasting if appropriate
        if source.media_type in [MediaType.RADIO, MediaType.TELEVISION]:
            self.emergency_broadcaster.register_broadcast_channel(source)
        
        logger.info(f"Registered media source: {source.name} ({source.media_type.value})")
    
    async def monitor_all_sources(self, duration_minutes: int = 60) -> Dict[str, Any]:
        """Monitor all registered media sources"""
        
        monitoring_results = {
            'monitoring_session_id': f"MON_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            'start_time': datetime.now(),
            'duration_minutes': duration_minutes,
            'sources_monitored': len(self.monitored_sources),
            'content_collected': [],
            'alerts_generated': [],
            'verification_results': []
        }
        
        # Monitor radio sources
        radio_sources = [s for s in self.monitored_sources.values() if s.media_type == MediaType.RADIO]
        
        for source in radio_sources:
            try:
                content_list = await self.radio_monitor.monitor_radio_stream(source.source_id, duration_minutes)
                monitoring_results['content_collected'].extend(content_list)
                
                # Verify collected content
                for content in content_list:
                    if content.category in [ContentCategory.NEWS, ContentCategory.SECURITY, ContentCategory.EMERGENCY_ALERT]:
                        verification = await self.news_verifier.verify_news_content(content)
                        monitoring_results['verification_results'].append(verification)
                        
                        # Generate alert if needed
                        if content.category == ContentCategory.EMERGENCY_ALERT or verification['overall_credibility'] < 0.3:
                            alert = self._generate_threat_alert(content, verification)
                            if alert:
                                monitoring_results['alerts_generated'].append(alert)
                
            except Exception as e:
                logger.error(f"Error monitoring {source.name}: {e}")
        
        monitoring_results['end_time'] = datetime.now()
        monitoring_results['content_count'] = len(monitoring_results['content_collected'])
        monitoring_results['alert_count'] = len(monitoring_results['alerts_generated'])
        
        return monitoring_results
    
    def _generate_threat_alert(self, content: MediaContent, verification: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Generate threat alert based on content analysis"""
        
        # Determine threat level
        threat_level = ThreatLevel.NONE
        
        if content.category == ContentCategory.EMERGENCY_ALERT:
            threat_level = ThreatLevel.HIGH
        elif verification['overall_credibility'] < 0.3:
            threat_level = ThreatLevel.MEDIUM
        elif any(keyword in content.content_text.lower() for keyword in ['attack', 'terrorism', 'shooting', 'bomb']):
            threat_level = ThreatLevel.HIGH
        
        if threat_level != ThreatLevel.NONE:
            alert = {
                'alert_id': f"THREAT_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{len(self.threat_alerts):03d}",
                'content_id': content.content_id,
                'source_id': content.source_id,
                'threat_level': threat_level.value,
                'alert_type': 'media_content_analysis',
                'description': f"Potential threat detected in media content: {content.title}",
                'confidence_score': 1.0 - verification['overall_credibility'],
                'timestamp': datetime.now(),
                'requires_investigation': True
            }
            
            self.threat_alerts.append(alert)
            return alert
        
        return None
    
    def get_media_overview(self) -> Dict[str, Any]:
        """Get comprehensive media monitoring overview"""
        
        total_sources = len(self.monitored_sources)
        active_sources = len([s for s in self.monitored_sources.values() if s.status == 'active'])
        
        # Content statistics
        recent_content = [c for c in self.content_database if c.timestamp >= datetime.now() - timedelta(hours=24)]
        
        # Verification statistics
        verified_content = len([c for c in recent_content if c.verification_status == VerificationStatus.VERIFIED])
        disputed_content = len([c for c in recent_content if c.verification_status == VerificationStatus.DISPUTED])
        false_content = len([c for c in recent_content if c.verification_status == VerificationStatus.FALSE])
        
        return {
            'media_monitoring_system': {
                'total_sources': total_sources,
                'active_sources': active_sources,
                'source_types': {media_type.value: len([s for s in self.monitored_sources.values() if s.media_type == media_type]) 
                               for media_type in MediaType},
                'monitoring_uptime_percent': 95.0  # Mock uptime
            },
            'content_analysis': {
                'content_processed_24h': len(recent_content),
                'verified_content': verified_content,
                'disputed_content': disputed_content,
                'false_content': false_content,
                'verification_rate_percent': (verified_content / len(recent_content) * 100) if recent_content else 0
            },
            'threat_detection': {
                'active_alerts': len(self.threat_alerts),
                'alerts_24h': len([a for a in self.threat_alerts if a['timestamp'] >= datetime.now() - timedelta(hours=24)]),
                'high_threat_alerts': len([a for a in self.threat_alerts if a['threat_level'] == 'high']),
                'system_threat_level': self._calculate_system_threat_level()
            },
            'emergency_broadcasting': {
                'active_emergency_alerts': len(self.emergency_broadcaster.get_active_alerts()),
                'broadcast_channels': len(self.emergency_broadcaster.broadcast_channels),
                'alerts_issued_24h': len([a for a in self.emergency_broadcaster.alert_history 
                                        if a.issue_time >= datetime.now() - timedelta(hours=24)])
            },
            'timestamp': datetime.now().isoformat()
        }
    
    def _calculate_system_threat_level(self) -> str:
        """Calculate overall system threat level"""
        recent_alerts = [a for a in self.threat_alerts if a['timestamp'] >= datetime.now() - timedelta(hours=24)]
        
        high_threats = len([a for a in recent_alerts if a['threat_level'] == 'high'])
        medium_threats = len([a for a in recent_alerts if a['threat_level'] == 'medium'])
        
        if high_threats > 3:
            return "CRITICAL"
        elif high_threats > 1 or medium_threats > 5:
            return "HIGH"
        elif high_threats > 0 or medium_threats > 2:
            return "MEDIUM"
        else:
            return "LOW"


# Example usage and testing
if __name__ == "__main__":
    
    async def demo_media_monitoring():
        """Demonstrate media monitoring system"""
        
        print("📻 MEDIA MONITORING AND INFORMATION VERIFICATION SYSTEM")
        print("=" * 60)
        
        # Initialize system
        media_system = MediaMonitoringSystem()
        
        # Register sample media sources
        sources = [
            MediaSource("RADIO_NEWS_101", "News Radio 101.5 FM", MediaType.RADIO, "101.5 FM", 
                       (40.7128, -74.0060), "English", 0.85, 0.1, 50000),
            MediaSource("TV_NEWS_7", "Channel 7 News", MediaType.TELEVISION, "channel7.com/live", 
                       (40.7589, -73.9851), "English", 0.9, -0.2, 200000),
            MediaSource("BBC_WORLD", "BBC World Service", MediaType.RADIO, "bbc.com/worldservice", 
                       (51.5074, -0.1278), "English", 0.95, 0.0, 500000),
            MediaSource("LOCAL_AM", "Local AM 1010", MediaType.RADIO, "1010 AM", 
                       (40.8176, -73.9782), "English", 0.7, 0.3, 25000)
        ]
        
        for source in sources:
            media_system.register_media_source(source)
        
        print("✅ Media monitoring system initialized")
        print(f"   - Radio Stations: 3")
        print(f"   - TV Channels: 1")
        print(f"   - Total Sources: {len(sources)}")
        
        # Monitor sources for sample period
        print("\n📡 Monitoring media sources...")
        monitoring_results = await media_system.monitor_all_sources(duration_minutes=30)
        
        print(f"   📊 Monitoring Session: {monitoring_results['monitoring_session_id']}")
        print(f"   🕒 Duration: {monitoring_results['duration_minutes']} minutes")
        print(f"   📰 Content Collected: {monitoring_results['content_count']} items")
        print(f"   ✓ Verification Checks: {len(monitoring_results['verification_results'])}")
        print(f"   🚨 Alerts Generated: {monitoring_results['alert_count']}")
        
        # Show sample collected content
        if monitoring_results['content_collected']:
            print("\n📰 Sample Collected Content:")
            for content in monitoring_results['content_collected'][:3]:
                print(f"   📻 {content.title}")
                print(f"      Category: {content.category.value}")
                print(f"      Status: {content.verification_status.value}")
                print(f"      Keywords: {', '.join(content.keywords[:5])}")
        
        # Show verification results
        if monitoring_results['verification_results']:
            print("\n🔍 Verification Results:")
            for verification in monitoring_results['verification_results'][:2]:
                print(f"   📋 Content ID: {verification['content_id']}")
                print(f"      Credibility: {verification['overall_credibility']:.2f}")
                print(f"      Source Check: {verification['verification_checks']['source_credibility']['category']}")
                if verification['recommendations']:
                    print(f"      Recommendations: {', '.join(verification['recommendations'])}")
        
        # Generate sample emergency alert
        print("\n🚨 Testing Emergency Broadcast System...")
        alert_id = media_system.emergency_broadcaster.create_emergency_alert(
            alert_type="severe_weather",
            severity=ThreatLevel.HIGH,
            title="Severe Thunderstorm Warning",
            message="Severe thunderstorms with damaging winds and large hail approaching the metropolitan area. Seek shelter immediately.",
            affected_areas=["Downtown", "Midtown", "Airport District"],
            issuing_authority="National Weather Service",
            duration_hours=6
        )
        
        print(f"   🚨 Emergency alert created: {alert_id}")
        print(f"   📡 Broadcast to {len(media_system.emergency_broadcaster.broadcast_channels)} channels")
        
        # Get system overview
        print("\n📊 Media Monitoring System Overview:")
        overview = media_system.get_media_overview()
        print(f"   System Status: {overview['media_monitoring_system']}")
        print(f"   Content Analysis: {overview['content_analysis']['content_processed_24h']} items processed")
        print(f"   Verification Rate: {overview['content_analysis']['verification_rate_percent']:.1f}%")
        print(f"   Threat Level: {overview['threat_detection']['system_threat_level']}")
        print(f"   Emergency Alerts: {overview['emergency_broadcasting']['active_emergency_alerts']} active")
    
    # Run demo
    asyncio.run(demo_media_monitoring())