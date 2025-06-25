# AI Algo Trade – API Reference

The OpenAPI spec lives at `/docs` (Swagger UI) once the backend is running. This markdown provides a quick index.

---

## Base URLs

| Environment | URL |
|-------------|-----|
| Local Backend | `http://localhost:8001` |
| Local Proxy  | `http://localhost:8081/api` |
| Production   | `https://api.ai-algo.io` |

All endpoints require header `X-API-KEY: <your-key>`.

---

## 1. Health & Status

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/status` | Service health, MT5 ping |
| GET | `/metrics` | Prometheus metrics |

---

## 2. Market Data

| Method | Endpoint | Params | Description |
|--------|----------|--------|-------------|
| GET | `/market-data/tick` | `symbol` | Latest tick |
| GET | `/market-data/candles` | `symbol`, `timeframe`, `limit` | OHLC candles |

---

## 3. Signals

| Method | Endpoint | Params | Description |
|--------|----------|--------|-------------|
| GET | `/signals` | `min_score`, `symbols`, `timeframes` | Retrieve ICT/AI signals |
| POST | `/signals/ack` | JSON `{id}` | Mark signal processed |

---

## 4. Trading

| Method | Endpoint | Body | Description |
|--------|----------|------|-------------|
| POST | `/trading/order` | `symbol`, `type`, `volume`, `tp`, `sl`, `comment` | Place order |
| GET | `/trading/positions` | — | Open positions |
| DELETE | `/trading/positions/{ticket}` | — | Close position |

---

## 5. Account

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/account/info` | Balance, equity, margin |
| GET | `/account/history` | Closed orders & P/L |

---

For full schemas visit Swagger UI.
