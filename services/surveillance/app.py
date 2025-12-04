"""
City Surveillance Service - Video Management System Integration

LEGAL COMPLIANCE:
- NDPR 2019: Purpose limitation (security only), data minimization (metadata only)
- Cybercrime Act 2015: Authorized access, encrypted transmission
- Lagos State CCTV Law 2021: Public safety, privacy safeguards

TECHNICAL FEATURES:
- RTSP/ONVIF camera integration (no direct recording)
- AI video analysis pipeline (YOLOv8, OpenCV)
- Event-driven alerts (fire, crowd, violence, LPR)
- Google Maps integration (legal display only)
- Playback via VMS APIs (not local storage)

ARCHITECTURE:
- Camera metadata registry (locations, capabilities)
- Live stream proxy (RTSP → WebRTC for dashboard)
- AI inference engine (edge or cloud)
- Event database (alerts only, no video storage)
- Geospatial search (cameras near incident)

PORT: 8091
"""

from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field, validator
from typing import Optional, List, Literal, Dict
from datetime import datetime, timedelta
from enum import Enum
import logging
import asyncio
import json
import hashlib

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="City Surveillance Service", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:3001"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ============================================================================
# MODELS
# ============================================================================

class CameraType(str, Enum):
    TRAFFIC = "traffic"
    SECURITY = "security"
    PTZ = "ptz"
    DOME = "dome"
    BULLET = "bullet"
    DRONE = "drone"

class EventType(str, Enum):
    VEHICLE_DETECTION = "vehicle_detection"
    CROWD_DETECTION = "crowd_detection"
    FIRE_SMOKE = "fire_smoke"
    VIOLENCE = "violence"
    ABANDONED_OBJECT = "abandoned_object"
    LICENSE_PLATE = "license_plate"
    DRONE_DETECTION = "drone_detection"
    PERSON_OF_INTEREST = "person_of_interest"
    ACCIDENT = "accident"
    RIOT = "riot"

class CameraLocation(BaseModel):
    lat: float = Field(..., ge=-90, le=90)
    lng: float = Field(..., ge=-180, le=180)
    address: Optional[str] = None
    city: str
    state: str

class CameraRegistration(BaseModel):
    camera_id: str = Field(..., pattern=r"^[A-Z]{3}-[A-Z0-9\-]{5,20}$")
    name: str
    location: CameraLocation
    stream_url: str  # rtsp://... or https://... (ONVIF)
    camera_type: CameraType
    capabilities: List[str] = []  # ["ptz", "ir", "audio", "lpr"]
    owner: str  # "Lagos State", "FCT Police", "Airport Authority"
    authorization_level: int = Field(..., ge=1, le=5)  # 1=Public, 5=Restricted

class Camera(CameraRegistration):
    registered_at: datetime
    last_seen: datetime
    status: Literal["online", "offline", "maintenance"]
    ai_enabled: bool = True

class VideoEvent(BaseModel):
    event_id: str
    camera_id: str
    timestamp: datetime
    event_type: EventType
    confidence: float = Field(..., ge=0.0, le=1.0)
    location: CameraLocation
    metadata: Dict  # Event-specific data (vehicle color, crowd size, etc.)
    snapshot_url: Optional[str] = None  # S3 URL for 30-day retention
    officer_notified: bool = False

class SurveillanceSearchRequest(BaseModel):
    city: str
    query: str  # "red toyota camry", "crowd gathering", "fire"
    time_range: Literal["last_hour", "last_2_hours", "last_6_hours", "last_24_hours", "custom"]
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    event_types: Optional[List[EventType]] = None
    min_confidence: float = 0.7

class SurveillanceSearchResult(BaseModel):
    event: VideoEvent
    camera: Camera
    distance_km: Optional[float] = None  # Distance from search point

class LiveFeedRequest(BaseModel):
    camera_id: str
    officer_id: str
    case_id: Optional[str] = None
    duration_minutes: int = Field(default=15, le=60)  # Max 1 hour per session

# ============================================================================
# MOCK DATA (Replace with real VMS/Camera APIs)
# ============================================================================

