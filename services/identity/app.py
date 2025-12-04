"""
Privacy-Preserving Identity Matching Service
Tokenized matching with NIMC integration, secure enclave support
"""
from fastapi import FastAPI, HTTPException, Depends, Header
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
import hashlib
import hmac
import json
import time
from datetime import datetime
from enum import Enum
import numpy as np
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives import hashes, serialization
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Privacy-Preserving Identity Service", version="1.0.0")
security = HTTPBearer()


class MatchMode(str, Enum):
    """Identity matching modes"""
    TOKENIZED = "tokenized"  # Return pseudonymous token only
    ENCLAVE = "enclave"      # Server-side secure enclave matching
    FEDERATED = "federated"  # Query NIMC without transferring template


class MatchRequest(BaseModel):
    """Request for identity matching"""
    device_id: str = Field(..., description="Attested device identifier")
    timestamp: str = Field(..., description="ISO 8601 timestamp")
    location: Dict[str, float] = Field(..., description="GPS coordinates")
    template: str = Field(..., description="Encrypted biometric template (base64)")
    signature: str = Field(..., description="Device signature (hex)")
    metadata: Dict[str, Any] = Field(default_factory=dict)
    mode: MatchMode = Field(default=MatchMode.TOKENIZED)


class MatchResult(BaseModel):
    """Privacy-preserving match result"""
    match: bool
    pseudonym: Optional[str] = None  # Unlinkable token, not real ID
    confidence: float
    allowed_attributes: Dict[str, Any] = Field(default_factory=dict)
    timestamp: str
    mode: MatchMode


class NIMCConnector:
    """
    Simulated NIMC (Nigerian Identity Management Commission) integration
    In production: use official NIMC API with proper authentication
    """
    
    def __init__(self, api_endpoint: str, api_key: str, salt: str):
        self.endpoint = api_endpoint
        self.api_key = api_key
        self.salt = salt
        
        # Simulated enrolled database (hash -> pseudonym mapping)
        # In production: NIMC maintains this securely
        self.enrolled_db = {}
        
        logger.info("NIMC connector initialized (DEMO MODE)")
    
    def register_identity(self, template_hash: str, nin: str, attributes: Dict[str, Any]):
        """
        Register identity with NIMC (admin operation)
        Stores hash -> pseudonymous token mapping, not raw NIN
        """
        # Generate pseudonymous token (one-way, unlinkable)
        pseudonym = self._generate_pseudonym(template_hash, nin)
        
        # Store minimal attributes (NOT full PII)
        self.enrolled_db[template_hash] = {
            'pseudonym': pseudonym,
            'allowed_attributes': {
                'age_group': attributes.get('age_group'),
                'state': attributes.get('state'),
                'voter_status': attributes.get('voter_status', 'unknown')
            },
            'enrolled_date': datetime.utcnow().isoformat()
        }
        
        logger.info(f"Identity registered: {pseudonym[:16]}... (template hash)")
        return pseudonym
    
    def _generate_pseudonym(self, template_hash: str, nin: str) -> str:
        """Generate unlinkable pseudonymous token"""
        token_input = f"{template_hash}:{nin}:{self.salt}".encode()
        return f"nimc_token_{hashlib.sha256(token_input).hexdigest()}"
    
    def match_tokenized(self, template_hash: str) -> Optional[MatchResult]:
        """
        Tokenized matching: return pseudonym if match exists
        NO PII is exposed in response
        """
        if template_hash in self.enrolled_db:
            record = self.enrolled_db[template_hash]
            return MatchResult(
                match=True,
                pseudonym=record['pseudonym'],
                confidence=0.95,  # Exact hash match
                allowed_attributes=record['allowed_attributes'],
                timestamp=datetime.utcnow().isoformat(),
                mode=MatchMode.TOKENIZED
            )
        
        return MatchResult(
            match=False,
            confidence=0.0,
            timestamp=datetime.utcnow().isoformat(),
            mode=MatchMode.TOKENIZED
        )
    
    def match_enclave(self, embedding: np.ndarray, threshold: float = 0.85) -> Optional[MatchResult]:
        """
        Secure enclave matching: compute similarity inside trusted environment
        Only match decision leaves the enclave, not embeddings
        """
        # Simulated enclave - in production: use Intel SGX, ARM TrustZone, or AWS Nitro
        logger.info("Computing match inside secure enclave...")
        
        # Compare embedding to enrolled templates (inside enclave)
        # For demo, we simulate by checking template hash
        template_hash = hashlib.sha256(embedding.tobytes()).hexdigest()
        
        return self.match_tokenized(template_hash)
    
    def match_federated(self, encrypted_query: bytes) -> Optional[MatchResult]:
        """
        Federated matching: NIMC runs matching locally
        Client sends encrypted query, NIMC returns signed result
        """
        # Decrypt query inside NIMC's secure environment
        # Run matching against NIMC database
        # Return only match decision + token
        
        logger.info("Federated match: NIMC processing query locally")
        # Simulated - would involve actual cryptographic protocol
        return MatchResult(
            match=False,
            confidence=0.0,
            timestamp=datetime.utcnow().isoformat(),
            mode=MatchMode.FEDERATED
        )


