# Government Agency Integration Guide
## Security AI Platform - Agency Partnerships

This guide provides comprehensive documentation for government agency integrations with the Security AI Platform.

**Last Updated**: November 27, 2025  
**Version**: 1.0.0

---

## 📋 Overview

The Security AI Platform provides privacy-preserving services to four government agencies:

1. **INEC** (Independent National Electoral Commission) - Voter verification
2. **Federal Fire Service** - Fire/smoke detection and alerting
3. **Nigeria Police Force** - Security threat detection and response
4. **Social Media Platforms** - Content moderation and Cybercrime Act compliance

All integrations follow privacy-by-design principles with:
- Tokenized matching (no raw PII)
- Human-in-the-loop oversight
- NDPR compliance
- Immutable audit trails

---

## 🗳️ INEC Integration

### Service Overview

**Port**: 8085  
**Purpose**: Privacy-preserving voter verification for election assistance  
**Legal Framework**: Electoral Act 2022, NDPR 2019

### API Endpoints

#### 1. Voter Verification
```http
POST /api/v1/verify
Content-Type: application/json

{
  "token": "sha256_hashed_credentials_with_salt",
  "polling_unit_hint": "LA/09/05/001"
}
```

**Response**:
```json
{
  "match": true,
  "pseudonym": "inec_token_abc123",
  "status": "registered",
  "allowed_attributes": {
    "is_registered": true,
    "polling_unit_id": "LA/09/05/001",
    "polling_unit_name": "Obalende Primary School"
  },
  "confidence": 0.94
}
```

**Privacy Guarantee**: NO PII in response (no name, address, VIN, phone, email)

#### 2. Polling Unit Status
```http
GET /api/v1/polling-unit/{polling_unit_id}
```

**Response**:
```json
{
  "polling_unit_id": "LA/09/05/001",
  "name": "Obalende Primary School",
  "status": "open",
  "queue_count": 45,
  "estimated_wait_min": 30,
  "updated_at": "2025-11-27T14:30:00Z"
}
```

#### 3. Record Vote (Prevent Double Voting)
```http
POST /api/v1/vote/record

{
  "pseudonym": "inec_token_abc123",
  "polling_unit_id": "LA/09/05/001"
}
```

#### 4. Accessibility Assistance
```http
POST /api/v1/accessibility/request

{
  "pseudonym": "inec_token_abc123",
  "assistance_type": "wheelchair",
  "polling_unit_id": "LA/09/05/001"
}
```

### Security Controls

| Control | Implementation |
|---------|----------------|
| **Authentication** | mTLS + JWT (INEC state offices only) |
| **Rate Limiting** | 1000 requests/hour per office |
| **IP Whitelisting** | INEC HQ + 36 state offices |
| **Encryption** | TLS 1.3 (transit), AES-256 (rest) |
| **Audit Logging** | All verifications logged (immutable) |

### Data Retention

- **Voter Tokens**: Deleted 24 hours after polls close
- **API Logs**: 30 days
- **Audit Trails**: 1 year (legal requirement)

### MOU Reference

See `legal/INEC_MOU.md` for complete Memorandum of Understanding

---

## 🔥 Federal Fire Service Integration

### Service Overview

**Port**: 8086  
**Purpose**: Automated fire/smoke detection and emergency response  
**Integration**: Drone/camera computer vision → Fire Service dispatch

### API Endpoints

#### 1. Report Fire Detection
```http
POST /api/v1/detect

{
  "detection_id": "fire-det-001",
  "device_id": "drone-fire-001",
  "timestamp": "2025-11-27T14:30:00Z",
  "location": {
    "lat": 9.0765,
    "lon": 7.3986,
    "accuracy_m": 5,
    "altitude_m": 150
  },
  "severity": "high",
  "confidence": 0.92,
  "metadata": {
    "smoke_density": "high",
    "flame_detected": true,
    "wind_speed_kmh": 15,
    "temperature_c": 35
  }
}
```

**Auto-Notification**: HIGH/CRITICAL severity incidents automatically notify nearest Fire Service station

#### 2. Send Notification (Manual)
```http
POST /api/v1/incidents/{incident_id}/notify
```

