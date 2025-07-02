# MT5 Configuration for Multi-Account Copy Trading
MT5_LOGIN = 25201110
MT5_PASSWORD = "e|([rXU1IsiM"
MT5_SERVER = "Tickmill-Demo"

# COPY TRADING DEMO ACCOUNTS - Yeni hesaplar
COPY_TRADING_ACCOUNTS = [
    {
        "login": 25216036,
        "password": "oB9UY1&,B=^9",
        "server": "Tickmill-Demo",
        "name": "Copy Account 1",
        "type": "follower"
    },
    {
        "login": 25216037,
        "password": "L[.Sdo4QRxx2", 
        "server": "Tickmill-Demo",
        "name": "Copy Account 2",
        "type": "follower"
    }
]

ACCOUNT_TYPE = "Classic"
ACCOUNT_CURRENCY = "USD"
DEFAULT_SYMBOLS = ["EURUSD", "GBPUSD", "USDJPY", "XAUUSD"]
ICT_ENABLED = True
SIGNAL_GENERATION = True
AUTO_TRADING = False
