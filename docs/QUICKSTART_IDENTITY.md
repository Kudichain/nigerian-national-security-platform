# Quick Start Guide - Identity Integration

## Overview

This guide helps you get started with the privacy-first identity integration features added to the Security AI Platform.

## Prerequisites

✅ Python 3.10+  
✅ Docker & Docker Compose  
✅ OpenCV, dlib, face-recognition libraries  
✅ Access to NIMC API (for production)  

## Local Development Setup

### 1. Install Dependencies

```powershell
# Navigate to project root
cd c:\Users\moham\AI

# Activate virtual environment
.\venv\Scripts\Activate.ps1

# Install new dependencies
pip install opencv-python dlib face-recognition pillow cryptography pyjwt fastapi uvicorn
```

### 2. Start Core Services

```powershell
# Start infrastructure (Kafka, Redis, Postgres)
cd infra\docker
docker-compose up -d

# Wait for services to be ready
Start-Sleep -Seconds 10
```

### 3. Start Identity Integration Services

Open 5 separate PowerShell terminals:

**Terminal 1: API Gateway**
```powershell
cd c:\Users\moham\AI
python services\gateway\app.py
# Listens on: http://0.0.0.0:8080
```

**Terminal 2: Identity Matching Service**
```powershell
cd c:\Users\moham\AI
python services\identity\app.py
# Listens on: http://0.0.0.0:8081
```

**Terminal 3: Decision Engine**
```powershell
cd c:\Users\moham\AI
python services\decision\app.py
# Listens on: http://0.0.0.0:8082
```

**Terminal 4: Traffic Control**
```powershell
cd c:\Users\moham\AI
python services\traffic\app.py
# Listens on: http://0.0.0.0:8083
```

**Terminal 5: Governance Service**
```powershell
cd c:\Users\moham\AI
python services\governance\app.py
# Listens on: http://0.0.0.0:8084
```

### 4. Verify Services

```powershell
# Check health endpoints
Invoke-WebRequest http://localhost:8080/health
Invoke-WebRequest http://localhost:8081/health
Invoke-WebRequest http://localhost:8082/health
Invoke-WebRequest http://localhost:8083/health
Invoke-WebRequest http://localhost:8084/health
```

## Testing the System

### Test 1: Edge Processing (Drone Simulation)

```python
# Create test script: test_edge.py
from edge.drone_edge import DroneEdgeProcessor, generate_device_keypair
from cryptography.fernet import Fernet
import numpy as np

# Initialize
private_key, public_key = generate_device_keypair()
encryption_key = Fernet.generate_key()

processor = DroneEdgeProcessor(
    device_id="drone-test-001",
    encryption_key=encryption_key,
    private_key=private_key,
    video_ttl=30,
    enable_differential_privacy=True
)

# Simulate frame
frame = np.zeros((480, 640, 3), dtype=np.uint8)
location = {"lat": 9.0765, "lon": 7.3986, "accuracy_m": 3}
metadata = {"altitude": 120, "weather": "clear"}

# Process
request = processor.create_match_request(frame, location, metadata)
print(f"Encrypted template created: {len(request['template'])} bytes")
```

Run:
```powershell
python test_edge.py
```

### Test 2: Identity Matching API

```powershell
# Login to get JWT
$response = Invoke-RestMethod -Method Post -Uri "http://localhost:8080/auth/login" `
    -ContentType "application/json" `
    -Body '{"username": "admin", "password": "test123"}'

$token = $response.access_token

# Submit match request
Invoke-RestMethod -Method Post -Uri "http://localhost:8081/api/v1/match" `
    -Headers @{Authorization = "Bearer $token"} `
    -ContentType "application/json" `
    -Body @"
{
  "device_id": "drone-test-001",
  "timestamp": "$(Get-Date -Format 'o')",
  "location": {"lat": 9.0765, "lon": 7.3986, "accuracy_m": 3},
  "template": "test_encrypted_template",
  "signature": "test_signature",
  "mode": "tokenized"
}
"@
```

### Test 3: Decision Engine (Policy Evaluation)

```powershell
# Evaluate match context
Invoke-RestMethod -Method Post -Uri "http://localhost:8082/api/v1/evaluate" `
    -ContentType "application/json" `
    -Body @"
{
  "match": true,
  "pseudonym": "nimc_token_xyz123",
  "confidence": 0.92,
  "location": {"lat": 9.0765, "lon": 7.3986},
  "timestamp": "$(Get-Date -Format 'o')",
  "device_id": "drone-test-001",
  "threat_score": 0.6
}
"@
```

### Test 4: Approval Workflow

```powershell
# Get pending approvals
$pending = Invoke-RestMethod -Uri "http://localhost:8082/api/v1/approvals/pending"

