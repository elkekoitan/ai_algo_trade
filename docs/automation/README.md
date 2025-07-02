# 📚 AI Algo Trade - Documentation Automation System

Bu klasör, AI Algo Trade projesi için gelişmiş dokümantasyon senkronizasyon ve analiz sistemini içerir. Büyük geliştirmeler sonrası otomatik olarak çalıştırılarak proje dokümantasyonunu güncel tutar.

## 🎯 Sistem Özellikleri

### 🚀 Ana Bileşenler

1. **Enhanced Doc Sync** - Gelişmiş dokümantasyon senkronizasyonu
2. **Master Doc Sync** - Ana koordinatör sistem
3. **Health Scanner** - Dokümantasyon sağlık kontrolü
4. **Inventory System** - Dokümantasyon envanteri
5. **Cross-Reference Analyzer** - Kod-dokümantasyon çapraz referans analizi

### 🔄 Otomatik İşlemler

- ✅ API endpoint'lerini otomatik dokümante eder
- ✅ Frontend component'leri analiz eder
- ✅ Dokümantasyon sağlık kontrolü yapar
- ✅ Broken link'leri tespit eder
- ✅ Kod-dokümantasyon uyumunu kontrol eder
- ✅ Detaylı raporlar oluşturur
- ✅ Git entegrasyonu (opsiyonel)

## 🚀 Hızlı Başlangıç

### Büyük Geliştirme Sonrası Kullanım

```bash
# Ana dizine git
cd /path/to/ai_algo_trade

# Master analizi çalıştır (ÖNERİLEN)
node docs/automation/master-doc-sync.js major

# Veya sadece hızlı kontrol
node docs/automation/master-doc-sync.js quick
```

### Manuel Araçlar

```bash
# Dokümantasyon sağlık kontrolü
node docs/automation/doc-health-scanner.js

# Dokümantasyon envanteri
python docs/automation/documentation_inventory.py

# Detaylı kod analizi
python docs/automation/detailed-doc-analysis.py

# Gelişmiş sync
node docs/automation/enhanced-doc-sync.js sync
```

## 📋 Dosya Yapısı

```
docs/automation/
├── README.md                          # Bu dosya
├── master-doc-sync.js                 # Ana koordinatör sistem ⭐
├── enhanced-doc-sync.js               # Gelişmiş senkronizasyon
├── doc-health-scanner.js              # Sağlık kontrolü
├── documentation_inventory.py         # Envanter sistemi
├── detailed-doc-analysis.py           # Detaylı analiz
├── doc-sync-config.json              # Konfigürasyon
├── doc-sync-state.json               # Durum takibi
├── reports/                           # Otomatik raporlar
│   ├── analysis_*.md                  # Major update raporları
│   └── health_*.csv                   # Sağlık kontrol sonuçları
└── templates/                         # Dokümantasyon şablonları
    ├── api-template.md
    ├── component-template.md
    └── module-template.md
```

## ⚙️ Konfigürasyon

### `doc-sync-config.json`

```json
{
  "watchDirs": [
    "src", "components", "modules", 
    "backend", "frontend", "api"
  ],
  "watchExtensions": [
    ".js", ".ts", ".jsx", ".tsx", ".py"
  ],
  "autoGenRules": {
    "api": {
      "enabled": true,
      "patterns": ["**/api/**/*.js", "**/api/**/*.py"],
      "output": "docs/API_REFERENCE.md"
    },
    "components": {
      "enabled": true,
      "patterns": ["**/components/**/*.tsx"],
      "output": "docs/COMPONENTS_REFERENCE.md"
    }
  },
  "gitIntegration": {
    "enabled": true,
    "autoCommit": true,
    "autoPush": false
  }
}
```

## 🎯 Kullanım Senaryoları

### 1. 🚨 Büyük Geliştirme Sonrası (ÖNERİLEN)

Yeni modül eklediğinizde, API değişiklikleri yaptığınızda veya büyük refactor sonrası:

```bash
node docs/automation/master-doc-sync.js major
```

**Bu komut:**
- Tüm API endpoint'lerini analiz eder
- Component'leri sayar ve kategorize eder
- Dokümantasyon sağlık kontrolü yapar
- Cross-reference analizi yapar
- Detaylı rapor oluşturur
- API_REFERENCE.md'yi günceller

### 2. ⚡ Hızlı Kontrol

Küçük değişiklikler sonrası hızlı kontrol için:

```bash
node docs/automation/master-doc-sync.js quick
```

### 3. 🏥 Sadece Sağlık Kontrolü

Dokümantasyon kalitesini kontrol etmek için:

```bash
node docs/automation/doc-health-scanner.js
```

### 4. 📊 Envanter Çıkarma

Proje dokümantasyonunun kapsamlı envanteri için:

```bash
python docs/automation/documentation_inventory.py
```

## 📊 Çıktılar ve Raporlar

### Ana Raporlar

- **`reports/analysis_*_major_update.md`** - Kapsamlı analiz raporları
- **`docs/API_REFERENCE.md`** - Otomatik API dokümantasyonu
- **`docs/COMPONENTS_REFERENCE.md`** - Component referansı
- **`doc-health-raw.csv`** - Sağlık kontrol detayları
- **`documentation_index.json`** - Dokümantasyon envanteri

