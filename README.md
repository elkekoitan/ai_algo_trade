# ICT Ultra v2: Algo Forge Edition

Next-generation algorithmic trading platform with full MetaTrader 5 integration and MQL5 Algo Forge Git capabilities.

## Overview

ICT Ultra v2 is a comprehensive trading platform that leverages the power of MetaTrader 5's new Git integration and MQL5 Algo Forge developer hub. Built on the success of the original ICT Ultra Platform, this new version brings institutional-grade trading tools, advanced ICT concepts implementation, and professional-level risk management to retail traders.

## Key Features

- **Full MT5 Integration**: Direct connection to MetaTrader 5 with real-time data and trading capabilities
- **MQL5 Algo Forge Git Integration**: Seamless development workflow with Git repositories
- **ICT Trading Concepts**: Order blocks, fair value gaps, breaker blocks, and more
- **Advanced Risk Management**: Portfolio-level risk analysis and position sizing
- **Real-Time ML Predictions**: TensorFlow.js powered price predictions
- **Professional UI/UX**: Dark-themed, glassmorphic design with TradingView-style charts

## Getting Started

### Prerequisites

- MetaTrader 5 platform (version 5100+) with demo account
- Python 3.13+
- Node.js 20+

### Installation

1. Clone this repository
2. Set up the backend:
   ```
   cd backend
   pip install -r requirements.txt
   python main.py
   ```
3. Set up the frontend:
   ```
   cd frontend
   npm install
   npm run dev
   ```

## Architecture

The project follows a modular monolith architecture with domain-driven design principles:

- **Backend**: Python FastAPI server with MT5 integration
- **Frontend**: Next.js with TypeScript and TailwindCSS
- **MQL5 Forge Repos**: Git repositories for MT5 algorithms

For more details, see the [Architecture Document](docs/ARCHITECTURE.md).

## License

This project is proprietary software. All rights reserved. 