# MetaTrader&nbsp;5 Integration Guide

> **Version**: Platform v2025.6 | Last updated: 2025-06-19

This guide explains how to link the **ICT Ultra Platform** to a live **MetaTrader 5** (MT5) terminal so that the backend can pull real-time market data and execute trades automatically.

---

## 1. Prerequisites

| Requirement | Version / Value | Notes |
|-------------|-----------------|-------|
| Operating System | Windows 10 (build 19045) / Windows Server 2019 | MT5 terminal is Windows-only. Use Wine or a Windows VM on Linux/macOS. |
| MetaTrader 5 Terminal | **≥ 5100** | Needed for built-in **Git** integration & WebSocket improvements. |
| MT5 Demo Account | Login `25201110` (Tickmill-Demo) | Replace with your own if desired. |
| Python | **3.13.1** | Matches the platform backend version. |
| `MetaTrader5` Python package | **5.0.5120** | Installed via `pip install MetaTrader5==5.0.5120`. |
| ICT Ultra Platform backend | Running on port `8001` | See [`SETUP_GUIDE.md`](SETUP_GUIDE.md). |

---

## 2. Terminal Installation & Configuration

1. **Download MT5** from the broker (e.g., Tickmill) or [MetaQuotes](https://www.metatrader5.com).  
2. Install to `C:\Program Files\MetaTrader 5` (default).  
3. Launch MT5 and **log in** with the demo credentials:
   * Login: `25201110`
   * Password: _provided by broker_
   * Server: `Tickmill-Demo`
4. Enable **Algo Trading**: `Tools → Options → Expert Advisors → Allow automated trading`.
5. Disable UAC prompts by **running MT5 as Administrator** (optional but prevents IPC permission issues).

---

## 3. Python Environment

Inside the platform root:

```bash
python -m venv .venv
source .venv/Scripts/activate  # PowerShell: . .venv\Scripts\Activate.ps1
pip install -r requirements.txt  # includes MetaTrader5==5.0.5120
```

> The backend module `backend/src/ict_ultra/modules/mt5_integration/services/connection.py` wraps the MetaTrader5 package behind an async interface.

---

## 4. Service Configuration

Open `backend/.env` (or copy from `env.example`) and set:

```ini
# MT5 CONNECTION
MT5_LOGIN=25201110
MT5_PASSWORD=YOUR_PASSWORD_HERE
MT5_SERVER=Tickmill-Demo
MT5_PATH=C:\\Program Files\\MetaTrader 5\\terminal64.exe
```

If MT5 is installed elsewhere, adjust `MT5_PATH` accordingly.

### Redis & Database

The MT5 integration relies on the event bus and cache. Make sure Redis (default `localhost:6379`) and the Postgres/SQLite DB are running before you start the backend.

---

## 5. Running the MT5 Service

```bash
# In a dedicated shell
cd backend
python production_api_server.py
```

On startup you should see log lines similar to:
```
[mt5_connection] Connected to MetaTrader 5 build 5100 (Tickmill-Demo | ping=12ms)
[trading_engine] Equity: $2 609 337.52 | 64 open positions loaded
```

The service exposes endpoints via **FastAPI**:

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/status` | GET | Health-check, MT5 ping, account balance |
| `/positions` | GET | List open orders & positions |
| `/order` | POST | Place a trade (`symbol`, `type`, `volume`, `tp`, `sl`, `comment`) |

See [`API_REFERENCE.md`](API_REFERENCE.md) for full Swagger docs.

---

## 6. Testing the Connection

```bash
python test_api_status.py  # checks /status and prints account info
python test_order_execution.py  # executes a 0.01 lot EURUSD market buy as dry-run
```

Alternatively use **cURL**:
```bash
curl http://localhost:8001/status
```

Expected JSON:
```json
{
  "status": "ok",
  "account": {
    "login": 25201110,
    "balance": 2609337.52,
    "equity": 2609337.52,
    "margin": 0.0
  },
  "mt5_build": 5100
}
```

---

## 7. Troubleshooting

| Symptom | Possible Cause | Fix |
|---------|----------------|-----|
| `account_info() failed` | Wrong credentials or server offline | Re-enter login & password; check broker status. |
| `Permission denied` spawning terminal | MT5 not run as admin | Exit MT5 and restart **as Administrator**. |
| `ERR_TRADE_DISABLED` when placing order | Market closed or trading disabled for the symbol | Wait for market open; check symbol permissions. |
| MT5 terminal freezes | Running in Wine/VM with low RAM | Allocate ≥ 4 GB RAM and enable 3D acceleration. |

---

## 8. Next Steps

1. **Enable Live Trading**: switch from demo to live account once strategy is validated.
2. **Git-Sync EAs**: explore MT5 build 5100's built-in Git client to sync custom EAs located in `ICT_Ultra_Platform/mt5_integration/`.
3. **Monitor Performance**: use `continuous_performance_monitor.py` (re-create if missing) to track P&L & drawdown in real-time.

---

Made with ❤️ by the ICT Ultra Platform team. 