# Approve request (use actual request_id from previous step)
Invoke-RestMethod -Method Post `
    -Uri "http://localhost:8082/api/v1/approvals/REQUEST_ID_HERE/approve?operator_id=admin"
```

### Test 5: Traffic Control

```powershell
# Submit traffic control request
Invoke-RestMethod -Method Post -Uri "http://localhost:8083/control/v1/requests" `
    -ContentType "application/json" `
    -Body @"
{
  "request_id": "$(New-Guid)",
  "action": "set_phase",
  "intersection_id": "igy-12",
  "phase": "pedestrian_crossing",
  "duration_seconds": 30,
  "authority": "operator:admin",
  "signed_policy_token": "demo-signed-token-xyz",
  "reason": "High-threat individual detected, allow pedestrian crossing"
}
"@
```

### Test 6: Audit Log Verification

```powershell
# Verify audit integrity
Invoke-RestMethod -Uri "http://localhost:8082/api/v1/audit/verify"

# Query audit events
Invoke-RestMethod -Uri "http://localhost:8082/api/v1/audit/events?event_type=policy_evaluation"
```

## Running Integration Tests

```powershell
# Run full test suite
pytest tests\test_identity_integration.py -v

# Run specific test
pytest tests\test_identity_integration.py::test_tokenized_matching_privacy -v

# Run with coverage
pytest tests\test_identity_integration.py --cov=edge --cov=services --cov-report=html
```

## Operation Modes

### Mode 1: Observe (Development/Pilot)

```powershell
# Set observe mode
Invoke-RestMethod -Method Post -Uri "http://localhost:8082/api/v1/mode" `
    -ContentType "application/json" `
    -Body '{"mode": "observe"}'
```

**What happens:**
- All identity matches logged
- NO enforcement actions taken
- Data collected for bias analysis
- Safe for testing

### Mode 2: Assisted (Recommended Production)

```powershell
# Set assisted mode
Invoke-RestMethod -Method Post -Uri "http://localhost:8082/api/v1/mode" `
    -ContentType "application/json" `
    -Body '{"mode": "assisted"}'
```

**What happens:**
- Identity matches trigger operator review
- Human approves/rejects actions
- 5-minute timeout on pending approvals
- Full audit trail

### Mode 3: Automatic (Emergency Only)

```powershell
# Set automatic mode (requires certification)
Invoke-RestMethod -Method Post -Uri "http://localhost:8082/api/v1/mode" `
    -ContentType "application/json" `
    -Body '{"mode": "automatic"}'
```

**What happens:**
- Pre-approved rules execute automatically
- Traffic control for critical threats
- Operator notified post-action
- Requires safety certification

## Monitoring

### Check System Status

```powershell
# All service health
"8080", "8081", "8082", "8083", "8084" | ForEach-Object {
    Invoke-RestMethod "http://localhost:$_/health"
}

# Traffic intersection status
Invoke-RestMethod "http://localhost:8083/control/v1/status"

# Pending approvals count
(Invoke-RestMethod "http://localhost:8082/api/v1/approvals/pending").Count
```

### View Audit Logs

```powershell
# Get recent audit events
$events = Invoke-RestMethod "http://localhost:8082/api/v1/audit/events"
$events | Select-Object event_id, event_type, timestamp | Format-Table
```

## NDPR Compliance Operations

### Record Consent

```powershell
Invoke-RestMethod -Method Post -Uri "http://localhost:8084/api/v1/consent" `
    -ContentType "application/json" `
    -Body @"
{
  "subject_id": "pseudonym_abc123",
  "purpose": "law_enforcement",
  "legal_basis": "legal_obligation",
  "duration_days": 365
}
"@
```

