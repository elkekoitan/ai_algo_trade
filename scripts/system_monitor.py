#!/usr/bin/env python3
"""
AI Algo Trade - System Monitor
Comprehensive monitoring script for continuous operation
"""

import time
import requests
import subprocess
import psutil
import json
from datetime import datetime
import logging
from pathlib import Path

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/system_monitor.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class SystemMonitor:
    def __init__(self):
        self.backend_url = "http://localhost:8002"
        self.frontend_url = "http://localhost:3000"
        self.monitoring_interval = 30  # seconds
        self.performance_data = []
        
    def check_backend_health(self):
        """Check backend API health"""
        try:
            response = requests.get(f"{self.backend_url}/health", timeout=10)
            if response.status_code == 200:
                data = response.json()
                logger.info(f"✅ Backend healthy: {data}")
                return True, data
        except Exception as e:
            logger.error(f"❌ Backend health check failed: {e}")
            return False, str(e)
        
        return False, "Backend not responding"
    
    def check_frontend_health(self):
        """Check frontend health"""
        try:
            response = requests.get(self.frontend_url, timeout=10)
            if response.status_code == 200:
                logger.info("✅ Frontend healthy")
                return True, "Frontend responding"
        except Exception as e:
            logger.error(f"❌ Frontend health check failed: {e}")
            return False, str(e)
        
        return False, "Frontend not responding"
    
    def check_mt5_connection(self):
        """Check MT5 connection status"""
        try:
            response = requests.get(f"{self.backend_url}/api/v1/mt5/status", timeout=10)
            if response.status_code == 200:
                data = response.json()
                logger.info(f"✅ MT5 Status: {data}")
                return True, data
        except Exception as e:
            logger.error(f"❌ MT5 status check failed: {e}")
            return False, str(e)
        
        return False, "MT5 status unavailable"
    
    def check_copy_trading_status(self):
        """Check copy trading system status"""
        try:
            response = requests.get(f"{self.backend_url}/api/v1/copy-trading/status", timeout=10)
            if response.status_code == 200:
                data = response.json()
                logger.info(f"✅ Copy Trading: {data}")
                return True, data
        except Exception as e:
            logger.error(f"❌ Copy trading check failed: {e}")
            return False, str(e)
        
        return False, "Copy trading status unavailable"
    
    def get_system_performance(self):
        """Get system performance metrics"""
        try:
            cpu_percent = psutil.cpu_percent(interval=1)
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage('/')
            
            performance = {
                "timestamp": datetime.now().isoformat(),
                "cpu_percent": cpu_percent,
                "memory_percent": memory.percent,
                "memory_available_gb": round(memory.available / (1024**3), 2),
                "disk_percent": disk.percent,
                "disk_free_gb": round(disk.free / (1024**3), 2)
            }
            
            logger.info(f"📊 Performance: CPU {cpu_percent}%, RAM {memory.percent}%, Disk {disk.percent}%")
            return performance
            
        except Exception as e:
            logger.error(f"❌ Performance check failed: {e}")
            return None
    
    def check_running_processes(self):
        """Check if key processes are running"""
        python_processes = []
        node_processes = []
        
        for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
            try:
                if proc.info['name'] == 'python.exe':
                    cmdline = ' '.join(proc.info['cmdline'])
                    if 'simple_mt5_backend' in cmdline or 'launch_copy_trading' in cmdline:
                        python_processes.append({
                            "pid": proc.info['pid'],
                            "command": cmdline
                        })
                elif proc.info['name'] == 'node.exe':
                    cmdline = ' '.join(proc.info['cmdline'])
                    if 'next' in cmdline:
                        node_processes.append({
                            "pid": proc.info['pid'],
                            "command": cmdline
                        })
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue
        
        logger.info(f"🔍 Running processes: {len(python_processes)} Python, {len(node_processes)} Node")
        return python_processes, node_processes
    
    def check_all_modules(self):
        """Check all trading modules status"""
        modules_status = {}
        
        modules = [
            "shadow-mode",
            "god-mode", 
            "market-narrator",
            "strategy-whisperer",
            "adaptive-trade-manager"
        ]
        
        for module in modules:
            try:
                response = requests.get(f"{self.backend_url}/api/v1/{module}/status", timeout=5)
                if response.status_code == 200:
                    modules_status[module] = {"status": "active", "data": response.json()}
                    logger.info(f"✅ {module}: Active")
                else:
                    modules_status[module] = {"status": "error", "code": response.status_code}
                    logger.warning(f"⚠️ {module}: Error {response.status_code}")
            except Exception as e:
                modules_status[module] = {"status": "unavailable", "error": str(e)}
                logger.error(f"❌ {module}: {e}")
        
        return modules_status
    
    def generate_status_report(self):
        """Generate comprehensive status report"""
        report = {
            "timestamp": datetime.now().isoformat(),
            "system_status": "checking"
        }
        
        # Check all components
        backend_healthy, backend_data = self.check_backend_health()
        frontend_healthy, frontend_data = self.check_frontend_health()
        mt5_healthy, mt5_data = self.check_mt5_connection()
        copy_healthy, copy_data = self.check_copy_trading_status()
        
        # Get performance metrics
        performance = self.get_system_performance()
        python_procs, node_procs = self.check_running_processes()
        modules_status = self.check_all_modules()
        
        # Compile report
        report.update({
            "backend": {"healthy": backend_healthy, "data": backend_data},
            "frontend": {"healthy": frontend_healthy, "data": frontend_data},
            "mt5": {"healthy": mt5_healthy, "data": mt5_data},
            "copy_trading": {"healthy": copy_healthy, "data": copy_data},
            "performance": performance,
            "processes": {
                "python": python_procs,
                "node": node_procs
            },
            "modules": modules_status
        })
        
        # Determine overall status
        core_systems = [backend_healthy, frontend_healthy]
        if all(core_systems):
            report["system_status"] = "healthy"
            logger.info("🟢 System Status: HEALTHY")
        elif any(core_systems):
            report["system_status"] = "degraded"
            logger.warning("🟡 System Status: DEGRADED")
        else:
            report["system_status"] = "critical"
            logger.error("🔴 System Status: CRITICAL")
        
        return report
    
    def save_report(self, report):
        """Save report to file"""
        try:
            # Save to logs directory
            logs_dir = Path("logs")
            logs_dir.mkdir(exist_ok=True)
            
            # Save latest report
            with open(logs_dir / "latest_status.json", 'w') as f:
                json.dump(report, f, indent=2)
            
            # Append to history
            with open(logs_dir / "status_history.jsonl", 'a') as f:
                f.write(json.dumps(report) + '\n')
                
        except Exception as e:
            logger.error(f"Failed to save report: {e}")
    
    def display_dashboard(self, report):
        """Display real-time dashboard"""
        print("\n" + "="*80)
        print("🚀 AI ALGO TRADE - SYSTEM DASHBOARD")
        print("="*80)
        
        # System Overview
        status_icon = {"healthy": "🟢", "degraded": "🟡", "critical": "🔴"}
        print(f"System Status: {status_icon.get(report['system_status'], '⚪')} {report['system_status'].upper()}")
        print(f"Timestamp: {report['timestamp']}")
        
        # Core Services
        print("\n📡 CORE SERVICES:")
        services = ["backend", "frontend", "mt5", "copy_trading"]
        for service in services:
            if service in report:
                status = "✅" if report[service]["healthy"] else "❌"
                print(f"  {status} {service.replace('_', ' ').title()}")
        
        # Performance Metrics
        if report.get("performance"):
            perf = report["performance"]
            print(f"\n📊 PERFORMANCE:")
            print(f"  CPU: {perf['cpu_percent']}%")
            print(f"  RAM: {perf['memory_percent']}% (Available: {perf['memory_available_gb']}GB)")
            print(f"  Disk: {perf['disk_percent']}% (Free: {perf['disk_free_gb']}GB)")
        
        # Trading Modules
        if report.get("modules"):
            print(f"\n🤖 TRADING MODULES:")
            for module, status in report["modules"].items():
                icon = "✅" if status["status"] == "active" else "❌"
                print(f"  {icon} {module.replace('-', ' ').title()}")
        
        # Running Processes
        if report.get("processes"):
            python_count = len(report["processes"]["python"])
            node_count = len(report["processes"]["node"])
            print(f"\n🔄 RUNNING PROCESSES:")
            print(f"  Python: {python_count} processes")
            print(f"  Node.js: {node_count} processes")
        
        print("="*80)
    
    def continuous_monitoring(self):
        """Run continuous monitoring loop"""
        logger.info("🚀 Starting AI Algo Trade System Monitor")
        logger.info(f"Monitoring interval: {self.monitoring_interval} seconds")
        
        try:
            while True:
                # Generate status report
                report = self.generate_status_report()
                
                # Save report
                self.save_report(report)
                
                # Display dashboard
                self.display_dashboard(report)
                
                # Check for critical issues
                if report["system_status"] == "critical":
                    logger.error("🚨 CRITICAL SYSTEM ISSUE DETECTED!")
                    # Here you could add alerting logic
                
                # Wait for next check
                time.sleep(self.monitoring_interval)
                
        except KeyboardInterrupt:
            logger.info("👋 System monitoring stopped by user")
        except Exception as e:
            logger.error(f"❌ Monitor crashed: {e}")

def main():
    """Main function"""
    monitor = SystemMonitor()
    
    # Run one status check first
    print("🔍 Running initial system check...")
    report = monitor.generate_status_report()
    monitor.display_dashboard(report)
    monitor.save_report(report)
    
    # Ask if user wants continuous monitoring
    try:
        choice = input("\n🔄 Start continuous monitoring? (y/n): ").lower().strip()
        if choice in ['y', 'yes']:
            monitor.continuous_monitoring()
        else:
            print("✅ Single check completed. Reports saved to logs/")
    except KeyboardInterrupt:
        print("\n👋 Monitoring stopped")

if __name__ == "__main__":
    main() 