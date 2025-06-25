# ICT Ultra v2: Algo Forge Edition - Geliştirme Yol Haritası

## Proje Vizyonu

Bu proje, ICT Ultra Platformu'nun başarısını temel alarak, MetaTrader 5'in devrim niteliğindeki yeni **MQL5 Algo Forge** ve **Git entegrasyonu** yeteneklerini tam merkezine alan, yeni nesil bir algoritmik trading platformu oluşturmayı hedefler. Platform, kurumsal düzeyde stabilite, profesyonel analiz araçları ve geliştirici dostu bir ekosistem sunacaktır.

---

### **Phase 0: Proje Temeli ve Kurulum (Süre: 1 Gün)**

*   **Amaç:** Proje için sağlam ve temiz bir temel oluşturmak.
*   **Görevler:**
    *   [x] **Arşivleme:** Mevcut tüm proje dosyalarının temizlenmesi.
    *   [x] **Yeni Proje Yapısı:** `backend`, `frontend`, `docs`, `mql5_forge_repos` ana klasörlerinin oluşturulması.
    *   [ ] **Versiyon Kontrolü:** Proje için `git init` ile Git deposunun başlatılması.
    *   [x] **Temel Dokümantasyon:** Bu `ROADMAP.md` dosyasının oluşturulması.

### **Phase 1: Çekirdek Mimari ve MQL5 Algo Forge Entegrasyonu (Süre: 1 Hafta)**

*   **Amaç:** Platformun bel kemiğini oluşturmak ve tam Git entegrasyonunu hayata geçirmek.
*   **Görevler:**
    1.  **Çekirdek Modüller:** `Config`, `Logging`, `Database`, `Cache`, `Events` gibi çekirdek servislerin `backend` içinde `Clean Architecture` prensipleriyle oluşturulması.
    2.  **Yeni Nesil MT5 Entegrasyon Modülü:**
        *   MT5 platformuna temel bağlantının sağlanması (Login: `25201110`).
        *   MQL5 Algo Forge Git depolarını listeleyen, klonlayan ve senkronize eden servislerin geliştirilmesi.
        *   Platform arayüzünden Algo Forge repolarına `commit` ve `push` yapma yeteneğinin altyapısını hazırlama.

### **Phase 2: Veri Akışı ve Akıllı Sinyal Motoru (Süre: 1 Hafta)**

*   **Amaç:** Platformu canlı piyasa verileriyle beslemek ve ICT tabanlı alım-satım sinyalleri üretmek.
*   **Görevler:**
    1.  **Market Data Modülü:** MT5'ten canlı tick ve bar verilerini çeken ve Redis üzerinden yayınlayan servisin oluşturulması.
    2.  **ICT Sinyal Modülü:** Eski projeden alınan `Order Blocks`, `FVG` gibi kanıtlanmış ICT algoritmalarının yeni ve optimize edilmiş şekilde `backend`'e entegrasyonu.
    3.  **Gelişmiş Sinyal Skorlama:** Trend gücü, hacim, likidite gibi çoklu faktörlere dayalı sinyal skorlama motorunun implementasyonu.

### **Phase 3: Profesyonel Arayüz (UI/UX) - Trader'ın Komuta Merkezi (Süre: 2 Hafta)**

*   **Amaç:** Modern, hızlı ve kullanışlı bir kullanıcı arayüzü oluşturmak.
*   **Görevler:**
    1.  **Frontend Altyapısı:** `frontend` klasörü içinde Next.js, TailwindCSS ve TypeScript projesinin kurulması.
    2.  **Ana Dashboard:** Canlı hesap bilgilerini, P/L durumunu ve temel metrikleri gösteren ana ekranın tasarlanması.
    3.  **MQL5 Algo Forge Yönetim Paneli:** Kullanıcıların Git repolarını, dallarını ve `commit` geçmişini yönetebileceği bir arayüz.
    4.  **Gelişmiş Grafikler:** TradingView Lightweight Charts ile profesyonel bir grafik component'i.

### **Phase 4: Otomatik Trading ve Gelişmiş Risk Yönetimi (Süre: 1 Hafta)**

*   **Amaç:** Platforma otomatik işlem ve kurumsal seviye risk kontrolü yetenekleri kazandırmak.
*   **Görevler:**
    1.  **Trading Modülü:** Tek tıkla işlem, pozisyon yönetimi ve emir iletim altyapısı.
    2.  **ContinuousAutoTrader:** Ayarlanabilir skor eşiği ve dinamik lot büyüklüğü ile sürekli çalışan otomatik alım-satım sisteminin geliştirilmesi.
    3.  **Advanced Risk Manager:** Portföy bazlı risk hesaplama (VaR) ve pozisyon risk analizi modülü.

### **Phase 5: Yapay Zeka ve Makine Öğrenmesi Entegrasyonu (Süre: 1-2 Hafta)**

*   **Amaç:** Platforma tahminsel ve akıllı karar destek mekanizmaları eklemek.
*   **Görevler:**
    1.  **Real-Time ML Predictor:** TensorFlow.js ile canlı fiyat tahminleri yapan bir LSTM modelinin frontend'e entegrasyonu.
    2.  **AI Strateji Yöneticisi:** Birden fazla AI/ML modelini yönetme ve performanslarını izleme imkanı.

### **Phase 6: Profesyonel Araçlar ve Platform Stabilitesi (Süre: 1 Hafta)**

*   **Amaç:** Platformu endüstri standardı araçlarla donatmak ve uzun süreli çalışmalarda stabilitesini garantilemek.
*   **Görevler:**
    1.  **Profesyonel Analiz Araçları:** `VolumeFootprintChart`, `MultiTimeframeAnalysis`, `RiskRewardCalculator` gibi gelişmiş analiz araçlarının entegrasyonu.
    2.  **Anlık Bildirim Sistemi:** Filtrelenebilir, kategorize edilmiş (Sinyal, Risk, Sistem) anlık bildirimler.
    3.  **Robust Startup Sistemi:** Platformun tüm servislerini (backend, frontend, proxy) doğru sırada ve hatasız başlatan, sağlık kontrolü yapan script'lerin oluşturulması. 