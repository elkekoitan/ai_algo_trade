# Development Guide

Welcome, contributor! This guide explains how to navigate, extend, and debug the **ICT Ultra Platform**.

---

## 1. Repository Layout

```
backend/                         # Python codebase
└── src/ict_ultra/              #   ├─ core/ – cross-cutting utilities
                                #   ├─ modules/ – domain-driven bounded contexts
ICT_Ultra_Platform/             # Monorepo for Node workspaces
└── apps/web/                   #   Next.js dashboard
└── services/api/               #   Express proxy + websocket hub
```

See [`ARCHITECTURE.md`](../backend/docs/ARCHITECTURE.md) for a deeper explanation.

---

## 2. Branching Strategy

* `main` – stable, deployable at all times.  
* `develop` – integration branch, nightly builds.  
* `feat/<scope>` – feature branches (merge → `develop`).  
* `hotfix/<issue>` – critical fixes (merge into `main` & `develop`).

> Use **Conventional Commits** (`feat:`, `fix:`, `docs:`) – auto version bump & changelog.

---

## 3. Coding Standards

| Language | Formatter | Linter |
|----------|-----------|--------|
| Python | `black` | `ruff`, `mypy` |
| TypeScript | `prettier` | `eslint`, `tsc --noEmit` |
|

Run all checks:
```bash
pnpm lint         # TypeScript & TSX
pnpm format       # prettier write
poetry run ruff . # Python linting
```

---

## 4. Database Migrations

We use **Alembic** (Python) for Postgres migrations.

```bash
alembic revision --autogenerate -m "add trades table"
alembic upgrade head
```

For SQLite dev DB, migrations run automatically on startup.

---

## 5. Adding a New Module

1. Create directory `backend/src/ict_ultra/modules/<module_name>/` with sub-folders `api`, `application`, `domain`, `infrastructure`, `interfaces`.
2. Define `domain/models.py` with Pydantic & SQLAlchemy hybrid models.
3. Implement use-cases inside `application/services.py`.
4. Expose REST endpoints via `api/router.py` and wire in `ict_ultra/api/__init__.py`.
5. Add unit tests under `backend/tests/`.
6. Update docs & OpenAPI tags.

---

## 6. Debugging Tips (Backend)

* **VS Code launch**: `.vscode/launch.json` includes a `FastAPI` config.
* Use `watchgod` hot reload: `uvicorn ict_ultra.main:app --reload`.
* Toggle `DEBUG=true` in `.env` to enable verbose logging.

---

## 7. Debugging Tips (Frontend)

* `pnpm dev` enables React Fast Refresh and full HMR.
* Use Chrome DevTools + Redux DevTools (for Zustand store inspection).
* Enable `NEXT_PUBLIC_API_MOCKING=true` to stub API in Storybook.

---

## 8. Testing

See [Testing Guide](TESTING_GUIDE.md) for full details, but in short:

```bash
pytest -q  # Python unit tests
pnpm test  # Frontend Jest + React Testing Library
```

---

## 9. Committing & Pushing

```bash
git add .
git commit -m "feat(signals): add divergence detector"
git push origin feat/signals-divergence
```

CI will run lint, type-check, tests, and build docker images. Merge via PR once green.

---

Happy coding! 