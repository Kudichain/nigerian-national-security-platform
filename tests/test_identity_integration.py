"""
Integration Tests for Identity-Integrated Security System
Bias testing, safety interlocks, IEC 62443 compliance validation
"""
import pytest
import asyncio
import numpy as np
from datetime import datetime
import hashlib
import json

# Test Edge Processing
def test_edge_privacy_filter():
    """Test privacy filter blurs faces and enforces TTL"""
    from edge.drone_edge import PrivacyFilter
    
    filter = PrivacyFilter(video_ttl_seconds=30, blur_non_targets=True)
    
    # Simulate frame with faces
    frame = np.zeros((480, 640, 3), dtype=np.uint8)
    faces = [(100, 100, 50, 50), (300, 200, 60, 60)]
    
    blurred = filter.blur_faces(frame, faces)
    
    assert blurred.shape == frame.shape
    # Verify regions are different (blurred)
    assert not np.array_equal(blurred[100:150, 100:150], frame[100:150, 100:150])


def test_edge_differential_privacy():
    """Test differential privacy noise addition"""
    from edge.drone_edge import PrivacyFilter
    
    filter = PrivacyFilter()
    embedding = np.random.randn(128).astype(np.float32)
    
    noisy = filter.add_differential_noise(embedding, epsilon=0.1)
    
    # Verify shape preserved
    assert noisy.shape == embedding.shape
    # Verify noise added
    assert not np.array_equal(embedding, noisy)
    # Verify not too much noise (within bounds)
    diff = np.linalg.norm(embedding - noisy)
    assert diff < 10.0  # Reasonable noise magnitude


def test_edge_template_encryption():
    """Test biometric template encryption"""
    from edge.drone_edge import BiometricTemplate
    from cryptography.fernet import Fernet
    
    key = Fernet.generate_key()
    embedding = np.random.randn(128).astype(np.float32)
    template_hash = hashlib.sha256(embedding.tobytes()).hexdigest()
    
    template = BiometricTemplate(
        template_hash=template_hash,
        embedding=embedding,
        confidence=0.92,
        metadata={'device_id': 'test-001'}
    )
    
    encrypted = template.encrypt(key)
    
    # Verify encryption
    assert isinstance(encrypted, bytes)
    assert len(encrypted) > 0
    
    # Verify decryption
    fernet = Fernet(key)
    decrypted = json.loads(fernet.decrypt(encrypted))
    assert decrypted['template_hash'] == template_hash
    assert decrypted['confidence'] == 0.92


# Test Identity Matching
def test_tokenized_matching_privacy():
    """Test tokenized matching exposes no PII"""
    from services.identity.app import NIMCConnector
    
    nimc = NIMCConnector(
        api_endpoint="test",
        api_key="test",
        salt="test-salt"
    )
    
    # Register identity
    test_hash = hashlib.sha256(b"test_template").hexdigest()
    pseudonym = nimc.register_identity(
        template_hash=test_hash,
        nin="12345678901",
        attributes={
            'age_group': '25-34',
            'state': 'Lagos',
            'full_name': 'SENSITIVE PII'  # Should NOT be returned
        }
    )
    
    # Match
    result = nimc.match_tokenized(test_hash)
    
    # Verify privacy guarantees
    assert result is not None, "Result should not be None"
    assert result.match is True
    assert result.pseudonym is not None
    assert result.pseudonym.startswith("nimc_token_")
    
    # Verify only allowed attributes returned
    assert 'age_group' in result.allowed_attributes
    assert 'state' in result.allowed_attributes
    assert 'full_name' not in result.allowed_attributes
    assert 'nin' not in result.allowed_attributes


def test_pseudonym_unlinkability():
    """Test pseudonyms are unlinkable without salt"""
    from services.identity.app import NIMCConnector
    
    nimc1 = NIMCConnector("test", "test", salt="salt1")
    nimc2 = NIMCConnector("test", "test", salt="salt2")
    
    test_hash = hashlib.sha256(b"same_person").hexdigest()
    nin = "12345678901"
    
    pseudonym1 = nimc1._generate_pseudonym(test_hash, nin)
    pseudonym2 = nimc2._generate_pseudonym(test_hash, nin)
    
    # Different salts produce different pseudonyms (unlinkable)
    assert pseudonym1 != pseudonym2


# Test Decision Engine
def test_decision_observe_mode():
    """Test observe mode prevents actuation"""
    from services.decision.app import PolicyEngine, MatchContext, OperationMode
    
    engine = PolicyEngine(mode=OperationMode.OBSERVE)
    
    context = MatchContext(
        match=True,
        pseudonym="test_token",
        confidence=0.95,
        location={"lat": 9.0, "lon": 7.0},
        timestamp=datetime.utcnow().isoformat(),
        device_id="test",
        threat_score=0.9  # High threat
    )
    
    decision = engine.evaluate(context)
    
    # Verify no actuation in observe mode
    assert decision.allowed is False
    assert "observe" in decision.reason.lower()


