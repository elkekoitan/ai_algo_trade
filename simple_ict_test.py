"""
ICT Ultra v2: Algo Forge Edition - Simple ICT Signal Detection Test
"""

import time
import numpy as np
import pandas as pd
import MetaTrader5 as mt5

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


def detect_order_blocks(df):
    """Simple order block detection algorithm."""
    print("\nDetecting Order Blocks...")
    
    # Create copies of the dataframe
    df_copy = df.copy()
    
    # Calculate price movements
    df_copy['body_size'] = abs(df_copy['close'] - df_copy['open'])
    df_copy['is_bullish'] = df_copy['close'] > df_copy['open']
    df_copy['is_bearish'] = df_copy['close'] < df_copy['open']
    
    # Calculate moving average for trend determination
    df_copy['ma20'] = df_copy['close'].rolling(window=20).mean()
    
    # Initialize lists for order blocks
    bullish_obs = []
    bearish_obs = []
    
    # Detect bullish order blocks (support)
    for i in range(3, len(df_copy) - 1):
        # Check for a bearish candle followed by bullish momentum
        if (df_copy['is_bearish'].iloc[i-2] and 
            df_copy['body_size'].iloc[i-2] > df_copy['body_size'].iloc[i-2:i+1].mean() and
            df_copy['is_bullish'].iloc[i-1] and 
            df_copy['is_bullish'].iloc[i] and
            df_copy['close'].iloc[i] > df_copy['close'].iloc[i-1]):
            
            # This is a potential bullish order block
            bullish_obs.append({
                'index': i-2,
                'time': df_copy['time'].iloc[i-2],
                'price': min(df_copy['open'].iloc[i-2], df_copy['close'].iloc[i-2]),
                'strength': df_copy['body_size'].iloc[i-2] / df_copy['body_size'].iloc[i-2:i+1].mean()
            })
    
    # Detect bearish order blocks (resistance)
    for i in range(3, len(df_copy) - 1):
        # Check for a bullish candle followed by bearish momentum
        if (df_copy['is_bullish'].iloc[i-2] and 
            df_copy['body_size'].iloc[i-2] > df_copy['body_size'].iloc[i-2:i+1].mean() and
            df_copy['is_bearish'].iloc[i-1] and 
            df_copy['is_bearish'].iloc[i] and
            df_copy['close'].iloc[i] < df_copy['close'].iloc[i-1]):
            
            # This is a potential bearish order block
            bearish_obs.append({
                'index': i-2,
                'time': df_copy['time'].iloc[i-2],
                'price': max(df_copy['open'].iloc[i-2], df_copy['close'].iloc[i-2]),
                'strength': df_copy['body_size'].iloc[i-2] / df_copy['body_size'].iloc[i-2:i+1].mean()
            })
    
    print(f"Found {len(bullish_obs)} bullish order blocks")
    print(f"Found {len(bearish_obs)} bearish order blocks")
    
    return bullish_obs, bearish_obs


def detect_fair_value_gaps(df):
    """Simple fair value gap detection algorithm."""
    print("\nDetecting Fair Value Gaps...")
    
    # Create copies of the dataframe
    df_copy = df.copy()
    
    # Initialize lists for fair value gaps
    bullish_fvgs = []
    bearish_fvgs = []
    
    # Detect bullish fair value gaps
    for i in range(2, len(df_copy) - 1):
        # Check for a gap up
        if df_copy['low'].iloc[i] > df_copy['high'].iloc[i-2]:
            # This is a bullish fair value gap
            bullish_fvgs.append({
                'index': i-1,
                'time': df_copy['time'].iloc[i-1],
                'price': (df_copy['low'].iloc[i] + df_copy['high'].iloc[i-2]) / 2,
                'size': df_copy['low'].iloc[i] - df_copy['high'].iloc[i-2]
            })
    
    # Detect bearish fair value gaps
    for i in range(2, len(df_copy) - 1):
        # Check for a gap down
        if df_copy['high'].iloc[i] < df_copy['low'].iloc[i-2]:
            # This is a bearish fair value gap
            bearish_fvgs.append({
                'index': i-1,
                'time': df_copy['time'].iloc[i-1],
                'price': (df_copy['high'].iloc[i] + df_copy['low'].iloc[i-2]) / 2,
                'size': df_copy['low'].iloc[i-2] - df_copy['high'].iloc[i]
            })
    
    print(f"Found {len(bullish_fvgs)} bullish fair value gaps")
    print(f"Found {len(bearish_fvgs)} bearish fair value gaps")
    
    return bullish_fvgs, bearish_fvgs


