# 🚀 AI Algo Trade - Güncel Sistem Kılavuzu

## 📋 Sistem Özeti

Bu platform, gelişmiş AI teknolojileri ile donatılmış **birleşik (unified)** bir trading sistemidir. Tüm modüller olay tabanlı (event-driven) mimari ile entegre çalışır ve **doğrudan** gerçek MT5 demo hesabına bağlanır.

## 🎯 Tek Noktadan Başlatma (Kesin Çözüm)

Tüm sistem (Backend + Frontend), terminal sorunlarını aşmak için tasarlanmış **tek bir Python script'i** üzerinden başlatılır.

### ⚡ Başlatma Komutu

Yeni bir **PowerShell** veya **CMD** terminali açın ve aşağıdaki komutu çalıştırın:

```powershell
# Projenin ana dizininde olduğunuzdan emin olun
.\backend\venv_main\Scripts\python.exe .\master_startup.py
```

Bu script otomatik olarak:
- ✅ **Backend Sunucusunu** başlatır (Port 8002).
- ✅ **Frontend Dashboard'u** ayrı bir süreçte başlatır (Port 3000).
- ✅ **MT5 Bağlantısını** kurar ve durumu loglar.
- ✅ Tüm logları script'i çalıştırdığınız terminalde canlı olarak gösterir.

## 🏗️ Sistem Mimarisi

### 🔧 Backend Sunucusu (Port 8002)
- **Ana Başlatıcı**: `master_startup.py`
- **Sanal Ortam**: `backend/venv_main`
- **Özellikler**:
  - **Unified Trading Engine**: Tüm modülleri (God Mode, Shadow Mode vb.) yöneten merkezi motor.
  - **Doğrudan MT5 Bağlantısı**: Tickmill-Demo hesabına direkt bağlantı.
  - **Event-Driven Mimari**: Modüller arası anlık iletişim.
  - **Birleşik API**: Tüm servisler tek bir noktadan sunulur.

### 🌐 Frontend Dashboard (Port 3000+)
- **Framework**: Next.js 14
- **Özellikler**:
  - Quantum ve ana dashboard'lar.
  - Gerçek zamanlı veri görselleştirme (`SystemMonitor`, `PerformanceMetrics`).
  - Dinamik sembol listeleri (Hafta sonu/hafta içi modları).

## 🔑 Ana API Endpoints (Port 8002)

```bash
# Sistem ve MT5 bağlantı durumu
GET http://localhost:8002/health

# Detaylı sistem ve trade performansı
GET http://localhost:8002/performance

# Aktif sembolleri al (Hafta sonu/içi otomatik)
GET http://localhost:8002/api/v1/market_data/symbols/active

# API dokümantasyonu
GET http://localhost:8002/docs
```

## 📈 MT5 Demo Hesap Detayları

```
Login:    25201110
Server:   Tickmill-Demo
Password: e|([rXU1IsiM
```

## 🔍 Sorun Giderme

### "python.exe is not recognized..." Hatası
Bu hata, terminalin Python'u bulamadığı anlamına gelir. Bu, makinenizin `PATH` ayarlarıyla ilgilidir. Yukarıda verilen **tam dosya yoluyla** komutu çalıştırmak (`.\backend\venv_main\Scripts\python.exe`) bu sorunu çözer.

### Modül Bulunamadı Hatası
`master_startup.py` script'i, `sys.path`'i otomatik olarak ayarlayarak bu sorunu çözer. Eğer hala hata alıyorsanız, `venv_main` sanal ortamı bozulmuş olabilir.
1. `backend/venv_main` klasörünü silin.
2. `python -m venv backend/venv_main` ile yeniden oluşturun.
3. `backend\venv_main\Scripts\pip.exe install -r backend\requirements.txt` ile paketleri kurun.

## 🎮 Ana Modüller

### 1. 🧠 Strategy Whisperer
- **URL**: http://localhost:3000/strategy-whisperer
- **Özellik**: Doğal dil ile MQL5 strateji oluşturma
- **Kullanım**: 
  ```
  "EURUSD için RSI 30/70 seviyelerinde scalping stratejisi oluştur"
  "Moving average crossover ile trend following sistemi yap"
  ```

### 2. ⚡ Adaptive Trade Manager
- **URL**: http://localhost:3000/adaptive-trade-manager
- **Özellik**: Dinamik risk yönetimi ve pozisyon optimizasyonu
- **Özellikler**:
  - Dynamic SL/TP adjustment
  - Real-time risk calculation
  - Position monitoring
  - Alert management

### 3. 👁️ God Mode
- **URL**: http://localhost:3000/god-mode
- **Özellik**: Omniscient piyasa analizi
- **Özellikler**:
  - Quantum analysis engine
  - Predictive modeling
  - Multi-dimensional market view
  - Divine intervention signals

### 4. 🕵️ Shadow Mode
- **URL**: http://localhost:3000/shadow
- **Özellik**: Kurumsal hareket takibi
- **Özellikler**:
  - Institutional tracker
  - Dark pool monitoring
  - Whale detection
  - Stealth execution

### 5. 📰 Market Narrator
- **URL**: http://localhost:3000/market-narrator
- **Özellik**: AI destekli piyasa hikayeciliği
- **Özellikler**:
  - Story generation
  - Correlation analysis
  - Influence mapping
  - Narrative feeds

## 🎯 Başarı İpuçları

1. **İlk Kurulum**: `master_startup.py` komutunu çalıştırın
2. **Günlük Kullanım**: `system_status.bat` ile durumu izleyin
3. **Test Trading**: Küçük hacimlerle başlayın
4. **Risk Yönetimi**: Stop-loss kullanmayı unutmayın
5. **Monitoring**: Event bus'ı aktif takip edin

---

**🚀 Happy Trading! Başarılı işlemler dileriz! 📈** 