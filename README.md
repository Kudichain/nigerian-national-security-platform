# Security AI Platform with National Identity Integration

Production-grade security threat detection platform using machine learning across 5 core domains + privacy-first national identity integration:

## Core Security Domains

- **Network Intrusion Detection (NIDS)** - Detect malicious network traffic patterns
- **Log Anomaly Detection (SIEM)** - Identify suspicious behavior in system logs
- **Phishing Detection** - Classify emails and URLs as legitimate or phishing
- **Authentication Risk Scoring** - Real-time fraud detection for login events
- **Malware Detection** - Static and dynamic analysis of executable files

## Identity Integration

- **Privacy-Preserving Identity Matching** - NIMC integration with tokenized matching
- **Drone Surveillance Edge AI** - Face detection with local privacy filters
- **ICS/SCADA Traffic Control** - IEC 62443-compliant intersection control
- **NDPR Governance** - Full Nigerian Data Protection Regulation compliance
- **Human-in-the-Loop** - Operator approval workflows with audit trails

## Government Agency Integrations (NEW)

- **INEC (Port 8085)** - Privacy-preserving voter verification for elections
- **Federal Fire Service (Port 8086)** - Automated fire/smoke detection and alerting
- **Nigeria Police Force (Port 8087)** - Security threat detection with analyst review
- **Social Media Regulation (Port 8088)** - Content moderation, Cybercrime Act compliance

## Architecture

```
┌─────────────────────────────────────────────────────────────────────────┐
│                       Core ML Security Platform                          │
│  Sensors/Agents → Kafka → Parsers → Features → ML Models → Services    │
│                              ↓                                            │
│                      Feature Store (Redis/S3)                            │
│                              ↓                                            │
│                      Model Registry (MLflow)                             │
└─────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────┐
│                   Identity Integration Layer (NEW)                       │
│                                                                           │
│  Edge (Drones) ──mTLS──> API Gateway ──> Identity Service (NIMC)       │
│       │                       │                    │                      │
│   Privacy AI             JWT/Auth          Tokenized Matching            │
│  (blur, encrypt)        Rate Limit         (no raw PII)                 │
│       │                       │                    │                      │
│       └───────────────────────┴────────────────────┴──> Decision Engine │
│                                                              │            │
│                                                    ┌─────────┴────────┐  │
│                                                    │                  │  │
│                                              Approval        Traffic   │  │
│                                              Workflow       Control    │  │
│                                              (Human)         (ICS)     │  │
│                                                    │                  │  │
│                                                    └──────────────────┘  │
│                                                              │            │
│                                                    Immutable Audit Log   │
│                                                         (WORM)            │
└─────────────────────────────────────────────────────────────────────────┘
```

### Technology Stack

**Core ML Platform:**
- **Languages**: Python 3.10+ (ML core), Go/Rust (performance-critical agents)
- **Streaming**: Kafka, Flink/Spark Structured Streaming
- **Storage**: S3 (raw data), ClickHouse/Elasticsearch (queries), Postgres (metadata), Redis (online features)
- **ML**: scikit-learn, XGBoost, LightGBM, PyTorch, Hugging Face Transformers
- **MLOps**: MLflow (tracking + registry), Docker, Kubernetes, Helm
- **Monitoring**: Prometheus, Grafana, ELK
- **Explainability**: SHAP (tree models), Captum (deep learning)

**Identity Integration:**
- **Edge AI**: OpenCV, dlib, face-recognition (FaceNet/ArcFace embeddings)
- **Privacy**: Cryptography (Fernet, RSA-2048), differential privacy
- **Identity**: NIMC API integration, secure enclave support (Intel SGX/AWS Nitro)
- **Control**: ICS/SCADA-compliant (IEC 62443), failsafe design
- **Governance**: NDPR compliance, consent management, transparency reporting

## Quick Start

### Prerequisites

- Python 3.10+
- Docker & Docker Compose
- Kubernetes cluster (for production)
- Access to S3 or compatible object storage

### Local Development

1. **Clone and setup**:
   ```powershell
   git clone <repo-url>
   cd AI
   python -m venv venv
   .\venv\Scripts\Activate.ps1
   pip install -r requirements.txt
   ```

2. **Configure environment**:
   ```powershell
   cp .env.example .env
   # Edit .env with your configurations
   ```

3. **Start infrastructure** (Kafka, Redis, MLflow, etc.):
   ```powershell
   cd infra/docker
   docker-compose up -d
   ```

