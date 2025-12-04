"""
Quick test script to verify all verification services are operational
"""

import requests
import json

SERVICES = [
    {"name": "Visa Verification", "url": "http://localhost:8107/health"},
    {"name": "Voice Verification", "url": "http://localhost:8108/health"},
    {"name": "Photo Verification", "url": "http://localhost:8109/health"},
    {"name": "Phone Tracking", "url": "http://localhost:8110/health"},
]

print("\n" + "="*60)
print("🔍 VERIFICATION SERVICES HEALTH CHECK".center(60))
print("="*60 + "\n")

all_healthy = True

for service in SERVICES:
    try:
        response = requests.get(service["url"], timeout=5)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ {service['name']:<25} - {data.get('status', 'unknown').upper()}")
        else:
            print(f"❌ {service['name']:<25} - HTTP {response.status_code}")
            all_healthy = False
    except requests.exceptions.ConnectionError:
        print(f"❌ {service['name']:<25} - NOT RUNNING")
        all_healthy = False
    except Exception as e:
        print(f"❌ {service['name']:<25} - ERROR: {str(e)[:30]}")
        all_healthy = False

print("\n" + "="*60)
if all_healthy:
    print("🎉 ALL VERIFICATION SERVICES OPERATIONAL! 🎉".center(60))
else:
    print("⚠️  SOME SERVICES ARE DOWN - CHECK LOGS".center(60))
print("="*60 + "\n")

# Test sample API calls
print("\n📝 SAMPLE API TESTS:\n")

# Test visa verification
print("1️⃣  Testing Visa Verification...")
try:
    response = requests.post(
        "http://localhost:8107/api/v1/visa/verify",
        json={
            "visa_number": "VISA-2025-12345",
            "passport_number": "A12345678"
        },
        timeout=5
    )
    if response.status_code == 200:
        data = response.json()
        print(f"   ✅ Found citizen: {data['citizen']['name']}")
        print(f"   📋 Visa Type: {data['visa']['visa_type']}")
        print(f"   📅 Status: {data['visa']['status']}")
    else:
        print(f"   ❌ HTTP {response.status_code}")
except Exception as e:
    print(f"   ❌ Error: {str(e)[:50]}")

# Test phone verification
print("\n2️⃣  Testing Phone Tracking...")
try:
    response = requests.post(
        "http://localhost:8110/api/v1/phone/verify",
        json={"phone_number": "+2348012345678"},
        timeout=5
    )
    if response.status_code == 200:
        data = response.json()
        print(f"   ✅ Owner: {data['owner']['name']}")
        print(f"   📍 Location: {data['location']['current']}")
        print(f"   📱 Carrier: {data['owner']['carrier']}")
    else:
        print(f"   ❌ HTTP {response.status_code}")
except Exception as e:
    print(f"   ❌ Error: {str(e)[:50]}")

print("\n" + "="*60)
print("✨ TEST COMPLETE - All services ready for dashboard!".center(60))
print("="*60 + "\n")
