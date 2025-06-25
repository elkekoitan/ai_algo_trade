# MetaTrader 5 Integration Guide for ICT Ultra Platform

## Overview

This guide explains how to use the MetaTrader 5 (MT5) integration in the ICT Ultra Platform, including the new MQL5 Algo Forge features introduced in MT5 version 5100. The integration allows you to connect to MT5 accounts, access market data, execute trades, and manage trading algorithms using Git version control.

## Prerequisites

1. MetaTrader 5 terminal installed (version 5100 or later)
2. MT5 demo or real account credentials
3. Python 3.8 or later
4. ICT Ultra Platform installed and configured

## Setup

### 1. Install Required Packages

```bash
pip install MetaTrader5 fastapi uvicorn sqlalchemy pydantic redis
```

### 2. Configure MT5 Connection

Edit your `.env` file or environment variables to include MT5 connection settings:

```
MT5_ENABLED=true
MT5_SERVER=demo.mt5tickmill.com
MT5_LOGIN=25201110
MT5_PASSWORD=your_password
MT5_TIMEOUT=60000

# MQL5 Algo Forge settings
ALGO_FORGE_ENABLED=true
ALGO_FORGE_URL=https://forge.mql5.io
ALGO_FORGE_TOKEN=your_token
ALGO_FORGE_REPO_PATH=./algo_repos
```

### 3. Start the ICT Ultra Platform

```bash
cd backend
python -m uvicorn src.ict_ultra.main:app --reload
```

## Using the MT5 Integration API

The MT5 integration provides a REST API for interacting with MetaTrader 5. The API is available at `/api/mt5` and includes the following endpoints:

### Connection Management

- `GET /api/mt5/connection/status` - Get MT5 connection status
- `POST /api/mt5/connection/connect` - Connect to MT5
- `POST /api/mt5/connection/disconnect` - Disconnect from MT5
- `POST /api/mt5/connection/reconnect` - Reconnect to MT5

### Account Information

- `GET /api/mt5/account/info` - Get MT5 account information

### Symbol Information

- `GET /api/mt5/symbols` - Get available symbols
- `GET /api/mt5/symbols/{symbol}` - Get symbol information

### MQL5 Algo Forge Integration

- `POST /api/mt5/algo-forge/repositories/{repo_id}/sync` - Synchronize with MQL5 Algo Forge repository
- `GET /api/mt5/algo-forge/repositories/{repo_id}/scripts` - Get scripts from MQL5 Algo Forge repository

## Working with MQL5 Algo Forge

MQL5 Algo Forge is a new feature in MetaTrader 5 that provides Git integration for managing trading algorithms. The ICT Ultra Platform integrates with MQL5 Algo Forge to enable version-controlled algorithm development and deployment.

### Repository Management

1. **Synchronize Repository**

   ```
   POST /api/mt5/algo-forge/repositories/your_repo_id/sync
   ```

   This will clone or pull the latest changes from the MQL5 Algo Forge repository.

2. **List Scripts**

   ```
   GET /api/mt5/algo-forge/repositories/your_repo_id/scripts
   ```

   This will scan the repository for MQL5 scripts (indicators, experts, scripts, libraries) and return their information.

### Script Development Workflow

1. **Clone Repository**

   Use the API to clone the repository to your local machine.

2. **Develop Scripts**

   Create or modify MQL5 scripts in the repository directory.

3. **Commit and Push Changes**

   Use Git commands to commit and push your changes to the MQL5 Algo Forge repository.

4. **Synchronize Repository**

   Use the API to pull the latest changes from the MQL5 Algo Forge repository.

5. **Deploy Scripts**

   Use the MT5 terminal to compile and deploy the scripts.

## Integrating with ICT Concepts

The ICT Ultra Platform integrates MT5 with Inner Circle Trader (ICT) concepts such as order blocks, fair value gaps, and breaker blocks. Here's how to use these concepts with MT5:

### Order Blocks

Order blocks are significant areas where orders were placed that moved the market. They are often used as support/resistance zones.

