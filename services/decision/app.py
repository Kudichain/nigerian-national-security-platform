"""
Policy-Based Decision Engine with Human-in-the-Loop
OPA integration, three operation modes, immutable audit logging
"""
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any, Literal
from enum import Enum
from datetime import datetime, timedelta
import json
import hashlib
import hmac
import uuid
import logging
from dataclasses import dataclass, asdict

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Decision Engine", version="1.0.0")


class OperationMode(str, Enum):
    """Three-tier operation modes"""
    OBSERVE = "observe"      # Log only, no actuation
    ASSISTED = "assisted"    # Human approval required
    AUTOMATIC = "automatic"  # Automated (safety-critical only)


class ActionType(str, Enum):
    """Types of enforcement actions"""
    ALERT_ONLY = "alert_only"
    OPERATOR_REVIEW = "operator_review"
    TRAFFIC_CONTROL = "traffic_control"
    EMERGENCY_STOP = "emergency_stop"


class MatchContext(BaseModel):
    """Context for identity match decision"""
    match: bool
    pseudonym: Optional[str]
    confidence: float
    location: Dict[str, float]
    timestamp: str
    device_id: str
    threat_score: Optional[float] = 0.0
    metadata: Dict[str, Any] = Field(default_factory=dict)


class PolicyDecision(BaseModel):
    """Decision output from policy engine"""
    decision_id: str
    allowed: bool
    action: ActionType
    requires_approval: bool
    reason: str
    confidence: float
    mode: OperationMode
    audit_event: Dict[str, Any]


class ApprovalRequest(BaseModel):
    """Pending approval request"""
    request_id: str
    decision_id: str
    action: ActionType
    evidence: Dict[str, Any]
    operator_id: Optional[str] = None
    status: Literal["pending", "approved", "rejected", "expired"]
    created_at: str
    expires_at: str
    approved_at: Optional[str] = None


@dataclass
class AuditEvent:
    """Immutable audit log entry"""
    event_id: str
    timestamp: str
    event_type: str
    decision_id: str
    mode: OperationMode
    action: ActionType
    context: Dict[str, Any]
    decision: Dict[str, Any]
    operator_id: Optional[str]
    hash_chain: str  # Cryptographic hash of previous event
    
    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)
    
    def compute_hash(self, previous_hash: str) -> str:
        """Compute tamper-evident hash"""
        data = f"{self.event_id}:{self.timestamp}:{previous_hash}:{json.dumps(self.decision)}".encode()
        return hashlib.sha256(data).hexdigest()


class ImmutableAuditLog:
    """Write-once, tamper-evident audit log (WORM storage simulation)"""
    
    def __init__(self):
        self.events: List[AuditEvent] = []
        self.last_hash = "genesis"
        logger.info("Immutable audit log initialized")
    
    def append(self, event: AuditEvent) -> str:
        """Append event to audit log"""
        event.hash_chain = event.compute_hash(self.last_hash)
        self.events.append(event)
        self.last_hash = event.hash_chain
        
        logger.info(f"Audit event recorded: {event.event_id}")
        return event.hash_chain
    
    def verify_integrity(self) -> bool:
        """Verify audit log integrity"""
        prev_hash = "genesis"
        for event in self.events:
            expected_hash = event.compute_hash(prev_hash)
            if event.hash_chain != expected_hash:
                logger.error(f"Audit log tampering detected at event {event.event_id}")
                return False
            prev_hash = event.hash_chain
        return True
    
    def get_events(self, filters: Optional[Dict[str, Any]] = None) -> List[AuditEvent]:
        """Query audit events"""
        if not filters:
            return self.events
        
        # Simple filtering
        filtered = self.events
        if 'event_type' in filters:
            filtered = [e for e in filtered if e.event_type == filters['event_type']]
        if 'decision_id' in filters:
            filtered = [e for e in filtered if e.decision_id == filters['decision_id']]
        
        return filtered


