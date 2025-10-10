### RaceCast Frontend Runbook

This runbook explains how the backend container behaves (Docker), which API endpoints exist, and exactly how/when GitHub Actions will call the backend to write predictions and results into the database. Share this with anyone wiring the frontend.

---

## 1) What the Docker image does

- The Docker image only runs the FastAPI server:
  - Command: `uvicorn src.api.main:app --host 0.0.0.0 --port 8000`
- It does NOT schedule itself, does NOT run background tasks by default.
- Database writes happen only when the API is called.
- Environment variables the container expects (examples):
  - `DATABASE_URL` (required for DB writes) – e.g. `postgresql://USER:PASS@HOST:PORT/DB?sslmode=require`
  - `API_KEY` (optional) – if set, protected endpoints require header `X-API-Key: <API_KEY>`
  - `ALLOW_ORIGINS` – CORS origins for frontend
  - `MODEL_RANKER_PATH` – defaults to `models/xgboost/xgboost_ranker_model.pkl`

Startup behavior
- On startup, if `DATABASE_URL` is set, SQL tables are created (if not exist).
- Health endpoint: `GET /healthz` returns `{ status: "ok", model_loaded: true, ... }`.

---

## 2) API contract for the frontend

Base URL: your deployed backend (Render URL).

Auth: If `API_KEY` is set, include `X-API-Key` for protected endpoints.

### 2.1 Health
- `GET /healthz`
- Use to verify deployment and model load.

### 2.2 Predictions (READ)
- `GET /predictions?year={YYYY}&round={R}`
- Response
```
{
  "year": 2025,
  "round": 19,
  "predictions": [
    { "driver": "RUS", "grid": 4, "score": 0.781, "predicted_rank": 4 }
  ]
}
```

### 2.3 Predictions (WRITE after Qualifying)
- `POST /predict`
- Body
```
{ "year": 2025, "round": 19, "persist": true }
```
- When `persist=true`, predictions are written into `predictions` table (idempotent via unique constraint).

### 2.4 Results (WRITE after Race)
- `POST /update_results`
- Body
```
{ "year": 2025, "round": 19 }
```
- Pulls official results from Ergast and writes to `results` table. Ergast can lag by 12–24h; safe to retry.

### 2.5 Tables
- `predictions(year, round, driver_code, grid, score, predicted_rank, group_key, created_at)`
- `results(year, round, driver_code, position, points, created_at)`

---

## 3) UI data mapping

Previous Race card
- Predictions: `GET /predictions?year=YYYY&round=R_prev`
- Results: later you can add a small `GET /results?year&round` or compute elsewhere; for now, showing predictions-only is supported.
- Fields
  - Driver → `prediction.driver` (driver code)
  - Prediction → `P{prediction.predicted_rank}`
  - Actual Rank → `P{result.position}` (after results exist)
- Badges
  - Top-3 & Top-5 accuracy can be computed client-side (compare prediction ranks vs result positions).

Next Race card
- Schedule (Qualifying & Race UTC times) from Ergast `current.json`:
  - `https://api.jolpi.ca/ergast/f1/current.json`
- Status logic
  - Before qualifying → "Prediction Pending"
  - After qualifying (and `/predict` persisted) → show predictions via `GET /predictions`
  - After race results persisted → show comparison table/metrics

---

## 4) Race weekend operations via GitHub Actions

Goal: Write predictions right after Qualifying, and write results after the Race (with Ergast delay tolerance). The backend does not run automatically, so Actions (or a manual curl) triggers the writes.

### 4.1 Manual button workflows (simplest)

Add two workflows in your repo. You will paste the temporary backend URL from Back4App when you trigger them.

`.github/workflows/predict.yml`
```
name: Predict
on:
  workflow_dispatch:
    inputs:
      backend_url: { description: 'Backend URL', required: true }
      api_key:     { description: 'API key', required: true }
      year:        { required: true, default: '2025' }
      round:       { required: true }
jobs:
  run:
    runs-on: ubuntu-latest
    steps:
      - name: Write prediction
        run: |
          curl -s -X POST "${{ inputs.backend_url }}/predict" \
            -H "Content-Type: application/json" \
            -H "X-API-Key: ${{ inputs.api_key }}" \
            -d "{\"year\":${{ inputs.year }},\"round\":${{ inputs.round }},\"persist\":true}"
```

`.github/workflows/update-results.yml`
```
name: Update Results
on:
  workflow_dispatch:
    inputs:
      backend_url: { required: true }
      api_key:     { required: true }
      year:        { required: true, default: '2025' }
      round:       { required: true }
jobs:
  run:
    runs-on: ubuntu-latest
    steps:
      - name: Retry until Ergast data is ready (max ~36h)
        run: |
          for i in {1..12}; do
            curl -s -X POST "${{ inputs.backend_url }}/update_results" \
              -H "Content-Type: application/json" \
              -H "X-API-Key: ${{ inputs.api_key }}" \
              -d "{\"year\":${{ inputs.year }},\"round\":${{ inputs.round }}}" && break
            sleep 10800  # 3h
          done
```

Race weekend usage
- Back4App → Redeploy → copy the temporary URL (valid ~60 minutes).
- After Qualifying → trigger "Predict" workflow with URL/year/round.
- After Race → trigger "Update Results" workflow with URL/year/round.

### 4.2 Optional: automatic schedule-aware job

- Run daily (or every 6h). Fetch schedule from Ergast `current.json`, detect if now ≥ qualifying time or ≥ race time + delay, and call the API accordingly. This removes manual timing but requires a stable backend URL (or the job must run while the temporary URL is alive).

---

## 5) Quick test commands

```
curl -s "$BACKEND/healthz"

curl -s -X POST "$BACKEND/predict" \
  -H "Content-Type: application/json" \
  -H "X-API-Key: $API_KEY" \
  -d '{"year":2025,"round":19,"persist":true}'

curl -s "$BACKEND/predictions?year=2025&round=19" \
  -H "X-API-Key: $API_KEY"

curl -s -X POST "$BACKEND/update_results" \
  -H "Content-Type: application/json" \
  -H "X-API-Key: $API_KEY" \
  -d '{"year":2025,"round":19}'
```

---

## 6) What the frontend needs

- To render the screenshot you shared:
  - Read predictions via `GET /predictions?year=YYYY&round=R`.
  - Show "Prediction Pending" until predictions exist for the next race.
  - Optional: once a `GET /results` endpoint is added, render Actual Rank and accuracy badges by comparing predictions vs results.


