# 🚀 AI Algo Trade - Tickmill MT5 Login Guide

## 📋 Quick Start

### 1. **Start Backend**
```bash
cd backend
python main.py
```

### 2. **Start Frontend**
```bash
cd frontend
npm run dev
```

### 3. **Open Browser**
Navigate to: http://localhost:3000

## 🔐 MT5 Login Credentials

### Demo Account (Tickmill)
- **Login:** `25201110`
- **Password:** `e|([rXU1IsiM`
- **Server:** `Tickmill-Demo`

## 📱 Login Steps

### Method 1: MT5 Direct Login
1. Click on **"MT5"** tab in login form
2. Enter credentials:
   - MT5 Login: `25201110`
   - MT5 Password: `e|([rXU1IsiM`
   - MT5 Server: Select `Tickmill-Demo` from dropdown
3. Click **"Sign in with MT5"**

### Method 2: Email/Phone Registration + MT5
1. First register with email/phone
2. Add MT5 account from dashboard
3. Navigate to Settings → MT5 Accounts → Add Account

## ✅ Features Available After Login

### 📊 Trading Dashboard
- Real-time account balance and equity
- Open positions monitoring
- Profit/Loss tracking
- Market overview

### 🤖 AI Features
- **Strategy Whisperer**: Natural language strategy creation
- **Shadow Mode**: Institutional flow tracking
- **God Mode**: Omniscient market monitoring
- **Adaptive Trade Manager**: Dynamic position management
- **Market Narrator**: AI-powered market stories

### 📈 Trading Operations
- Place Buy/Sell orders
- Set Stop Loss and Take Profit
- View order history
- Real-time price charts

### 🔍 Market Analysis
- ICT pattern detection
- Fair Value Gaps
- Order Blocks
- Breaker Blocks
- Liquidity zones

## 🛠️ Troubleshooting

### Backend Not Starting?
```bash
# Check Python version (3.10+ required)
python --version

# Install dependencies
pip install -r requirements.txt

# Check MT5 package
pip install MetaTrader5
```

### Frontend Issues?
```bash
# Install dependencies
cd frontend
npm install

# Clear cache
npm cache clean --force
```

### MT5 Connection Failed?
1. Ensure you have internet connection
2. Check if MT5 servers are accessible
3. Verify credentials are correct
4. Try alternative demo account

## 📱 API Endpoints

### Authentication
- `POST /api/v1/auth/login/mt5` - MT5 login
- `GET /api/v1/auth/me` - Get current user
- `POST /api/v1/auth/logout` - Logout

### Trading
- `GET /api/v1/trading/account_info` - Account details
- `GET /api/v1/trading/positions` - Open positions
- `POST /api/v1/trading/order` - Place order
- `GET /api/v1/trading/history` - Trade history

### Market Data
- `GET /api/v1/market/symbols` - Available symbols
- `GET /api/v1/market/price/{symbol}` - Current price
- `GET /api/v1/market/candles/{symbol}` - Historical data

### AI Signals
- `GET /api/v1/signals/ict` - ICT patterns
- `GET /api/v1/signals/shadow` - Shadow mode signals
- `GET /api/v1/signals/god` - God mode predictions

## 🔒 Security Features

- ✅ SQL Injection Protection
- ✅ Encrypted MT5 passwords
- ✅ JWT token authentication
- ✅ Session management
- ✅ Rate limiting
- ✅ Row Level Security (RLS)

## 📞 Support

### Common Issues:
1. **"Invalid credentials"** - Double-check login details
2. **"Server not found"** - Select correct server from dropdown
3. **"Connection timeout"** - Check internet/firewall settings

### Need Help?
- Check logs in `backend/logs/`
- Review documentation in `docs/`
- Test connection with `python test_mt5_connection.py`

## 🎯 Next Steps

After successful login:
1. Explore the dashboard
2. Try Strategy Whisperer with natural language
3. Enable Shadow Mode for institutional tracking
4. Set up risk management rules
5. Start automated trading

---

**Happy Trading! 🚀**

*Last Updated: January 2025* 