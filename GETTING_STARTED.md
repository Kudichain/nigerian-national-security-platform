# Security AI Platform - Quick Start Guide

## 🚀 Start Everything (Two Simple Steps)

### Step 1: Start Mock API Server
```powershell
# Install dependencies (first time only)
pip install fastapi uvicorn pydantic

# Start the API server
python services/mock_api.py
```

**You should see:**
```
🚀 Starting Security AI Mock API Server
📡 Dashboard: http://localhost:3000
🔌 API: http://localhost:8000

Endpoints:
  - http://localhost:8000/api/v1/alerts
  - http://localhost:8000/api/v1/inec/health
  - http://localhost:8000/api/v1/fire/health
  ...
```

### Step 2: Start Dashboard
```powershell
# Open a new terminal
cd dashboard
npm run dev
```

**Access:** http://localhost:3000 (or 3001 if 3000 is busy)

## 🔐 Default Login

- Username: `admin`
- Password: `admin123`

## ✨ Features Available

### Core ML Detection (5 Domains)
- **NIDS:** Network intrusion detection
- **Phishing:** Email/web threat analysis  
- **Logs:** SIEM anomaly detection
- **Malware:** Binary analysis
- **Auth:** Authentication risk scoring

### Government Agency Integrations (4 Services)
- **INEC** (Port 8085): Voter verification with privacy
- **Fire Service** (Port 8086): Automated fire/smoke detection
- **Police** (Port 8087): Security threat alerts
- **Social Media** (Port 8088): Content moderation (Cybercrime Act)

### National Identity System
- **NIMC:** Privacy-preserving identity matching (tokenized)
- **Decision Engine:** Human-in-the-loop approvals
- **Traffic Control:** IEC 62443-compliant ICS/SCADA
- **Governance:** NDPR 2019 compliance management

### Airport Pilot Program
- 90-day regulatory sandbox at MMIA Lagos
- Live KPI dashboard (MTTV, MTTA, stream health)
- 6-phase deployment: Observe → Assisted → Production

## 📊 Real Data vs Mock Data

The system currently uses **mock data** for development:
- ✅ Realistic alerts generated every 10 seconds
- ✅ Government agency health checks (INEC, Fire, Police, Social)
- ✅ Live metrics (precision 94.2%, latency 12ms, uptime 99.8%)
- ✅ All features fully functional without production infrastructure

To switch to **real production services**:
1. Deploy actual Python services in `services/` directory
2. Configure production databases (ClickHouse, Postgres, Kafka)
3. Update API endpoints in `dashboard/src/store/alertStore.ts`

## 🛠️ Troubleshooting

### Dashboard won't start
```powershell
cd dashboard
npm install
npm run dev
```

### API server won't start
```powershell
# Install Python dependencies
pip install -r requirements-mock.txt

# Or manually
pip install fastapi uvicorn pydantic

# Run server
python services/mock_api.py
```

### No data showing in dashboard
1. Verify API is running: http://localhost:8000/health
2. Check browser console for errors (F12)
3. Ensure CORS is enabled (already configured in mock API)
4. Try refreshing the page

### Port already in use
```powershell
# Find process using port 8000
netstat -ano | findstr :8000

# Kill process by PID
taskkill /PID <PID> /F

# Or use a different port
# Edit services/mock_api.py line: uvicorn.run(app, port=8001)
```

## 📁 Project Structure

```
AI/
├── services/
│   ├── mock_api.py          # 🔥 Mock data server (START HERE)
│   ├── gateway/             # Secure API gateway (mTLS + attestation)
│   ├── inec/                # INEC voter verification
│   ├── fire/                # Fire Service integration
│   ├── police/              # Police alert system
│   └── social_media/        # Content moderation
├── dashboard/
│   ├── src/
│   │   ├── pages/
│   │   │   ├── Dashboard.tsx    # Main overview
│   │   │   ├── Agencies.tsx     # Government integrations
│   │   │   ├── Identity.tsx     # NIMC/NDPR system
│   │   │   └── Pilot.tsx        # Airport pilot program
│   │   ├── store/
│   │   │   └── alertStore.ts    # Real-time data fetching
│   │   └── api/
│   │       └── client.ts        # API client
│   └── package.json
├── models/                  # ML training scripts
├── docs/
│   ├── AIRPORT_PILOT_PLAN.md       # 90-day deployment guide
│   ├── NCC_OUTREACH_PACKET.md      # Regulatory submission
│   ├── ARCHITECTURE.md              # System architecture
│   └── AGENCY_INTEGRATIONS.md       # API documentation
└── requirements-mock.txt    # Python dependencies (minimal)
```

## 📚 Next Steps

1. ✅ **Explore Dashboard**: Navigate through all 6 pages
   - Dashboard: System overview
   - Alerts: Real-time threat feed
   - Agencies: INEC, Fire, Police, Social Media
   - Identity: NIMC privacy system
   - Pilot: Airport deployment tracker
   - Settings: Configuration

