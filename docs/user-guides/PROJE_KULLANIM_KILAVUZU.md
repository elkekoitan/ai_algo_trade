# AI ALGO TRADE - PROJE KULLANIM KILAVUZU

## 🚀 Hızlı Başlangıç

### Tek Komutla Başlatma
```bash
BASLA.bat
```

Bu komut otomatik olarak:
- Python ve gerekli paketleri kontrol eder
- MT5 bağlantısını test eder
- Backend'i başlatır (Port 8002)
- Frontend'i başlatır (Port 3000)

### Tarayıcıda Açma
Proje başladıktan sonra tarayıcınızda şu adresi açın:
```
http://localhost:3000
```

## 📋 Sistem Gereksinimleri

- **Python 3.8+** (3.13.1 test edildi)
- **Node.js 16+**
- **MetaTrader 5** (Windows)
- **Windows 10/11**

## 🔧 Manuel Kurulum (Gerekirse)

### 1. Python Paketleri
```bash
pip install -r requirements.txt
```

### 2. Frontend Bağımlılıkları
```bash
cd frontend
npm install
```

## 🏗️ Proje Yapısı

```
ai_algo_trade/
├── backend/           # FastAPI backend
│   ├── api/          # API endpoints
│   ├── modules/      # Trading modülleri
│   └── core/         # Core sistemler
├── frontend/         # Next.js frontend
│   ├── app/          # Sayfalar
│   └── components/   # UI bileşenleri
└── docs/            # Dokümantasyon
```

## 🔌 MT5 Bağlantı Bilgileri

- **Login:** 25201110
- **Server:** Tickmill-Demo
- **Hesap Türü:** Demo USD

## 📊 Özellikler

### Dashboard
- Gerçek zamanlı hesap bilgileri
- Canlı fiyat takibi
- Trade geçmişi
- Performance grafikleri

### Trading Modülleri
- **God Mode**: Gelişmiş tahmin ve analiz
- **Shadow Mode**: Kurumsal hareket takibi
- **Adaptive Trade Manager**: Otomatik risk yönetimi
- **Market Narrator**: Piyasa hikaye anlatımı
- **Strategy Whisperer**: Doğal dil ile strateji oluşturma

## 🛠️ Sorun Giderme

### Backend Başlamıyor
1. Python path'ini kontrol edin
2. Tüm paketlerin yüklü olduğundan emin olun
3. 8002 portunu kullanan başka bir uygulama var mı kontrol edin

### Frontend Başlamıyor
1. Node.js'in yüklü olduğundan emin olun
2. `frontend` klasöründe `npm install` çalıştırın
3. 3000 portunu kontrol edin

### MT5 Bağlantı Hatası
1. MetaTrader 5'in açık olduğundan emin olun
2. Demo hesap bilgilerini kontrol edin
3. İnternet bağlantınızı kontrol edin

## 📞 Destek

Sorunlar için GitHub Issues kullanın veya dokümantasyonu inceleyin.

## 🎯 Hafta Sonu Modu

Hafta sonları sadece kripto işlemleri aktiftir:
- BTCUSD, ETHUSD, XRPUSD vb.
- Forex piyasaları kapalı

## ⚡ Performans İpuçları

1. Gereksiz modülleri kapatın
2. Düzenli olarak log dosyalarını temizleyin
3. Yüksek frekanslı işlemlerde dikkatli olun

---

**Not:** Bu bir demo/geliştirme ortamıdır. Gerçek para ile kullanmadan önce kapsamlı test yapın. 