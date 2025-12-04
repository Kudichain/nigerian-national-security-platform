"""
Visa Verification Service
Verify visa status and immigrant documentation
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
from datetime import datetime, timedelta
import random

app = FastAPI(
    title="🛂 Visa Verification Service",
    version="1.0.0",
    description="Nigerian Immigration Service - Visa Verification System"
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3001", "http://localhost:3000", "http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Models
class VisaVerificationRequest(BaseModel):
    visa_number: str
    passport_number: str

class CitizenInfo(BaseModel):
    name: str
    nin: str
    photo: str
    nationality: str
    date_of_birth: str
    gender: str

class VisaInfo(BaseModel):
    visa_number: str
    visa_type: str
    issue_date: str
    expiry_date: str
    status: str
    purpose: str
    sponsor: Optional[str] = None

class VisaVerificationResponse(BaseModel):
    valid: bool
    citizen: CitizenInfo
    visa: VisaInfo
    entry_records: list
    warnings: list

# Mock database
VISA_DATABASE = {
    "VISA-2025-12345": {
        "passport": "A12345678",
        "citizen": {
            "name": "John Michael Smith",
            "nin": "NIN-UK-87654321",
            "photo": "https://randomuser.me/api/portraits/men/32.jpg",
            "nationality": "United Kingdom",
            "date_of_birth": "1985-03-15",
            "gender": "Male"
        },
        "visa": {
            "visa_type": "Work Visa",
            "issue_date": "2025-01-15",
            "expiry_date": "2026-12-31",
            "status": "Active",
            "purpose": "Employment at Tech Solutions Ltd",
            "sponsor": "Tech Solutions Nigeria Ltd"
        },
        "entry_records": [
            {"date": "2025-01-20", "port": "Murtala Muhammed Airport, Lagos", "type": "Entry"},
            {"date": "2025-06-10", "port": "Nnamdi Azikiwe Airport, Abuja", "type": "Exit"},
            {"date": "2025-07-05", "port": "Port Harcourt Airport", "type": "Entry"}
        ]
    },
    "VISA-2025-54321": {
        "passport": "B98765432",
        "citizen": {
            "name": "Maria Elena Rodriguez",
            "nin": "NIN-ES-11223344",
            "photo": "https://randomuser.me/api/portraits/women/44.jpg",
            "nationality": "Spain",
            "date_of_birth": "1992-08-22",
            "gender": "Female"
        },
        "visa": {
            "visa_type": "Business Visa",
            "issue_date": "2025-03-10",
            "expiry_date": "2025-09-10",
            "status": "Active",
            "purpose": "Business meetings and conferences",
            "sponsor": "Nigerian Chamber of Commerce"
        },
        "entry_records": [
            {"date": "2025-03-15", "port": "Murtala Muhammed Airport, Lagos", "type": "Entry"}
        ]
    },
    "VISA-2024-99999": {
        "passport": "C11111111",
        "citizen": {
            "name": "David Chen",
            "nin": "NIN-CN-55667788",
            "photo": "https://randomuser.me/api/portraits/men/67.jpg",
            "nationality": "China",
            "date_of_birth": "1988-11-30",
            "gender": "Male"
        },
        "visa": {
            "visa_type": "Tourist Visa",
            "issue_date": "2024-06-01",
            "expiry_date": "2024-12-01",
            "status": "Expired",
            "purpose": "Tourism and sightseeing",
            "sponsor": None
        },
        "entry_records": [
            {"date": "2024-06-15", "port": "Lagos Port", "type": "Entry"},
            {"date": "2024-07-20", "port": "Murtala Muhammed Airport, Lagos", "type": "Exit"}
        ]
    }
}

@app.post("/api/v1/visa/verify")
async def verify_visa(request: VisaVerificationRequest):
    """Verify visa status"""
    
    visa_data = VISA_DATABASE.get(request.visa_number)
    
    if not visa_data:
        raise HTTPException(status_code=404, detail="Visa number not found")
    
    if visa_data["passport"] != request.passport_number:
        raise HTTPException(status_code=400, detail="Passport number does not match visa record")
    
    # Check expiry
    expiry = datetime.strptime(visa_data["visa"]["expiry_date"], "%Y-%m-%d")
    is_expired = expiry < datetime.now()
    
    warnings = []
    if is_expired:
        warnings.append("⚠️ VISA EXPIRED - Overstay detected")
    elif (expiry - datetime.now()).days < 30:
        warnings.append("⚠️ Visa expiring soon - Renewal required")
    
    return {
        "valid": not is_expired,
        "citizen": visa_data["citizen"],
        "visa": {
            **visa_data["visa"],
            "visa_number": request.visa_number
        },
        "entry_records": visa_data["entry_records"],
        "warnings": warnings
    }

@app.get("/api/v1/visa/statistics")
async def get_visa_statistics():
    """Get visa statistics"""
    return {
        "total_active_visas": 45782,
        "expired_visas": 3421,
        "visas_expiring_30_days": 892,
        "by_type": {
            "Work Visa": 15234,
            "Business Visa": 8932,
            "Tourist Visa": 18456,
            "Student Visa": 2347,
            "Diplomatic Visa": 813
        },
        "by_nationality": {
            "United Kingdom": 5234,
            "United States": 4892,
            "China": 3456,
            "India": 3021,
            "South Africa": 2890,
            "Others": 26289
        }
    }

@app.get("/health")
async def health_check():
    return {
        "status": "operational",
        "service": "visa-verification",
        "version": "1.0.0"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8107)