```python
from ict_ultra.modules.signals.domain.models import OrderBlock, Direction, TimeFrame

# Create an order block
order_block = OrderBlock(
    symbol="EURUSD",
    timeframe=TimeFrame.H1,
    direction=Direction.BUY,
    start_time=datetime(2023, 1, 1, 10, 0),
    end_time=datetime(2023, 1, 1, 11, 0),
    high_price=1.2000,
    low_price=1.1950,
    entry_price=1.1975,
    stop_loss_price=1.1940,
    take_profit_price=1.2050,
    volume=0.1,
    strength=0.8
)

# Calculate risk-reward ratio
risk_reward = order_block.calculate_risk_reward_ratio()
print(f"Risk-reward ratio: {risk_reward}")
```

### Fair Value Gaps

Fair value gaps (FVGs) are gaps in price that represent "fair value" that the market often returns to fill. They are high-probability reversal zones.

```python
from ict_ultra.modules.signals.domain.models import FairValueGap, Direction, TimeFrame

# Create a fair value gap
fvg = FairValueGap(
    symbol="EURUSD",
    timeframe=TimeFrame.H1,
    direction=Direction.BUY,
    start_time=datetime(2023, 1, 1, 10, 0),
    end_time=datetime(2023, 1, 1, 11, 0),
    gap_high=1.2000,
    gap_low=1.1950,
    gap_middle=1.1975,
    strength=0.8
)

# Calculate gap size in pips
gap_size = fvg.calculate_gap_size()
print(f"Gap size: {gap_size} pips")
```

### Breaker Blocks

Breaker blocks are former support/resistance levels that have been broken and are now expected to act in the opposite role (former support becomes resistance and vice versa).

```python
from ict_ultra.modules.signals.domain.models import BreakerBlock, Direction, TimeFrame

# Create a breaker block
breaker_block = BreakerBlock(
    symbol="EURUSD",
    timeframe=TimeFrame.H1,
    direction=Direction.BUY,
    start_time=datetime(2023, 1, 1, 10, 0),
    end_time=datetime(2023, 1, 1, 11, 0),
    high_price=1.2000,
    low_price=1.1950,
    broken_level=1.1975,
    strength=0.8
)

# Check if breaker block has been retested
is_retested = breaker_block.is_retested()
print(f"Is retested: {is_retested}")
```

## Troubleshooting

### Common Issues

1. **Connection Errors**

   - Check that the MT5 terminal is running
   - Verify that the MT5 credentials are correct
   - Ensure that the MT5 server is accessible

2. **MQL5 Algo Forge Errors**

   - Check that the repository ID is correct
   - Verify that the ALGO_FORGE_TOKEN is valid
   - Ensure that Git is installed and accessible

3. **Script Compilation Errors**

   - Check the script syntax
   - Verify that the script dependencies are available
   - Ensure that the MT5 terminal has the necessary permissions

### Logging

The ICT Ultra Platform uses structured logging to provide detailed information about MT5 integration operations. Check the logs for error messages and troubleshooting information.

## Advanced Configuration

### MT5 Connection Settings

The MT5 connection settings can be configured in the `ict_ultra.core.config` module:

```python
class MT5Config(BaseSettings):
    """MetaTrader 5 configuration"""
    enabled: bool = Field(default=True, env="MT5_ENABLED")
    server: str = Field(default="demo.mt5tickmill.com", env="MT5_SERVER")
    login: int = Field(default=25201110, env="MT5_LOGIN")
    password: str = Field(default="", env="MT5_PASSWORD")
    timeout: int = Field(default=60000, env="MT5_TIMEOUT")
    
    # MQL5 Algo Forge settings
    algo_forge_enabled: bool = Field(default=True, env="ALGO_FORGE_ENABLED")
    algo_forge_url: str = Field(default="https://forge.mql5.io", env="ALGO_FORGE_URL")
    algo_forge_token: Optional[str] = Field(default=None, env="ALGO_FORGE_TOKEN")
    algo_forge_repo_path: str = Field(default="./algo_repos", env="ALGO_FORGE_REPO_PATH")
```

### Custom MT5 Services

You can extend the MT5 integration by creating custom services in the `ict_ultra.modules.mt5_integration.services` package. For example, you could create a service for automated trading or backtesting.

## Conclusion

The MetaTrader 5 integration in the ICT Ultra Platform provides a powerful way to connect to MT5 accounts, access market data, execute trades, and manage trading algorithms using Git version control. By following this guide, you should be able to set up and use the MT5 integration effectively. 