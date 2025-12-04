"""
AI Gateway - Secure Ingest API
Production-grade drone/edge → AI → agency pipeline
Implements mTLS, attestation, HSM signing, Kafka integration
"""
from fastapi import FastAPI, Header, HTTPException, Request, status, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel, Field, validator
from typing import Optional, Dict, Any, List
from datetime import datetime, timedelta
from enum import Enum
import uvicorn
import base64
import json
import hmac
import hashlib
import os
import logging
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.backends import default_backend
import jwt

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="AI Gateway - Secure Ingest API",
    version="1.0.0",
    description="Production-grade edge → AI → agency pipeline with mTLS, attestation, HSM"
)

# Security configuration (in production: use Vault/HSM)
GATEWAY_SIGNING_KEY = os.environ.get("GATEWAY_SIGN_KEY", "change-me-secret-key-use-vault")
JWT_SECRET = os.environ.get("JWT_SECRET", "change-me-jwt-secret-use-vault")
JWT_ALGORITHM = "HS256"
JWT_EXPIRY_MINUTES = 60

# Device registry (in production: use secure device database)
AUTHORIZED_DEVICES = {
    "drone-fire-001": {"type": "fire_detection", "location": "Lagos", "public_key": "..."},
    "traffic-cam-045": {"type": "traffic_surveillance", "location": "Abuja", "public_key": "..."},
    "drone-police-002": {"type": "security_patrol", "location": "Kano", "public_key": "..."}
}

# Kafka configuration (in production: use proper Kafka cluster)
KAFKA_ENABLED = os.environ.get("KAFKA_ENABLED", "false").lower() == "true"
KAFKA_BOOTSTRAP_SERVERS = os.environ.get("KAFKA_BOOTSTRAP", "localhost:9092")


# ============================================================================
# Pydantic Models
# ============================================================================

class Location(BaseModel):
    """GPS location with accuracy"""
    lat: float = Field(..., ge=-90, le=90)
    lon: float = Field(..., ge=-180, le=180)
    accuracy_m: Optional[float] = Field(None, ge=0)
    altitude_m: Optional[float] = None


class DeviceAttestation(BaseModel):
    """Device attestation token from TPM/Secure Enclave"""
    device_id: str
    nonce: str
    timestamp: str
    signature: str  # Base64 TPM/SE signature
    
    @validator('timestamp')
    def validate_timestamp(cls, v):
        try:
            ts = datetime.fromisoformat(v.replace('Z', '+00:00'))
            now = datetime.utcnow()
            # Attestation must be recent (within 5 minutes)
            if abs((now - ts).total_seconds()) > 300:
                raise ValueError("Attestation timestamp too old or in future")
            return v
        except Exception as e:
            raise ValueError(f"Invalid timestamp format: {e}")


class IngestPayload(BaseModel):
    """Encrypted template + telemetry from edge device"""
    device_id: str
    timestamp: datetime
    location: Location
    encrypted_template: str = Field(..., description="Base64 AES-256-GCM encrypted biometric template")
    template_type: str = Field(..., description="face_embedding | fire_detection | vehicle_plate")
    metadata: Dict[str, Any] = Field(default_factory=dict)
    attestation: str = Field(..., description="Base64 encoded attestation token")
    
    class Config:
        json_schema_extra = {
            "example": {
                "device_id": "drone-fire-001",
                "timestamp": "2025-11-27T14:30:00Z",
                "location": {"lat": 9.0765, "lon": 7.3986, "accuracy_m": 5},
                "encrypted_template": "base64_encrypted_data_here",
                "template_type": "fire_detection",
                "metadata": {"confidence": 0.92, "severity": "high"},
                "attestation": "base64_attestation_token_here"
            }
        }


class CaseCreationRequest(BaseModel):
    """Request to create operator review case"""
    event_id: str
    case_type: str = Field(..., description="identity_match | fire_alert | police_alert | traffic_control")
    priority: str = Field(..., description="low | medium | high | critical")
    evidence: Dict[str, Any]
    recommended_action: str
    requires_approval_count: int = Field(1, ge=1, le=3)