### Örnek Rapor İçeriği

```markdown
# 🚀 AI Algo Trade - Major Update Analiz Raporu

**Analiz ID:** analysis_1704123456789
**Tarih:** 2024-01-01T12:00:00.000Z

## 🔗 API Analizi
- **Toplam Endpoint:** 45
- **API Dosyası:** 12
- **Modüller:** trading, god_mode, shadow_mode, adaptive_trade_manager

## 🏥 Dokümantasyon Sağlığı
- **Toplam Sorun:** 8
- **Kritik:** 2 broken links
- **Uyarı:** 6 style issues

## 🎨 Frontend Analizi
- **Toplam Component:** 67
- **Toplam Sayfa:** 15
```

## 🔧 Gelişmiş Özellikler

### 1. Otomatik Git Entegrasyonu

```json
{
  "gitIntegration": {
    "enabled": true,
    "autoCommit": true,
    "commitMessage": "docs: otomatik dokümantasyon güncellemesi",
    "autoPush": false
  }
}
```

### 2. Major Update Tespiti

Sistem şu durumlarda "major update" olarak algılar:
- 15+ dosya değişikliği
- Yeni modül eklenmesi
- API endpoint'lerinde büyük değişiklik
- Mimari değişiklikler

### 3. Sağlık Kontrol Kriterleri

- **Broken Links**: Kırık iç/dış linkler
- **Missing Images**: Eksik resim dosyaları
- **Style Issues**: Markdown stil sorunları
- **Heading Hierarchy**: Başlık hiyerarşi problemleri
- **Missing Alt Text**: Eksik alt text'ler

## 🎮 NPM Scripts Entegrasyonu

`package.json`'a ekleyin:

```json
{
  "scripts": {
    "doc:major": "node docs/automation/master-doc-sync.js major",
    "doc:quick": "node docs/automation/master-doc-sync.js quick",
    "doc:health": "node docs/automation/doc-health-scanner.js",
    "doc:inventory": "python docs/automation/documentation_inventory.py"
  }
}
```

## 🔄 Sürekli Entegrasyon

### GitHub Actions (.github/workflows/docs.yml)

```yaml
name: Documentation Sync
on:
  push:
    branches: [main]
    paths: ['backend/**', 'frontend/**']

jobs:
  docs:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-node@v3
      - uses: actions/setup-python@v3
      
      - name: Run Documentation Analysis
        run: |
          npm install
          node docs/automation/master-doc-sync.js major
      
      - name: Commit Documentation Updates
        run: |
          git config --local user.email "action@github.com"
          git config --local user.name "Documentation Bot"
          git add docs/
          git diff --staged --quiet || git commit -m "docs: otomatik güncelleme"
          git push
```

## 📈 İstatistikler ve Metrikler

Sistem şu metrikleri takip eder:

- **API Coverage**: Kaç endpoint dokümante edildi
- **Component Coverage**: Kaç component analiz edildi
- **Health Score**: Dokümantasyon sağlık skoru
- **Cross-Reference Accuracy**: Kod-dokümantasyon uyum yüzdesi
- **Update Frequency**: Güncelleme sıklığı

## 🛠️ Troubleshooting

### Sık Karşılaşılan Sorunlar

#### 1. Python Script Çalışmıyor
```bash
# Python yolu kontrol et
python --version
# veya
python3 --version

# Gerekli kütüphaneler
pip install pandas openpyxl
```

#### 2. Node.js Bağımlılıkları
```bash
# Automation dizininde
npm install chokidar
```

#### 3. Permission Hataları
```bash
# Script'leri executable yap
chmod +x docs/automation/*.js
chmod +x docs/automation/*.py
```

## 💡 En İyi Pratikler

### 1. Büyük Geliştirmeler Sonrası

- ✅ Her zaman `master-doc-sync.js major` çalıştır
- ✅ Raporu incele ve önerileri uygula
- ✅ Broken link'leri düzelt
- ✅ API dokümantasyonunu kontrol et

### 2. Düzenli Bakım

- 🔄 Haftada bir sağlık kontrolü yap
- 🔄 Ayda bir envanter çıkar
- 🔄 Eski raporları temizle

### 3. Geliştirme Süreci

- 📝 Kod yazarken JSDoc yorumları ekle
- 📝 API endpoint'lerine docstring ekle
- 📝 Component'lerde prop dokümantasyonu yap

## 🎯 Özet

Bu otomasyon sistemi AI Algo Trade projesi için:

1. **Manual çalıştırılmalı**: Büyük geliştirmeler sonrası
2. **Kapsamlı analiz**: Kod-dokümantasyon uyumu
3. **Otomatik güncelleme**: API ve component referansları
4. **Kalite kontrol**: Sağlık kontrolleri ve raporlar
5. **Git entegrasyonu**: Otomatik commit (opsiyonel)

**Ana komut:** `node docs/automation/master-doc-sync.js major`

Bu sistemi büyük geliştirmeler sonrası çalıştırarak dokümantasyonunuzun her zaman güncel ve kaliteli olmasını sağlayabilirsiniz.

---

*Bu sistem AI Algo Trade projesi için özel olarak geliştirilmiştir.* 