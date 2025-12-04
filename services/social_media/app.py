"""
Social Media Regulation Service
AI-powered content moderation with mandatory human review
Disinformation detection, hate speech flagging, Cybercrime Act compliance
"""
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any, Literal
from enum import Enum
from datetime import datetime, timedelta
import hashlib
import uuid
import logging
import re

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Social Media Regulation Service", version="1.0.0")


class ContentType(str, Enum):
    """Content categories"""
    POST = "post"
    COMMENT = "comment"
    IMAGE = "image"
    VIDEO = "video"
    LIVE_STREAM = "live_stream"


class ViolationType(str, Enum):
    """Content violation types per Nigeria Cybercrime Act 2015"""
    HATE_SPEECH = "hate_speech"              # Section 24 - Cyberstalking
    DISINFORMATION = "disinformation"        # False news, election interference
    VIOLENT_CONTENT = "violent_content"      # Graphic violence, terrorism
    CHILD_EXPLOITATION = "child_exploitation"  # Section 23 - Child pornography
    HARASSMENT = "harassment"                # Section 24 - Cyberstalking
    TERRORISM = "terrorism"                  # Section 26 - Cyber terrorism
    FRAUD = "fraud"                          # Section 22 - Identity theft
    COPYRIGHT = "copyright"                  # Intellectual property
    NONE = "none"


class ModerationAction(str, Enum):
    """Recommended moderation actions"""
    APPROVE = "approve"
    FLAG_REVIEW = "flag_review"
    SOFT_DELETE = "soft_delete"
    HARD_DELETE = "hard_delete"
    SHADOWBAN = "shadowban"
    ACCOUNT_SUSPEND = "account_suspend"
    REPORT_LAW_ENFORCEMENT = "report_law_enforcement"


class ReviewStatus(str, Enum):
    """Human review status"""
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    ESCALATED = "escalated"
    TAKEDOWN_ORDERED = "takedown_ordered"


class ContentSubmission(BaseModel):
    """Content submitted for moderation"""
    content_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    platform: str = Field(..., description="Social media platform (Twitter, Facebook, etc)")
    content_type: ContentType
    text: Optional[str] = None
    media_url: Optional[str] = None
    author_id: str = Field(..., description="Pseudonymous author ID (no PII)")
    timestamp: str
    metadata: Dict[str, Any] = Field(default_factory=dict)
    
    class Config:
        json_schema_extra = {
            "example": {
                "content_id": "content-001",
                "platform": "Twitter",
                "content_type": "post",
                "text": "Example tweet text here",
                "author_id": "user_abc123",
                "timestamp": "2025-11-27T10:00:00Z",
                "metadata": {"reach": 5000, "engagement": 120}
            }
        }


class ModerationResult(BaseModel):
    """AI moderation result"""
    content_id: str
    violation_type: ViolationType
    confidence: float = Field(..., ge=0.0, le=1.0)
    recommended_action: ModerationAction
    explanation: str
    detected_patterns: List[str] = Field(default_factory=list)
    severity_score: float = Field(..., ge=0.0, le=1.0)
    requires_human_review: bool
    cybercrime_act_sections: List[str] = Field(default_factory=list)


class ModeratorReview(BaseModel):
    """Human moderator review"""
    review_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    content_id: str
    moderator_id: str
    decision: ReviewStatus
    action_taken: ModerationAction
    justification: str
    reviewed_at: str = Field(default_factory=lambda: datetime.utcnow().isoformat())
    legal_basis: Optional[str] = None


class ContentRecord(BaseModel):
    """Complete content moderation record"""
    record_id: str
    submission: ContentSubmission
    ai_moderation: ModerationResult
    human_review: Optional[ModeratorReview]
    status: ReviewStatus
    action_log: List[Dict[str, Any]] = Field(default_factory=list)
    created_at: str
    resolved_at: Optional[str] = None


