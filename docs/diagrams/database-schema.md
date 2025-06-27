# 🗄️ Veritabanı Şeması

Bu diyagram, AI Algo Trade platformunun PostgreSQL veritabanında kullanılan ana tablaları ve aralarındaki ilişkileri göstermektedir.

## Mermaid ERD Diagram

```mermaid
graph TD
    subgraph "🗄️ Database Schema"
        Users(👤 Users)
        Accounts(💳 Accounts)
        Trades(📈 Trades)
        Positions(📊 Positions)
        Signals(💡 Signals)
        Performance(📉 PerformanceMetrics)

        Users -- "1..*" --> Accounts
        Accounts -- "1..*" --> Trades
        Accounts -- "1..*" --> Positions
        Accounts -- "1..*" --> Performance
        Signals -- "Analyzes" --> Trades

        subgraph "Users Table"
            U_ID[id PK]
            U_Email[email]
            U_Pass[password_hash]
            U_Created[created_at]
        end

        subgraph "Accounts Table"
            A_ID[id PK]
            A_UserID[user_id FK]
            A_MT5ID[mt5_login]
            A_Server[server]
            A_Balance[balance]
        end

        subgraph "Trades Table"
            T_ID[id PK]
            T_AccID[account_id FK]
            T_Ticket[ticket]
            T_Symbol[symbol]
            T_Volume[volume]
            T_Open[open_price]
            T_Close[close_price]
            T_Profit[profit]
        end
        
        Users --> U_ID & U_Email & U_Pass & U_Created
        Accounts --> A_ID & A_UserID & A_MT5ID & A_Server & A_Balance
        Trades --> T_ID & T_AccID & T_Ticket & T_Symbol & T_Volume & T_Open & T_Close & T_Profit
    end
    
    style Users fill:#2C2C2C,stroke:#009688,stroke-width:2px,color:#fff
    style Accounts fill:#2C2C2C,stroke:#009688,stroke-width:2px,color:#fff
    style Trades fill:#2C2C2C,stroke:#009688,stroke-width:2px,color:#fff
```

## Tablo Açıklamaları

-   **Users:** Platforma kayıtlı kullanıcıların temel bilgilerini tutar.
-   **Accounts:** Her kullanıcının bir veya daha fazla MetaTrader 5 hesabını temsil eder. Bakiye gibi anlık bilgiler burada saklanabilir.
-   **Trades:** Gerçekleşmiş (kapanmış) alım-satım işlemlerinin kaydını tutar. Performans analizi için temel veridir.
-   **Positions:** Mevcutta açık olan pozisyonların anlık durumunu gösterir.
-   **Signals:** ICT, God Mode veya Shadow Mode tarafından üretilen alım-satım sinyallerini kaydeder.
-   **PerformanceMetrics:** Hesap bazında hesaplanan performans metriklerini (Sharpe oranı, Maks. Drawdown vb.) periyodik olarak saklar.

## İlişkiler

-   Bir **Kullanıcı** birden çok **Hesap** sahibi olabilir.
-   Bir **Hesap** üzerinden birden çok **İşlem** ve **Pozisyon** açılabilir.
-   **Sinyaller**, analiz sonucu olarak **İşlemlerin** açılmasına neden olabilir.

Bu yapı, kullanıcı ve hesap bazında detaylı performans takibi ve raporlama yapılmasına olanak tanır. 