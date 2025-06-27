# 🏗️ Genel Sistem Mimarisi

Bu diyagram, AI Algo Trade platformunun tüm ana bileşenlerini ve aralarındaki ilişkileri göstermektedir.

## Mermaid Diagram

```mermaid
graph TD
    subgraph "System Architecture"
        A[Frontend: Next.js] --> B[Backend: FastAPI]
        B --> C{Event Bus}
        B --> D[Database: PostgreSQL]
        C --> E[MT5 Integration]
        C --> F[ICT Analysis Engine]
        C --> G[God Mode]
        C --> H[Shadow Mode]
        E --> I[MetaTrader 5]
        F --> D
        G --> D
        H --> D
    end

    style A fill:#000000,stroke:#61DAFB,stroke-width:2px,color:#fff
    style B fill:#000000,stroke:#009688,stroke-width:2px,color:#fff
    style I fill:#0A3B53,stroke:#fff,stroke-width:2px,color:#fff
    style G fill:#D4AF37,stroke:#fff,stroke-width:2px,color:#000
    style H fill:#FF6B35,stroke:#fff,stroke-width:2px,color:#000
```

## Bileşenler

-   **Frontend (Next.js):** Kullanıcı arayüzü, quantum dashboard'lar ve interaktif bileşenler.
-   **Backend (FastAPI):** Ana iş mantığı, API endpoint'leri ve servis yönetimi.
-   **Event Bus:** Bileşenler arası asenkron iletişimi sağlayan olay tabanlı sistem.
-   **Database (PostgreSQL):** Alım-satım geçmişi, performans metrikleri ve kullanıcı verilerinin saklandığı veritabanı.
-   **MT5 Integration:** MetaTrader 5 ile gerçek zamanlı veri alışverişi ve emir yönetimi.
-   **ICT Analysis Engine:** Inner Circle Trader konseptlerine dayalı piyasa analizi motoru.
-   **God Mode:** Piyasaya yön veren, tahmine dayalı alım-satım motoru.
-   **Shadow Mode:** Kurumsal oyuncuları takip eden gizli mod.
-   **MetaTrader 5:** Canlı piyasa verilerinin ve alım-satım altyapısının sağlandığı platform.

Bu yapı, sistemin modüler, ölçeklenebilir ve yüksek performanslı olmasını sağlar. 