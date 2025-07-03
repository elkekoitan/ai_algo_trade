#!/usr/bin/env python3
"""
AI Algo Trade - Complete System Startup Script
Tek komutla tüm sistemi ayağa kaldırır, sağlık kontrolü yapar ve hazır hale getirir.
"""

import os
import sys
import time
import subprocess
import threading
import requests
from pathlib import Path
import logging
import asyncio
import json
from datetime import datetime

# Logging setup
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("SystemStarter")

class AIAlgoTradeSystemStarter:
    def __init__(self):
        self.project_root = Path(__file__).resolve().parent
        self.backend_process = None
        self.frontend_process = None
        self.backend_port = 8000
        self.frontend_port = 3000
        self.startup_timeout = 60  # seconds
        
        # Default login credentials (MT5 Demo)
        self.default_credentials = {
            "mt5_login": 25201110,
            "mt5_password": "e|([rXU1IsiM",
            "mt5_server": "Tickmill-Demo",
            "account_type": "demo"
        }
        
        # Health check endpoints
        self.health_endpoints = {
            "backend": f"http://localhost:{self.backend_port}/health",
            "backend_alt": f"http://localhost:{self.backend_port}/",
            "frontend": f"http://localhost:{self.frontend_port}",
            "mt5_connection": f"http://localhost:{self.backend_port}/api/v1/mt5/connection_status"
        }
        
    def log_header(self, message):
        """Log with fancy header"""
        print("\n" + "="*60)
        print(f"🚀 {message}")
        print("="*60)
        logger.info(message)
    
    def log_success(self, message):
        """Log success message"""
        print(f"✅ {message}")
        logger.info(f"SUCCESS: {message}")
    
    def log_error(self, message):
        """Log error message"""
        print(f"❌ {message}")
        logger.error(f"ERROR: {message}")
    
    def log_info(self, message):
        """Log info message"""
        print(f"ℹ️  {message}")
        logger.info(message)
    
    def cleanup_existing_processes(self):
        """Kill existing Python processes to ensure clean start"""
        self.log_header("CLEANING UP EXISTING PROCESSES")
        
        try:
            # Windows process cleanup
            if sys.platform == "win32":
                # Force kill any python processes that might be hanging
                subprocess.run('taskkill /f /im python.exe', shell=True, capture_output=True)
                subprocess.run('taskkill /f /im node.exe', shell=True, capture_output=True)
                
                time.sleep(2)  # Wait for cleanup
                self.log_success("Existing processes cleaned up")
            
        except Exception as e:
            self.log_info(f"Cleanup completed (some processes may not have existed): {e}")
    
    def start_backend(self):
        """Start the backend server"""
        self.log_header("STARTING BACKEND SERVER")
        
        try:
            backend_script = self.project_root / "backend" / "simple_mt5_backend.py"
            
            if not backend_script.exists():
                self.log_error(f"Backend script not found: {backend_script}")
                return False
            
            # Start backend process
            self.backend_process = subprocess.Popen(
                [sys.executable, str(backend_script)],
                cwd=str(self.project_root),
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                creationflags=subprocess.CREATE_NEW_PROCESS_GROUP if sys.platform == "win32" else 0
            )
            
            self.log_success(f"Backend process started (PID: {self.backend_process.pid})")
            return True
            
        except Exception as e:
            self.log_error(f"Failed to start backend: {e}")
            return False
    
    def start_frontend(self):
        """Start the frontend development server"""
        self.log_header("STARTING FRONTEND SERVER")
        
        try:
            frontend_dir = self.project_root / "frontend"
            
            if not frontend_dir.exists():
                self.log_error(f"Frontend directory not found: {frontend_dir}")
                return False
            
            # Check if package.json exists
            package_json = frontend_dir / "package.json"
            if not package_json.exists():
                self.log_error("package.json not found in frontend directory")
                return False
            
            # Start frontend development server
            self.frontend_process = subprocess.Popen(
                ["npm", "run", "dev"],
                cwd=str(frontend_dir),
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                shell=True,
                creationflags=subprocess.CREATE_NEW_PROCESS_GROUP if sys.platform == "win32" else 0
            )
            
            self.log_success(f"Frontend process started (PID: {self.frontend_process.pid})")
            return True
            
        except Exception as e:
            self.log_error(f"Failed to start frontend: {e}")
            return False
    
    def wait_for_service(self, url, service_name, timeout=30):
        """Wait for a service to become available"""
        self.log_info(f"Waiting for {service_name} to be ready...")
        
        start_time = time.time()
        while time.time() - start_time < timeout:
            try:
                response = requests.get(url, timeout=5)
                if response.status_code in [200, 404]:  # 404 is OK for root endpoints
                    self.log_success(f"{service_name} is ready!")
                    return True
            except requests.exceptions.RequestException:
                pass
            
            time.sleep(2)
            print(".", end="", flush=True)
        
        print()  # New line after dots
        self.log_error(f"{service_name} failed to start within {timeout} seconds")
        return False
    
    def perform_health_checks(self):
        """Perform comprehensive health checks"""
        self.log_header("PERFORMING HEALTH CHECKS")
        
        health_status = {}
        
        # Backend health check
        try:
            response = requests.get(self.health_endpoints["backend"], timeout=10)
            health_status["backend"] = response.status_code == 200
            if health_status["backend"]:
                self.log_success("Backend health check passed")
            else:
                # Try alternative endpoint
                response = requests.get(self.health_endpoints["backend_alt"], timeout=10)
                health_status["backend"] = response.status_code in [200, 404]
                if health_status["backend"]:
                    self.log_success("Backend is responding (alternative endpoint)")
                else:
                    self.log_error("Backend health check failed")
        except Exception as e:
            health_status["backend"] = False
            self.log_error(f"Backend health check failed: {e}")
        
        # Frontend health check
        try:
            response = requests.get(self.health_endpoints["frontend"], timeout=10)
            health_status["frontend"] = response.status_code == 200
            if health_status["frontend"]:
                self.log_success("Frontend health check passed")
            else:
                self.log_error("Frontend health check failed")
        except Exception as e:
            health_status["frontend"] = False
            self.log_error(f"Frontend health check failed: {e}")
        
        # MT5 connection check
        try:
            response = requests.get(self.health_endpoints["mt5_connection"], timeout=10)
            if response.status_code == 200:
                mt5_data = response.json()
                health_status["mt5"] = mt5_data.get("connected", False)
                if health_status["mt5"]:
                    self.log_success("MT5 connection check passed")
                    self.log_info(f"Connected to: {mt5_data.get('server', 'Unknown')}")
                else:
                    self.log_error("MT5 not connected")
            else:
                health_status["mt5"] = False
                self.log_error("MT5 connection endpoint not available")
        except Exception as e:
            health_status["mt5"] = False
            self.log_error(f"MT5 connection check failed: {e}")
        
        return health_status
    
    def setup_default_login(self):
        """Setup default login with MT5 demo account"""
        self.log_header("SETTING UP DEFAULT LOGIN")
        
        try:
            # Store default credentials in memory/session
            login_data = {
                "login_type": "mt5_demo",
                "credentials": self.default_credentials,
                "auto_login": True,
                "timestamp": datetime.now().isoformat()
            }
            
            # Save credentials to a temp file for frontend access
            credentials_file = self.project_root / "temp_login_session.json"
            with open(credentials_file, 'w') as f:
                json.dump(login_data, f, indent=2)
            
            self.log_success("Default login credentials prepared")
            self.log_info(f"MT5 Demo Account: {self.default_credentials['mt5_login']}")
            self.log_info(f"Server: {self.default_credentials['mt5_server']}")
            
            return True
            
        except Exception as e:
            self.log_error(f"Failed to setup default login: {e}")
            return False
    
    def display_system_status(self, health_status):
        """Display comprehensive system status"""
        self.log_header("SYSTEM STATUS SUMMARY")
        
        print("\n📊 SERVICE STATUS:")
        print(f"   Backend (Port {self.backend_port}): {'🟢 RUNNING' if health_status.get('backend') else '🔴 FAILED'}")
        print(f"   Frontend (Port {self.frontend_port}): {'🟢 RUNNING' if health_status.get('frontend') else '🔴 FAILED'}")
        print(f"   MT5 Connection: {'🟢 CONNECTED' if health_status.get('mt5') else '🟡 DISCONNECTED'}")
        
        print("\n🌐 ACCESS URLS:")
        print(f"   Frontend Dashboard: http://localhost:{self.frontend_port}")
        print(f"   Backend API: http://localhost:{self.backend_port}")
        
        print("\n🎯 AVAILABLE MODULES:")
        modules = [
            "Dashboard (Main)", "God Mode", "Shadow Mode", 
            "Strategy Whisperer", "Adaptive Trade Manager", 
            "Market Narrator", "Trading Panel"
        ]
        for module in modules:
            print(f"   ✅ {module}")
        
        print("\n🔐 DEFAULT LOGIN:")
        print(f"   MT5 Demo Account: {self.default_credentials['mt5_login']}")
        print(f"   Server: {self.default_credentials['mt5_server']}")
        print(f"   Status: {'✅ READY' if health_status.get('mt5') else '⚠️ CONNECTING'}")
        
        # Overall status
        all_critical_services = health_status.get('backend', False) and health_status.get('frontend', False)
        
        if all_critical_services:
            print("\n🎉 SYSTEM FULLY OPERATIONAL!")
            print("   You can now access the AI Algo Trade platform.")
        else:
            print("\n⚠️ SYSTEM PARTIALLY OPERATIONAL")
            print("   Some services may need manual intervention.")
        
        return all_critical_services
    
    def cleanup_on_exit(self):
        """Cleanup processes on exit"""
        self.log_info("Cleaning up processes...")
        
        if self.backend_process:
            self.backend_process.terminate()
            self.backend_process.wait()
        
        if self.frontend_process:
            self.frontend_process.terminate()
            self.frontend_process.wait()
    
    def start_complete_system(self):
        """Start the complete AI Algo Trade system"""
        try:
            start_time = time.time()
            
            print("\n" + "🚀" * 20)
            print("AI ALGO TRADE - COMPLETE SYSTEM STARTUP")
            print("🚀" * 20)
            
            # Step 1: Cleanup
            self.cleanup_existing_processes()
            
            # Step 2: Start Backend
            if not self.start_backend():
                self.log_error("Backend startup failed")
                return False
            
            # Step 3: Wait for Backend
            if not self.wait_for_service(
                self.health_endpoints["backend_alt"], 
                "Backend", 
                timeout=30
            ):
                self.log_error("Backend failed to become ready")
                return False
            
            # Step 4: Start Frontend
            if not self.start_frontend():
                self.log_error("Frontend startup failed")
                return False
            
            # Step 5: Wait for Frontend
            if not self.wait_for_service(
                self.health_endpoints["frontend"], 
                "Frontend", 
                timeout=45
            ):
                self.log_error("Frontend failed to become ready")
                return False
            
            # Step 6: Health Checks
            time.sleep(5)  # Allow services to fully initialize
            health_status = self.perform_health_checks()
            
            # Step 7: Setup Default Login
            self.setup_default_login()
            
            # Step 8: Display Status
            system_ready = self.display_system_status(health_status)
            
            # Step 9: Show startup time
            total_time = time.time() - start_time
            print(f"\n⏱️ Total startup time: {total_time:.1f} seconds")
            
            if system_ready:
                print("\n🎯 READY FOR TRADING!")
                print("   Press Ctrl+C to stop all services")
                
                # Keep running until interrupted
                try:
                    while True:
                        time.sleep(1)
                except KeyboardInterrupt:
                    print("\n\n🛑 Shutting down system...")
                    self.cleanup_on_exit()
                    print("✅ System shutdown complete")
                    
            return system_ready
            
        except Exception as e:
            self.log_error(f"System startup failed: {e}")
            self.cleanup_on_exit()
            return False

def main():
    """Main entry point"""
    starter = AIAlgoTradeSystemStarter()
    success = starter.start_complete_system()
    
    if not success:
        print("\n❌ SYSTEM STARTUP FAILED")
        print("Please check the logs above for details.")
        sys.exit(1)

if __name__ == "__main__":
    main() 