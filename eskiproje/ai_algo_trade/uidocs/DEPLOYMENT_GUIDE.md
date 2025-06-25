# AI Algo Trade – Deployment Guide

This document details how to deploy **ai_algo_trade** to a production environment using **Docker Compose**.

---

## 1. Architecture Overview

```
┌────────────┐   443/80   ┌──────────────┐
│   Nginx    │ ─────────▶ │ Node Proxy   │ (8081)
│ (Reverse   │            │   Express    │
│  Proxy)    │            └────┬─────────┘
└────────────┘                 │ HTTP JSON
        ▲                      ▼
        │               ┌──────────────┐
        │               │  Backend API │ (8001)
        │               │   FastAPI    │
        │               └────┬─────────┘
        │                     │ gRPC / IPC
        │                     ▼
        │               ┌──────────────┐
        │               │   MT5 Term.  │ (Win32)
        │               └──────────────┘
```

---

## 2. Build Images

```bash
# Backend
docker build -t ai-algo-backend:latest backend/

# Frontend + Proxy (multi-stage build)
docker build -t ai-algo-web:latest .
```

MT5 terminal requires a **Windows** container (`services/mt5_service/`).

---

## 3. Environment Variables

Create `docker/.env.prod`:

```ini
API_KEY=change_me
REDIS_URL=redis://redis:6379/0
DATABASE_URL=postgresql+asyncpg://ai_algo:secure@postgres:5432/ai_algo
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
      POSTGRES_DB: ai_algo
      POSTGRES_USER: ai_algo
      POSTGRES_PASSWORD: secure
    volumes: [pg-data:/var/lib/postgresql/data]

  redis:
    image: redis:7-alpine
    command: ["redis-server", "--appendonly", "yes"]

  backend:
    image: ai-algo-backend:latest
    env_file: docker/.env.prod
    ports: ["8001:8001"]

  proxy:
    image: ai-algo-web:latest
    env_file: docker/.env.prod
    command: ["node", "services/api/api-server-8081.js"]
    ports: ["8081:8081"]

  frontend:
    image: ai-algo-web:latest
    env_file: docker/.env.prod
    command: ["node", "apps/web/server.js"]
    ports: ["3000:3000"]

  mt5:
    build: services/mt5_service  # Windows container
    env_file: docker/.env.prod
    ports: ["1950:1950"]

volumes:
  pg-data:
```

Start stack:
```bash
docker compose -f docker-compose.prod.yml up -d
```

---

## 5. CI/CD (GitHub Actions)

`.github/workflows/deploy.yml` steps:
1. Build images.
2. Push to `ghcr.io/your-org/ai-algo/*`.
3. SSH into server & `docker compose pull && docker compose up -d`.

Add secret `PROD_SSH_KEY` to repository settings.

---

## 6. Monitoring

* **Prometheus + Grafana** – `/metrics` endpoint.
* **Loki** – Docker log aggregation.
* **Sentry** – Error tracking (set `SENTRY_DSN`).
* **Healthchecks.io** – External uptime probe hitting `/status`.

---

## 7. Rollback

```bash
docker compose -f docker-compose.prod.yml up -d --no-deps backend@previous proxy@previous frontend@previous
```

Keep at least **two tags** (`latest`, `previous`) for each service.

---

## 8. Security Hardening

1. Enforce TLS 1.3 in Nginx reverse proxy.
2. Enable rate-limiting (`express-rate-limit`, `slowapi`).
3. Rotate MT5 & DB credentials quarterly.
4. Enable Vault-backed secrets (planned Q4-2025).

---

Your platform is now production-ready! 🎉 