# Local Setup Guide

This document walks you through setting up the **ICT Ultra Platform** on a development workstation.

---

## 1. System Requirements

| Component | Recommended Version |
|-----------|---------------------|
| OS | Windows 10 / 11, macOS 12+, Ubuntu 22.04 LTS |
| CPU | 4-core 3.0 GHz+ |
| RAM | 16 GB |
| Disk | 5 GB free (excl. MT5 data) |
| Node.js | ≥ 18.x LTS |
| pnpm | ≥ 8.x |
| Python | 3.13.1 |
| Docker (optional) | 24.x |
| Git | ≥ 2.40 |

> On Windows, **Git Bash** or **WSL 2** is recommended for smooth shell scripts.

---

## 2. Clone the Repository

```bash
git clone https://github.com/your-org/ict-ultra-platform.git
cd ict-ultra-platform
```

---

## 3. Node & pnpm Workspace

```bash
corepack enable  # enables pnpm if not already
pnpm i  # installs all workspaces under ICT_Ultra_Platform/
```

`pnpm` workspaces handle **frontend**, **proxy**, and shared **UI packages**.

---

## 4. Python Virtual Environment

```bash
python -m venv .venv
source .venv/Scripts/activate  # Linux/macOS: source .venv/bin/activate
pip install -r backend/requirements.txt
```

Packages include **FastAPI**, **SQLAlchemy**, **Redis**, **MetaTrader5**.

---

## 5. Environment Variables

Copy the example files and adjust where needed.

```bash
cp backend/env.example backend/.env
cp ICT_Ultra_Platform/env.example ICT_Ultra_Platform/.env
```

Key variables:

| Variable | Example | Description |
|----------|---------|-------------|
| `MT5_LOGIN` | `25201110` | Demo account login |
| `MT5_PASSWORD` | `s3cr3t` | Demo account password |
| `MT5_SERVER` | `Tickmill-Demo` | Broker server name |
| `REDIS_URL` | `redis://localhost:6379/0` | Redis connection URI |
| `DATABASE_URL` | `sqlite+aiosqlite:///ict_ultra.db` | SQLAlchemy DB URL |

---

## 6. Start Services (Dev Mode)

```bash
# 1️⃣ Backend (FastAPI)
cd backend
python production_api_server.py &

# 2️⃣ Proxy (Node/Express)
cd ../ICT_Ultra_Platform
node api-server-8081.js &

# 3️⃣ Frontend (Next.js)
cd apps/web
pnpm dev &
```

Verify:
```bash
curl http://localhost:8001/status   # backend
curl http://localhost:8081/api/status  # proxy
open http://localhost:3000           # frontend
```

---

## 7. Helpful Scripts

| Script | Location | Purpose |
|--------|----------|---------|
| `start_platform.bat` | project root | One-click Windows startup |
| `scripts/robust-start.js` | ICT_Ultra_Platform/scripts | Cross-platform startup & health-check |
| `scripts/auto-recovery.js` | ICT_Ultra_Platform/scripts | Auto-restart crashed processes |

---

## 8. IDE Recommendations

* **VS Code** with extensions: _Python_, _Pylance_, _ESLint_, _Prettier_, _Tailwind CSS Intellisense_.
* Use **devcontainers** (coming soon) for zero-setup environment.

---

## 9. Next Steps

1. Complete the [MT5 Integration](MT5_INTEGRATION_GUIDE.md).  
2. Run the [Testing Suite](TESTING_GUIDE.md).  
3. Read the [Development Guide](DEVELOPMENT_GUIDE.md) to start contributing. 