class SocialMediaRegulator:
    """
    Social media content moderation with AI + mandatory human oversight
    Enforces Nigeria Cybercrime Act 2015 compliance
    """
    
    def __init__(self):
        # Content records
        self.records: Dict[str, ContentRecord] = {}
        
        # Moderator registry (in production: SSO/LDAP)
        self.moderators = {
            "mod-001": {"name": "Moderator A", "clearance": "standard"},
            "mod-002": {"name": "Moderator B", "clearance": "senior"},
            "mod-admin": {"name": "Admin", "clearance": "admin"}
        }
        
        # Cybercrime Act reference
        self.cybercrime_sections = {
            ViolationType.HATE_SPEECH: "Section 24 - Cyberstalking",
            ViolationType.CHILD_EXPLOITATION: "Section 23 - Child Pornography",
            ViolationType.TERRORISM: "Section 26 - Cyber Terrorism",
            ViolationType.FRAUD: "Section 22 - Identity Theft/Fraud",
            ViolationType.HARASSMENT: "Section 24 - Cyberstalking"
        }
        
        # Banned keywords (hate speech, violence)
        self.hate_keywords = [
            "ethnic slur", "religious hate", "violent threats",
            # In production: comprehensive hate speech lexicon
        ]
        
        self.disinformation_indicators = [
            "fake news", "unverified claim", "manipulated media",
            # In production: ML-based fact-checking
        ]
        
        logger.info("Social Media Regulator initialized")
    
    def moderate_content(self, submission: ContentSubmission) -> ModerationResult:
        """
        AI-powered content moderation
        Returns violation detection + recommended action
        """
        violation_type = ViolationType.NONE
        confidence = 0.0
        detected_patterns = []
        severity = 0.0
        explanation = "Content approved"
        recommended_action = ModerationAction.APPROVE
        
        if submission.text:
            text_lower = submission.text.lower()
            
            # Hate speech detection
            hate_matches = [kw for kw in self.hate_keywords if kw in text_lower]
            if hate_matches:
                violation_type = ViolationType.HATE_SPEECH
                confidence = 0.85
                detected_patterns = hate_matches
                severity = 0.9
                explanation = f"Detected hate speech patterns: {', '.join(hate_matches)}"
                recommended_action = ModerationAction.FLAG_REVIEW
            
            # Disinformation detection
            disinfo_matches = [ind for ind in self.disinformation_indicators if ind in text_lower]
            if disinfo_matches and violation_type == ViolationType.NONE:
                violation_type = ViolationType.DISINFORMATION
                confidence = 0.75
                detected_patterns = disinfo_matches
                severity = 0.7
                explanation = f"Potential disinformation: {', '.join(disinfo_matches)}"
                recommended_action = ModerationAction.FLAG_REVIEW
            
            # Violence keywords
            if "kill" in text_lower or "bomb" in text_lower or "attack" in text_lower:
                if violation_type == ViolationType.NONE:
                    violation_type = ViolationType.VIOLENT_CONTENT
                confidence = max(confidence, 0.8)
                detected_patterns.append("violent language")
                severity = max(severity, 0.85)
                explanation = "Detected violent content"
                recommended_action = ModerationAction.FLAG_REVIEW
            
            # Terrorism indicators
            if "isis" in text_lower or "boko haram" in text_lower:
                violation_type = ViolationType.TERRORISM
                confidence = 0.95
                detected_patterns.append("terrorism reference")
                severity = 1.0
                explanation = "Terrorism-related content detected"
                recommended_action = ModerationAction.REPORT_LAW_ENFORCEMENT
        
        # Get Cybercrime Act sections
        cybercrime_sections = []
        if violation_type in self.cybercrime_sections:
            cybercrime_sections = [self.cybercrime_sections[violation_type]]
        
        # Require human review for violations
        requires_review = (
            violation_type != ViolationType.NONE or
            confidence >= 0.7 or
            severity >= 0.8
        )
        
        result = ModerationResult(
            content_id=submission.content_id,
            violation_type=violation_type,
            confidence=confidence,
            recommended_action=recommended_action,
            explanation=explanation,
            detected_patterns=detected_patterns,
            severity_score=severity,
            requires_human_review=requires_review,
            cybercrime_act_sections=cybercrime_sections
        )
        
        logger.info(
            f"Moderated {submission.content_id}: {violation_type.value} "
            f"(confidence: {confidence:.2f}, severity: {severity:.2f})"
        )
        
        return result
    
    def create_record(self, submission: ContentSubmission) -> ContentRecord:
        """Create content moderation record"""
        record_id = f"REC-{datetime.utcnow().strftime('%Y%m%d')}-{str(uuid.uuid4())[:8].upper()}"
        
        # Run AI moderation
        ai_result = self.moderate_content(submission)
        
        # Determine initial status
        if ai_result.requires_human_review:
            status = ReviewStatus.PENDING
        else:
            status = ReviewStatus.APPROVED
        
        record = ContentRecord(
            record_id=record_id,
            submission=submission,
            ai_moderation=ai_result,
            human_review=None,
            status=status,
            created_at=datetime.utcnow().isoformat()
        )
        
        self.records[record_id] = record
        
        # Auto-escalate critical violations
        if ai_result.severity_score >= 0.9:
            logger.warning(
                f"🚨 CRITICAL VIOLATION: {record_id} - {ai_result.violation_type} "
                f"(severity: {ai_result.severity_score:.2f}) - REQUIRES IMMEDIATE REVIEW"
            )
        
        return record
    
    def submit_moderator_review(self, review: ModeratorReview) -> ContentRecord:
        """
        Human moderator reviews flagged content
        MANDATORY for all violations
        """
        # Find record
        record = None
        for rec in self.records.values():
            if rec.submission.content_id == review.content_id:
                record = rec
                break
        
        if not record:
            raise HTTPException(status_code=404, detail="Content record not found")
        
        # Verify moderator
        if review.moderator_id not in self.moderators:
            raise HTTPException(status_code=403, detail="Unauthorized moderator")
        
        # Update record
        record.human_review = review
        record.status = review.decision
        
        # Execute action
        if review.action_taken == ModerationAction.HARD_DELETE:
            logger.warning(f"🗑️ TAKEDOWN: {review.content_id} - {review.justification}")
        elif review.action_taken == ModerationAction.REPORT_LAW_ENFORCEMENT:
            logger.critical(
                f"🚔 LAW ENFORCEMENT REPORT: {review.content_id} - "
                f"{record.ai_moderation.violation_type} - {review.legal_basis}"
            )
        
        # Add to action log
        record.action_log.append({
            'timestamp': review.reviewed_at,
            'action': 'moderator_review',
            'moderator': review.moderator_id,
            'decision': review.decision.value,
            'action_taken': review.action_taken.value,
            'justification': review.justification
        })
        
        if review.decision == ReviewStatus.TAKEDOWN_ORDERED:
            record.resolved_at = datetime.utcnow().isoformat()
        
        logger.info(
            f"Moderator {review.moderator_id} reviewed {review.content_id}: "
            f"{review.decision.value} -> {review.action_taken.value}"
        )
        
        return record
    
    def get_pending_reviews(self) -> List[ContentRecord]:
        """Get content awaiting human review"""
        return [
            rec for rec in self.records.values()
            if rec.status == ReviewStatus.PENDING
        ]
    
    def get_cybercrime_reports(self) -> List[ContentRecord]:
        """Get content requiring law enforcement notification"""
        return [
            rec for rec in self.records.values()
            if rec.human_review and 
            rec.human_review.action_taken == ModerationAction.REPORT_LAW_ENFORCEMENT
        ]
    
    def generate_compliance_report(self) -> Dict[str, Any]:
        """
        Generate Cybercrime Act compliance report
        For regulatory submission
        """
        total_content = len(self.records)
        violations_detected = sum(
            1 for rec in self.records.values()
            if rec.ai_moderation.violation_type != ViolationType.NONE
        )
        human_reviewed = sum(
            1 for rec in self.records.values()
            if rec.human_review is not None
        )
        takedowns = sum(
            1 for rec in self.records.values()
            if rec.status == ReviewStatus.TAKEDOWN_ORDERED
        )
        law_enforcement_reports = len(self.get_cybercrime_reports())
        
        violation_breakdown = {}
        for rec in self.records.values():
            vtype = rec.ai_moderation.violation_type.value
            violation_breakdown[vtype] = violation_breakdown.get(vtype, 0) + 1
        
        return {
            "report_date": datetime.utcnow().isoformat(),
            "total_content_moderated": total_content,
            "violations_detected": violations_detected,
            "human_reviews_conducted": human_reviewed,
            "takedowns_executed": takedowns,
            "law_enforcement_reports": law_enforcement_reports,
            "violation_breakdown": violation_breakdown,
            "compliance_rate": f"{(human_reviewed / max(violations_detected, 1)) * 100:.1f}%",
            "legal_framework": "Nigeria Cybercrime (Prohibition, Prevention, etc.) Act 2015"
        }


