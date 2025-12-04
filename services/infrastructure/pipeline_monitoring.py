"""
Critical Infrastructure Pipeline Leak Detection System

World-class AI security for oil, gas, and water pipeline monitoring:
- Real-time leak detection using pressure sensors and acoustic monitoring
- Predictive maintenance using machine learning
- Environmental impact assessment
- Emergency response coordination
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
from collections import defaultdict, deque

# ML and signal processing
try:
    from scipy import signal
    from scipy.stats import zscore
    from sklearn.ensemble import IsolationForest
    from sklearn.preprocessing import StandardScaler
    ANALYTICS_AVAILABLE = True
except ImportError:
    ANALYTICS_AVAILABLE = False

# Real-time monitoring
import asyncio
import aiohttp
from collections import deque

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class PipelineType(Enum):
    OIL = "oil"
    GAS = "gas"
    WATER = "water"
    CHEMICAL = "chemical"


class AlertSeverity(Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"
    EMERGENCY = "emergency"


@dataclass
class PipelineSensor:
    sensor_id: str
    pipeline_id: str
    location: Tuple[float, float]  # (latitude, longitude)
    sensor_type: str  # pressure, flow, temperature, acoustic, vibration
    normal_range: Tuple[float, float]
    units: str
    last_calibration: datetime
    status: str = "active"


@dataclass
class PipelineAlert:
    alert_id: str
    pipeline_id: str
    sensor_id: str
    alert_type: str
    severity: AlertSeverity
    location: Tuple[float, float]
    description: str
    readings: Dict[str, float]
    timestamp: datetime
    predicted_impact: Dict[str, Any]
    response_required: bool = True


class LeakDetectionEngine:
    """Advanced AI-powered leak detection system"""
    
    def __init__(self):
        self.models = {}
        self.baseline_profiles = {}
        self.sensor_history = defaultdict(lambda: deque(maxlen=1000))
        
    def initialize_baseline(self, pipeline_id: str, sensor_data: pd.DataFrame):
        """Initialize normal operation baseline for a pipeline"""
        logger.info(f"Initializing baseline for pipeline {pipeline_id}")
        
        # Calculate statistical baselines
        baseline = {
            'pressure_mean': sensor_data['pressure'].mean(),
            'pressure_std': sensor_data['pressure'].std(),
            'flow_mean': sensor_data['flow_rate'].mean(),
            'flow_std': sensor_data['flow_rate'].std(),
            'temperature_mean': sensor_data['temperature'].mean(),
            'temperature_std': sensor_data['temperature'].std(),
            'normal_pressure_range': (
                sensor_data['pressure'].quantile(0.05),
                sensor_data['pressure'].quantile(0.95)
            ),
            'normal_flow_range': (
                sensor_data['flow_rate'].quantile(0.05),
                sensor_data['flow_rate'].quantile(0.95)
            )
        }
        
        self.baseline_profiles[pipeline_id] = baseline
        
        # Train anomaly detection model
        if ANALYTICS_AVAILABLE:
            features = sensor_data[['pressure', 'flow_rate', 'temperature']].values
            scaler = StandardScaler()
            features_scaled = scaler.fit_transform(features)
            
            model = IsolationForest(contamination=0.1, random_state=42)
            model.fit(features_scaled)
            
            self.models[pipeline_id] = {
                'anomaly_detector': model,
                'scaler': scaler
            }
    
    def detect_leak(self, pipeline_id: str, sensor_readings: Dict[str, float]) -> Optional[PipelineAlert]:
        """Detect potential leaks using multiple detection methods"""
        
        if pipeline_id not in self.baseline_profiles:
            logger.warning(f"No baseline profile for pipeline {pipeline_id}")
            return None
        
        baseline = self.baseline_profiles[pipeline_id]
        anomalies_detected = []
        severity = AlertSeverity.LOW
        
        # 1. Statistical threshold detection
        pressure = sensor_readings.get('pressure', 0)
        flow_rate = sensor_readings.get('flow_rate', 0)
        temperature = sensor_readings.get('temperature', 0)
        
        # Pressure drop detection
        if pressure < baseline['normal_pressure_range'][0]:
            pressure_drop = (baseline['pressure_mean'] - pressure) / baseline['pressure_std']
            if pressure_drop > 3:  # 3-sigma rule
                anomalies_detected.append(f"Severe pressure drop: {pressure_drop:.2f} sigma")
                severity = AlertSeverity.CRITICAL
            elif pressure_drop > 2:
                anomalies_detected.append(f"Moderate pressure drop: {pressure_drop:.2f} sigma")
                severity = max(severity, AlertSeverity.HIGH)
        
        # Flow rate anomaly detection
        if flow_rate < baseline['normal_flow_range'][0]:
            flow_anomaly = (baseline['flow_mean'] - flow_rate) / baseline['flow_std']
            if flow_anomaly > 2:
                anomalies_detected.append(f"Unexpected flow reduction: {flow_anomaly:.2f} sigma")
                severity = max(severity, AlertSeverity.HIGH)
        
        # 2. Machine learning anomaly detection
        if ANALYTICS_AVAILABLE and pipeline_id in self.models:
            features = np.array([[pressure, flow_rate, temperature]])
            features_scaled = self.models[pipeline_id]['scaler'].transform(features)
            anomaly_score = self.models[pipeline_id]['anomaly_detector'].decision_function(features_scaled)[0]
            
            if anomaly_score < -0.5:  # Anomaly threshold
                anomalies_detected.append(f"ML anomaly detected: score {anomaly_score:.3f}")
                severity = max(severity, AlertSeverity.MEDIUM)
        
        # 3. Pattern-based detection
        self.sensor_history[pipeline_id].append(sensor_readings)
        if len(self.sensor_history[pipeline_id]) >= 10:
            recent_data = list(self.sensor_history[pipeline_id])[-10:]
            pressure_trend = [reading['pressure'] for reading in recent_data]
            
            # Detect sustained pressure drop
            if len(pressure_trend) >= 5:
                slope = np.polyfit(range(5), pressure_trend[-5:], 1)[0]
                if slope < -0.5:  # Negative slope indicates dropping pressure
                    anomalies_detected.append(f"Sustained pressure decline: {slope:.3f}/min")
                    severity = max(severity, AlertSeverity.HIGH)
        
        # Generate alert if anomalies detected
        if anomalies_detected:
            # Predict impact
            predicted_impact = self._predict_impact(pipeline_id, sensor_readings, severity)
            
            alert = PipelineAlert(
                alert_id=f"PIPE_{pipeline_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                pipeline_id=pipeline_id,
                sensor_id=sensor_readings.get('sensor_id', 'unknown'),
                alert_type="leak_detection",
                severity=severity,
                location=sensor_readings.get('location', (0.0, 0.0)),
                description="; ".join(anomalies_detected),
                readings=sensor_readings,
                timestamp=datetime.now(),
                predicted_impact=predicted_impact
            )
            
            return alert
        
        return None
    
    def _predict_impact(self, pipeline_id: str, readings: Dict[str, float], severity: AlertSeverity) -> Dict[str, Any]:
        """Predict environmental and economic impact of detected leak"""
        
        # Simplified impact prediction model
        flow_rate = readings.get('flow_rate', 0)
        pressure = readings.get('pressure', 0)
        
        # Estimate leak rate based on pressure and flow anomaly
        estimated_leak_rate = max(0, flow_rate * 0.1)  # Simplified calculation
        
        impact = {
            'estimated_leak_rate_lph': estimated_leak_rate,  # Liters per hour
            'environmental_risk': 'high' if severity in [AlertSeverity.CRITICAL, AlertSeverity.EMERGENCY] else 'medium',
            'estimated_response_time_minutes': 15 if severity == AlertSeverity.EMERGENCY else 30,
            'potential_affected_area_km2': estimated_leak_rate * 0.001,  # Rough estimate
            'economic_impact_estimate': estimated_leak_rate * 100,  # Cost in USD
            'evacuation_required': severity == AlertSeverity.EMERGENCY
        }
        
        return impact


class RadiationDetectionSystem:
    """AI-powered radiation monitoring for pipeline security"""
    
    def __init__(self):
        self.radiation_baselines = {}
        self.detection_history = defaultdict(list)
    
    def monitor_radiation_levels(self, location: Tuple[float, float], reading: float, sensor_id: str) -> Optional[Dict[str, Any]]:
        """Monitor radiation levels around critical pipeline infrastructure"""
        
        # Normal background radiation: 0.05-0.2 μSv/h
        normal_background = 0.2
        alert_threshold = 1.0  # μSv/h
        emergency_threshold = 10.0  # μSv/h
        
        self.detection_history[sensor_id].append({
            'timestamp': datetime.now(),
            'reading': reading,
            'location': location
        })
        
        alert_level = None
        response_required = False
        
        if reading > emergency_threshold:
            alert_level = "EMERGENCY"
            response_required = True
        elif reading > alert_threshold:
            alert_level = "HIGH"
            response_required = True
        elif reading > normal_background * 3:
            alert_level = "MEDIUM"
        
        if alert_level:
            return {
                'alert_id': f"RAD_{sensor_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                'alert_type': 'radiation_detection',
                'level': alert_level,
                'reading_usv_h': reading,
                'location': location,
                'sensor_id': sensor_id,
                'background_multiple': reading / normal_background,
                'response_required': response_required,
                'timestamp': datetime.now().isoformat(),
                'recommended_actions': self._get_radiation_response_actions(alert_level)
            }
        
        return None
    
    def _get_radiation_response_actions(self, alert_level: str) -> List[str]:
        """Get recommended response actions for radiation alerts"""
        
        actions = {
            'MEDIUM': [
                'Increase monitoring frequency',
                'Notify radiation safety officer',
                'Begin preliminary investigation'
            ],
            'HIGH': [
                'Evacuate non-essential personnel within 500m radius',
                'Alert emergency response teams',
                'Establish radiation monitoring perimeter',
                'Notify regulatory authorities'
            ],
            'EMERGENCY': [
                'Immediate evacuation of 2km radius',
                'Deploy hazmat teams',
                'Establish emergency command center',
                'Notify national emergency management',
                'Begin radiological assessment',
                'Coordinate with nuclear response teams'
            ]
        }
        
        return actions.get(alert_level, [])


class PipelineSecuritySystem:
    """Comprehensive pipeline security and monitoring system"""
    
    def __init__(self):
        self.leak_detector = LeakDetectionEngine()
        self.radiation_monitor = RadiationDetectionSystem()
        self.active_pipelines = {}
        self.sensor_registry = {}
        self.active_alerts = []
        
    def register_pipeline(self, 
                         pipeline_id: str,
                         pipeline_type: PipelineType,
                         route: List[Tuple[float, float]],
                         sensors: List[PipelineSensor]):
        """Register a new pipeline for monitoring"""
        
        self.active_pipelines[pipeline_id] = {
            'id': pipeline_id,
            'type': pipeline_type,
            'route': route,
            'sensors': {s.sensor_id: s for s in sensors},
            'status': 'operational',
            'last_inspection': datetime.now(),
            'total_length_km': self._calculate_pipeline_length(route)
        }
        
        for sensor in sensors:
            self.sensor_registry[sensor.sensor_id] = sensor
        
        logger.info(f"Registered pipeline {pipeline_id} with {len(sensors)} sensors")
    
    def process_sensor_data(self, sensor_id: str, readings: Dict[str, Any]) -> List[PipelineAlert]:
        """Process incoming sensor data and generate alerts"""
        
        if sensor_id not in self.sensor_registry:
            logger.warning(f"Unknown sensor: {sensor_id}")
            return []
        
        sensor = self.sensor_registry[sensor_id]
        pipeline_id = sensor.pipeline_id
        alerts = []
        
        # Add sensor location to readings
        readings['location'] = sensor.location
        readings['sensor_id'] = sensor_id
        
        # Leak detection
        leak_alert = self.leak_detector.detect_leak(pipeline_id, readings)
        if leak_alert:
            alerts.append(leak_alert)
            self.active_alerts.append(leak_alert)
        
        # Radiation monitoring
        if 'radiation_usv_h' in readings:
            radiation_alert = self.radiation_monitor.monitor_radiation_levels(
                sensor.location, 
                readings['radiation_usv_h'], 
                sensor_id
            )
            if radiation_alert:
                alerts.append(radiation_alert)
        
        return alerts
    
    def get_pipeline_status(self, pipeline_id: str) -> Dict[str, Any]:
        """Get comprehensive status for a pipeline"""
        
        if pipeline_id not in self.active_pipelines:
            return {'error': 'Pipeline not found'}
        
        pipeline = self.active_pipelines[pipeline_id]
        
        # Count active alerts
        active_alerts = [a for a in self.active_alerts if a.pipeline_id == pipeline_id]
        
        # Calculate risk level
        risk_level = "LOW"
        if any(a.severity in [AlertSeverity.CRITICAL, AlertSeverity.EMERGENCY] for a in active_alerts):
            risk_level = "CRITICAL"
        elif any(a.severity == AlertSeverity.HIGH for a in active_alerts):
            risk_level = "HIGH"
        elif active_alerts:
            risk_level = "MEDIUM"
        
        return {
            'pipeline_id': pipeline_id,
            'type': pipeline['type'].value,
            'status': pipeline['status'],
            'total_length_km': pipeline['total_length_km'],
            'sensor_count': len(pipeline['sensors']),
            'active_alerts': len(active_alerts),
            'risk_level': risk_level,
            'last_inspection': pipeline['last_inspection'].isoformat(),
            'recent_alerts': [
                {
                    'alert_id': a.alert_id,
                    'severity': a.severity.value,
                    'description': a.description,
                    'timestamp': a.timestamp.isoformat()
                } for a in active_alerts[-5:]  # Last 5 alerts
            ]
        }
    
    def get_national_pipeline_overview(self) -> Dict[str, Any]:
        """Get national overview of all pipeline infrastructure"""
        
        total_pipelines = len(self.active_pipelines)
        total_length = sum(p['total_length_km'] for p in self.active_pipelines.values())
        total_sensors = sum(len(p['sensors']) for p in self.active_pipelines.values())
        
        # Count by type
        type_counts = {}
        for pipeline in self.active_pipelines.values():
            pipeline_type = pipeline['type'].value
            type_counts[pipeline_type] = type_counts.get(pipeline_type, 0) + 1
        
        # Alert statistics
        total_alerts = len(self.active_alerts)
        critical_alerts = len([a for a in self.active_alerts if a.severity in [AlertSeverity.CRITICAL, AlertSeverity.EMERGENCY]])
        
        return {
            'national_infrastructure_status': {
                'total_pipelines': total_pipelines,
                'total_length_km': total_length,
                'total_sensors': total_sensors,
                'pipeline_types': type_counts,
                'operational_pipelines': sum(1 for p in self.active_pipelines.values() if p['status'] == 'operational'),
                'average_sensors_per_km': total_sensors / total_length if total_length > 0 else 0
            },
            'security_status': {
                'total_active_alerts': total_alerts,
                'critical_alerts': critical_alerts,
                'alert_rate_24h': len([a for a in self.active_alerts if a.timestamp >= datetime.now() - timedelta(days=1)]),
                'highest_risk_pipeline': self._get_highest_risk_pipeline(),
                'system_health_score': self._calculate_system_health_score()
            },
            'timestamp': datetime.now().isoformat()
        }
    
    def _calculate_pipeline_length(self, route: List[Tuple[float, float]]) -> float:
        """Calculate pipeline length from GPS coordinates"""
        if len(route) < 2:
            return 0
        
        total_length = 0
        for i in range(len(route) - 1):
            # Simplified distance calculation (Haversine formula would be more accurate)
            lat1, lon1 = route[i]
            lat2, lon2 = route[i + 1]
            
            # Convert to radians
            lat1, lon1, lat2, lon2 = map(np.radians, [lat1, lon1, lat2, lon2])
            
            # Haversine formula
            dlat = lat2 - lat1
            dlon = lon2 - lon1
            a = np.sin(dlat/2)**2 + np.cos(lat1) * np.cos(lat2) * np.sin(dlon/2)**2
            c = 2 * np.arcsin(np.sqrt(a))
            r = 6371  # Earth's radius in kilometers
            
            total_length += c * r
        
        return total_length
    
    def _get_highest_risk_pipeline(self) -> str:
        """Identify the pipeline with highest risk"""
        pipeline_risks = {}
        
        for pipeline_id in self.active_pipelines.keys():
            alerts = [a for a in self.active_alerts if a.pipeline_id == pipeline_id]
            risk_score = sum({
                AlertSeverity.EMERGENCY: 10,
                AlertSeverity.CRITICAL: 5,
                AlertSeverity.HIGH: 3,
                AlertSeverity.MEDIUM: 1,
                AlertSeverity.LOW: 0.5
            }.get(a.severity, 0) for a in alerts)
            
            pipeline_risks[pipeline_id] = risk_score
        
        return max(pipeline_risks.items(), key=lambda x: x[1])[0] if pipeline_risks else "none"
    
    def _calculate_system_health_score(self) -> float:
        """Calculate overall system health score (0-100)"""
        if not self.active_pipelines:
            return 100
        
        total_score = 100
        
        # Deduct for alerts
        for alert in self.active_alerts:
            deduction = {
                AlertSeverity.EMERGENCY: 20,
                AlertSeverity.CRITICAL: 10,
                AlertSeverity.HIGH: 5,
                AlertSeverity.MEDIUM: 2,
                AlertSeverity.LOW: 1
            }.get(alert.severity, 0)
            total_score -= deduction
        
        return max(0, total_score)


# Example usage and testing
if __name__ == "__main__":
    
    async def demo_pipeline_monitoring():
        """Demonstrate pipeline monitoring capabilities"""
        
        print("🛢️ CRITICAL INFRASTRUCTURE PIPELINE MONITORING")
        print("=" * 60)
        
        # Initialize system
        pipeline_system = PipelineSecuritySystem()
        
        # Register sample pipeline
        sensors = [
            PipelineSensor("PS001", "PIPE_001", (40.7128, -74.0060), "pressure", (50, 100), "PSI", datetime.now()),
            PipelineSensor("FS001", "PIPE_001", (40.7130, -74.0058), "flow", (100, 200), "L/min", datetime.now()),
            PipelineSensor("TS001", "PIPE_001", (40.7132, -74.0056), "temperature", (10, 30), "°C", datetime.now()),
            PipelineSensor("RS001", "PIPE_001", (40.7134, -74.0054), "radiation", (0, 0.2), "μSv/h", datetime.now())
        ]
        
        route = [
            (40.7128, -74.0060),  # New York area
            (40.7589, -73.9851),
            (40.8176, -73.9782)
        ]
        
        pipeline_system.register_pipeline("PIPE_001", PipelineType.OIL, route, sensors)
        
        # Initialize baseline with sample data
        sample_data = pd.DataFrame({
            'pressure': np.random.normal(75, 5, 1000),
            'flow_rate': np.random.normal(150, 10, 1000),
            'temperature': np.random.normal(20, 3, 1000)
        })
        
        pipeline_system.leak_detector.initialize_baseline("PIPE_001", sample_data)
        
        print("✅ Pipeline system initialized")
        print(f"   - Pipeline: PIPE_001 (Oil)")
        print(f"   - Sensors: {len(sensors)}")
        print(f"   - Length: {pipeline_system.active_pipelines['PIPE_001']['total_length_km']:.1f} km")
        
        # Simulate normal readings
        print("\n📊 Processing normal sensor readings...")
        normal_readings = {
            'pressure': 74.5,
            'flow_rate': 148.2,
            'temperature': 19.8,
            'radiation_usv_h': 0.15
        }
        
        alerts = pipeline_system.process_sensor_data("PS001", normal_readings)
        print(f"   Normal readings processed - {len(alerts)} alerts generated")
        
        # Simulate leak scenario
        print("\n🚨 Simulating potential leak scenario...")
        leak_readings = {
            'pressure': 45.0,  # Significant pressure drop
            'flow_rate': 95.0,  # Reduced flow
            'temperature': 22.1,
            'radiation_usv_h': 0.16
        }
        
        alerts = pipeline_system.process_sensor_data("PS001", leak_readings)
        print(f"   Leak simulation - {len(alerts)} alerts generated")
        
        for alert in alerts:
            print(f"   🚨 ALERT: {alert.alert_type} - {alert.severity.value}")
            print(f"      Description: {alert.description}")
            print(f"      Impact: {alert.predicted_impact}")
        
        # Get pipeline status
        print("\n📋 Pipeline Status Report:")
        status = pipeline_system.get_pipeline_status("PIPE_001")
        for key, value in status.items():
            if key != 'recent_alerts':
                print(f"   {key}: {value}")
        
        # National overview
        print("\n🇺🇸 National Pipeline Infrastructure Overview:")
        overview = pipeline_system.get_national_pipeline_overview()
        print(f"   Infrastructure: {overview['national_infrastructure_status']}")
        print(f"   Security Status: {overview['security_status']}")
    
    # Run demo
    asyncio.run(demo_pipeline_monitoring())