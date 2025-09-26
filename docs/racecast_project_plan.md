# 🏎️ RaceCast Proje Planı

## 1. Proje Tanımı

**RaceCast**, Formula 1 yarışları için öngörücü bir analitik platformu. Proje; geçmiş yarış verileri, hava durumu, lastik stratejileri, sosyal medya hype verileri ve sürücü psikolojik profillerini kullanarak gelecek yarışların sonuçlarını tahmin etmeyi hedefliyor. Kullanıcıya bir dashboard üzerinden hem tahminleri hem de gerçekleşen sonuçlarla karşılaştırmaları sunacak.

- **Proje tipi:** Predictive Analytics Dashboard (end-to-end ML + backend + frontend)
- **Bileşenler:** Machine Learning Model, FastAPI backend, Neon PostgreSQL DB, Next.js frontend (Vercel).

---

## 2. Mimari Bileşenler

- **Database (Neon PostgreSQL)**

  - Prediction ve actual sonuçlar burada tutulacak.
  - Tablolar: `races`, `predictions`, `results`, `driver_profiles`.

- **Backend (FastAPI, Back4App)**

  - Modeli çalıştıracak ve API endpointleri sunacak.
  - Endpoint örnekleri: `/predict`, `/update_results`, `/healthz`.
  - Prediction sonuçlarını DB’ye yazacak.

- **Frontend (Next.js, Vercel)**

  - Dashboard UI.
  - Prediction kartı, prediction vs. reality karşılaştırmaları, accuracy trend grafikleri.
  - Opsiyonel olarak sosyal medya hype ve psikoloji katmanları.
  - **Data Fetching & Server State:** React Query (API fetch ve caching).
  - **UI Libraries:** TailwindCSS (styling), Recharts/Chart.js (grafikler), shadcn/ui (component library).

---

## 3. Geliştirme Aşamaları

### Aşama 1 — Model

1. Ergast ve FastF1 API’lerinden historic data toplama.
2. Feature engineering (driver form, constructor performance, track history, weather).
3. **ML Modelleri:**
   - Baseline → XGBoost (rank:pairwise).
   - Alternatif → LightGBM (daha hızlı, büyük dataset için).
   - Probabilistic → Bayesian modeller (olasılık dağılımları).
   - Sequence data için (ileride) → LSTM/GRU (lap-by-lap telemetry).
4. Accuracy metrikleri: Top-3 accuracy, RMSE.
5. Modeli `.pkl` veya `.json` dosyası olarak kaydetme.
6. **Training Ortamı:**
   - Küçük dataset → MacBook Air M4 üzerinde lokal training yapılabilir.
   - Büyük dataset / GPU ihtiyacı → Google Colab (T4 GPU free tier) veya benzeri cloud ortam kullanılabilir.
   - Öneri: MVP için local training, ileride dataset büyüyünce Colab’a geçiş.

### Aşama 2 — Backend

1. FastAPI projesi açma (`main.py`).
2. Modeli yükleyip `/predict` endpointinden JSON tahmin döndürme.
3. Neon DB’ye bağlanıp predictionları yazma.
4. Yarış sonrası actual sonuçları DB’ye yazma (`/update_results`).
5. Backend’i Back4App’e deploy etme.

### Aşama 3 — Frontend

1. Next.js ile dashboard iskeleti.
2. Upcoming Race Prediction kartları.
3. Prediction vs Reality comparison tablosu.
4. Season tracker grafikleri.
5. Sosyal medya hype + driver psychology layer (opsiyonel).
6. React Query ile server state yönetimi.
7. UI tarafında TailwindCSS + Recharts/Chart.js + shadcn/ui kullanımı.

### Aşama 4 — Otomasyon

1. Haftalık cron job → upcoming race prediction.
2. Yarış sonrası cron job → actual sonuç update.
3. Cron jobs için GitHub Actions veya Back4App scheduler.

---

## 4. Teknoloji Seçimleri

- **Database:** Neon (serverless Postgres, free tier yeterli).
- **Backend:** FastAPI (Python, Back4App’de host).
- **Frontend:** Next.js (Vercel’de host). React Query ile server state management.
- **ML:** XGBoost baseline, ileride LightGBM/Bayesian modeller. Gelişmiş telemetry için LSTM/GRU opsiyonu.
- **EDA & prototip:** Jupyter Notebook + opsiyonel DuckDB (local analytics).
- **UI/UX:** TailwindCSS, shadcn/ui, Recharts/Chart.js.
- **Training Ortamı:** Local MacBook (küçük dataset), Google Colab (GPU gerekirse).

---

## 5. MVP Kapsamı

- Upcoming Race Prediction kartı.
- Last Race Review (prediction vs actual).
- Season tracker accuracy trendi.
- Driver psychology kartları (sabit layer).
- Opsiyonel: Social hype (ileriki sprintlerde).

---