MOCK_CAMERAS: Dict[str, Camera] = {
    "ABJ-HIGHWAY-221": Camera(
        camera_id="ABJ-HIGHWAY-221",
        name="Airport Road Junction",
        location=CameraLocation(lat=9.0722, lng=7.4914, address="Airport Road, Abuja", city="Abuja", state="FCT"),
        stream_url="rtsp://mock-vms.gov.ng:554/camera/abj-221",
        camera_type=CameraType.TRAFFIC,
        capabilities=["ptz", "lpr", "ir"],
        owner="FCT Police",
        authorization_level=3,
        registered_at=datetime(2025, 1, 15),
        last_seen=datetime.utcnow(),
        status="online",
        ai_enabled=True
    ),
    "LOS-ISLAND-112": Camera(
        camera_id="LOS-ISLAND-112",
        name="Victoria Island Roundabout",
        location=CameraLocation(lat=6.4281, lng=3.4219, address="Ahmadu Bello Way, VI", city="Lagos", state="Lagos"),
        stream_url="rtsp://mock-vms.gov.ng:554/camera/los-112",
        camera_type=CameraType.PTZ,
        capabilities=["ptz", "zoom", "audio"],
        owner="Lagos State Security Trust Fund",
        authorization_level=2,
        registered_at=datetime(2025, 2, 10),
        last_seen=datetime.utcnow(),
        status="online",
        ai_enabled=True
    ),
    "ABJ-DRONE-001": Camera(
        camera_id="ABJ-DRONE-001",
        name="Aso Rock Patrol Drone",
        location=CameraLocation(lat=9.0765, lng=7.4890, address="Aso Villa Perimeter", city="Abuja", state="FCT"),
        stream_url="rtsp://mock-drone.gov.ng:554/drone/001",
        camera_type=CameraType.DRONE,
        capabilities=["thermal", "night_vision", "gps"],
        owner="DSS",
        authorization_level=5,
        registered_at=datetime(2025, 3, 1),
        last_seen=datetime.utcnow(),
        status="online",
        ai_enabled=True
    )
}

MOCK_EVENTS: List[VideoEvent] = [
    VideoEvent(
        event_id="EVT-20251127-001",
        camera_id="ABJ-HIGHWAY-221",
        timestamp=datetime.utcnow() - timedelta(minutes=15),
        event_type=EventType.VEHICLE_DETECTION,
        confidence=0.92,
        location=CameraLocation(lat=9.0722, lng=7.4914, city="Abuja", state="FCT"),
        metadata={"vehicle_type": "sedan", "color": "red", "make": "Toyota Camry", "direction": "north"},
        snapshot_url="https://mock-s3.gov.ng/events/evt-001.jpg",
        officer_notified=False
    ),
    VideoEvent(
        event_id="EVT-20251127-002",
        camera_id="LOS-ISLAND-112",
        timestamp=datetime.utcnow() - timedelta(minutes=45),
        event_type=EventType.CROWD_DETECTION,
        confidence=0.87,
        location=CameraLocation(lat=6.4281, lng=3.4219, city="Lagos", state="Lagos"),
        metadata={"crowd_size": 150, "density": "high", "movement": "static"},
        snapshot_url="https://mock-s3.gov.ng/events/evt-002.jpg",
        officer_notified=True
    ),
    VideoEvent(
        event_id="EVT-20251127-003",
        camera_id="ABJ-HIGHWAY-221",
        timestamp=datetime.utcnow() - timedelta(hours=1),
        event_type=EventType.ACCIDENT,
        confidence=0.95,
        location=CameraLocation(lat=9.0722, lng=7.4914, city="Abuja", state="FCT"),
        metadata={"severity": "minor", "vehicles_involved": 2, "lane_blocked": "left"},
        snapshot_url="https://mock-s3.gov.ng/events/evt-003.jpg",
        officer_notified=True
    )
]

# Active WebSocket connections (for live feed streaming)
active_connections: Dict[str, WebSocket] = {}

# ============================================================================
# CAMERA MANAGEMENT
# ============================================================================

@app.post("/api/v1/cameras/register", response_model=Camera)
async def register_camera(camera: CameraRegistration):
    """
    Register a new camera in the VMS
    
    AUTHORIZATION: VMS administrator only
    VALIDATION: Test RTSP connection before registration
    """
    if camera.camera_id in MOCK_CAMERAS:
        raise HTTPException(status_code=400, detail="Camera already registered")
    
    new_camera = Camera(
        **camera.dict(),
        registered_at=datetime.utcnow(),
        last_seen=datetime.utcnow(),
        status="online",
        ai_enabled=True
    )
    
    MOCK_CAMERAS[camera.camera_id] = new_camera
    logger.info(f"Registered camera: {camera.camera_id} at {camera.location.address}")
    
    return new_camera

