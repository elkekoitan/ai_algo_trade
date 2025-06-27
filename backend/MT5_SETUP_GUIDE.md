# MT5 Terminal Kurulum ve Konfigürasyon Rehberi

## 1. MetaTrader 5 Terminal Kurulumu

### Windows için:
1. **MetaTrader 5 İndir**: https://www.metatrader5.com/en/download
2. **Kurulum yapın** ve MT5 Terminal'i başlatın
3. **Demo hesap** açın veya mevcut hesap bilgilerinizi girin

### Broker Seçimi:
- **Demo Hesap**: Herhangi bir büyük broker (MetaQuotes Demo, Alpari, etc.)
- **Live Hesap**: Kendi broker'ınızın bilgileri

## 2. Environment Variables Ayarları

Sistem environment variables'larını ayarlayın:

```bash
# Windows CMD
set MT5_LOGIN=123456789
set MT5_PASSWORD=your_password
set MT5_SERVER=MetaQuotes-Demo

# Windows PowerShell
$env:MT5_LOGIN="123456789"
$env:MT5_PASSWORD="your_password"
$env:MT5_SERVER="MetaQuotes-Demo"

# Linux/Mac
export MT5_LOGIN=123456789
export MT5_PASSWORD=your_password
export MT5_SERVER=MetaQuotes-Demo
```

## 3. MT5 Terminal Konfigürasyonu

### Algoritmic Trading'i Etkinleştirin:
1. MT5 Terminal → **Tools** → **Options**
2. **Expert Advisors** sekmesi
3. ✅ **Allow algorithmic trading**
4. ✅ **Allow DLL imports**
5. ✅ **Allow imports of external experts**

### Sembolleri Ekleyin:
1. **Market Watch** → Right click → **Symbols**
2. İhtiyacınız olan sembolleri ekleyin:
   - EURUSD
   - GBPUSD
   - USDJPY
   - XAUUSD (Gold)
   - US30 (Dow Jones)

## 4. Python MetaTrader5 Kütüphanesi

```bash
pip install MetaTrader5
```

## 5. Bağlantı Testi

Backend'i başlatın ve aşağıdaki endpoint'i test edin:

```bash
# Backend başlat
cd backend
python main.py

# Test endpoint
curl http://localhost:8001/api/v1/health
```

## 6. Başarılı Bağlantı Çıktısı

```
🚀 Starting ICT Ultra v2: REAL MT5 Integration
✅ REAL MT5 connection established successfully
Account: 123456789
Server: MetaQuotes-Demo
Balance: $10,000.00
🎉 ICT Ultra v2 REAL platform started successfully
```

## 7. Hata Giderme

### MT5 Bağlantı Hataları:
- **Terminal çalışıyor mu?** MT5 Terminal açık olmalı
- **Hesap giriş yapmış mı?** Terminal'de account login olmalı
- **Algoritmic trading aktif mi?** Options'da etkinleştirilmeli
- **Environment variables doğru mu?** Login, password, server

### Genel Hatalar:
```bash
# MT5 durumunu kontrol et
python -c "import MetaTrader5 as mt5; print(mt5.initialize()); print(mt5.last_error())"
```

## 8. Güvenlik Notları

- **Demo hesap kullanın** geliştirme için
- **Environment variables'ı güvenli tutun**
- **MT5 Terminal güncel tutun**
- **Broker'ınızın API politikalarını kontrol edin** 