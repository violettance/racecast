"""
Test script for XGBoost model - Azerbaijan GP 2025 Prediction
Testing the trained model against actual race results
"""

import pandas as pd
import numpy as np
import pickle
from sklearn.preprocessing import LabelEncoder

# Load the trained model
print("=" * 80)
print("XGBoost Model Test - Azerbaijan Grand Prix 2025")
print("=" * 80)

model_path = '/Users/mary/Library/CloudStorage/GoogleDrive-productora.analytics@gmail.com/My Drive/productora_projects/racecast/models/xgboost/xgboost_ranker_model.pkl'
data_path = '/Users/mary/Library/CloudStorage/GoogleDrive-productora.analytics@gmail.com/My Drive/productora_projects/racecast/data/processed/xgboost/final_model_dataset.csv'

print("\n1. Loading model...")
with open(model_path, 'rb') as f:
    model = pickle.load(f)
print("✓ Model loaded successfully")

# Load the dataset
print("\n2. Loading dataset...")
df = pd.read_csv(data_path)
print(f"✓ Dataset loaded: {df.shape[0]} records, {df.shape[1]} features")

# Filter for 2025 Azerbaijan GP (Round 17)
print("\n3. Extracting Azerbaijan GP 2025 data...")
baku_2025 = df[(df['year'] == 2025) & (df['round'] == 17)].copy()
print(f"✓ Found {len(baku_2025)} drivers for Azerbaijan GP 2025")

# Display race information
print("\n" + "=" * 80)
print("RACE INFORMATION")
print("=" * 80)
print(f"Country: {baku_2025.iloc[0]['country']}")
print(f"Date: 2025-09-21")
print(f"Race Type: {'Sprint Weekend' if baku_2025.iloc[0]['has_sprint_format'] == 1 else 'Regular Weekend'}")

# Load driver names from the enhanced dataset for display purposes
enhanced_df = pd.read_csv('/Users/mary/Library/CloudStorage/GoogleDrive-productora.analytics@gmail.com/My Drive/productora_projects/racecast/data/processed/xgboost/enhanced_f1_dataset.csv')
enhanced_baku = enhanced_df[(enhanced_df['year'] == 2025) & (enhanced_df['round'] == 17)].copy()

# Display actual results (target_position)
print("\n" + "=" * 80)
print("ACTUAL RACE RESULTS")
print("=" * 80)
actual_results = enhanced_baku[['driver_first_name', 'driver_last_name', 'constructor_name', 
                                 'grid_position', 'target_position']].copy()
actual_results = actual_results.sort_values('target_position')
actual_results.columns = ['First Name', 'Last Name', 'Team', 'Grid', 'Finish']
actual_results['Driver'] = actual_results['First Name'] + ' ' + actual_results['Last Name']
actual_results = actual_results[['Finish', 'Driver', 'Team', 'Grid']]
actual_results['Grid'] = actual_results['Grid'].astype(int)
actual_results['Finish'] = actual_results['Finish'].astype(int)

print(actual_results.to_string(index=False))

# Prepare features for prediction
print("\n4. Preparing features for prediction...")

# Get categorical columns
categorical_columns = baku_2025.select_dtypes(exclude=[np.number]).columns.tolist()

# Encode categorical variables
baku_encoded = baku_2025.copy()
for col in categorical_columns:
    if col in baku_encoded.columns:
        le = LabelEncoder()
        baku_encoded[col] = le.fit_transform(baku_encoded[col].astype(str))

# Remove only the target column
target_column = 'target_position'

# Get feature columns (all columns except target)
feature_columns = [col for col in baku_encoded.columns 
                  if col != target_column]

X_test = baku_encoded[feature_columns]
y_actual = baku_encoded[target_column].values

print(f"✓ Feature matrix prepared: {X_test.shape}")

# Make predictions
print("\n5. Making predictions...")
y_pred = model.predict(X_test)
print("✓ Predictions complete")

# Create predictions DataFrame
print("\n" + "=" * 80)
print("MODEL PREDICTIONS VS ACTUAL RESULTS")
print("=" * 80)

