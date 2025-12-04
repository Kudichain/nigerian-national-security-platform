"""
Railway Transportation Security and CCTV Monitoring System

World-class AI security for railway infrastructure:
- Real-time CCTV monitoring with AI video analytics
- Train movement tracking and route optimization
- Passenger safety monitoring
- Threat detection and emergency response
- Station security and crowd management
"""

import asyncio
import numpy as np
import pandas as pd
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime, timedelta
import json
import logging
from dataclasses import dataclass
from enum import Enum
from collections import defaultdict
import cv2
import base64

# AI and computer vision
try:
    from sklearn.cluster import DBSCAN
    from sklearn.preprocessing import StandardScaler
    import torch
    import torchvision.transforms as transforms
    CV_AVAILABLE = True
except ImportError:
    CV_AVAILABLE = False

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ThreatLevel(Enum):
    NONE = "none"
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class TrainStatus(Enum):
    ON_TIME = "on_time"
    DELAYED = "delayed"
    CANCELLED = "cancelled"
    EMERGENCY = "emergency"


@dataclass
class CCTVCamera:
    camera_id: str
    station_id: str
    location: Tuple[float, float, float]  # lat, lon, elevation
    camera_type: str  # platform, entrance, concourse, track
    resolution: str  # "1080p", "4K"
    field_of_view: float  # degrees
    night_vision: bool
    pan_tilt_zoom: bool
    ai_analytics_enabled: bool
    status: str = "active"


@dataclass
class SecurityIncident:
    incident_id: str
    camera_id: str
    incident_type: str
    threat_level: ThreatLevel
    location: Tuple[float, float]
    description: str
    confidence_score: float
    timestamp: datetime
    video_evidence: Optional[str] = None
    requires_response: bool = True


@dataclass
class TrainRoute:
    route_id: str
    train_number: str
    origin_station: str
    destination_station: str
    intermediate_stops: List[str]
    scheduled_departure: datetime
    scheduled_arrival: datetime
    current_location: Optional[Tuple[float, float]] = None
    current_status: TrainStatus = TrainStatus.ON_TIME
    passenger_count: int = 0
    delay_minutes: int = 0