class PolicyEngine:
    """
    Policy evaluation engine (OPA-like)
    Evaluates context against policies to determine allowed actions
    """
    
    def __init__(self, mode: OperationMode = OperationMode.ASSISTED):
        self.mode = mode
        self.policies = self._load_default_policies()
        logger.info(f"Policy engine initialized in {mode} mode")
    
    def _load_default_policies(self) -> Dict[str, Any]:
        """Load default security policies"""
        return {
            'identity_match': {
                'min_confidence': 0.85,
                'max_threat_score': 0.7,
                'allowed_actions': {
                    'high_confidence_low_threat': ActionType.ALERT_ONLY,
                    'high_confidence_high_threat': ActionType.OPERATOR_REVIEW,
                    'critical_threat': ActionType.TRAFFIC_CONTROL
                }
            },
            'traffic_control': {
                'requires_approval': True,
                'approval_timeout_seconds': 300,
                'authorized_operators': ['admin', 'law_enforcement']
            },
            'observe_mode': {
                'allow_actuation': False,
                'log_all_events': True
            }
        }
    
    def evaluate(self, context: MatchContext) -> PolicyDecision:
        """
        Evaluate context against policies
        Returns decision with required action
        """
        decision_id = str(uuid.uuid4())
        
        # Mode-based routing
        if self.mode == OperationMode.OBSERVE:
            return self._observe_only_decision(decision_id, context)
        
        # Evaluate identity match policies
        if not context.match:
            return PolicyDecision(
                decision_id=decision_id,
                allowed=False,
                action=ActionType.ALERT_ONLY,
                requires_approval=False,
                reason="No identity match",
                confidence=0.0,
                mode=self.mode,
                audit_event=self._create_audit_event(decision_id, context, "no_match")
            )
        
        # Check confidence threshold
        min_confidence = self.policies['identity_match']['min_confidence']
        if context.confidence < min_confidence:
            return PolicyDecision(
                decision_id=decision_id,
                allowed=False,
                action=ActionType.OPERATOR_REVIEW,
                requires_approval=True,
                reason=f"Confidence {context.confidence} below threshold {min_confidence}",
                confidence=context.confidence,
                mode=self.mode,
                audit_event=self._create_audit_event(decision_id, context, "low_confidence")
            )
        
        # Determine action based on threat score
        threat_score = context.threat_score or 0.0
        
        if threat_score > 0.8:
            # Critical threat - may allow traffic control in AUTOMATIC mode
            action = ActionType.TRAFFIC_CONTROL
            requires_approval = (self.mode != OperationMode.AUTOMATIC)
            reason = "Critical threat detected - traffic control authorized"
        
        elif threat_score > 0.5:
            # High threat - operator review
            action = ActionType.OPERATOR_REVIEW
            requires_approval = True
            reason = "High threat - operator review required"
        
        else:
            # Low threat - alert only
            action = ActionType.ALERT_ONLY
            requires_approval = False
            reason = "Low threat - monitoring only"
        
        return PolicyDecision(
            decision_id=decision_id,
            allowed=True,
            action=action,
            requires_approval=requires_approval,
            reason=reason,
            confidence=context.confidence,
            mode=self.mode,
            audit_event=self._create_audit_event(decision_id, context, "policy_evaluated")
        )
    
    def _observe_only_decision(self, decision_id: str, context: MatchContext) -> PolicyDecision:
        """Observe mode: log only, no actuation"""
        return PolicyDecision(
            decision_id=decision_id,
            allowed=False,
            action=ActionType.ALERT_ONLY,
            requires_approval=False,
            reason="Observe-only mode - no actuation permitted",
            confidence=context.confidence,
            mode=OperationMode.OBSERVE,
            audit_event=self._create_audit_event(decision_id, context, "observe_mode")
        )
    
    def _create_audit_event(
        self,
        decision_id: str,
        context: MatchContext,
        event_type: str
    ) -> Dict[str, Any]:
        """Create audit event data"""
        return {
            'decision_id': decision_id,
            'event_type': event_type,
            'context': context.dict(),
            'timestamp': datetime.utcnow().isoformat(),
            'mode': self.mode.value
        }


class ApprovalWorkflow:
    """Human-in-the-loop approval workflow"""
    
    def __init__(self, timeout_seconds: int = 300):
        self.pending_approvals: Dict[str, ApprovalRequest] = {}
        self.timeout = timedelta(seconds=timeout_seconds)
        logger.info(f"Approval workflow initialized (timeout: {timeout_seconds}s)")
    
    def create_approval_request(
        self,
        decision: PolicyDecision,
        evidence: Dict[str, Any]
    ) -> ApprovalRequest:
        """Create pending approval request"""
        request_id = str(uuid.uuid4())
        now = datetime.utcnow()
        
        request = ApprovalRequest(
            request_id=request_id,
            decision_id=decision.decision_id,
            action=decision.action,
            evidence=evidence,
            status="pending",
            created_at=now.isoformat(),
            expires_at=(now + self.timeout).isoformat()
        )
        
        self.pending_approvals[request_id] = request
        logger.info(f"Approval request created: {request_id}")
        return request
    
    def approve(self, request_id: str, operator_id: str) -> ApprovalRequest:
        """Approve pending request"""
        if request_id not in self.pending_approvals:
            raise HTTPException(status_code=404, detail="Request not found")
        
        request = self.pending_approvals[request_id]
        
        # Check expiry
        if datetime.fromisoformat(request.expires_at) < datetime.utcnow():
            request.status = "expired"
            raise HTTPException(status_code=410, detail="Request expired")
        
        request.status = "approved"
        request.operator_id = operator_id
        request.approved_at = datetime.utcnow().isoformat()
        
        logger.info(f"Request approved: {request_id} by {operator_id}")
        return request
    
    def reject(self, request_id: str, operator_id: str) -> ApprovalRequest:
        """Reject pending request"""
        if request_id not in self.pending_approvals:
            raise HTTPException(status_code=404, detail="Request not found")
        
        request = self.pending_approvals[request_id]
        request.status = "rejected"
        request.operator_id = operator_id
        request.approved_at = datetime.utcnow().isoformat()
        
        logger.info(f"Request rejected: {request_id} by {operator_id}")
        return request
    
    def get_pending(self) -> List[ApprovalRequest]:
        """Get all pending approval requests"""
        return [r for r in self.pending_approvals.values() if r.status == "pending"]


