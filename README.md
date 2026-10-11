# FXMind — GBP/USD Market Analysis

FXMind is a probabilistic market analysis platform designed specifically for **GBP/USD**.

> [!IMPORTANT]
> **ANALYSIS ONLY**: FXMind NEVER executes trades, places broker orders, manages brokerage accounts, or automatically buys/sells anything.

---

## 🌟 Product Capabilities

- **Current GBP/USD Price & Quote**: Real-time bid, ask, spread, 24h high/low, session state.
- **M15 Primary Analysis & H1 Context**: Multi-timeframe trend, RSI, ATR, EMA alignment.
- **Directional Bias**: `BULLISH`, `BEARISH`, or `NEUTRAL` with calibrated probabilities.
- **Market Regime Detection**: `TRENDING`, `RANGING`, `HIGH_VOLATILITY`, or `ILLIQUID`.
- **Calibrated Probabilities**: Raw soft probabilities calibrated using Isotonic Regression.
- **Deterministic Trade Setup**: Entry zone, Stop Loss (SL = 1.0 × ATR), Take Profit (TP = 1.8 × ATR), Risk/Reward ratio.
- **Explicit NO_TRADE Decisions**: First-class status when market edge is weak, news is near, or regime is ranging.
- **Economic Calendar & News Risk Windows**: Automated risk pauses during high-impact news (CPI, NFP, FOMC, BoE).
- **Cross-Market Context**: Real-time correlation tracking across DXY, EUR/USD, USD/JPY, and EUR/GBP.
- **Historical Signal History**: Complete record of past signals and outcome status (`TARGET_HIT`, `STOP_HIT`, `EXPIRED`).
- **Walk-Forward Performance**: Out-of-sample profit factor, Sharpe, Sortino, max drawdown, and win rate.
- **Model Versioning**: Immutable model registry with state machine lifecycle (`TRAINING` → `CANDIDATE` → `VALIDATED` → `PRODUCTION`).
- **Real-Time WebSocket Updates**: Live streaming of market quotes and AI analysis updates.
- **Evidence-Based Explanations**: Feature attribution (SHAP) across Trend, Momentum, Structure, Cross-Market, Volatility, Regime, and News Risk.

---

## 🏗️ Architecture Overview

```
MARKET DATA
  → DATA VALIDATION
  → DATA NORMALIZATION
  → FEATURE ENGINEERING (~100 features)
  → REGIME MODEL
  → DIRECTION MODEL (XGBoost Multiclass)
  → PROBABILITY CALIBRATION (Isotonic)
  → SIGNAL ENGINE (Candidate Gates)
  → RISK/SETUP ENGINE (Deterministic ATR)
  → EXPLANATION ENGINE (SHAP Evidence)
  → SIGNAL JSON CONTRACT
  → FASTAPI REST + WEBSOCKETS
  → NEXT.JS FRONTEND DASHBOARD
```

---

## 💻 Tech Stack

- **Frontend**: Next.js 14 (App Router), TypeScript, Tailwind CSS, Lucide icons, Lightweight Charts, React Query.
- **Backend**: Python 3.11+, FastAPI, Pydantic v2, PyMongo Async.
- **Database**: MongoDB Atlas (the free M0 cluster currently includes 512 MB storage; free database service does not guarantee always-on application hosting).
- **ML Engine**: XGBoost, Scikit-Learn, SciPy, Optuna, SHAP, PyArrow, Pandas, NumPy.

---

## 🚀 Quick Start Guide

### Prerequisites
- Python 3.11+
- Node.js 18+
- A MongoDB Atlas cluster (or another reachable MongoDB deployment)

### 1. Initial Setup
```bash
# Clone the repository
git clone https://github.com/your-org/gbpusd-ai-assistant.git
cd gbpusd-ai-assistant

# Create environment file and add your MongoDB Atlas connection string
cp .env.example .env
```

Set `MONGODB_URI` and `MONGODB_DATABASE` in `backend/.env` or the repository-root `.env`. Get the URI from Atlas **Connect → Drivers**. Add a database user, allow your hosting provider's outbound IP in Atlas Network Access, and URL-encode special characters in the username/password. Do not commit the connection URI. Set `JWT_SECRET_KEY` to a random value of at least 32 characters; for example, generate one with `python -c "import secrets; print(secrets.token_urlsafe(48))"`.

