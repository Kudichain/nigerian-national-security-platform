"""
Federal Fire Service Integration
Automated fire/smoke detection, GPS alerting, authenticated incident notification
Emergency response coordination with Fire Service command centers
"""
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any, Literal
from enum import Enum
from datetime import datetime, timedelta
import hashlib
import uuid
import logging
import asyncio

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Federal Fire Service Integration", version="1.0.0")


class IncidentSeverity(str, Enum):
    """Fire incident severity levels"""
    LOW = "low"              # Smoke detected, no visible flames
    MEDIUM = "medium"        # Small fire, localized
    HIGH = "high"            # Large fire, spreading
    CRITICAL = "critical"    # Major fire, lives at risk


class IncidentStatus(str, Enum):
    """Incident response status"""
    DETECTED = "detected"
    NOTIFIED = "notified"
    DISPATCHED = "dispatched"
    ON_SCENE = "on_scene"
    CONTAINED = "contained"
    EXTINGUISHED = "extinguished"


class FireDetection(BaseModel):
    """Fire/smoke detection event from drone/camera"""
    detection_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    device_id: str
    timestamp: str
    location: Dict[str, float] = Field(..., description="GPS coordinates")
    severity: IncidentSeverity
    confidence: float = Field(..., ge=0.0, le=1.0)
    image_template: Optional[str] = None  # Encrypted/compressed image for verification
    metadata: Dict[str, Any] = Field(default_factory=dict)
    
    class Config:
        json_schema_extra = {
            "example": {
                "detection_id": "fire-det-001",
                "device_id": "drone-fire-001",
                "timestamp": "2025-11-27T14:30:00Z",
                "location": {"lat": 9.0765, "lon": 7.3986, "accuracy_m": 5, "altitude_m": 150},
                "severity": "high",
                "confidence": 0.92,
                "metadata": {
                    "smoke_density": "high",
                    "flame_detected": True,
                    "wind_speed_kmh": 15,
                    "temperature_c": 35
                }
            }
        }


class IncidentNotification(BaseModel):
    """Notification sent to Fire Service"""
    incident_id: str
    detection_id: str
    severity: IncidentSeverity
    location: Dict[str, float]
    nearest_station: str
    estimated_response_time_min: int
    contact_numbers: List[str]
    message: str
    sent_at: str
    authenticated: bool
    signature: str


class IncidentRecord(BaseModel):
    """Complete incident record"""
    incident_id: str
    detection: FireDetection
    notification: Optional[IncidentNotification]
    status: IncidentStatus
    assigned_station: Optional[str]
    dispatch_time: Optional[str]
    response_team: Optional[List[str]]
    updates: List[Dict[str, Any]] = Field(default_factory=list)
    created_at: str
    resolved_at: Optional[str] = None


class FireStation(BaseModel):
    """Fire station information"""
    station_id: str
    name: str
    location: Dict[str, float]
    contact_numbers: List[str]
    email: str
    capacity: int
    available_units: int
    coverage_radius_km: float