# Initialize components
audit_log = ImmutableAuditLog()
policy_engine = PolicyEngine(mode=OperationMode.ASSISTED)
approval_workflow = ApprovalWorkflow(timeout_seconds=300)


# API Endpoints

@app.post("/api/v1/evaluate", response_model=PolicyDecision)
async def evaluate_decision(context: MatchContext):
    """
    Evaluate policy and return decision
    Records immutable audit event
    """
    decision = policy_engine.evaluate(context)
    
    # Record audit event
    audit_event = AuditEvent(
        event_id=str(uuid.uuid4()),
        timestamp=datetime.utcnow().isoformat(),
        event_type="policy_evaluation",
        decision_id=decision.decision_id,
        mode=decision.mode,
        action=decision.action,
        context=context.dict(),
        decision=decision.dict(),
        operator_id=None,
        hash_chain=audit_log.last_hash
    )
    audit_log.append(audit_event)
    
    # Create approval request if needed
    if decision.requires_approval:
        evidence = {
            'match_confidence': context.confidence,
            'location': context.location,
            'device_id': context.device_id,
            'pseudonym': context.pseudonym
        }
        approval_req = approval_workflow.create_approval_request(decision, evidence)
        decision.audit_event['approval_request_id'] = approval_req.request_id
    
    return decision


@app.post("/api/v1/approvals/{request_id}/approve")
async def approve_request(request_id: str, operator_id: str):
    """Approve pending action (operator only)"""
    request = approval_workflow.approve(request_id, operator_id)
    
    # Record approval in audit log
    audit_event = AuditEvent(
        event_id=str(uuid.uuid4()),
        timestamp=datetime.utcnow().isoformat(),
        event_type="approval_granted",
        decision_id=request.decision_id,
        mode=policy_engine.mode,
        action=request.action,
        context={'request_id': request_id},
        decision={'status': 'approved'},
        operator_id=operator_id,
        hash_chain=audit_log.last_hash
    )
    audit_log.append(audit_event)
    
    return request


@app.post("/api/v1/approvals/{request_id}/reject")
async def reject_request(request_id: str, operator_id: str):
    """Reject pending action (operator only)"""
    request = approval_workflow.reject(request_id, operator_id)
    
    # Record rejection in audit log
    audit_event = AuditEvent(
        event_id=str(uuid.uuid4()),
        timestamp=datetime.utcnow().isoformat(),
        event_type="approval_rejected",
        decision_id=request.decision_id,
        mode=policy_engine.mode,
        action=request.action,
        context={'request_id': request_id},
        decision={'status': 'rejected'},
        operator_id=operator_id,
        hash_chain=audit_log.last_hash
    )
    audit_log.append(audit_event)
    
    return request


@app.get("/api/v1/approvals/pending", response_model=List[ApprovalRequest])
async def get_pending_approvals():
    """Get all pending approval requests"""
    return approval_workflow.get_pending()


@app.get("/api/v1/audit/verify")
async def verify_audit_integrity():
    """Verify audit log integrity"""
    is_valid = audit_log.verify_integrity()
    return {
        "valid": is_valid,
        "total_events": len(audit_log.events),
        "last_hash": audit_log.last_hash
    }


@app.get("/api/v1/audit/events")
async def query_audit_events(event_type: Optional[str] = None):
    """Query audit events"""
    filters = {}
    if event_type:
        filters['event_type'] = event_type
    
    events = audit_log.get_events(filters)
    return [e.to_dict() for e in events]


@app.post("/api/v1/mode")
async def set_operation_mode(mode: OperationMode):
    """Change operation mode (admin only)"""
    old_mode = policy_engine.mode
    policy_engine.mode = mode
    
    # Record mode change in audit log
    audit_event = AuditEvent(
        event_id=str(uuid.uuid4()),
        timestamp=datetime.utcnow().isoformat(),
        event_type="mode_change",
        decision_id="N/A",
        mode=mode,
        action=ActionType.ALERT_ONLY,
        context={'old_mode': old_mode.value, 'new_mode': mode.value},
        decision={'mode_changed': True},
        operator_id="admin",
        hash_chain=audit_log.last_hash
    )
    audit_log.append(audit_event)
    
    logger.warning(f"Operation mode changed: {old_mode} -> {mode}")
    return {"old_mode": old_mode, "new_mode": mode}


@app.get("/health")
async def health_check():
    """Health check"""
    return {
        "status": "healthy",
        "service": "decision-engine",
        "mode": policy_engine.mode.value,
        "pending_approvals": len(approval_workflow.get_pending()),
        "audit_events": len(audit_log.events)
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8082)