### Submit Redress Request (Citizen Appeal)

```powershell
Invoke-RestMethod -Method Post -Uri "http://localhost:8084/api/v1/redress" `
    -ContentType "application/json" `
    -Body @"
{
  "subject_pseudonym": "citizen_token_xyz",
  "request_type": "objection",
  "details": "I object to the processing of my data for this purpose"
}
"@
```

### Generate Transparency Report

```powershell
Invoke-RestMethod "http://localhost:8084/api/v1/transparency-report?period=2025-Q4"
```

## Production Deployment

### Docker Compose (All Services)

Create `docker-compose.identity.yml`:

```yaml
version: '3.8'

services:
  api-gateway:
    build:
      context: .
      dockerfile: infra/docker/Dockerfile.gateway
    ports:
      - "8080:8080"
    environment:
      - JWT_SECRET=${JWT_SECRET}
    volumes:
      - ./certs:/certs

  identity-service:
    build:
      context: .
      dockerfile: infra/docker/Dockerfile.identity
    ports:
      - "8081:8081"
    environment:
      - NIMC_API_ENDPOINT=${NIMC_API_ENDPOINT}
      - NIMC_API_KEY=${NIMC_API_KEY}

  decision-engine:
    build:
      context: .
      dockerfile: infra/docker/Dockerfile.decision
    ports:
      - "8082:8082"
    environment:
      - OPERATION_MODE=assisted

  traffic-control:
    build:
      context: .
      dockerfile: infra/docker/Dockerfile.traffic
    ports:
      - "8083:8083"
    environment:
      - CONTROLLER_IDS=igy-12,lag-01

  governance:
    build:
      context: .
      dockerfile: infra/docker/Dockerfile.governance
    ports:
      - "8084:8084"
```

Deploy:
```powershell
docker-compose -f docker-compose.identity.yml up -d
```

### Kubernetes (Production)

```powershell
# Apply Kubernetes manifests
kubectl apply -f infra/k8s/identity-services.yaml

# Check deployment
kubectl get pods -l app=identity-platform

# View logs
kubectl logs -l app=decision-engine --tail=100
```

## Security Checklist

Before production deployment:

- [ ] Generate production JWT secret (store in Azure Key Vault)
- [ ] Configure mutual TLS certificates
- [ ] Set up HSM for signing keys
- [ ] Enable NIMC production API endpoint
- [ ] Configure network segmentation (analytics/control separation)
- [ ] Set up WORM storage for audit logs
- [ ] Enable Prometheus metrics collection
- [ ] Configure Grafana dashboards
- [ ] Set up alerting (PagerDuty, email)
- [ ] Complete penetration testing
- [ ] Obtain IEC 62443 certification (traffic control)
- [ ] Legal approval from NDPR authority
- [ ] NIMC partnership agreement signed

## Troubleshooting

### Services won't start

```powershell
# Check port conflicts
netstat -ano | Select-String "8080|8081|8082|8083|8084"

# Check logs
Get-Content services\identity\app.log -Tail 50
```

### Authentication errors

```powershell
# Regenerate JWT
$token = (Invoke-RestMethod -Method Post -Uri "http://localhost:8080/auth/login" `
    -ContentType "application/json" `
    -Body '{"username": "admin", "password": "test123"}').access_token

echo $token
```

### Traffic control not responding

```powershell
# Check controller health
Invoke-RestMethod "http://localhost:8083/control/v1/status/igy-12"

# Emergency release (revert to local control)
Invoke-RestMethod -Method Post "http://localhost:8083/control/v1/emergency-release/igy-12"
```

## Next Steps

1. ✅ Review full documentation: `docs/IDENTITY_INTEGRATION.md`
2. ✅ Study architecture: `docs/ARCHITECTURE.md`
3. ⏳ Legal consultation (NIMC, NDPR authority)
4. ⏳ Pilot deployment (observe mode)
5. ⏳ Operator training
6. ⏳ Safety certification (traffic control)
7. ⏳ Public transparency reporting

## Support

For questions or issues:
- Technical: See `docs/` folder
- Legal: Consult NDPR authority
- Safety: IEC 62443 certified auditor required
- NIMC API: Contact NIMC technical support