4. **Train models**:
   ```powershell
   # NIDS
   python models/nids/train.py --data data/netflow_sample.parquet --model isoforest
   
   # Phishing
   python models/phishing/train.py --data data/emails_labeled.parquet --model tfidf
   
   # Auth Risk
   python models/auth/train.py --data data/auth_events_labeled.parquet
   ```

5. **Start inference services**:
   ```powershell
   # NIDS service (port 8080)
   python services/nids/app.py
   
   # Phishing service (port 8081)
   python services/phishing/app.py
   
   # Auth risk service (port 8082)
   python services/auth/app.py
   ```

6. **Test inference**:
   ```powershell
   Invoke-WebRequest -Uri "http://localhost:8080/score" -Method POST `
     -Headers @{"Content-Type"="application/json"} `
     -Body '{\"bytes\": 1024, \"packets\": 10, \"duration_ms\": 500}'
   ```

## Project Structure

```
sec-ai-platform/
├── collectors/          # Data collection agents
│   ├── netflow_agent.py
│   ├── log_agent.py
│   ├── email_agent.py
│   ├── auth_agent.py
│   └── malware_agent.py
├── parsers/             # Data normalization
│   ├── netflow_parser.py
│   ├── log_parser.py
│   └── email_parser.py
├── features/            # Feature extraction
│   ├── netflow_features.py
│   ├── log_features.py
│   ├── phishing_features.py
│   ├── auth_features.py
│   └── malware_features.py
├── models/              # Training scripts
│   ├── nids/train.py
│   ├── logs/train.py
│   ├── phishing/train.py
│   ├── auth/train.py
│   └── malware/train.py
├── services/            # Inference microservices
│   ├── nids/app.py
│   ├── phishing/app.py
│   ├── auth/app.py
│   ├── logs/app.py
│   ├── malware/app.py
│   ├── identity/app.py      # NIMC identity matching
│   ├── decision/app.py      # Policy engine
│   ├── traffic/app.py       # ICS/SCADA traffic control
│   ├── gateway/app.py       # API gateway
│   ├── governance/app.py    # NDPR compliance
│   ├── inec/app.py          # Voter verification
│   ├── fire/app.py          # Fire Service integration
│   ├── police/app.py        # Police integration
│   └── social_media/app.py  # Content moderation
├── schemas/             # Data schemas and config
│   ├── data_schemas.py
│   └── config.py
├── infra/               # Infrastructure as code
│   ├── docker/
│   │   ├── Dockerfile.nids
│   │   └── docker-compose.yml
│   ├── k8s/
│   │   ├── common.yaml
│   │   └── nids-deployment.yaml
│   └── helm/
├── edge/                # Edge AI processing
│   └── drone_edge.py
├── legal/               # Legal templates and MOUs
│   ├── README.md
│   ├── INEC_MOU.md
│   ├── NDPR_CHECKLIST.md
│   └── CYBERCRIME_COMPLIANCE.md
├── tests/               # Unit and integration tests
│   ├── test_identity_integration.py
│   └── model_smoke_test.py
├── dashboard/           # React dashboard (Material-UI)
└── docs/                # Documentation
    ├── ARCHITECTURE.md
    ├── AGENCY_INTEGRATIONS.md
    ├── IDENTITY_INTEGRATION.md
    └── DEPLOYMENT.md
```

## Data Schemas

All domains use standardized Pydantic schemas. Example for network flows:

```python
class NetworkFlow(BaseModel):
    ts: datetime
    src_ip: str
    dst_ip: str
    src_port: int
    dst_port: int
    protocol: str
    bytes: int
    packets: int
    duration_ms: int
    # ... additional fields
```

See `schemas/data_schemas.py` for all domain schemas.

## Model Training

### NIDS (Network Intrusion Detection)

```powershell
# Unsupervised (Isolation Forest)
python models/nids/train.py `
  --data s3://sec-ai-raw/netflow/2025-11/*.parquet `
  --model isoforest `
  --contamination 0.005

# Supervised (XGBoost) - requires labeled data
python models/nids/train.py `
  --data s3://sec-ai-raw/netflow_labeled.parquet `
  --model xgboost
```

### Phishing Detection

```powershell
# TF-IDF + Logistic Regression
python models/phishing/train.py `
  --data s3://sec-ai-raw/emails/labeled.parquet `
  --model tfidf

# XGBoost on extracted features
python models/phishing/train.py `
  --data s3://sec-ai-features/email_features.parquet `
  --model xgboost
