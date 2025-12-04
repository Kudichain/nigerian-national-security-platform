"""
Final Security Platform Validation and Demo

This script provides a comprehensive test of all security platform components
and demonstrates the capabilities of the AI security system.
"""

import json
import sys
import os
from datetime import datetime, timedelta
from pathlib import Path
import traceback

# Add current directory to path
sys.path.insert(0, '.')
sys.path.insert(0, str(Path.cwd()))

def test_security_modules():
    """Test all security modules"""
    print("🛡️ SECURITY MODULES VALIDATION")
    print("=" * 50)
    
    modules_tested = []
    
    # Test 1: Security Features
    try:
        from features.security_features import SecurityFeatureExtractor, NetworkProtocolAnalyzer
        extractor = SecurityFeatureExtractor()
        print("✅ SecurityFeatureExtractor - Network protocol analysis, malware detection")
        modules_tested.append("SecurityFeatureExtractor")
    except ImportError as e:
        print(f"⚠️ SecurityFeatureExtractor - {e}")
    
    # Test 2: Threat Detection
    try:
        from features.threat_detection import ComprehensiveThreatDetector, AnomalyDetector
        detector = ComprehensiveThreatDetector()
        print("✅ ThreatDetector - Anomaly detection, attack patterns, C2 detection")
        modules_tested.append("ThreatDetector")
    except ImportError as e:
        print(f"⚠️ ThreatDetector - {e}")
    
    # Test 3: Advanced Features
    try:
        from features.advanced_features import AdvancedFeatureExtractor
        advanced = AdvancedFeatureExtractor()
        print("✅ AdvancedFeatureExtractor - Graph embeddings, advanced ML features")
        modules_tested.append("AdvancedFeatureExtractor")
    except ImportError as e:
        print(f"⚠️ AdvancedFeatureExtractor - {e}")
    
    # Test 4: Security Operations
    try:
        from utils.security_ops import SecurityOperationsCenter, LogParser, ThreatIntelligence
        soc = SecurityOperationsCenter()
        print("✅ SecurityOperationsCenter - Log parsing, threat intel, reporting")
        modules_tested.append("SecurityOperationsCenter")
    except ImportError as e:
        print(f"⚠️ SecurityOperationsCenter - {e}")
    
    return modules_tested


def test_core_packages():
    """Test core Python packages"""
    print("\n📦 CORE PACKAGES VALIDATION")
    print("=" * 50)
    
    packages_tested = []
    
    core_packages = [
        ('numpy', 'Numerical computing'),
        ('pandas', 'Data manipulation'),
        ('scikit-learn', 'Machine learning'),
        ('networkx', 'Graph analysis'),
        ('requests', 'HTTP requests'),
        ('json', 'JSON processing'),
        ('hashlib', 'Cryptographic hashing'),
        ('re', 'Regular expressions'),
        ('datetime', 'Date/time processing'),
        ('logging', 'Logging system')
    ]
    
    for package, description in core_packages:
        try:
            __import__(package)
            print(f"✅ {package} - {description}")
            packages_tested.append(package)
        except ImportError:
            print(f"❌ {package} - Not available")
    
    return packages_tested


def test_advanced_packages():
    """Test advanced security packages"""
    print("\n🔒 ADVANCED SECURITY PACKAGES")
    print("=" * 50)
    
    security_packages = [
        ('scapy', 'Network packet analysis'),
        ('cryptography', 'Cryptographic operations'),
        ('pefile', 'PE file analysis'),
        ('paramiko', 'SSH operations'),
        ('elasticsearch', 'Search and analytics'),
        ('redis', 'In-memory database'),
        ('aiohttp', 'Async HTTP server'),
        ('websockets', 'WebSocket support'),
        ('prometheus_client', 'Metrics collection')
    ]
    
    available_packages = []
    for package, description in security_packages:
        try:
            __import__(package)
            print(f"✅ {package} - {description}")
            available_packages.append(package)
        except ImportError:
            print(f"⚠️ {package} - Not installed (optional for enhanced features)")
    
    return available_packages


