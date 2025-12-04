"""
Photo Verification Service
Facial recognition and citizen search
"""

from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List
import random

app = FastAPI(
    title="📸 Photo Verification Service",
    version="1.0.0",
    description="Facial Recognition & Citizen Search System"
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
class FaceMatch(BaseModel):
    name: str
    nin: str
    confidence: float
    location: str
    photo: str
    age: int
    gender: str
    last_seen: str

class PhotoVerificationResponse(BaseModel):
    matches: List[FaceMatch]
    total_matches: int
    processing_time: str
    image_quality: str

# Mock citizen database
CITIZEN_DATABASE = [
    {
        "name": "Adewale Ogunleye",
        "nin": "NIN-45678901",
        "photo": "https://randomuser.me/api/portraits/men/22.jpg",
        "location": "Lagos, Victoria Island",
        "age": 34,
        "gender": "Male",
        "last_seen": "2025-11-30"
    },
    {
        "name": "Ngozi Eze",
        "nin": "NIN-78901234",
        "photo": "https://randomuser.me/api/portraits/women/35.jpg",
        "location": "Abuja, Wuse 2",
        "age": 28,
        "gender": "Female",
        "last_seen": "2025-11-29"
    },
    {
        "name": "Ibrahim Suleiman",
        "nin": "NIN-23456789",
        "photo": "https://randomuser.me/api/portraits/men/45.jpg",
        "location": "Kano, Sabon Gari",
        "age": 41,
        "gender": "Male",
        "last_seen": "2025-11-28"
    },
    {
        "name": "Grace Okoro",
        "nin": "NIN-56789012",
        "photo": "https://randomuser.me/api/portraits/women/52.jpg",
        "location": "Port Harcourt, GRA",
        "age": 36,
        "gender": "Female",
        "last_seen": "2025-11-27"
    },
    {
        "name": "Ahmed Bello",
        "nin": "NIN-89012345",
        "photo": "https://randomuser.me/api/portraits/men/67.jpg",
        "location": "Kaduna, Barnawa",
        "age": 39,
        "gender": "Male",
        "last_seen": "2025-11-26"
    },
    {
        "name": "Blessing Ajayi",
        "nin": "NIN-12309876",
        "photo": "https://randomuser.me/api/portraits/women/64.jpg",
        "location": "Ibadan, Bodija",
        "age": 31,
        "gender": "Female",
        "last_seen": "2025-11-25"
    }
]

@app.post("/api/v1/photo/verify")
async def verify_photo(file: UploadFile = File(...)):
    """Search for citizens matching uploaded photo"""
    
    # Validate file type
    if not file.content_type or not file.content_type.startswith('image/'):
        raise HTTPException(status_code=400, detail="Invalid file type. Please upload an image file.")
    
    # Simulate facial recognition analysis
    # In production, this would use actual face recognition AI (e.g., Azure Face API, AWS Rekognition, DeepFace)
    
    num_matches = random.randint(1, 4)
    matches = random.sample(CITIZEN_DATABASE, min(num_matches, len(CITIZEN_DATABASE)))
    
    results = []
    for i, match in enumerate(matches):
        # Higher confidence for first match
        if i == 0:
            confidence = round(random.uniform(92.0, 99.5), 1)
        elif i == 1:
            confidence = round(random.uniform(75.0, 89.0), 1)
        else:
            confidence = round(random.uniform(60.0, 74.0), 1)
        
        results.append({
            "name": match["name"],
            "nin": match["nin"],
            "confidence": confidence,
            "location": match["location"],
            "photo": match["photo"],
            "age": match["age"],
            "gender": match["gender"],
            "last_seen": match["last_seen"]
        })
    
    # Sort by confidence
    results.sort(key=lambda x: x["confidence"], reverse=True)
    
    return {
        "matches": results,
        "total_matches": len(results),
        "processing_time": f"{random.randint(1200, 3000)}ms",
        "image_quality": random.choice(["Excellent", "Good", "Fair"]),
        "face_detected": True,
        "analysis_details": {
            "face_count": 1,
            "face_quality": random.choice(["High", "Medium"]),
            "lighting": random.choice(["Good", "Fair"]),
            "angle": "Frontal",
            "resolution": "High"
        }
    }

@app.get("/api/v1/photo/statistics")
async def get_photo_statistics():
    """Get photo verification statistics"""
    return {
        "total_face_records": 12847631,
        "searches_today": 8932,
        "average_matches": 2.3,
        "average_confidence": 87.4,
        "high_confidence_rate": 76.8,
        "by_quality": {
            "Excellent": 5234,
            "Good": 2890,
            "Fair": 808
        }
    }

@app.get("/health")
async def health_check():
    return {
        "status": "operational",
        "service": "photo-verification",
        "version": "1.0.0"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8109)
