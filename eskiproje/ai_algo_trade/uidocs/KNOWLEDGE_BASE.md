# ai_algo_trade Projesi Bilgi Kütüphanesi

## 1. Proje Özeti
Bu döküman, `ai_algo_trade` projesi kapsamında geliştirilen ICT Ultra Platform'un bilgi kütüphanesidir. Projenin amacı, Inner Circle Trader (ICT) konseptlerini modern teknolojilerle birleştirerek yüksek performanslı bir algoritmik trading platformu oluşturmaktır.
Platform, MetaTrader 5 (MT5) ile entegre çalışarak gerçek zamanlı piyasa verileri üzerinde işlem yapar ve Git tabanlı MQL5 Algo Forge ile versiyon kontrollü algoritma geliştirmeyi destekler. [Demo MT5 hesabı (Login: 25201110)][[memory:1905727111279718659]] ile yapılan testlerde sistemin başarısı kanıtlanmıştır.

## 2. Mimari
ICT Ultra Platform, modüler monolit mimari prensiplerine göre tasarlanmıştır. Bu yaklaşım, monolitik uygulamaların dağıtım ve performans avantajlarını, modüler mimarinin bakım ve ölçeklenebilirlik kolaylıkları ile birleştirir.

### Mimari İlkeler
*   **Domain-Driven Design (DDD)**: Sistem, iş alanlarına göre modüllere ayrılmıştır.
*   **Clean Architecture**: Her modül, domain, application ve infrastructure katmanlarına ayrılmıştır.
*   **Gevşek Bağlılık (Loose Coupling)**: Modüller arası bağımlılıklar en aza indirilmiştir.

### Mimari Diyagramı
```mermaid
graph TD
    subgraph "ICT Ultra Platform"
        A[Main Application] --> B[Core Modules]
        A --> C[Domain Modules]
        
        subgraph "Core Modules"
            B1[Events System]
            B2[Configuration]
            B3[Database]
            B4[Cache]
            B5[Logging]
        end
        
        subgraph "Domain Modules"
            C1[Trading Module]
            C2[Market Data Module]
            C3[Signals Module]
            C4[Risk Module]
            C5[AI Module]
            C6[Account Module]
            C7[MT5 Integration Module]
        end
        
        C7 --> D[MetaTrader 5]
        
        subgraph "MT5 Integration"
            D1[Connection Service]
            D2[Trading Service]
            D3[Market Data Service]
            D4[MQL5 Algo Forge]
        end
        
        C7 --> D1
        C7 --> D2
        C7 --> D3
        C7 --> D4
        
        D4 --> E[Git Repositories]
        
        C3 --> F[ICT Concepts]
        
        subgraph "ICT Concepts"
            F1[Order Blocks]
            F2[Fair Value Gaps]
            F3[Breaker Blocks]
            F4[Liquidity Sweeps]
            F5[Market Structure]
        end
    end
```

## 3. Modüller
Platform, herbiri belirli bir işlevselliğe odaklanmış çekirdek (core) ve alan (domain) modüllerinden oluşur.

### Çekirdek Modüller
*   **Events System**: Modüller arası asenkron iletişim için olay tabanlı sistem.
*   **Configuration**: Ortam değişkeni destekli merkezi yapılandırma yönetimi.
*   **Database**: SQLAlchemy ile asenkron veritabanı işlemleri.
*   **Cache**: Redis tabanlı önbellekleme ve pub/sub mesajlaşma.
*   **Logging**: Yapılandırılmış (structured) loglama sistemi.

### Alan Modülleri
*   **Trading**: Emir gönderimi, pozisyon yönetimi.
*   **Market Data**: Fiyat verilerinin alınması ve işlenmesi.
*   **Signals**: ICT konseptlerine dayalı sinyal üretimi.
*   **Risk**: Pozisyon boyutlandırma ve risk yönetimi.
*   **AI**: Makine öğrenmesi modelleri ile tahminleme.
*   **Account**: Kullanıcı ve hesap yönetimi.
*   **MT5 Integration**: MetaTrader 5 ile doğrudan bağlantı ve Algo Forge entegrasyonu.