```

### Auth Risk Scoring

```powershell
python models/auth/train.py `
  --data s3://sec-ai-raw/auth_events/labeled.parquet
```

## Inference

All inference services expose consistent REST APIs:

### Request
```json
POST /score
{
  "feature1": value1,
  "feature2": value2,
  ...
}
```

### Response
```json
{
  "timestamp": "2025-11-27T10:30:00Z",
  "domain": "nids",
  "score": 0.85,
  "confidence": 0.92,
  "label": "anomalous",
  "action": "alert",
  "explanation": [
    {"feature": "bytes_per_second", "contribution": 0.45},
    {"feature": "dst_port", "contribution": 0.23}
  ],
  "model_version": "isoforest_v1"
}
```

## Deployment

### Docker Compose (Development)

```powershell
cd infra/docker
docker-compose up -d
```

This starts:
- Kafka + Zookeeper
- Redis
- Postgres
- MLflow
- Prometheus + Grafana
- All inference services

### Kubernetes (Production)

```powershell
# Create namespace and common resources
kubectl apply -f infra/k8s/common.yaml

# Deploy services
kubectl apply -f infra/k8s/nids-deployment.yaml

# Check status
kubectl get pods -n sec-ai
```

## Monitoring

- **Prometheus metrics**: `http://localhost:9090`
- **Grafana dashboards**: `http://localhost:3000` (admin/admin)
- **MLflow UI**: `http://localhost:5000`

Each inference service exposes `/metrics` endpoint with:
- Request count
- Request latency
- Anomaly/alert counts
- Model score distributions

## MLOps

### Model Registry

All models are tracked in MLflow:

```python
import mlflow
mlflow.set_tracking_uri("http://localhost:5000")
mlflow.set_experiment("sec-ai-nids")

with mlflow.start_run():
    mlflow.log_params({"model_type": "IsolationForest"})
    mlflow.sklearn.log_model(model, "model")
    mlflow.log_metrics({"auc": 0.95})
```

### Model Versioning

Models are versioned and stored in S3:
- `s3://sec-ai-models/nids/isoforest_v1.pkl`
- `s3://sec-ai-models/phishing/tfidf_v2.pkl`

### Retraining

Automated retraining via scheduled jobs (Kubernetes CronJob):

```yaml
apiVersion: batch/v1
kind: CronJob
metadata:
  name: nids-retrain
spec:
  schedule: "0 2 * * *"  # Daily at 2 AM
  jobTemplate:
    spec:
      template:
        spec:
          containers:
          - name: train
            image: sec-ai/nids-train:latest
            command: ["python", "models/nids/train.py"]
```

## Security

- All secrets in HashiCorp Vault or Kubernetes Secrets
- TLS everywhere (mTLS between services)
- Model artifact signing
- Input validation and sanitization
- Rate limiting on APIs
- RBAC in Kubernetes

## Testing

```powershell
# Unit tests
pytest tests/unit/

# Integration tests
pytest tests/integration/

# Model smoke tests
python tests/model_smoke_test.py

# Coverage
pytest --cov=. --cov-report=html
```

## Contributing

1. Create feature branch
2. Make changes with tests
3. Run linters: `black .` and `flake8 .`
4. Submit PR

## License

[Your License]

## Documentation

### Core Platform
- **Architecture**: `docs/ARCHITECTURE.md` - Complete system design diagrams
- **API Reference**: `docs/API.md` - REST API specifications
- **Deployment**: `docs/DEPLOYMENT.md` - Kubernetes and Docker deployment
- **MLOps**: `docs/MLOPS.md` - Model training, versioning, and monitoring

### Identity & Agency Integrations
- **Identity Integration**: `docs/IDENTITY_INTEGRATION.md` - NIMC integration, privacy design
- **Agency Integrations**: `docs/AGENCY_INTEGRATIONS.md` - INEC, Fire, Police, Social Media
- **Quickstart**: `docs/QUICKSTART_IDENTITY.md` - Quick start guide

### Legal & Compliance
- **INEC MOU**: `legal/INEC_MOU.md` - Voter verification agreement
- **NDPR Compliance**: `legal/NDPR_CHECKLIST.md` - Privacy compliance checklist
- **Cybercrime Act**: `legal/CYBERCRIME_COMPLIANCE.md` - Content moderation compliance

## Support

- Documentation: `docs/`
- Issues: GitHub Issues
- Email: security-ai@example.com