Sends authenticated notification to Fire Service with:
- GPS coordinates
- Severity level
- Image template (compressed/encrypted)
- Estimated response time
- Contact numbers (112 / station)

#### 3. Update Incident Status
```http
POST /api/v1/incidents/{incident_id}/status

{
  "status": "dispatched",
  "details": {
    "units_dispatched": 2,
    "eta_minutes": 8
  }
}
```

#### 4. List Active Incidents
```http
GET /api/v1/incidents?active_only=true
```

### Automation Rules

| Severity | Action | Notification |
|----------|--------|--------------|
| **CRITICAL** | Auto-notify Fire Service | Immediate |
| **HIGH** | Auto-notify Fire Service | Within 1 minute |
| **MEDIUM** | Flag for operator review | Manual approval |
| **LOW** | Log only | No notification |

### Emergency Contacts

- **National Emergency**: 112
- **Fire Service HQ (FCT)**: +234-9-234-1234
- **Lagos Fire Service**: +234-1-775-0018, 767

### Integration Flow

```
Drone/Camera → Fire Detection AI → API (Port 8086) → Fire Service Dispatch
                 (Confidence > 0.7)     (Auto-notify if HIGH/CRITICAL)
```

---

## 🚔 Nigeria Police Force Integration

### Service Overview

**Port**: 8087  
**Purpose**: High-confidence security alerts with mandatory analyst review  
**Critical**: ALL dispatches require human approval

### API Endpoints

#### 1. Submit Security Alert
```http
POST /api/v1/alerts

{
  "threat_type": "kidnapping",
  "severity": "high",
  "confidence": 0.89,
  "timestamp": "2025-11-27T15:00:00Z",
  "location": {
    "lat": 9.0765,
    "lon": 7.3986,
    "accuracy_m": 10
  },
  "description": "Suspicious vehicle following school bus for 15 minutes",
  "detected_by": "traffic-cam-045",
  "evidence": {
    "vehicle_plate": "ABC-123-XY",
    "duration_minutes": 15,
    "erratic_behavior": true
  }
}
```

**Auto-Escalation**: Confidence ≥ 0.9 + CRITICAL severity → immediate analyst review

#### 2. Analyst Review (MANDATORY)
```http
POST /api/v1/incidents/{incident_id}/review

{
  "analyst_id": "analyst-001",
  "decision": "approve_dispatch",
  "confidence_override": 0.95,
  "notes": "Verified vehicle plate matches kidnapping suspect profile",
  "recommended_action": "Dispatch Anti-Kidnapping Unit to intercept on Lagos-Ibadan Expressway"
}
```

**Analyst Decisions**:
- `approve_dispatch` - Authorize police response
- `false_positive` - Reject as false alarm
- `escalate` - Escalate to senior analyst
- `need_more_info` - Request additional evidence

#### 3. Dispatch Police Units
```http
POST /api/v1/incidents/{incident_id}/dispatch

{
  "priority": "emergency"  // routine | urgent | emergency
}
```

**SAFETY CHECK**: Only allowed after analyst approval (status = APPROVED)

#### 4. List Pending Reviews
```http
GET /api/v1/incidents?pending_review=true
```

Returns all incidents awaiting analyst review

### Threat Types

| Threat Type | Auto-Review Threshold | Specialization |
|-------------|----------------------|----------------|
| **Kidnapping** | Confidence ≥ 0.8 | Anti-Kidnapping Unit |
| **Armed Robbery** | Confidence ≥ 0.8 | Anti-Robbery Squad |
| **Terrorism** | Confidence ≥ 0.7 | Intelligence/DSS |
| **Suspicious Activity** | Confidence ≥ 0.9 | General patrol |

### Human-in-the-Loop Safeguards

1. **No Automated Dispatch**: All police responses require analyst approval
2. **Confidence Thresholds**: Minimum 0.6 for alert creation, 0.8 for review
3. **False Positive Tracking**: Rejected alerts improve model accuracy
4. **Analyst Authorization**: Only authorized Police analysts can approve dispatch

### Emergency Contacts

- **National Emergency**: 112
- **Police Force HQ**: +234-9-461-0000
- **Lagos Police Command**: +234-1-794-5555

