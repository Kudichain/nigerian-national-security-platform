"""
Main API Entry Point - Nigerian National Security Platform
"""

from fastapi import FastAPI, HTTPException, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
import random

app = FastAPI(
    title="🇳🇬 Nigerian National Security Platform - Main API",
    version="1.0.0",
    description="Central API for National Security Command Center"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3001", "http://localhost:3000", "http://localhost:5173", "http://localhost:3002", "http://localhost:3003", "http://localhost:3004"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mock data for national overview
@app.get("/api/v1/overview/national")
async def get_national_overview():
    """Get comprehensive national security overview"""
    return {
        "national_security_overview": {
            "active_incidents": 847,
            "resolved_today": 234,
            "personnel_active": 15234,
            "systems_online": 98.7
        },
        "infrastructure": {
            "pipelines_monitored": 127,
            "facilities_secured": 89,
            "incidents_prevented": 23
        },
        "transportation": {
            "trains_tracked": 342,
            "stations_monitored": 156,
            "incidents_today": 3
        },
        "law_enforcement": {
            "officers_on_duty": 8945,
            "patrols_active": 456,
            "arrests_today": 67
        },
        "immigration": {
            "officers_on_duty": 1234,
            "ports_monitored": 23,
            "entries_processed": 4567
        },
        "media_monitoring": {
            "sources_monitored": 2847,
            "mentions_today": 15234,
            "sentiment_positive": 67.3
        },
        "citizen_services": {
            "active_citizens": 12400000,
            "services_accessed": 34567,
            "satisfaction_rate": 89.5
        }
    }

@app.get("/api/v1/threat-level")
async def get_threat_level():
    """Get current national threat level"""
    return {
        "current_level": "ELEVATED",
        "level_code": 3,
        "last_updated": datetime.now().isoformat(),
        "active_threats": {
            "critical": 12,
            "high": 45,
            "medium": 234,
            "low": 556
        },
        "recent_incidents": {
            "past_24h": 89,
            "past_7d": 523,
            "past_30d": 2134
        },
        "threat_sources": {
            "cyber": 234,
            "physical": 123,
            "terrorism": 45,
            "fraud": 445
        }
    }

@app.get("/api/v1/alerts")
async def get_alerts(limit: int = 100):
    """Get recent security alerts"""
    
    domains = ["nids", "phishing", "logs", "malware", "auth"]
    severities = ["critical", "high", "medium", "low"]
    
    alerts = []
    for i in range(min(limit, 50)):
        alerts.append({
            "id": f"ALERT-{1000 + i}",
            "domain": random.choice(domains),
            "severity": random.choice(severities),
            "message": f"Security event detected - ID {1000 + i}",
            "timestamp": datetime.now().isoformat(),
            "resolved": random.choice([True, False])
        })
    
    return {"alerts": alerts, "total": len(alerts)}

@app.get("/api/v1/biometric/stats")
async def get_biometric_stats():
    """Get biometric authentication statistics"""
    return {
        "total_enrolled": 12400000,
        "verifications_today": 234567,
        "success_rate": 99.87,
        "average_time_ms": 234
    }

# Biometric Authentication Endpoints
@app.get("/api/v1/biometric/health")
async def biometric_health():
    """Health check for biometric service"""
    return {
        "status": "healthy",
        "service": "biometric-auth",
        "version": "1.0.0",
        "webauthn_supported": True,
        "registered_users": 12400000,
        "active_sessions": 15432
    }

class BiometricRegisterRequest(BaseModel):
    username: str
    display_name: str

class BiometricAuthRequest(BaseModel):
    username: Optional[str] = None

class BiometricRegisterVerifyRequest(BaseModel):
    credential_id: str
    client_data_json: str
    attestation_object: str
    user_id: str
    challenge_id: str

class BiometricAuthVerifyRequest(BaseModel):
    credential_id: str
    client_data_json: str
    authenticator_data: str
    signature: str
    challenge_id: str
    user_handle: Optional[str] = None

@app.post("/api/v1/biometric/register/options")
async def biometric_register_options(request: BiometricRegisterRequest):
    """Generate registration options for fingerprint enrollment"""
    import secrets
    import base64
    
    challenge = base64.urlsafe_b64encode(secrets.token_bytes(32)).decode('utf-8').rstrip('=')
    user_id = base64.urlsafe_b64encode(secrets.token_bytes(16)).decode('utf-8').rstrip('=')
    challenge_id = base64.urlsafe_b64encode(secrets.token_bytes(16)).decode('utf-8').rstrip('=')
    
    return {
        "challenge": challenge,
        "challenge_id": challenge_id,
        "rp": {
            "name": "Nigeria Security AI Platform",
            "id": "localhost"
        },
        "user": {
            "id": user_id,
            "name": request.username,
            "displayName": request.display_name
        },
        "pubKeyCredParams": [
            {"alg": -7, "type": "public-key"},
            {"alg": -257, "type": "public-key"}
        ],
        "authenticatorSelection": {
            "authenticatorAttachment": "platform",
            "userVerification": "required",
            "requireResidentKey": True,
            "residentKey": "required"
        },
        "timeout": 120000,
        "attestation": "direct"
    }

@app.post("/api/v1/biometric/register/verify")
async def biometric_register_verify(request: BiometricRegisterVerifyRequest):
    """Verify and complete fingerprint registration"""
    # Simulate successful registration
    return {
        "success": True,
        "user_id": request.user_id,
        "credential_id": request.credential_id,
        "message": "Fingerprint registered successfully",
        "enrolled_at": datetime.now().isoformat()
    }

@app.post("/api/v1/biometric/authenticate/options")
async def biometric_auth_options(request: BiometricAuthRequest):
    """Generate authentication options for fingerprint login"""
    import secrets
    import base64
    
    challenge = base64.urlsafe_b64encode(secrets.token_bytes(32)).decode('utf-8').rstrip('=')
    challenge_id = base64.urlsafe_b64encode(secrets.token_bytes(16)).decode('utf-8').rstrip('=')
    
    return {
        "challenge": challenge,
        "challenge_id": challenge_id,
        "timeout": 120000,
        "rpId": "localhost",
        "userVerification": "required",
        "allowCredentials": [] if not request.username else [
            {
                "type": "public-key",
                "id": "mock-credential-id",
                "transports": ["internal", "usb", "nfc", "ble"]
            }
        ]
    }

@app.post("/api/v1/biometric/authenticate/verify")
async def biometric_auth_verify(request: BiometricAuthVerifyRequest):
    """Verify fingerprint authentication"""
    import secrets
    
    # Simulate successful authentication
    session_token = secrets.token_urlsafe(32)
    
    return {
        "success": True,
        "session_token": session_token,
        "user_id": request.user_handle or "user123",
        "username": "officer_admin",
        "message": "Authentication successful",
        "expires_in": 86400
    }

@app.get("/api/v1/biometric/session")
async def biometric_session(authorization: str = None):
    """Get current biometric session info"""
    if not authorization or not authorization.startswith('Bearer '):
        raise HTTPException(status_code=401, detail="Invalid session token")
    
    return {
        "user_id": "user123",
        "username": "officer_admin",
        "enrolled_at": "2024-01-15T10:30:00Z",
        "credential_count": 2,
        "session_expires_at": (datetime.now() + timedelta(hours=24)).isoformat()
    }

@app.get("/api/v1/elections/stats")
async def get_election_stats():
    """Get INEC election security statistics"""
    return {
        "polling_units_monitored": 176846,
        "incidents_detected": 23,
        "voter_turnout": 67.8,
        "systems_online": 99.2
    }

@app.get("/api/v1/emergency/stats")
async def get_emergency_stats():
    """Get emergency services statistics"""
    return {
        "fire_stations_active": 234,
        "ambulances_deployed": 456,
        "response_time_avg_min": 8.5,
        "incidents_today": 89
    }

@app.get("/api/v1/police/stats")
async def get_police_stats():
    """Get police operations statistics"""
    return {
        "officers_on_duty": 8945,
        "patrols_active": 456,
        "arrests_today": 67,
        "cases_resolved": 234
    }

@app.post("/api/v1/visa/verify")
async def verify_visa(visa_number: str, passport_number: str):
    """Verify visa and passport"""
    VISA_DATABASE = {
        "VISA-2025-12345": {
            "citizen": {
                "name": "John Michael Smith",
                "nin": "NIN-12345678",
                "photo": "https://i.pravatar.cc/150?img=12",
                "nationality": "United Kingdom",
                "date_of_birth": "1985-03-15",
                "gender": "Male"
            },
            "visa": {
                "visa_number": "VISA-2025-12345",
                "visa_type": "Work Visa",
                "issue_date": "2025-01-15",
                "expiry_date": "2026-12-31",
                "status": "Active",
                "purpose": "Software Engineering",
                "sponsor": "TechCorp Nigeria Ltd"
            },
            "passport": "A12345678",
            "entry_records": [
                {"date": "2025-11-15", "port": "Murtala Muhammed Airport", "type": "Entry"},
                {"date": "2025-10-20", "port": "Lagos Port", "type": "Exit"}
            ]
        }
    }
    
    visa = VISA_DATABASE.get(visa_number)
    if not visa or visa["passport"] != passport_number:
        return {"valid": False, "message": "Visa not found or passport mismatch"}
    
    return {
        "valid": True,
        "citizen": visa["citizen"],
        "visa": visa["visa"],
        "entry_records": visa["entry_records"],
        "warnings": []
    }

@app.post("/api/v1/voice/verify")
async def verify_voice(file: UploadFile = File(...)):
    """Voice verification (mock)"""
    return {
        "match": True,
        "confidence": 94.5,
        "citizen": {
            "name": "Adebayo Johnson",
            "nin": "NIN-12345678",
            "photo": "https://i.pravatar.cc/150?img=33"
        },
        "voice_characteristics": {
            "pitch": "Medium",
            "accent": "Yoruba-English",
            "speaking_rate": "Normal"
        },
        "analysis_details": {
            "audio_duration": "4.2 seconds",
            "audio_quality": "Good",
            "speech_clarity": "High"
        }
    }

@app.post("/api/v1/photo/verify")
async def verify_photo(file: UploadFile = File(...)):
    """Photo verification (mock)"""
    return {
        "matches": [
            {
                "name": "Adewale Ogunleye",
                "nin": "NIN-98765432",
                "confidence": 96.8,
                "location": "Lagos Victoria Island",
                "photo": "https://i.pravatar.cc/150?img=15",
                "age": 34,
                "gender": "Male",
                "last_seen": "2025-11-30 14:30:00"
            }
        ],
        "total_matches": 1,
        "processing_time": "1.2s"
    }

@app.post("/api/v1/phone/verify")
async def verify_phone(phone_number: str):
    """Phone verification and tracking"""
    PHONE_DATABASE = {
        "+2348012345678": {
            "owner": {
                "name": "Oluwaseun Adeyemi",
                "nin": "NIN-12345678",
                "carrier": "MTN",
                "registered_date": "2020-05-15",
                "sim_status": "Active",
                "photo": "https://i.pravatar.cc/150?img=25"
            },
            "location": {
                "current": "Lagos Victoria Island",
                "coordinates": {"latitude": 6.4281, "longitude": 3.4219},
                "last_seen": "2025-12-01 10:30:00",
                "cell_tower": "MTN-TOWER-VI-001",
                "history": [
                    {"location": "Lagos Victoria Island", "duration": "2 hours"},
                    {"location": "Lekki Phase 1", "duration": "4 hours"}
                ]
            },
            "activity": {
                "calls_today": 15,
                "sms_today": 23,
                "data_usage_mb": 234,
                "last_call": "2025-12-01 09:45:00",
                "roaming": False
            },
            "warnings": []
        }
    }
    
    data = PHONE_DATABASE.get(phone_number)
    if not data:
        return {"registered": False, "message": "Phone number not found"}
    
    return {"registered": True, **data}

@app.get("/api/v1/infrastructure/pipelines")
async def get_pipeline_stats():
    """Pipeline infrastructure monitoring"""
    return {
        "pipeline_infrastructure": {
            "total_pipelines": 45,
            "pipelines_monitored": 42,
            "total_length_km": 5247,
            "monitoring_coverage_percent": 93.3
        },
        "leak_detection": {
            "active_leaks": 3,
            "leaks_detected_period": 12,
            "leaks_repaired": 9,
            "false_positive_rate": 5.2,
            "average_detection_time_minutes": 8
        }
    }

@app.get("/api/v1/transportation/railway")
async def get_railway_stats():
    """Railway security monitoring"""
    return {
        "railway_security": {
            "total_trains": 342,
            "trains_on_schedule": 328,
            "trains_delayed": 14,
            "cctv_cameras_active": 1247,
            "threat_detections_24h": 5
        }
    }

@app.get("/api/v1/law-enforcement/police")
async def get_police_operations():
    """Police operations"""
    return {
        "operations": {
            "officers_on_duty": 8945,
            "patrols_active": 456,
            "arrests_today": 67,
            "response_time_avg": 12.5
        }
    }

@app.get("/api/v1/immigration/airport")
async def get_airport_security():
    """Airport security"""
    return {
        "airport_security": {
            "terminals_monitored": 12,
            "passengers_processed_24h": 45678,
            "high_risk_flagged": 23,
            "officers_on_duty": 1234
        }
    }

@app.get("/api/v1/media/monitoring")
async def get_media_monitoring():
    """Media monitoring"""
    return {
        "media_monitoring": {
            "sources_monitored": 2847,
            "content_verified_24h": 15234,
            "misinformation_detected": 45,
            "sentiment_positive_percent": 67.3
        }
    }

@app.get("/api/v1/citizen/search")
async def search_citizens(query: str = ""):
    """Citizen search"""
    citizens = [
        {
            "nin": "NIN-12345678",
            "name": "Adebayo Johnson",
            "photo": "https://i.pravatar.cc/150?img=33",
            "location": "Lagos",
            "age": 34,
            "status": "Active"
        },
        {
            "nin": "NIN-87654321",
            "name": "Chioma Okafor",
            "photo": "https://i.pravatar.cc/150?img=45",
            "location": "Abuja",
            "age": 28,
            "status": "Active"
        }
    ]
    return {"citizens": citizens, "total": len(citizens)}

@app.get("/api/v1/vehicle/tracking")
async def track_vehicles():
    """Vehicle tracking"""
    return {
        "vehicles": [
            {
                "plate": "LAG-123-ABC",
                "owner": "John Doe",
                "location": "Lagos VI",
                "speed": 45,
                "status": "Moving"
            }
        ],
        "total": 1
    }

@app.get("/api/v1/surveillance/cctv")
async def get_cctv_feeds():
    """CCTV monitoring"""
    return {
        "cameras": [
            {
                "id": "CAM-001",
                "location": "Lagos VI Junction",
                "status": "Online",
                "feed_url": "https://example.com/feed1"
            }
        ],
        "total_cameras": 1247,
        "online": 1234,
        "offline": 13
    }

@app.get("/api/v1/surveillance/border-cctv")
async def get_border_cctv():
    """Get Border CCTV monitoring across Nigeria's international borders"""
    borders = [
        {
            "id": "BDR-001",
            "name": "Seme Border",
            "state": "Lagos",
            "country": "Benin Republic",
            "coordinates": {"lat": 6.4281, "lng": 2.6972},
            "cameras": 45,
            "online": 43,
            "offline": 2,
            "daily_crossings": 8450,
            "vehicles_today": 2340,
            "pedestrians_today": 6110,
            "alerts": 3,
            "status": "operational",
            "last_incident": "2025-11-28T14:30:00Z",
            "staff_on_duty": 67
        },
        {
            "id": "BDR-002",
            "name": "Mfum Border",
            "state": "Cross River",
            "country": "Cameroon",
            "coordinates": {"lat": 5.9833, "lng": 8.6167},
            "cameras": 38,
            "online": 38,
            "offline": 0,
            "daily_crossings": 3420,
            "vehicles_today": 890,
            "pedestrians_today": 2530,
            "alerts": 1,
            "status": "operational",
            "last_incident": "2025-11-25T09:15:00Z",
            "staff_on_duty": 52
        },
        {
            "id": "BDR-003",
            "name": "Jibia Border",
            "state": "Katsina",
            "country": "Niger Republic",
            "coordinates": {"lat": 13.0833, "lng": 7.2167},
            "cameras": 52,
            "online": 50,
            "offline": 2,
            "daily_crossings": 5670,
            "vehicles_today": 1450,
            "pedestrians_today": 4220,
            "alerts": 7,
            "status": "high_alert",
            "last_incident": "2025-12-01T06:45:00Z",
            "staff_on_duty": 89
        },
        {
            "id": "BDR-004",
            "name": "Maiduguri Border",
            "state": "Borno",
            "country": "Chad",
            "coordinates": {"lat": 11.8333, "lng": 13.15},
            "cameras": 64,
            "online": 62,
            "offline": 2,
            "daily_crossings": 2340,
            "vehicles_today": 670,
            "pedestrians_today": 1670,
            "alerts": 12,
            "status": "high_alert",
            "last_incident": "2025-12-01T03:20:00Z",
            "staff_on_duty": 98
        }
    ]
    
    return {
        "total_borders": len(borders),
        "total_cameras": sum(b["cameras"] for b in borders),
        "cameras_online": sum(b["online"] for b in borders),
        "cameras_offline": sum(b["offline"] for b in borders),
        "total_crossings_today": sum(b["daily_crossings"] for b in borders),
        "total_alerts": sum(b["alerts"] for b in borders),
        "borders_on_high_alert": sum(1 for b in borders if b["status"] == "high_alert"),
        "borders": borders,
        "operational_status": "active",
        "last_updated": datetime.now().isoformat()
    }

@app.get("/api/v1/surveillance/tollgate-cctv")
async def get_tollgate_cctv():
    """Get Toll Gate CCTV monitoring across all 36 states of Nigeria"""
    states = [
        {"name": "Abia", "capital": "Umuahia", "zone": "South East", "tollgates": 4, "cameras": 16, "online": 16, "vehicles_today": 3420},
        {"name": "Adamawa", "capital": "Yola", "zone": "North East", "tollgates": 3, "cameras": 12, "online": 11, "vehicles_today": 2340},
        {"name": "Akwa Ibom", "capital": "Uyo", "zone": "South South", "tollgates": 5, "cameras": 20, "online": 19, "vehicles_today": 4560},
        {"name": "Anambra", "capital": "Awka", "zone": "South East", "tollgates": 6, "cameras": 24, "online": 24, "vehicles_today": 5670},
        {"name": "Bauchi", "capital": "Bauchi", "zone": "North East", "tollgates": 4, "cameras": 16, "online": 15, "vehicles_today": 3210},
        {"name": "Bayelsa", "capital": "Yenagoa", "zone": "South South", "tollgates": 2, "cameras": 8, "online": 8, "vehicles_today": 1890},
        {"name": "Benue", "capital": "Makurdi", "zone": "North Central", "tollgates": 5, "cameras": 20, "online": 19, "vehicles_today": 4120},
        {"name": "Borno", "capital": "Maiduguri", "zone": "North East", "tollgates": 3, "cameras": 12, "online": 10, "vehicles_today": 2100},
        {"name": "Cross River", "capital": "Calabar", "zone": "South South", "tollgates": 4, "cameras": 16, "online": 16, "vehicles_today": 3890},
        {"name": "Delta", "capital": "Asaba", "zone": "South South", "tollgates": 6, "cameras": 24, "online": 23, "vehicles_today": 5230},
        {"name": "Ebonyi", "capital": "Abakaliki", "zone": "South East", "tollgates": 3, "cameras": 12, "online": 12, "vehicles_today": 2670},
        {"name": "Edo", "capital": "Benin City", "zone": "South South", "tollgates": 7, "cameras": 28, "online": 27, "vehicles_today": 6450},
        {"name": "Ekiti", "capital": "Ado Ekiti", "zone": "South West", "tollgates": 3, "cameras": 12, "online": 12, "vehicles_today": 2340},
        {"name": "Enugu", "capital": "Enugu", "zone": "South East", "tollgates": 5, "cameras": 20, "online": 20, "vehicles_today": 4890},
        {"name": "Gombe", "capital": "Gombe", "zone": "North East", "tollgates": 3, "cameras": 12, "online": 11, "vehicles_today": 2120},
        {"name": "Imo", "capital": "Owerri", "zone": "South East", "tollgates": 5, "cameras": 20, "online": 19, "vehicles_today": 4560},
        {"name": "Jigawa", "capital": "Dutse", "zone": "North West", "tollgates": 4, "cameras": 16, "online": 15, "vehicles_today": 3120},
        {"name": "Kaduna", "capital": "Kaduna", "zone": "North West", "tollgates": 8, "cameras": 32, "online": 31, "vehicles_today": 7890},
        {"name": "Kano", "capital": "Kano", "zone": "North West", "tollgates": 10, "cameras": 40, "online": 39, "vehicles_today": 9870},
        {"name": "Katsina", "capital": "Katsina", "zone": "North West", "tollgates": 6, "cameras": 24, "online": 23, "vehicles_today": 5430},
        {"name": "Kebbi", "capital": "Birnin Kebbi", "zone": "North West", "tollgates": 4, "cameras": 16, "online": 15, "vehicles_today": 3210},
        {"name": "Kogi", "capital": "Lokoja", "zone": "North Central", "tollgates": 5, "cameras": 20, "online": 20, "vehicles_today": 4670},
        {"name": "Kwara", "capital": "Ilorin", "zone": "North Central", "tollgates": 5, "cameras": 20, "online": 19, "vehicles_today": 4230},
        {"name": "Lagos", "capital": "Ikeja", "zone": "South West", "tollgates": 15, "cameras": 60, "online": 58, "vehicles_today": 45670},
        {"name": "Nasarawa", "capital": "Lafia", "zone": "North Central", "tollgates": 4, "cameras": 16, "online": 16, "vehicles_today": 3450},
        {"name": "Niger", "capital": "Minna", "zone": "North Central", "tollgates": 6, "cameras": 24, "online": 23, "vehicles_today": 5120},
        {"name": "Ogun", "capital": "Abeokuta", "zone": "South West", "tollgates": 8, "cameras": 32, "online": 31, "vehicles_today": 8760},
        {"name": "Ondo", "capital": "Akure", "zone": "South West", "tollgates": 5, "cameras": 20, "online": 19, "vehicles_today": 4340},
        {"name": "Osun", "capital": "Osogbo", "zone": "South West", "tollgates": 5, "cameras": 20, "online": 20, "vehicles_today": 4120},
        {"name": "Oyo", "capital": "Ibadan", "zone": "South West", "tollgates": 9, "cameras": 36, "online": 35, "vehicles_today": 8930},
        {"name": "Plateau", "capital": "Jos", "zone": "North Central", "tollgates": 5, "cameras": 20, "online": 19, "vehicles_today": 4560},
        {"name": "Rivers", "capital": "Port Harcourt", "zone": "South South", "tollgates": 8, "cameras": 32, "online": 31, "vehicles_today": 7890},
        {"name": "Sokoto", "capital": "Sokoto", "zone": "North West", "tollgates": 5, "cameras": 20, "online": 19, "vehicles_today": 4120},
        {"name": "Taraba", "capital": "Jalingo", "zone": "North East", "tollgates": 3, "cameras": 12, "online": 11, "vehicles_today": 2340},
        {"name": "Yobe", "capital": "Damaturu", "zone": "North East", "tollgates": 3, "cameras": 12, "online": 10, "vehicles_today": 1890},
        {"name": "Zamfara", "capital": "Gusau", "zone": "North West", "tollgates": 4, "cameras": 16, "online": 15, "vehicles_today": 3120}
    ]
    
    # Add detailed tollgate info for each state
    for state in states:
        state["offline"] = state["cameras"] - state["online"]
        state["operational_rate"] = round((state["online"] / state["cameras"]) * 100, 1)
        state["revenue_today"] = state["vehicles_today"] * random.randint(200, 500)
        state["alerts"] = random.randint(0, 5)
    
    return {
        "total_states": len(states),
        "total_tollgates": sum(s["tollgates"] for s in states),
        "total_cameras": sum(s["cameras"] for s in states),
        "cameras_online": sum(s["online"] for s in states),
        "cameras_offline": sum(s["offline"] for s in states),
        "total_vehicles_today": sum(s["vehicles_today"] for s in states),
        "total_revenue_today": sum(s["revenue_today"] for s in states),
        "total_alerts": sum(s["alerts"] for s in states),
        "operational_rate": round((sum(s["online"] for s in states) / sum(s["cameras"] for s in states)) * 100, 1),
        "states": states,
        "zones": {
            "North Central": sum(1 for s in states if s["zone"] == "North Central"),
            "North East": sum(1 for s in states if s["zone"] == "North East"),
            "North West": sum(1 for s in states if s["zone"] == "North West"),
            "South East": sum(1 for s in states if s["zone"] == "South East"),
            "South South": sum(1 for s in states if s["zone"] == "South South"),
            "South West": sum(1 for s in states if s["zone"] == "South West")
        },
        "last_updated": datetime.now().isoformat()
    }

@app.get("/api/v1/drone/live")
async def get_drone_feeds():
    """Drone live feeds"""
    return {
        "drones": [
            {
                "id": "DRONE-001",
                "location": "Abuja",
                "altitude": 150,
                "battery": 78,
                "status": "Active"
            }
        ],
        "total": 45
    }

@app.get("/api/v1/security/map")
async def get_security_map():
    """Security map data"""
    return {
        "incidents": [
            {
                "id": "INC-001",
                "type": "Suspicious Activity",
                "location": {"lat": 6.5244, "lng": 3.3792},
                "severity": "medium",
                "timestamp": datetime.now().isoformat()
            }
        ],
        "total": 1
    }

@app.get("/health")
async def health_check():
    return {
        "status": "operational",
        "service": "main-api",
        "version": "1.0.0",
        "timestamp": datetime.now().isoformat()
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