2. 📖 **Read Documentation**:
   - `docs/AIRPORT_PILOT_PLAN.md` - Deployment roadmap
   - `docs/NCC_OUTREACH_PACKET.md` - Regulatory approval guide
   - `docs/AGENCY_INTEGRATIONS.md` - API integration guide

3. 🚀 **Deploy to Production**:
   - Replace mock API with real services
   - Configure Kafka for event streaming
   - Set up ClickHouse for analytics
   - Enable HSM signing for audit trail
   - Integrate NIMC NINAuth sandbox

## 🔒 Security & Compliance

- **NDPR 2019**: Privacy-by-design, tokenized matching, 30-day retention
- **Cybercrime Act 2015**: Law enforcement reporting, audit trails
- **Electoral Act 2022**: Voter privacy protections (INEC)
- **IEC 62443**: Industrial control system safety (traffic lights)
- **NCC IoT Guidelines**: Device registration, private APN

## 📞 Support

- **Documentation**: `docs/` directory
- **Email**: support@securityai.ng
- **Issues**: GitHub Issues

## 💡 Pro Tips

1. **Live Metrics**: Dashboard auto-refreshes every 10 seconds
2. **API Docs**: Visit http://localhost:8000/docs for interactive API testing
3. **Service Status**: Check agency health in Agencies page
4. **KPI Dashboard**: Monitor pilot metrics in Airport Pilot page
5. **Mock Data**: Restart API server to regenerate fresh data

---

**Ready?** Start the API server and dashboard, then login to explore! 🎉

- [ ] Python 3.10 or higher installed
- [ ] Docker Desktop installed and running
- [ ] At least 8GB RAM available
- [ ] 10GB free disk space
- [ ] Git installed

## Step-by-Step Setup (15 minutes)

### 1. Initial Setup (5 min)

```powershell
# Clone repository (if from git)
cd c:\Users\moham\AI

# Run setup script
.\setup.ps1

# Activate virtual environment
.\venv\Scripts\Activate.ps1
```

### 2. Configure Environment (2 min)

```powershell
# Edit .env file with your settings
notepad .env
```

**Minimal configuration for local development:**
```bash
# .env
KAFKA_BOOTSTRAP_SERVERS=localhost:9092
REDIS_HOST=localhost
MLFLOW_TRACKING_URI=http://localhost:5000
LOG_LEVEL=INFO
```

### 3. Start Infrastructure (3 min)

```powershell
# Start all services (Kafka, Redis, MLflow, Prometheus, Grafana)
.\Makefile.ps1 docker-up

# Wait ~30 seconds for services to be ready
# Verify services are running
docker ps
```

You should see containers for:
- Kafka + Zookeeper
- Redis
- PostgreSQL
- MLflow
- Prometheus
- Grafana

### 4. Quick Test with Pre-built Examples (5 min)

Since we don't have real data yet, let's test the infrastructure:

#### Test 1: Check MLflow

```powershell
# Open MLflow UI
Start-Process http://localhost:5000
```

#### Test 2: Run Feature Extraction

```powershell
# Test network flow feature extractor
python -c "
from features.netflow_features import NetFlowFeatureExtractor
extractor = NetFlowFeatureExtractor()
flow = {'bytes': 1024, 'packets': 10, 'duration_ms': 500, 'protocol': 'TCP', 'dst_port': 443}
features = extractor.extract_flow_features(flow)
print(f'Extracted {len(features)} features: {list(features.keys())[:5]}...')
"
```

#### Test 3: Run Feature Tests

```powershell
# Run unit tests for feature extractors
pytest tests/test_features.py -v
```

## Working with Real Data

### Option A: Generate Synthetic Data

Create a simple synthetic data generator:

```powershell
# Create and run synthetic data generator
python -c "
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

# Generate synthetic network flows
n_samples = 1000
df = pd.DataFrame({
    'ts': [datetime.now() - timedelta(minutes=i) for i in range(n_samples)],
    'src_ip': [f'192.168.1.{np.random.randint(1, 255)}' for _ in range(n_samples)],
    'dst_ip': [f'8.8.{np.random.randint(0, 255)}.{np.random.randint(0, 255)}' for _ in range(n_samples)],
    'src_port': np.random.randint(1024, 65535, n_samples),
    'dst_port': np.random.choice([80, 443, 53, 22, 3389], n_samples),
    'protocol': np.random.choice(['TCP', 'UDP', 'ICMP'], n_samples),
    'bytes': np.random.randint(100, 50000, n_samples),
    'packets': np.random.randint(1, 100, n_samples),
    'duration_ms': np.random.randint(10, 5000, n_samples),
})

# Add derived features
df['bytes_per_packet'] = df['bytes'] / df['packets']
df['packets_per_second'] = df['packets'] * 1000 / df['duration_ms']
df['bytes_per_second'] = df['bytes'] * 1000 / df['duration_ms']
df['protocol_tcp'] = (df['protocol'] == 'TCP').astype(int)
df['protocol_udp'] = (df['protocol'] == 'UDP').astype(int)
df['protocol_icmp'] = (df['protocol'] == 'ICMP').astype(int)
df['is_well_known_port'] = (df['dst_port'] < 1024).astype(int)

# Create data directory if it doesn't exist
import os
os.makedirs('data', exist_ok=True)

# Save
df.to_parquet('data/netflow_sample.parquet')
print(f'Generated {len(df)} synthetic network flows in data/netflow_sample.parquet')
"
```

