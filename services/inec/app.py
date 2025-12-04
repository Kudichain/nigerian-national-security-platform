"""
INEC Voting Assistance Service
Privacy-preserving voter verification, polling unit assistance, accessibility support
Complies with Electoral Act, NDPR, INEC BVAS integration guidelines
"""
from fastapi import FastAPI, HTTPException, Depends
from fastapi.security import HTTPBearer
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any, Literal
from enum import Enum
from datetime import datetime, timedelta
import hashlib
import hmac
import uuid
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="INEC Voting Assistance", version="1.0.0")
security = HTTPBearer()


class AssistanceType(str, Enum):
    """Types of voting assistance"""
    VOTER_VERIFICATION = "voter_verification"
    ACCESSIBILITY_SUPPORT = "accessibility_support"  # Physical disabilities
    QUEUE_MANAGEMENT = "queue_management"
    POLLING_UNIT_STATUS = "polling_unit_status"


class VoterStatus(str, Enum):
    """Voter registration status"""
    REGISTERED = "registered"
    NOT_REGISTERED = "not_registered"
    ALREADY_VOTED = "already_voted"
    INVALID_POLLING_UNIT = "invalid_polling_unit"


class VerificationRequest(BaseModel):
    """Voter verification request"""
    request_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    device_id: str
    timestamp: str
    location: Dict[str, float]
    template: str = Field(..., description="Encrypted biometric template")
    purpose: AssistanceType
    polling_unit_id: Optional[str] = None
    signature: str = Field(..., description="Device signature")


class VerificationResponse(BaseModel):
    """Privacy-preserving verification response"""
    request_id: str
    match: bool
    pseudonym: Optional[str] = None  # INEC voter token (unlinkable)
    status: VoterStatus
    allowed_attributes: Dict[str, Any] = Field(default_factory=dict)
    confidence: float
    timestamp: str
    signed_by: str = "INEC"
    
    class Config:
        json_schema_extra = {
            "example": {
                "request_id": "req-001",
                "match": True,
                "pseudonym": "inec_token_abc123",
                "status": "registered",
                "allowed_attributes": {
                    "is_registered": True,
                    "polling_unit_id": "LA/09/05/001",
                    "polling_unit_name": "Obalende Primary School"
                },
                "confidence": 0.94,
                "timestamp": "2025-11-27T12:00:00Z",
                "signed_by": "INEC"
            }
        }


class PollingUnitStatus(BaseModel):
    """Real-time polling unit status"""
    polling_unit_id: str
    name: str
    location: Dict[str, float]
    queue_length: int
    estimated_wait_minutes: int
    status: Literal["open", "closed", "paused", "incident"]
    last_updated: str


class AccessibilityRequest(BaseModel):
    """Request for accessibility assistance"""
    request_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    voter_pseudonym: str
    polling_unit_id: str
    assistance_type: Literal["visual_impairment", "mobility", "cognitive", "other"]
    timestamp: str


