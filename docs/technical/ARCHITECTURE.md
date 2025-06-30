# ICT Ultra v2: Mimari Dokümantasyon

Bu doküman, ICT Ultra v2 platformunun genel mimari yapısını, tasarım prensiplerini ve bileşenler arası ilişkileri detaylandırmaktadır.

## Mimari Vizyon

ICT Ultra v2, modüler monolith mimarisi üzerine inşa edilmiş, domain-driven design prensiplerini uygulayan ve clean architecture katmanlarını kullanan bir trading platformudur. Platform, MetaTrader 5'in yeni Git entegrasyonu ve MQL5 Algo Forge özelliklerini tam olarak destekleyecek şekilde tasarlanmıştır.

## Temel Mimari Prensipler

1. **Modüler Monolith:** Tüm sistem tek bir deployment ünitesi olarak çalışır, ancak içeride mantıksal olarak ayrılmış modüllerden oluşur.
2. **Domain-Driven Design (DDD):** İş mantığı, domain modelleri etrafında organize edilir ve ubiquitous language kullanılır.
3. **Clean Architecture:** Bağımlılıklar içeriden dışarıya doğru akar; domain katmanı hiçbir dış katmana bağımlı değildir.
4. **Event-Driven:** Modüller arası iletişim, event'ler üzerinden gerçekleşir.
5. **CQRS Pattern:** Komut (Command) ve sorgu (Query) sorumlulukları ayrılmıştır.

## Sistem Bileşenleri

### 1. Backend (Python/FastAPI)

```
backend/
├── core/
│   ├── config/       # Yapılandırma yönetimi
│   ├── database/     # Veritabanı bağlantıları ve modelleri
│   ├── events/       # Event bus ve event handlers
│   ├── logging/      # Loglama altyapısı
│   └── cache/        # Redis cache yönetimi
├── modules/
│   ├── account/      # Kullanıcı ve hesap yönetimi
│   ├── market_data/  # Piyasa verisi işleme
│   ├── trading/      # İşlem yönetimi
│   ├── signals/      # ICT sinyalleri ve analiz
│   ├── risk/         # Risk yönetimi
│   ├── ai/           # Yapay zeka ve ML modelleri
│   └── mt5_integration/ # MT5 bağlantısı ve MQL5 Algo Forge
└── api/
    ├── v1/           # API endpoints (version 1)
    └── websocket/    # WebSocket bağlantıları
```

### 2. Frontend (Next.js/TypeScript/TailwindCSS)

```
frontend/
├── app/              # Next.js 13+ App Router yapısı
│   ├── dashboard/    # Ana dashboard sayfası
│   ├── charts/       # Grafik görüntüleme sayfaları
│   ├── trading/      # İşlem sayfaları
│   ├── signals/      # Sinyal analiz sayfaları
│   ├── risk/         # Risk yönetimi sayfaları
│   ├── settings/     # Ayarlar sayfaları
│   └── forge/        # MQL5 Algo Forge yönetim sayfaları
├── components/       # Yeniden kullanılabilir bileşenler
│   ├── ui/           # Temel UI bileşenleri
│   ├── charts/       # Grafik bileşenleri
│   ├── trading/      # İşlem bileşenleri
│   └── forge/        # Algo Forge bileşenleri
└── lib/              # Yardımcı fonksiyonlar ve hooks
    ├── api/          # API istemcileri
    ├── store/        # State yönetimi
    └── utils/        # Yardımcı fonksiyonlar
```

### 3. MQL5 Forge Repos

```
mql5_forge_repos/
├── strategies/       # Trading stratejileri
│   ├── ict_ob_strategy/  # Order Block stratejisi
│   ├── ict_fvg_strategy/ # Fair Value Gap stratejisi
│   └── smart_money_flow/ # Smart Money Flow stratejisi
├── indicators/       # Teknik göstergeler
│   ├── order_blocks/     # Order Block göstergeleri
│   ├── fair_value_gaps/  # FVG göstergeleri
│   └── liquidity_levels/ # Likidite seviyesi göstergeleri
└── libraries/       # Yeniden kullanılabilir MQL5 kütüphaneleri
    ├── ict_core/        # ICT konsept çekirdek fonksiyonları
    ├── risk_management/ # Risk yönetimi fonksiyonları
    └── utils/           # Yardımcı fonksiyonlar
```

## Veri Akışı

1. **MT5 → Backend:** MetaTrader 5 platformundan canlı fiyat verileri ve hesap bilgileri backend'e aktarılır.
2. **Backend → Frontend:** Backend, işlenmiş verileri REST API ve WebSocket üzerinden frontend'e iletir.
3. **Frontend → Backend → MT5:** Kullanıcı frontend'den işlem talimatı verdiğinde, bu talep backend üzerinden MT5'e iletilir.
4. **Git ↔ MQL5 Forge Repos:** MQL5 Algo Forge'daki Git repoları ile yerel MQL5 Forge Repos klasörü arasında senkronizasyon sağlanır.

## Teknoloji Yığını

### Backend
- **Python 3.13+**: Ana programlama dili
- **FastAPI**: Web framework
- **SQLAlchemy**: ORM (Object-Relational Mapping)
- **Redis**: Cache ve pub/sub mesajlaşma
- **MetaTrader5 Python Package**: MT5 bağlantısı

### Frontend
- **Next.js 14+**: React framework
- **TypeScript**: Tip güvenliği
- **TailwindCSS**: Stil kütüphanesi
- **TradingView Lightweight Charts**: Grafik kütüphanesi
- **Socket.io-client**: WebSocket bağlantıları

### DevOps & Araçlar
- **Git**: Versiyon kontrolü
- **Docker**: Konteynerizasyon
- **GitHub Actions**: CI/CD
- **Python Poetry**: Bağımlılık yönetimi

## Güvenlik Önlemleri

1. **API Güvenliği**: JWT tabanlı kimlik doğrulama ve yetkilendirme
2. **Rate Limiting**: API isteklerini sınırlama
3. **Input Validation**: Tüm kullanıcı girdilerinin doğrulanması
4. **Logging & Monitoring**: Kapsamlı loglama ve izleme
5. **Secure Coding Practices**: OWASP güvenlik prensiplerinin uygulanması

## Ölçeklenebilirlik

Sistem, başlangıçta modüler monolith olarak tasarlanmış olsa da, gelecekte mikroservislere geçiş için hazırlıklıdır:

1. **Modüler Yapı**: Her modül bağımsız olarak çalışabilir.
2. **Event-Driven Mimari**: Modüller arası gevşek bağlantı (loose coupling).
3. **API Abstraction**: Tüm modüller API üzerinden iletişim kurar.

## Performans Optimizasyonu

1. **Veri Önbellekleme**: Redis ile sık kullanılan verilerin önbelleklenmesi
2. **Asenkron İşlemler**: Uzun süren işlemler için asenkron işleme
3. **Veritabanı İndeksleme**: Sorgu performansını artırmak için uygun indeksleme
4. **Lazy Loading**: Frontend'de gerektiğinde veri yükleme

## Test Stratejisi

1. **Unit Tests**: Bireysel fonksiyonlar ve sınıflar için birim testleri
2. **Integration Tests**: Modüller arası entegrasyon testleri
3. **E2E Tests**: Uçtan uca kullanıcı senaryoları testleri
4. **Performance Tests**: Yük ve performans testleri 