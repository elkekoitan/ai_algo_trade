# 🐋 Whale Detection Process

Büyük oyuncu (whale) tespit sürecinin detaylı akış diyagramı.

## Process Flow

```mermaid
graph LR
    subgraph "🐋 WHALE DETECTION PROCESS"
        
        START([Market Data Input]) --> FILTER[Volume Filter]
        FILTER --> SIZE{Position Size > Threshold?}
        
        SIZE -->|Yes| ANALYZE[Behavioral Analysis]
        SIZE -->|No| IGNORE[Ignore Small Trades]
        
        ANALYZE --> PATTERN[Pattern Recognition]
        PATTERN --> STEALTH[Stealth Score Calculation]
        
        STEALTH --> CONFIDENCE[Confidence Assessment]
        CONFIDENCE --> CLASSIFY[Whale Classification]
        
        CLASSIFY --> SMALL[Small Whale<br/>100K-1M]
        CLASSIFY --> MEDIUM[Medium Whale<br/>1M-10M]
        CLASSIFY --> LARGE[Large Whale<br/>10M-100M]
        CLASSIFY --> MASSIVE[Massive Whale<br/>100M+]
        
        SMALL --> ALERT[Generate Alert]
        MEDIUM --> ALERT
        LARGE --> ALERT
        MASSIVE --> ALERT
        
        ALERT --> TRACK[Add to Tracking]
        TRACK --> STRATEGY[Generate Shadow Strategy]
        
        STRATEGY --> END([Shadow Execution])
    end
    
    style START fill:#50C878,stroke:#fff,stroke-width:2px
    style MASSIVE fill:#FF4444,stroke:#fff,stroke-width:2px,color:#fff
    style END fill:#FF6B35,stroke:#fff,stroke-width:2px,color:#fff
```

## Süreç Adımları

### 1. Market Data Input
- Gerçek zamanlı piyasa verisi alımı
- Volume ve price action analizi
- Order book derinlik verisi

### 2. Volume Filter
- Minimum volume threshold kontrolü
- Anormal volume spike tespiti
- Statistical deviation analizi

### 3. Position Size Analysis
- Pozisyon büyüklüğü hesaplama
- Threshold karşılaştırması
- Risk assessment

### 4. Behavioral Analysis
- Trading pattern analizi
- Execution style profiling
- Historical behavior matching

### 5. Whale Classification
- **Small Whale**: 100K - 1M
- **Medium Whale**: 1M - 10M  
- **Large Whale**: 10M - 100M
- **Massive Whale**: 100M+

### 6. Shadow Strategy Generation
- Pattern-based strategy creation
- Risk-adjusted position sizing
- Timing optimization 