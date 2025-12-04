"""
Nigeria Police Force Integration
High-confidence security alerts, analyst review, rapid response coordination
Situation Room connector for kidnapping, armed robbery, suspicious activity
"""
from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any, Literal
from enum import Enum
from datetime import datetime, timedelta
import hashlib
import uuid
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Nigeria Police Force Integration", version="1.0.0")


class ThreatType(str, Enum):
    """Security threat categories"""
    KIDNAPPING = "kidnapping"
    ARMED_ROBBERY = "armed_robbery"
    TERRORISM = "terrorism"
    SUSPICIOUS_ACTIVITY = "suspicious_activity"
    VEHICLE_THEFT = "vehicle_theft"
    ASSAULT = "assault"
    OTHER = "other"


class AlertSeverity(str, Enum):
    """Alert severity levels"""
    LOW = "low"              # Monitor only
    MEDIUM = "medium"        # Analyst review required
    HIGH = "high"            # Dispatch recommendation
    CRITICAL = "critical"    # Immediate dispatch


class AlertStatus(str, Enum):
    """Alert processing status"""
    DETECTED = "detected"
    ANALYST_REVIEW = "analyst_review"
    APPROVED = "approved"
    REJECTED = "rejected"
    DISPATCHED = "dispatched"
    RESPONDED = "responded"
    RESOLVED = "resolved"


class AnalystDecision(str, Enum):
    """Analyst review outcome"""
    APPROVE_DISPATCH = "approve_dispatch"
    ESCALATE = "escalate"
    FALSE_POSITIVE = "false_positive"
    NEED_MORE_INFO = "need_more_info"


class SecurityAlert(BaseModel):
    """Security alert from AI detection"""
    alert_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    threat_type: ThreatType
    severity: AlertSeverity
    confidence: float = Field(..., ge=0.0, le=1.0)
    timestamp: str
    location: Dict[str, float] = Field(..., description="GPS coordinates")
    description: str
    detected_by: str  # device_id or system
    evidence: Dict[str, Any] = Field(default_factory=dict)
    metadata: Dict[str, Any] = Field(default_factory=dict)
    
    class Config:
        json_schema_extra = {
            "example": {
                "alert_id": "alert-001",
                "threat_type": "kidnapping",
                "severity": "high",
                "confidence": 0.89,
                "timestamp": "2025-11-27T15:00:00Z",
                "location": {"lat": 9.0765, "lon": 7.3986, "accuracy_m": 10},
                "description": "Suspicious vehicle (black SUV) observed following school bus for 15 minutes",
                "detected_by": "traffic-cam-045",
                "evidence": {
                    "vehicle_plate": "ABC-123-XY",
                    "duration_minutes": 15,
                    "erratic_behavior": True
                }
            }
        }


class AnalystReview(BaseModel):
    """Analyst review of security alert"""
    review_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    alert_id: str
    analyst_id: str
    decision: AnalystDecision
    confidence_override: Optional[float] = Field(None, ge=0.0, le=1.0)
    notes: str
    recommended_action: str
    reviewed_at: str = Field(default_factory=lambda: datetime.utcnow().isoformat())


class PoliceDispatch(BaseModel):
    """Police dispatch order"""
    dispatch_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    alert_id: str
    station_id: str
    station_name: str
    units_dispatched: List[str]
    officers: List[str]
    dispatch_time: str
    estimated_arrival_min: int
    priority: Literal["routine", "urgent", "emergency"]
    special_instructions: Optional[str] = None


class IncidentRecord(BaseModel):
    """Complete incident record"""
    incident_id: str
    alert: SecurityAlert
    analyst_review: Optional[AnalystReview]
    dispatch: Optional[PoliceDispatch]
    status: AlertStatus
    response_log: List[Dict[str, Any]] = Field(default_factory=list)
    created_at: str
    resolved_at: Optional[str] = None


class PoliceStation(BaseModel):
    """Police station information"""
    station_id: str
    name: str
    division: str
    location: Dict[str, float]
    contact_numbers: List[str]
    email: str
    available_units: int
    specializations: List[str]


