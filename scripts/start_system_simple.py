#!/usr/bin/env python3
"""
Simple System Starter for AI Algo Trade
"""

import subprocess
import time
import sys
import os
from pathlib import Path

def start_backend():
    """Start backend"""
    print("🚀 Starting backend...")
    try:
        backend_process = subprocess.Popen([
            sys.executable, "backend/simple_mt5_backend.py"
        ])
        print(f"✅ Backend started (PID: {backend_process.pid})")
        return backend_process
    except Exception as e:
        print(f"❌ Backend start failed: {e}")
        return None

def start_frontend():
    """Start frontend"""
    print("🎨 Starting frontend...")
    try:
        frontend_process = subprocess.Popen([
            "npm", "run", "dev"
        ], cwd="frontend")
        print(f"✅ Frontend started (PID: {frontend_process.pid})")
        return frontend_process
    except Exception as e:
        print(f"❌ Frontend start failed: {e}")
        return None

def start_copy_trading():
    """Start copy trading"""
    print("📈 Starting copy trading...")
    try:
        copy_process = subprocess.Popen([
            sys.executable, "launch_copy_trading.py"
        ])
        print(f"✅ Copy trading started (PID: {copy_process.pid})")
        return copy_process
    except Exception as e:
        print(f"❌ Copy trading start failed: {e}")
        return None

def main():
    print("🎯 AI Algo Trade - System Startup")
    print("=" * 40)
    
    # Start all services
    backend = start_backend()
    time.sleep(5)
    
    frontend = start_frontend()
    time.sleep(5)
    
    copy_trading = start_copy_trading()
    
    print("\n✅ All services started!")
    print("🔗 Backend: http://localhost:8002")
    print("🎨 Frontend: http://localhost:3000")
    print("📈 Copy Trading: Active")
    print("\n💡 Press Ctrl+C to stop all services")
    
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n👋 Stopping services...")
        if backend:
            backend.terminate()
        if frontend:
            frontend.terminate()
        if copy_trading:
            copy_trading.terminate()

if __name__ == "__main__":
    main() 