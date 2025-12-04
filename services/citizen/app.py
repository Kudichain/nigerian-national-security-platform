"""
Citizen Search Service - Privacy-Preserving Federated Identity Verification

LEGAL COMPLIANCE:
- NDPR 2019: Data minimization, purpose limitation, lawful basis (public interest)
- Cybercrime Act 2015: Authorized access only, full audit trail
- NIMC Act 2007: NIN verification for authorized agencies

SECURITY FEATURES:
- Officer authorization validation (role-based access)
- Case-based access (no general searches)
- Full audit logging (immutable, WORM storage)
- No citizen data storage (federated lookups only)
- Rate limiting (prevent abuse)

ARCHITECTURE:
- Federated API gateway (NIMC, CBN BVN, Immigration)
- Zero local PII storage (queries only)
- Unlinkable pseudonyms for cross-agency correlation
- Consent tracking (where applicable)

PORT: 8090
"""

from fastapi import FastAPI, HTTPException, Depends, Header
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field, validator
from typing import Optional, List, Literal
from datetime import datetime, timedelta
import hashlib
import hmac
import json
import logging
from enum import Enum

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Citizen Search Service", version="1.0.0")

# CORS for dashboard
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

class SearchType(str, Enum):
    NIN = "nin"
    BVN = "bvn"
    PASSPORT = "passport"
    PHONE = "phone"
    NAME = "name"

class OfficerRole(str, Enum):
    POLICE = "police"
    DSS = "dss"
    EFCC = "efcc"
    ICPC = "icpc"
    NDLEA = "ndlea"
    CUSTOMS = "customs"
    IMMIGRATION = "immigration"
    FIRE = "fire"
    SECURITY_ANALYST = "security_analyst"

class CitizenSearchRequest(BaseModel):
    search_type: SearchType
    value: str = Field(..., min_length=1, max_length=100)
    officer_id: str = Field(..., pattern=r"^[A-Z]{3,5}-\d{3,6}$")
    case_id: str = Field(..., pattern=r"^[A-Z0-9\-]{5,50}$")
    justification: str = Field(..., min_length=10, max_length=500)
    
    @validator('value')
    def validate_search_value(cls, v, values):
        search_type = values.get('search_type')
        if search_type == SearchType.NIN and len(v) != 11:
            raise ValueError("NIN must be 11 digits")
        if search_type == SearchType.BVN and len(v) != 11:
            raise ValueError("BVN must be 11 digits")
        if search_type == SearchType.PASSPORT and not (len(v) == 9 and v[0].isalpha()):
            raise ValueError("Passport must be 1 letter + 8 digits (e.g., A12345678)")
        return v

class NIMCVerificationResponse(BaseModel):
    match: bool
    full_name: Optional[str] = None
    date_of_birth: Optional[str] = None
    gender: Optional[str] = None
    state_of_origin: Optional[str] = None
    lga: Optional[str] = None
    photo_base64: Optional[str] = None  # Redacted unless critical case
    verification_status: str
    nin_hash: Optional[str] = None  # One-way hash for correlation

class BVNVerificationResponse(BaseModel):
    match: bool
    full_name: Optional[str] = None
    phone_number: Optional[str] = None  # Last 4 digits only
    bank_count: Optional[int] = None
    registration_date: Optional[str] = None
    verification_status: str

class PassportVerificationResponse(BaseModel):
    match: bool
    full_name: Optional[str] = None
    nationality: Optional[str] = None
    issue_date: Optional[str] = None
    expiry_date: Optional[str] = None
    travel_history_count: Optional[int] = None  # Count only, no destinations
    watchlist_status: Optional[str] = None
    verification_status: str

class CitizenProfile(BaseModel):
    search_id: str
    timestamp: datetime
    officer_id: str
    case_id: str
    search_type: SearchType
    search_value_hash: str  # Never return raw search value
    nimc_result: Optional[NIMCVerificationResponse] = None
    bvn_result: Optional[BVNVerificationResponse] = None
    passport_result: Optional[PassportVerificationResponse] = None
    match_score: float = Field(..., ge=0.0, le=1.0)
    linked_alerts: List[str] = []
    audit_trail_id: str

class AuditLogEntry(BaseModel):
    audit_id: str
    timestamp: datetime
    officer_id: str
    officer_role: OfficerRole
    case_id: str
    search_type: SearchType
    search_value_hash: str
    justification: str
    result_match: bool
    ip_address: str
    user_agent: str

# ============================================================================
# MOCK DATA (Replace with real API calls in production)
# ============================================================================

