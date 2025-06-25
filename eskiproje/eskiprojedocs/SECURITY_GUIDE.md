# Security Guide

The ICT Ultra Platform handles real trading capital. Security therefore sits at the core of every feature.

---

## 1. Threat Model

* API key leakage (client → proxy)  
* Unauthorized order execution  
* Credential theft (MT5, Postgres, Redis)  
* Insider code abuse  
* Supply-chain attacks via npm/pip  

---

## 2. Authentication & Authorization

| Layer | Method |
|-------|--------|
| Gateway/Proxy | `X-API-KEY` header validated against Redis cache |
| Backend | OAuth2 bearer tokens (planned) |
| Frontend | Stored in `httpOnly` secure cookies |

Rate-limit enforced by `express-rate-limit` (proxy) & `slowapi` (backend).

---

## 3. Secrets Management

1. **Local Dev**: `.env` files (excluded via `.gitignore`).
2. **CI/CD**: GitHub Actions **Secrets & Variables**.
3. **Production**: Docker `--env-file` + **HashiCorp Vault** integration (2025-Q4).

Rotate all passwords every 90 days.

---

## 4. Data Encryption

* TLS 1.3 enforced on Nginx reverse proxy (ACME certificates).  
* Redis protected by `tls-server-cert.pem` & `tls-server-key.pem`.  
* PostgreSQL uses `sslmode=require`.

---

## 5. Dependency Scanning

* Python – `pip-audit` on CI.  
* Node – `npm audit --production`.  
* GitHub Dependabot alerts reviewed weekly.

---

## 6. Secure Coding Checklist

- [x] No `eval()` or dynamic SQL.
- [x] Parameterized DB queries (SQLAlchemy core).
- [x] CSRF tokens for non-idempotent endpoints.
- [x] Content-Security-Policy & Helmet in Express.
- [x] `@typescript-eslint/no-explicit-any` enforced.

---

## 7. Incident Response

1. **Detect** via Sentry alert or Prometheus anomaly.  
2. **Contain** by disabling `AUTO_TRADING_ENABLED` flag.  
3. **Remediate** patch & redeploy within SLA (8 hours).  
4. **Post-mortem** within 48 hours (template in `docs/incident_template.md`).

---

For vulnerabilities, email **security@ict-ultra.io** or open a private GitHub security advisory. 