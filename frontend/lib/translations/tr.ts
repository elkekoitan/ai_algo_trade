/**
 * Turkish translations for ICT Ultra v2
 */

const translations = {
  // Common
  common: {
    loading: 'Yükleniyor...',
    error: 'Hata',
    success: 'Başarılı',
    retry: 'Tekrar Dene',
    save: 'Kaydet',
    cancel: 'İptal',
    close: 'Kapat',
    confirm: 'Onayla',
    yes: 'Evet',
    no: 'Hayır',
    back: 'Geri',
    next: 'İleri',
    submit: 'Gönder',
  },

  // Navigation
  navigation: {
    dashboard: 'Kontrol Paneli',
    trading: 'İşlem Terminali',
    signals: 'ICT Sinyalleri',
    performance: 'Performans',
    quantum: 'Quantum Paneli',
    settings: 'Ayarlar',
    logout: 'Çıkış',
  },

  // Dashboard
  dashboard: {
    title: 'İşlem Kontrol Paneli',
    subtitle: 'Gerçek zamanlı piyasa analizi ve işlem',
    quickAccess: 'Hızlı Erişim',
    marketSymbols: 'Piyasa Sembolleri',
    marketChart: 'Piyasa Grafiği',
  },

  // Account
  account: {
    overview: 'Hesap Genel Bakış',
    balance: 'Bakiye',
    equity: 'Özsermaye',
    margin: 'Marjin',
    freeMargin: 'Serbest Marjin',
    marginLevel: 'Marjin Seviyesi',
    profit: 'Kar/Zarar',
    leverage: 'Kaldıraç',
    accountInfo: 'Hesap Bilgisi',
    server: 'Sunucu',
  },

  // Trading
  trading: {
    buy: 'AL',
    sell: 'SAT',
    volume: 'Hacim (Lot)',
    entry: 'Giriş',
    stopLoss: 'Zarar Kes',
    takeProfit: 'Kar Al',
    orderType: 'Emir Türü',
    market: 'Piyasa',
    limit: 'Limit',
    stop: 'Stop',
    pending: 'Bekleyen',
    positions: 'Pozisyonlar',
    orders: 'Emirler',
    history: 'Geçmiş',
    symbol: 'Sembol',
    timeframe: 'Zaman Dilimi',
    price: 'Fiyat',
    openTime: 'Açılış Zamanı',
    closeTime: 'Kapanış Zamanı',
    profit: 'Kar',
    loss: 'Zarar',
    comment: 'Yorum',
  },

  // Signals
  signals: {
    orderBlock: 'Emir Bloğu',
    fairValueGap: 'Adil Değer Boşluğu',
    breakerBlock: 'Kırıcı Blok',
    bullish: 'Yükseliş',
    bearish: 'Düşüş',
    strength: 'Güç',
    confidence: 'Güven',
    status: 'Durum',
    active: 'Aktif',
    expired: 'Süresi Dolmuş',
    confirmed: 'Onaylanmış',
  },

  // Scanner
  scanner: {
    title: 'Piyasa Tarayıcı',
    scanning: 'Taranıyor',
    paused: 'Duraklatıldı',
    filters: 'Filtreler',
    scan: 'Tara',
    lastScan: 'Son Tarama',
    nextScan: 'Sonraki Tarama',
    opportunities: 'İşlem Fırsatları',
    found: 'bulundu',
    symbols: 'Semboller',
    timeframes: 'Zaman Dilimleri',
    minStrength: 'Min. Güç',
    minConfidence: 'Min. Güven',
    minRiskReward: 'Min. Risk/Ödül',
    noOpportunities: 'İşlem Fırsatı Bulunamadı',
    tryAdjusting: 'Filtrelerinizi ayarlamayı deneyin veya yeni piyasa koşullarını bekleyin.',
  },

  // Auto Trader
  autoTrader: {
    title: 'Otomatik İşlem Kontrolü',
    status: 'Durum',
    active: 'Aktif',
    inactive: 'Pasif',
    start: 'Başlat',
    stop: 'Durdur',
    settings: 'Ayarlar',
    strategies: 'Stratejiler',
    riskManagement: 'Risk Yönetimi',
    maxRisk: 'Maksimum Risk',
    maxPositions: 'Maksimum Pozisyon',
    maxDrawdown: 'Maksimum Drawdown',
  },

  // Contact
  contact: {
    title: 'İletişim',
    name: 'İsim',
    email: 'E-posta',
    message: 'Mesaj',
    send: 'Gönder',
    success: 'Mesajınız başarıyla gönderildi. En kısa sürede size dönüş yapacağız.',
    error: 'Mesajınız gönderilemedi. Lütfen daha sonra tekrar deneyin.',
  },

  // Errors
  errors: {
    connectionFailed: 'Bağlantı hatası. Lütfen internet bağlantınızı kontrol edin.',
    serverError: 'Sunucu hatası. Lütfen daha sonra tekrar deneyin.',
    dataLoadFailed: 'Veri yüklenemedi. Lütfen sayfayı yenileyin.',
    invalidCredentials: 'Geçersiz kullanıcı adı veya şifre.',
    insufficientBalance: 'Yetersiz bakiye.',
    invalidVolume: 'Geçersiz işlem hacmi.',
    invalidPrice: 'Geçersiz fiyat.',
    invalidStopLoss: 'Geçersiz zarar kes seviyesi.',
    invalidTakeProfit: 'Geçersiz kar al seviyesi.',
  }
};

export default translations; 