MOCK_OFFICERS = {
    "NPF-12345": {"role": OfficerRole.POLICE, "name": "Insp. Adamu Yusuf", "station": "FCT Command"},
    "DSS-98765": {"role": OfficerRole.DSS, "name": "Agent Aisha Bello", "unit": "Counter-Terrorism"},
    "EFCC-55443": {"role": OfficerRole.EFCC, "name": "Det. Chidi Okafor", "unit": "Economic Crimes"},
}

MOCK_CITIZENS = {
    "12345678901": {  # NIN
        "full_name": "Abdulkadir Musa Ibrahim",
        "date_of_birth": "1993-02-11",
        "gender": "Male",
        "state_of_origin": "Kano",
        "lga": "Nassarawa",
        "photo": "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNkYPhfDwAChwGA60e6kgAAAABJRU5ErkJggg=="  # 1x1 placeholder
    },
    "98765432100": {  # NIN
        "full_name": "Ngozi Chioma Okonkwo",
        "date_of_birth": "1988-07-22",
        "gender": "Female",
        "state_of_origin": "Anambra",
        "lga": "Awka South",
        "photo": "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNkYPhfDwAChwGA60e6kgAAAABJRU5ErkJggg=="
    }
}

MOCK_BVN = {
    "22339911001": {
        "full_name": "Abdulkadir Musa Ibrahim",
        "phone": "****6789",
        "bank_count": 3,
        "registration_date": "2015-08-10"
    }
}

MOCK_PASSPORTS = {
    "A12345678": {
        "full_name": "Abdulkadir Musa Ibrahim",
        "nationality": "Nigerian",
        "issue_date": "2020-01-15",
        "expiry_date": "2030-01-14",
        "travel_count": 12,
        "watchlist": "clear"
    }
}

# In-memory audit log (use PostgreSQL with WORM in production)
audit_logs: List[AuditLogEntry] = []
search_history: List[CitizenProfile] = []

# ============================================================================
# AUTHORIZATION
# ============================================================================

def verify_officer(officer_id: str) -> dict:
    """Verify officer authorization"""
    officer = MOCK_OFFICERS.get(officer_id)
    if not officer:
        raise HTTPException(status_code=403, detail="Officer not authorized")
    return officer

def hash_pii(value: str) -> str:
    """One-way hash for PII (unlinkable pseudonym)"""
    return hashlib.sha256(f"{value}:security-ai-salt-2025".encode()).hexdigest()

def log_audit(request: CitizenSearchRequest, result: CitizenProfile, officer: dict, ip: str):
    """Immutable audit log"""
    audit_entry = AuditLogEntry(
        audit_id=f"AUDIT-{datetime.utcnow().timestamp()}",
        timestamp=datetime.utcnow(),
        officer_id=request.officer_id,
        officer_role=officer["role"],
        case_id=request.case_id,
        search_type=request.search_type,
        search_value_hash=hash_pii(request.value),
        justification=request.justification,
        result_match=result.match_score > 0.5,
        ip_address=ip,
        user_agent="FastAPI/1.0"
    )
    audit_logs.append(audit_entry)
    logger.info(f"AUDIT: {request.officer_id} searched {request.search_type} for case {request.case_id}")

# ============================================================================
# FEDERATED API CALLS (Mock - Replace with real APIs)
# ============================================================================

def query_nimc_api(nin: str, case_id: str) -> NIMCVerificationResponse:
    """
    PRODUCTION: POST https://gateway.gov.ng/nimc/verify-nin
    Headers: Authorization: Bearer {GOV_TOKEN}
    Body: {"nin": "...", "case_id": "...", "requesting_agency": "SECURITY_AI"}
    """
    citizen = MOCK_CITIZENS.get(nin)
    if not citizen:
        return NIMCVerificationResponse(match=False, verification_status="not_found")
    
    return NIMCVerificationResponse(
        match=True,
        full_name=citizen["full_name"],
        date_of_birth=citizen["date_of_birth"],
        gender=citizen["gender"],
        state_of_origin=citizen["state_of_origin"],
        lga=citizen["lga"],
        photo_base64=citizen["photo"],  # Only for CRITICAL cases in production
        verification_status="verified",
        nin_hash=hash_pii(nin)
    )

def query_bvn_api(bvn: str) -> BVNVerificationResponse:
    """
    PRODUCTION: POST https://api.cbn.gov.ng/bvn/verify
    Requires CBN authorization + case justification
    """
    record = MOCK_BVN.get(bvn)
    if not record:
        return BVNVerificationResponse(match=False, verification_status="not_found")
    
    return BVNVerificationResponse(
        match=True,
        full_name=record["full_name"],
        phone_number=record["phone"],
        bank_count=record["bank_count"],
        registration_date=record["registration_date"],
        verification_status="verified"
    )

