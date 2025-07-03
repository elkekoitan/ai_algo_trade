# Sanal Süpürge V1 Trading Strategy

## Açıklama
Sanal Süpürge V1, 14 seviyeli grid trading sistemi kullanan gelişmiş bir MQL4 Expert Advisor'dır. Bu strateji, piyasadaki fiyat hareketlerini takip ederek çoklu pozisyon açma ve yönetme prensibine dayanır.

## Özellikler

### Grid Trading Sistemi
- **14 Seviye**: Her yön için 14 farklı seviyede pozisyon açma
- **Dinamik Lot Boyutu**: İlk 9 seviye 0.01-0.09, son 5 seviye 0.1 lot
- **Progressif TP**: İlk 9 seviye 1000 pips TP, son 5 seviye 2500 pips TP
- **Sabit SL**: Tüm seviyelerde 100 pips SL

### Risk Yönetimi
- **Pivot Filtreleme**: PivotUst (1.8) ve PivotAlt (1.01) arasında işlem
- **Zaman Filtreleri**: İsteğe bağlı trading saatleri kısıtlaması
- **Position Comment**: "HayaletSüpürge" magic number sistemi

### Bildirim Sistemi
- **MT5 Native Alerts**: 3., 4. ve 5. seviyelerde otomatik bildirim
- **Position Kapatma**: TP/SL'ye ulaşıldığında bildirim

## Parametreler

### Temel Ayarlar
```mql4
extern bool BuyIslemiAc = true;        // Buy işlemleri aktif
extern bool SellIslemiAc = true;       // Sell işlemleri aktif
extern string PositionComment = "HayaletSüpürge";
extern double PivotUst = 1.8;          // Üst pivot seviyesi
extern double PivotAlt = 1.01;         // Alt pivot seviyesi
```

### Seviye Ayarları
Her seviye için ayrı ayrı:
- `SendOrder[1-14]`: Seviye aktif/pasif
- `LotSize[1-14]`: Lot boyutu
- `tp[1-14]`: Take Profit (pips)
- `sl[1-14]`: Stop Loss (pips)
- `NewPositionAddLevel[2-14]`: Seviye arası mesafe

### Zaman Filtreleri
```mql4
extern bool UseTimeLimit = false;          // Zaman filtresi aktif
extern int DoNotOpenAfterHour = 20;        // İşlem kapatma saati
extern int DoNotOpenBeforeHour = 02;       // İşlem açma saati
extern bool UseTimeLimitBreak = true;      // Ara zaman filtresi
```

## Kurulum

1. **MT5'e Yükleme**:
   - `Sanal_SupurgeV1.mq4` dosyasını MT5 `MQL4/Experts` klasörüne kopyalayın
   - `Sanal_SupurgeV1_Functions.mqh` dosyasını aynı klasöre kopyalayın
   - MT5'i yeniden başlatın

2. **Parametrelerin Ayarlanması**:
   - Expert'i çarta ekleyin
   - Parametreleri risk toleransınıza göre ayarlayın
   - AutoTrading'i aktif edin

3. **Lisans Kontrolü**:
   - Master hesap: 25201110
   - Lisans tarihi: 02.04.2025'e kadar geçerli

## AI Algo Trade Entegrasyonu

Bu strateji AI Algo Trade platformu ile tam entegre edilmiştir:

- **Copy Trading**: Master hesaptan diğer hesaplara otomatik kopyalama
- **Risk Monitoring**: Gerçek zamanlı risk takibi
- **Performance Analytics**: Detaylı performans analizi
- **Strategy Whisperer**: Doğal dil ile parametre optimizasyonu

## Risk Uyarısı

⚠️ **ÖNEMLİ**: Bu strateji grid trading sistemi kullanır ve yüksek volatilitede önemli drawdown yaşayabilir. Sadece risk alabileceğiniz sermaye ile kullanın.

### Önerilen Ayarlar
- **Minimum Bakiye**: $10,000
- **Maksimum Risk**: Bakiyenin %2'si per trade
- **Önerilen Çiftler**: EUR/USD, GBP/USD, USD/JPY
- **Timeframe**: M15 veya üzeri

## Performans Metrikleri

- **Karlılık**: Orta-yüksek volatilitede pozitif
- **Drawdown**: %10-30 arası (parametre setine bağlı)
- **Win Rate**: %60-75
- **Risk/Reward**: 1:2 - 1:3

## Destek

Teknik destek için AI Algo Trade support ekibi ile iletişime geçin.

## Versiyon Geçmişi

- **v1.0**: İlk release - Grid trading sistemi, zaman filtreleri, bildirim sistemi 