"""
Backend startup script for testing environment.
Starts the backend with minimal configuration for smoke testing.
"""

import os
import sys
import subprocess
import time
import requests
import signal
from pathlib import Path

# Add backend to Python path
backend_path = Path(__file__).parent.parent / "backend"
sys.path.insert(0, str(backend_path))

def check_backend_health(base_url="http://localhost:8002", timeout=10):
    """Check if backend is responding."""
    try:
        response = requests.get(f"{base_url}/health", timeout=timeout)
        return response.status_code == 200
    except:
        return False

def start_backend():
    """Start the backend using uvicorn."""
    print("🚀 Starting AI Algo Trade Backend for testing...")
    
    # Change to backend directory
    backend_dir = Path(__file__).parent.parent / "backend"
    os.chdir(backend_dir)
    
    # Start uvicorn
    cmd = [
        sys.executable, "-m", "uvicorn", 
        "main:app",
        "--host", "0.0.0.0",
        "--port", "8002", 
        "--reload",
        "--log-level", "info"
    ]
    
    print(f"Running command: {' '.join(cmd)}")
    print(f"Working directory: {backend_dir}")
    
    try:
        # Start the process
        process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            universal_newlines=True,
            bufsize=1
        )
        
        print("⏳ Waiting for backend to start...")
        
        # Wait for backend to be ready
        for i in range(30):  # Wait up to 30 seconds
            if check_backend_health():
                print("✅ Backend is ready!")
                return process
            print(f"   Waiting... ({i+1}/30)")
            time.sleep(1)
        
        print("❌ Backend failed to start within timeout")
        process.terminate()
        return None
        
    except Exception as e:
        print(f"❌ Error starting backend: {e}")
        return None

def stop_backend(process):
    """Stop the backend process."""
    if process:
        print("🛑 Stopping backend...")
        process.terminate()
        try:
            process.wait(timeout=5)
        except subprocess.TimeoutExpired:
            process.kill()
        print("✅ Backend stopped")

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Start backend for testing")
    parser.add_argument("--keep-running", action="store_true", 
                       help="Keep backend running (don't auto-stop)")
    args = parser.parse_args()
    
    process = start_backend()
    
    if process and args.keep_running:
        print("Backend is running. Press Ctrl+C to stop...")
        try:
            # Keep running until interrupted
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            stop_backend(process)
    elif process:
        print("Backend started successfully for testing")
        stop_backend(process)
