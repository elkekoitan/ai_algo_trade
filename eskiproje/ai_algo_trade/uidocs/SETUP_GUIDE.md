# AI Algo Trade – Local Setup Guide

This guide walks you through setting up the **ai_algo_trade** project on a development machine.

---

## 1. System Requirements

| Component | Recommended Version |
|-----------|---------------------|
| OS | Windows 10/11, macOS 12+, Ubuntu 22.04 LTS |
| CPU | 4-core 3.0 GHz+ |
| RAM | 16 GB |
| Disk | 5 GB free (excluding MT5 data) |
| Python | 3.13.1 |
| Node.js | ≥ 18.x LTS |
| pnpm | ≥ 8.x (via `corepack`) |
| Docker (optional) | 24.x |
| Git | ≥ 2.40 |

> On Windows, **Git Bash** or **WSL 2** is preferred for shell scripts.

---

## 2. Clone the Repository

```bash
git clone https://github.com/your-org/ai_algo_trade.git
cd ai_algo_trade
```

---

## 3. Python Virtual Environment

```bash
python -m venv .venv
source .venv/Scripts/activate      # macOS/Linux: source .venv/bin/activate
pip install -r requirements.txt    # includes FastAPI, MetaTrader5, SQLAlchemy
```

---

## 4. Node & pnpm Workspace (Frontend / Proxy)

```bash
corepack enable        # enables pnpm if not already
pnpm i                 # installs workspaces under apps/web & services/
```

---

## 5. Environment Variables

Copy the example files and adjust values where necessary.

```bash
cp env.example .env
cp apps/web/.env.example apps/web/.env
```

Key variables:

| Variable | Example | Description |
|----------|---------|-------------|
| `MT5_LOGIN` | `25201110` | Demo account login |
| `MT5_PASSWORD` | `your_password` | Demo account password |
| `MT5_SERVER` | `Tickmill-Demo` | Broker server name |
| `REDIS_URL` | `redis://localhost:6379/0` | Redis connection URI |
| `DATABASE_URL` | `sqlite+aiosqlite:///ai_algo_trade.db` | SQLAlchemy DB URL |
| `API_KEY` | `changeme` | Gateway authentication key |

---

## 6. Start Services (Dev Mode)

```bash
# 1️⃣ Backend (FastAPI)
python backend/production_api_server.py &

# 2️⃣ Proxy (Node/Express)
node services/api/api-server-8081.js &

# 3️⃣ Frontend (Next.js)
cd apps/web
pnpm dev &
```

Verify endpoints:
```bash
curl http://localhost:8001/status       # backend
curl http://localhost:8081/api/status   # proxy
open http://localhost:3000              # frontend
```

---

## 7. Helpful Scripts

| Script | Purpose |
|--------|---------|
| `start-platform.bat` | One-click Windows startup |
| `scripts/robust-start.js` | Cross-platform startup & health-check |
| `scripts/auto-recovery.js` | Auto-restart crashed services |

---

## 8. IDE Recommendations

* **VS Code** with Python, Pylance, ESLint, Prettier, Tailwind CSS extensions.
* Use **devcontainers** (coming soon) for zero-setup environments.

---

## 9. Next Steps

1. Complete the [MT5 Integration Guide](MT5_INTEGRATION_GUIDE.md).  
2. Run the [Testing Guide](TESTING_GUIDE.md).  
3. Read the [Development Guide](DEVELOPMENT_GUIDE.md) to start contributing. 