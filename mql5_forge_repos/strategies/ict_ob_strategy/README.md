# ICT Order Block Expert Advisor

This Expert Advisor implements the ICT (Inner Circle Trader) concept of Order Blocks for automated trading in MetaTrader 5.

## Overview

Order blocks are areas on the chart where significant orders were placed before a strong move in price, often serving as support/resistance in the future. This EA identifies these areas and trades when price returns to them.

## Features

- **Multi-symbol Trading**: Monitor and trade multiple symbols simultaneously
- **Advanced Order Block Detection**: Identifies high-quality order blocks using body size, move size, and confirmation candles
- **Strength-based Scoring**: Calculates a strength score for each order block
- **Risk Management**: Position sizing based on account balance and risk percentage
- **Trade Management**: Stop loss and take profit levels based on the order block

## Installation

1. Open MetaTrader 5
2. Go to File > Open Data Folder
3. Navigate to MQL5 > Experts
4. Copy the ICT_OrderBlock_EA.mq5 file to this folder
5. Restart MetaTrader 5 or refresh the Navigator panel
6. Drag the EA onto a chart to start using it

## Parameters

### Symbol Settings
- **Symbol List**: Comma-separated list of symbols to monitor (e.g., "EURUSD,GBPUSD,USDJPY,XAUUSD")
- **Timeframe**: The timeframe to analyze for order blocks

### Order Block Settings
- **MinBodySizeFactor**: Minimum candle body size as a factor of average body size
- **MinMoveAfterFactor**: Minimum move after the order block as a factor of average body size
- **ConfirmationCandles**: Number of candles to confirm the move after the order block
- **LookbackPeriod**: How far back to look for order blocks
- **StrengthThreshold**: Minimum strength threshold for valid order blocks

### Trade Settings
- **LotSize**: Fixed lot size for trades
- **RiskPercent**: Risk percent per trade (for dynamic position sizing)
- **StopLoss**: Stop loss in points (0 = no SL)
- **TakeProfit**: Take profit in points
- **MaxTrades**: Maximum simultaneous trades
- **MagicNumber**: Magic number for identifying EA trades

## Usage

1. Attach the EA to any chart
2. Configure the parameters according to your trading preferences
3. Enable automated trading in MetaTrader 5
4. The EA will monitor the specified symbols and timeframes for order blocks
5. When price returns to a valid order block, the EA will open a trade

## Recommended Settings

For beginners, we recommend starting with:
- Symbol List: "EURUSD,GBPUSD,USDJPY,XAUUSD"
- Timeframe: H1
- MinBodySizeFactor: 0.6
- MinMoveAfterFactor: 1.5
- ConfirmationCandles: 3
- LookbackPeriod: 100
- StrengthThreshold: 0.7
- RiskPercent: 1.0
- StopLoss: 50
- TakeProfit: 100

## Notes

- This EA works best in trending markets
- Higher timeframes (H1, H4, D1) tend to produce more reliable order blocks
- The strength threshold can be adjusted based on your risk tolerance
- Always test on a demo account before using on a live account

## Version History

- 1.0: Initial release

## License

This Expert Advisor is part of the ICT Ultra v2 platform and is subject to its license terms.

## Author

ICT Ultra v2: Algo Forge 