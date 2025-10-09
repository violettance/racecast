"""Prediction service wrapping XGBoost ranker for pre-race inference.

Builds a feature frame compatible with the final training schema using
Ergast qualifying and race calendar data, encodes categoricals, and
generates rankings. Designed for pre-race usage: fetches latest grid
positions from Ergast shortly before race day.
"""

from __future__ import annotations

import pickle
from dataclasses import dataclass
from pathlib import Path
from typing import List, Optional, Tuple

import numpy as np
import pandas as pd
from loguru import logger
from sklearn.preprocessing import LabelEncoder

from src.config.settings import settings
from src.data.collectors.ergast_collector import ErgastCollector


@dataclass
class PredictionItem:
    driver: str
    grid: Optional[int]
    score: float
    predicted_rank: int


class RankerPredictor:
    def __init__(self, model_path: Optional[Path] = None):
        self.model_path = Path(model_path) if model_path else Path(settings.MODEL_RANKER_PATH)
        self._model = None
        self._header_columns: Optional[List[str]] = None
        # Path to the header CSV from training to guarantee column order
        self._final_dataset_path = settings.PROCESSED_DATA_DIR / "xgboost" / "final_model_dataset.csv"

    def load(self) -> None:
        if self._model is None:
            with open(self.model_path, "rb") as f:
                self._model = pickle.load(f)
            logger.info(f"Ranker model loaded from {self.model_path}")

        if self._header_columns is None:
            if not self._final_dataset_path.exists():
                # Fallback to existing project data path if present in repo
                alt = Path("data/processed/xgboost/final_model_dataset.csv")
                if alt.exists():
                    self._final_dataset_path = alt
                else:
                    raise FileNotFoundError("final_model_dataset.csv not found to derive feature columns")
            header_df = pd.read_csv(self._final_dataset_path, nrows=0)
            self._header_columns = header_df.columns.tolist()

    def _resolve_round(self, collector: ErgastCollector, year: int, round: Optional[int], country: Optional[str], race_name: Optional[str]) -> Tuple[int, str]:
        races = collector.collect_races(year)
        if round is not None:
            row = races[races["round"] == int(round)].iloc[0]
            return int(round), row.get("country", None) or row.get("race_name", "")
        df = races.copy()
        if country:
            df = df[df["country"].str.contains(country, case=False, na=False)]
        if race_name and df.empty:
            df = races[races["race_name"].str.contains(race_name, case=False, na=False)]
        if df.empty:
            raise RuntimeError("Could not resolve race round from inputs")
        row = df.iloc[0]
        return int(row["round"]), row.get("country", None) or row.get("race_name", "")

    def _build_inference_frame(self, collector: ErgastCollector, year: int, round_number: int) -> pd.DataFrame:
        assert self._header_columns is not None
        header_cols = self._header_columns

        # Fetch qualifying data for specific round only (not entire season!)
        qual = collector.collect_qualifying_round(year, round_number)
        
        # Check if qualifying results exist
        if qual.empty:
            raise ValueError(f"No qualifying results available for {year} Round {round_number}. Qualifying session may not have been completed yet.")
        
        # Fetch race info for specific round only
        race_row = collector.collect_race_round(year, round_number)
        country = race_row.get("country", None)

        rows = []
        for _, r in qual.iterrows():
            row = {col: np.nan for col in header_cols}
            
            # Basic race info
            row["year"] = int(year)
            row["round"] = int(round_number)
            row["country"] = country
            row["group_key"] = f"{int(year)}_{int(round_number)}"
            
            # Driver info
            row["driver_nationality"] = r.get("driver_nationality", np.nan)
            row["driver_abbreviation"] = r.get("driver_code", np.nan)
            try:
                row["driver_number"] = int(r.get("driver_number")) if pd.notna(r.get("driver_number")) else np.nan
            except Exception:
                row["driver_number"] = np.nan
            
            # Grid position (most important!)
            row["grid_position"] = r.get("position", np.nan)
            
            # Race format
            row["has_sprint_format"] = 1 if "Sprint" in str(race_row.get("race_name", "")) else 0
            
            # Era flags
            row["is_2017_plus_era"] = 1 if year >= 2017 else 0
            row["is_2022_plus_era"] = 1 if year >= 2022 else 0
            row["is_covid_season_2020"] = 1 if year == 2020 else 0
            
            # Race size
            row["race_size"] = len(qual)
            
            # All other features as NaN (model will use defaults)
            # Historical data is already learned by the model during training!
            
            rows.append(row)

        df = pd.DataFrame(rows)
        df = df.reindex(columns=header_cols, fill_value=np.nan)
        return df

    def _encode_categoricals(self, df: pd.DataFrame) -> pd.DataFrame:
        non_numeric = df.select_dtypes(exclude=[np.number]).columns.tolist()
        encoded = df.copy()
        for col in non_numeric:
            le = LabelEncoder()
            encoded[col] = le.fit_transform(encoded[col].astype(str))
        return encoded

    def predict(self, year: int, round: Optional[int] = None, country: Optional[str] = None, race_name: Optional[str] = None) -> Tuple[int, str, List[PredictionItem]]:
        self.load()
        collector = ErgastCollector()
        round_number, country_resolved = self._resolve_round(collector, year, round, country, race_name)
        base_df = self._build_inference_frame(collector, year, round_number)

        # Drop target column if present
        feature_df = base_df.copy()
        if "target_position" in feature_df.columns:
            feature_df = feature_df.drop(columns=["target_position"]) 

        X = self._encode_categoricals(feature_df)
        y_pred = self._model.predict(X)

        out = pd.DataFrame({
            "driver": base_df.get("driver_abbreviation", pd.Series(["?"] * len(base_df))),
            "grid": base_df.get("grid_position", pd.Series([np.nan] * len(base_df))),
            "score": y_pred,
        })
        out["predicted_rank"] = pd.Series(y_pred).rank(method="min").astype(int)
        out = out.sort_values("predicted_rank")

        items = [PredictionItem(driver=str(r.driver), grid=int(r.grid) if pd.notna(r.grid) else None, score=float(r.score), predicted_rank=int(r.predicted_rank)) for r in out.itertuples(index=False)]
        return round_number, country_resolved, items