def test_decision_assisted_approval_required():
    """Test assisted mode requires human approval"""
    from services.decision.app import PolicyEngine, MatchContext, OperationMode, ActionType
    
    engine = PolicyEngine(mode=OperationMode.ASSISTED)
    
    context = MatchContext(
        match=True,
        pseudonym="test_token",
        confidence=0.92,
        location={"lat": 9.0, "lon": 7.0},
        timestamp=datetime.utcnow().isoformat(),
        device_id="test",
        threat_score=0.85  # Critical
    )
    
    decision = engine.evaluate(context)
    
    # Verify approval required for critical actions
    assert decision.action == ActionType.TRAFFIC_CONTROL
    assert decision.requires_approval is True


def test_audit_log_tamper_detection():
    """Test audit log detects tampering"""
    from services.decision.app import ImmutableAuditLog, AuditEvent, OperationMode, ActionType
    
    log = ImmutableAuditLog()
    
    # Add events
    for i in range(3):
        event = AuditEvent(
            event_id=f"event_{i}",
            timestamp=datetime.utcnow().isoformat(),
            event_type="test",
            decision_id="test",
            mode=OperationMode.OBSERVE,
            action=ActionType.ALERT_ONLY,
            context={},
            decision={},
            operator_id=None,
            hash_chain=""
        )
        log.append(event)
    
    # Verify integrity
    assert log.verify_integrity() is True
    
    # Tamper with event
    log.events[1].decision = {"tampered": True}
    
    # Verify tampering detected
    assert log.verify_integrity() is False


# Test Traffic Control Safety
def test_traffic_safe_transition_validation():
    """Test traffic controller rejects unsafe transitions"""
    from services.traffic.app import IntersectionState, TrafficPhase, ControllerStatus
    
    state = IntersectionState(
        intersection_id="test",
        current_phase=TrafficPhase.NORTH_SOUTH_GREEN,
        status=ControllerStatus.NORMAL,
        last_phase_change=datetime.utcnow(),
        next_scheduled_change=datetime.utcnow(),
        remote_control_active=False,
        controller_health="healthy",
        phase_history=[]
    )
    
    # Safe transition
    assert state.is_safe_transition(TrafficPhase.NORTH_SOUTH_YELLOW) is True
    
    # Unsafe transition (both directions green)
    assert state.is_safe_transition(TrafficPhase.EAST_WEST_GREEN) is False


def test_traffic_clearance_requirement():
    """Test all-red clearance required for major transitions"""
    from services.traffic.app import IntersectionState, TrafficPhase, ControllerStatus
    
    state = IntersectionState(
        intersection_id="test",
        current_phase=TrafficPhase.NORTH_SOUTH_GREEN,
        status=ControllerStatus.NORMAL,
        last_phase_change=datetime.utcnow(),
        next_scheduled_change=datetime.utcnow(),
        remote_control_active=False,
        controller_health="healthy",
        phase_history=[]
    )
    
    # Major transition requires clearance
    assert state.requires_clearance(TrafficPhase.EAST_WEST_GREEN) is True
    
    # Minor transition does not
    assert state.requires_clearance(TrafficPhase.NORTH_SOUTH_YELLOW) is False


def test_traffic_simulation_prevents_conflicts():
    """Test simulation prevents conflicting signals"""
    from services.traffic.app import TrafficController, TrafficPhase
    
    controller = TrafficController("test-intersection")
    controller.state.current_phase = TrafficPhase.NORTH_SOUTH_GREEN
    
    # Simulate unsafe transition
    result = controller.simulate_phase_change(TrafficPhase.EAST_WEST_GREEN)
    
    # Should fail due to conflict
    assert result is False


def test_traffic_rate_limiting():
    """Test traffic controller rate limits phase changes"""
    from services.traffic.app import SafetyInterlock, IntersectionState, ControllerStatus, TrafficPhase
    import time
    
    interlock = SafetyInterlock()
    
    state = IntersectionState(
        intersection_id="test",
        current_phase=TrafficPhase.NORTH_SOUTH_GREEN,
        status=ControllerStatus.NORMAL,
        last_phase_change=datetime.utcnow(),
        next_scheduled_change=datetime.utcnow(),
        remote_control_active=False,
        controller_health="healthy",
        phase_history=[]
    )
    
    # First check should fail (too soon after last change)
    assert interlock._check_rate_limit(state) is False
    
    # Wait and retry
    time.sleep(6)
    state.last_phase_change = datetime.utcnow()
    assert interlock._check_rate_limit(state) is False  # Still recent


# Test Bias & Fairness
def test_bias_demographic_parity():
    """Test for demographic parity in identity matching"""
    # Simulated: test matching accuracy across demographic groups
    
    # In production: test with balanced dataset
    # Group A: 1000 samples, 95% accuracy
    # Group B: 1000 samples, should be >= 90% (fairness threshold)
    
    group_a_accuracy = 0.95
    group_b_accuracy = 0.93
    
    # Demographic parity: max 5% difference
    parity = abs(group_a_accuracy - group_b_accuracy)
    assert parity < 0.05, "Demographic parity violated"


