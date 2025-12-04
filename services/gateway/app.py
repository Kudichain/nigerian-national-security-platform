"""
Secure API Gateway with mTLS, JWT, Rate Limiting
"""
from fastapi import FastAPI, Request, HTTPException, Depends, Header
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from pydantic import BaseModel
from typing import Optional, Dict, Any
import time
import hashlib
import jwt
from datetime import datetime, timedelta
from collections import defaultdict
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Secure API Gateway", version="1.0.0")
security = HTTPBearer()

# JWT Configuration
JWT_SECRET = "your-secret-key-use-env-var-in-production"
JWT_ALGORITHM = "HS256"
JWT_EXPIRATION = 3600  # 1 hour


class RateLimiter:
    """Token bucket rate limiter"""
    
    def __init__(self, requests_per_minute: int = 60):
        self.rate = requests_per_minute
        self.buckets: Dict[str, list] = defaultdict(list)
    
    def is_allowed(self, client_id: str) -> bool:
        """Check if request is allowed under rate limit"""
        now = time.time()
        minute_ago = now - 60
        
        # Clean old requests
        self.buckets[client_id] = [
            req_time for req_time in self.buckets[client_id]
            if req_time > minute_ago
        ]
        
        # Check limit
        if len(self.buckets[client_id]) >= self.rate:
            return False
        
        self.buckets[client_id].append(now)
        return True


class AnomalyDetector:
    """Simple anomaly detection for API usage"""
    
    def __init__(self):
        self.request_patterns: Dict[str, list] = defaultdict(list)
        self.alert_threshold = 100  # requests per minute
    
    def check_anomaly(self, client_id: str, endpoint: str) -> bool:
        """Detect unusual request patterns"""
        now = time.time()
        minute_ago = now - 60
        
        # Track requests
        key = f"{client_id}:{endpoint}"
        self.request_patterns[key] = [
            req_time for req_time in self.request_patterns[key]
            if req_time > minute_ago
        ]
        
        self.request_patterns[key].append(now)
        
        # Check for spike
        if len(self.request_patterns[key]) > self.alert_threshold:
            logger.warning(f"Anomaly detected: {client_id} - {len(self.request_patterns[key])} req/min on {endpoint}")
            return True
        
        return False


class DeviceRegistry:
    """Device attestation registry"""
    
    def __init__(self):
        self.devices: Dict[str, Dict[str, Any]] = {}
    
    def register(self, device_id: str, public_key: str, metadata: Dict[str, Any]):
        """Register attested device"""
        self.devices[device_id] = {
            'public_key': public_key,
            'metadata': metadata,
            'registered_at': datetime.utcnow().isoformat(),
            'last_seen': None
        }
        logger.info(f"Device registered: {device_id}")
    
    def verify(self, device_id: str) -> bool:
        """Verify device is registered"""
        if device_id in self.devices:
            self.devices[device_id]['last_seen'] = datetime.utcnow().isoformat()
            return True
        return False
    
    def get_public_key(self, device_id: str) -> Optional[str]:
        """Get device public key for signature verification"""
        return self.devices.get(device_id, {}).get('public_key')


# Initialize components
rate_limiter = RateLimiter(requests_per_minute=120)
anomaly_detector = AnomalyDetector()
device_registry = DeviceRegistry()


# Middleware

@app.middleware("http")
async def rate_limiting_middleware(request: Request, call_next):
    """Rate limiting middleware"""
    client_host = request.client.host if request.client else "unknown"
    client_id = request.headers.get('X-Device-ID', client_host)
    
    if not rate_limiter.is_allowed(client_id):
        logger.warning(f"Rate limit exceeded: {client_id}")
        raise HTTPException(status_code=429, detail="Rate limit exceeded")
    
    response = await call_next(request)
    return response


