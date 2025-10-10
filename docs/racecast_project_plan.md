# 🏎️ RaceCast Project Plan

## 1. Project Definition

**RaceCast** is a predictive analytics platform for Formula 1 races. The project aims to predict future race results using historical race data, weather conditions, tire strategies, social media hype data, and driver psychological profiles. It will provide users with both predictions and comparisons with actual results through a dashboard.

- **Project type:** Predictive Analytics Dashboard (end-to-end ML + backend + frontend)
- **Components:** Machine Learning Model, FastAPI backend, Neon PostgreSQL DB, Next.js frontend (Vercel).

---

## 2. Architecture Components

- **Database (Neon PostgreSQL)**

  - Prediction and actual results will be stored here.
  - Tables: `races`, `predictions`, `results`, `driver_profiles`.

- **Backend (FastAPI, Render)**

  - Will run the model and provide API endpoints.
  - Endpoint examples: `/predict`, `/update_results`, `/healthz`.
  - Will write prediction results to DB.

- **Frontend (Next.js, Vercel)**

  - Dashboard UI.
  - Prediction cards, prediction vs. reality comparisons, accuracy trend charts.
  - Optionally social media hype and psychology layers.
  - **Data Fetching & Server State:** React Query (API fetch and caching).
  - **UI Libraries:** TailwindCSS (styling), Recharts/Chart.js (charts), shadcn/ui (component library).

---

## 3. Development Stages

### Stage 1 — Model

1. Collecting historic data from Ergast and FastF1 APIs.
2. Feature engineering (driver form, constructor performance, track history, weather).
3. **ML Models:**
   - Baseline → XGBoost (rank:pairwise).
   - Alternative → LightGBM (faster, for large datasets).
   - Probabilistic → Bayesian models (probability distributions).
   - For sequence data (future) → LSTM/GRU (lap-by-lap telemetry).
4. Accuracy metrics: Top-3 accuracy, RMSE.
5. Save model as `.pkl` or `.json` file.
6. **Training Environment:**
   - Small dataset → Can be trained locally on MacBook Air M4.
   - Large dataset / GPU needed → Google Colab (T4 GPU free tier) or similar cloud environment.
   - Recommendation: Local training for MVP, migrate to Colab when dataset grows.

### Stage 2 — Backend

1. Create FastAPI project (`main.py`).
2. Load model and return JSON predictions from `/predict` endpoint.
3. Connect to Neon DB and write predictions.
4. Write actual results to DB after race (`/update_results`).
5. Deploy backend to Render.

### Stage 3 — Frontend

1. Dashboard skeleton with Next.js.
2. Upcoming Race Prediction cards.
3. Prediction vs Reality comparison table.
4. Season tracker charts.
5. Social media hype + driver psychology layer (optional).
6. Server state management with React Query.
7. UI side usage of TailwindCSS + Recharts/Chart.js + shadcn/ui.

### Stage 4 — Automation

1. Weekly cron job → upcoming race prediction.
2. Post-race cron job → actual result update.
3. GitHub Actions or Back4App scheduler for cron jobs.

---

## 4. Technology Choices

- **Database:** Neon (serverless Postgres, free tier sufficient).
- **Backend:** FastAPI (Python, hosted on Render).
- **Frontend:** Next.js (hosted on Vercel). Server state management with React Query.
- **ML:** XGBoost baseline, future LightGBM/Bayesian models. LSTM/GRU option for advanced telemetry.
- **EDA & prototype:** Jupyter Notebook + optional DuckDB (local analytics).
- **UI/UX:** TailwindCSS, shadcn/ui, Recharts/Chart.js.
- **Training Environment:** Local MacBook (small dataset), Google Colab (if GPU needed).

---

## 5. MVP Scope

- Upcoming Race Prediction card.
- Last Race Review (prediction vs actual).
- Season tracker accuracy trend.
- Driver psychology cards (static layer).
- Optional: Social hype (future sprints).

---

