/**
 * English translations for ICT Ultra v2
 */

const translations = {
  // Common
  common: {
    loading: 'Loading...',
    error: 'Error',
    success: 'Success',
    retry: 'Retry',
    save: 'Save',
    cancel: 'Cancel',
    close: 'Close',
    confirm: 'Confirm',
    yes: 'Yes',
    no: 'No',
    back: 'Back',
    next: 'Next',
    submit: 'Submit',
  },

  // Navigation
  navigation: {
    dashboard: 'Dashboard',
    trading: 'Trading Terminal',
    signals: 'ICT Signals',
    performance: 'Performance',
    quantum: 'Quantum Dashboard',
    settings: 'Settings',
    logout: 'Logout',
  },

  // Dashboard
  dashboard: {
    title: 'Trading Dashboard',
    subtitle: 'Real-time market analysis and trading',
    quickAccess: 'Quick Access',
    marketSymbols: 'Market Symbols',
    marketChart: 'Market Chart',
  },

  // Account
  account: {
    overview: 'Account Overview',
    balance: 'Balance',
    equity: 'Equity',
    margin: 'Margin',
    freeMargin: 'Free Margin',
    marginLevel: 'Margin Level',
    profit: 'Profit/Loss',
    leverage: 'Leverage',
    accountInfo: 'Account Info',
    server: 'Server',
  },

  // Trading
  trading: {
    buy: 'BUY',
    sell: 'SELL',
    volume: 'Volume (Lots)',
    entry: 'Entry',
    stopLoss: 'Stop Loss',
    takeProfit: 'Take Profit',
    orderType: 'Order Type',
    market: 'Market',
    limit: 'Limit',
    stop: 'Stop',
    pending: 'Pending',
    positions: 'Positions',
    orders: 'Orders',
    history: 'History',
    symbol: 'Symbol',
    timeframe: 'Timeframe',
    price: 'Price',
    openTime: 'Open Time',
    closeTime: 'Close Time',
    profit: 'Profit',
    loss: 'Loss',
    comment: 'Comment',
  },

  // Signals
  signals: {
    orderBlock: 'Order Block',
    fairValueGap: 'Fair Value Gap',
    breakerBlock: 'Breaker Block',
    bullish: 'Bullish',
    bearish: 'Bearish',
    strength: 'Strength',
    confidence: 'Confidence',
    status: 'Status',
    active: 'Active',
    expired: 'Expired',
    confirmed: 'Confirmed',
  },

  // Scanner
  scanner: {
    title: 'Market Scanner',
    scanning: 'Scanning',
    paused: 'Paused',
    filters: 'Filters',
    scan: 'Scan',
    lastScan: 'Last Scan',
    nextScan: 'Next Scan',
    opportunities: 'Trading Opportunities',
    found: 'found',
    symbols: 'Symbols',
    timeframes: 'Timeframes',
    minStrength: 'Min. Strength',
    minConfidence: 'Min. Confidence',
    minRiskReward: 'Min. Risk/Reward',
    noOpportunities: 'No Opportunities Found',
    tryAdjusting: 'Try adjusting your filters or wait for new market conditions.',
  },

  // Auto Trader
  autoTrader: {
    title: 'Auto Trader Control',
    status: 'Status',
    active: 'Active',
    inactive: 'Inactive',
    start: 'Start',
    stop: 'Stop',
    settings: 'Settings',
    strategies: 'Strategies',
    riskManagement: 'Risk Management',
    maxRisk: 'Max Risk',
    maxPositions: 'Max Positions',
    maxDrawdown: 'Max Drawdown',
  },

  // Contact
  contact: {
    title: 'Contact',
    name: 'Name',
    email: 'Email',
    message: 'Message',
    send: 'Send',
    success: 'Your message has been sent successfully. We will get back to you soon.',
    error: 'Failed to send your message. Please try again later.',
  },

  // Errors
  errors: {
    connectionFailed: 'Connection failed. Please check your internet connection.',
    serverError: 'Server error. Please try again later.',
    dataLoadFailed: 'Failed to load data. Please refresh the page.',
    invalidCredentials: 'Invalid username or password.',
    insufficientBalance: 'Insufficient balance.',
    invalidVolume: 'Invalid volume.',
    invalidPrice: 'Invalid price.',
    invalidStopLoss: 'Invalid stop loss level.',
    invalidTakeProfit: 'Invalid take profit level.',
  }
};

export default translations;
