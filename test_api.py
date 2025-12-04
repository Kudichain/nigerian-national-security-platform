"""
Test if main.py works without uvicorn shutting down
"""
import sys
import asyncio
from main import app

async def test_endpoints():
    """Test basic endpoint responses"""
    print("Testing endpoints...")
    
    # Import test client
    from fastapi.testclient import TestClient
    client = TestClient(app)
    
    # Test health
    response = client.get("/health")
    print(f"✓ Health: {response.status_code}")
    
    # Test overview
    response = client.get("/api/v1/overview/national")
    print(f"✓ Overview: {response.status_code}")
    
    # Test threat level
    response = client.get("/api/v1/threat-level")
    print(f"✓ Threat Level: {response.status_code}")
    
    # Test visa
    response = client.post("/api/v1/visa/verify?visa_number=VISA-2025-12345&passport_number=A12345678")
    print(f"✓ Visa Verify: {response.status_code}")
    
    print("\nAll endpoints working! ✅")

if __name__ == "__main__":
    asyncio.run(test_endpoints())
