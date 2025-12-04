"""
Phone Number Verification & Tracking Service
Real-time location and carrier integration
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime, timedelta
import random

app = FastAPI(
    title="📱 Phone Tracking Service",
    version="1.0.0",
    description="Phone Number Verification & Real-Time Location Tracking"
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
class PhoneVerificationRequest(BaseModel):
    phone_number: str

class OwnerInfo(BaseModel):
    name: str
    nin: str
    carrier: str
    registered_date: str
    sim_status: str
    photo: str
    alternate_numbers: List[str]

class LocationInfo(BaseModel):
    current: str
    coordinates: dict
    last_seen: str
    history: List[dict]
    cell_tower: str

class PhoneVerificationResponse(BaseModel):
    registered: bool
    owner: OwnerInfo
    location: LocationInfo
    activity: dict
    warnings: List[str]

# Mock phone database
PHONE_DATABASE = {
    "+2348012345678": {
        "owner": {
            "name": "Oluwaseun Adeyemi",
            "nin": "NIN-99887766",
            "carrier": "MTN Nigeria",
            "registered_date": "2023-05-10",
            "sim_status": "Active",
            "photo": "https://randomuser.me/api/portraits/men/33.jpg",
            "alternate_numbers": ["+2349012345678", "+2347012345678"]
        },
        "location_history": [
            {"location": "Lagos, Victoria Island", "timestamp": "2025-12-01 14:23:45", "lat": 6.4281, "lng": 3.4219},
            {"location": "Lagos, Lekki", "timestamp": "2025-12-01 10:15:30", "lat": 6.4474, "lng": 3.5486},
            {"location": "Lagos, Ikeja", "timestamp": "2025-11-30 18:42:12", "lat": 6.5964, "lng": 3.3425}
        ]
    },
    "+2349087654321": {
        "owner": {
            "name": "Fatima Abubakar",
            "nin": "NIN-55443322",
            "carrier": "Airtel Nigeria",
            "registered_date": "2022-08-15",
            "sim_status": "Active",
            "photo": "https://randomuser.me/api/portraits/women/45.jpg",
            "alternate_numbers": ["+2348087654321"]
        },
        "location_history": [
            {"location": "Abuja, Wuse 2", "timestamp": "2025-12-01 13:45:22", "lat": 9.0720, "lng": 7.4905},
            {"location": "Abuja, Garki", "timestamp": "2025-12-01 09:30:15", "lat": 9.0369, "lng": 7.4908},
            {"location": "Kaduna, Barnawa", "timestamp": "2025-11-30 16:20:45", "lat": 10.5167, "lng": 7.4333}
        ]
    },
    "+2347098765432": {
        "owner": {
            "name": "Chinedu Okonkwo",
            "nin": "NIN-11224488",
            "carrier": "Glo Mobile",
            "registered_date": "2024-02-20",
            "sim_status": "Active",
            "photo": "https://randomuser.me/api/portraits/men/58.jpg",
            "alternate_numbers": []
        },
        "location_history": [
            {"location": "Port Harcourt, GRA", "timestamp": "2025-12-01 15:10:33", "lat": 4.8156, "lng": 7.0498},
            {"location": "Port Harcourt, Trans Amadi", "timestamp": "2025-12-01 11:05:18", "lat": 4.8014, "lng": 6.9988},
            {"location": "Owerri, New Owerri", "timestamp": "2025-11-30 14:55:27", "lat": 5.4840, "lng": 7.0351}
        ]
    }
}

@app.post("/api/v1/phone/verify")
async def verify_phone(request: PhoneVerificationRequest):
    """Verify phone number and get real-time location"""
    
    phone_number = request.phone_number.strip()
    
    # Check if number exists
    if phone_number not in PHONE_DATABASE:
        # Try variations
        for key in PHONE_DATABASE.keys():
            if key.endswith(phone_number[-10:]):
                phone_number = key
                break
        else:
            raise HTTPException(status_code=404, detail="Phone number not registered in national database")
    
    data = PHONE_DATABASE[phone_number]
    
    # Get current location (most recent)
    current_location = data["location_history"][0]
    
    # Generate warnings
    warnings = []
    if len(data["owner"]["alternate_numbers"]) > 2:
        warnings.append("⚠️ Multiple phone numbers registered to this NIN")
    
    # Check for suspicious activity
    if random.random() < 0.1:  # 10% chance
        warnings.append("🚨 Suspicious activity detected - Multiple location changes in short time")
    
    return {
        "registered": True,
        "owner": data["owner"],
        "location": {
            "current": current_location["location"],
            "coordinates": {
                "latitude": current_location["lat"],
                "longitude": current_location["lng"]
            },
            "last_seen": current_location["timestamp"],
            "history": [
                {
                    "location": loc["location"],
                    "timestamp": loc["timestamp"],
                    "duration": f"{random.randint(15, 240)} minutes"
                }
                for loc in data["location_history"][:5]
            ],
            "cell_tower": f"TOWER-{random.randint(1000, 9999)}"
        },
        "activity": {
            "calls_today": random.randint(5, 25),
            "sms_today": random.randint(10, 50),
            "data_usage_mb": random.randint(50, 500),
            "last_call": f"{random.randint(1, 120)} minutes ago",
            "roaming": False
        },
        "warnings": warnings
    }

@app.get("/api/v1/phone/statistics")
async def get_phone_statistics():
    """Get phone tracking statistics"""
    return {
        "total_registered_numbers": 185234567,
        "active_numbers": 142567890,
        "tracked_today": 45234,
        "by_carrier": {
            "MTN Nigeria": 78234567,
            "Airtel Nigeria": 42567890,
            "Glo Mobile": 28234567,
            "9mobile": 12345678,
            "Others": 23851865
        },
        "location_accuracy": "95.7%",
        "average_response_time": "1.2 seconds"
    }

@app.post("/api/v1/phone/track-history")
async def track_phone_history(request: PhoneVerificationRequest, days: int = 7):
    """Get detailed location history for a phone number"""
    
    phone_number = request.phone_number.strip()
    
    if phone_number not in PHONE_DATABASE:
        raise HTTPException(status_code=404, detail="Phone number not found")
    
    data = PHONE_DATABASE[phone_number]
    
    return {
        "phone_number": phone_number,
        "owner": data["owner"]["name"],
        "nin": data["owner"]["nin"],
        "history_period": f"Last {days} days",
        "locations": data["location_history"],
        "total_locations": len(data["location_history"]),
        "unique_cities": len(set(loc["location"].split(",")[0] for loc in data["location_history"]))
    }

@app.get("/health")
async def health_check():
    return {
        "status": "operational",
        "service": "phone-tracking",
        "version": "1.0.0"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8110)