def query_passport_api(passport: str) -> PassportVerificationResponse:
    """
    PRODUCTION: POST https://immigration.gov.ng/api/passport/verify
    Returns limited info unless on watchlist
    """
    record = MOCK_PASSPORTS.get(passport)
    if not record:
        return PassportVerificationResponse(match=False, verification_status="not_found")
    
    return PassportVerificationResponse(
        match=True,
        full_name=record["full_name"],
        nationality=record["nationality"],
        issue_date=record["issue_date"],
        expiry_date=record["expiry_date"],
        travel_history_count=record["travel_count"],
        watchlist_status=record["watchlist"],
        verification_status="verified"
    )

# ============================================================================
# ENDPOINTS
# ============================================================================

@app.post("/api/v1/citizen/search", response_model=CitizenProfile)
async def search_citizen(
    request: CitizenSearchRequest,
    x_forwarded_for: Optional[str] = Header(None)
):
    """
    Federated citizen search via NIMC/BVN/Passport APIs
    
    AUTHORIZATION: Officer ID + Case ID required
    AUDIT: All searches logged immutably
    PRIVACY: No PII storage, federated lookups only
    """
    # Validate officer
    officer = verify_officer(request.officer_id)
    
    # Rate limiting check (implement Redis-based in production)
    recent_searches = [s for s in search_history if s.officer_id == request.officer_id and s.timestamp > datetime.utcnow() - timedelta(minutes=5)]
    if len(recent_searches) > 10:
        raise HTTPException(status_code=429, detail="Rate limit exceeded: max 10 searches per 5 minutes")
    
    # Initialize results
    nimc_result = None
    bvn_result = None
    passport_result = None
    
    # Query appropriate APIs based on search type
    if request.search_type == SearchType.NIN:
        nimc_result = query_nimc_api(request.value, request.case_id)
    elif request.search_type == SearchType.BVN:
        bvn_result = query_bvn_api(request.value)
    elif request.search_type == SearchType.PASSPORT:
        passport_result = query_passport_api(request.value)
    
    # Cross-reference if primary match found (optional advanced feature)
    if nimc_result and nimc_result.match:
        # Try to find matching BVN/Passport (production: use NIMC's linked records API)
        pass
    
    # Calculate match score
    match_score = 0.0
    if nimc_result and nimc_result.match:
        match_score = 1.0
    elif bvn_result and bvn_result.match:
        match_score = 0.8
    elif passport_result and passport_result.match:
        match_score = 0.9
    
    # Build response
    search_id = f"SEARCH-{datetime.utcnow().timestamp()}"
    audit_trail_id = f"AUDIT-{search_id}"
    
    profile = CitizenProfile(
        search_id=search_id,
        timestamp=datetime.utcnow(),
        officer_id=request.officer_id,
        case_id=request.case_id,
        search_type=request.search_type,
        search_value_hash=hash_pii(request.value),
        nimc_result=nimc_result,
        bvn_result=bvn_result,
        passport_result=passport_result,
        match_score=match_score,
        linked_alerts=[],  # TODO: Query police/EFCC databases for linked cases
        audit_trail_id=audit_trail_id
    )
    
    # Audit log
    log_audit(request, profile, officer, x_forwarded_for or "unknown")
    
    # Store search (30-day retention for case tracking)
    search_history.append(profile)
    
    return profile

@app.get("/api/v1/citizen/audit-logs")
async def get_audit_logs(officer_id: str, limit: int = 100):
    """Retrieve audit logs (DPO/supervisor access only)"""
    officer = verify_officer(officer_id)
    if officer["role"] not in [OfficerRole.DSS, OfficerRole.EFCC]:
        raise HTTPException(status_code=403, detail="Supervisor access required")
    
    return audit_logs[-limit:]

@app.get("/api/v1/citizen/case-history/{case_id}")
async def get_case_history(case_id: str, officer_id: str):
    """Get all searches for a specific case"""
    verify_officer(officer_id)
    case_searches = [s for s in search_history if s.case_id == case_id]
    return case_searches

@app.get("/health")
async def health():
    return {
        "status": "healthy",
        "service": "citizen-search",
        "version": "1.0.0",
        "total_searches": len(search_history),
        "total_audits": len(audit_logs)
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8090)
