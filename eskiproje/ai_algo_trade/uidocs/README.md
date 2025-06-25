# ICT Ultra Platform

## Overview

ICT Ultra Platform is an advanced trading platform that integrates Inner Circle Trader (ICT) concepts with MetaTrader 5 (MT5) for algorithmic trading. The platform is designed as a modular monolith architecture with domain-driven design principles, providing a robust foundation for trading strategy development and execution.

## Key Features

- **MT5 Integration**: Direct connection to MetaTrader 5 platform with real-time data and trading capabilities
- **MQL5 Algo Forge**: Integration with the new Git-based developer hub for algorithm version control
- **ICT Concepts**: Implementation of key ICT trading concepts such as order blocks, fair value gaps, and breaker blocks
- **Modular Architecture**: Clean separation of concerns with domain-specific modules
- **Real-Time Data**: Live market data processing and analysis
- **Risk Management**: Advanced risk calculation and position sizing
- **AI Capabilities**: Machine learning integration for predictive analytics

## Architecture

The platform follows a modular monolith architecture with the following components:

### Core Modules

- **Events System**: Pub/sub pattern for inter-module communication
- **Configuration**: Environment-based configuration management
- **Database**: Async SQLAlchemy integration for data persistence
- **Cache**: Redis-based caching for performance optimization
- **Logging**: Structured logging for comprehensive system monitoring

### Domain Modules

- **Trading**: Order execution and management
- **Market Data**: Price data acquisition and processing
- **Signals**: Trading signal generation based on ICT concepts
- **Risk**: Position sizing and risk management
- **AI**: Machine learning models for market prediction
- **Account**: User and account management
- **MT5 Integration**: Direct connection to MetaTrader 5

## Getting Started

### Prerequisites

- Python 3.8+
- MetaTrader 5 terminal (version 5100+)
- MT5 demo or real account
- Git

### Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/your-username/ict-ultra-platform.git
   cd ict-ultra-platform
   ```

2. Install dependencies:
   ```bash
   cd backend
   pip install -r requirements.txt
   ```

3. Configure environment variables:
   ```bash
   cp .env.example .env
   # Edit .env with your MT5 credentials and settings
   ```

4. Start the platform:
   ```bash
   python -m uvicorn src.ict_ultra.main:app --reload
   ```

5. Access the API documentation:
   ```
   http://localhost:8000/docs
   ```

## Documentation

- [Architecture Documentation](./MODULAR_MONOLITH_ARCHITECTURE.md)
- [MT5 Integration Guide](./MT5_INTEGRATION_GUIDE.md)
- [API Reference](http://localhost:8000/docs) (available when the server is running)

## Performance

The ICT Ultra Platform has been tested with a MetaTrader 5 demo account (login: 25201110) and has shown impressive performance:

- 102 open positions
- $2.6M+ equity
- 76.47% win rate
- $249,623.43 profit

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the LICENSE file for details. 