class PoliceForceConnector:
    """
    Nigeria Police Force integration
    In production: integrate with official Police Situation Room
    """
    
    def __init__(self):
        # Police stations database
        self.police_stations = {
            "NPF-FCT-001": PoliceStation(
                station_id="NPF-FCT-001",
                name="Force Headquarters - Abuja",
                division="FCT Command",
                location={"lat": 9.0765, "lon": 7.3986},
                contact_numbers=["112", "08037133078", "+234-9-461-0000"],
                email="fct@npf.gov.ng",
                available_units=15,
                specializations=["SARS", "Anti-Kidnapping", "Intelligence"]
            ),
            "NPF-LAG-001": PoliceStation(
                station_id="NPF-LAG-001",
                name="Lagos State Police Command - Ikeja",
                division="Lagos State Command",
                location={"lat": 6.6018, "lon": 3.3515},
                contact_numbers=["112", "08063237147", "+234-1-794-5555"],
                email="lagos@npf.gov.ng",
                available_units=20,
                specializations=["RRS", "Anti-Robbery", "Marine"]
            )
        }
        
        # Active incidents
        self.incidents: Dict[str, IncidentRecord] = {}
        
        # Approved analysts (in production: SSO/LDAP)
        self.analysts = {
            "analyst-001": {"name": "John Doe", "clearance": "high"},
            "analyst-002": {"name": "Jane Smith", "clearance": "critical"}
        }
        
        # Dispatch log (immutable)
        self.dispatch_log: List[PoliceDispatch] = []
        
        logger.info("Police Force connector initialized")
    
    def find_nearest_station(self, location: Dict[str, float], specialization: Optional[str] = None) -> PoliceStation:
        """Find nearest police station"""
        lat = location['lat']
        lon = location['lon']
        
        min_distance = float('inf')
        nearest_station = None
        
        for station in self.police_stations.values():
            # Check specialization if specified
            if specialization and specialization not in station.specializations:
                continue
            
            s_lat = station.location['lat']
            s_lon = station.location['lon']
            
            # Simple distance
            distance = ((lat - s_lat)**2 + (lon - s_lon)**2)**0.5 * 111  # km
            
            if distance < min_distance and station.available_units > 0:
                min_distance = distance
                nearest_station = station
        
        if not nearest_station:
            # Fallback to any station
            nearest_station = list(self.police_stations.values())[0]
        
        return nearest_station
    
    def create_incident(self, alert: SecurityAlert) -> IncidentRecord:
        """Create incident from security alert"""
        incident_id = f"INC-{datetime.utcnow().strftime('%Y%m%d')}-{str(uuid.uuid4())[:8].upper()}"
        
        # Determine initial status based on confidence
        if alert.confidence >= 0.9 and alert.severity == AlertSeverity.CRITICAL:
            status = AlertStatus.ANALYST_REVIEW  # Fast-track for review
        elif alert.confidence >= 0.8:
            status = AlertStatus.ANALYST_REVIEW
        else:
            status = AlertStatus.DETECTED
        
        incident = IncidentRecord(
            incident_id=incident_id,
            alert=alert,
            analyst_review=None,
            dispatch=None,
            status=status,
            created_at=datetime.utcnow().isoformat()
        )
        
        self.incidents[incident_id] = incident
        
        logger.info(f"Incident created: {incident_id} - {alert.threat_type} (confidence: {alert.confidence})")
        
        # Auto-escalate for critical threats
        if alert.severity == AlertSeverity.CRITICAL and alert.confidence >= 0.9:
            logger.warning(f"🚨 CRITICAL ALERT: {incident_id} - {alert.threat_type} - REQUIRES IMMEDIATE ANALYST REVIEW")
        
        return incident
    
    def submit_analyst_review(self, review: AnalystReview) -> IncidentRecord:
        """Analyst reviews alert and decides action"""
        if review.alert_id not in self.incidents:
            raise HTTPException(status_code=404, detail="Incident not found")
        
        incident = self.incidents[review.alert_id]
        
        # Verify analyst authorization
        if review.analyst_id not in self.analysts:
            raise HTTPException(status_code=403, detail="Unauthorized analyst")
        
        incident.analyst_review = review
        
        # Update status based on decision
        if review.decision == AnalystDecision.APPROVE_DISPATCH:
            incident.status = AlertStatus.APPROVED
            logger.info(f"✅ Analyst approved dispatch for {review.alert_id}")
        
        elif review.decision == AnalystDecision.FALSE_POSITIVE:
            incident.status = AlertStatus.REJECTED
            logger.info(f"❌ Analyst rejected {review.alert_id} as false positive")
        
        elif review.decision == AnalystDecision.ESCALATE:
            incident.status = AlertStatus.ANALYST_REVIEW
            logger.warning(f"⚠️ Escalated {review.alert_id} for senior review")
        
        # Add to response log
        incident.response_log.append({
            'timestamp': review.reviewed_at,
            'action': 'analyst_review',
            'analyst': review.analyst_id,
            'decision': review.decision.value,
            'notes': review.notes
        })
        
        return incident
    
    def dispatch_police(self, incident_id: str, priority: Literal["routine", "urgent", "emergency"]) -> PoliceDispatch:
        """
        Dispatch police units to incident
        CRITICAL: Only after analyst approval
        """
        if incident_id not in self.incidents:
            raise HTTPException(status_code=404, detail="Incident not found")
        
        incident = self.incidents[incident_id]
        
        # SAFETY CHECK: Require analyst approval
        if incident.status != AlertStatus.APPROVED:
            raise HTTPException(
                status_code=403,
                detail=f"Cannot dispatch without analyst approval. Current status: {incident.status}"
            )
        
        if not incident.analyst_review:
            raise HTTPException(status_code=403, detail="Analyst review required before dispatch")
        
        # Find appropriate station
        specialization = None
        if incident.alert.threat_type == ThreatType.KIDNAPPING:
            specialization = "Anti-Kidnapping"
        elif incident.alert.threat_type == ThreatType.ARMED_ROBBERY:
            specialization = "Anti-Robbery"
        
        station = self.find_nearest_station(incident.alert.location, specialization)
        
        # Create dispatch order
        dispatch = PoliceDispatch(
            alert_id=incident_id,
            station_id=station.station_id,
            station_name=station.name,
            units_dispatched=["Unit-1", "Unit-2"],  # In production: actual unit IDs
            officers=["Officer-A", "Officer-B", "Officer-C"],  # In production: actual officer IDs
            dispatch_time=datetime.utcnow().isoformat(),
            estimated_arrival_min=10,
            priority=priority,
            special_instructions=incident.analyst_review.recommended_action
        )
        
        incident.dispatch = dispatch
        incident.status = AlertStatus.DISPATCHED
        
        # Log dispatch
        self.dispatch_log.append(dispatch)
        
        incident.response_log.append({
            'timestamp': dispatch.dispatch_time,
            'action': 'dispatch',
            'station': station.name,
            'units': dispatch.units_dispatched,
            'priority': priority
        })
        
        # In production: Send via Police radio system / Situation Room API
        logger.warning(f"🚔 POLICE DISPATCHED: {incident_id} -> {station.name} ({priority.upper()} priority)")
        logger.info(f"Units: {dispatch.units_dispatched}, ETA: {dispatch.estimated_arrival_min} min")
        
        return dispatch
    
    def update_incident_status(
        self,
        incident_id: str,
        status: AlertStatus,
        details: Optional[Dict[str, Any]] = None
    ):
        """Update incident status"""
        if incident_id not in self.incidents:
            raise HTTPException(status_code=404, detail="Incident not found")
        
        incident = self.incidents[incident_id]
        old_status = incident.status
        incident.status = status
        
        incident.response_log.append({
            'timestamp': datetime.utcnow().isoformat(),
            'action': 'status_update',
            'old_status': old_status.value,
            'new_status': status.value,
            'details': details or {}
        })
        
        if status == AlertStatus.RESOLVED:
            incident.resolved_at = datetime.utcnow().isoformat()
        
        logger.info(f"Incident {incident_id} status: {old_status} -> {status}")
    
    def get_pending_reviews(self) -> List[IncidentRecord]:
        """Get incidents awaiting analyst review"""
        return [
            inc for inc in self.incidents.values()
            if inc.status == AlertStatus.ANALYST_REVIEW and not inc.analyst_review
        ]
    
    def get_active_incidents(self) -> List[IncidentRecord]:
        """Get active (unresolved) incidents"""
        return [
            inc for inc in self.incidents.values()
            if inc.status not in [AlertStatus.RESOLVED, AlertStatus.REJECTED]
        ]