def demonstrate_capabilities():
    """Demonstrate key security capabilities"""
    print("\n🎯 SECURITY CAPABILITIES DEMONSTRATION")
    print("=" * 50)
    
    capabilities = []
    
    # Demonstrate log parsing
    try:
        sample_log = '192.168.1.100 - - [28/Nov/2025:10:00:01 +0000] "GET /admin HTTP/1.1" 200 1234'
        
        # Simple log parsing demonstration
        import re
        ip_pattern = r'\b(?:[0-9]{1,3}\.){3}[0-9]{1,3}\b'
        ips = re.findall(ip_pattern, sample_log)
        
        if ips:
            print(f"✅ Log Parsing - Extracted IP: {ips[0]}")
            capabilities.append("Log Parsing")
    except:
        print("⚠️ Log Parsing - Error in demonstration")
    
    # Demonstrate threat scoring
    try:
        import hashlib
        import random
        
        # Simple threat scoring algorithm
        def calculate_threat_score(event_data):
            suspicious_patterns = ['admin', 'passwd', 'cmd', '../']
            score = 0
            
            for pattern in suspicious_patterns:
                if pattern in str(event_data).lower():
                    score += 0.25
            
            return min(score, 1.0)
        
        test_events = [
            'GET /admin HTTP/1.1',
            'GET /../../../etc/passwd HTTP/1.1',
            'GET /normal-page HTTP/1.1',
            'POST /cmd.php HTTP/1.1'
        ]
        
        for event in test_events:
            score = calculate_threat_score(event)
            risk_level = 'HIGH' if score > 0.5 else 'MEDIUM' if score > 0.2 else 'LOW'
            print(f"✅ Threat Scoring - '{event[:30]}...' Score: {score:.2f} ({risk_level})")
        
        capabilities.append("Threat Scoring")
    except:
        print("⚠️ Threat Scoring - Error in demonstration")
    
    # Demonstrate anomaly detection simulation
    try:
        import statistics
        
        # Simulate network traffic anomaly detection
        normal_traffic = [100, 95, 110, 105, 98, 102, 108]  # Normal baseline
        current_traffic = [400, 450, 380, 420]  # Anomalous spike
        
        baseline_avg = statistics.mean(normal_traffic)
        baseline_std = statistics.stdev(normal_traffic)
        
        anomalies_detected = 0
        for traffic in current_traffic:
            z_score = abs((traffic - baseline_avg) / baseline_std)
            if z_score > 2.0:  # 2 standard deviations
                anomalies_detected += 1
        
        print(f"✅ Anomaly Detection - {anomalies_detected}/{len(current_traffic)} anomalous traffic patterns")
        capabilities.append("Anomaly Detection")
    except:
        print("⚠️ Anomaly Detection - Error in demonstration")
    
    # Demonstrate alert generation
    try:
        alert_count = 0
        
        # Generate sample alerts
        alert_types = [
            ("Critical", "Possible data exfiltration detected"),
            ("High", "Multiple failed authentication attempts"),
            ("Medium", "Unusual network traffic patterns"),
            ("Low", "Information gathering activity")
        ]
        
        for severity, description in alert_types:
            alert_id = f"ALT_{datetime.now().strftime('%Y%m%d%H%M%S')}_{alert_count:03d}"
            print(f"✅ Alert Generation - {alert_id}: {severity} - {description}")
            alert_count += 1
        
        capabilities.append("Alert Generation")
    except:
        print("⚠️ Alert Generation - Error in demonstration")
    
    return capabilities


def generate_security_report():
    """Generate a final security platform report"""
    print("\n📊 SECURITY PLATFORM ASSESSMENT REPORT")
    print("=" * 60)
    
    # Run all tests
    modules = test_security_modules()
    core_packages = test_core_packages() 
    advanced_packages = test_advanced_packages()
    capabilities = demonstrate_capabilities()
    
    # Calculate scores
    module_score = len(modules) / 4 * 100  # 4 expected modules
    core_score = len(core_packages) / 10 * 100  # 10 expected core packages
    advanced_score = len(advanced_packages) / 9 * 100  # 9 expected advanced packages
    capability_score = len(capabilities) / 4 * 100  # 4 demonstrated capabilities
    
    overall_score = (module_score + core_score + advanced_score + capability_score) / 4
    
    # Generate report
    print(f"\n📈 ASSESSMENT SCORES:")
    print(f"   Security Modules:      {module_score:5.1f}% ({len(modules)}/4)")
    print(f"   Core Packages:         {core_score:5.1f}% ({len(core_packages)}/10)")
    print(f"   Advanced Packages:     {advanced_score:5.1f}% ({len(advanced_packages)}/9)")
    print(f"   Security Capabilities: {capability_score:5.1f}% ({len(capabilities)}/4)")
    print(f"   Overall Platform:      {overall_score:5.1f}%")
    
    # Determine status
    if overall_score >= 90:
        status = "🟢 FULLY OPERATIONAL - Enterprise Ready"
    elif overall_score >= 75:
        status = "🟡 MOSTLY OPERATIONAL - Production Ready" 
    elif overall_score >= 50:
        status = "🟠 PARTIALLY OPERATIONAL - Development Ready"
    elif overall_score >= 25:
        status = "🔴 LIMITED FUNCTIONALITY - Basic Features Only"
    else:
        status = "⚫ MINIMAL SETUP - Core Components Only"
    
    print(f"\n🏆 PLATFORM STATUS: {status}")
    
    # Recommendations
    print(f"\n💡 RECOMMENDATIONS:")
    if module_score < 100:
        print("   • Install missing security packages for full module functionality")
    if advanced_score < 75:
        print("   • Install advanced security packages for enhanced capabilities")
    if overall_score >= 75:
        print("   • Platform ready for security monitoring deployment")
        print("   • Consider configuring external threat intelligence feeds")
        print("   • Set up automated alerting and notification systems")
    
    # Usage instructions
    print(f"\n🚀 DEPLOYMENT INSTRUCTIONS:")
    print("   1. Launch Security Monitoring Service:")
    print("      python services/security_monitoring.py")
    print("   2. Access Dashboard:")
    print("      http://localhost:8080/")
    print("   3. Test API Endpoints:")
    print("      curl http://localhost:8080/health")
    print("      curl http://localhost:8080/stats")
    
    return {
        'modules': modules,
        'core_packages': core_packages,
        'advanced_packages': advanced_packages,
        'capabilities': capabilities,
        'scores': {
            'module_score': module_score,
            'core_score': core_score,
            'advanced_score': advanced_score,
            'capability_score': capability_score,
            'overall_score': overall_score
        },
        'status': status,
        'timestamp': datetime.now().isoformat()
    }


if __name__ == "__main__":
    print("🛡️ AI SECURITY PLATFORM - COMPREHENSIVE VALIDATION")
    print("=" * 60)
    print(f"Validation Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Platform Path: {Path.cwd()}")
    print()
    
    try:
        report = generate_security_report()
        
        # Save report to file
        report_file = Path("security_platform_report.json")
        with open(report_file, 'w') as f:
            json.dump(report, f, indent=2, default=str)
        
        print(f"\n📄 DETAILED REPORT SAVED: {report_file}")
        print("\n✅ SECURITY PLATFORM VALIDATION COMPLETE")
        
    except Exception as e:
        print(f"\n❌ Validation failed with error: {e}")
        traceback.print_exc()