### Option B: Use Your Own Data

If you have access to real security data:

```powershell
# For network flows (NetFlow/IPFIX)
python parsers/netflow_parser.py --input your_netflow_data.json --output data/netflow.parquet

# For logs
python parsers/log_parser.py --input /path/to/logs --output data/logs.parquet
```

## Train Your First Model

### NIDS Model (Network Intrusion Detection)

```powershell
# Train Isolation Forest on synthetic data
python models/nids/train.py --data data/netflow_sample.parquet --model isoforest --contamination 0.01

# View in MLflow
Start-Process http://localhost:5000
```

### Check Training Results

1. Open MLflow UI: http://localhost:5000
2. Navigate to "sec-ai-nids" experiment
3. Click on the latest run
4. View metrics, parameters, and artifacts

## Start Inference Service

```powershell
# Note: You need to have trained a model first
# Start NIDS service on port 8080
python services/nids/app.py
```

In a new PowerShell window:

```powershell
# Test the inference endpoint
Invoke-WebRequest -Uri "http://localhost:8080/score" -Method POST `
  -Headers @{"Content-Type"="application/json"} `
  -Body '{\"bytes\": 1024, \"packets\": 10, \"duration_ms\": 500, \"bytes_per_packet\": 102.4, \"packets_per_second\": 20.0, \"bytes_per_second\": 2048.0, \"protocol_tcp\": 1, \"protocol_udp\": 0, \"protocol_icmp\": 0, \"dst_port\": 443, \"is_well_known_port\": 0}'

# Check health
Invoke-WebRequest -Uri "http://localhost:8080/health"

# Check Prometheus metrics
curl http://localhost:8080/metrics
```

## View Monitoring Dashboards

```powershell
# Prometheus
Start-Process http://localhost:9090

# Grafana (login: admin/admin)
Start-Process http://localhost:3000
```

## Common Workflows

### Daily Development

```powershell
# Start your day
.\Makefile.ps1 docker-up
.\venv\Scripts\Activate.ps1

# Make changes to code...

# Run tests
.\Makefile.ps1 test

# Format code
.\Makefile.ps1 format

# Train updated model
.\Makefile.ps1 train-nids

# Start service
.\Makefile.ps1 serve-nids
```

### Before Committing

```powershell
# Format code
.\Makefile.ps1 format

# Run linters
.\Makefile.ps1 lint

# Run all tests
.\Makefile.ps1 test

# Clean up
.\Makefile.ps1 clean
```

## Troubleshooting

### Issue: Docker containers won't start

```powershell
# Check Docker is running
docker ps

# Check logs
cd infra/docker
docker-compose logs

# Restart everything
docker-compose down
docker-compose up -d
```

### Issue: Port already in use

```powershell
# Find what's using the port (e.g., 8080)
netstat -ano | findstr :8080

# Kill the process
taskkill /PID <PID> /F
```

### Issue: Python import errors

```powershell
# Make sure virtual environment is activated
.\venv\Scripts\Activate.ps1

# Reinstall dependencies
pip install -r requirements.txt

# Install package in editable mode
pip install -e .
```

### Issue: Model files not found

```powershell
# Train models first
.\Makefile.ps1 train-nids

# Or copy pre-trained models to models/ directory
# Ensure paths match in service code
```

## Next Steps

1. **Explore the Code**
   - Start with `schemas/data_schemas.py` to understand data structures
   - Review `features/` to see feature engineering
   - Check `models/*/train.py` for training pipelines

2. **Add More Data**
   - Integrate with your security tools
   - Set up Kafka producers
   - Configure log shippers (Filebeat, Fluentd)

3. **Customize Models**
   - Tune hyperparameters in training scripts
   - Add domain-specific features
   - Experiment with different algorithms

4. **Deploy to Production**
   - See `docs/DEPLOYMENT.md` for K8s deployment
   - Configure monitoring alerts
   - Set up CI/CD pipeline

5. **Read Documentation**
   - `README.md` - Complete overview
   - `docs/API.md` - API reference
   - `docs/MLOPS.md` - MLOps best practices
   - `PROJECT_SUMMARY.md` - Architecture details

## Quick Reference

| Command | Action |
|---------|--------|
| `.\Makefile.ps1 docker-up` | Start infrastructure |
| `.\Makefile.ps1 docker-down` | Stop infrastructure |
| `.\Makefile.ps1 test` | Run tests |
| `.\Makefile.ps1 lint` | Check code quality |
| `.\Makefile.ps1 train-nids` | Train NIDS model |
| `.\Makefile.ps1 serve-nids` | Start NIDS service |

## Getting Help

- Check `README.md` for detailed documentation
- Review code comments and docstrings
- See examples in `tests/` directory
- Check MLflow UI for training history
- Review Grafana dashboards for metrics

**Happy threat hunting! 🔒🛡️**
