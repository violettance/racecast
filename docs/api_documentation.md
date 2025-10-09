# RaceCast API Documentation

## Overview
RaceCast API provides Formula 1 race predictions using machine learning models trained on historical F1 data. The API can predict race results based on qualifying positions and fetch actual race results from the Ergast API.

## Base URL
- **Local Development:** `http://localhost:8000`
- **Production (Render):** `https://racecast-backend.onrender.com`

## Authentication
All endpoints (except `/healthz` and `/last_race`) require an API key in the request header:
```
X-API-Key: your-api-key-here
```

## Endpoints

### 1. Health Check
**GET** `/healthz`

Check API status and model loading status.

**Response:**
```json
{
  "status": "ok",
  "time": "2025-10-09T19:41:14.681638+00:00",
  "model_loaded": true
}
```

### 2. Get Last Race
**GET** `/last_race`

Get information about the last race of a season.

**Parameters:**
- `year` (optional): Season year (default: 2025)

**Response:**
```json
{
  "year": 2025,
  "round": 16,
  "race_name": "Italian Grand Prix",
  "country": "Italy",
  "circuit_name": "Autodromo Nazionale Monza",
  "date": "2025-10-05",
  "time": "14:00:00Z"
}
```

### 3. Predict Race Results
**POST** `/predict`

Generate race predictions for a specific round or the last race of the season.

**Request Body:**
```json
{
  "year": 2025,
  "round": 18,
  "country": "Singapore",
  "race_name": "Singapore Grand Prix"
}
```

**Parameters:**
- `year` (required): Season year
- `round` (optional): Race round number
- `country` (optional): Country name
- `race_name` (optional): Race name

**Important:** The API requires qualifying results to make predictions. If no specific round/country/race_name is provided, the API will attempt to find a race with available qualifying data, but this may fail if no qualifying results are available.

**Error Handling:**
- **400 Bad Request:** If qualifying results are not available for the specified round
- **500 Internal Server Error:** For other prediction failures

**Example Error Response:**
```json
{
  "detail": "No qualifying results available for 2025 Round 19. Qualifying session may not have been completed yet."
}
```

**Best Practice:** Always specify a `round` parameter when making predictions to avoid ambiguity. The API is designed to work with completed qualifying sessions.

**Response:**
```json
{
  "year": 2025,
  "round": 18,
  "country": "Singapore",
  "generated_at": "2025-10-09T19:43:49.382974+00:00",
  "predictions": [
    {
      "driver": "NOR",
      "grid": 5,
      "score": 1.1445177793502808,
      "predicted_rank": 1
    },
    {
      "driver": "ANT",
      "grid": 4,
      "score": 1.2236847877502441,
      "predicted_rank": 2
    },
    {
      "driver": "PIA",
      "grid": 3,
      "score": 1.4637243747711182,
      "predicted_rank": 3
    }
  ]
}
```

### 4. Get Predictions
**GET** `/predictions`

Retrieve saved predictions from the database.

**Parameters:**
- `year` (required): Season year
- `round` (required): Race round number

**Response:**
```json
{
  "year": 2025,
  "round": 18,
  "predictions": [
    {
      "driver": "NOR",
      "grid": 5,
      "score": 1.1445177793502808,
      "predicted_rank": 1
    }
  ]
}
```

### 5. Update Race Results
**POST** `/update_results`

Fetch actual race results from Ergast API and save to database.

**Request Body:**
```json
{
  "year": 2025,
  "round": 18
}
```

**Response:**
```json
{
  "inserted": 20
}
```

### 6. Get Race Results
**GET** `/results`

Retrieve actual race results from the database.

**Parameters:**
- `year` (required): Season year
- `round` (required): Race round number

**Response:**
```json
{
  "year": 2025,
  "round": 18,
  "results": [
    {
      "driver": "RUS",
      "position": 1,
      "points": 25.0
    },
    {
      "driver": "VER",
      "position": 2,
      "points": 18.0
    },
    {
      "driver": "NOR",
      "position": 3,
      "points": 15.0
    }
  ]
}
```

## Error Responses

### 401 Unauthorized
```json
{
  "detail": "Invalid API key"
}
```

### 503 Service Unavailable
```json
{
  "detail": "DATABASE_URL is not configured"
}
```

### 404 Not Found
```json
{
  "detail": "No races found for the given year"
}
```

## Example Usage

### Predict Last Race (Automatically detects current last race)
```bash
curl -X POST "https://racecast-backend.onrender.com/predict" \
  -H "Content-Type: application/json" \
  -H "X-API-Key: your-api-key" \
  -d '{"year": 2025}'
```

### Get Predictions
```bash
curl -X GET "https://racecast-backend.onrender.com/predictions?year=2025&round=18" \
  -H "X-API-Key: your-api-key"
```

### Update Results
```bash
curl -X POST "https://racecast-backend.onrender.com/update_results" \
  -H "Content-Type: application/json" \
  -H "X-API-Key: your-api-key" \
  -d '{"year": 2025, "round": 18}'
```

## Model Performance

The API uses an XGBoost Ranker model trained on historical F1 data (2017-2024) with the following performance metrics:

### Training Performance:
- **Top-3 Accuracy:** ~71%
- **Top-5 Accuracy:** ~84%
- **Mean Absolute Error:** ~3 positions

### Real-world Test Results:
- **Italy 2025 (Round 16):** Top-3: 66.7%, Top-5: 80%
- **Singapore 2025 (Round 18):** Top-3: 33.3%, Top-5: 60%

**Note:** Model performs better on traditional circuits compared to street circuits where grid positions are more likely to be maintained.

## Data Sources

- **Predictions:** Based on qualifying results and historical driver/constructor performance
- **Race Results:** Fetched from Ergast API (https://api.jolpi.ca/ergast/f1)
- **Model Training:** Historical F1 data from 2017-2024

## Rate Limits

Currently no rate limits are implemented. Please use the API responsibly.

## Support

For issues or questions, please contact the development team.
