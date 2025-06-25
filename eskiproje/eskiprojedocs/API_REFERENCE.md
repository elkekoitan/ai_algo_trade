# API Reference

The complete, auto-generated OpenAPI specification lives at **`/docs`** (Swagger UI) once the backend is running. This markdown provides a quick index of the most common endpoints.

---

## Base URLs

| Environment | URL |
|-------------|-----|
| Local Backend | `http://localhost:8001` |
| Local Proxy  | `http://localhost:8081/api` |
| Production   | `https://api.ict-ultra.io` |

> All endpoints require the header `X-API-KEY: <your-key>`.

---

## 1. Health & Status

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/status` | Service health & MT5 ping |
| GET | `/metrics` | Prometheus family metrics |

---

## 2. Market Data

| Method | Endpoint | Query Params | Description |
|--------|----------|-------------|-------------|
| GET | `/market-data/tick` | `symbol` | Latest tick data |
| GET | `/market-data/candles` | `symbol`, `timeframe`, `limit` | OHLC candles |

---

## 3. ICT Signals

| Method | Endpoint | Query Params | Description |
|--------|----------|-------------|-------------|
| GET | `/ict/signals` | `min_score`, `symbols`, `timeframes` | Retrieve ranked signals |
| POST | `/ict/signals/ack` | JSON `{id}` | Mark signal as processed |

---

## 4. Trading

| Method | Endpoint | Body | Description |
|--------|----------|------|-------------|
| POST | `/trading/order` | `symbol`, `type`, `volume`, `tp`, `sl`, `comment` | Place market/limit order |
| GET | `/trading/positions` | — | Open positions |
| DELETE | `/trading/positions/{ticket}` | — | Close position |

---

## 5. Account

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/account/info` | Balance, equity, margin |
| GET | `/account/history` | Closed orders & P/L |

---

For exhaustive schemas (request/response), visit **Swagger UI** at `/docs` or download the raw JSON at `/openapi.json`. 