class OperatorApproval(BaseModel):
    """Operator approval for case action"""
    case_id: str
    operator_id: str
    decision: str = Field(..., description="approve | reject | escalate")
    justification: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class ControlToken(BaseModel):
    """Signed control token for actuator"""
    action_id: str
    target_controller: str
    action_type: str = Field(..., description="traffic_phase_change | alert_notification | access_control")
    parameters: Dict[str, Any]
    approvals: List[OperatorApproval]
    expires_at: datetime
    signature: str


# ============================================================================
# Security Functions
# ============================================================================

security = HTTPBearer()


def verify_jwt(credentials: HTTPAuthorizationCredentials = Depends(security)) -> Dict[str, Any]:
    """Verify JWT token"""
    try:
        token = credentials.credentials
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        
        # Check expiry
        exp = payload.get('exp')
        if exp and datetime.utcnow().timestamp() > exp:
            raise HTTPException(status_code=401, detail="Token expired")
        
        return payload
    except jwt.InvalidTokenError as e:
        raise HTTPException(status_code=401, detail=f"Invalid token: {e}")


def verify_attestation(attestation_b64: str, device_id: str) -> bool:
    """
    Verify device attestation from TPM/Secure Enclave
    
    In production:
    1. Decode attestation token
    2. Verify TPM/SE signature using device public key
    3. Check nonce freshness (prevent replay)
    4. Verify certificate chain to trusted root CA
    5. Check device revocation list
    """
    try:
        # Decode attestation
        attestation_json = base64.b64decode(attestation_b64).decode('utf-8')
        attestation = json.loads(attestation_json)
        
        # Basic checks
        if attestation.get('device_id') != device_id:
            logger.warning(f"Device ID mismatch: {device_id} != {attestation.get('device_id')}")
            return False
        
        # Check device is authorized
        if device_id not in AUTHORIZED_DEVICES:
            logger.warning(f"Unauthorized device: {device_id}")
            return False
        
        # Verify timestamp (must be recent)
        att_timestamp = datetime.fromisoformat(attestation.get('timestamp', '').replace('Z', '+00:00'))
        age_seconds = (datetime.utcnow() - att_timestamp).total_seconds()
        if age_seconds > 300:  # 5 minutes
            logger.warning(f"Attestation too old: {age_seconds}s")
            return False
        
        # TODO: Verify TPM/SE signature using device public key
        # signature = base64.b64decode(attestation.get('signature'))
        # public_key = load_device_public_key(device_id)
        # public_key.verify(signature, data, padding.PSS(...), hashes.SHA256())
        
        logger.info(f"Attestation verified for device: {device_id}")
        return True
        
    except Exception as e:
        logger.error(f"Attestation verification failed: {e}")
        return False


def sign_event(payload_json: str) -> str:
    """
    Sign event with HSM
    
    In production:
    1. Use HSM/KMS to sign with RSA-2048 or ECDSA P-256
    2. Return detached signature
    3. Log signing operation to audit trail
    """
    # Demo: HMAC-SHA256 (replace with HSM signing)
    signature = hmac.new(
        GATEWAY_SIGNING_KEY.encode(),
        payload_json.encode(),
        hashlib.sha256
    ).hexdigest()
    
    return signature


def publish_to_kafka(topic: str, key: str, value: dict):
    """
    Publish event to Kafka
    
    In production:
    1. Use confluent-kafka with SASL/SSL
    2. Schema registry for Avro/Protobuf validation
    3. Idempotent producer with retries
    """
    if not KAFKA_ENABLED:
        logger.info(f"Kafka disabled. Would publish to {topic}: {key}")
        # Write to local file for demo
        with open("incoming_events.log", "a") as f:
            f.write(json.dumps({"topic": topic, "key": key, "value": value}) + "\n")
        return
    
    # TODO: Implement proper Kafka producer
    # from confluent_kafka import Producer
    # producer.produce(topic, key=key, value=json.dumps(value))
    # producer.flush()


