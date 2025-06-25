# AI Algo Trade – Development Guide

Welcome, contributor! This guide explains how to navigate, extend, and debug the **ai_algo_trade** codebase.

---

## 1. Repository Layout

```
ai_algo_trade/
├── backend/                 # Python services & trading engine
│   ├── src/ai_algo/        #   • core, modules, utils
│   └── tests/              #   • pytest suite
├── services/api/            # Node/Express proxy + websocket hub
├── apps/web/                # Next.js dashboard
├── scripts/                 # Startup & recovery scripts
└── docs/                    # Project documentation (this folder)
```

See [`ARCHITECTURE.md`](ARCHITECTURE.md) for deeper details.

---

## 2. Branching Strategy

* `main` – always deployable
* `develop` – integration branch
* `feat/<scope>` – feature branches (merge → `develop`)
* `hotfix/<issue>` – critical fixes (merge into `main` & `develop`)

> Use **Conventional Commits** (`feat:`, `fix:`, `docs:`) – automatically updates CHANGELOG.

---

## 3. Coding Standards

| Language | Formatter | Linter | Type Checker |
|----------|-----------|--------|--------------|
| Python   | `black`   | `ruff` | `mypy` |
| TypeScript | `prettier` | `eslint` | `tsc --noEmit` |

Run all checks:
```bash
pnpm lint          # TS/TSX linting
pnpm format        # prettier write
ruff .             # Python linting
mypy backend/src   # Static typing
```

---

## 4. Database Migrations

We use **Alembic**.
```bash
alembic revision --autogenerate -m "add trades table"
alembic upgrade head
```
SQLite dev DB migrations run on startup.

---

## 5. Adding a New Module

1. `backend/src/ai_algo/modules/<module_name>/` with `api`, `application`, `domain`, `infrastructure`, `interfaces` folders.
2. Define Pydantic/SQLAlchemy models in `domain/models.py`.
3. Implement business logic in `application/services.py`.
4. Expose REST endpoints via `api/router.py` and wire in `ai_algo/api/__init__.py`.
5. Add unit tests.
6. Update OpenAPI tags & docs.

---

## 6. Debugging Tips

Backend:
* Start with `uvicorn ai_algo.main:app --reload`.
* Toggle `DEBUG=true` in `.env` for verbose logs.
* Use `--reload-dir` to auto-restart on code change.

Frontend:
* `pnpm dev` enables React Fast Refresh.
* Use Chrome DevTools + React Developer Tools.

---

## 7. Testing

See [Testing Guide](TESTING_GUIDE.md) but quick reference:
```bash
pytest -q               # Python unit tests
pnpm test               # Frontend Jest tests
pnpm playwright test    # End-to-end tests
```

Coverage must stay ≥ 90 % to merge.

---

Happy coding! 🚀 