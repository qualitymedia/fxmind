# FXMind — GBP/USD AI Market Analysis Assistant

FXMind is a production-oriented, probabilistic AI market analysis system designed specifically for **GBP/USD**.

> [!IMPORTANT]
> **ANALYSIS ONLY**: FXMind NEVER executes trades, places broker orders, manages brokerage accounts, or automatically buys/sells anything.

---

## 🌟 Product Capabilities

- **Current GBP/USD Price & Quote**: Real-time bid, ask, spread, 24h high/low, session state.
- **M15 Primary Analysis & H1 Context**: Multi-timeframe trend, RSI, ATR, EMA alignment.
- **AI Directional Bias**: `BULLISH`, `BEARISH`, or `NEUTRAL` with calibrated probabilities.
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

## 💻 Tech Stack ($0 Recurring Infrastructure Cost)

- **Frontend**: Next.js 14 (App Router), TypeScript, Tailwind CSS, Lucide icons, Lightweight Charts, React Query.
- **Backend**: Python 3.11+, FastAPI, Pydantic v2, SQLAlchemy (Asyncio), Alembic, PostgreSQL 16.
- **ML Engine**: XGBoost, Scikit-Learn, SciPy, Optuna, SHAP, PyArrow, Pandas, NumPy.
- **Infrastructure**: Docker, Docker Compose.

---

## 🚀 Quick Start Guide

### Prerequisites
- Docker & Docker Compose
- Python 3.11+
- Node.js 18+

### 1. Initial Setup
```bash
# Clone the repository
git clone https://github.com/your-org/gbpusd-ai-assistant.git
cd gbpusd-ai-assistant

# Create environment file
cp .env.example .env
```

### 2. Running Locally

#### Start Backend:
```bash
cd backend
python -m venv venv
# Windows: venv\Scripts\activate | Unix: source venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

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
# Run backend tests
cd backend && python -m pytest tests/ -v

# Typecheck frontend
cd frontend && npm run build
```

---

## 🔒 Security & Safe Analysis Guarantee

- **Zero Order Execution**: System contains no broker API integration or order placement code.
- **Probabilistic Outputs**: All confidence numbers represent calibrated probabilities, never absolute guarantees.
- **Fail-Closed Principle**: If market data is stale (>45 mins) or model is unavailable, the system defaults to `NO_TRADE`.

---

## 📄 License

MIT License. Open-source and free for production deployment.