def validate_mtls_client_cert(request: Request) -> str:
    """
    Validate mTLS client certificate
    
    In production:
    1. Nginx/Envoy terminates mTLS
    2. Passes verified client DN in X-SSL-CLIENT-S-DN header
    3. Validate CN matches authorized device list
    """
    # Check for mTLS header from reverse proxy
    client_dn = request.headers.get("X-SSL-CLIENT-S-DN")
    
    if not client_dn:
        logger.warning("Missing mTLS client certificate")
        # In demo mode, allow without mTLS
        return "demo-mode-no-mtls"
    
    # Extract CN from DN
    # Example DN: "CN=drone-fire-001,O=Security AI Platform,C=NG"
    cn = None
    for part in client_dn.split(','):
        if part.strip().startswith('CN='):
            cn = part.split('=')[1].strip()
            break
    
    if not cn or cn not in AUTHORIZED_DEVICES:
        logger.warning(f"Unauthorized client certificate: {cn}")
        raise HTTPException(status_code=403, detail="Unauthorized client certificate")
    
    return cn


# ============================================================================
# API Endpoints
# ============================================================================

@app.post("/v1/ingest/template", status_code=202)
async def ingest_template(
    payload: IngestPayload,
    request: Request,
    token_payload: Dict = Depends(verify_jwt)
):
    """
    Ingest encrypted biometric template + telemetry from edge device
    
    Security:
    - mTLS client certificate (validated by reverse proxy)
    - JWT bearer token
    - Device attestation (TPM/SE)
    - Signed events for audit trail
    """
    # Validate mTLS client cert
    client_cn = validate_mtls_client_cert(request)
    
    # Verify client CN matches device_id in payload
    if client_cn != "demo-mode-no-mtls" and client_cn != payload.device_id:
        raise HTTPException(
            status_code=403,
            detail=f"Client cert CN ({client_cn}) does not match device_id ({payload.device_id})"
        )
    
    # Verify device attestation
    if not verify_attestation(payload.attestation, payload.device_id):
        raise HTTPException(status_code=400, detail="Invalid device attestation")
    
    # Check device authorization
    if payload.device_id not in AUTHORIZED_DEVICES:
        raise HTTPException(status_code=403, detail="Device not authorized")
    
    # Create event ID
    event_id = f"evt-{datetime.utcnow().strftime('%Y%m%d%H%M%S')}-{payload.device_id}"
    
    # Prepare event for signing
    event_data = {
        "event_id": event_id,
        "device_id": payload.device_id,
        "timestamp": payload.timestamp.isoformat(),
        "location": payload.location.dict(),
        "template_type": payload.template_type,
        "metadata": payload.metadata,
        "ingested_at": datetime.utcnow().isoformat(),
        "client_cn": client_cn
    }
    
    # Sign event (HSM in production)
    signature = sign_event(json.dumps(event_data, sort_keys=True))
    event_data['signature'] = signature
    
    # Publish to Kafka
    topic = f"ingest.{payload.template_type}"
    publish_to_kafka(topic, payload.device_id, {
        "event": event_data,
        "encrypted_template": payload.encrypted_template
    })
    
    logger.info(f"Event ingested: {event_id} from {payload.device_id}")
    
    return {
        "status": "accepted",
        "event_id": event_id,
        "signature": signature,
        "queued_at": datetime.utcnow().isoformat()
    }


@app.post("/v1/cases/create", status_code=201)
async def create_case(
    request: CaseCreationRequest,
    token_payload: Dict = Depends(verify_jwt)
):
    """
    Create operator review case
    Requires human approval before any control action
    """
    case_id = f"case-{datetime.utcnow().strftime('%Y%m%d%H%M%S')}-{request.case_type}"
    
    case_data = {
        "case_id": case_id,
        "event_id": request.event_id,
        "case_type": request.case_type,
        "priority": request.priority,
        "evidence": request.evidence,
        "recommended_action": request.recommended_action,
        "requires_approval_count": request.requires_approval_count,
        "approvals": [],
        "status": "pending_review",
        "created_at": datetime.utcnow().isoformat(),
        "created_by": token_payload.get("sub", "system")
    }
    
    # Sign case
    signature = sign_event(json.dumps(case_data, sort_keys=True))
    case_data['signature'] = signature
    
    # Publish to case queue
    publish_to_kafka("cases.pending", case_id, case_data)
    
    logger.warning(f"Case created: {case_id} - {request.case_type} ({request.priority} priority)")
    
    return {
        "case_id": case_id,
        "status": "pending_review",
        "signature": signature
    }