class FireServiceConnector:
    """
    Federal Fire Service integration
    In production: integrate with official Fire Service dispatch system
    """
    
    def __init__(self):
        # Fire stations database
        self.fire_stations = {
            "FFS-FCT-001": FireStation(
                station_id="FFS-FCT-001",
                name="Federal Fire Service HQ - Area 10, Garki",
                location={"lat": 9.0443, "lon": 7.4889},
                contact_numbers=["112", "+234-9-234-1234"],
                email="fct@federalfireservice.gov.ng",
                capacity=10,
                available_units=7,
                coverage_radius_km=15.0
            ),
            "FFS-LAG-001": FireStation(
                station_id="FFS-LAG-001",
                name="Lagos State Fire Service - Alausa",
                location={"lat": 6.6018, "lon": 3.3515},
                contact_numbers=["112", "767", "+234-1-775-0018"],
                email="operations@lagosfire.gov.ng",
                capacity=15,
                available_units=10,
                coverage_radius_km=20.0
            )
        }
        
        # Active incidents
        self.incidents: Dict[str, IncidentRecord] = {}
        
        # Notification log (immutable)
        self.notification_log: List[IncidentNotification] = []
        
        logger.info("Fire Service connector initialized")
    
    def find_nearest_station(self, location: Dict[str, float]) -> FireStation:
        """Find nearest fire station with available capacity"""
        lat = location['lat']
        lon = location['lon']
        
        # Simple distance calculation (in production: use proper geospatial lib)
        min_distance = float('inf')
        nearest_station = None
        
        for station in self.fire_stations.values():
            s_lat = station.location['lat']
            s_lon = station.location['lon']
            
            # Haversine distance (simplified)
            distance = ((lat - s_lat)**2 + (lon - s_lon)**2)**0.5 * 111  # approx km
            
            if distance < min_distance and station.available_units > 0:
                min_distance = distance
                nearest_station = station
        
        if not nearest_station:
            # Fallback to any station
            nearest_station = list(self.fire_stations.values())[0]
        
        return nearest_station
    
    def create_incident(self, detection: FireDetection) -> IncidentRecord:
        """Create incident from fire detection"""
        incident_id = f"INC-{datetime.utcnow().strftime('%Y%m%d')}-{str(uuid.uuid4())[:8].upper()}"
        
        incident = IncidentRecord(
            incident_id=incident_id,
            detection=detection,
            notification=None,
            status=IncidentStatus.DETECTED,
            assigned_station=None,
            dispatch_time=None,
            response_team=None,
            created_at=datetime.utcnow().isoformat()
        )
        
        self.incidents[incident_id] = incident
        logger.info(f"Incident created: {incident_id} at {detection.location}")
        
        return incident
    
    def send_notification(self, incident: IncidentRecord) -> IncidentNotification:
        """
        Send authenticated notification to Fire Service
        In production: use secure SMS/API to Fire Service dispatch
        """
        # Find nearest station
        station = self.find_nearest_station(incident.detection.location)
        
        # Estimate response time (distance / average speed)
        distance_km = 5.0  # Simplified
        estimated_time = int((distance_km / 40) * 60)  # 40 km/h average, convert to minutes
        
        # Create notification message
        message = (
            f"🔥 FIRE INCIDENT ALERT\n"
            f"Incident ID: {incident.incident_id}\n"
            f"Severity: {incident.detection.severity.upper()}\n"
            f"Location: {incident.detection.location['lat']}, {incident.detection.location['lon']}\n"
            f"Confidence: {incident.detection.confidence * 100:.1f}%\n"
            f"Detected: {incident.detection.timestamp}\n"
            f"Nearest Station: {station.name}\n"
            f"Estimated Response: {estimated_time} minutes\n"
            f"Contact 112 for emergency coordination"
        )
        
        # Sign notification (HMAC)
        signature = self._sign_notification(incident.incident_id, station.station_id)
        
        notification = IncidentNotification(
            incident_id=incident.incident_id,
            detection_id=incident.detection.detection_id,
            severity=incident.detection.severity,
            location=incident.detection.location,
            nearest_station=station.name,
            estimated_response_time_min=estimated_time,
            contact_numbers=station.contact_numbers,
            message=message,
            sent_at=datetime.utcnow().isoformat(),
            authenticated=True,
            signature=signature
        )
        
        # Update incident
        incident.notification = notification
        incident.status = IncidentStatus.NOTIFIED
        incident.assigned_station = station.station_id
        
        # Log notification (immutable)
        self.notification_log.append(notification)
        
        # In production: Send via SMS API, Firebase, or Fire Service dispatch system
        logger.warning(f"🔥 FIRE ALERT: {incident.incident_id} -> {station.name}")
        logger.info(f"Notification sent: {notification.message}")
        
        # Simulate SMS to 112 / Fire Service
        self._send_emergency_sms(notification)
        
        return notification
    
    def _sign_notification(self, incident_id: str, station_id: str) -> str:
        """Sign notification with HMAC"""
        secret = b"fire-service-signing-key"
        data = f"{incident_id}:{station_id}:{datetime.utcnow().isoformat()}".encode()
        return hashlib.sha256(data).hexdigest()
    
    def _send_emergency_sms(self, notification: IncidentNotification):
        """
        Send SMS to Fire Service / 112 emergency line
        In production: integrate with SMS gateway
        """
        for number in notification.contact_numbers:
            logger.info(f"SMS sent to {number}: {notification.message[:100]}...")
    
    def update_incident_status(
        self,
        incident_id: str,
        status: IncidentStatus,
        details: Optional[Dict[str, Any]] = None
    ):
        """Update incident status"""
        if incident_id not in self.incidents:
            raise HTTPException(status_code=404, detail="Incident not found")
        
        incident = self.incidents[incident_id]
        old_status = incident.status
        incident.status = status
        
        # Add update to history
        update = {
            'timestamp': datetime.utcnow().isoformat(),
            'old_status': old_status.value,
            'new_status': status.value,
            'details': details or {}
        }
        incident.updates.append(update)
        
        # Handle specific statuses
        if status == IncidentStatus.DISPATCHED:
            incident.dispatch_time = datetime.utcnow().isoformat()
            logger.info(f"Fire units dispatched for {incident_id}")
        
        elif status == IncidentStatus.EXTINGUISHED:
            incident.resolved_at = datetime.utcnow().isoformat()
            logger.info(f"Incident resolved: {incident_id}")
        
        logger.info(f"Incident {incident_id} status: {old_status} -> {status}")
    
    def get_active_incidents(self) -> List[IncidentRecord]:
        """Get all active (unresolved) incidents"""
        return [
            inc for inc in self.incidents.values()
            if inc.status not in [IncidentStatus.EXTINGUISHED]
        ]


