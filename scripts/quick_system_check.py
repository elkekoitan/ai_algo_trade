#!/usr/bin/env python3
"""
Quick System Check for AI Algo Trade
"""

import subprocess
import time
import sys
from pathlib import Path

def run_command(cmd, timeout=10):
    """Run command safely with timeout"""
    try:
        result = subprocess.run(
            cmd, 
            shell=True, 
            capture_output=True, 
            text=True, 
            timeout=timeout
        )
        return result.returncode == 0, result.stdout, result.stderr
    except subprocess.TimeoutExpired:
        return False, "", "Command timed out"
    except Exception as e:
        return False, "", str(e)

def check_port(port):
    """Check if port is in use"""
    success, stdout, stderr = run_command(f"netstat -an | findstr :{port}")
    return port in stdout if success else False

def check_process(name):
    """Check if process is running"""
    success, stdout, stderr = run_command(f"tasklist | findstr {name}")
    return name in stdout if success else False

def main():
    print("🔍 AI Algo Trade - Quick System Check")
    print("=" * 50)
    
    # Check current directory
    current_dir = Path.cwd()
    print(f"📁 Current Directory: {current_dir}")
    
    # Check key files
    key_files = [
        "backend/simple_mt5_backend.py",
        "frontend/package.json",
        "launch_copy_trading.py",
        "start_complete_system.py"
    ]
    
    print("\n📋 File Check:")
    for file_path in key_files:
        exists = (current_dir / file_path).exists()
        status = "✅" if exists else "❌"
        print(f"  {status} {file_path}")
    
    # Check ports
    print("\n🌐 Port Check:")
    ports = {"Backend": 8002, "Frontend": 3000}
    for name, port in ports.items():
        in_use = check_port(port)
        status = "✅" if in_use else "❌"
        print(f"  {status} {name} (Port {port})")
    
    # Check processes
    print("\n🔄 Process Check:")
    processes = {"Python": "python", "Node": "node"}
    for name, proc in processes.items():
        running = check_process(proc)
        status = "✅" if running else "❌"
        print(f"  {status} {name} processes")
    
    # Check Python environment
    print("\n🐍 Python Environment:")
    try:
        import MetaTrader5
        print("  ✅ MetaTrader5 available")
    except ImportError:
        print("  ❌ MetaTrader5 not available")
    
    try:
        import fastapi
        print("  ✅ FastAPI available")
    except ImportError:
        print("  ❌ FastAPI not available")
    
    # Try to start backend if not running
    if not check_port(8002):
        print("\n🚀 Backend not running, attempting to start...")
        try:
            # Start backend in background
            subprocess.Popen([
                sys.executable, 
                "backend/simple_mt5_backend.py"
            ], cwd=current_dir)
            print("  ⏳ Backend starting...")
            
            # Wait and check
            time.sleep(5)
            if check_port(8002):
                print("  ✅ Backend started successfully!")
            else:
                print("  ⚠️ Backend may still be starting...")
        except Exception as e:
            print(f"  ❌ Failed to start backend: {e}")
    
    # Try to start frontend if not running  
    if not check_port(3000):
        print("\n🎨 Frontend not running, attempting to start...")
        try:
            # Start frontend in background
            subprocess.Popen([
                "npm", "run", "dev"
            ], cwd=current_dir / "frontend")
            print("  ⏳ Frontend starting...")
            
            # Wait and check
            time.sleep(5)
            if check_port(3000):
                print("  ✅ Frontend started successfully!")
            else:
                print("  ⏳ Frontend may still be starting...")
        except Exception as e:
            print(f"  ❌ Failed to start frontend: {e}")
    
    print("\n" + "=" * 50)
    print("🎯 System Status Summary:")
    
    backend_running = check_port(8002)
    frontend_running = check_port(3000)
    
    if backend_running and frontend_running:
        print("🟢 System Status: FULLY OPERATIONAL")
        print("🔗 Backend: http://localhost:8002")
        print("🎨 Frontend: http://localhost:3000")
    elif backend_running or frontend_running:
        print("🟡 System Status: PARTIALLY RUNNING")
        if backend_running:
            print("✅ Backend: http://localhost:8002")
        if frontend_running:
            print("✅ Frontend: http://localhost:3000")
    else:
        print("🔴 System Status: NOT RUNNING")
        print("💡 Run this script again to attempt restart")
    
    print("\n💻 Next steps:")
    print("- Open http://localhost:3000 for the dashboard")
    print("- Check http://localhost:8002/docs for API documentation")
    print("- Monitor logs for any issues")
    print("=" * 50)

if __name__ == "__main__":
    main() 