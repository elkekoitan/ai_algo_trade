#!/usr/bin/env python3
"""
Unified Trading Engine Backend Startup Script
Handles dependency installation and starts the backend server
"""

import sys
import subprocess
import os
from pathlib import Path

def install_missing_dependencies():
    """Install missing dependencies"""
    required_packages = [
        'requests',
        'pandas', 
        'pydantic-settings',
        'MetaTrader5',
        'fastapi',
        'uvicorn',
        'python-multipart'
    ]
    
    print("🔍 Checking dependencies...")
    missing = []
    
    for package in required_packages:
        try:
            __import__(package.replace('-', '_'))
            print(f"✅ {package} - OK")
        except ImportError:
            print(f"❌ {package} - Missing")
            missing.append(package)
    
    if missing:
        print(f"\n📦 Installing {len(missing)} missing packages...")
        for package in missing:
            try:
                subprocess.check_call([sys.executable, '-m', 'pip', 'install', package])
                print(f"✅ Installed {package}")
            except subprocess.CalledProcessError:
                print(f"❌ Failed to install {package}")
                return False
    
    return True

def start_backend():
    """Start the unified backend server"""
    print("\n🚀 Starting Unified Trading Engine Backend...")
    
    # Add current directory to Python path
    current_dir = Path(__file__).parent
    sys.path.insert(0, str(current_dir))
    
    try:
        # Try to import and start the unified main
        from unified_main import app
        import uvicorn
        
        print("✅ Starting server on http://localhost:8002")
        uvicorn.run(app, host="0.0.0.0", port=8002, reload=True)
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("🔄 Trying alternative startup method...")
        
        # Alternative: try to run unified_main.py directly
        try:
            subprocess.run([sys.executable, "unified_main.py"])
        except Exception as e2:
            print(f"❌ Alternative startup failed: {e2}")
            return False
    
    except Exception as e:
        print(f"❌ Startup error: {e}")
        return False
    
    return True

if __name__ == "__main__":
    print("=" * 50)
    print("🤖 AI Algo Trade - Unified Backend Startup")
    print("=" * 50)
    
    # Step 1: Install dependencies
    if not install_missing_dependencies():
        print("❌ Failed to install dependencies")
        sys.exit(1)
    
    # Step 2: Start backend
    if not start_backend():
        print("❌ Failed to start backend")
        sys.exit(1)
    
    print("✅ Backend started successfully!") 