# Initialize service
police_service = PoliceForceConnector()


# API Endpoints

@app.post("/api/v1/alerts", response_model=IncidentRecord)
async def submit_security_alert(alert: SecurityAlert):
    """
    Submit security alert from AI detection
    High-confidence alerts auto-escalate to analyst review
    """
    # Validate confidence threshold
    if alert.confidence < 0.6:
        raise HTTPException(
            status_code=400,
            detail=f"Confidence {alert.confidence} below minimum threshold 0.6"
        )
    
    incident = police_service.create_incident(alert)
    return incident


@app.post("/api/v1/incidents/{incident_id}/review")
async def submit_analyst_review(incident_id: str, review: AnalystReview):
    """
    Analyst reviews incident and approves/rejects dispatch
    MANDATORY for all dispatches
    """
    review.alert_id = incident_id  # Ensure consistency
    incident = police_service.submit_analyst_review(review)
    return incident


@app.post("/api/v1/incidents/{incident_id}/dispatch", response_model=PoliceDispatch)
async def dispatch_police_units(
    incident_id: str,
    priority: Literal["routine", "urgent", "emergency"] = "urgent"
):
    """
    Dispatch police units to incident
    REQUIRES analyst approval
    """
    dispatch = police_service.dispatch_police(incident_id, priority)
    return dispatch


