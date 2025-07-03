#!/usr/bin/env python3
"""
AI Algo Trade - Performance System Launcher
Sistem performansını test etmek için comprehensive launcher
"""

import subprocess
import time
import sys
import json
import requests
from datetime import datetime
from pathlib import Path
import logging
import threading
import os

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/performance_launch.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class PerformanceSystemLauncher:
    def __init__(self):
        self.processes = {}
        self.backend_url = "http://localhost:8002"
        self.frontend_url = "http://localhost:3000"
        self.startup_sequence = []
        
    def check_prerequisites(self):
        """Check system prerequisites"""
        logger.info("🔍 Checking system prerequisites...")
        
        checks = {
            "Python": {"cmd": "python --version", "required": True},
            "Node.js": {"cmd": "node --version", "required": True},
            "npm": {"cmd": "npm --version", "required": True},
            "MT5 Files": {"path": "backend/modules/mt5_integration", "required": True},
            "Frontend": {"path": "frontend/package.json", "required": True}
        }
        
        for name, check in checks.items():
            try:
                if "cmd" in check:
                    result = subprocess.run(
                        check["cmd"].split(), 
                        capture_output=True, 
                        text=True, 
                        timeout=10
                    )
                    if result.returncode == 0:
                        version = result.stdout.strip()
                        logger.info(f"  ✅ {name}: {version}")
                    else:
                        logger.error(f"  ❌ {name}: Not found")
                        if check["required"]:
                            return False
                elif "path" in check:
                    if Path(check["path"]).exists():
                        logger.info(f"  ✅ {name}: Found")
                    else:
                        logger.error(f"  ❌ {name}: Missing")
                        if check["required"]:
                            return False
            except Exception as e:
                logger.error(f"  ❌ {name}: Error - {e}")
                if check["required"]:
                    return False
        
        return True
    
    def kill_existing_processes(self):
        """Kill any existing backend/frontend processes"""
        logger.info("🧹 Cleaning up existing processes...")
        
        try:
            # Kill Python processes on port 8002
            subprocess.run(
                ["taskkill", "/f", "/fi", "IMAGENAME eq python.exe"], 
                capture_output=True, 
                timeout=10
            )
            logger.info("  ✅ Python processes cleaned")
            
            # Kill Node processes on port 3000
            subprocess.run(
                ["taskkill", "/f", "/fi", "IMAGENAME eq node.exe"], 
                capture_output=True, 
                timeout=10
            )
            logger.info("  ✅ Node processes cleaned")
            
            time.sleep(2)  # Wait for cleanup
            
        except Exception as e:
            logger.warning(f"  ⚠️ Cleanup warning: {e}")
    
    def check_port_availability(self, port):
        """Check if port is available"""
        try:
            result = subprocess.run(
                f"netstat -an | findstr :{port}",
                shell=True,
                capture_output=True,
                text=True,
                timeout=5
            )
            return str(port) not in result.stdout
        except:
            return True
    
    def start_backend(self):
        """Start backend service"""
        logger.info("🚀 Starting backend service...")
        
        if not self.check_port_availability(8002):
            logger.warning("  ⚠️ Port 8002 already in use, attempting cleanup...")
            self.kill_existing_processes()
            time.sleep(2)
        
        try:
            # Start backend
            backend_process = subprocess.Popen(
                [sys.executable, "backend/simple_mt5_backend.py"],
                cwd=Path.cwd(),
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            
            self.processes["backend"] = backend_process
            self.startup_sequence.append({"service": "backend", "time": datetime.now()})
            
            logger.info(f"  ⏳ Backend starting (PID: {backend_process.pid})")
            
            # Wait for backend to start
            for i in range(30):  # 30 second timeout
                try:
                    response = requests.get(f"{self.backend_url}/health", timeout=2)
                    if response.status_code == 200:
                        logger.info("  ✅ Backend is healthy and responding")
                        return True
                except:
                    pass
                time.sleep(1)
                logger.info(f"  ⏳ Waiting for backend... ({i+1}/30)")
            
            logger.error("  ❌ Backend failed to start within timeout")
            return False
            
        except Exception as e:
            logger.error(f"  ❌ Backend startup failed: {e}")
            return False
    
    def start_frontend(self):
        """Start frontend service"""
        logger.info("🎨 Starting frontend service...")
        
        if not self.check_port_availability(3000):
            logger.warning("  ⚠️ Port 3000 already in use")
        
        try:
            # Install dependencies if needed
            if not Path("frontend/node_modules").exists():
                logger.info("  📦 Installing npm dependencies...")
                install_process = subprocess.run(
                    ["npm", "install"],
                    cwd=Path("frontend"),
                    timeout=120
                )
                if install_process.returncode != 0:
                    logger.error("  ❌ npm install failed")
                    return False
            
            # Start frontend
            frontend_process = subprocess.Popen(
                ["npm", "run", "dev"],
                cwd=Path("frontend"),
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            
            self.processes["frontend"] = frontend_process
            self.startup_sequence.append({"service": "frontend", "time": datetime.now()})
            
            logger.info(f"  ⏳ Frontend starting (PID: {frontend_process.pid})")
            
            # Wait for frontend to start
            for i in range(60):  # 60 second timeout for frontend
                try:
                    response = requests.get(self.frontend_url, timeout=3)
                    if response.status_code == 200:
                        logger.info("  ✅ Frontend is healthy and responding")
                        return True
                except:
                    pass
                time.sleep(1)
                if i % 10 == 0:
                    logger.info(f"  ⏳ Waiting for frontend... ({i+1}/60)")
            
            logger.error("  ❌ Frontend failed to start within timeout")
            return False
            
        except Exception as e:
            logger.error(f"  ❌ Frontend startup failed: {e}")
            return False
    
    def start_copy_trading(self):
        """Start copy trading system"""
        logger.info("📈 Starting copy trading system...")
        
        try:
            copy_process = subprocess.Popen(
                [sys.executable, "launch_copy_trading.py"],
                cwd=Path.cwd(),
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            
            self.processes["copy_trading"] = copy_process
            self.startup_sequence.append({"service": "copy_trading", "time": datetime.now()})
            
            logger.info(f"  ✅ Copy trading started (PID: {copy_process.pid})")
            
            # Check copy trading status
            time.sleep(5)
            try:
                response = requests.get(f"{self.backend_url}/api/v1/copy-trading/status", timeout=5)
                if response.status_code == 200:
                    logger.info("  ✅ Copy trading is operational")
                    return True
            except:
                pass
            
            logger.info("  ⏳ Copy trading system initializing...")
            return True
            
        except Exception as e:
            logger.error(f"  ❌ Copy trading startup failed: {e}")
            return False
    
    def run_health_checks(self):
        """Run comprehensive health checks"""
        logger.info("🏥 Running comprehensive health checks...")
        
        health_results = {}
        
        # Backend health
        try:
            response = requests.get(f"{self.backend_url}/health", timeout=10)
            health_results["backend"] = {
                "status": "healthy" if response.status_code == 200 else "unhealthy",
                "response_time": response.elapsed.total_seconds(),
                "data": response.json() if response.status_code == 200 else None
            }
            logger.info(f"  ✅ Backend health: {health_results['backend']['status']}")
        except Exception as e:
            health_results["backend"] = {"status": "error", "error": str(e)}
            logger.error(f"  ❌ Backend health check failed: {e}")
        
        # Frontend health
        try:
            response = requests.get(self.frontend_url, timeout=10)
            health_results["frontend"] = {
                "status": "healthy" if response.status_code == 200 else "unhealthy",
                "response_time": response.elapsed.total_seconds()
            }
            logger.info(f"  ✅ Frontend health: {health_results['frontend']['status']}")
        except Exception as e:
            health_results["frontend"] = {"status": "error", "error": str(e)}
            logger.error(f"  ❌ Frontend health check failed: {e}")
        
        # MT5 connection
        try:
            response = requests.get(f"{self.backend_url}/api/v1/market/status", timeout=10)
            if response.status_code == 200:
                data = response.json()
                health_results["mt5"] = {
                    "status": "connected" if data.get("mt5_connected") else "disconnected",
                    "data": data
                }
                logger.info(f"  ✅ MT5 connection: {health_results['mt5']['status']}")
            else:
                health_results["mt5"] = {"status": "error", "code": response.status_code}
        except Exception as e:
            health_results["mt5"] = {"status": "error", "error": str(e)}
            logger.error(f"  ❌ MT5 health check failed: {e}")
        
        # Module status checks
        modules = ["shadow-mode", "god-mode", "market-narrator", "strategy-whisperer", "adaptive-tm"]
        health_results["modules"] = {}
        
        for module in modules:
            try:
                response = requests.get(f"{self.backend_url}/api/v1/{module}/status", timeout=5)
                health_results["modules"][module] = {
                    "status": "active" if response.status_code == 200 else "inactive",
                    "response_time": response.elapsed.total_seconds() if hasattr(response, 'elapsed') else None
                }
                status = health_results["modules"][module]["status"]
                logger.info(f"  ✅ {module}: {status}")
            except Exception as e:
                health_results["modules"][module] = {"status": "error", "error": str(e)}
                logger.warning(f"  ⚠️ {module}: error")
        
        return health_results
    
    def run_performance_tests(self):
        """Run performance tests"""
        logger.info("⚡ Running performance tests...")
        
        performance_results = {}
        
        # API Response Time Tests
        api_endpoints = [
            "/health",
            "/api/v1/trading/account",
            "/api/v1/trading/positions",
            "/api/v1/market/status",
            "/api/v1/god-mode/status",
            "/api/v1/performance/performance_summary"
        ]
        
        for endpoint in api_endpoints:
            try:
                start_time = time.time()
                response = requests.get(f"{self.backend_url}{endpoint}", timeout=10)
                end_time = time.time()
                
                response_time = (end_time - start_time) * 1000  # milliseconds
                
                performance_results[endpoint] = {
                    "response_time_ms": round(response_time, 2),
                    "status_code": response.status_code,
                    "success": response.status_code == 200
                }
                
                status = "✅" if response.status_code == 200 else "❌"
                logger.info(f"  {status} {endpoint}: {response_time:.1f}ms")
                
            except Exception as e:
                performance_results[endpoint] = {
                    "response_time_ms": None,
                    "status_code": None,
                    "success": False,
                    "error": str(e)
                }
                logger.error(f"  ❌ {endpoint}: Error - {e}")
        
        # Calculate averages
        successful_tests = [r for r in performance_results.values() if r["success"]]
        if successful_tests:
            avg_response_time = sum(r["response_time_ms"] for r in successful_tests) / len(successful_tests)
            performance_results["summary"] = {
                "average_response_time_ms": round(avg_response_time, 2),
                "successful_requests": len(successful_tests),
                "total_requests": len(api_endpoints),
                "success_rate": round(len(successful_tests) / len(api_endpoints) * 100, 1)
            }
            logger.info(f"  📊 Average response time: {avg_response_time:.1f}ms")
            logger.info(f"  📊 Success rate: {performance_results['summary']['success_rate']}%")
        
        return performance_results
    
    def generate_system_report(self, health_results, performance_results):
        """Generate comprehensive system report"""
        report = {
            "timestamp": datetime.now().isoformat(),
            "startup_sequence": self.startup_sequence,
            "health_checks": health_results,
            "performance_tests": performance_results,
            "running_processes": {
                "backend": self.processes.get("backend", {}).pid if self.processes.get("backend") else None,
                "frontend": self.processes.get("frontend", {}).pid if self.processes.get("frontend") else None,
                "copy_trading": self.processes.get("copy_trading", {}).pid if self.processes.get("copy_trading") else None
            },
            "system_urls": {
                "backend": self.backend_url,
                "frontend": self.frontend_url,
                "backend_docs": f"{self.backend_url}/docs",
                "backend_health": f"{self.backend_url}/health"
            }
        }
        
        # Save report
        logs_dir = Path("logs")
        logs_dir.mkdir(exist_ok=True)
        
        with open(logs_dir / "system_performance_report.json", 'w') as f:
            json.dump(report, f, indent=2)
        
        logger.info(f"📄 System report saved to logs/system_performance_report.json")
        
        return report
    
    def display_system_dashboard(self, health_results, performance_results):
        """Display real-time system dashboard"""
        print("\n" + "="*80)
        print("🚀 AI ALGO TRADE - SYSTEM PERFORMANCE DASHBOARD")
        print("="*80)
        
        # System Status Overview
        backend_healthy = health_results.get("backend", {}).get("status") == "healthy"
        frontend_healthy = health_results.get("frontend", {}).get("status") == "healthy"
        mt5_connected = health_results.get("mt5", {}).get("status") == "connected"
        
        overall_status = "🟢 FULLY OPERATIONAL" if all([backend_healthy, frontend_healthy, mt5_connected]) else \
                        "🟡 PARTIALLY OPERATIONAL" if any([backend_healthy, frontend_healthy]) else \
                        "🔴 CRITICAL ISSUES"
        
        print(f"System Status: {overall_status}")
        print(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        # Core Services
        print(f"\n📡 CORE SERVICES:")
        services = [
            ("Backend API", backend_healthy, f"{self.backend_url}"),
            ("Frontend UI", frontend_healthy, f"{self.frontend_url}"),
            ("MT5 Connection", mt5_connected, "Tickmill-Demo Server")
        ]
        
        for name, status, url in services:
            icon = "✅" if status else "❌"
            print(f"  {icon} {name}: {url}")
        
        # Performance Metrics
        if performance_results.get("summary"):
            summary = performance_results["summary"]
            print(f"\n⚡ PERFORMANCE METRICS:")
            print(f"  Average Response Time: {summary['average_response_time_ms']}ms")
            print(f"  API Success Rate: {summary['success_rate']}%")
            print(f"  Successful Requests: {summary['successful_requests']}/{summary['total_requests']}")
        
        # Module Status
        modules = health_results.get("modules", {})
        if modules:
            print(f"\n🤖 TRADING MODULES:")
            for module, status in modules.items():
                icon = "✅" if status.get("status") == "active" else "⚠️"
                print(f"  {icon} {module.replace('-', ' ').title()}")
        
        # Running Processes
        print(f"\n🔄 RUNNING PROCESSES:")
        for service, process in self.processes.items():
            if process and hasattr(process, 'pid'):
                print(f"  ✅ {service.replace('_', ' ').title()}: PID {process.pid}")
        
        # Quick Access URLs
        print(f"\n🔗 QUICK ACCESS:")
        print(f"  🎨 Dashboard: {self.frontend_url}")
        print(f"  📡 API Docs: {self.backend_url}/docs")
        print(f"  🏥 Health Check: {self.backend_url}/health")
        print(f"  📊 Performance: {self.backend_url}/api/v1/performance/performance_summary")
        
        print("="*80)
    
    def continuous_monitoring(self):
        """Start continuous monitoring mode"""
        logger.info("📊 Starting continuous monitoring mode...")
        
        try:
            while True:
                print(f"\n🔄 Running health checks... ({datetime.now().strftime('%H:%M:%S')})")
                
                health_results = self.run_health_checks()
                performance_results = self.run_performance_tests()
                self.display_system_dashboard(health_results, performance_results)
                
                time.sleep(60)  # Check every minute
                
        except KeyboardInterrupt:
            logger.info("👋 Continuous monitoring stopped by user")
    
    def launch_system(self):
        """Launch the complete system"""
        logger.info("🎯 AI Algo Trade - Performance System Launch")
        logger.info("=" * 60)
        
        try:
            # Check prerequisites
            if not self.check_prerequisites():
                logger.error("❌ Prerequisites check failed")
                return False
            
            # Clean up
            self.kill_existing_processes()
            
            # Start services in sequence
            if not self.start_backend():
                logger.error("❌ Backend startup failed")
                return False
            
            if not self.start_frontend():
                logger.error("❌ Frontend startup failed")
                return False
            
            # Start copy trading (optional)
            self.start_copy_trading()
            
            # Wait for stabilization
            logger.info("⏳ Waiting for system stabilization...")
            time.sleep(10)
            
            # Run health checks
            health_results = self.run_health_checks()
            
            # Run performance tests
            performance_results = self.run_performance_tests()
            
            # Generate report
            report = self.generate_system_report(health_results, performance_results)
            
            # Display dashboard
            self.display_system_dashboard(health_results, performance_results)
            
            logger.info("🎉 System launch completed!")
            
            # Ask for continuous monitoring
            try:
                choice = input("\n🔄 Start continuous monitoring? (y/n): ").lower().strip()
                if choice in ['y', 'yes']:
                    self.continuous_monitoring()
            except KeyboardInterrupt:
                logger.info("👋 System launch completed")
            
            return True
            
        except Exception as e:
            logger.error(f"❌ System launch failed: {e}")
            return False

def main():
    """Main function"""
    launcher = PerformanceSystemLauncher()
    success = launcher.launch_system()
    
    if success:
        logger.info("✅ AI Algo Trade system is now operational!")
    else:
        logger.error("❌ System launch failed!")
        sys.exit(1)

if __name__ == "__main__":
    main() 