## 4. MetaTrader 5 Entegrasyonu
Platform, [MetaTrader 5 platformunun 5100 versiyonuyla tam uyumludur][[memory:1905727111279718659]]. Bu versiyon, Git entegrasyonu ve MQL5 Algo Forge gibi yeni geliştici özelliklerini içermektedir.

### MQL5 Algo Forge & Git Entegrasyonu
MQL5 Algo Forge, trading algoritmalarının Git ile versiyonlanarak yönetilmesini sağlayan yeni bir özelliktir. Platform, bu özellik sayesinde algoritmaların takım olarak geliştirilmesini, test edilmesini ve dağıtılmasını kolaylaştırır.

### Entegrasyon Akış Diyagramı
```mermaid
sequenceDiagram
    participant User
    participant API as ICT Ultra API
    participant MT5Service as MT5 Integration Service
    participant MT5 as MetaTrader 5
    participant Git as MQL5 Algo Forge (Git)
    
    User->>API: Connect to MT5
    API->>MT5Service: Initialize connection
    MT5Service->>MT5: mt5.initialize()
    MT5->>MT5Service: Connection established
    MT5Service->>MT5: mt5.login(login, password, server)
    MT5->>MT5Service: Login successful
    MT5Service->>API: Connection status
    API->>User: Connection successful
    
    User->>API: Get account info
    API->>MT5Service: Request account info
    MT5Service->>MT5: mt5.account_info()
    MT5->>MT5Service: Account data
    MT5Service->>API: Formatted account info
    API->>User: Account details
    
    User->>API: Sync Algo Forge repository
    API->>MT5Service: Sync repository
    MT5Service->>Git: git clone/pull
    Git->>MT5Service: Repository data
    MT5Service->>API: Repository status
    API->>User: Sync successful
    
    User->>API: Create ICT signal
    API->>MT5Service: Execute trade based on signal
    MT5Service->>MT5: mt5.order_send()
    MT5->>MT5Service: Order result
    MT5Service->>API: Trade execution status
    API->>User: Signal executed
```

## 5. ICT Konseptleri
Sinyal modülü, aşağıdaki ICT konseptlerini içerecek şekilde geliştirilmiştir:
*   **Order Blocks**: Piyasa yapıcıların emirlerini topladığı önemli destek/direnç bölgeleri.
*   **Fair Value Gaps (FVG)**: Fiyatta oluşan ve piyasanın genellikle doldurmak için geri döndüğü boşluklar.
*   **Breaker Blocks**: Kırıldıktan sonra rol değiştiren (destek->direnç) eski destek/direnç seviyeleri.
*   **Liquidity Sweeps**: Stop-loss emirlerini temizleyerek likidite toplayan fiyat hareketleri.
*   **Market Structure**: Yükselen/alçalan trendleri ve yapı kırılımlarını (BOS) belirleyen analiz.

## 6. Kurulum ve Kullanım
Platformu yerel makinenizde çalıştırmak için aşağıdaki adımları izleyin.

### Sunucuyu Başlatma
Uygulamayı çalıştırırken `ModuleNotFoundError: No module named 'src'` hatası almanız, komutu yanlış dizinde çalıştırdığınızı gösterir. Sunucuyu başlatmak için **`backend`** dizini içinde olmanız gerekmektedir.

Doğru komutlar:
```bash
cd backend
python -m uvicorn ict_ultra.main:app --reload
```

Sunucu `http://127.0.0.1:8000` adresinde çalışmaya başlayacaktır. API dokümantasyonuna `http://127.0.0.1:8000/docs` adresinden erişebilirsiniz.

## 7. Teknik Detaylar
*   **Python Versiyonu**: 3.13.1
*   **Ana Kütüphaneler**:
    *   `fastapi`
    *   `uvicorn`
    *   `sqlalchemy`
    *   `pydantic`
    *   `redis`
    *   `MetaTrader5` (versiyon: [5.0.5120][[memory:3051932918362058828]])

## 8. Proje Durumu
Proje başarıyla tamamlanmış ve [tüm ana bileşenler implemente edilmiştir][[memory:3730752119578726901]]. Platform, MT5 demo hesabı üzerinden kullanıma hazırdır. Mevcut dökümantasyon, projenin mimarisini ve kullanımını detaylı bir şekilde açıklamaktadır. 