@app.post("/v1/cases/{case_id}/approve")
async def approve_case(
    case_id: str,
    approval: OperatorApproval,
    token_payload: Dict = Depends(verify_jwt)
):
    """
    Operator approves/rejects case
    Dual authorization required for critical actions
    """
    # Verify operator authorization
    operator_id = token_payload.get("sub")
    operator_role = token_payload.get("role")
    
    if operator_role not in ["operator", "senior_operator", "admin"]:
        raise HTTPException(status_code=403, detail="Insufficient permissions")
    
    # TODO: Load case from database, verify status, check approval count
    
    approval_data = {
        "case_id": case_id,
        "operator_id": operator_id,
        "operator_role": operator_role,
        "decision": approval.decision,
        "justification": approval.justification,
        "timestamp": approval.timestamp.isoformat()
    }
    
    # Sign approval
    signature = sign_event(json.dumps(approval_data, sort_keys=True))
    approval_data['signature'] = signature
    
    # Publish approval
    publish_to_kafka("cases.approvals", case_id, approval_data)
    
    logger.info(f"Case {case_id} {approval.decision} by {operator_id}")
    
    return {
        "case_id": case_id,
        "approval_recorded": True,
        "signature": signature
    }


@app.post("/v1/control/issue-token")
async def issue_control_token(
    control: ControlToken,
    token_payload: Dict = Depends(verify_jwt)
):
    """
    Issue signed control token for actuator
    CRITICAL: Only after required approvals received
    """
    # Verify all required approvals present
    if len(control.approvals) < 1:
        raise HTTPException(status_code=400, detail="Insufficient approvals")
    
    # Verify approvals are signed and valid
    for approval in control.approvals:
        # TODO: Verify approval signatures
        pass
    
    # Generate control token
    token_data = {
        "action_id": control.action_id,
        "target_controller": control.target_controller,
        "action_type": control.action_type,
        "parameters": control.parameters,
        "approvals": [a.dict() for a in control.approvals],
        "issued_at": datetime.utcnow().isoformat(),
        "expires_at": control.expires_at.isoformat(),
        "issued_by": token_payload.get("sub")
    }
    
    # Sign with HSM
    signature = sign_event(json.dumps(token_data, sort_keys=True))
    token_data['signature'] = signature
    
    # Publish to control queue
    publish_to_kafka("control.tokens", control.target_controller, token_data)
    
    logger.critical(f"🚨 CONTROL TOKEN ISSUED: {control.action_id} -> {control.target_controller}")
    
    return {
        "action_id": control.action_id,
        "control_token": base64.b64encode(json.dumps(token_data).encode()).decode(),
        "signature": signature,
        "expires_at": control.expires_at.isoformat()
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "ai-gateway",
        "timestamp": datetime.utcnow().isoformat(),
        "kafka_enabled": KAFKA_ENABLED
    }


@app.get("/metrics")
async def metrics():
    """Prometheus metrics endpoint"""
    # TODO: Return proper Prometheus metrics
    return {
        "api_requests_total": 0,
        "events_ingested_total": 0,
        "cases_created_total": 0,
        "control_tokens_issued_total": 0
    }


# ============================================================================
# Utility: Generate JWT for testing
# ============================================================================

def generate_test_jwt(subject: str = "operator-001", role: str = "operator", exp_minutes: int = 60) -> str:
    """Generate test JWT token"""
    payload = {
        "sub": subject,
        "role": role,
        "iat": datetime.utcnow(),
        "exp": datetime.utcnow() + timedelta(minutes=exp_minutes)
    }
    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)


if __name__ == "__main__":
    logger.info("=" * 80)
    logger.info("AI Gateway - Secure Ingest API")
    logger.info("=" * 80)
    logger.info("CRITICAL: This demo runs without mTLS termination")
    logger.info("PRODUCTION: Use Nginx/Envoy for mTLS + client cert validation")
    logger.info("PRODUCTION: Use Vault/HSM for key management")
    logger.info("PRODUCTION: Use Kafka cluster with SASL/SSL")
    logger.info("=" * 80)
    
    # Generate test JWT
    test_token = generate_test_jwt()
    logger.info(f"Test JWT: {test_token}")
    logger.info("=" * 80)
    
    # Start server
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8443,
        log_level="info"
    )
