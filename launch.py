"""
Security Platform Quick Launch Script

This script provides easy deployment options for the AI security platform.
"""

import sys
import os
import subprocess
import time
import webbrowser
from pathlib import Path

def launch_security_monitoring():
    """Launch the security monitoring service"""
    print("🛡️ Launching AI Security Monitoring Service...")
    print("=" * 50)
    
    # Get the virtual environment Python path
    venv_python = Path("C:/Users/moham/AI/.venv/Scripts/python.exe")
    
    if not venv_python.exists():
        print("❌ Virtual environment not found!")
        print("   Please run setup first: python setup.py")
        return False
    
    # Launch the service
    service_script = Path("services/security_monitoring.py")
    
    if not service_script.exists():
        print("❌ Security monitoring service not found!")
        return False
    
    print("🚀 Starting security monitoring service...")
    print("📊 Dashboard will be available at: http://localhost:8080/")
    print()
    print("🔌 API Endpoints:")
    print("   📊 GET  /stats    - Processing statistics")
    print("   🚨 GET  /alerts   - Recent security alerts")
    print("   📥 POST /events   - Submit security events") 
    print("   ❤️  GET  /health  - Service health check")
    print("   🔌 GET  /ws      - WebSocket real-time updates")
    print()
    print("⏹️  Press Ctrl+C to stop the service")
    print("=" * 50)
    
    try:
        # Start the service
        process = subprocess.Popen(
            [str(venv_python), str(service_script)],
            cwd=Path.cwd()
        )
        
        # Wait a moment for the service to start
        time.sleep(2)
        
        # Open dashboard in browser
        try:
            webbrowser.open('http://localhost:8080/')
            print("🌐 Dashboard opened in your web browser")
        except:
            print("ℹ️  Manually navigate to: http://localhost:8080/")
        
        # Wait for the process
        process.wait()
        
    except KeyboardInterrupt:
        print("\\n🛑 Shutting down security monitoring service...")
        process.terminate()
        process.wait()
        print("✅ Service stopped successfully")
    
    except Exception as e:
        print(f"❌ Error launching service: {e}")
        return False
    
    return True

def run_validation():
    """Run platform validation"""
    print("🔍 Running Security Platform Validation...")
    
    venv_python = Path("C:/Users/moham/AI/.venv/Scripts/python.exe")
    validation_script = Path("validate_security_platform.py")
    
    if not venv_python.exists() or not validation_script.exists():
        print("❌ Required files not found!")
        return False
    
    try:
        result = subprocess.run(
            [str(venv_python), str(validation_script)],
            cwd=Path.cwd(),
            capture_output=True,
            text=True
        )
        
        print(result.stdout)
        if result.stderr:
            print("Warnings/Errors:", result.stderr)
        
        return result.returncode == 0
    
    except Exception as e:
        print(f"❌ Validation failed: {e}")
        return False

def show_menu():
    """Show the main menu"""
    print("🛡️ AI SECURITY PLATFORM - QUICK LAUNCHER")
    print("=" * 50)
    print("1. 🚀 Launch Security Monitoring Service")
    print("2. 🔍 Run Platform Validation")  
    print("3. 📊 Show Platform Status")
    print("4. ❌ Exit")
    print("=" * 50)

def show_platform_status():
    """Show current platform status"""
    print("📊 AI SECURITY PLATFORM STATUS")
    print("=" * 50)
    
    # Check key files
    key_files = [
        ("Virtual Environment", "C:/Users/moham/AI/.venv/Scripts/python.exe"),
        ("Security Features", "features/security_features.py"),
        ("Threat Detection", "features/threat_detection.py"),
        ("Advanced Features", "features/advanced_features.py"),
        ("Security Operations", "utils/security_ops.py"),
        ("Monitoring Service", "services/security_monitoring.py"),
        ("Validation Script", "validate_security_platform.py")
    ]
    
    all_ready = True
    for name, path in key_files:
        if Path(path).exists():
            print(f"✅ {name}")
        else:
            print(f"❌ {name} - Missing")
            all_ready = False
    
    print()
    if all_ready:
        print("🟢 STATUS: All components ready for deployment")
        print("🚀 Ready to launch security monitoring service!")
    else:
        print("🟡 STATUS: Some components missing")
        print("⚠️  Run setup.py to complete installation")
    
    print("=" * 50)

def main():
    """Main entry point"""
    while True:
        print()
        show_menu()
        
        try:
            choice = input("Select an option (1-4): ").strip()
            
            if choice == '1':
                launch_security_monitoring()
            elif choice == '2':
                run_validation()
            elif choice == '3':
                show_platform_status()
            elif choice == '4':
                print("👋 Goodbye! Stay secure!")
                break
            else:
                print("❌ Invalid choice. Please select 1-4.")
                
        except KeyboardInterrupt:
            print("\\n👋 Goodbye! Stay secure!")
            break
        except Exception as e:
            print(f"❌ Error: {e}")

if __name__ == "__main__":
    main()