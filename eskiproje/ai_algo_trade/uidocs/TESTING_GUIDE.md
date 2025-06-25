# AI Algo Trade – Testing Guide

Quality is mandatory. This guide explains how to run and extend tests for **ai_algo_trade**.

---

## 1. Test Pyramid

| Layer | Tooling | Target |
|-------|---------|--------|
| Unit | `pytest`, `pytest-asyncio`, `jest` | Pure functions, React components |
| Integration | `httpx`, `pytest-docker` | API endpoints, DB interactions |
| End-to-End | `Playwright` | Full stack (browser ↔ proxy ↔ backend ↔ MT5) |
| Load | `locust` | Signal engine, order execution |

---

## 2. Python Tests

```bash
pytest -q                   # run all tests
pytest tests/test_orders.py # run a single file
pytest --cov=backend/src/ai_algo --cov-report=term-missing
```

Fixtures:
* `redis_client` – spins up Redis in Docker.
* `db_session` – transactional DB session rolled back after each test.
* `mt5_stub` – fakes MetaTrader calls when `LIVE_MT5=false`.

---

## 3. Frontend Tests

```bash
pnpm test           # Jest + React Testing Library
pnpm test --watch   # interactive mode
```

Snapshots reside in `apps/web/src/__snapshots__/`.

---

## 4. End-to-End (E2E)

```bash
# Ensure all services are running (see Setup Guide)
pnpm playwright test
```

Flows covered:
1. Dashboard loads & shows live account info.
2. Signal list refresh & score filtering.
3. Execute trade → Verify position via backend.

---

## 5. Continuous Integration

GitHub Actions `ci.yml` runs on push:
1. Install deps.
2. Lint & type-check.
3. Unit + integration tests.
4. Build Docker images (dry-run).

Coverage thresholds:
* Backend ≥ **90 %**
* Frontend ≥ **90 %**

---

## 6. Writing New Tests

* Follow **AAA** pattern (Arrange, Act, Assert).
* Mock external services unless E2E.
* Use factories (`factory_boy`) for models.
* Name tests `test_<function>_<scenario>`.

---

## 7. Load Testing

```bash
locust -f tests/locustfile.py --host http://localhost:8081
```

Monitor latency, throughput, error rate.

---

Keep tests green; your future self will thank you. 