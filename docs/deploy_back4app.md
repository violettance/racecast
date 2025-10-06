# Back4App Deployment Guide (RaceCast Backend)

## Requirements
- GitHub repo connected
- Back4App Containers (Docker)
- Neon Postgres (prod branch)

## Build & Deploy Settings (Back4App)
- Branch: `main`
- Root Directory: `./` (or `./deploy` if using deploy-only context)
- Port: `8000`
- Health Check Path: `/healthz`

## Files in repo
- `deploy/Dockerfile` (or root `Dockerfile`) – builds the FastAPI app
- `deploy/Procfile` – `web: uvicorn src.api.main:app --host 0.0.0.0 --port ${PORT:-8000}`
- `deploy/.dockerignore` – excludes large/local files from image

## Environment Variables (Back4App → Settings → Environment)
Set the following keys exactly (build and runtime):

```
DATABASE_URL=postgresql+psycopg2://<USER>:<PASSWORD>@<HOST>/<DBNAME>?sslmode=require
API_KEY=<strong-random-secret>
ALLOW_ORIGINS=https://racecast.vercel.app
MODEL_RANKER_PATH=models/xgboost/xgboost_ranker_model.pkl
ERGAST_BASE_URL=https://api.jolpi.ca/ergast/f1
```

Notes:
- `DATABASE_URL`: Copy Neon "Psycopg2" connection string for the target branch (prod) and ensure `?sslmode=require` is present.
- `API_KEY`: Generate locally `python -c "import secrets; print(secrets.token_urlsafe(32))"` and paste the value. Frontend must send `x-api-key` header with the same value.
- `ALLOW_ORIGINS`: Set to your frontend prod domain; add multiple domains comma-separated if needed.

## Deploy Steps
1. Connect the GitHub repo in Back4App (Container app).
2. Configure Build & Deploy settings and add environment variables above.
3. Start deploy. The container will build using the Dockerfile.
4. After deploy finishes, verify endpoints:
   - `GET /healthz` → `{ "status": "ok" }`
   - `POST /predict` with headers `x-api-key: <API_KEY>` and body `{"year": 2025, "country": "Singapore", "persist": true}`
   - `GET /predictions?year=2025&round=18` with header `x-api-key: <API_KEY>`

## Operational Notes
- Tables are created automatically at startup if they do not exist (`Prediction`, `Result`).
- For schema migrations later, introduce Alembic and run `alembic upgrade head` on release.
- Use Neon production connection (not Neon Local Connect) in Back4App.