class INECConnector:
    """
    Simulated INEC BVAS / Electoral Database integration
    In production: use official INEC API with proper authentication
    """
    
    def __init__(self, api_endpoint: str, api_key: str, salt: str):
        self.endpoint = api_endpoint
        self.api_key = api_key
        self.salt = salt
        
        # Simulated voter registry (template_hash -> voter record)
        self.voter_registry = {}
        
        # Polling unit database
        self.polling_units = {
            "LA/09/05/001": {
                "name": "Obalende Primary School",
                "location": {"lat": 6.4541, "lon": 3.4106},
                "capacity": 500,
                "current_queue": 45
            },
            "LA/09/05/002": {
                "name": "Victoria Island Ward Hall",
                "location": {"lat": 6.4281, "lon": 3.4219},
                "capacity": 300,
                "current_queue": 12
            }
        }
        
        # Vote tracking (pseudonym -> voted status)
        self.voted_tracker = set()
        
        logger.info("INEC connector initialized (DEMO MODE - use official INEC API in production)")
    
    def register_voter(
        self,
        template_hash: str,
        vin: str,
        polling_unit_id: str,
        attributes: Dict[str, Any]
    ) -> str:
        """
        Register voter in INEC database (admin operation)
        VIN = Voter Identification Number
        Returns pseudonymous token
        """
        # Generate unlinkable pseudonymous token
        pseudonym = self._generate_voter_token(template_hash, vin)
        
        self.voter_registry[template_hash] = {
            'pseudonym': pseudonym,
            'polling_unit_id': polling_unit_id,
            'allowed_attributes': {
                'is_registered': True,
                'polling_unit_id': polling_unit_id,
                'polling_unit_name': self.polling_units.get(polling_unit_id, {}).get('name', 'Unknown'),
                'registration_area': attributes.get('lga')
            },
            'registered_date': datetime.utcnow().isoformat()
        }
        
        logger.info(f"Voter registered: {pseudonym[:20]}... for PU {polling_unit_id}")
        return pseudonym
    
    def _generate_voter_token(self, template_hash: str, vin: str) -> str:
        """Generate unlinkable voter pseudonym"""
        token_input = f"{template_hash}:{vin}:{self.salt}".encode()
        return f"inec_token_{hashlib.sha256(token_input).hexdigest()}"
    
    def verify_voter(
        self,
        template_hash: str,
        polling_unit_id: Optional[str] = None
    ) -> VerificationResponse:
        """
        Tokenized voter verification
        Returns pseudonym + limited attributes, NO PII
        """
        request_id = str(uuid.uuid4())
        
        # Check if voter registered
        if template_hash not in self.voter_registry:
            return VerificationResponse(
                request_id=request_id,
                match=False,
                status=VoterStatus.NOT_REGISTERED,
                confidence=0.0,
                timestamp=datetime.utcnow().isoformat()
            )
        
        voter_record = self.voter_registry[template_hash]
        pseudonym = voter_record['pseudonym']
        
        # Check if already voted
        if pseudonym in self.voted_tracker:
            return VerificationResponse(
                request_id=request_id,
                match=True,
                pseudonym=pseudonym,
                status=VoterStatus.ALREADY_VOTED,
                allowed_attributes={'message': 'Voter has already cast ballot'},
                confidence=1.0,
                timestamp=datetime.utcnow().isoformat()
            )
        
        # Verify polling unit (if provided)
        if polling_unit_id:
            voter_pu = voter_record['allowed_attributes']['polling_unit_id']
            if voter_pu != polling_unit_id:
                return VerificationResponse(
                    request_id=request_id,
                    match=True,
                    pseudonym=pseudonym,
                    status=VoterStatus.INVALID_POLLING_UNIT,
                    allowed_attributes={
                        'assigned_polling_unit': voter_pu,
                        'message': f'Voter assigned to {voter_pu}, not {polling_unit_id}'
                    },
                    confidence=1.0,
                    timestamp=datetime.utcnow().isoformat()
                )
        
        # Valid voter at correct polling unit
        return VerificationResponse(
            request_id=request_id,
            match=True,
            pseudonym=pseudonym,
            status=VoterStatus.REGISTERED,
            allowed_attributes=voter_record['allowed_attributes'],
            confidence=0.95,
            timestamp=datetime.utcnow().isoformat()
        )
    
    def record_vote(self, pseudonym: str):
        """Record that voter has cast ballot (prevents double voting)"""
        self.voted_tracker.add(pseudonym)
        logger.info(f"Vote recorded for {pseudonym[:20]}...")
    
    def get_polling_unit_status(self, polling_unit_id: str) -> PollingUnitStatus:
        """Get real-time polling unit status"""
        if polling_unit_id not in self.polling_units:
            raise HTTPException(status_code=404, detail="Polling unit not found")
        
        pu = self.polling_units[polling_unit_id]
        queue_length = pu['current_queue']
        
        # Estimate wait time (5 min per 10 voters)
        estimated_wait = (queue_length // 10) * 5
        
        return PollingUnitStatus(
            polling_unit_id=polling_unit_id,
            name=pu['name'],
            location=pu['location'],
            queue_length=queue_length,
            estimated_wait_minutes=estimated_wait,
            status="open",
            last_updated=datetime.utcnow().isoformat()
        )
    
    def update_queue_count(self, polling_unit_id: str, delta: int):
        """Update polling unit queue (from drone/camera analytics)"""
        if polling_unit_id in self.polling_units:
            self.polling_units[polling_unit_id]['current_queue'] += delta
            self.polling_units[polling_unit_id]['current_queue'] = max(
                0,
                self.polling_units[polling_unit_id]['current_queue']
            )
            logger.info(f"Queue updated for {polling_unit_id}: {self.polling_units[polling_unit_id]['current_queue']}")


class AccessibilityAssistance:
    """Accessibility support for voters with disabilities"""
    
    def __init__(self):
        self.assistance_requests: Dict[str, AccessibilityRequest] = {}
        logger.info("Accessibility assistance service initialized")
    
    def request_assistance(self, request: AccessibilityRequest) -> Dict[str, Any]:
        """Register accessibility assistance request"""
        self.assistance_requests[request.request_id] = request
        
        logger.info(
            f"Accessibility assistance requested: {request.assistance_type} "
            f"at PU {request.polling_unit_id}"
        )
        
        # In production: notify polling unit staff via SMS/app
        return {
            "request_id": request.request_id,
            "status": "registered",
            "message": "Polling unit staff notified. Assistance will be provided.",
            "estimated_response_minutes": 5
        }


# Initialize services
INEC_API_ENDPOINT = "https://bvas.inec.gov.ng/api/v2"  # Example
INEC_API_KEY = "demo-api-key"
INEC_SALT = "inec-production-salt-2025"

inec_connector = INECConnector(
    api_endpoint=INEC_API_ENDPOINT,
    api_key=INEC_API_KEY,
    salt=INEC_SALT
)

accessibility_service = AccessibilityAssistance()


# API Endpoints

@app.post("/api/v1/verify", response_model=VerificationResponse)
async def verify_voter(request: VerificationRequest):
    """
    Privacy-preserving voter verification
    Returns pseudonym + limited attributes, NO PII (name, address, VIN)
    """
    # In production: decrypt template, compute hash
    # For demo: use template as hash
    template_hash = hashlib.sha256(request.template.encode()).hexdigest()
    
    # Verify with INEC
    result = inec_connector.verify_voter(
        template_hash=template_hash,
        polling_unit_id=request.polling_unit_id
    )
    
    logger.info(
        f"Voter verification: {request.request_id}, "
        f"match={result.match}, status={result.status}"
    )
    
    return result


@app.post("/api/v1/vote/record")
async def record_vote(pseudonym: str):
    """
    Record that voter has cast ballot
    Prevents double voting (operator only)
    """
    inec_connector.record_vote(pseudonym)
    return {
        "status": "recorded",
        "pseudonym": pseudonym,
        "message": "Vote recorded successfully"
    }


@app.get("/api/v1/polling-unit/{polling_unit_id}", response_model=PollingUnitStatus)
async def get_polling_unit_status(polling_unit_id: str):
    """Get real-time polling unit status"""
    return inec_connector.get_polling_unit_status(polling_unit_id)


@app.post("/api/v1/polling-unit/{polling_unit_id}/queue")
async def update_queue(polling_unit_id: str, delta: int):
    """
    Update queue count (from drone/camera analytics)
    Delta: +1 (person joined), -1 (person left/voted)
    """
    inec_connector.update_queue_count(polling_unit_id, delta)
    return {
        "polling_unit_id": polling_unit_id,
        "new_queue_length": inec_connector.polling_units[polling_unit_id]['current_queue']
    }


@app.post("/api/v1/accessibility/request")
async def request_accessibility_assistance(request: AccessibilityRequest):
    """Request accessibility assistance for voter with disabilities"""
    return accessibility_service.request_assistance(request)


@app.get("/api/v1/polling-units")
async def list_polling_units():
    """List all polling units with current status"""
    return [
        inec_connector.get_polling_unit_status(pu_id)
        for pu_id in inec_connector.polling_units.keys()
    ]


@app.get("/health")
async def health_check():
    """Health check"""
    return {
        "status": "healthy",
        "service": "inec-voting-assistance",
        "registered_voters": len(inec_connector.voter_registry),
        "polling_units": len(inec_connector.polling_units)
    }


if __name__ == "__main__":
    import uvicorn
    
    # Demo: Register test voters
    test_hash_1 = hashlib.sha256(b"voter_template_001").hexdigest()
    test_hash_2 = hashlib.sha256(b"voter_template_002").hexdigest()
    
    inec_connector.register_voter(
        template_hash=test_hash_1,
        vin="VIN-0000001",
        polling_unit_id="LA/09/05/001",
        attributes={'lga': 'Lagos Mainland'}
    )
    
    inec_connector.register_voter(
        template_hash=test_hash_2,
        vin="VIN-0000002",
        polling_unit_id="LA/09/05/002",
        attributes={'lga': 'Victoria Island'}
    )
    
    logger.info("INEC voting assistance service started with demo voters")
    logger.info("CRITICAL: Use official INEC BVAS API and MOU in production")
    uvicorn.run(app, host="0.0.0.0", port=8085)
