#!/usr/bin/env python3
"""
Predict grid ranking for the 2025 Singapore Grand Prix using the existing
XGBoost ranker model. This script fetches 2025 season race and qualifying data
from Ergast, constructs a Singapore-only feature frame aligned to the
final_model_dataset schema (filling unavailable engineered features with NaN),
encodes categoricals, loads the model, and prints predicted ranks.
"""

import sys
from pathlib import Path

# Ensure src is importable
project_root = Path(__file__).parent.parent
# Add project root so that `import src...` works
sys.path.insert(0, str(project_root))

import pickle
import numpy as np
import pandas as pd
from loguru import logger
from sklearn.preprocessing import LabelEncoder

from src.data.collectors.ergast_collector import ErgastCollector


MODEL_PATH = Path(
    "/Users/mary/Library/CloudStorage/GoogleDrive-productora.analytics@gmail.com/My Drive/productora_projects/racecast/models/xgboost/xgboost_ranker_model.pkl"
)
FINAL_DATASET_PATH = Path(
    "/Users/mary/Library/CloudStorage/GoogleDrive-productora.analytics@gmail.com/My Drive/productora_projects/racecast/data/processed/xgboost/final_model_dataset.csv"
)
RESULTS_DIR = Path(
    "/Users/mary/Library/CloudStorage/GoogleDrive-productora.analytics@gmail.com/My Drive/productora_projects/racecast/results"
)


def get_singapore_round_2025(collector: ErgastCollector) -> int:
    races = collector.collect_races(2025)
    sgp = races[(races["country"].str.contains("Singapore", case=False)) | (races["race_name"].str.contains("Singapore", case=False))]
    if sgp.empty:
        raise RuntimeError("Could not find Singapore GP in 2025 race calendar.")
    # In case of multiple (shouldn't happen), take the first
    return int(sgp.iloc[0]["round"])


def build_singapore_dataframe(collector: ErgastCollector, round_number: int) -> pd.DataFrame:
    # Load the final model dataset header to align columns
    header_df = pd.read_csv(FINAL_DATASET_PATH, nrows=0)
    all_columns = header_df.columns.tolist()

    # Pull qualifying for 2025 and filter Singapore round
    qual = collector.collect_qualifying(2025)
    qual = qual[qual["round"] == round_number].copy()
    if qual.empty:
        raise RuntimeError("No qualifying data available for Singapore 2025 (round {}).".format(round_number))

    # Pull races to get country info
    races = collector.collect_races(2025)
    race_row = races[races["round"] == round_number].iloc[0]
    country = race_row.get("country", "Singapore")

    # Construct base rows with known fields; others default to NaN
    base = pd.DataFrame({col: pd.Series(dtype=header_df.dtypes.get(col, np.float64)) for col in all_columns})

    rows = []
    for _, r in qual.iterrows():
        row = {col: np.nan for col in all_columns}
        row["year"] = 2025
        row["round"] = int(round_number)
        row["country"] = country
        row["driver_nationality"] = r.get("driver_nationality", np.nan)
        row["constructor_nationality"] = np.nan  # not present in qualifying endpoint
        row["grid_position"] = r.get("position", np.nan)
        row["has_sprint_format"] = 1 if "Sprint" in str(race_row.get("race_name", "")) else 0
        row["driver_abbreviation"] = r.get("driver_code", np.nan)
        # driver_number can be string in Ergast; cast safe
        try:
            row["driver_number"] = int(r.get("driver_number")) if pd.notna(r.get("driver_number")) else np.nan
        except Exception:
            row["driver_number"] = np.nan
        # Minimal group key components
        row["group_key"] = f"2025_{int(round_number)}"
        rows.append(row)

    df = pd.DataFrame(rows)
    # Ensure all expected columns exist in the right order
    df = df.reindex(columns=all_columns, fill_value=np.nan)
    return df


def encode_categoricals(df: pd.DataFrame) -> pd.DataFrame:
    # Identify non-numeric columns
    non_numeric = df.select_dtypes(exclude=[np.number]).columns.tolist()
    encoded = df.copy()
    for col in non_numeric:
        # Leave identifier/group key columns as-is if model expects numeric only
        # Azerbaijan test encoded all non-numerics; follow same approach
        le = LabelEncoder()
        encoded[col] = le.fit_transform(encoded[col].astype(str))
    return encoded


def main():
    logger.info("Preparing Singapore 2025 dataset and running predictions...")

    # Load model
    with open(MODEL_PATH, "rb") as f:
        model = pickle.load(f)
    logger.info("Model loaded: {}".format(MODEL_PATH.name))

    # Build Singapore-only dataframe
    collector = ErgastCollector()
    round_number = get_singapore_round_2025(collector)
    logger.info(f"Singapore 2025 round: {round_number}")
    sgp_df = build_singapore_dataframe(collector, round_number)

    # Remove target if present
    target_col = "target_position"
    feature_df = sgp_df.copy()
    if target_col in feature_df.columns:
        feature_df = feature_df.drop(columns=[target_col])

    # Encode categoricals
    X = encode_categoricals(feature_df)

    # Predict
    y_pred = model.predict(X)

    # Produce a concise ranking output
    output_df = pd.DataFrame({
        "Driver": sgp_df.get("driver_abbreviation", pd.Series(["?"] * len(sgp_df))),
        "Grid": sgp_df.get("grid_position", pd.Series([np.nan] * len(sgp_df))),
        "Predicted_Position_Score": y_pred,
    })
    output_df["Predicted_Rank"] = pd.Series(y_pred).rank(method="min").astype(int)
    output_df = output_df.sort_values("Predicted_Rank")

    print("\n=== Singapore GP 2025 Prediction (XGBoost Ranker) ===")
    print(output_df.to_string(index=False))
    # Save predictions CSV
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    predictions_path = RESULTS_DIR / "predictions_singapore_2025.csv"
    output_df.to_csv(predictions_path, index=False)
    logger.info(f"Saved predictions to {predictions_path}")

    # Fetch actual race results and evaluate top-N overlap
    results = collector.collect_results(2025)
    actual_sgp = results[(results["round"] == round_number) & results["position"].notna()].copy()
    if not actual_sgp.empty:
        actual_sgp["position"] = actual_sgp["position"].astype(int)
        actual_sorted = actual_sgp.sort_values("position")
        actual_codes = actual_sorted["driver_code"].astype(str).tolist()

        predicted_codes = output_df.sort_values("Predicted_Rank")["Driver"].astype(str).tolist()

        def hit_rate(k: int) -> float:
            return len(set(predicted_codes[:k]).intersection(set(actual_codes[:k]))) / float(k)

        top3_rate = hit_rate(3)
        top5_rate = hit_rate(5)

        print("\n=== Evaluation vs Actual Results ===")
        print(f"Actual top 5: {actual_codes[:5]}")
        print(f"Pred   top 5: {predicted_codes[:5]}")
        print(f"Top-3 hit rate: {top3_rate:.2%}")
        print(f"Top-5 hit rate: {top5_rate:.2%}")

        # Save metrics CSV
        metrics_df = pd.DataFrame({
            "metric": ["top3_hit_rate", "top5_hit_rate"],
            "value": [top3_rate, top5_rate]
        })
        metrics_path = RESULTS_DIR / "metrics_singapore_2025.csv"
        metrics_df.to_csv(metrics_path, index=False)
        logger.info(f"Saved metrics to {metrics_path}")
    else:
        print("\n(No actual Singapore 2025 race results available yet; skipping evaluation.)")


if __name__ == "__main__":
    main()