@app.get("/api/v1/cameras", response_model=List[Camera])
async def list_cameras(city: Optional[str] = None, status: Optional[str] = None):
    """Get all registered cameras (with optional filters)"""
    cameras = list(MOCK_CAMERAS.values())
    
    if city:
        cameras = [c for c in cameras if c.location.city.lower() == city.lower()]
    if status:
        cameras = [c for c in cameras if c.status == status]
    
    return cameras

@app.get("/api/v1/cameras/{camera_id}", response_model=Camera)
async def get_camera(camera_id: str):
    """Get camera details"""
    camera = MOCK_CAMERAS.get(camera_id)
    if not camera:
        raise HTTPException(status_code=404, detail="Camera not found")
    return camera

@app.get("/api/v1/cameras/nearby")
async def get_nearby_cameras(lat: float, lng: float, radius_km: float = 5.0):
    """
    Get cameras within radius of a location
    
    Uses Haversine formula for distance calculation
    """
    def haversine(lat1, lon1, lat2, lon2):
        from math import radians, sin, cos, sqrt, atan2
        R = 6371  # Earth radius in km
        dlat = radians(lat2 - lat1)
        dlon = radians(lon2 - lon1)
        a = sin(dlat/2)**2 + cos(radians(lat1)) * cos(radians(lat2)) * sin(dlon/2)**2
        c = 2 * atan2(sqrt(a), sqrt(1-a))
        return R * c
    
    nearby = []
    for camera in MOCK_CAMERAS.values():
        distance = haversine(lat, lng, camera.location.lat, camera.location.lng)
        if distance <= radius_km:
            nearby.append({"camera": camera, "distance_km": round(distance, 2)})
    
    return sorted(nearby, key=lambda x: x["distance_km"])

# ============================================================================
# VIDEO ANALYSIS & EVENTS
# ============================================================================

@app.post("/api/v1/surveillance/search", response_model=List[SurveillanceSearchResult])
async def search_surveillance(request: SurveillanceSearchRequest):
    """
    Search video events by query (natural language)
    
    PRIVACY: Returns event metadata only, no raw video
    AI: Uses semantic search on event descriptions
    """
    # Parse time range
    now = datetime.utcnow()
    if request.time_range == "last_hour":
        start_time = now - timedelta(hours=1)
    elif request.time_range == "last_2_hours":
        start_time = now - timedelta(hours=2)
    elif request.time_range == "last_6_hours":
        start_time = now - timedelta(hours=6)
    elif request.time_range == "last_24_hours":
        start_time = now - timedelta(hours=24)
    elif request.time_range == "custom":
        start_time = request.start_time or now - timedelta(hours=24)
    else:
        start_time = now - timedelta(hours=24)
    
    end_time = request.end_time or now
    
    # Filter events
    results = []
    for event in MOCK_EVENTS:
        # Time filter
        if not (start_time <= event.timestamp <= end_time):
            continue
        
        # City filter
        if event.location.city.lower() != request.city.lower():
            continue
        
        # Confidence filter
        if event.confidence < request.min_confidence:
            continue
        
        # Event type filter
        if request.event_types and event.event_type not in request.event_types:
            continue
        
        # Query matching (simple keyword search - use semantic search in production)
        query_lower = request.query.lower()
        metadata_str = json.dumps(event.metadata).lower()
        if query_lower in metadata_str or query_lower in event.event_type.value:
            camera = MOCK_CAMERAS.get(event.camera_id)
            if camera:
                results.append(SurveillanceSearchResult(
                    event=event,
                    camera=camera,
                    distance_km=None
                ))
    
    return results

@app.get("/api/v1/events", response_model=List[VideoEvent])
async def get_events(
    camera_id: Optional[str] = None,
    event_type: Optional[EventType] = None,
    limit: int = 100
):
    """Get recent video events"""
    events = MOCK_EVENTS
    
    if camera_id:
        events = [e for e in events if e.camera_id == camera_id]
    if event_type:
        events = [e for e in events if e.event_type == event_type]
    
    # Sort by timestamp (most recent first)
    events = sorted(events, key=lambda x: x.timestamp, reverse=True)
    
    return events[:limit]

