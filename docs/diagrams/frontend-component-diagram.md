# ⚛️ Frontend Component Architecture

Bu diyagram, Next.js ile geliştirilen frontend uygulamasının ana bileşenlerini ve sayfalar arası ilişkilerini göstermektedir.

## Mermaid Diagram

```mermaid
graph TD
    subgraph "⚛️ Frontend Component Architecture"
        
        QL[QuantumLayout]
        
        subgraph "Pages"
            HP[HomePage]
            TP[TradingPage]
            GP[GodModePage]
            SP[ShadowModePage]
        end
        
        subgraph "Core Components"
            QH[QuantumHeader]
            AC[AccountInfo]
            QT[QuickTrade]
            TVC[TradingViewChart]
        end
        
        subgraph "God Mode Components"
            GMC[GodModeControl]
            PP[PredictionsPanel]
        end

        subgraph "Shadow Mode Components"
            SMC[ShadowControlPanel]
            IR[InstitutionalRadar]
            WT[WhaleTracker]
            DPM[DarkPoolMonitor]
        end

        QL --> HP & TP & GP & SP
        QL --> QH
        
        HP --> AC & QT & TVC
        TP --> TVC & QT & AC

        GP --> GMC & PP
        SP --> SMC & IR & WT & DPM

        QH --> QL
    end

    style QL fill:#000000,stroke:#61DAFB,stroke-width:2px,color:#fff
    style HP fill:#1a1a1a,stroke:#61DAFB,stroke-width:1px,color:#fff
    style TP fill:#1a1a1a,stroke:#61DAFB,stroke-width:1px,color:#fff
    style GP fill:#1a1a1a,stroke:#D4AF37,stroke-width:1px,color:#fff
    style SP fill:#1a1a1a,stroke:#FF6B35,stroke-width:1px,color:#fff
```

## Bileşen Açıklamaları

-   **QuantumLayout:** Tüm sayfaları saran ana layout bileşeni. `QuantumHeader`'ı içerir.
-   **Pages:** Uygulamanın ana sayfaları (`HomePage`, `TradingPage`, `GodModePage`, `ShadowModePage`).
-   **Core Components:** Uygulama genelinde kullanılan temel bileşenler (`AccountInfo`, `QuickTrade`, `TradingViewChart`).
-   **God Mode / Shadow Mode Components:** İlgili modüllere özel, modüler olarak geliştirilmiş bileşen grupları.

Bu yapı, sayfalar ve bileşenler arasında net bir hiyerarşi ve yeniden kullanılabilirlik sağlar. 