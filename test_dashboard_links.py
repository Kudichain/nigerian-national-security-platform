"""
Dashboard Link Status Check - Verify all endpoints are functional
"""
import asyncio
from fastapi.testclient import TestClient
from main import app

def test_all_endpoints():
    """Test all dashboard endpoints"""
    client = TestClient(app)
    
    endpoints = [
        # Core
        ("GET", "/health", "Health Check"),
        ("GET", "/api/v1/overview/national", "National Overview"),
        ("GET", "/api/v1/threat-level", "Threat Level"),
        ("GET", "/api/v1/alerts", "Alerts"),
        
        # Statistics
        ("GET", "/api/v1/biometric/stats", "Biometric Stats"),
        ("GET", "/api/v1/elections/stats", "INEC Stats"),
        ("GET", "/api/v1/emergency/stats", "Emergency Stats"),
        ("GET", "/api/v1/police/stats", "Police Stats"),
        
        # Verification
        ("POST", "/api/v1/visa/verify?visa_number=VISA-2025-12345&passport_number=A12345678", "Visa Verification"),
        ("POST", "/api/v1/phone/verify?phone_number=+2348012345678", "Phone Tracking"),
        
        # Infrastructure & Monitoring
        ("GET", "/api/v1/infrastructure/pipelines", "Pipeline Monitoring"),
        ("GET", "/api/v1/transportation/railway", "Railway Security"),
        ("GET", "/api/v1/law-enforcement/police", "Police Operations"),
        ("GET", "/api/v1/immigration/airport", "Airport Security"),
        ("GET", "/api/v1/media/monitoring", "Media Monitoring"),
        
        # Search & Tracking
        ("GET", "/api/v1/citizen/search", "Citizen Search"),
        ("GET", "/api/v1/vehicle/tracking", "Vehicle Tracking"),
        ("GET", "/api/v1/surveillance/cctv", "CCTV Feeds"),
        ("GET", "/api/v1/surveillance/border-cctv", "Border CCTV"),
        ("GET", "/api/v1/surveillance/tollgate-cctv", "Toll Gate CCTV"),
        ("GET", "/api/v1/drone/live", "Drone Feeds"),
        ("GET", "/api/v1/security/map", "Security Map"),
    ]
    
    print("\n" + "="*70)
    print("🔗 DASHBOARD LINK STATUS CHECK")
    print("="*70 + "\n")
    
    working = 0
    failed = 0
    
    for method, endpoint, name in endpoints:
        try:
            if method == "GET":
                response = client.get(endpoint)
            else:
                response = client.post(endpoint)
            
            if response.status_code == 200:
                print(f"✅ {name:<30} → {endpoint}")
                working += 1
            else:
                print(f"❌ {name:<30} → {endpoint} (Status: {response.status_code})")
                failed += 1
        except Exception as e:
            print(f"❌ {name:<30} → {endpoint} (Error: {str(e)[:50]})")
            failed += 1
    
    print("\n" + "="*70)
    print(f"📊 Results: {working}/{len(endpoints)} endpoints working ({working/len(endpoints)*100:.1f}%)")
    print("="*70 + "\n")
    
    if failed == 0:
        print("🎉 All dashboard links are functional!")
    else:
        print(f"⚠️  {failed} endpoints need attention")
    
    return failed == 0

if __name__ == "__main__":
    success = test_all_endpoints()
    exit(0 if success else 1)
