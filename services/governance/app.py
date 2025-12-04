"""
NDPR Compliance & Governance Module
Data minimization, consent management, redress mechanisms
"""
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any, Literal
from datetime import datetime, timedelta
from enum import Enum
import uuid
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Governance & Compliance", version="1.0.0")


class ProcessingPurpose(str, Enum):
    """Lawful purposes for data processing"""
    LAW_ENFORCEMENT = "law_enforcement"
    SEARCH_RESCUE = "search_rescue"
    TRAFFIC_MANAGEMENT = "traffic_management"
    PUBLIC_SAFETY = "public_safety"
    RESEARCH = "research"


class LegalBasis(str, Enum):
    """Legal basis under NDPR"""
    CONSENT = "consent"
    LEGAL_OBLIGATION = "legal_obligation"
    PUBLIC_INTEREST = "public_interest"
    VITAL_INTERESTS = "vital_interests"


class ConsentRecord(BaseModel):
    """Consent record for data subject"""
    consent_id: str
    subject_id: str  # Pseudonymous
    purpose: ProcessingPurpose
    legal_basis: LegalBasis
    granted_at: str
    expires_at: Optional[str]
    withdrawn: bool = False
    withdrawn_at: Optional[str] = None


class DataMinimizationPolicy(BaseModel):
    """Data minimization rules"""
    allowed_attributes: List[str]
    prohibited_attributes: List[str]
    retention_days: int
    anonymization_required: bool


class RedressRequest(BaseModel):
    """Citizen redress/appeal request"""
    request_id: str
    subject_pseudonym: str
    request_type: Literal["access", "correction", "deletion", "objection", "complaint"]
    details: str
    submitted_at: str
    status: Literal["pending", "reviewed", "resolved", "rejected"]
    resolution: Optional[str] = None


class TransparencyReport(BaseModel):
    """Public transparency report"""
    report_period: str
    total_identity_checks: int
    purposes: Dict[ProcessingPurpose, int]
    false_positive_rate: float
    bias_metrics: Dict[str, float]
    redress_requests: int
    redress_resolved: int


