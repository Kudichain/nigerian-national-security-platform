"""Data schemas for all security domains."""

from typing import Optional, List
from pydantic import BaseModel, Field
from datetime import datetime


# ============ Network Flow Schema ============
class NetworkFlow(BaseModel):
    """Network flow event schema (NetFlow/IPFIX)."""
    
    ts: datetime = Field(..., description="Event timestamp")
    src_ip: str = Field(..., description="Source IP address")
    dst_ip: str = Field(..., description="Destination IP address")
    src_port: int = Field(..., ge=0, le=65535)
    dst_port: int = Field(..., ge=0, le=65535)
    protocol: str = Field(..., description="Protocol (TCP/UDP/ICMP)")
    bytes: int = Field(..., ge=0, description="Total bytes transferred")
    packets: int = Field(..., ge=0, description="Total packets")
    duration_ms: int = Field(..., ge=0, description="Flow duration in milliseconds")
    flow_type: Optional[str] = Field(None, description="Flow type (DNS/HTTP/TLS)")
    ja3: Optional[str] = Field(None, description="JA3 TLS fingerprint")
    asn_src: Optional[int] = Field(None, description="Source ASN")
    asn_dst: Optional[int] = Field(None, description="Destination ASN")
    geo_src: Optional[str] = Field(None, description="Source country code")
    geo_dst: Optional[str] = Field(None, description="Destination country code")
    label: Optional[str] = Field(None, description="Ground truth label")


# ============ Log Event Schema ============
class LogEvent(BaseModel):
    """Normalized log event schema (ECS-compatible)."""
    
    ts: datetime
    host: str = Field(..., description="Source hostname")
    user: Optional[str] = Field(None, description="Username")
    event_id: str = Field(..., description="Event identifier")
    event_type: str = Field(..., description="Event type/category")
    process: Optional[str] = Field(None, description="Process name")
    cmdline: Optional[str] = Field(None, description="Command line")
    status: Optional[str] = Field(None, description="Event status (success/failure)")
    message: str = Field(..., description="Log message")
    src_ip: Optional[str] = Field(None)
    dst_ip: Optional[str] = Field(None)
    session_id: Optional[str] = Field(None)
    label: Optional[str] = Field(None)


# ============ Email/Phishing Schema ============
class EmailMessage(BaseModel):
    """Email message schema for phishing detection."""
    
    msg_id: str = Field(..., description="Unique message ID")
    ts: datetime
    from_addr: str = Field(..., alias="from")
    to_addrs: List[str] = Field(..., alias="to")
    subject: str
    body_text: Optional[str] = Field(None, description="Plain text body")
    body_html: Optional[str] = Field(None, description="HTML body")
    attachments: List[str] = Field(default_factory=list, description="Attachment hashes")
    spf_result: Optional[str] = Field(None, description="SPF check result")
    dkim_result: Optional[str] = Field(None, description="DKIM check result")
    dmarc_result: Optional[str] = Field(None, description="DMARC check result")
    urls: List[str] = Field(default_factory=list, description="Extracted URLs")
    label: Optional[str] = Field(None)

    class Config:
        populate_by_name = True


# ============ Authentication Event Schema ============
class AuthEvent(BaseModel):
    """Authentication event schema for risk scoring."""
    
    ts: datetime
    user_id: str
    device_id: Optional[str] = Field(None, description="Device fingerprint")
    ip: str = Field(..., description="Source IP address")
    geo: Optional[str] = Field(None, description="Country code")
    user_agent: Optional[str] = Field(None, alias="ua")
    event_type: str = Field(..., description="login_success/login_fail/token_refresh")
    mfa_used: bool = Field(default=False)
    risk_score: Optional[float] = Field(None, ge=0.0, le=1.0)
    label: Optional[str] = Field(None, description="Ground truth: fraud/compromised/benign")

    class Config:
        populate_by_name = True


# ============ Malware File Schema ============
class MalwareFile(BaseModel):
    """Malware file metadata schema."""
    
    file_hash: str = Field(..., description="SHA256 hash")
    file_name: str
    file_size: int = Field(..., ge=0)
    file_type: Optional[str] = Field(None, description="MIME type or PE/ELF")
    pe_imports: Optional[List[str]] = Field(None, description="PE import functions")
    sections_entropy: Optional[List[float]] = Field(None, description="Section entropy values")
    ssdeep: Optional[str] = Field(None, description="Fuzzy hash")
    sandbox_trace_url: Optional[str] = Field(None, description="Link to sandbox analysis")
    yara_matches: Optional[List[str]] = Field(None, description="YARA rule matches")
    label: Optional[str] = Field(None, description="benign/malicious/family_name")


# ============ Inference Response Schema ============
class InferenceResponse(BaseModel):
    """Standardized inference response across all domains."""
    
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    domain: str = Field(..., description="nids/logs/phishing/auth/malware")
    score: float = Field(..., description="Anomaly/risk score")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Model confidence")
    label: str = Field(..., description="Predicted label")
    action: str = Field(..., description="Recommended action: allow/alert/block")
    explanation: List[dict] = Field(
        default_factory=list,
        description="Top contributing features with SHAP values"
    )
    metadata: Optional[dict] = Field(None, description="Additional context")
    model_version: str = Field(..., description="Model version used")


# ============ Alert Schema ============
class SecurityAlert(BaseModel):
    """Security alert sent to SIEM."""
    
    alert_id: str
    timestamp: datetime
    domain: str
    severity: str = Field(..., description="low/medium/high/critical")
    title: str
    description: str
    affected_assets: List[str] = Field(default_factory=list)
    indicators: List[dict] = Field(default_factory=list)
    raw_events: List[str] = Field(default_factory=list, description="Links to raw events")
    inference_result: InferenceResponse
    analyst_action: Optional[str] = Field(None, description="Action taken by analyst")
    false_positive: Optional[bool] = Field(None)