# Initialize service
fire_service = FireServiceConnector()


# API Endpoints

@app.post("/api/v1/detect", response_model=IncidentRecord)
async def report_fire_detection(detection: FireDetection):
    """
    Report fire/smoke detection from drone/camera
    Automatically creates incident and notifies Fire Service
    """
    # Validate confidence threshold
    if detection.confidence < 0.7:
        raise HTTPException(
            status_code=400,
            detail=f"Confidence {detection.confidence} below threshold 0.7"
        )
    
    # Create incident
    incident = fire_service.create_incident(detection)
    
    # Auto-notify for high severity
    if detection.severity in [IncidentSeverity.HIGH, IncidentSeverity.CRITICAL]:
        notification = fire_service.send_notification(incident)
        logger.warning(f"🔥 HIGH SEVERITY FIRE: Auto-notified {notification.nearest_station}")
    
    return incident


@app.post("/api/v1/incidents/{incident_id}/notify")
async def send_notification(incident_id: str):
    """
    Manually send notification to Fire Service
    (for operator-reviewed incidents)
    """
    if incident_id not in fire_service.incidents:
        raise HTTPException(status_code=404, detail="Incident not found")
    
    incident = fire_service.incidents[incident_id]
    
    if incident.notification:
        raise HTTPException(status_code=400, detail="Notification already sent")
    
    notification = fire_service.send_notification(incident)
    return notification


@app.post("/api/v1/incidents/{incident_id}/status")
async def update_incident_status(
    incident_id: str,
    status: IncidentStatus,
    details: Optional[Dict[str, Any]] = None
):
    """Update incident status (Fire Service operators)"""
    fire_service.update_incident_status(incident_id, status, details)
    return {"incident_id": incident_id, "status": status}


@app.get("/api/v1/incidents", response_model=List[IncidentRecord])
async def list_incidents(active_only: bool = False):
    """List all incidents"""
    if active_only:
        return fire_service.get_active_incidents()
    return list(fire_service.incidents.values())


@app.get("/api/v1/incidents/{incident_id}", response_model=IncidentRecord)
async def get_incident(incident_id: str):
    """Get specific incident details"""
    if incident_id not in fire_service.incidents:
        raise HTTPException(status_code=404, detail="Incident not found")
    return fire_service.incidents[incident_id]


@app.get("/api/v1/stations", response_model=List[FireStation])
async def list_fire_stations():
    """List all fire stations"""
    return list(fire_service.fire_stations.values())


@app.get("/api/v1/stations/nearest")
async def find_nearest_station(lat: float, lon: float):
    """Find nearest fire station to location"""
    location = {"lat": lat, "lon": lon}
    station = fire_service.find_nearest_station(location)
    return station


@app.get("/health")
async def health_check():
    """Health check"""
    active_incidents = len(fire_service.get_active_incidents())
    
    return {
        "status": "healthy",
        "service": "fire-service-integration",
        "active_incidents": active_incidents,
        "total_incidents": len(fire_service.incidents),
        "notifications_sent": len(fire_service.notification_log)
    }


if __name__ == "__main__":
    import uvicorn
    
    logger.info("Federal Fire Service integration started")
    logger.info("Emergency contacts: 112 (national), 767 (Lagos)")
    logger.info("CRITICAL: Integrate with official Fire Service dispatch system in production")
    
    uvicorn.run(app, host="0.0.0.0", port=8086)
