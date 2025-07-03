#!/usr/bin/env python3
"""
Sanal Süpürge V1 Strategy Deployment ve Copy Trading Başlatma Scripti

Bu script:
1. Backend'i başlatır
2. Frontend'i başlatır  
3. Sanal Süpürge V1 stratejisini deploy eder
4. Copy trading sistemini aktif eder
5. Sistem sağlık kontrollerini yapar
"""

import os
import sys
import asyncio
import subprocess
import time
import requests
import json
from pathlib import Path

# Proje kök dizinini belirle
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.append(str(PROJECT_ROOT))

def print_step(step, message):
    """Adımları güzel formatta yazdır"""
    print(f"\n🔄 {step}: {message}")
    print("=" * 60)

def print_success(message):
    """Başarı mesajı"""
    print(f"✅ {message}")

def print_error(message):
    """Hata mesajı"""
    print(f"❌ {message}")

def print_info(message):
    """Bilgi mesajı"""
    print(f"ℹ️  {message}")

async def check_backend_health():
    """Backend sağlık kontrolü"""
    try:
        response = requests.get("http://localhost:8002/health", timeout=10)
        if response.status_code == 200:
            return True
        return False
    except:
        return False

async def check_frontend_health():
    """Frontend sağlık kontrolü"""
    try:
        response = requests.get("http://localhost:3000", timeout=10)
        if response.status_code == 200:
            return True
        return False
    except:
        return False

def start_backend():
    """Backend'i başlat"""
    print_step("1", "Backend Başlatılıyor")
    
    backend_dir = PROJECT_ROOT / "backend"
    
    # Python path ayarla
    env = os.environ.copy()
    env["PYTHONPATH"] = str(PROJECT_ROOT)
    
    # Backend'i başlat
    process = subprocess.Popen(
        [sys.executable, "simple_mt5_backend.py"],
        cwd=backend_dir,
        env=env,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )
    
    print_info(f"Backend process başlatıldı (PID: {process.pid})")
    
    # Backend'in hazır olmasını bekle
    for i in range(30):  # 30 saniye bekle
        time.sleep(1)
        if asyncio.run(check_backend_health()):
            print_success("Backend başarıyla başlatıldı!")
            return process
        print(f"Backend bekleniyor... ({i+1}/30)")
    
    print_error("Backend başlatılamadı!")
    return None

def start_frontend():
    """Frontend'i başlat"""
    print_step("2", "Frontend Başlatılıyor")
    
    frontend_dir = PROJECT_ROOT / "frontend"
    
    # Frontend'i başlat
    process = subprocess.Popen(
        ["npm", "run", "dev"],
        cwd=frontend_dir,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )
    
    print_info(f"Frontend process başlatıldı (PID: {process.pid})")
    
    # Frontend'in hazır olmasını bekle
    for i in range(30):  # 30 saniye bekle
        time.sleep(1)
        if asyncio.run(check_frontend_health()):
            print_success("Frontend başarıyla başlatıldı!")
            return process
        print(f"Frontend bekleniyor... ({i+1}/30)")
    
    print_error("Frontend başlatılamadı!")
    return None