class IdentityService:
    """Main identity matching service"""
    
    def __init__(self, nimc_connector: NIMCConnector, decryption_key: bytes):
        self.nimc = nimc_connector
        self.decryption_key = decryption_key
        self.fernet = Fernet(decryption_key)
        
        # Device attestation registry (public keys)
        self.registered_devices: Dict[str, bytes] = {}
    
    def verify_device_signature(self, device_id: str, data: bytes, signature: bytes) -> bool:
        """Verify device attestation signature"""
        if device_id not in self.registered_devices:
            logger.warning(f"Unknown device: {device_id}")
            return False
        
        public_key_pem = self.registered_devices[device_id]
        public_key = serialization.load_pem_public_key(public_key_pem)
        
        try:
            public_key.verify(
                signature,
                data,
                padding.PSS(
                    mgf=padding.MGF1(hashes.SHA256()),
                    salt_length=padding.PSS.MAX_LENGTH
                ),
                hashes.SHA256()
            )
            return True
        except Exception as e:
            logger.error(f"Signature verification failed: {e}")
            return False
    
    def decrypt_template(self, encrypted_template: str) -> Dict[str, Any]:
        """Decrypt biometric template"""
        try:
            decrypted = self.fernet.decrypt(encrypted_template.encode())
            return json.loads(decrypted)
        except Exception as e:
            logger.error(f"Template decryption failed: {e}")
            raise HTTPException(status_code=400, detail="Invalid template encryption")
    
    def process_match_request(self, request: MatchRequest) -> MatchResult:
        """
        Process identity match request with privacy guarantees
        """
        # Step 1: Verify device signature
        signature_bytes = bytes.fromhex(request.signature)
        template_bytes = request.template.encode()
        
        if not self.verify_device_signature(request.device_id, template_bytes, signature_bytes):
            raise HTTPException(status_code=403, detail="Device signature verification failed")
        
        # Step 2: Decrypt template
        template_data = self.decrypt_template(request.template)
        
        # Step 3: Route to appropriate matching mode
        if request.mode == MatchMode.TOKENIZED:
            template_hash = template_data['template_hash']
            result = self.nimc.match_tokenized(template_hash)
        
        elif request.mode == MatchMode.ENCLAVE:
            embedding = np.array(template_data['embedding'])
            result = self.nimc.match_enclave(embedding)
        
        elif request.mode == MatchMode.FEDERATED:
            # Would send encrypted query to NIMC
            result = self.nimc.match_federated(template_bytes)
        
        else:
            raise HTTPException(status_code=400, detail="Invalid match mode")
        
        logger.info(
            f"Match processed: device={request.device_id}, "
            f"match={result.match}, confidence={result.confidence}"
        )
        
        return result
    
    def register_device(self, device_id: str, public_key_pem: bytes):
        """Register device for attestation"""
        self.registered_devices[device_id] = public_key_pem
        logger.info(f"Device registered: {device_id}")


# Initialize services
ENCRYPTION_KEY = Fernet.generate_key()
NIMC_SALT = "nimc-production-salt-2025"  # In production: use HSM-protected secret

nimc_connector = NIMCConnector(
    api_endpoint="https://api.nimc.gov.ng/v2/identity",
    api_key="demo-api-key",
    salt=NIMC_SALT
)

identity_service = IdentityService(
    nimc_connector=nimc_connector,
    decryption_key=ENCRYPTION_KEY
)


# API Endpoints

@app.post("/api/v1/match", response_model=MatchResult)
async def match_identity(
    request: MatchRequest,
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    """
    Privacy-preserving identity matching endpoint
    Requires JWT authentication and device attestation
    """
    # Verify JWT (in production)
    # token = credentials.credentials
    # verify_jwt(token)
    
    try:
        result = identity_service.process_match_request(request)
        return result
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Match error: {e}")
        raise HTTPException(status_code=500, detail="Internal matching error")


@app.post("/api/v1/register-device")
async def register_device(
    device_id: str,
    public_key_pem: str,
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    """Register edge device for attestation (admin only)"""
    # Verify admin JWT
    identity_service.register_device(device_id, public_key_pem.encode())
    return {"status": "registered", "device_id": device_id}


@app.post("/api/v1/enroll")
async def enroll_identity(
    template_hash: str,
    nin: str,
    attributes: Dict[str, Any],
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    """
    Enroll identity with NIMC (admin only, requires authorization)
    Stores minimal attributes, NOT full PII
    """
    # Verify admin JWT + legal authorization
    pseudonym = nimc_connector.register_identity(template_hash, nin, attributes)
    return {
        "status": "enrolled",
        "pseudonym": pseudonym,
        "note": "PII is NOT stored in system, only pseudonymous tokens"
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "identity-matching",
        "mode": "privacy-preserving",
        "timestamp": datetime.utcnow().isoformat()
    }


if __name__ == "__main__":
    import uvicorn
    
    # Demo: Register a test identity
    test_hash = hashlib.sha256(b"test_template_001").hexdigest()
    nimc_connector.register_identity(
        template_hash=test_hash,
        nin="12345678901",  # Simulated NIN
        attributes={
            'age_group': '25-34',
            'state': 'Lagos',
            'voter_status': 'registered'
        }
    )
    
    logger.info("Identity service started with demo enrollment")
    uvicorn.run(app, host="0.0.0.0", port=8081)
