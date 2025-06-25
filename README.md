# ICT Ultra v2: Algo Forge Edition

Next-generation algorithmic trading platform with MetaTrader 5 integration and ICT (Inner Circle Trader) concepts implementation.

## 🚀 Features

### Core Features
- **MT5 Integration**: Direct connection to MetaTrader 5 with real-time data and trading capabilities
- **ICT Pattern Detection**: Advanced algorithms for Order Blocks, Fair Value Gaps, and Breaker Blocks
- **MQL5 Algo Forge**: Git-based strategy development and deployment with full Git integration
- **Real-time Trading**: Execute trades directly from the web interface
- **Advanced Scoring System**: 8-factor confluence analysis for signal quality
- **Professional UI**: Modern, responsive interface with TradingView charts

### Technical Stack
- **Backend**: Python FastAPI, SQLAlchemy, MetaTrader5 package
- **Frontend**: Next.js 14, TypeScript, TailwindCSS, TradingView Lightweight Charts
- **Architecture**: Modular monolith with DDD principles, Event-driven communication

## 📋 Prerequisites

- MetaTrader 5 Terminal installed
- Python 3.10+
- Node.js 18+
- MT5 Demo Account (Default: Login 25201110, Server: Tickmill-Demo)

## 🛠️ Installation

### 1. Clone the repository
```bash
git clone https://github.com/elkekoitan/ai_algo_trade.git
cd ai_algo_trade
```

### 2. Backend Setup

#### Create virtual environment
```bash
cd backend
python -m venv venv

# Windows
venv\Scripts\activate

# Linux/Mac
source venv/bin/activate
```

#### Install dependencies
```bash
pip install -r requirements.txt
```

#### Configure environment
```bash
# Copy example env file
cp env.example .env

# Edit .env with your MT5 credentials
# MT5_PASSWORD=your_password_here
```

### 3. Frontend Setup

```bash
cd ../frontend
npm install
```

## 🚀 Running the Application

### Start Backend Server
```bash
cd backend
python main.py
```
The backend will run on `http://localhost:8001`

### Start Frontend Development Server
```bash
cd frontend
npm run dev
```
The frontend will run on `http://localhost:3000`

## 📖 Usage

### Dashboard
- View account information
- Monitor system status
- Quick access to all features

### Trading Terminal
- Real-time charts with multiple timeframes
- Place market orders with SL/TP
- Manage open positions
- View P&L in real-time

### ICT Signals
- View detected ICT patterns
- Filter by timeframe and pattern type
- Detailed confluence analysis
- Risk assessment for each signal

### MQL5 Algo Forge Integration

The platform provides a complete Git-based workflow for MQL5 strategy development:

#### Repository Management
- Create new strategy repositories
- Clone existing repositories
- Manage multiple strategy versions with Git branches
- Push/pull changes to remote repositories

#### Strategy Development
- Edit MQL5 files directly from the web interface
- Commit changes with descriptive messages
- Track development history with detailed commit logs
- Collaborate with team members through Git

#### Deployment
- Deploy strategies directly to MT5
- Test strategies in demo environment
- Monitor strategy performance
- Roll back to previous versions if needed

#### Supported MQL5 Types
- Expert Advisors (EAs)
- Indicators
- Scripts
- Libraries
- Include files

## 🏗️ Project Structure

```
ai_algo_trade/
├── backend/
│   ├── api/v1/           # API endpoints
│   ├── core/             # Core modules (config, database, events)
│   ├── modules/          # Domain modules
│   │   ├── mt5_integration/
│   │   └── signals/
│   │       └── ict/      # ICT pattern detection
│   └── main.py           # FastAPI application
├── frontend/
│   ├── app/              # Next.js app directory
│   ├── components/       # React components
│   └── public/           # Static assets
├── mql5_forge_repos/     # MQL5 strategies
└── docs/                 # Documentation
```

## 🔧 API Documentation

Once the backend is running, access the interactive API documentation:
- Swagger UI: `http://localhost:8001/docs`
- ReDoc: `http://localhost:8001/redoc`

## 📊 ICT Scoring System

The platform uses an 8-factor scoring system:
- **Trend Strength** (20%): Alignment with higher timeframe trends
- **Volume Confirmation** (15%): Volume analysis at key levels
- **Structure Quality** (15%): Market structure clarity
- **Liquidity Presence** (10%): Liquidity pool detection
- **Confluence Factor** (20%): Multiple pattern alignment
- **Time of Day** (5%): Trading session analysis
- **Market Sentiment** (5%): Overall market conditions
- **Setup Strength** (10%): Pattern formation quality

## 🔒 Risk Levels

- **LOW** (90+ score): High probability setups
- **MEDIUM** (80-89 score): Good trading opportunities
- **HIGH** (70-79 score): Requires careful analysis
- **EXTREME** (<70 score): Not recommended for trading

## 🧪 Testing

Run the backend test script:
```bash
cd scripts
python test_backend.py
```

## 🤝 Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the LICENSE file for details.

## ⚠️ Disclaimer

This software is for educational and research purposes only. Trading forex and other financial instruments carries significant risk. Always use proper risk management and trade responsibly.

## 📞 Support

For support, please open an issue on GitHub or contact the development team.

---

Built with ❤️ for the trading community 