# 🔄 Veri Akış Diyagramı

Bu diyagram, kullanıcı tarafından başlatılan bir alım-satım işleminden, arka planda çalışan periyodik analizlere kadar sistemdeki ana veri akış yollarını göstermektedir.

## Mermaid Sequence Diagram

```mermaid
sequenceDiagram
    participant User as 👤 Kullanıcı
    participant FE as ⚛️ Frontend UI (Next.js)
    participant BE as ⚙️ Backend API (FastAPI)
    participant MT5 as 📈 MT5 Entegrasyonu
    participant ICT as 🧠 ICT Analiz Motoru
    participant DB as 🗄️ Veritabanı
    participant MetaTrader as 🏦 MetaTrader 5

    User->>FE: Emir Gönderir (Trade)
    FE->>BE: /trading/place_order isteği
    BE->>MT5: Emri İlet (place_order)
    MT5->>MetaTrader: Emri Gerçekleştir
    MetaTrader-->>MT5: Emir Sonucu
    MT5-->>BE: Sonuç Başarılı
    BE-->>FE: Emir Başarılı Yanıtı
    FE-->>User: Emir Başarılı Bildirimi

    loop Her Saniye
        MT5->>MetaTrader: Canlı Fiyat/Pozisyon Verisi İste
        MetaTrader-->>MT5: Veriyi Gönder
        MT5->>BE: Veriyi Event Bus'a Yayınla
        BE-->>FE: WebSocket ile Canlı Veriyi İlet
        FE-->>User: Dashboard'u Güncelle
    end
    
    loop Periyodik Analiz
        BE->>ICT: Yeni Mum Verisiyle Analiz Başlat
        ICT->>MT5: Tarihsel Veri İste
        MT5-->>ICT: Veriyi Gönder
        ICT->>DB: Analiz Sonuçlarını (Order Block, FVG) Kaydet
        DB-->>ICT: Kayıt Başarılı
    end
```

## Akış Senaryoları

### 1. Kullanıcı Alım-Satım İşlemi
1.  **Kullanıcı**, Frontend arayüzünden bir emir girer.
2.  **Frontend**, bu isteği Backend API'sine (`/api/v1/trading/place_order`) iletir.
3.  **Backend**, `MT5 Entegrasyon` servisi aracılığıyla emri MetaTrader 5'e gönderir.
4.  **MetaTrader 5**, emri işleme alır ve sonucunu döner.
5.  Sonuç, aynı yol üzerinden kullanıcıya bildirim olarak geri döner.

### 2. Canlı Veri Akışı (Real-time)
1.  `MT5 Entegrasyon` servisi, saniyede bir MetaTrader 5'ten güncel fiyatları ve açık pozisyonları çeker.
2.  Bu veriler, Backend'deki **Event Bus**'a yayınlanır.
3.  Frontend, **WebSocket** bağlantısı üzerinden bu verileri anında alır.
4.  Kullanıcının gördüğü **Dashboard** (örn. Bakiye, Kar/Zarar, Fiyat Grafikleri) gerçek zamanlı olarak güncellenir.

### 3. Otomatik Piyasa Analizi
1.  **Backend**, belirli periyotlarda (örn. her yeni H1 mumu oluştuğunda) `ICT Analiz Motoru`'nu tetikler.
2.  `ICT Analiz Motoru`, gerekli tarihsel verileri `MT5 Entegrasyonu` üzerinden çeker.
3.  Analizini (Fair Value Gap, Order Block tespiti vb.) yapar.
4.  Tespit edilen önemli yapıları ve sinyalleri ileriye dönük kullanım için **Veritabanına** kaydeder. 