# AI Algo Trade - Hızlı Başlangıç Kılavuzu

## 🚀 Sistem Özellikleri

Bu platform aşağıdaki gelişmiş özelliklerle donatılmıştır:

### 📊 Ana Modüller
1. **Strategy Whisperer** - Doğal dil ile strateji oluşturma
2. **Adaptive Trade Manager** - Dinamik risk yönetimi
3. **God Mode** - Omniscient piyasa analizi
4. **Shadow Mode** - Kurumsal hareket takibi
5. **Market Narrator** - AI destekli piyasa hikayeciliği
6. **Real-time MT5 Integration** - Canlı Tickmill demo hesabı

### 🔧 Teknik Özellikler
- Event-driven mimarisi
- Unified Trading Engine
- Real-time crypto trading (ETH/USD, BTC/USD)
- ICT analysis engine
- Quantum dashboard
- WhatsApp-style chat UI

## 🎯 Hızlı Başlatma

### Seçenek 1: Basit Backend Başlatma
```bash
start_simple_backend.bat
```

### Seçenek 2: Manuel Backend Başlatma
```bash
# Bağımlılıkları yükle
pip install requests pandas pydantic-settings MetaTrader5 fastapi uvicorn

# Backend'i başlat
cd backend
python start_unified_backend.py
```

### Seçenek 3: Crypto Trading Backend (Port 8004)
```bash
start_real_crypto_backend.bat
```

## 🌐 Frontend Başlatma

### Seçenek 1: Basit Frontend Başlatma
```bash
start_simple_frontend.bat
```

### Seçenek 2: Manuel Frontend Başlatma
```bash
cd frontend
rd /s /q .next
npm install --legacy-peer-deps
npm run dev
```

## 📱 Erişim Noktaları

### Backend API'ler
- **Unified Backend**: http://localhost:8000
- **Real Crypto Backend**: http://localhost:8004
- **API Docs**: http://localhost:8000/docs

### Frontend Dashboard
- **Ana Dashboard**: http://localhost:3000
- **Alternatif Portlar**: 3001, 3002, 3003

## 🔑 Önemli Endpoint'ler

### Unified Trading API (Port 8000)
```
GET  /health                    - Sistem durumu
GET  /api/v1/unified/status     - Trading engine durumu
POST /api/v1/unified/signal     - Manuel sinyal gönderme
GET  /api/v1/unified/metrics    - Performans metrikleri
```

### Real Crypto API (Port 8004)
```
GET  /health                    - MT5 bağlantı durumu
GET  /api/v1/crypto/prices      - Canlı ETH/USD, BTC/USD fiyatları
POST /api/v1/crypto/trade       - Gerçek trade işlemi
GET  /api/v1/account            - Hesap bilgileri
```

## 🎮 Dashboard Modülleri

### 1. Strategy Whisperer
- **URL**: http://localhost:3000/strategy-whisperer
- **Özellik**: Doğal dil ile MQL5 strateji oluşturma
- **Kullanım**: "EURUSD için RSI tabanlı scalping stratejisi yap"

### 2. Adaptive Trade Manager
- **URL**: http://localhost:3000/adaptive-trade-manager
- **Özellik**: Dinamik SL/TP ayarlama
- **Kullanım**: Risk parametrelerini gerçek zamanlı ayarlama

### 3. God Mode
- **URL**: http://localhost:3000/god-mode
- **Özellik**: Omniscient piyasa analizi
- **Kullanım**: Gelecek fiyat tahminleri ve quantum analiz

### 4. Shadow Mode
- **URL**: http://localhost:3000/shadow
- **Özellik**: Kurumsal hareket takibi
- **Kullanım**: Whale aktiviteleri ve dark pool monitoring

### 5. Market Narrator
- **URL**: http://localhost:3000/market-narrator
- **Özellik**: AI destekli piyasa hikayeciliği
- **Kullanım**: Piyasa olaylarının hikaye formatında sunumu

## 🔧 Sorun Giderme

### Backend Sorunları
1. **ModuleNotFoundError**: `pip install [missing_module]`
2. **Port zaten kullanımda**: Farklı port kullanın
3. **MT5 bağlantı hatası**: MT5 terminali açık olmalı

### Frontend Sorunları
1. **Chunk loading error**: `.next` klasörünü silin
2. **Module not found**: `npm install --legacy-peer-deps`
3. **Port conflict**: Otomatik olarak 3001, 3002 dener

## 📈 MT5 Demo Hesap Bilgileri
- **Login**: 25201110
- **Server**: Tickmill-Demo
- **Password**: e|([rXU1IsiM
- **Currency**: USD
- **Type**: Classic

## 🚀 Gelişmiş Kullanım

### Event Bus Monitoring
```bash
# Event geçmişini görüntüle
curl http://localhost:8000/api/v1/events/history

# Manuel event gönder
curl -X POST http://localhost:8000/api/v1/events/emit \
  -H "Content-Type: application/json" \
  -d '{"event_type": "test.signal", "data": {"symbol": "EURUSD"}, "priority": "HIGH"}'
```

### Real-time Crypto Monitoring
```bash
# Canlı fiyatları görüntüle
curl http://localhost:8004/api/v1/crypto/prices

# Test trade işlemi
curl -X POST http://localhost:8004/api/v1/crypto/trade \
  -H "Content-Type: application/json" \
  -d '{"symbol": "ETHUSD", "action": "BUY", "volume": 0.1}'
```

## 📊 Performans İzleme

### Sistem Metrikleri
- Trade success rate
- Event processing latency
- MT5 connection stability
- Module integration status

### Dashboard Analytics
- Real-time P&L
- Risk exposure
- Signal accuracy
- Market correlation

## 🎯 Sonraki Adımlar

1. **Backend'i başlatın**: `start_simple_backend.bat`
2. **Frontend'i başlatın**: `start_simple_frontend.bat`
3. **Dashboard'a erişin**: http://localhost:3000
4. **Strategy Whisperer'ı deneyin**: Doğal dil ile strateji oluşturun
5. **Real-time trading'i izleyin**: Crypto backend ile canlı işlemler

## 🆘 Destek

Herhangi bir sorun yaşarsanız:
1. Log dosyalarını kontrol edin
2. Dependencies'leri yeniden yükleyin
3. Cache'leri temizleyin
4. Portları kontrol edin

**Başarılı trading! 🚀📈** 