---

## 📱 Social Media Regulation

### Service Overview

**Port**: 8088  
**Purpose**: Content moderation with Cybercrime Act compliance  
**Critical**: Mandatory human review before enforcement actions

### API Endpoints

#### 1. Submit Content for Moderation
```http
POST /api/v1/moderate

{
  "platform": "Twitter",
  "content_type": "post",
  "text": "Example tweet text",
  "author_id": "user_abc123",  // Pseudonymous, no PII
  "timestamp": "2025-11-27T10:00:00Z",
  "metadata": {
    "reach": 5000,
    "engagement": 120
  }
}
```

**Response**:
```json
{
  "record_id": "REC-20251127-ABC12345",
  "ai_moderation": {
    "violation_type": "hate_speech",
    "confidence": 0.85,
    "recommended_action": "flag_review",
    "explanation": "Detected hate speech patterns: ethnic slur, religious hate",
    "severity_score": 0.9,
    "requires_human_review": true,
    "cybercrime_act_sections": ["Section 24 - Cyberstalking"]
  },
  "status": "pending"
}
```

#### 2. Moderator Review
```http
POST /api/v1/review/{content_id}

{
  "moderator_id": "mod-001",
  "decision": "takedown_ordered",
  "action_taken": "hard_delete",
  "justification": "Confirmed hate speech violating Section 24 of Cybercrime Act",
  "legal_basis": "Cybercrime (Prohibition, Prevention, etc.) Act 2015, Section 24"
}
```

**Review Decisions**:
- `approved` - Content acceptable
- `rejected` - False positive
- `escalated` - Escalate to senior moderator
- `takedown_ordered` - Remove content

**Actions**:
- `approve` - No action
- `soft_delete` - Hide but preserve
- `hard_delete` - Permanent removal
- `shadowban` - Reduce visibility
- `account_suspend` - Suspend user
- `report_law_enforcement` - Notify Police

#### 3. Compliance Report
```http
GET /api/v1/compliance/report
```

**Response**:
```json
{
  "report_date": "2025-11-27T12:00:00Z",
  "total_content_moderated": 15000,
  "violations_detected": 450,
  "human_reviews_conducted": 420,
  "takedowns_executed": 380,
  "law_enforcement_reports": 10,
  "violation_breakdown": {
    "hate_speech": 200,
    "disinformation": 150,
    "violent_content": 50,
    "harassment": 40,
    "fraud": 8,
    "terrorism": 2
  },
  "compliance_rate": "93.3%",
  "legal_framework": "Nigeria Cybercrime Act 2015"
}
```

### Cybercrime Act Violations

| Violation | Cybercrime Act Section | Response Timeline |
|-----------|------------------------|-------------------|
| **Child Exploitation** | Section 23 | Immediate Police report (no delay) |
| **Terrorism** | Section 26 | Within 1 hour to DSS + Police |
| **Hate Speech** | Section 24 | Within 24 hours |
| **Fraud/Identity Theft** | Section 22 | Within 48 hours |

### Law Enforcement Reporting

For serious violations:

```http
GET /api/v1/compliance/law-enforcement
```

Returns all content reported to Police/DSS with:
- Content snapshot
- Metadata (timestamp, IP address)
- Evidence package (encrypted)
- Moderator justification

### Privacy Considerations

- **Author IDs**: Pseudonymous only (no real names)
- **Content Preservation**: 90 days minimum (legal requirement)
- **Evidence Chain**: Cryptographic hashes, tamper-proof

---

## 🔒 Cross-Cutting Security Controls

### Authentication

All agency integrations use:

| Layer | Mechanism |
|-------|-----------|
| **Transport** | TLS 1.3 (minimum) |
| **Device** | mTLS (certificate-based) |
| **User** | JWT tokens (HS256, 1hr expiration) |
| **Authorization** | Role-based access control (RBAC) |

### Rate Limiting

| Agency | Rate Limit | Burst |
|--------|------------|-------|
| **INEC** | 1000 req/hour per office | 100/min |
| **Fire Service** | 500 req/hour | 50/min |
| **Police** | 2000 req/hour | 200/min |
| **Social Media** | 10000 req/hour | 1000/min |