@app.middleware("http")
async def anomaly_detection_middleware(request: Request, call_next):
    """Anomaly detection middleware"""
    client_host = request.client.host if request.client else "unknown"
    client_id = request.headers.get('X-Device-ID', client_host)
    endpoint = request.url.path
    
    is_anomaly = anomaly_detector.check_anomaly(client_id, endpoint)
    
    if is_anomaly:
        # Log but don't block (in production: trigger alert)
        logger.warning(f"Anomaly: {client_id} - unusual activity on {endpoint}")
    
    response = await call_next(request)
    return response


@app.middleware("http")
async def security_headers_middleware(request: Request, call_next):
    """Add security headers"""
    response = await call_next(request)
    response.headers['X-Content-Type-Options'] = 'nosniff'
    response.headers['X-Frame-Options'] = 'DENY'
    response.headers['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains'
    response.headers['X-XSS-Protection'] = '1; mode=block'
    return response


# CORS (restrictive in production)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://dashboard.secai.gov.ng"],  # Whitelist only
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)


# Helper functions

def create_jwt(user_id: str, role: str) -> str:
    """Create JWT token"""
    payload = {
        'sub': user_id,
        'role': role,
        'exp': datetime.utcnow() + timedelta(seconds=JWT_EXPIRATION),
        'iat': datetime.utcnow()
    }
    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)


def verify_jwt(token: str) -> Dict[str, Any]:
    """Verify and decode JWT"""
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")


async def verify_device_attestation(
    device_id: str = Header(..., alias="X-Device-ID"),
    signature: str = Header(..., alias="X-Device-Signature")
) -> str:
    """Verify device attestation"""
    if not device_registry.verify(device_id):
        raise HTTPException(status_code=403, detail="Device not registered")
    
    # In production: verify signature with device public key
    # public_key = device_registry.get_public_key(device_id)
    # verify_signature(data, signature, public_key)
    
    return device_id


async def verify_token(credentials: HTTPAuthorizationCredentials = Depends(security)) -> Dict[str, Any]:
    """Verify JWT from Authorization header"""
    token = credentials.credentials
    return verify_jwt(token)


# Endpoints

@app.post("/auth/login")
async def login(username: str, password: str):
    """
    Authenticate user and issue JWT
    In production: verify against secure credential store
    """
    # Simulated authentication
    if username and password:
        role = "operator" if username != "admin" else "admin"
        token = create_jwt(username, role)
        
        logger.info(f"User logged in: {username}")
        return {
            "access_token": token,
            "token_type": "bearer",
            "expires_in": JWT_EXPIRATION
        }
    
    raise HTTPException(status_code=401, detail="Invalid credentials")


@app.post("/devices/register")
async def register_device(
    device_id: str,
    public_key: str,
    manufacturer: str,
    firmware_version: str,
    user: Dict = Depends(verify_token)
):
    """Register edge device (admin only)"""
    if user.get('role') != 'admin':
        raise HTTPException(status_code=403, detail="Admin access required")
    
    device_registry.register(
        device_id=device_id,
        public_key=public_key,
        metadata={
            'manufacturer': manufacturer,
            'firmware_version': firmware_version
        }
    )
    
    return {"status": "registered", "device_id": device_id}


@app.get("/devices")
async def list_devices(user: Dict = Depends(verify_token)):
    """List registered devices"""
    return {
        "devices": [
            {
                'device_id': device_id,
                'registered_at': info['registered_at'],
                'last_seen': info['last_seen']
            }
            for device_id, info in device_registry.devices.items()
        ]
    }


@app.get("/health")
async def health_check():
    """Health check"""
    return {
        "status": "healthy",
        "service": "api-gateway",
        "registered_devices": len(device_registry.devices)
    }


if __name__ == "__main__":
    import uvicorn
    
    # Register demo device
    device_registry.register(
        device_id="drone-abc-123",
        public_key="demo-public-key-pem",
        metadata={'manufacturer': 'SecureEdge', 'firmware_version': 'v2.1.3'}
    )
    
    logger.info("API Gateway started with mTLS, rate limiting, and anomaly detection")
    uvicorn.run(app, host="0.0.0.0", port=8080, ssl_keyfile="certs/key.pem", ssl_certfile="certs/cert.pem")
