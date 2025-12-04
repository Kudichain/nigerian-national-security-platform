# Memorandum of Understanding (MOU)
## INEC Voter Verification Service

**Between:**
1. **Independent National Electoral Commission (INEC)**  
   Electoral Commission HQ, Constitution Avenue, Central Business District, Abuja  
   ("Data Controller" / "INEC")

2. **Security AI Platform**  
   [Organization Address]  
   ("Data Processor" / "Platform")

**Effective Date**: [Date]  
**Term**: 2 years (renewable)

---

## 1. Purpose

This MOU establishes the terms for privacy-preserving voter verification services to assist INEC electoral officers during elections, using tokenized identity matching that protects voter privacy while enabling:

- Voter registration status verification
- Polling unit assignment confirmation
- Queue management assistance
- Accessibility support for disabled voters

**CRITICAL**: This service is **assistive only** and does NOT replace BVAS or manual ballot procedures.

---

## 2. Scope of Services

### 2.1 Services Provided
The Platform shall provide:

1. **Voter Verification API** (Port 8085)
   - Input: Tokenized voter credentials (no raw PII)
   - Output: Registration status, polling unit ID (no name/address/VIN)
   - Method: Unlinkable pseudonymous matching

2. **Polling Unit Status**
   - Real-time queue counts from drone/camera analytics
   - Wait time estimation
   - Crowd density monitoring

3. **Accessibility Assistance**
   - Requests for disabled voter support
   - Special needs flagging
   - Priority queue management

### 2.2 Services NOT Provided
The Platform shall NOT:
- Replace BVAS or official voter verification
- Store raw voter registry data
- Provide names, addresses, or VINs in API responses
- Enable vote-buying or voter intimidation
- Process actual votes or ballot information

---

## 3. Data Processing Terms

### 3.1 Tokenized Matching Protocol

**Input**: 
```json
{
  "token": "sha256_hash_with_salt",
  "polling_unit_hint": "LA/09/05/001"
}
```

**Output**:
```json
{
  "match": true,
  "pseudonym": "inec_token_abc123",
  "allowed_attributes": {
    "is_registered": true,
    "polling_unit_id": "LA/09/05/001",
    "polling_unit_name": "Obalende Primary School"
  },
  "confidence": 0.94
}
```

**Prohibited in Output**:
- Full name
- Residential address
- Voter Identification Number (VIN)
- Telephone number
- Email address
- Biometric templates

### 3.2 Privacy Guarantees

1. **No Raw PII**: Platform never receives or stores raw voter data
2. **Unlinkable Pseudonyms**: SHA-256 hashed tokens prevent re-identification
3. **Purpose Limitation**: Tokens valid only for voter verification
4. **Time Limitation**: Tokens expire after election day
5. **Minimal Attributes**: Only `is_registered` and `polling_unit_id` returned

### 3.3 Data Retention

- **API Logs**: 30 days maximum (for audit purposes)
- **Verification Tokens**: Deleted within 24 hours after polls close
- **Pseudonymous Records**: Deleted within 7 days post-election
- **Audit Trails**: Retained 1 year (immutable, append-only)

---

## 4. Security Controls

### 4.1 Technical Safeguards

| Control | Requirement |
|---------|-------------|
| **Encryption in Transit** | TLS 1.3 minimum |
| **Encryption at Rest** | AES-256-GCM |
| **Authentication** | mTLS + JWT tokens |
| **API Rate Limiting** | 1000 requests/hour per INEC office |
| **IP Whitelisting** | INEC headquarters + state offices only |
| **Audit Logging** | All API calls logged (immutable) |

### 4.2 Access Controls

- **INEC Access**: Authorized electoral officers only (via SSO)
- **Platform Access**: Minimum 2-person authorization for system changes
- **Audit Access**: INEC + Platform compliance officers (read-only)

### 4.3 Operator Approval

- **Automated Verification**: Allowed for routine checks
- **Exception Cases**: Require human electoral officer approval
- **Dispute Resolution**: INEC electoral officer has final authority

---

## 5. Compliance

### 5.1 Legal Framework

This MOU complies with:

1. **Nigeria Data Protection Regulation (NDPR) 2019**
   - Lawful basis: Public interest (election administration)
   - Data minimization: Only essential attributes shared
   - Purpose limitation: Voter verification only

2. **Electoral Act 2022**
   - Section 47: Voter privacy protection
   - Section 52: Polling unit procedures
   - Section 65: Accessibility requirements

3. **Freedom of Information (FOI) Act 2011**
   - Transparency in election technology

