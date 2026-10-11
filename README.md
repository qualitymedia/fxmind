# FXMind

FXMind provides market analysis for GBP/USD. It shows market data, analysis signals, a calendar, and historical performance. It is for analysis only and is not a broker or trading service.

## Requirements

- Python 3.11
- Node.js 18
- MongoDB Atlas or another reachable MongoDB server

## Run locally

Copy `.env.example` to `.env` and set `MONGODB_URI` and `JWT_SECRET_KEY`. Keep `.env` private and do not commit it.

Start the API:

```bash
cd backend
python -m venv .venv
```

Activate the virtual environment, then run:

```bash
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

In a second terminal, start the website:

```bash
cd frontend
npm install
```

Copy `frontend/.env.example` to `frontend/.env.local`, then run:

```bash
npm run dev
```

The website runs at `http://localhost:3000`. The API health check is at `http://localhost:8000/api/v1/health`.

## Existing SQLite data

The old SQLite file is not used or removed automatically. To copy its records into MongoDB, set the MongoDB connection string and run the importer from the `backend` directory:

```bash
python scripts/migrate_sqlite_to_mongo.py
```

The importer leaves the SQLite file unchanged and does not replace documents already in MongoDB.

## Deploy

The frontend and API are deployed separately from this repository.

For Render, use the included `render.yaml`. Set `MONGODB_URI`, a unique `JWT_SECRET_KEY` of at least 32 characters, and `CORS_ORIGINS` to the HTTPS URL of the deployed Vercel site. The API health check is `/api/v1/health`.

For Vercel, set the project root to `frontend`. Set `NEXT_PUBLIC_API_URL` to the Render service URL and `NEXT_PUBLIC_WS_URL` to the same URL with the `wss://` scheme.

Production requires `APP_ENV=production` and `DEBUG=false`. Broker execution is disabled. Alert management and Telegram configuration return HTTP 503 until authentication and account ownership checks are implemented.

Atlas hosts the database, not the website or API. Hosting providers may pause free services, so continuous availability may require paid plans.

## Tests

Run backend tests:

```bash
cd backend
python -m pytest tests/ -v
```

Build the website:

```bash
cd frontend
npm run build
```