class AIVideoAnalytics:
    """Advanced AI video analytics for railway security"""
    
    def __init__(self):
        self.threat_models = {}
        self.crowd_density_threshold = 0.7
        self.suspicious_behavior_patterns = [
            'loitering', 'abandoned_object', 'aggressive_behavior', 
            'unauthorized_access', 'weapon_detection', 'suspicious_package'
        ]
    
    def analyze_video_frame(self, frame: np.ndarray, camera_id: str) -> Dict[str, Any]:
        """Analyze a single video frame for security threats"""
        
        if not CV_AVAILABLE:
            # Mock analysis for demonstration
            return self._mock_video_analysis(camera_id)
        
        analysis_results = {
            'camera_id': camera_id,
            'timestamp': datetime.now(),
            'people_count': 0,
            'crowd_density': 0.0,
            'threats_detected': [],
            'suspicious_objects': [],
            'crowd_behavior': 'normal'
        }
        
        try:
            # People detection and counting
            people_count = self._detect_people(frame)
            analysis_results['people_count'] = people_count
            
            # Crowd density calculation
            frame_area = frame.shape[0] * frame.shape[1]
            crowd_density = min(people_count * 1000 / frame_area, 1.0)
            analysis_results['crowd_density'] = crowd_density
            
            # Threat detection
            threats = self._detect_threats(frame)
            analysis_results['threats_detected'] = threats
            
            # Object detection
            objects = self._detect_suspicious_objects(frame)
            analysis_results['suspicious_objects'] = objects
            
            # Crowd behavior analysis
            behavior = self._analyze_crowd_behavior(frame, people_count)
            analysis_results['crowd_behavior'] = behavior
            
        except Exception as e:
            logger.error(f"Video analysis error: {e}")
        
        return analysis_results
    
    def _mock_video_analysis(self, camera_id: str) -> Dict[str, Any]:
        """Mock video analysis when CV libraries are not available"""
        import random
        
        # Simulate realistic railway station conditions
        base_people_count = random.randint(5, 50)
        
        # Rush hour simulation
        current_hour = datetime.now().hour
        if current_hour in [7, 8, 17, 18, 19]:  # Rush hours
            base_people_count *= 2
        
        threats = []
        objects = []
        
        # Occasional threats (1% chance)
        if random.random() < 0.01:
            threat_type = random.choice(self.suspicious_behavior_patterns)
            threats.append({
                'type': threat_type,
                'confidence': random.uniform(0.6, 0.95),
                'location': (random.randint(100, 500), random.randint(100, 400))
            })
        
        # Occasional suspicious objects (2% chance)
        if random.random() < 0.02:
            objects.append({
                'type': 'unattended_bag',
                'confidence': random.uniform(0.5, 0.8),
                'duration_minutes': random.randint(5, 30)
            })
        
        return {
            'camera_id': camera_id,
            'timestamp': datetime.now(),
            'people_count': base_people_count,
            'crowd_density': min(base_people_count / 50, 1.0),
            'threats_detected': threats,
            'suspicious_objects': objects,
            'crowd_behavior': 'crowded' if base_people_count > 30 else 'normal'
        }
    
    def _detect_people(self, frame: np.ndarray) -> int:
        """Detect and count people in the frame"""
        # Simplified people detection
        # In production, this would use YOLO, R-CNN, or similar models
        return np.random.randint(0, 20)
    
    def _detect_threats(self, frame: np.ndarray) -> List[Dict[str, Any]]:
        """Detect potential security threats"""
        threats = []
        
        # Mock threat detection
        if np.random.random() < 0.05:  # 5% chance of threat
            threat_type = np.random.choice(self.suspicious_behavior_patterns)
            threats.append({
                'type': threat_type,
                'confidence': np.random.uniform(0.6, 0.95),
                'location': (np.random.randint(100, 500), np.random.randint(100, 400))
            })
        
        return threats
    
    def _detect_suspicious_objects(self, frame: np.ndarray) -> List[Dict[str, Any]]:
        """Detect suspicious or unattended objects"""
        objects = []
        
        # Mock object detection
        if np.random.random() < 0.02:  # 2% chance
            objects.append({
                'type': 'unattended_bag',
                'confidence': np.random.uniform(0.5, 0.8),
                'duration_minutes': np.random.randint(5, 30)
            })
        
        return objects
    
    def _analyze_crowd_behavior(self, frame: np.ndarray, people_count: int) -> str:
        """Analyze crowd behavior patterns"""
        if people_count > 30:
            return 'crowded'
        elif people_count < 5:
            return 'sparse'
        else:
            return 'normal'


class TrainTrackingSystem:
    """Real-time train movement tracking and route optimization"""
    
    def __init__(self):
        self.active_routes = {}
        self.stations = {}
        self.track_segments = {}
        self.gps_history = defaultdict(list)
    
    def register_route(self, route: TrainRoute):
        """Register a new train route"""
        self.active_routes[route.route_id] = route
        logger.info(f"Registered route {route.route_id}: {route.origin_station} → {route.destination_station}")
    
    def update_train_location(self, route_id: str, location: Tuple[float, float], speed_kmh: float):
        """Update real-time train location"""
        if route_id not in self.active_routes:
            logger.warning(f"Unknown route: {route_id}")
            return
        
        route = self.active_routes[route_id]
        route.current_location = location
        
        # Store GPS history
        self.gps_history[route_id].append({
            'timestamp': datetime.now(),
            'location': location,
            'speed_kmh': speed_kmh
        })
        
        # Keep last 100 GPS points
        if len(self.gps_history[route_id]) > 100:
            self.gps_history[route_id] = self.gps_history[route_id][-100:]
        
        # Calculate delays
        self._calculate_delays(route_id)
    
    def _calculate_delays(self, route_id: str):
        """Calculate route delays and update status"""
        route = self.active_routes[route_id]
        
        # Simplified delay calculation
        current_time = datetime.now()
        scheduled_time = route.scheduled_arrival
        
        if current_time > scheduled_time:
            delay = (current_time - scheduled_time).total_seconds() / 60
            route.delay_minutes = int(delay)
            
            if delay > 30:
                route.current_status = TrainStatus.DELAYED
            elif delay > 5:
                route.current_status = TrainStatus.DELAYED
        else:
            route.current_status = TrainStatus.ON_TIME
    
    def get_route_status(self, route_id: str) -> Dict[str, Any]:
        """Get comprehensive route status"""
        if route_id not in self.active_routes:
            return {'error': 'Route not found'}
        
        route = self.active_routes[route_id]
        
        # Calculate progress
        progress_percent = 0.5  # Mock calculation
        estimated_arrival = route.scheduled_arrival
        
        if route.delay_minutes > 0:
            estimated_arrival += timedelta(minutes=route.delay_minutes)
        
        return {
            'route_id': route_id,
            'train_number': route.train_number,
            'current_location': route.current_location,
            'progress_percent': progress_percent,
            'status': route.current_status.value,
            'delay_minutes': route.delay_minutes,
            'passenger_count': route.passenger_count,
            'next_station': self._get_next_station(route),
            'estimated_arrival': estimated_arrival.isoformat(),
            'recent_gps_points': self.gps_history[route_id][-10:]  # Last 10 GPS points
        }
    
    def _get_next_station(self, route: TrainRoute) -> str:
        """Determine next station on route"""
        # Simplified next station logic
        if route.intermediate_stops:
            return route.intermediate_stops[0]
        return route.destination_station


