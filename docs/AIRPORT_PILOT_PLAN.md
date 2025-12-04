# Airport Pilot Deployment Plan

## Executive Summary

90-day regulatory sandbox pilot at Murtala Muhammed International Airport (MMIA) Lagos, deploying privacy-first AI surveillance with human-in-the-loop controls. Phased approach from observe-only to assisted mode, with third-party audits before production scale.

**Pilot Duration:** 10 weeks (9 weeks active + 1 week audit)  
**Location:** MMIA Lagos Terminal 2 (expandable to Abuja FCT)  
**Authorization:** FAAN formal approval secured  
**Compliance:** NDPR 2019, NCC IoT Guidelines, IEC 62443 (ICS safety)

---

## Pilot Phases

### Phase 1: Airport Selection & Authorization (Week 0)

**Objective:** Secure formal permissions and access

**Tasks:**
1. ✅ Select pilot airport: MMIA Lagos Terminal 2
2. ✅ Obtain formal authorization letter from FAAN
3. ✅ Sign Memorandum of Understanding (MOU) with airport manager
4. ⏳ Issue vendor access credentials (airside & IT infrastructure)

**Deliverables:**
- Signed MOU with FAAN
- Data Sharing Agreement (DSA) with airport authority
- Vendor access credentials (badge, VPN, API keys)

**Responsible:** Legal team + Airport liaison officer

---

### Phase 2: Edge Gateway Deployment (Week 1)

**Objective:** Install and configure edge infrastructure

**Tasks:**
1. Install Edge Gateway in secure communications room (UPS-backed)
2. Connect to 3–5 existing security cameras (Terminal 2 entrance, baggage, gates)
3. Configure drone corridor monitoring (one approach path)
4. Verify TPM attestation on edge device
5. Test redundant power supply & UPS failover (4-hour battery backup)
6. Establish private APN/VPN link with QoS guarantees from MTN/Airtel

**Deliverables:**
- Edge hardware operational with TPM attestation
- Network link with <50ms latency, <0.1% packet loss
- UPS backup verified (4-hour runtime)

**Responsible:** DevOps + Airport IT team

---

### Phase 3: Observe-Only Mode (Weeks 1–4)

**Objective:** Baseline AI performance, tune thresholds, no automated actions

**Tasks:**
1. Run AI detection models (person detection, behavior analysis, object classification)
2. Send alerts to airport security via SMS/email (no camera control)
3. Collect baseline metrics: precision, recall, false positive rate
4. Tune detection thresholds weekly based on feedback
5. Weekly stakeholder briefings (airport security, FAAN, privacy officer)

**Success Criteria:**
- Precision @ top-k >90%
- False positive rate <10% (tuned from initial 20%)
- Zero security incidents caused by system

**Deliverables:**
- Baseline performance report (precision, recall, latency)
- Tuned detection thresholds
- Operator feedback log

**Responsible:** ML team + Airport security chief

---

### Phase 4: Assisted Mode (Weeks 5–8)

**Objective:** Enable human-in-the-loop controls with operator approval

**Tasks:**
1. Enable case creation workflow in Decision Engine (port 8082)
2. Operator-approved PTZ camera control on selected cameras (3 total)
3. Track operational metrics:
   - **MTTV (Mean Time to Verify):** Target <60 seconds
   - **MTTA (Mean Time to Action):** Target <5 minutes
4. Test dual authorization for CRITICAL actions (e.g., locking down a gate)
5. Daily operator training sessions + SOP reviews

**Success Criteria:**
- MTTV <60 seconds (95th percentile)
- MTTA <5 minutes (95th percentile)
- 100% dual authorization compliance for critical actions
- Operator workload <15 alerts/hour

**Deliverables:**
- Standard Operating Procedures (SOPs) for case handling
- Operator training logs (8 operators, 40 hours total)
- HITL approval metrics dashboard

**Responsible:** Operations team + Airport security supervisors

---

### Phase 5: Audit & Sign-Off (Week 9)

**Objective:** Independent validation before production scale

**Tasks:**
1. **Third-party privacy audit:** NDPR 2019 compliance review
2. **Security audit:** Penetration testing, vulnerability scan
3. **Community stakeholder briefing:** Civil society, privacy advocates
4. **PIA review:** Data Protection Officer (DPO) final approval
5. **FAAN sign-off:** Operational readiness certificate

**Deliverables:**
- Privacy audit report (NDPR compliance)
- Security audit report (pen test results)
- Updated Privacy Impact Assessment (PIA)
- Stakeholder sign-off document
- FAAN production approval letter

**Responsible:** Legal + Compliance team + External auditors

---

### Phase 6: Scale to Production (Week 10+)

**Objective:** Expand to additional cameras and airports

**Tasks:**
1. Expand to 10+ camera groups at MMIA
2. Deploy to second airport: Nnamdi Azikiwe International Airport (Abuja FCT)
3. Integrate with national threat database (NIMC, Police watchlists)
4. Enable limited automated response with strict safeguards (e.g., auto-zoom on threat)

**Deliverables:**
- Multi-airport deployment (Lagos + Abuja)
- National agency integrations (NIMC, Police, Fire)
- Production SLA (99.5% uptime, <500ms detection latency)

**Responsible:** Engineering team + National stakeholders