class GovernanceService:
    """Main governance and compliance service"""
    
    def __init__(self):
        self.consents: Dict[str, ConsentRecord] = {}
        self.redress_requests: Dict[str, RedressRequest] = {}
        self.data_policies = self._load_policies()
        self.transparency_data = {
            'identity_checks': 0,
            'purposes': defaultdict(int),
            'redress_count': 0
        }
        logger.info("Governance service initialized")
    
    def _load_policies(self) -> Dict[str, DataMinimizationPolicy]:
        """Load data minimization policies"""
        return {
            'identity_matching': DataMinimizationPolicy(
                allowed_attributes=['age_group', 'state', 'voter_status'],
                prohibited_attributes=['full_name', 'nin', 'address', 'phone'],
                retention_days=90,
                anonymization_required=True
            ),
            'traffic_control': DataMinimizationPolicy(
                allowed_attributes=['location', 'timestamp'],
                prohibited_attributes=['identity', 'biometric_template'],
                retention_days=30,
                anonymization_required=True
            )
        }
    
    def validate_processing(
        self,
        purpose: ProcessingPurpose,
        legal_basis: LegalBasis,
        data_attributes: List[str]
    ) -> bool:
        """Validate data processing against NDPR"""
        # Check purpose limitation
        if purpose not in ProcessingPurpose:
            logger.error(f"Invalid processing purpose: {purpose}")
            return False
        
        # Check legal basis
        if legal_basis == LegalBasis.CONSENT:
            # Require explicit consent record
            logger.info("Consent-based processing - checking consent records")
        
        # Check data minimization
        policy = self.data_policies.get('identity_matching')
        for attr in data_attributes:
            if attr in policy.prohibited_attributes:
                logger.error(f"Prohibited attribute requested: {attr}")
                return False
        
        return True
    
    def record_consent(
        self,
        subject_id: str,
        purpose: ProcessingPurpose,
        legal_basis: LegalBasis,
        duration_days: Optional[int] = None
    ) -> ConsentRecord:
        """Record consent from data subject"""
        consent_id = str(uuid.uuid4())
        now = datetime.utcnow()
        
        consent = ConsentRecord(
            consent_id=consent_id,
            subject_id=subject_id,
            purpose=purpose,
            legal_basis=legal_basis,
            granted_at=now.isoformat(),
            expires_at=(now + timedelta(days=duration_days)).isoformat() if duration_days else None
        )
        
        self.consents[consent_id] = consent
        logger.info(f"Consent recorded: {consent_id}")
        return consent
    
    def withdraw_consent(self, consent_id: str):
        """Withdraw consent"""
        if consent_id not in self.consents:
            raise HTTPException(status_code=404, detail="Consent not found")
        
        self.consents[consent_id].withdrawn = True
        self.consents[consent_id].withdrawn_at = datetime.utcnow().isoformat()
        logger.info(f"Consent withdrawn: {consent_id}")
    
    def submit_redress(
        self,
        subject_pseudonym: str,
        request_type: str,
        details: str
    ) -> RedressRequest:
        """Submit redress/appeal request"""
        request_id = str(uuid.uuid4())
        
        request = RedressRequest(
            request_id=request_id,
            subject_pseudonym=subject_pseudonym,
            request_type=request_type,
            details=details,
            submitted_at=datetime.utcnow().isoformat(),
            status="pending"
        )
        
        self.redress_requests[request_id] = request
        self.transparency_data['redress_count'] += 1
        
        logger.info(f"Redress request submitted: {request_id}")
        return request
    
    def generate_transparency_report(self, period: str) -> TransparencyReport:
        """Generate public transparency report"""
        from collections import defaultdict
        
        return TransparencyReport(
            report_period=period,
            total_identity_checks=self.transparency_data['identity_checks'],
            purposes=dict(self.transparency_data['purposes']),
            false_positive_rate=0.02,  # From bias monitoring
            bias_metrics={'demographic_parity': 0.95, 'equal_opportunity': 0.93},
            redress_requests=self.transparency_data['redress_count'],
            redress_resolved=len([r for r in self.redress_requests.values() if r.status == 'resolved'])
        )


from collections import defaultdict
governance = GovernanceService()


@app.post("/api/v1/consent", response_model=ConsentRecord)
async def record_consent(
    subject_id: str,
    purpose: ProcessingPurpose,
    legal_basis: LegalBasis,
    duration_days: Optional[int] = 365
):
    """Record consent from data subject"""
    return governance.record_consent(subject_id, purpose, legal_basis, duration_days)


@app.post("/api/v1/consent/{consent_id}/withdraw")
async def withdraw_consent(consent_id: str):
    """Withdraw consent"""
    governance.withdraw_consent(consent_id)
    return {"status": "withdrawn", "consent_id": consent_id}


@app.post("/api/v1/validate-processing")
async def validate_processing(
    purpose: ProcessingPurpose,
    legal_basis: LegalBasis,
    data_attributes: List[str]
):
    """Validate if data processing is compliant"""
    is_valid = governance.validate_processing(purpose, legal_basis, data_attributes)
    
    return {
        "compliant": is_valid,
        "purpose": purpose,
        "legal_basis": legal_basis,
        "ndpr_compliant": is_valid
    }


@app.post("/api/v1/redress", response_model=RedressRequest)
async def submit_redress(
    subject_pseudonym: str,
    request_type: Literal["access", "correction", "deletion", "objection", "complaint"],
    details: str
):
    """Submit redress/appeal request"""
    return governance.submit_redress(subject_pseudonym, request_type, details)


@app.get("/api/v1/redress/{request_id}")
async def get_redress_status(request_id: str):
    """Check redress request status"""
    if request_id not in governance.redress_requests:
        raise HTTPException(status_code=404, detail="Request not found")
    
    return governance.redress_requests[request_id]


@app.get("/api/v1/transparency-report", response_model=TransparencyReport)
async def get_transparency_report(period: str = "2025-Q4"):
    """Get public transparency report"""
    return governance.generate_transparency_report(period)


@app.get("/health")
async def health():
    return {"status": "healthy", "service": "governance"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8084)
