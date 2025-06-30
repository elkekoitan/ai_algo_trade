# Unified Trading Engine - Başlatma Kılavuzu

## 🚀 Hızlı Başlangıç

### 1. Backend'i Başlatma

#### Yöntem 1: Batch Dosyası (Önerilen)
```bash
# Ana dizinde:
start_unified_windows.bat
```

#### Yöntem 2: Manuel Başlatma
```bash
# Terminal'de:
cd backend
python unified_main.py
```

#### Yöntem 3: Virtual Environment ile
```bash
# Ana dizinde:
backend\venv\Scripts\python.exe backend\unified_main.py
```

### 2. Sistem Kontrolü

Backend başladıktan sonra aşağıdaki URL'leri kontrol edin:

- **Ana Sayfa**: http://localhost:8002/
- **API Dokümantasyonu**: http://localhost:8002/docs
- **Sağlık Kontrolü**: http://localhost:8002/health
- **Event Geçmişi**: http://localhost:8002/api/v1/events/history

## 📋 Event Bus Sistemi

### Event Bus Özellikleri

1. **Öncelik Bazlı İşleme**
   - CRITICAL: Acil trade sinyalleri
   - HIGH: Önemli market olayları
   - NORMAL: Standart güncellemeler
   - LOW: Bilgilendirme mesajları

2. **Asenkron Event İşleme**
   - Non-blocking event emission
   - Concurrent handler execution
   - Event filtering ve history

3. **Modül Entegrasyonu**
   - Tüm modüller event bus üzerinden haberleşir
   - Otomatik event routing
   - Cross-module signal enrichment

### Event Örnekleri

```python
# Trade sinyali gönderme
POST /api/v1/events/emit
{
    "event_type": "trade.signal",
    "data": {
        "symbol": "EURUSD",
        "action": "BUY",
        "confidence": 0.85
    },
    "priority": "HIGH"
}

# Market güncelleme
POST /api/v1/events/emit
{
    "event_type": "market.update",
    "data": {
        "symbol": "XAUUSD",
        "price": 2050.50,
        "volume": 1500000
    },
    "priority": "NORMAL"
}
```

## 🔧 Unified Trading Engine

### Entegre Modüller

1. **Adaptive Trade Manager (ATM)**
   - Dinamik SL/TP ayarlama
   - Risk yönetimi
   - Pozisyon optimizasyonu

2. **God Mode**
   - Tahmin modelleri
   - Quantum analiz
   - Omniscient monitoring

3. **Market Narrator**
   - Hikaye üretimi
   - Korelasyon analizi
   - Etki haritaları

4. **Shadow Mode**
   - Kurumsal takip
   - Dark pool monitoring
   - Whale detection

### API Endpoints

#### Unified Trading
- `GET /api/v1/unified/status` - Sistem durumu
- `GET /api/v1/unified/dashboard` - Dashboard verileri
- `POST /api/v1/unified/execute-trade` - Trade çalıştırma
- `GET /api/v1/unified/active-modules` - Aktif modüller

#### Event Management
- `POST /api/v1/events/emit` - Event gönderme
- `GET /api/v1/events/history` - Event geçmişi

#### Module-Specific
- `/api/v1/adaptive-trade-manager/*` - ATM endpoints
- `/api/v1/god-mode/*` - God Mode endpoints
- `/api/v1/market-narrator/*` - Market Narrator endpoints
- `/api/v1/shadow-mode/*` - Shadow Mode endpoints

## 📊 Signal Flow

```
1. Original Signal → Event Bus
2. God Mode adds prediction
3. Market Narrator adds context
4. Shadow Mode adds whale intelligence
5. ATM calculates dynamic SL/TP
6. Risk Manager validates
7. Order Execution
```

## 🛠️ Troubleshooting

### Backend Başlamıyor
1. Python 3.8+ kurulu olduğundan emin olun
2. Gerekli paketleri yükleyin: `pip install -r backend/requirements.txt`
3. Port 8002'nin kullanımda olmadığından emin olun

### MT5 Bağlantı Hatası
1. MT5 credentials'ların doğru olduğundan emin olun
2. MetaTrader 5 terminal'in açık olduğundan emin olun
3. Demo hesabın aktif olduğunu kontrol edin

### Event Bus Hataları
1. Redis bağlantısını kontrol edin (opsiyonel)
2. Event handler'ların async olduğundan emin olun
3. Priority değerlerinin doğru olduğunu kontrol edin

## 🎯 Kullanım Senaryoları

### 1. Manuel Trade with AI Enhancement
```python
# 1. Signal oluştur
POST /api/v1/unified/process-signal
{
    "symbol": "EURUSD",
    "action": "BUY",
    "volume": 0.1
}

# 2. Enriched signal'i al
# 3. Execute trade
```

### 2. Automated Trading
```python
# 1. Auto-trader'ı başlat
POST /api/v1/unified/start-module/auto_trader

# 2. Monitoring
GET /api/v1/unified/module-status/auto_trader
```

### 3. Event Monitoring
```python
# Event history'yi takip et
GET /api/v1/events/history?limit=50

# Belirli event türlerini filtrele
GET /api/v1/events/history?event_type=trade.signal
```

## 📈 Performance Metrics

Backend başarıyla çalıştığında:
- Event processing latency: <10ms
- API response time: <100ms
- Module startup time: <5s per module
- Memory usage: ~200-500MB (modül sayısına bağlı)

## 🔐 Güvenlik

- CORS ayarları production için güncellenmeli
- API key authentication eklenebilir
- Rate limiting uygulanmalı
- SSL/TLS production'da zorunlu

## 📞 Destek

Sorun yaşarsanız:
1. Backend log'larını kontrol edin
2. `/health` endpoint'ini test edin
3. Event history'yi inceleyin
4. Module status'lerini kontrol edin 