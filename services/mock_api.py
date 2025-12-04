"""
Mock API server for dashboard development
Provides realistic data for all agency services
"""
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
import uvicorn
from datetime import datetime, timedelta
import random
import json

app = FastAPI(title="Security AI Mock API", version="1.0.0")

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:3001"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mock data generators
def generate_alerts(count: int = 50):
    domains = ["nids", "phishing", "logs", "malware", "auth"]
    severities = ["critical", "high", "medium", "low"]
    
    alerts = []
    for i in range(count):
        domain = random.choice(domains)
        severity = random.choice(severities)
        timestamp = datetime.now() - timedelta(hours=random.randint(0, 72))
        
        alerts.append({
            "id": f"alert-{i+1000}",
            "domain": domain,
            "severity": severity,
            "title": f"{domain.upper()} Alert: {severity.title()} threat detected",
            "description": f"Detected suspicious {domain} activity requiring investigation",
            "timestamp": timestamp.isoformat(),
            "status": random.choice(["new", "investigating", "resolved"]),
            "score": round(random.uniform(0.6, 0.99), 2),
            "source_ip": f"192.168.{random.randint(1,254)}.{random.randint(1,254)}",
        })
    
    return sorted(alerts, key=lambda x: x["timestamp"], reverse=True)

# Global data
ALERTS = generate_alerts(100)

# Health check
@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "service": "mock-api"
    }

# Core ML alerts
@app.get("/api/v1/alerts")
async def get_alerts(domain: Optional[str] = None, severity: Optional[str] = None):
    filtered = ALERTS
    if domain:
        filtered = [a for a in filtered if a["domain"] == domain]
    if severity:
        filtered = [a for a in filtered if a["severity"] == severity]
    return {"alerts": filtered, "total": len(filtered)}

@app.get("/api/v1/alerts/{alert_id}")
async def get_alert(alert_id: str):
    alert = next((a for a in ALERTS if a["id"] == alert_id), None)
    if not alert:
        raise HTTPException(status_code=404, detail="Alert not found")
    return alert

# INEC Service (Port 8085)
@app.get("/api/v1/inec/health")
async def inec_health():
    return {
        "status": "healthy",
        "service": "INEC Voter Verification",
        "port": 8085,
        "total_verifications": 1247,
        "pending_reviews": 12,
        "polling_units": 2
    }

@app.get("/api/v1/inec/verify")
async def inec_verify():
    return {
        "status": "success",
        "verifications_today": 156,
        "pending_reviews": 12,
        "recent_verifications": [
            {"id": "v-001", "timestamp": datetime.now().isoformat(), "status": "verified"},
            {"id": "v-002", "timestamp": (datetime.now() - timedelta(minutes=5)).isoformat(), "status": "pending"},
            {"id": "v-003", "timestamp": (datetime.now() - timedelta(minutes=10)).isoformat(), "status": "verified"},
        ]
    }

# Fire Service (Port 8086)
@app.get("/api/v1/fire/health")
async def fire_health():
    return {
        "status": "healthy",
        "service": "Federal Fire Service",
        "port": 8086,
        "active_incidents": 2,
        "total_incidents": 38,
        "notifications_sent": 412
    }

@app.get("/api/v1/fire/incidents")
async def fire_incidents():
    return {
        "active_incidents": [
            {
                "id": "fire-001",
                "location": {"lat": 6.5244, "lon": 3.3792},
                "severity": "high",
                "timestamp": (datetime.now() - timedelta(minutes=15)).isoformat(),
                "status": "responding"
            },
            {
                "id": "fire-002",
                "location": {"lat": 6.4281, "lon": 3.4219},
                "severity": "medium",
                "timestamp": (datetime.now() - timedelta(minutes=45)).isoformat(),
                "status": "contained"
            }
        ],
        "total_incidents": 38,
        "notifications_sent": 412
    }

# Police Service (Port 8087)
@app.get("/api/v1/police/health")
async def police_health():
    return {
        "status": "healthy",
        "service": "Nigeria Police Force",
        "port": 8087,
        "pending_analyst_review": 8,
        "active_incidents": 5,
        "total_incidents": 127,
        "dispatches_today": 23
    }