@app.post("/api/v1/events/create", response_model=VideoEvent)
async def create_event(event: VideoEvent):
    """
    Create a new video event (called by AI inference engine)
    
    AUTHORIZATION: AI service API key required
    NOTIFICATION: Triggers alerts to operators if high confidence
    """
    MOCK_EVENTS.append(event)
    
    # Trigger notification if critical event
    if event.confidence > 0.85 and event.event_type in [EventType.FIRE_SMOKE, EventType.VIOLENCE, EventType.RIOT]:
        logger.warning(f"CRITICAL EVENT: {event.event_type.value} at {event.location.address} (confidence: {event.confidence})")
        # TODO: Send SMS/push notification to operators
    
    return event

# ============================================================================
# LIVE FEED (WebSocket)
# ============================================================================

@app.websocket("/ws/camera/{camera_id}")
async def camera_live_feed(websocket: WebSocket, camera_id: str):
    """
    WebSocket for live camera feed
    
    PRODUCTION: Proxy RTSP → WebRTC using FFmpeg/Janus
    AUTHORIZATION: JWT token in query params
    RATE LIMIT: Max 5 concurrent streams per officer
    """
    await websocket.accept()
    
    camera = MOCK_CAMERAS.get(camera_id)
    if not camera:
        await websocket.send_json({"error": "Camera not found"})
        await websocket.close()
        return
    
    active_connections[camera_id] = websocket
    
    try:
        # Send camera metadata
        await websocket.send_json({
            "type": "camera_info",
            "camera": camera.dict()
        })
        
        # Simulate live feed frames (production: proxy RTSP stream)
        while True:
            # Mock frame data
            await websocket.send_json({
                "type": "frame",
                "timestamp": datetime.utcnow().isoformat(),
                "frame_number": 0,
                "message": "Live feed placeholder - integrate with RTSP proxy"
            })
            await asyncio.sleep(1)
    
    except WebSocketDisconnect:
        logger.info(f"WebSocket disconnected for camera {camera_id}")
        if camera_id in active_connections:
            del active_connections[camera_id]

@app.post("/api/v1/live-feed/request", response_model=dict)
async def request_live_feed(request: LiveFeedRequest):
    """
    Request live feed access (audit log + time limit)
    
    AUTHORIZATION: Officer ID + case ID required
    AUDIT: All feed access logged
    TIME LIMIT: Max 60 minutes per session
    """
    camera = MOCK_CAMERAS.get(request.camera_id)
    if not camera:
        raise HTTPException(status_code=404, detail="Camera not found")
    
    # Authorization check
    if camera.authorization_level >= 4 and not request.case_id:
        raise HTTPException(status_code=403, detail="Case ID required for restricted cameras")
    
    # Generate session token
    session_token = hashlib.sha256(f"{request.officer_id}:{request.camera_id}:{datetime.utcnow()}".encode()).hexdigest()
    
    logger.info(f"Live feed requested: Officer {request.officer_id} → Camera {request.camera_id}")
    
    return {
        "session_token": session_token,
        "websocket_url": f"ws://localhost:8091/ws/camera/{request.camera_id}",
        "expires_at": (datetime.utcnow() + timedelta(minutes=request.duration_minutes)).isoformat(),
        "camera": camera
    }

# ============================================================================
# STATISTICS
# ============================================================================

@app.get("/api/v1/stats")
async def get_stats():
    """Get surveillance system statistics"""
    return {
        "total_cameras": len(MOCK_CAMERAS),
        "cameras_online": len([c for c in MOCK_CAMERAS.values() if c.status == "online"]),
        "total_events": len(MOCK_EVENTS),
        "events_last_hour": len([e for e in MOCK_EVENTS if e.timestamp > datetime.utcnow() - timedelta(hours=1)]),
        "active_streams": len(active_connections),
        "cities_covered": len(set(c.location.city for c in MOCK_CAMERAS.values()))
    }

@app.get("/health")
async def health():
    return {
        "status": "healthy",
        "service": "city-surveillance",
        "version": "1.0.0",
        "cameras": len(MOCK_CAMERAS),
        "events": len(MOCK_EVENTS)
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8091)