### 5.2 Privacy Impact Assessment

A full Privacy Impact Assessment (PIA) has been completed and approved by:
- INEC Legal Department
- Platform Data Protection Officer
- NITDA (pending review)

### 5.3 Audit Rights

INEC reserves the right to:
- Audit Platform systems quarterly
- Review API logs on-demand
- Inspect security controls
- Test for PII leakage

---

## 6. Incident Response

### 6.1 Data Breach Notification

Platform must notify INEC within **72 hours** of:
- Unauthorized access to voter tokens
- PII exposure (if any)
- System compromise
- Anomalous verification patterns

### 6.2 Breach Response Procedures

1. Immediate containment (disable API if necessary)
2. Forensic investigation
3. INEC + NITDA notification
4. Voter notification (if PII exposed)
5. Remediation plan
6. Post-incident report

---

## 7. Operational Procedures

### 7.1 Pre-Election Setup

- **T-30 days**: API credentials issued to INEC state offices
- **T-14 days**: Integration testing
- **T-7 days**: Security audit
- **T-1 day**: Final readiness check

### 7.2 Election Day Operations

- **24/7 support**: Platform engineering team on standby
- **Incident hotline**: +234-9-XXXX-XXXX
- **Backup procedures**: Manual verification if API unavailable

### 7.3 Post-Election Cleanup

- **T+1 day**: Disable API access
- **T+7 days**: Delete verification tokens
- **T+30 days**: Final audit report to INEC

---

## 8. Intellectual Property

### 8.1 Ownership

- **Voter Data**: INEC retains all rights
- **Platform Code**: Platform retains ownership
- **API Integration**: Joint ownership (for INEC-specific customizations)

### 8.2 Open Source

Platform commits to open-sourcing:
- Tokenization protocols (for transparency)
- Privacy-preserving matching algorithms
- Audit logging framework

---

## 9. Limitations of Liability

### 9.1 Platform Liability

Platform liable for:
- Unauthorized PII disclosure (due to Platform negligence)
- Security breaches (due to inadequate controls)
- API downtime > 4 hours on election day

Platform NOT liable for:
- INEC misuse of API
- Third-party attacks (beyond industry-standard defenses)
- Force majeure (natural disasters, etc.)

### 9.2 INEC Liability

INEC liable for:
- Misuse of API credentials
- Unauthorized data sharing by INEC staff
- Voter intimidation using Platform data

---

## 10. Term and Termination

### 10.1 Initial Term
- **Duration**: 2 years from signing
- **Renewal**: Automatic unless either party objects (90 days notice)

### 10.2 Termination Conditions

Either party may terminate for:
- Material breach (30 days cure period)
- Legal non-compliance
- Mutual agreement

### 10.3 Data Deletion on Termination

Upon termination:
- Platform deletes all voter tokens within **24 hours**
- INEC revokes API credentials immediately
- Audit logs retained 1 year (legal requirement)
- Final compliance report delivered to INEC

---

## 11. Dispute Resolution

### 11.1 Escalation Path

1. **Technical Issues**: Platform CTO + INEC IT Director
2. **Privacy Concerns**: DPOs (both parties)
3. **Legal Disputes**: Legal counsel (both parties)
4. **Final Authority**: NITDA mediation

### 11.2 Arbitration

Unresolved disputes subject to arbitration under Nigerian law.

---

## 12. Amendments

This MOU may be amended by:
- Written agreement of both parties
- NITDA directive (compliance updates)
- Legislative changes (Electoral Act, NDPR)

---

## 13. Signatures

**For INEC:**

_____________________________  
Name: [INEC Chairman]  
Title: Chairman, INEC  
Date: _______________

**For Security AI Platform:**

_____________________________  
Name: [Platform CEO]  
Title: Chief Executive Officer  
Date: _______________

**Witnessed by:**

_____________________________  
Name: [Legal Counsel]  
Title: Data Protection Officer  
Date: _______________

---

## Appendices

### Appendix A: API Specification
See `docs/API.md` - INEC Voter Verification Endpoints

### Appendix B: Tokenization Protocol
See `legal/TOKENIZATION_PROTOCOL.md`

### Appendix C: Privacy Impact Assessment
See `legal/PIA_TEMPLATE.md` (completed for INEC integration)

### Appendix D: Security Controls Matrix
See `docs/DEPLOYMENT.md` - Security Controls section

---

*This MOU is governed by the laws of the Federal Republic of Nigeria.*

*Version: 1.0.0*  
*Last Updated: November 27, 2025*