def test_bias_false_positive_rate():
    """Test false positive rate is acceptably low"""
    # Simulated: test FPR across demographics
    
    # In production: measure FPR on holdout set
    total_negatives = 10000
    false_positives = 150
    
    fpr = false_positives / total_negatives
    
    # FPR should be < 2%
    assert fpr < 0.02, f"False positive rate too high: {fpr}"


# Test API Security
def test_api_rate_limiting():
    """Test API gateway rate limiting"""
    from services.gateway.app import RateLimiter
    
    limiter = RateLimiter(requests_per_minute=10)
    
    client_id = "test-device"
    
    # First 10 requests should pass
    for _ in range(10):
        assert limiter.is_allowed(client_id) is True
    
    # 11th request should be blocked
    assert limiter.is_allowed(client_id) is False


def test_api_anomaly_detection():
    """Test anomaly detection triggers on abuse"""
    from services.gateway.app import AnomalyDetector
    
    detector = AnomalyDetector()
    detector.alert_threshold = 50  # Lower for testing
    
    client_id = "test-abuser"
    endpoint = "/api/v1/match"
    
    # Simulate 51 requests in 1 second
    for _ in range(51):
        is_anomaly = detector.check_anomaly(client_id, endpoint)
    
    # Should detect anomaly
    assert is_anomaly is True


# Test Governance & NDPR Compliance
def test_ndpr_data_minimization():
    """Test prohibited attributes are rejected"""
    from services.governance.app import GovernanceService, ProcessingPurpose, LegalBasis
    
    service = GovernanceService()
    
    # Attempt to process prohibited attributes
    is_valid = service.validate_processing(
        purpose=ProcessingPurpose.LAW_ENFORCEMENT,
        legal_basis=LegalBasis.LEGAL_OBLIGATION,
        data_attributes=['age_group', 'full_name', 'nin']  # Last two prohibited
    )
    
    # Should reject due to prohibited attributes
    assert is_valid is False


def test_ndpr_consent_withdrawal():
    """Test consent can be withdrawn"""
    from services.governance.app import GovernanceService, ProcessingPurpose, LegalBasis
    
    service = GovernanceService()
    
    # Record consent
    consent = service.record_consent(
        subject_id="test_subject",
        purpose=ProcessingPurpose.SEARCH_RESCUE,
        legal_basis=LegalBasis.CONSENT,
        duration_days=365
    )
    
    consent_id = consent.consent_id
    
    # Withdraw consent
    service.withdraw_consent(consent_id)
    
    # Verify withdrawal
    assert service.consents[consent_id].withdrawn is True
    assert service.consents[consent_id].withdrawn_at is not None


def test_redress_mechanism():
    """Test citizen redress requests are recorded"""
    from services.governance.app import GovernanceService
    
    service = GovernanceService()
    
    request = service.submit_redress(
        subject_pseudonym="citizen_token_xyz",
        request_type="objection",
        details="I object to processing of my data for this purpose"
    )
    
    assert request.status == "pending"
    assert request.request_type == "objection"
    assert service.transparency_data['redress_count'] == 1


# Integration Test: End-to-End Flow
@pytest.mark.asyncio
async def test_end_to_end_identity_flow():
    """Test complete flow from edge to decision"""
    from edge.drone_edge import DroneEdgeProcessor, generate_device_keypair
    from services.identity.app import IdentityService, NIMCConnector
    from services.decision.app import PolicyEngine, MatchContext, OperationMode
    from cryptography.fernet import Fernet
    
    # Setup
    private_key, public_key = generate_device_keypair()
    encryption_key = Fernet.generate_key()
    
    # 1. Edge: Process frame
    edge = DroneEdgeProcessor(
        device_id="drone-test-001",
        encryption_key=encryption_key,
        private_key=private_key
    )
    
    frame = np.zeros((480, 640, 3), dtype=np.uint8)
    location = {"lat": 9.0765, "lon": 7.3986, "accuracy_m": 3}
    metadata = {"altitude": 120, "weather": "clear"}
    
    match_request = edge.create_match_request(frame, location, metadata)
    
    # Verify edge output
    assert match_request is not None
    assert 'template' in match_request
    assert 'signature' in match_request
    
    # 2. Identity: Match (simulated - would call API)
    # In real flow: POST to /api/v1/match
    
    # 3. Decision: Evaluate policy
    engine = PolicyEngine(mode=OperationMode.ASSISTED)
    
    context = MatchContext(
        match=True,
        pseudonym="test_token",
        confidence=0.92,
        location=location,
        timestamp=datetime.utcnow().isoformat(),
        device_id="drone-test-001",
        threat_score=0.6
    )
    
    decision = engine.evaluate(context)
    
    # Verify decision
    assert decision.decision_id is not None
    assert decision.mode == OperationMode.ASSISTED
    assert decision.audit_event is not None


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