### Audit Logging

All agency API calls logged with:
- Request timestamp
- Agency/user ID
- API endpoint
- Request/response data (redacted PII)
- Response status
- Cryptographic hash (SHA-256)

**Retention**: 1 year (immutable, append-only)

### Encryption

- **In Transit**: TLS 1.3
- **At Rest**: AES-256-GCM
- **Tokenization**: SHA-256 with salt
- **Digital Signatures**: RSA-2048 or Ed25519

---

## 📊 Monitoring and Observability

### Metrics (Prometheus)

All services expose metrics at `/metrics`:

- `api_requests_total` (counter) - Total API requests
- `api_request_duration_seconds` (histogram) - Request latency
- `api_errors_total` (counter) - Error count
- `confidence_score` (histogram) - ML confidence distribution
- `human_reviews_pending` (gauge) - Pending analyst reviews

### Dashboards (Grafana)

Pre-configured dashboards:
1. **INEC Dashboard**: Voter verifications, queue status, accessibility requests
2. **Fire Service Dashboard**: Active incidents, response times, severity distribution
3. **Police Dashboard**: Pending reviews, dispatch times, false positive rate
4. **Social Media Dashboard**: Content moderated, takedowns, law enforcement reports

### Alerts

Critical alerts configured:
- API error rate > 5%
- Response time > 5 seconds (P99)
- Pending reviews > 50 (Police/Social Media)
- High-severity incidents unacknowledged > 10 minutes (Fire Service)

---

## 🚀 Deployment

### Development

```powershell
# Start all agency services
cd services

# INEC
cd inec; uvicorn app:app --port 8085 --reload; cd ..

# Fire Service
cd fire; uvicorn app:app --port 8086 --reload; cd ..

# Police
cd police; uvicorn app:app --port 8087 --reload; cd ..

# Social Media
cd social_media; uvicorn app:app --port 8088 --reload; cd ..
```

### Production (Kubernetes)

```yaml
# Helm deployment
helm install security-ai-agencies ./infra/k8s/agencies \
  --set inec.enabled=true \
  --set fire.enabled=true \
  --set police.enabled=true \
  --set socialMedia.enabled=true \
  --set monitoring.enabled=true
```

### Health Checks

All services expose `/health`:

```http
GET /health

Response:
{
  "status": "healthy",
  "service": "inec-integration",
  "pending_reviews": 5,
  "total_verifications": 12450
}
```

---

## 📞 Support and Contacts

### Technical Support

| Agency | Email | Phone |
|--------|-------|-------|
| **INEC** | inec-support@securityai.gov.ng | +234-9-XXXX-XXXX |
| **Fire Service** | fire-support@securityai.gov.ng | +234-9-XXXX-XXXX |
| **Police** | police-support@securityai.gov.ng | +234-9-XXXX-XXXX |
| **Social Media** | moderation-support@securityai.gov.ng | +234-9-XXXX-XXXX |

### Emergency Escalation

- **24/7 Hotline**: +234-9-XXXX-XXXX
- **Security Incidents**: security@securityai.gov.ng
- **Data Breach**: dpo@securityai.gov.ng (within 72 hours)

### Legal Inquiries

- **General Legal**: legal@securityai.gov.ng
- **Data Protection Officer**: dpo@securityai.gov.ng
- **Compliance Officer**: compliance@securityai.gov.ng

---

## 📚 Additional Documentation

- **API Specifications**: `docs/API.md`
- **Legal MOUs**: `legal/` directory
  - `INEC_MOU.md` - INEC partnership agreement
  - `NDPR_CHECKLIST.md` - Privacy compliance
  - `CYBERCRIME_COMPLIANCE.md` - Cybercrime Act compliance
- **Architecture**: `docs/ARCHITECTURE.md` (updated with agency integrations)
- **Deployment**: `docs/DEPLOYMENT.md`
- **Quickstart**: `docs/QUICKSTART_IDENTITY.md`

---

*This guide is a living document. Please report issues or suggest improvements to: docs@securityai.gov.ng*

*Version: 1.0.0*  
*Last Updated: November 27, 2025*