### 2. Running Locally

#### Start Backend:
```bash
cd backend
python -m venv venv
# Windows: venv\Scripts\activate | Unix: source venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

The API intentionally has no SQLite fallback: it will fail startup if `MONGODB_URI` is missing or MongoDB cannot be reached.

For a local MongoDB development instance only, `docker compose up -d mongo` starts MongoDB on `127.0.0.1:27017`. Set `MONGODB_URI=mongodb://localhost:27017` in `backend/.env` to use it. This local container is not an online/24-hour deployment.

#### Start Frontend:
```bash
cd frontend
npm install
npm run dev
```

### 3. Historical Data & Model Training
```bash
cd backend
# Fetch live multi-asset historical data
python scripts/fetch_yfinance_data.py

# Train ensemble ML model with probability calibration
python scripts/retrain_v2.py

# Run backtest validation
python scripts/run_backtest.py --version gbpusd-ensemble-v2.0
```

---

## 🧪 Testing & Verification

```bash
# Run backend tests (MongoDB access is mocked; no Atlas credentials required)
cd backend && python -m pytest tests/ -v

# Typecheck frontend
cd frontend && npm run build
```

### Existing local SQLite data

The previous `backend/data/fxmind.db` file is not deleted or automatically copied. It is about 28.5 MB in this workspace, below Atlas M0's 512 MB storage limit, though actual MongoDB storage also includes indexes and BSON overhead. After setting your Atlas URI, copy existing SQL records (and embed signal reasons) **before first starting the API against Atlas** with `cd backend` then `python scripts/migrate_sqlite_to_mongo.py`. The importer is repeatable, does not overwrite existing MongoDB documents, and does not modify or delete SQLite data. Market-history Parquet files and trained model artifacts remain file-based inputs and are not uploaded automatically.

### Deployment: Render backend and Vercel frontend

The app is maintained in one repository, but the backend and frontend are deployed as separate services:

1. **Deploy the backend to Render.** Create a Blueprint from this repository and select `render.yaml`, or create a Python web service using the repository root, build command `pip install -r backend/requirements.txt`, and start command `PYTHONPATH=backend uvicorn app.main:app --host 0.0.0.0 --port $PORT`. Add `MONGODB_URI` from Atlas, `JWT_SECRET_KEY` (a unique random value with at least 32 characters), and `CORS_ORIGINS` containing the exact HTTPS URL of your Vercel site. The health check is `/api/v1/health`.
2. **Deploy the frontend to Vercel.** Import the same repository and set the project root directory to `frontend`. Add `NEXT_PUBLIC_API_URL` to the Render service URL (for example, `https://fxmind-api.onrender.com`, without a trailing slash) and `NEXT_PUBLIC_WS_URL` to that service's secure WebSocket URL (for example, `wss://fxmind-api.onrender.com`). These `NEXT_PUBLIC_` values are public browser configuration, not secrets.
3. **Configure Atlas Network Access** to allow connections from the backend host. Prefer the provider's published outbound IP ranges or a private network integration; avoid opening access to all IP addresses when possible.

Keep production `APP_ENV=production` and `DEBUG=false`. Production startup rejects weak/missing JWT keys, non-HTTPS CORS origins, missing MongoDB configuration, or debug mode. Atlas stores the database but does not host either app service. Free hosting/database plans may sleep or have usage limits, so always-on service may require paid plans.

Until proper user authentication and per-user ownership checks are implemented, production deliberately disables alert management and Telegram configuration endpoints with HTTP 503 responses. Broker execution is also disabled in production.

For local frontend development, copy `frontend/.env.example` to `frontend/.env.local`. The local API proxy is enabled only during development; production frontend builds must use the deployed API URL.

---

## 🔒 Security & Safe Analysis Guarantee

- **Broker Safety**: Broker execution is disabled in production. Do not enable it until broker actions have authentication, authorization, and explicit user confirmation.
- **Probabilistic Outputs**: All confidence numbers represent calibrated probabilities, never absolute guarantees.
- **Fail-Closed Principle**: If market data is stale (>45 mins) or model is unavailable, the system defaults to `NO_TRADE`.

---

## 📄 License

MIT License. Open-source and free for production deployment.