@app.post("/api/v1/incidents/{incident_id}/status")
async def update_status(
    incident_id: str,
    status: AlertStatus,
    details: Optional[Dict[str, Any]] = None
):
    """Update incident status (field officers)"""
    police_service.update_incident_status(incident_id, status, details)
    return {"incident_id": incident_id, "status": status}


@app.get("/api/v1/incidents", response_model=List[IncidentRecord])
async def list_incidents(
    active_only: bool = False,
    pending_review: bool = False
):
    """List incidents"""
    if pending_review:
        return police_service.get_pending_reviews()
    elif active_only:
        return police_service.get_active_incidents()
    return list(police_service.incidents.values())


@app.get("/api/v1/incidents/{incident_id}", response_model=IncidentRecord)
async def get_incident(incident_id: str):
    """Get incident details"""
    if incident_id not in police_service.incidents:
        raise HTTPException(status_code=404, detail="Incident not found")
    return police_service.incidents[incident_id]


@app.get("/api/v1/stations", response_model=List[PoliceStation])
async def list_police_stations():
    """List police stations"""
    return list(police_service.police_stations.values())


@app.get("/api/v1/stations/nearest")
async def find_nearest_station(lat: float, lon: float, specialization: Optional[str] = None):
    """Find nearest police station"""
    location = {"lat": lat, "lon": lon}
    station = police_service.find_nearest_station(location, specialization)
    return station


@app.get("/health")
async def health_check():
    """Health check"""
    pending_reviews = len(police_service.get_pending_reviews())
    active_incidents = len(police_service.get_active_incidents())
    
    return {
        "status": "healthy",
        "service": "police-force-integration",
        "pending_analyst_review": pending_reviews,
        "active_incidents": active_incidents,
        "total_incidents": len(police_service.incidents),
        "dispatches_today": len(police_service.dispatch_log)
    }


if __name__ == "__main__":
    import uvicorn
    
    logger.info("Nigeria Police Force integration started")
    logger.info("Emergency contacts: 112 (national)")
    logger.info("CRITICAL: All dispatches require analyst approval")
    logger.info("SAFETY: Human-in-the-loop enforced for all police responses")
    
    uvicorn.run(app, host="0.0.0.0", port=8087)