async def deploy_sanal_supurge_strategy():
    """Sanal Süpürge V1 stratejisini deploy et"""
    print_step("3", "Sanal Süpürge V1 Strategy Deployment")
    
    try:
        # Test deployment endpoint'ini çağır
        response = requests.post(
            "http://localhost:8002/api/v1/strategy-deployment/test-deployment",
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            if result.get("success"):
                deployment_id = result.get("deployment_id")
                print_success(f"Strateji başarıyla deploy edildi! Deployment ID: {deployment_id}")
                return deployment_id
            else:
                print_error(f"Deployment başarısız: {result.get('message')}")
                return None
        else:
            print_error(f"Deployment API hatası: {response.status_code}")
            return None
            
    except Exception as e:
        print_error(f"Deployment hatası: {str(e)}")
        return None

async def check_deployment_status(deployment_id):
    """Deployment durumunu kontrol et"""
    print_step("4", "Deployment Durumu Kontrolü")
    
    try:
        response = requests.get(
            f"http://localhost:8002/api/v1/strategy-deployment/deployments/{deployment_id}",
            timeout=10
        )
        
        if response.status_code == 200:
            deployment_info = response.json()
            status = deployment_info.get("status")
            
            print_info(f"Deployment Durumu: {status}")
            print_info(f"Deployment Adı: {deployment_info.get('deployment_name')}")
            print_info(f"Strateji: {deployment_info.get('strategy_config', {}).get('strategy_name')}")
            print_info(f"Hedef Hesap Sayısı: {len(deployment_info.get('target_accounts', []))}")
            
            if status == "deployed":
                print_success("Deployment aktif ve çalışıyor!")
                return True
            elif status == "failed":
                error_msg = deployment_info.get("error_message", "Bilinmeyen hata")
                print_error(f"Deployment başarısız: {error_msg}")
                return False
            else:
                print_info(f"Deployment durumu: {status}")
                return True
                
        else:
            print_error(f"Deployment durumu alınamadı: {response.status_code}")
            return False
            
    except Exception as e:
        print_error(f"Deployment durumu kontrol hatası: {str(e)}")
        return False

async def check_mt5_connections():
    """MT5 hesap bağlantılarını kontrol et"""
    print_step("5", "MT5 Hesap Bağlantı Kontrolü")
    
    try:
        # Demo hesapları listele
        response = requests.get(
            "http://localhost:8002/api/v1/strategy-deployment/accounts/demo",
            timeout=10
        )
        
        if response.status_code == 200:
            accounts = response.json()
            print_success(f"{len(accounts)} demo hesap bulundu:")
            
            for account in accounts:
                print_info(f"  - {account['name']}: {account['login']} ({account['server']})")
                print_info(f"    Bakiye: ${account['balance']:,.2f} {account['currency']}")
                print_info(f"    Açıklama: {account['description']}")
                print()
            
            return True
        else:
            print_error(f"Demo hesapları alınamadı: {response.status_code}")
            return False
            
    except Exception as e:
        print_error(f"MT5 hesap kontrolü hatası: {str(e)}")
        return False

async def check_system_status():
    """Genel sistem durumunu kontrol et"""
    print_step("6", "Sistem Durumu Kontrolü")
    
    try:
        response = requests.get("http://localhost:8002/api/v1/system/status", timeout=10)
        
        if response.status_code == 200:
            status = response.json()
            print_success("Sistem durumu:")
            print_info(f"  Platform: {status['platform']} v{status['version']}")
            print_info(f"  Total Endpoints: {status['total_endpoints']}")
            print_info(f"  System Health: {status['system_health']}")
            print_info(f"  Uptime: {status['uptime']}")
            
            # Faz durumları
            phases = status.get('phases_status', {})
            for phase_name, phase_info in phases.items():
                print_info(f"  {phase_name}: {phase_info['status']} ({phase_info['endpoints']} endpoints)")
            
            return True
        else:
            print_error(f"Sistem durumu alınamadı: {response.status_code}")
            return False
            
    except Exception as e:
        print_error(f"Sistem durumu kontrol hatası: {str(e)}")
        return False

def print_final_summary(deployment_id, backend_process, frontend_process):
    """Final özet bilgileri"""
    print("\n" + "=" * 80)
    print("🎉 SİSTEM BAŞARIYLA BAŞLATILDI!")
    print("=" * 80)
    
    print("\n📊 ÇALIŞAN SERVİSLER:")
    print(f"  • Backend: http://localhost:8002 (PID: {backend_process.pid if backend_process else 'N/A'})")
    print(f"  • Frontend: http://localhost:3000 (PID: {frontend_process.pid if frontend_process else 'N/A'})")
    print(f"  • Strategy Deployment ID: {deployment_id or 'N/A'}")
    
    print("\n🔗 ÖNEMLİ LINKLER:")
    print("  • Ana Sayfa: http://localhost:3000")
    print("  • API Docs: http://localhost:8002/docs")
    print("  • Strategy Deployment: http://localhost:8002/api/v1/strategy-deployment")
    print("  • System Status: http://localhost:8002/api/v1/system/status")
    
    print("\n💰 AKTİF STRATEJİ:")
    print("  • Sanal Süpürge V1: 14 seviyeli grid trading sistemi")
    print("  • Master Hesap: 25201110 (Tickmill-Demo)")
    print("  • Copy Hesapları: 25216036, 25216037")
    print("  • Symbol: EURUSD")
    print("  • Timeframe: M15")
    
    print("\n⚠️  ÖNEMLİ NOTLAR:")
    print("  • Sistem demo hesaplarla çalışmaktadır")
    print("  • Copy trading otomatik olarak aktiftir")
    print("  • Gerçek para ile işlem yapmadan önce test edin")
    print("  • Performans takibi /api/v1/strategy-deployment/deployments/{deployment_id}/performance adresinden yapılabilir")
    
    print("\n🛑 SİSTEMİ DURDURMAK İÇİN:")
    print("  • Ctrl+C tuşlayın veya terminal'i kapatın")
    print("  • Manuel olarak process'leri öldürmek için:")
    if backend_process:
        print(f"    kill {backend_process.pid}  # Backend")
    if frontend_process:
        print(f"    kill {frontend_process.pid}  # Frontend")
    
    print("\n" + "=" * 80)

async def main():
    """Ana fonksiyon"""
    print("🚀 AI ALGO TRADE - SANAL SÜPÜRGE V1 STRATEGY DEPLOYMENT")
    print("=" * 80)
    print("Bu script Sanal Süpürge V1 stratejisini tam sistem ile başlatır")
    print("Hafızada bulunan 3 demo hesap kullanılacak:")
    print("  • Master: 25201110 (Tickmill-Demo)")  
    print("  • Copy 1: 25216036 (Tickmill-Demo)")
    print("  • Copy 2: 25216037 (Tickmill-Demo)")
    print("=" * 80)
    
    backend_process = None
    frontend_process = None
    deployment_id = None
    
    try:
        # 1. Backend başlat
        backend_process = start_backend()
        if not backend_process:
            print_error("Backend başlatılamadı, çıkılıyor...")
            return
        
        # 2. Frontend başlat
        frontend_process = start_frontend()
        if not frontend_process:
            print_error("Frontend başlatılamadı, sadece backend çalışıyor...")
        
        # 3. Strategy deploy et
        deployment_id = await deploy_sanal_supurge_strategy()
        if not deployment_id:
            print_error("Strategy deployment başarısız!")
        
        # 4. Deployment durumunu kontrol et
        if deployment_id:
            await asyncio.sleep(5)  # Deployment'ın hazır olmasını bekle
            await check_deployment_status(deployment_id)
        
        # 5. MT5 bağlantılarını kontrol et
        await check_mt5_connections()
        
        # 6. Sistem durumunu kontrol et
        await check_system_status()
        
        # 7. Final özet
        print_final_summary(deployment_id, backend_process, frontend_process)
        
        # 8. Sistem çalışmaya devam etsin
        print("\n💡 Sistem çalışıyor... Durdurmak için Ctrl+C tuşlayın")
        
        try:
            # Kullanıcı müdahale edene kadar bekle
            while True:
                await asyncio.sleep(1)
        except KeyboardInterrupt:
            print("\n\n🛑 Kullanıcı tarafından durduruldu...")
            
    except Exception as e:
        print_error(f"Beklenmeyen hata: {str(e)}")
    
    finally:
        # Cleanup
        print("\n🧹 Cleanup işlemi...")
        
        if frontend_process:
            print_info("Frontend kapatılıyor...")
            frontend_process.terminate()
            
        if backend_process:
            print_info("Backend kapatılıyor...")
            backend_process.terminate()
            
        print_success("Sistem başarıyla kapatıldı!")

if __name__ == "__main__":
    asyncio.run(main()) 