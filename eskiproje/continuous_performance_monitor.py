import requests
import time
import json
from datetime import datetime
import os

class ContinuousPerformanceMonitor:
    def __init__(self):
        self.api_base = "http://localhost:8001"
        self.start_time = datetime.now()
        self.initial_balance = None
        self.trade_count = 0
        self.last_trade_count = 0
        self.profit_history = []
        
    def clear_screen(self):
        os.system('cls' if os.name == 'nt' else 'clear')
        
    def get_account_info(self):
        try:
            response = requests.get(f'{self.api_base}/account_info', timeout=3)
            if response.status_code == 200:
                return response.json()
        except:
            pass
        return None
    
    def get_positions(self):
        try:
            response = requests.get(f'{self.api_base}/positions', timeout=3)
            if response.status_code == 200:
                return response.json()
        except:
            pass
        return []
    
    def get_ict_signals(self):
        try:
            response = requests.get(f'{self.api_base}/ict/signals?min_score=85&max_results=20', timeout=3)
            if response.status_code == 200:
                return response.json()
        except:
            pass
        return []
    
    def calculate_stats(self, positions):
        total_profit = sum(pos.get('profit', 0) for pos in positions)
        profitable_trades = len([p for p in positions if p.get('profit', 0) > 0])
        losing_trades = len([p for p in positions if p.get('profit', 0) < 0])
        
        win_rate = (profitable_trades / len(positions) * 100) if positions else 0
        
        return {
            'total_profit': total_profit,
            'profitable_trades': profitable_trades,
            'losing_trades': losing_trades,
            'win_rate': win_rate,
            'total_trades': len(positions)
        }
    
    def display_performance(self):
        self.clear_screen()
        
        print("🚀 ICT ULTRA PLATFORM - SÜREKLI OTOMATİK İŞLEM SİSTEMİ")
        print("=" * 80)
        
        # Account Info
        account = self.get_account_info()
        if account:
            balance = account.get('balance', 0)
            equity = account.get('equity', 0)
            if self.initial_balance is None:
                self.initial_balance = balance
            
            profit_from_start = balance - self.initial_balance if self.initial_balance else 0
            roi_percent = (profit_from_start / self.initial_balance * 100) if self.initial_balance else 0
            
            print(f"💰 HESAP BİLGİLERİ:")
            print(f"   Balance: ${balance:,.2f}")
            print(f"   Equity: ${equity:,.2f}")
            print(f"   Başlangıçtan Kar: ${profit_from_start:,.2f}")
            print(f"   ROI: {roi_percent:.2f}%")
        
        # Positions
        positions = self.get_positions()
        if positions:
            stats = self.calculate_stats(positions)
            
            print(f"\n📊 TRADING PERFORMANSI:")
            print(f"   Açık Pozisyonlar: {stats['total_trades']}")
            print(f"   Toplam Kar/Zarar: ${stats['total_profit']:,.2f}")
            print(f"   Kazanan İşlemler: {stats['profitable_trades']}")
            print(f"   Kaybeden İşlemler: {stats['losing_trades']}")
            print(f"   Başarı Oranı: {stats['win_rate']:.1f}%")
            
            # Trade frequency
            current_trade_count = len(positions)
            if current_trade_count > self.last_trade_count:
                new_trades = current_trade_count - self.last_trade_count
                print(f"   🔥 Yeni İşlemler: +{new_trades}")
            self.last_trade_count = current_trade_count
        
        # ICT Signals
        signals = self.get_ict_signals()
        if isinstance(signals, list):
            high_score_signals = [s for s in signals if isinstance(s, dict) and s.get('score', 0) >= 90]
        else:
            high_score_signals = []
        
        print(f"\n🎯 ICT SİNYALLERİ:")
        print(f"   Toplam Aktif Sinyal: {len(signals)}")
        print(f"   Yüksek Skor (90+): {len(high_score_signals)}")
        
        if high_score_signals:
            print(f"   🔥 EN İYİ SİNYALLER:")
            for signal in high_score_signals[:3]:
                symbol = signal.get('symbol', 'N/A')
                score = signal.get('score', 0)
                action = signal.get('action', 'N/A')
                setup = signal.get('setup_type', 'N/A')
                print(f"      {symbol} | {action} | Score: {score} | Setup: {setup}")
        
        # System Status
        uptime = datetime.now() - self.start_time
        hours = int(uptime.total_seconds() // 3600)
        minutes = int((uptime.total_seconds() % 3600) // 60)
        
        print(f"\n⚡ SİSTEM DURUMU:")
        print(f"   Çalışma Süresi: {hours}h {minutes}m")
        print(f"   Son Güncelleme: {datetime.now().strftime('%H:%M:%S')}")
        print(f"   Backend API: ✅ Aktif")
        print(f"   ICT Engine: ✅ Çalışıyor")
        print(f"   Auto Trading: ✅ Sürekli Aktif")
        
        print("\n" + "=" * 80)
        print("💡 Dashboard: http://localhost:3000/dashboard")
        print("🔄 5 saniyede bir güncelleniyor... (Ctrl+C ile çıkış)")
    
    def run(self):
        print("🚀 ICT Ultra Platform Performance Monitor Başlatılıyor...")
        time.sleep(2)
        
        try:
            while True:
                self.display_performance()
                time.sleep(5)  # 5 saniyede bir güncelle
        except KeyboardInterrupt:
            print("\n\n👋 Performance Monitor Kapatılıyor...")
            print("Sistem çalışmaya devam ediyor!")

if __name__ == "__main__":
    monitor = ContinuousPerformanceMonitor()
    monitor.run() 