# System Architecture Diagram

## Complete Security AI Platform with Identity Integration

```
┌──────────────────────────────────────────────────────────────────────────────────────────┐
│                                  DATA SOURCES                                             │
├──────────────────────────────────────────────────────────────────────────────────────────┤
│                                                                                           │
│  NetFlow Agents    Email Servers    System Logs    Auth Events    Malware Samples       │
│       │                  │                │              │                │               │
│       └──────────────────┴────────────────┴──────────────┴────────────────┘               │
│                                         │                                                 │
│                                    Kafka Ingestion                                        │
│                                         │                                                 │
└─────────────────────────────────────────┼─────────────────────────────────────────────────┘
                                          │
┌─────────────────────────────────────────┼─────────────────────────────────────────────────┐
│                              CORE ML PIPELINE                                             │
├─────────────────────────────────────────┼─────────────────────────────────────────────────┤
│                                         ▼                                                 │
│                              ┌────────────────────┐                                       │
│                              │   Parsers Layer    │                                       │
│                              │  - NetFlow         │                                       │
│                              │  - Email/Headers   │                                       │
│                              │  - Syslog          │                                       │
│                              └──────────┬─────────┘                                       │
│                                         │                                                 │
│                                         ▼                                                 │
│                              ┌────────────────────┐                                       │
│                              │ Feature Engineering│                                       │
│                              │  - Statistical     │                                       │
│                              │  - Behavioral      │                                       │
│                              │  - Graph (GNN)     │                                       │
│                              │  - Text (BERT)     │                                       │
│                              └──────────┬─────────┘                                       │
│                                         │                                                 │
│                    ┌────────────────────┼─────────────────────┐                          │
│                    ▼                    ▼                     ▼                          │
│            ┌──────────────┐    ┌──────────────┐     ┌──────────────┐                   │
│            │ XGBoost/LGBM │    │  LSTM/BERT   │     │ GraphSAGE    │                   │
│            │  (Tabular)   │    │  (Sequences) │     │   (Graphs)   │                   │
│            └──────┬───────┘    └──────┬───────┘     └──────┬───────┘                   │
│                   │                   │                     │                            │
│                   └───────────────────┼─────────────────────┘                            │
│                                       ▼                                                  │
│                              ┌────────────────────┐                                      │
│                              │  MLflow Registry   │                                      │
│                              │  (Model Versions)  │                                      │
│                              └──────────┬─────────┘                                      │
│                                         │                                                │
│                    ┌────────────────────┼─────────────────────┐                         │
│                    ▼                    ▼                     ▼                         │
│          ┌──────────────┐      ┌──────────────┐     ┌──────────────┐                  │
│          │ NIDS Service │      │ Phishing Svc │     │  Auth Svc    │                  │
│          │  (Port 8080) │      │  (Port 8081) │     │  (Port 8082) │                  │
│          └──────┬───────┘      └──────┬───────┘     └──────┬───────┘                  │
│                 │                     │                     │                           │
│                 └─────────────────────┴─────────────────────┘                           │
│                                       │                                                 │
│                              SIEM / Alerts / Dashboard                                  │
│                                                                                          │
└──────────────────────────────────────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────────────────────────────────────┐
│                        IDENTITY INTEGRATION LAYER (NEW)                                   │
├──────────────────────────────────────────────────────────────────────────────────────────┤
│                                                                                           │
│  ┌─────────────────┐                                                                     │
│  │  Drone Fleet    │  ← Computer Vision AI                                               │
│  │  (Edge Devices) │     - Face detection (Haar/DNN)                                     │
│  └────────┬────────┘     - FaceNet embeddings (128-d)                                    │
│           │              - Privacy filters (blur, TTL=30s)                                │
│           │              - Differential privacy (ε-DP)                                    │
│           │              - Device attestation (RSA-2048)                                  │
│           │                                                                               │
│           │ mTLS (Encrypted Templates)                                                   │
│           ▼                                                                               │
│  ┌─────────────────────────────────────────────────────────────────────┐                │
│  │                      API Gateway (Port 8080)                         │                │
│  │  - JWT Authentication (HS256, 1hr expiration)                       │                │
│  │  - Mutual TLS (device certificates)                                 │                │
│  │  - Rate Limiting (120 req/min per device)                           │                │
│  │  - Anomaly Detection (>100 req/min = alert)                         │                │
│  │  - Security Headers (HSTS, CSP, X-Frame-Options)                    │                │
│  └────┬────────────────────────────┬───────────────────────┬───────────┘                │
│       │                            │                       │                             │
│       ▼                            ▼                       ▼                             │
│  ┌──────────────┐       ┌────────────────┐       ┌──────────────────┐                  │
│  │  Identity    │       │   Decision     │       │   Governance     │                  │
│  │  Matching    │       │   Engine       │       │   (NDPR)         │                  │
│  │ (Port 8081)  │       │  (Port 8082)   │       │  (Port 8084)     │                  │
│  └──────┬───────┘       └───────┬────────┘       └──────────────────┘                  │
│         │                       │                                                        │
│         │ NIMC API              │ Policy Evaluation                                      │
│         │ (Tokenized)           │ (OPA-style)                                            │
│         │                       │                                                        │
│  ┌──────┴───────┐       ┌───────┴─────────┐                                            │
│  │ Pseudonymous │       │ Three Modes:    │                                            │
│  │ Token Only   │       │  1. Observe     │                                            │
│  │ (no raw PII) │       │  2. Assisted    │                                            │
│  │              │       │  3. Automatic   │                                            │
│  │ age_group    │       └───────┬─────────┘                                            │
│  │ state        │               │                                                       │
│  │ voter_status │               ▼                                                       │
│  └──────────────┘       ┌─────────────────────────┐                                    │
│                         │  Approval Workflow      │                                    │
│                         │  (Human-in-the-Loop)    │                                    │
│                         │  - Redacted evidence    │                                    │
│                         │  - 5-min timeout        │                                    │
│                         │  - Operator approval    │                                    │
│                         └───────┬─────────────────┘                                    │
│                                 │                                                       │
│                                 ▼                                                       │
│                         ┌─────────────────────────┐                                    │
│                         │  Traffic Control Plane  │                                    │
│                         │    (ICS/SCADA)          │                                    │
│                         │   (Port 8083)           │                                    │
│                         └───────┬─────────────────┘                                    │
│                                 │                                                       │
│  IEC 62443 Compliant:           │                                                       │
│  ✓ Phase simulation             │                                                       │
│  ✓ Conflict prevention          │                                                       │
│  ✓ 3-sec clearance              │                                                       │
│  ✓ Signed commands              ▼                                                       │
│  ✓ Failsafe (local schedule)   ┌──────────────────────┐                               │
│  ✓ Watchdog (5-min max)         │  Traffic Lights      │                               │
│                                  │  (Intersections)     │                               │
│                                  │  - igy-12            │                               │
│                                  │  - lag-01            │                               │
│                                  └──────────────────────┘                               │
│                                                                                          │
│  ┌──────────────────────────────────────────────────────────────────────────┐          │
│  │                    Immutable Audit Log (WORM Storage)                     │          │
│  │  - Cryptographic hash chain (SHA-256)                                     │          │
│  │  - Tamper detection (Merkle tree)                                         │          │
│  │  - 7-year retention                                                        │          │
│  │  - Records: device_id, operator, timestamp, decision, action, confidence │          │
│  └──────────────────────────────────────────────────────────────────────────┘          │
│                                                                                          │
└──────────────────────────────────────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────────────────────────────────────┐
│                           INFRASTRUCTURE & STORAGE                                        │
├──────────────────────────────────────────────────────────────────────────────────────────┤
│                                                                                           │
│  Redis (Online Features)    Postgres (Metadata)    ClickHouse (Queries)                 │
│                                                                                           │
│  S3/MinIO (Raw Data + Models)        Elasticsearch (Logs + SIEM)                        │
│                                                                                           │
│  Prometheus (Metrics)    Grafana (Dashboards)    ELK Stack (Observability)              │
│                                                                                           │
│  Docker Compose (Dev)    Kubernetes (Production)    Helm Charts (Deployment)            │
│                                                                                           │
└──────────────────────────────────────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────────────────────────────────────┐
│                        GOVERNMENT AGENCY INTEGRATIONS (NEW)                               │
├──────────────────────────────────────────────────────────────────────────────────────────┤
│                                                                                           │
│  ┌─────────────────────────────────────────────────────────────────────────┐            │
│  │  INEC - Independent National Electoral Commission (Port 8085)            │            │
│  │  ─────────────────────────────────────────────────────────────────────  │            │
│  │  Services:                                                                │            │
│  │  ✓ Privacy-preserving voter verification (tokenized matching)           │            │
│  │  ✓ Polling unit status and queue management                              │            │
│  │  ✓ Accessibility assistance for disabled voters                          │            │
│  │                                                                           │            │
│  │  Privacy Guarantees:                                                      │            │
│  │  • Unlinkable pseudonyms (SHA-256 + salt)                               │            │
│  │  • NO PII in responses (no name, address, VIN)                           │            │
│  │  • Returns: is_registered, polling_unit_id ONLY                          │            │
│  │  • Tokens expire 24h after election                                      │            │
│  │                                                                           │            │
│  │  Legal Framework: Electoral Act 2022, NDPR 2019                          │            │
│  └─────────────────────────────────────────────────────────────────────────┘            │
│                                                                                           │
│  ┌─────────────────────────────────────────────────────────────────────────┐            │
│  │  Federal Fire Service (Port 8086)                                        │            │
│  │  ─────────────────────────────────────────────────────────────────────  │            │
│  │  Services:                                                                │            │
│  │  ✓ Fire/smoke detection from drones and cameras                         │            │
│  │  ✓ GPS alerting with incident location                                   │            │
│  │  ✓ Authenticated notification to nearest command center                  │            │
│  │  ✓ Emergency call fallbacks (112 / fire contact)                        │            │
│  │                                                                           │            │
│  │  Automation:                                                              │            │
│  │  • HIGH/CRITICAL severity → auto-notify Fire Service                    │            │
│  │  • Image templates (not raw images) for faster dispatch                 │            │
│  │  • Real-time incident tracking                                           │            │
│  │                                                                           │            │
│  │  Integration: Drone computer vision → Fire Service dispatch API          │            │
│  └─────────────────────────────────────────────────────────────────────────┘            │
│                                                                                           │
│  ┌─────────────────────────────────────────────────────────────────────────┐            │
│  │  Nigeria Police Force (Port 8087)                                        │            │
│  │  ─────────────────────────────────────────────────────────────────────  │            │
│  │  Services:                                                                │            │
│  │  ✓ High-confidence security alerts to Situation Room                    │            │
│  │  ✓ Kidnapping detection, armed robbery alerts                            │            │
│  │  ✓ MANDATORY analyst review before dispatch                              │            │
│  │  ✓ Rapid response coordination                                           │            │
│  │                                                                           │            │
│  │  Human-in-the-Loop Enforcement:                                           │            │
│  │  • ALL dispatches require analyst approval                               │            │
│  │  • Confidence threshold: 0.8+ triggers review                            │            │
│  │  • Analysts can approve/reject/escalate                                  │            │
│  │  • False positives tracked for model improvement                         │            │
│  │                                                                           │            │
│  │  Threat Types: Kidnapping, armed robbery, terrorism, suspicious activity │            │
│  └─────────────────────────────────────────────────────────────────────────┘            │
│                                                                                           │
│  ┌─────────────────────────────────────────────────────────────────────────┐            │
│  │  Social Media Regulation (Port 8088)                                     │            │
│  │  ─────────────────────────────────────────────────────────────────────  │            │
│  │  Services:                                                                │            │
│  │  ✓ AI-powered content moderation (hate speech, disinformation)          │            │
│  │  ✓ Cybercrime Act compliance (terrorism, child exploitation)            │            │
│  │  ✓ Takedown recommendations with MANDATORY human review                  │            │
│  │  ✓ Law enforcement reporting for serious violations                      │            │
│  │                                                                           │            │
│  │  Violation Detection:                                                     │            │
│  │  • Hate speech (Cybercrime Act Section 24)                               │            │
│  │  • Disinformation (election interference)                                │            │
│  │  • Violent content / terrorism (Section 26)                              │            │
│  │  • Child exploitation (Section 23) → immediate Police report             │            │
│  │                                                                           │            │
│  │  Compliance: Nigeria Cybercrime Act 2015, NDPR 2019                      │            │
│  └─────────────────────────────────────────────────────────────────────────┘            │
│                                                                                           │
└──────────────────────────────────────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────────────────────────────────────┐
│                          GOVERNANCE & OVERSIGHT                                           │
├──────────────────────────────────────────────────────────────────────────────────────────┤
│                                                                                           │
│  Multi-Stakeholder Oversight Board:                                                      │
│  - Government (NIMC, INEC, Fire Service, Police, Transport Authority)                   │
│  - Civil Society (Privacy advocates, legal experts)                                      │
│  - Technical (Security researchers, AI ethics)                                           │
│  - Community (Local government representatives)                                          │
│                                                                                           │
│  Responsibilities:                                                                        │
│  ✓ Review transparency reports (quarterly)                                               │
│  ✓ Investigate complaints and redress requests                                          │
│  ✓ Approve policy changes                                                                │
│  ✓ Audit system access and usage                                                         │
│                                                                                           │
│  Public Transparency Reports:                                                             │
│  - Total identity checks performed                                                       │
│  - Breakdown by purpose (elections, fire, police, traffic)                              │
│  - False positive rate and bias metrics                                                  │
│  - Redress requests (submitted, resolved)                                                │
│  - Enforcement actions taken                                                             │
│  - Agency integration statistics (INEC, Fire, Police, Social Media)                     │
│                                                                                           │
└──────────────────────────────────────────────────────────────────────────────────────────┘

KEY PRINCIPLES:
✓ Privacy by design (no raw PII, tokenized matching)
✓ Human oversight (approval workflows, operator review)
✓ Safety-critical control (ICS compliance, failsafes)
✓ Legal compliance (NDPR, purpose limitation, data minimization)
✓ Full auditability (immutable logs, transparency)
✓ Security hardening (mTLS, JWT, rate limiting, HSM-ready)
```