def detect_breaker_blocks(df):
    """Simple breaker block detection algorithm."""
    print("\nDetecting Breaker Blocks...")
    
    # Get order blocks first
    bullish_obs, bearish_obs = detect_order_blocks(df)
    
    # Create copies of the dataframe
    df_copy = df.copy()
    
    # Initialize lists for breaker blocks
    bullish_bbs = []
    bearish_bbs = []
    
    # Detect bullish breaker blocks
    for ob in bearish_obs:
        idx = ob['index']
        price = ob['price']
        
        # Check if price broke through this level after the order block formed
        for i in range(idx + 3, len(df_copy) - 1):
            if df_copy['close'].iloc[i] > price and df_copy['close'].iloc[i-1] < price:
                # This is a bullish breaker block
                bullish_bbs.append({
                    'index': i,
                    'time': df_copy['time'].iloc[i],
                    'price': price,
                    'original_ob_index': idx
                })
                break
    
    # Detect bearish breaker blocks
    for ob in bullish_obs:
        idx = ob['index']
        price = ob['price']
        
        # Check if price broke through this level after the order block formed
        for i in range(idx + 3, len(df_copy) - 1):
            if df_copy['close'].iloc[i] < price and df_copy['close'].iloc[i-1] > price:
                # This is a bearish breaker block
                bearish_bbs.append({
                    'index': i,
                    'time': df_copy['time'].iloc[i],
                    'price': price,
                    'original_ob_index': idx
                })
                break
    
    print(f"Found {len(bullish_bbs)} bullish breaker blocks")
    print(f"Found {len(bearish_bbs)} bearish breaker blocks")
    
    return bullish_bbs, bearish_bbs


def score_signal(signal, signal_type, direction):
    """Simple signal scoring algorithm."""
    base_score = 70  # Base score
    
    # Add score based on signal type
    if signal_type == 'order_block':
        base_score += 5
        if 'strength' in signal and signal['strength'] > 1.5:
            base_score += 5
    elif signal_type == 'fair_value_gap':
        base_score += 3
        if 'size' in signal and signal['size'] > 0.001:
            base_score += 5
    elif signal_type == 'breaker_block':
        base_score += 8
    
    # Add some randomness to simulate other factors
    base_score += np.random.randint(-5, 15)
    
    # Cap score at 100
    return min(100, base_score)


def main():
    """Main function."""
    print("ICT Ultra v2: Algo Forge Edition - Simple ICT Signal Detection Test")
    print("=================================================================")
    
    # Connect to MT5
    if not connect_to_mt5():
        return
    
    try:
        # Get market data
        df = get_market_data(SYMBOL, TIMEFRAME, CANDLE_COUNT)
        if df is None:
            return
        
        # Detect order blocks
        bullish_obs, bearish_obs = detect_order_blocks(df)
        
        # Detect fair value gaps
        bullish_fvgs, bearish_fvgs = detect_fair_value_gaps(df)
        
        # Detect breaker blocks
        bullish_bbs, bearish_bbs = detect_breaker_blocks(df)
        
        # Score and collect all signals
        all_signals = []
        
        # Score order blocks
        for ob in bullish_obs:
            score = score_signal(ob, 'order_block', 'bullish')
            all_signals.append({
                'type': 'Order Block',
                'direction': 'Bullish',
                'index': ob['index'],
                'time': ob['time'],
                'price': ob['price'],
                'score': score
            })
        
        for ob in bearish_obs:
            score = score_signal(ob, 'order_block', 'bearish')
            all_signals.append({
                'type': 'Order Block',
                'direction': 'Bearish',
                'index': ob['index'],
                'time': ob['time'],
                'price': ob['price'],
                'score': score
            })
        
        # Score fair value gaps
        for fvg in bullish_fvgs:
            score = score_signal(fvg, 'fair_value_gap', 'bullish')
            all_signals.append({
                'type': 'Fair Value Gap',
                'direction': 'Bullish',
                'index': fvg['index'],
                'time': fvg['time'],
                'price': fvg['price'],
                'score': score
            })
        
        for fvg in bearish_fvgs:
            score = score_signal(fvg, 'fair_value_gap', 'bearish')
            all_signals.append({
                'type': 'Fair Value Gap',
                'direction': 'Bearish',
                'index': fvg['index'],
                'time': fvg['time'],
                'price': fvg['price'],
                'score': score
            })
        
        # Score breaker blocks
        for bb in bullish_bbs:
            score = score_signal(bb, 'breaker_block', 'bullish')
            all_signals.append({
                'type': 'Breaker Block',
                'direction': 'Bullish',
                'index': bb['index'],
                'time': bb['time'],
                'price': bb['price'],
                'score': score
            })
        
        for bb in bearish_bbs:
            score = score_signal(bb, 'breaker_block', 'bearish')
            all_signals.append({
                'type': 'Breaker Block',
                'direction': 'Bearish',
                'index': bb['index'],
                'time': bb['time'],
                'price': bb['price'],
                'score': score
            })
        
        # Sort by score
        all_signals.sort(key=lambda x: x['score'], reverse=True)
        
        # Display top signals
        print("\nTop ICT Signals:")
        print("=" * 100)
        print(f"{'Type':<15} {'Direction':<10} {'Index':<10} {'Time':<25} {'Price':<10} {'Score':<10} {'Risk Level':<10}")
        print("-" * 100)
        
        for i, signal in enumerate(all_signals[:10]):
            # Determine risk level
            risk_level = "EXTREME"
            if signal['score'] >= 90:
                risk_level = "LOW"
            elif signal['score'] >= 80:
                risk_level = "MEDIUM"
            elif signal['score'] >= 70:
                risk_level = "HIGH"
            
            print(f"{signal['type']:<15} {signal['direction']:<10} {signal['index']:<10} "
                  f"{signal['time']!s:<25} {signal['price']:<10.5f} {signal['score']:<10.2f} {risk_level:<10}")
        
        print("=" * 100)
        
    except Exception as e:
        print(f"Error: {e}")
    finally:
        # Disconnect from MT5
        print("\nDisconnecting from MT5...")
        mt5.shutdown()
        print("Disconnected!")


if __name__ == "__main__":
    main() 