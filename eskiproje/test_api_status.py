import requests
import json

try:
    # Backend API Status
    response = requests.get('http://localhost:8001/status', timeout=5)
    print('=== BACKEND API STATUS ===')
    print(f'Status Code: {response.status_code}')
    if response.status_code == 200:
        data = response.json()
        print(f'MT5 Status: {data.get("mt5_status", "Unknown")}')
        print(f'Account Login: {data.get("account_info", {}).get("login", "N/A")}')
        print(f'Balance: ${data.get("account_info", {}).get("balance", "N/A")}')
        print(f'Server: {data.get("account_info", {}).get("server", "N/A")}')
    else:
        print(f'Error: {response.text}')
except Exception as e:
    print(f'Backend API Error: {e}')

try:
    # ICT Signals
    response = requests.get('http://localhost:8001/ict/signals?min_score=85&max_results=10', timeout=5)
    print('\n=== ICT SIGNALS ===')
    print(f'Status Code: {response.status_code}')
    if response.status_code == 200:
        signals = response.json()
        print(f'Active Signals: {len(signals)}')
        for signal in signals[:3]:
            print(f'- {signal.get("symbol", "N/A")} | Score: {signal.get("score", "N/A")} | Action: {signal.get("action", "N/A")}')
    else:
        print(f'Error: {response.text}')
except Exception as e:
    print(f'ICT Signals Error: {e}')

try:
    # Current Positions
    response = requests.get('http://localhost:8001/positions', timeout=5)
    print('\n=== CURRENT POSITIONS ===')
    print(f'Status Code: {response.status_code}')
    if response.status_code == 200:
        positions = response.json()
        print(f'Open Positions: {len(positions)}')
        total_profit = 0
        for pos in positions[:5]:
            profit = pos.get('profit', 0)
            total_profit += profit
            print(f'- {pos.get("symbol", "N/A")} | Volume: {pos.get("volume", "N/A")} | Profit: ${profit:.2f}')
        print(f'Total Profit: ${total_profit:.2f}')
    else:
        print(f'Error: {response.text}')
except Exception as e:
    print(f'Positions Error: {e}') 