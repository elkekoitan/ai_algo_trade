"""
ICT Ultra v2: Algo Forge Edition - ICT Signal Detection Test
"""

import time
import sys
import os
import numpy as np
import pandas as pd
import MetaTrader5 as mt5

# Add backend directory to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

# Import ICT signal modules
from modules.signals.ict.order_blocks import detect_order_blocks
from modules.signals.ict.fair_value_gaps import detect_fair_value_gaps
from modules.signals.ict.breaker_blocks import detect_breaker_blocks
from modules.signals.ict.scoring import score_signal

# MT5 credentials
MT5_LOGIN = 25201110
MT5_PASSWORD = "e|([rXU1IsiM"
MT5_SERVER = "Tickmill-Demo"

# Test parameters
SYMBOL = "EURUSD"
TIMEFRAME = mt5.TIMEFRAME_H1
CANDLE_COUNT = 100


def connect_to_mt5():
    """Connect to MetaTrader 5."""
    print("Initializing MetaTrader 5...")
    if not mt5.initialize():
        print(f"MT5 initialization failed!")
        return False
    
    print(f"Connecting to MT5 account...")
    print(f"Login: {MT5_LOGIN}")
    print(f"Server: {MT5_SERVER}")
    
    if not mt5.login(
        login=MT5_LOGIN,
        password=MT5_PASSWORD,
        server=MT5_SERVER
    ):
        print(f"MT5 login failed: {mt5.last_error()}")
        mt5.shutdown()
        return False
    
    print(f"Connected successfully!")
    return True


def get_market_data(symbol, timeframe, count):
    """Get market data from MT5."""
    print(f"Getting {count} candles for {symbol}...")
    rates = mt5.copy_rates_from_pos(symbol, timeframe, 0, count)
    
    if rates is None:
        print(f"Failed to get {symbol} rates: {mt5.last_error()}")
        return None
    
    # Convert to DataFrame
    df = pd.DataFrame(rates)
    df['time'] = pd.to_datetime(df['time'], unit='s')
    
    print(f"Retrieved {len(df)} candles")
    return df


def detect_signals(df):
    """Detect ICT signals in the market data."""
    print("\nDetecting ICT signals...")
    
    # Detect order blocks
    print("\nDetecting Order Blocks...")
    bullish_obs, bearish_obs = detect_order_blocks(df)
    print(f"Found {len(bullish_obs)} bullish order blocks")
    print(f"Found {len(bearish_obs)} bearish order blocks")
    
    # Detect fair value gaps
    print("\nDetecting Fair Value Gaps...")
    bullish_fvgs, bearish_fvgs = detect_fair_value_gaps(df)
    print(f"Found {len(bullish_fvgs)} bullish fair value gaps")
    print(f"Found {len(bearish_fvgs)} bearish fair value gaps")
    
    # Detect breaker blocks
    print("\nDetecting Breaker Blocks...")
    bullish_bbs, bearish_bbs = detect_breaker_blocks(df)
    print(f"Found {len(bullish_bbs)} bullish breaker blocks")
    print(f"Found {len(bearish_bbs)} bearish breaker blocks")
    
    return {
        'order_blocks': {
            'bullish': bullish_obs,
            'bearish': bearish_obs
        },
        'fair_value_gaps': {
            'bullish': bullish_fvgs,
            'bearish': bearish_fvgs
        },
        'breaker_blocks': {
            'bullish': bullish_bbs,
            'bearish': bearish_bbs
        }
    }


def score_signals(signals, df):
    """Score the detected signals."""
    print("\nScoring signals...")
    
    scored_signals = []
    
    # Score order blocks
    for ob in signals['order_blocks']['bullish']:
        score = score_signal(df, ob, 'order_block', 'bullish')
        scored_signals.append({
            'type': 'Order Block',
            'direction': 'Bullish',
            'index': ob['index'],
            'price': ob['price'],
            'score': score
        })
    
    for ob in signals['order_blocks']['bearish']:
        score = score_signal(df, ob, 'order_block', 'bearish')
        scored_signals.append({
            'type': 'Order Block',
            'direction': 'Bearish',
            'index': ob['index'],
            'price': ob['price'],
            'score': score
        })
    
    # Score fair value gaps
    for fvg in signals['fair_value_gaps']['bullish']:
        score = score_signal(df, fvg, 'fair_value_gap', 'bullish')
        scored_signals.append({
            'type': 'Fair Value Gap',
            'direction': 'Bullish',
            'index': fvg['index'],
            'price': fvg['price'],
            'score': score
        })
    
    for fvg in signals['fair_value_gaps']['bearish']:
        score = score_signal(df, fvg, 'fair_value_gap', 'bearish')
        scored_signals.append({
            'type': 'Fair Value Gap',
            'direction': 'Bearish',
            'index': fvg['index'],
            'price': fvg['price'],
            'score': score
        })
    
    # Score breaker blocks
    for bb in signals['breaker_blocks']['bullish']:
        score = score_signal(df, bb, 'breaker_block', 'bullish')
        scored_signals.append({
            'type': 'Breaker Block',
            'direction': 'Bullish',
            'index': bb['index'],
            'price': bb['price'],
            'score': score
        })
    
    for bb in signals['breaker_blocks']['bearish']:
        score = score_signal(df, bb, 'breaker_block', 'bearish')
        scored_signals.append({
            'type': 'Breaker Block',
            'direction': 'Bearish',
            'index': bb['index'],
            'price': bb['price'],
            'score': score
        })
    
    # Sort by score
    scored_signals.sort(key=lambda x: x['score'], reverse=True)
    
    return scored_signals


def display_top_signals(scored_signals, limit=5):
    """Display top scored signals."""
    print("\nTop signals:")
    print("=" * 80)
    print(f"{'Type':<15} {'Direction':<10} {'Index':<10} {'Price':<10} {'Score':<10} {'Risk Level':<10}")
    print("-" * 80)
    
    for i, signal in enumerate(scored_signals[:limit]):
        # Determine risk level
        risk_level = "EXTREME"
        if signal['score'] >= 90:
            risk_level = "LOW"
        elif signal['score'] >= 80:
            risk_level = "MEDIUM"
        elif signal['score'] >= 70:
            risk_level = "HIGH"
        
        print(f"{signal['type']:<15} {signal['direction']:<10} {signal['index']:<10} "
              f"{signal['price']:<10.5f} {signal['score']:<10.2f} {risk_level:<10}")
    
    print("=" * 80)


def main():
    """Main function."""
    print("ICT Ultra v2: Algo Forge Edition - ICT Signal Detection Test")
    print("===========================================================")
    
    # Connect to MT5
    if not connect_to_mt5():
        return
    
    try:
        # Get market data
        df = get_market_data(SYMBOL, TIMEFRAME, CANDLE_COUNT)
        if df is None:
            return
        
        # Detect signals
        signals = detect_signals(df)
        
        # Score signals
        scored_signals = score_signals(signals, df)
        
        # Display top signals
        display_top_signals(scored_signals)
        
    except Exception as e:
        print(f"Error: {e}")
    finally:
        # Disconnect from MT5
        print("\nDisconnecting from MT5...")
        mt5.shutdown()
        print("Disconnected!")


if __name__ == "__main__":
    main() 