# Initialize service
regulator = SocialMediaRegulator()


# API Endpoints

@app.post("/api/v1/moderate", response_model=ContentRecord)
async def moderate_content(submission: ContentSubmission):
    """
    Submit content for AI moderation
    Flagged content requires human review before action
    """
    record = regulator.create_record(submission)
    return record


@app.post("/api/v1/review/{content_id}")
async def submit_review(content_id: str, review: ModeratorReview):
    """
    Human moderator reviews flagged content
    MANDATORY before enforcement actions
    """
    review.content_id = content_id
    record = regulator.submit_moderator_review(review)
    return record


@app.get("/api/v1/records", response_model=List[ContentRecord])
async def list_records(
    pending_only: bool = False,
    violation_type: Optional[ViolationType] = None
):
    """List content moderation records"""
    if pending_only:
        return regulator.get_pending_reviews()
    
    records = list(regulator.records.values())
    
    if violation_type:
        records = [
            rec for rec in records
            if rec.ai_moderation.violation_type == violation_type
        ]
    
    return records


@app.get("/api/v1/records/{record_id}", response_model=ContentRecord)
async def get_record(record_id: str):
    """Get specific record"""
    if record_id not in regulator.records:
        raise HTTPException(status_code=404, detail="Record not found")
    return regulator.records[record_id]


@app.get("/api/v1/compliance/report")
async def get_compliance_report():
    """
    Generate Cybercrime Act compliance report
    For regulatory submission to NBC/NITDA
    """
    return regulator.generate_compliance_report()


@app.get("/api/v1/compliance/law-enforcement")
async def get_law_enforcement_reports():
    """Get content reported to law enforcement"""
    return regulator.get_cybercrime_reports()


@app.get("/health")
async def health_check():
    """Health check"""
    pending = len(regulator.get_pending_reviews())
    
    return {
        "status": "healthy",
        "service": "social-media-regulation",
        "pending_reviews": pending,
        "total_records": len(regulator.records),
        "law_enforcement_reports": len(regulator.get_cybercrime_reports())
    }


if __name__ == "__main__":
    import uvicorn
    
    logger.info("Social Media Regulation Service started")
    logger.info("Legal Framework: Nigeria Cybercrime Act 2015")
    logger.info("CRITICAL: All enforcement actions require human moderator approval")
    logger.info("Privacy: Author IDs must be pseudonymous (no PII)")
    
    uvicorn.run(app, host="0.0.0.0", port=8088)
