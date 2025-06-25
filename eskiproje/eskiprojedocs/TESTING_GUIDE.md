# Testing Guide

Quality is non-negotiable. This guide describes how to run and extend tests for the **ICT Ultra Platform**.

---

## 1. Test Pyramid

| Layer | Tooling | Target |
|-------|---------|--------|
| Unit | `pytest`, `pytest-asyncio`, `jest` | Pure functions, React components |
| Integration | `httpx`, `pytest-docker` | API endpoints, DB interactions |
| End-to-End | `Playwright`, `Cypress` | Full stack (browser ↔ backend ↔ MT5) |
| Load/Stress | `locust` | `/ict/signals`, order execution |

---

## 2. Python Tests

```bash
# run all
pytest -q

# run single file
pytest tests/test_trading_engine.py -q

# show coverage
pytest --cov=backend/src/ict_ultra --cov-report=term-missing
```

### Fixtures
* `redis_client` – creates ephemeral Redis instance.
* `db_session` – rolls back DB after each test.
* `mt5_mock` – optional stub that mimics MetaTrader when `LIVE_MT5=false`.

---

## 3. Frontend Tests

```bash
pnpm test                 # Jest + React Testing Library
pnpm test --watch  # interactive mode
```

Snapshot tests live under `apps/web/src/__snapshots__/`.

---

## 4. End-to-End (E2E) Tests

```bash
# Requires services running (see Setup Guide)
# Runs full browser automation across 3 viewports
pnpm playwright test
```

Key flows covered:
1. User login & dashboard load.
2. Live signal list refresh.
3. One-click trade execution, verify MT5 order).

---

## 5. Continuous Integration

* GitHub Actions workflow `ci.yml` runs on each push:
  1. Install deps
  2. Lint & type-check
  3. Unit + Integration tests
  4. Build Docker images (dry-run)

Coverage must stay ≥ **90 %** for backend *and* frontend to merge.

---

## 6. Writing New Tests

1. Follow **AAA pattern** (Arrange, Act, Assert).
2. Mock external services (Redis, MT5) with `pytest-mock` unless performing E2E.
3. Prefer **factories** (`factory_boy`) for model setup.
4. Keep test names descriptive: `test_<function>_<scenario>`.

---

## 7. Debugging Failing Tests

* Run with `-vv` for verbose logs.
* Add `--log-cli-level=INFO` to see app logs.
* Use `pytest-interactive` to drop into REPL on failure.

---

## 8. Load Testing

```bash
locust -f tests/locustfile.py --host http://localhost:8081
```

Monitor latency, throughput, error rate; adjust autoscaling thresholds.

---

Keep tests green. Your future self will thank you. 