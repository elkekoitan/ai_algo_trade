#!/usr/bin/env python3
"""
AI Algo Trade - System Monitor Script
Sürekli sistem performansını takip eder ve raporlar
"""

import asyncio
import aiohttp
import time
import json
from datetime import datetime
from typing import Dict, Any

class SystemMonitor:
    def __init__(self):
        self.backend_url = "http://localhost:8002"
        self.frontend_url = "http://localhost:3000"
        self.check_interval = 30  # seconds
        self.running = True
        
    async def check_backend_health(self) -> Dict[str, Any]:
        """Backend sağlık durumunu kontrol et"""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(f"{self.backend_url}/health", timeout=10) as response:
                    if response.status == 200:
                        data = await response.json()
                        return {"status": "healthy", "data": data}
                    else:
                        return {"status": "unhealthy", "error": f"HTTP {response.status}"}
        except Exception as e:
            return {"status": "error", "error": str(e)}
    
    async def check_performance_metrics(self) -> Dict[str, Any]:
        """Performans metriklerini al"""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(f"{self.backend_url}/performance", timeout=10) as response:
                    if response.status == 200:
                        return await response.json()
                    else:
                        return {"error": f"HTTP {response.status}"}
        except Exception as e:
            return {"error": str(e)}
    
    async def check_frontend_health(self) -> Dict[str, Any]:
        """Frontend sağlık durumunu kontrol et"""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(f"{self.frontend_url}", timeout=10) as response:
                    if response.status == 200:
                        return {"status": "healthy"}
                    else:
                        return {"status": "unhealthy", "error": f"HTTP {response.status}"}
        except Exception as e:
            return {"status": "error", "error": str(e)}
    
    def format_uptime(self, seconds: float) -> str:
        """Uptime'ı formatla"""
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        secs = int(seconds % 60)
        return f"{hours}h {minutes}m {secs}s"
    
    def print_status_report(self, backend_health: Dict, performance: Dict, frontend_health: Dict):
        """Durum raporunu yazdır"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f"\n{'='*80}")
        print(f"AI ALGO TRADE - SYSTEM STATUS REPORT")
        print(f"Time: {timestamp}")
        print(f"{'='*80}")
        
        # Backend Status
        print(f"\n🔧 BACKEND STATUS:")
        if backend_health["status"] == "healthy":
            data = backend_health["data"]
            print(f"  ✅ Status: {data.get('status', 'Unknown')}")
            print(f"  🔗 MT5 Connected: {'✅ Yes' if data.get('mt5_connected') else '❌ No'}")
            print(f"  ⏱️  Uptime: {data.get('uptime_seconds', 0):.0f}s")
            print(f"  🌍 Weekend Mode: {'✅ Yes' if data.get('weekend_mode') else '❌ No'}")
        else:
            print(f"  ❌ Error: {backend_health.get('error', 'Unknown error')}")
        
        # Performance Metrics
        print(f"\n📊 PERFORMANCE METRICS:")
        if "error" not in performance:
            system = performance.get("system", {})
            trading = performance.get("trading_engine", {})
            account = performance.get("account", {})
            market = performance.get("market", {})
            
            print(f"  🖥️  CPU Usage: {system.get('cpu_usage', 0):.1f}%")
            print(f"  💾 Memory: {system.get('memory_usage_mb', 0):.0f} MB")
            print(f"  ⏰ Uptime: {self.format_uptime(system.get('uptime_seconds', 0))}")
            print(f"  🧵 Threads: {system.get('threads', 0)}")
            
            print(f"\n  🚀 Trading Engine:")
            print(f"    • Running: {'✅' if trading.get('running') else '❌'}")
            print(f"    • MT5 Connected: {'✅' if trading.get('mt5_connected') else '❌'}")
            print(f"    • Weekend Mode: {'✅' if trading.get('weekend_mode') else '❌'}")
            
            if account:
                print(f"\n  💰 Account Info:")
                print(f"    • Balance: ${account.get('balance', 0):,.2f}")
                print(f"    • Equity: ${account.get('equity', 0):,.2f}")
                print(f"    • Profit: ${account.get('profit', 0):,.2f}")
                print(f"    • Margin Level: {account.get('margin_level', 0):.0f}%")
            
            if market:
                print(f"\n  📈 Market Info:")
                print(f"    • Active Symbols: {market.get('active_symbols', 0)}")
                print(f"    • Weekend Mode: {'✅' if market.get('weekend_mode') else '❌'}")
            
            # Module Status
            modules = trading.get('active_modules', {})
            if modules:
                print(f"\n  🎯 Active Modules:")
                for module, active in modules.items():
                    status_icon = "✅" if active else "❌"
                    module_name = module.replace('_', ' ').title()
                    print(f"    • {module_name}: {status_icon}")
        else:
            print(f"  ❌ Error: {performance.get('error', 'Unknown error')}")
        
        # Frontend Status
        print(f"\n🌐 FRONTEND STATUS:")
        if frontend_health["status"] == "healthy":
            print(f"  ✅ Status: Healthy")
            print(f"  🔗 URL: {self.frontend_url}")
        else:
            print(f"  ❌ Error: {frontend_health.get('error', 'Unknown error')}")
        
        print(f"\n{'='*80}")
    
    async def monitor_loop(self):
        """Ana monitoring döngüsü"""
        print(f"🚀 AI Algo Trade System Monitor Started")
        print(f"📊 Monitoring interval: {self.check_interval}s")
        print(f"🔧 Backend: {self.backend_url}")
        print(f"🌐 Frontend: {self.frontend_url}")
        
        while self.running:
            try:
                # Tüm kontrolleri paralel olarak yap
                backend_task = self.check_backend_health()
                performance_task = self.check_performance_metrics()
                frontend_task = self.check_frontend_health()
                
                backend_health, performance, frontend_health = await asyncio.gather(
                    backend_task, performance_task, frontend_task
                )
                
                # Raporu yazdır
                self.print_status_report(backend_health, performance, frontend_health)
                
                # Kritik durumları kontrol et
                await self.check_critical_alerts(backend_health, performance)
                
            except Exception as e:
                print(f"❌ Monitor error: {e}")
            
            # Sonraki kontrolü bekle
            await asyncio.sleep(self.check_interval)
    
    async def check_critical_alerts(self, backend_health: Dict, performance: Dict):
        """Kritik durum uyarıları"""
        alerts = []
        
        # Backend bağlantısı kopmuş
        if backend_health["status"] != "healthy":
            alerts.append("🚨 CRITICAL: Backend is not responding!")
        
        # MT5 bağlantısı kopmuş
        elif not backend_health.get("data", {}).get("mt5_connected", False):
            alerts.append("⚠️  WARNING: MT5 connection lost!")
        
        # Yüksek CPU kullanımı
        if "error" not in performance:
            cpu_usage = performance.get("system", {}).get("cpu_usage", 0)
            memory_mb = performance.get("system", {}).get("memory_usage_mb", 0)
            
            if cpu_usage > 90:
                alerts.append(f"🚨 CRITICAL: High CPU usage ({cpu_usage:.1f}%)!")
            elif cpu_usage > 70:
                alerts.append(f"⚠️  WARNING: Elevated CPU usage ({cpu_usage:.1f}%)")
            
            if memory_mb > 2000:
                alerts.append(f"🚨 CRITICAL: High memory usage ({memory_mb:.0f} MB)!")
            elif memory_mb > 1000:
                alerts.append(f"⚠️  WARNING: Elevated memory usage ({memory_mb:.0f} MB)")
        
        # Uyarıları yazdır
        if alerts:
            print(f"\n🔔 ALERTS:")
            for alert in alerts:
                print(f"  {alert}")

async def main():
    monitor = SystemMonitor()
    try:
        await monitor.monitor_loop()
    except KeyboardInterrupt:
        print(f"\n\n🛑 System Monitor stopped by user")
        monitor.running = False

if __name__ == "__main__":
    asyncio.run(main()) 