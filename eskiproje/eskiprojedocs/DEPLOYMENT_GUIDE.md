# Deployment Guide

This document describes how to deploy the **ICT Ultra Platform** to a production environment. The recommended approach uses **Docker Compose** with separate containers for the backend, proxy, frontend, Redis, and the MetaTrader&nbsp;5 terminal (Windows container).

---

## 1. Production Topology

```
┌──────────────────┐       443/80       ┌──────────────────┐
│    Nginx        │  ───────────────▶  │  Node Proxy      │ (8081)
│  (Reverse Proxy)│                   │  (Express.js)    │
└──────────────────┘                   └─────────▲────────┘
            ▲                                         │ HTTP JSON
            │                                         │
            │                                         ▼
     ┌──────┴──────┐                       ┌──────────────────┐
     │  Frontend   │  (Next.js 3000)       │  Backend API     │ (8001)
     │ (SSR + SPA) │                       │  (FastAPI)       │
     └─────────────┘                       └─────────▲────────┘
                                                   │ gRPC / IPC
                                                   ▼
                                           ┌──────────────────┐
                                           │   MT5 Terminal   │ (Win32)
                                           └──────────────────┘
```

---

## 2. Build Docker Images

```bash
# From the project root
# 1️⃣ Backend
cd backend
docker build -t ict-ultra-backend:latest .

# 2️⃣ Proxy & Frontend (multi-stage)
cd ../ICT_Ultra_Platform
docker build -t ict-ultra-web:latest .
```

The **MT5 terminal** requires a separate **Windows container**. See `services/mt5_service/Dockerfile` for base image `mcr.microsoft.com/windows/servercore:ltsc2022`.

---

## 3. Environment Variables (prod)

Create `docker/.env.prod`:

```ini
API_KEY=change_me
REDIS_URL=redis://redis:6379/0
DATABASE_URL=postgresql+asyncpg://ict_ultra:secure@postgres:5432/ict_ultra
# MT5 creds
MT5_LOGIN=25201110
MT5_PASSWORD=prod_password
MT5_SERVER=Tickmill-Demo
```

---

## 4. Docker Compose

`docker-compose.prod.yml` (excerpt):
```yaml
version: '3.9'
services:
  postgres:
    image: postgres:16
    environment:
      POSTGRES_DB: ict_ultra
      POSTGRES_USER: ict_ultra
      POSTGRES_PASSWORD: secure
    volumes:
      - pg-data:/var/lib/postgresql/data

  redis:
    image: redis:7-alpine
    command: ["redis-server", "--appendonly", "yes"]

  backend:
    image: ict-ultra-backend:latest
    env_file: docker/.env.prod
    ports: ["8001:8001"]

  proxy:
    image: ict-ultra-web:latest
    env_file: docker/.env.prod
    command: ["node", "api-server-8081.js"]
    ports: ["8081:8081"]

  frontend:
    image: ict-ultra-web:latest
    env_file: docker/.env.prod
    command: ["node", "apps/web/server.js"]
    ports: ["3000:3000"]

  mt5:
    build: ./services/mt5_service  # Windows container
    env_file: docker/.env.prod
    ports: ["1950:1950"]  # WebSocket bridge

volumes:
  pg-data:
```

Start stack:
```bash
docker compose -f docker-compose.prod.yml up -d
```

---

## 5. Continuous Deployment (GitHub Actions)

`.github/workflows/deploy.yml` (key steps):
1. Build backend & web images.
2. Push to `ghcr.io/your-org/ict-ultra/*`.
3. SSH into server & `docker compose pull && docker compose up -d`.

Add secret `PROD_SSH_KEY` to repository settings.

---

## 6. Monitoring & Logging

* **Prometheus + Grafana**: scrape `/metrics` from backend.
* **Loki**: aggregate container logs (`docker-compose` supports sidecar driver).
* **Sentry**: capture JavaScript & Python exceptions (see ENV vars `SENTRY_DSN`).
* **Healthchecks.io**: external uptime probe hitting `/status`.

---

## 7. Zero-Downtime Rollback

```bash
docker compose -f docker-compose.prod.yml rollback  # plugin required
# OR manually
docker compose ps --format json > previous.json
docker compose up -d --no-deps backend:previous web:previous
```

Keep at least **two tagged images** (`latest`, `prev`) for each service.

---

## 8. Security Hardening

1. Enable **firewall** (allow 80/443, drop others).
2. Use **Let's Encrypt** for TLS termination in Nginx.
3. Enforce **Content Security Policy** in frontend (already configured).
4. Rotate OAuth & MT5 passwords quarterly.

---

## 9. Disaster Recovery

* Nightly **Postgres dumps** to off-site S3 bucket.
* **Redis AOF** persisted & shipped via `redis-s3` cronjob.
* **MT5 terminal data** backed up via Windows Task Scheduler.

---

Your platform is now production-ready. 🎉 