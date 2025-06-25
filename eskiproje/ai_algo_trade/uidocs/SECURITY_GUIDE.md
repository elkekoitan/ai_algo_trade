# AI Algo Trade – Security Guide

This document outlines the security posture and best practices for **ai_algo_trade**.

---

## 1. Threat Model

* API key leakage → unauthorized trades
* CSRF / XSS against proxy / dashboard
* Credential theft (MT5, DB, Redis)
* Insider code abuse
* Supply-chain attacks (npm / pip)

---

## 2. Authentication & Authorization

| Layer | Method |
|-------|--------|
| Proxy (Express) | `X-API-KEY` header + rate limiting |
| Backend (FastAPI) | OAuth2 bearer tokens (planned) |
| Frontend | Secure, `httpOnly` cookies |

Enable **CSRF** middleware (`csurf`) in proxy.

---

## 3. Secrets Management

1. Local dev – `.env` (ignored in git).
2. CI/CD – GitHub Secrets.
3. Production – Docker `--env-file` + Vault (planned).

Rotate secrets every 90 days.

---

## 4. Data Encryption

* TLS 1.3 on Nginx ingress
* Redis TLS (`tls-server-cert.pem`)
* Postgres `sslmode=require`

---

## 5. Dependency Scanning

* Python – `pip-audit` (CI step)
* Node – `npm audit --production`
* Dependabot weekly alerts

---

## 6. Secure Coding Checklist

- [x] No `eval()` / dynamic SQL
- [x] Parameterized queries (SQLAlchemy)
- [x] Helmet + CSP headers in proxy
- [x] CSRF tokens for non-GET endpoints
- [x] `@typescript-eslint/no-explicit-any` enforced

---

## 7. Incident Response

1. Detect (Sentry alert / Prometheus anomaly)
2. Contain (`AUTO_TRADING_ENABLED=false`)
3. Remediate (patch & redeploy ≤ 8 h)
4. Post-mortem within 48 h (template in `docs/incident_template.md`)

Contact: security@ai-algo.io 