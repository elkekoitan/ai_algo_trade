"""
MT5 Configuration for Real Trading
SADECE gerçek demo hesap bilgileri
"""

# TICKMILL DEMO HESAP BİLGİLERİ
MT5_LOGIN = 25201110
MT5_PASSWORD = "e|([rXU1IsiM"
MT5_SERVER = "Tickmill-Demo"

# Hesap Bilgileri
ACCOUNT_TYPE = "Classic"
ACCOUNT_CURRENCY = "USD"

# Connection Settings
CONNECTION_TIMEOUT = 60000  # 60 seconds
RETRY_COUNT = 3
RETRY_DELAY = 5  # seconds

# Trading Settings
DEFAULT_SYMBOLS = [
    "EURUSD", "GBPUSD", "USDJPY", "USDCHF", "AUDUSD", 
    "USDCAD", "NZDUSD", "EURJPY", "GBPJPY", "EURGBP",
    "XAUUSD", "USOIL", "USTEC", "US30", "GER40"
]

# ICT Settings
ICT_ENABLED = True
SIGNAL_GENERATION = True
AUTO_TRADING = False  # Güvenlik için başlangıçta kapalı

# Logging
LOG_LEVEL = "INFO"
LOG_MT5_OPERATIONS = True 