@app.get("/api/v1/police/incidents")
async def police_incidents():
    return {
        "pending_reviews": 8,
        "active_incidents": 5,
        "incidents": [
            {
                "id": "pol-001",
                "type": "security_threat",
                "severity": "critical",
                "location": "MMIA Terminal 2",
                "timestamp": (datetime.now() - timedelta(minutes=20)).isoformat(),
                "status": "pending_review"
            },
            {
                "id": "pol-002",
                "type": "suspicious_behavior",
                "severity": "high",
                "location": "Lekki Phase 1",
                "timestamp": (datetime.now() - timedelta(hours=1)).isoformat(),
                "status": "investigating"
            }
        ]
    }

# Social Media (Port 8088)
@app.get("/api/v1/social/health")
async def social_health():
    return {
        "status": "healthy",
        "service": "Social Media Regulation",
        "port": 8088,
        "pending_reviews": 34,
        "total_records": 5621,
        "law_enforcement_reports": 12
    }

@app.get("/api/v1/social/moderate")
async def social_moderate():
    return {
        "pending_reviews": 34,
        "moderated_today": 287,
        "compliance_rate": 0.982,
        "recent_reports": [
            {
                "id": "sm-001",
                "platform": "twitter",
                "violation_type": "cybercrime_act_24",
                "severity": "high",
                "timestamp": (datetime.now() - timedelta(hours=2)).isoformat(),
                "status": "reviewed"
            }
        ]
    }

# Identity Service (Port 8081)
@app.get("/api/v1/identity/health")
async def identity_health():
    return {
        "status": "healthy",
        "service": "NIMC Identity Matching",
        "port": 8081,
        "matches_today": 423,
        "privacy_mode": "tokenized"
    }

# Gateway Service (Port 8443)
@app.get("/api/v1/gateway/health")
async def gateway_health():
    return {
        "status": "healthy",
        "service": "Secure API Gateway",
        "port": 8443,
        "telemetry": {
            "requests_today": 12847,
            "avg_latency_ms": 12,
            "packet_loss": 0.0002,
            "uptime": 0.998
        }
    }

@app.get("/api/v1/gateway/metrics")
async def gateway_metrics():
    return {
        "stream_health": {
            "packet_loss": 0.02,
            "latency_ms": 12,
            "camera_uptime": 99.8,
            "drone_link_quality": 95.0
        },
        "ai_performance": {
            "precision_top_k": 94.2,
            "false_positive_rate": 5.8,
            "detection_latency_ms": 180,
            "model_drift_weekly": 0.3
        },
        "operator_workload": {
            "alerts_per_hour": 12,
            "mttv_seconds": 45,
            "mtta_minutes": 3.2,
            "case_backlog": 3
        },
        "security_audit": {
            "audit_access_daily": 8,
            "suspicious_access": 0,
            "failed_auth": 2,
            "log_integrity": 100.0
        }
    }

# Pilot program
@app.get("/api/v1/pilot/status")
async def pilot_status():
    return {
        "phase": "observe-only",
        "week": 3,
        "location": "MMIA Lagos Terminal 2",
        "cameras_active": 5,
        "drone_corridors": 1,
        "alerts_today": 47,
        "operator_trained": 8
    }

if __name__ == "__main__":
    print("🚀 Starting Security AI Mock API Server")
    print("📡 Dashboard: http://localhost:3000")
    print("🔌 API: http://localhost:8000")
    print("\nEndpoints:")
    print("  - http://localhost:8000/api/v1/alerts")
    print("  - http://localhost:8000/api/v1/inec/health")
    print("  - http://localhost:8000/api/v1/fire/health")
    print("  - http://localhost:8000/api/v1/police/health")
    print("  - http://localhost:8000/api/v1/social/health")
    print("  - http://localhost:8000/api/v1/gateway/metrics")
    print("  - http://localhost:8000/api/v1/pilot/status")
    
    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info")