---

## Pre-Flight Checklist

Before pilot launch, verify:

| Requirement | Status | Owner |
|-------------|--------|-------|
| ✅ Signed MOU & DSA with airport | **DONE** | Legal |
| ⏳ Vendor access credentials (airside badge) | **PENDING** | Airport Security |
| ✅ PIA completed and approved by DPO | **DONE** | Compliance |
| ✅ Edge hardware with TPM attestation | **DONE** | DevOps |
| ⏳ Redundant power & UPS (4-hour backup) | **PENDING** | IT Infrastructure |
| ✅ Private APN/VPN with QoS guarantees | **DONE** | MTN (telco partner) |
| 🔄 Operator training & SOPs documented | **IN PROGRESS** | Operations |

---

## Monitoring & KPIs for Dashboard Operators

### 1. Stream Health
- **Packet Loss:** <0.1% (SLA threshold)
- **Network Latency:** <50ms (round-trip)
- **Camera Uptime:** >99.5% (per camera)
- **Drone Link Quality:** >90% (signal strength)

**Dashboard:** Real-time graphs (Grafana), alerts on threshold breach

---

### 2. AI Detection Performance
- **Precision @ Top-K:** >90% (weekly rolling average)
- **False Positive Rate:** <10% (tuned threshold)
- **Detection Latency:** <500ms (camera feed → alert)
- **Model Drift:** <2% weekly (monitor distribution shift)

**Dashboard:** Weekly ML performance report, confusion matrix

---

### 3. Operator Workload
- **Alerts per Operator per Hour:** <15 (sustainable workload)
- **Mean Time to Verify (MTTV):** <60 seconds (alert → operator review)
- **Mean Time to Action (MTTA):** <5 minutes (review → decision)
- **Case Backlog:** <10 pending cases (real-time)

**Dashboard:** Operator workload heatmap, burnout risk alerts

---

### 4. Security & Audit
- **Audit Access Frequency:** Monitor daily (DPO access, regulator queries)
- **Suspicious Access Attempts:** **0 tolerance** (immediate escalation)
- **Failed Authentication Attempts:** <5 per day (brute-force detection)
- **Audit Log Integrity:** 100% (SHA-256 hash validation)

**Dashboard:** Security events timeline, anomaly detection

---

## Escalation Procedures

### Incident Severity Levels

| Level | Definition | Response Time | Approval Required |
|-------|------------|---------------|-------------------|
| **LOW** | False positive, minor alert | <10 minutes | Operator decision |
| **MEDIUM** | Suspicious behavior, non-urgent | <5 minutes | Supervisor review |
| **HIGH** | Security threat, immediate action | <2 minutes | Dual authorization |
| **CRITICAL** | Active incident, physical safety risk | <30 seconds | Emergency protocol |

### Emergency Stop Procedure
1. Operator presses **EMERGENCY STOP** button in dashboard
2. All automated actions halted immediately
3. System reverts to observe-only mode
4. Incident report generated for DPO + FAAN
5. Manual security protocols activated

---

## Success Metrics

### Pilot Success Criteria (Must achieve 4/5)
1. ✅ Zero privacy breaches (NDPR compliance)
2. ✅ >90% AI detection precision (tuned thresholds)
3. ✅ MTTV <60s, MTTA <5min (operator efficiency)
4. ⏳ Third-party audit pass (privacy + security)
5. ⏳ FAAN operational approval (production sign-off)

---

## Budget & Resources

### Infrastructure Costs (Pilot Phase)
- Edge Gateway (TPM-enabled): ₦500,000
- UPS (4-hour backup): ₦300,000
- Private APN (3 months): ₦150,000/month
- Camera integration (5 units): ₦200,000
- **Total Infrastructure:** ₦1.45M

### Operational Costs (90 days)
- Operator training (8 people × 5 days): ₦800,000
- Third-party audits (privacy + security): ₦2M
- Legal & compliance: ₦500,000
- **Total Operational:** ₦3.3M

**Pilot Total:** ₦4.75M (~$3,000 USD at ₦1,580/$)

---

## Risks & Mitigation

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| **Privacy breach** | Low | Critical | Tokenized matching, 30-day data retention, DPO oversight |
| **False positive alert fatigue** | Medium | High | Tune thresholds weekly, operator feedback loop |
| **Network downtime** | Low | High | Redundant VPN, 4G failover, local caching |
| **Operator training gaps** | Medium | Medium | Daily SOPs review, shadow training, certification |
| **FAAN bureaucratic delays** | High | Medium | Weekly stakeholder meetings, escalation path |

---

## Next Steps

1. ✅ **Week 0:** Finalize vendor access credentials (Airport IT)
2. ⏳ **Week 1:** Deploy edge gateway + UPS (DevOps team)
3. ⏳ **Week 2:** Start observe-only mode (ML team)
4. ⏳ **Week 9:** Schedule third-party audits (Legal team)
5. ⏳ **Week 10:** FAAN production approval (Executive team)

**Primary Contact:** [Your Name], Pilot Program Manager  
**Email:** pilot@securityai.ng  
**Phone:** +234-XXX-XXX-XXXX

---

**Document Version:** 1.0  
**Last Updated:** November 27, 2025  
**Classification:** Internal Use Only (FAAN Pre-Approval)