predictions_df = pd.DataFrame({
    'Driver': enhanced_baku['driver_first_name'].values + ' ' + enhanced_baku['driver_last_name'].values,
    'Team': enhanced_baku['constructor_name'].values,
    'Grid': baku_2025['grid_position'].values.astype(int),
    'Actual_Finish': y_actual.astype(int),
    'Predicted_Position': y_pred,
    'Predicted_Rank': pd.Series(y_pred).rank(method='min').values.astype(int)
})

# Sort by predicted rank
predictions_df = predictions_df.sort_values('Predicted_Rank')
predictions_df['Error'] = abs(predictions_df['Predicted_Rank'] - predictions_df['Actual_Finish'])

# Display results
print("\n{:<4} {:<25} {:<20} {:<6} {:<8} {:<10} {:<6}".format(
    "Pred", "Driver", "Team", "Grid", "Actual", "Pred Pos", "Error"))
print("-" * 80)

for idx, row in predictions_df.iterrows():
    print("{:<4} {:<25} {:<20} {:<6} {:<8} {:<10.2f} {:<6}".format(
        row['Predicted_Rank'],
        row['Driver'][:25],
        row['Team'][:20],
        row['Grid'],
        row['Actual_Finish'],
        row['Predicted_Position'],
        row['Error']
    ))

# Calculate metrics
print("\n" + "=" * 80)
print("PERFORMANCE METRICS")
print("=" * 80)

from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from scipy.stats import spearmanr

# Sort predictions_df by actual finish to align with y_actual
predictions_sorted = predictions_df.sort_values('Actual_Finish')

mae = mean_absolute_error(predictions_sorted['Actual_Finish'], predictions_sorted['Predicted_Rank'])
rmse = np.sqrt(mean_squared_error(predictions_sorted['Actual_Finish'], predictions_sorted['Predicted_Rank']))
r2 = r2_score(predictions_sorted['Actual_Finish'], predictions_sorted['Predicted_Rank'])
spearman_corr, _ = spearmanr(predictions_sorted['Actual_Finish'], predictions_sorted['Predicted_Rank'])

print(f"Mean Absolute Error (MAE): {mae:.2f} positions")
print(f"Root Mean Squared Error (RMSE): {rmse:.2f} positions")
print(f"R² Score: {r2:.4f}")
print(f"Spearman Correlation: {spearman_corr:.4f}")

# Count perfect predictions and close predictions
perfect = (predictions_df['Error'] == 0).sum()
within_1 = (predictions_df['Error'] <= 1).sum()
within_2 = (predictions_df['Error'] <= 2).sum()
within_3 = (predictions_df['Error'] <= 3).sum()

print(f"\nPerfect predictions (±0): {perfect}/{len(predictions_df)} ({perfect/len(predictions_df)*100:.1f}%)")
print(f"Within ±1 position: {within_1}/{len(predictions_df)} ({within_1/len(predictions_df)*100:.1f}%)")
print(f"Within ±2 positions: {within_2}/{len(predictions_df)} ({within_2/len(predictions_df)*100:.1f}%)")
print(f"Within ±3 positions: {within_3}/{len(predictions_df)} ({within_3/len(predictions_df)*100:.1f}%)")

# Top 3 predictions
print("\n" + "=" * 80)
print("TOP 3 PODIUM COMPARISON")
print("=" * 80)

actual_podium = actual_results.head(3)
predicted_podium = predictions_df.sort_values('Predicted_Rank').head(3)

print("\nACTUAL PODIUM:")
for i, row in enumerate(actual_podium.itertuples(), 1):
    print(f"  {i}. {row.Driver} ({row.Team})")

print("\nPREDICTED PODIUM:")
for i, row in enumerate(predicted_podium.itertuples(), 1):
    print(f"  {i}. {row.Driver} ({row.Team})")

# Check if any podium finishers were predicted correctly
podium_drivers_actual = set(actual_podium['Driver'].values)
podium_drivers_predicted = set(predicted_podium['Driver'].values)
correct_podium = podium_drivers_actual.intersection(podium_drivers_predicted)

print(f"\nCorrect podium finishers predicted: {len(correct_podium)}/3")
if correct_podium:
    print("Correctly predicted podium finishers:")
    for driver in correct_podium:
        print(f"  - {driver}")

print("\n" + "=" * 80)
print("TEST COMPLETE")
print("=" * 80)