class RailwaySecuritySystem:
    """Comprehensive railway security and monitoring system"""
    
    def __init__(self):
        self.video_analytics = AIVideoAnalytics()
        self.train_tracker = TrainTrackingSystem()
        self.cctv_cameras = {}
        self.security_incidents = []
        self.stations = {}
    
    def register_station(self, 
                        station_id: str, 
                        station_name: str, 
                        location: Tuple[float, float],
                        cameras: List[CCTVCamera]):
        """Register a railway station with CCTV cameras"""
        
        self.stations[station_id] = {
            'id': station_id,
            'name': station_name,
            'location': location,
            'cameras': {c.camera_id: c for c in cameras},
            'status': 'operational',
            'passenger_capacity': 10000,  # Default capacity
            'current_occupancy': 0
        }
        
        for camera in cameras:
            self.cctv_cameras[camera.camera_id] = camera
        
        logger.info(f"Registered station {station_name} with {len(cameras)} cameras")
    
    def process_cctv_feed(self, camera_id: str, frame_data: bytes) -> List[SecurityIncident]:
        """Process CCTV video feed and detect security threats"""
        
        if camera_id not in self.cctv_cameras:
            logger.warning(f"Unknown camera: {camera_id}")
            return []
        
        # Convert frame data to numpy array (mock for demonstration)
        # In production, this would decode the actual video frame
        mock_frame = np.random.randint(0, 255, (480, 640, 3), dtype=np.uint8)
        
        # Analyze frame
        analysis = self.video_analytics.analyze_video_frame(mock_frame, camera_id)
        
        # Generate security incidents from analysis
        incidents = []
        
        # Process detected threats
        for threat in analysis['threats_detected']:
            if threat['confidence'] > 0.7:
                incident = SecurityIncident(
                    incident_id=f"SEC_{camera_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                    camera_id=camera_id,
                    incident_type=threat['type'],
                    threat_level=self._assess_threat_level(threat),
                    location=self.cctv_cameras[camera_id].location[:2],
                    description=f"{threat['type']} detected with {threat['confidence']:.1%} confidence",
                    confidence_score=threat['confidence'],
                    timestamp=datetime.now(),
                    video_evidence=base64.b64encode(frame_data).decode('utf-8')[:100] + "..."  # Truncated
                )
                incidents.append(incident)
                self.security_incidents.append(incident)
        
        # Process suspicious objects
        for obj in analysis['suspicious_objects']:
            if obj['confidence'] > 0.6:
                incident = SecurityIncident(
                    incident_id=f"OBJ_{camera_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                    camera_id=camera_id,
                    incident_type=f"suspicious_object_{obj['type']}",
                    threat_level=ThreatLevel.MEDIUM,
                    location=self.cctv_cameras[camera_id].location[:2],
                    description=f"Suspicious object: {obj['type']} ({obj['duration_minutes']} min)",
                    confidence_score=obj['confidence'],
                    timestamp=datetime.now()
                )
                incidents.append(incident)
                self.security_incidents.append(incident)
        
        # Update station occupancy
        camera = self.cctv_cameras[camera_id]
        if camera.station_id in self.stations:
            self.stations[camera.station_id]['current_occupancy'] = analysis['people_count']
        
        return incidents
    
    def _assess_threat_level(self, threat: Dict[str, Any]) -> ThreatLevel:
        """Assess threat level based on threat type and confidence"""
        
        high_risk_threats = ['weapon_detection', 'aggressive_behavior', 'unauthorized_access']
        medium_risk_threats = ['suspicious_package', 'loitering']
        
        if threat['type'] in high_risk_threats:
            return ThreatLevel.HIGH if threat['confidence'] > 0.8 else ThreatLevel.MEDIUM
        elif threat['type'] in medium_risk_threats:
            return ThreatLevel.MEDIUM if threat['confidence'] > 0.7 else ThreatLevel.LOW
        else:
            return ThreatLevel.LOW
    
    def get_station_security_status(self, station_id: str) -> Dict[str, Any]:
        """Get comprehensive security status for a station"""
        
        if station_id not in self.stations:
            return {'error': 'Station not found'}
        
        station = self.stations[station_id]
        
        # Count recent incidents
        recent_incidents = [
            i for i in self.security_incidents 
            if any(c.station_id == station_id for c in self.cctv_cameras.values() if c.camera_id == i.camera_id)
            and i.timestamp >= datetime.now() - timedelta(hours=24)
        ]
        
        # Calculate security level
        security_level = "GREEN"
        if any(i.threat_level in [ThreatLevel.CRITICAL, ThreatLevel.HIGH] for i in recent_incidents):
            security_level = "RED"
        elif any(i.threat_level == ThreatLevel.MEDIUM for i in recent_incidents):
            security_level = "YELLOW"
        
        return {
            'station_id': station_id,
            'station_name': station['name'],
            'security_level': security_level,
            'camera_count': len(station['cameras']),
            'operational_cameras': len([c for c in station['cameras'].values() if c.status == 'active']),
            'current_occupancy': station['current_occupancy'],
            'capacity_utilization': station['current_occupancy'] / station['passenger_capacity'],
            'incidents_24h': len(recent_incidents),
            'recent_incidents': [
                {
                    'incident_id': i.incident_id,
                    'type': i.incident_type,
                    'threat_level': i.threat_level.value,
                    'timestamp': i.timestamp.isoformat()
                } for i in recent_incidents[-5:]  # Last 5 incidents
            ]
        }
    
    def get_national_railway_overview(self) -> Dict[str, Any]:
        """Get national overview of railway security"""
        
        total_stations = len(self.stations)
        total_cameras = len(self.cctv_cameras)
        total_incidents_24h = len([i for i in self.security_incidents if i.timestamp >= datetime.now() - timedelta(hours=24)])
        
        # Count by threat level
        threat_counts = {'critical': 0, 'high': 0, 'medium': 0, 'low': 0}
        for incident in self.security_incidents:
            if incident.timestamp >= datetime.now() - timedelta(hours=24):
                threat_counts[incident.threat_level.value] = threat_counts.get(incident.threat_level.value, 0) + 1
        
        # Calculate system health
        operational_cameras = sum(1 for c in self.cctv_cameras.values() if c.status == 'active')
        camera_health = operational_cameras / total_cameras if total_cameras > 0 else 1.0
        
        return {
            'national_railway_security': {
                'total_stations': total_stations,
                'total_cameras': total_cameras,
                'operational_cameras': operational_cameras,
                'camera_health_percent': camera_health * 100,
                'stations_operational': sum(1 for s in self.stations.values() if s['status'] == 'operational')
            },
            'security_metrics': {
                'incidents_24h': total_incidents_24h,
                'threat_breakdown': threat_counts,
                'average_incidents_per_station': total_incidents_24h / total_stations if total_stations > 0 else 0,
                'system_security_level': self._calculate_national_security_level(threat_counts)
            },
            'train_operations': {
                'active_routes': len(self.train_tracker.active_routes),
                'on_time_performance': self._calculate_on_time_performance(),
                'delayed_trains': sum(1 for r in self.train_tracker.active_routes.values() if r.current_status == TrainStatus.DELAYED)
            },
            'timestamp': datetime.now().isoformat()
        }
    
    def _calculate_national_security_level(self, threat_counts: Dict[str, int]) -> str:
        """Calculate national railway security level"""
        if threat_counts.get('critical', 0) > 0 or threat_counts.get('high', 0) > 5:
            return "RED"
        elif threat_counts.get('high', 0) > 0 or threat_counts.get('medium', 0) > 10:
            return "YELLOW"
        else:
            return "GREEN"
    
    def _calculate_on_time_performance(self) -> float:
        """Calculate on-time performance percentage"""
        if not self.train_tracker.active_routes:
            return 100.0
        
        on_time_routes = sum(1 for r in self.train_tracker.active_routes.values() if r.current_status == TrainStatus.ON_TIME)
        return (on_time_routes / len(self.train_tracker.active_routes)) * 100


