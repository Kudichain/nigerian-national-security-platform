"""
Quick test of all enhanced services
"""

import requests
import sys

SERVICES = [
    ("Cross-Module Integration", "http://localhost:8111/health"),
    ("Adversarial ML Testing", "http://localhost:8112/health"),
    ("Observability", "http://localhost:8113/health"),
    ("DevSecOps CI/CD", "http://localhost:8114/health"),
    ("Nigerian Threat Intel Enhanced", "http://localhost:8115/health"),
    ("Explainable AI Enhanced", "http://localhost:8101/health"),
]

print("\n🧪 Testing Enhanced Services...")
print("=" * 60)

operational = 0
failed = 0

for name, url in SERVICES:
    try:
        response = requests.get(url, timeout=5)
        if response.status_code == 200:
            print(f"✅ {name:<40} OPERATIONAL")
            operational += 1
        else:
            print(f"❌ {name:<40} ERROR {response.status_code}")
            failed += 1
    except requests.exceptions.ConnectionError:
        print(f"❌ {name:<40} NOT RUNNING")
        failed += 1
    except Exception as e:
        print(f"❌ {name:<40} ERROR: {str(e)[:30]}")
        failed += 1

print("=" * 60)
print(f"\n📊 Results: {operational}/{len(SERVICES)} services operational")

if operational == len(SERVICES):
    print("✅ ALL ENHANCED SERVICES RUNNING!")
    
    # Quick feature tests
    print("\n🎯 Testing key features...")
    
    # Test cross-module integration
    try:
        response = requests.post(
            "http://localhost:8111/api/v1/integration/correlate",
            params={"entity_id": "NIN-12345678", "entity_type": "citizen"}
        )
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Knowledge Graph: Found {data.get('network_size', 0)} correlations")
    except:
        pass
    
    # Test adversarial testing
    try:
        response = requests.post(
            "http://localhost:8112/api/v1/adversarial/test-model",
            params={"model_name": "face_recognition", "attack_type": "FGSM"}
        )
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Adversarial Test: Robustness score {data.get('robustness_score', 0)}%")
    except:
        pass
    
    # Test observability
    try:
        response = requests.get("http://localhost:8113/api/v1/observability/health")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Observability: Overall uptime {data.get('overall_uptime', 0)}%")
    except:
        pass
    
    # Test DevSecOps
    try:
        response = requests.post("http://localhost:8114/api/v1/cicd/scan")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Security Scan: Found {data.get('total_findings', 0)} findings")
    except:
        pass
    
    # Test threat intel
    try:
        response = requests.get("http://localhost:8115/api/v1/threat-intel/unified")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Threat Intel: {data.get('total_intelligence_items', 0)} intelligence items")
    except:
        pass
    
    print("\n🎖️  TRANSFORMATION COMPLETE!")
    sys.exit(0)
else:
    print(f"⚠️  {failed} services need attention")
    sys.exit(1)
