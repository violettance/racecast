from datetime import datetime, timezone
from typing import Optional

from fastapi import FastAPI, Depends, Header, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from src.config.settings import settings
import pandas as pd
from src.services.predictor import RankerPredictor
from src.db.session import get_db, engine, SessionLocal
from src.db.models import Base, Prediction, Result


app = FastAPI(title="RaceCast API", version="0.1.0")

# CORS
allowed_origins = [o.strip() for o in (settings.ALLOW_ORIGINS or "*").split(",")]
app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins if allowed_origins != ["*"] else ["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


predictor = RankerPredictor()


@app.on_event("startup")
def on_startup():
    # Load model on startup
    predictor.load()
    
    # Create tables if DATABASE_URL configured
    if engine is not None:
        Base.metadata.create_all(bind=engine)


def require_api_key(x_api_key: Optional[str] = Header(default=None)):
    if settings.API_KEY and x_api_key != settings.API_KEY:
        raise HTTPException(status_code=401, detail="Invalid API key")


@app.get("/healthz")
def healthz():
    return {
        "status": "ok",
        "time": datetime.now(timezone.utc).isoformat(),
        "model_loaded": predictor._model is not None,
    }


@app.get("/last_race")
def get_last_race(year: int = 2025):
    """Get the last race of the season."""
    from src.data.collectors.ergast_collector import ErgastCollector
    collector = ErgastCollector()
    races = collector.collect_races(year)
    if races.empty:
        raise HTTPException(status_code=404, detail="No races found for the given year")
    
    last_race = races.iloc[-1]
    return {
        "year": int(last_race["year"]),
        "round": int(last_race["round"]),
        "race_name": last_race["race_name"],
        "country": last_race["country"],
        "circuit_name": last_race["circuit_name"],
        "date": last_race["date"],
        "time": last_race.get("time", "")
    }


from pydantic import BaseModel


class PredictRequest(BaseModel):
    year: int
    round: Optional[int] = None
    country: Optional[str] = None
    race_name: Optional[str] = None


class PredictionItemOut(BaseModel):
    driver: str
    grid: Optional[int] = None
    score: float
    predicted_rank: int


class PredictResponse(BaseModel):
    year: int
    round: int
    country: str
    generated_at: str
    predictions: list[PredictionItemOut]


@app.post("/predict", response_model=PredictResponse, dependencies=[Depends(require_api_key)])
def predict(req: PredictRequest):
    # If no specific round/country provided, let predictor find the right race
    if req.round is None and req.country is None and req.race_name is None:
        # Predictor will automatically find the race with qualifying results available
        # This works for any day - it finds the race that can be predicted
        pass
    
    try:
        rnd, country, items = predictor.predict(year=req.year, round=req.round, country=req.country, race_name=req.race_name)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Prediction failed: {str(e)}")

    # Always persist to database if available
    if engine is not None and SessionLocal is not None:
        db = SessionLocal()
        try:
            group_key = f"{req.year}_{rnd}"
            for it in items:
                rec = Prediction(
                    year=req.year,
                    round=rnd,
                    driver_code=it.driver,
                    grid=it.grid,
                    score=it.score,
                    predicted_rank=it.predicted_rank,
                    group_key=group_key,
                )
                try:
                    db.add(rec)
                    db.commit()
                except Exception:
                    db.rollback()
        finally:
            db.close()

    return PredictResponse(
        year=req.year,
        round=rnd,
        country=country,
        generated_at=datetime.now(timezone.utc).isoformat(),
        predictions=[PredictionItemOut(**item.__dict__) for item in items],
    )


class PredictionsQuery(BaseModel):
    year: int
    round: int


@app.get("/predictions", dependencies=[Depends(require_api_key)])
def get_predictions(year: int, round: int):
    if engine is None or SessionLocal is None:
        raise HTTPException(status_code=503, detail="DATABASE_URL is not configured")
    db = SessionLocal()
    try:
        rows = db.query(Prediction).filter(Prediction.year == year, Prediction.round == round).order_by(Prediction.predicted_rank.asc()).all()
    finally:
        db.close()
    return {
        "year": year,
        "round": round,
        "predictions": [
            {
                "driver": r.driver_code,
                "grid": r.grid,
                "score": r.score,
                "predicted_rank": r.predicted_rank,
            }
            for r in rows
        ],
    }


class UpdateResultsRequest(BaseModel):
    year: int
    round: int


@app.post("/update_results", dependencies=[Depends(require_api_key)])
def update_results(req: UpdateResultsRequest):
    if engine is None or SessionLocal is None:
        raise HTTPException(status_code=503, detail="DATABASE_URL is not configured")
    
    try:
        # Fetch actual results via Ergast and persist
        from src.data.collectors.ergast_collector import ErgastCollector

        collector = ErgastCollector()
        results = collector.collect_results(req.year)
        rows = results[(results["round"] == req.round) & results["position"].notna()].copy()
        
        # Check if no results found for this round
        if rows.empty:
            raise HTTPException(
                status_code=400, 
                detail=f"No race results available for {req.year} Round {req.round}. Race may not have been completed yet."
            )
        
        # Early exit optimization: if first 5 rows are empty, don't process the rest
        if len(rows) >= 5:
            first_five = rows.head(5)
            if first_five["position"].isna().all():
                raise HTTPException(
                    status_code=400, 
                    detail=f"No race results available for {req.year} Round {req.round}. Race may not have been completed yet."
                )
        # If we have data, continue processing all rows
        
        inserted = 0
        db = SessionLocal()
        try:
            for _, r in rows.iterrows():
                rec = Result(
                    year=req.year,
                    round=req.round,
                    driver_code=str(r.get("driver_code")),
                    position=int(r.get("position")) if pd.notna(r.get("position")) else None,
                    points=float(r.get("points")) if pd.notna(r.get("points")) else None,
                )
                try:
                    db.add(rec)
                    db.commit()
                    inserted += 1
                except Exception:
                    db.rollback()
        finally:
            db.close()
        
        return {"inserted": inserted}
        
    except HTTPException:
        # Re-raise HTTP exceptions (like our 400 error above)
        raise
    except Exception as e:
        # Handle other errors (network, API issues, etc.)
        raise HTTPException(
            status_code=500, 
            detail=f"Failed to fetch race results: {str(e)}"
        )


@app.get("/results", dependencies=[Depends(require_api_key)])
def get_results(year: int, round: int):
    if engine is None or SessionLocal is None:
        raise HTTPException(status_code=503, detail="DATABASE_URL is not configured")
    db = SessionLocal()
    try:
        rows = db.query(Result).filter(Result.year == year, Result.round == round).order_by(Result.position.asc()).all()
    finally:
        db.close()
    return {
        "year": year,
        "round": round,
        "results": [
            {
                "driver": r.driver_code,
                "position": r.position,
                "points": r.points,
            }
            for r in rows
        ],
    }