## Data Flow Examples

### Example 1: Identity Match (Assisted Mode)

```
1. Drone captures frame
   ↓ (local processing)
2. Face detected, 128-d embedding extracted
   ↓ (privacy filter)
3. Video blurred, deleted after 30s
   ↓ (encryption)
4. Template encrypted (AES-256)
   ↓ (mTLS)
5. API Gateway: JWT auth + rate limit check
   ↓
6. Identity Service: NIMC tokenized match
   → Match: YES, Pseudonym: "nimc_token_xyz", Confidence: 0.94
   ↓
7. Decision Engine: Policy evaluation
   → Threat score: 0.7 (high)
   → Action: TRAFFIC_CONTROL
   → Requires approval: YES
   ↓
8. Approval Workflow: Operator notified
   → Operator reviews: location, confidence, redacted image
   → Operator approves within 5 minutes
   ↓
9. Traffic Control: Signed command sent
   → Safety checks: PASS (no conflicts, simulation OK)
   → Phase changed: PEDESTRIAN_CROSSING (30 seconds)
   ↓
10. Audit Log: Immutable record created
    → event_id, operator_id, timestamp, decision, action
    → Cryptographic hash chain updated
```

### Example 2: Privacy Safeguards

```
What's Collected:           What's NEVER Stored:
✓ Face embedding (128 floats)   ✗ Raw video/images
✓ GPS coordinates               ✗ Full name
✓ Timestamp                     ✗ National ID number (NIN)
✓ Confidence score              ✗ Address
                                ✗ Phone number

What's Returned from NIMC:
✓ Pseudonymous token (unlinkable)
✓ Match confidence
✓ Allowed attributes only (age_group, state, voter_status)
✗ NO personally identifiable information
```

## Security Layers

```
Layer 1: Edge Security
- Device attestation (TPM, RSA signatures)
- Local privacy filters (blur, TTL)
- Encrypted templates only

Layer 2: Network Security
- mTLS (certificate-based)
- TLS 1.3 (all connections)
- Network segmentation

Layer 3: API Security
- JWT authentication
- Rate limiting (120/min)
- Anomaly detection

Layer 4: Data Security
- AES-256 encryption
- NO raw PII storage
- Minimal retention (30-90 days)

Layer 5: Audit Security
- Immutable logs (WORM)
- Hash chain integrity
- 7-year retention
```