# Example usage and testing
if __name__ == "__main__":
    
    async def demo_railway_security():
        """Demonstrate railway security monitoring capabilities"""
        
        print("🚄 RAILWAY TRANSPORTATION SECURITY SYSTEM")
        print("=" * 60)
        
        # Initialize system
        railway_system = RailwaySecuritySystem()
        
        # Register sample station with CCTV cameras
        cameras = [
            CCTVCamera("CAM001", "STN001", (40.7505, -73.9934, 10), "platform", "1080p", 90, True, True, True),
            CCTVCamera("CAM002", "STN001", (40.7507, -73.9936, 12), "entrance", "4K", 120, True, False, True),
            CCTVCamera("CAM003", "STN001", (40.7503, -73.9932, 8), "concourse", "1080p", 160, False, True, True),
            CCTVCamera("CAM004", "STN001", (40.7501, -73.9930, 15), "track", "4K", 180, True, True, True)
        ]
        
        railway_system.register_station("STN001", "Grand Central Terminal", (40.7527, -73.9772), cameras)
        
        # Register sample train route
        route = TrainRoute(
            route_id="RT001",
            train_number="NE001",
            origin_station="STN001",
            destination_station="STN002",
            intermediate_stops=["STN_INT1", "STN_INT2"],
            scheduled_departure=datetime.now() - timedelta(hours=1),
            scheduled_arrival=datetime.now() + timedelta(hours=2),
            passenger_count=245
        )
        
        railway_system.train_tracker.register_route(route)
        
        print("✅ Railway security system initialized")
        print(f"   - Station: Grand Central Terminal")
        print(f"   - CCTV Cameras: {len(cameras)}")
        print(f"   - Train Route: {route.train_number}")
        
        # Simulate CCTV monitoring
        print("\n📹 Processing CCTV feeds...")
        
        for i in range(3):
            # Mock video frame data
            mock_frame_data = b"mock_video_frame_data_" + str(i).encode()
            
            for camera in cameras:
                incidents = railway_system.process_cctv_feed(camera.camera_id, mock_frame_data)
                
                if incidents:
                    print(f"   📹 Camera {camera.camera_id}: {len(incidents)} incidents detected")
                    for incident in incidents:
                        print(f"      🚨 {incident.incident_type} - {incident.threat_level.value} ({incident.confidence_score:.1%})")
            
            await asyncio.sleep(0.1)
        
        # Update train location
        print("\n🚆 Updating train locations...")
        railway_system.train_tracker.update_train_location("RT001", (40.7589, -73.9851), 85.0)
        
        # Get station security status
        print("\n🏢 Station Security Status:")
        station_status = railway_system.get_station_security_status("STN001")
        for key, value in station_status.items():
            if key != 'recent_incidents':
                print(f"   {key}: {value}")
        
        if station_status.get('recent_incidents'):
            print("   Recent incidents:")
            for incident in station_status['recent_incidents']:
                print(f"     - {incident['type']} ({incident['threat_level']})")
        
        # Get train status
        print("\n🚆 Train Route Status:")
        route_status = railway_system.train_tracker.get_route_status("RT001")
        for key, value in route_status.items():
            if key != 'recent_gps_points':
                print(f"   {key}: {value}")
        
        # National overview
        print("\n🇺🇸 National Railway Security Overview:")
        overview = railway_system.get_national_railway_overview()
        print(f"   Security Status: {overview['national_railway_security']}")
        print(f"   Security Metrics: {overview['security_metrics']}")
        print(f"   Train Operations: {overview['train_operations']}")
    
    # Run demo
    asyncio.run(demo_railway_security())