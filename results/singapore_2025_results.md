## Singapore Grand Prix 2025 — Model Prediction vs Actual

- Event: Marina Bay Street Circuit (Round 18)
- Date: 2025-10-05

### Model Top 10 Prediction

| Rank | Driver | Grid |
|---:|:------|---:|
| 1 | NOR | 5 |
| 2 | ANT | 4 |
| 3 | VER | 2 |
| 4 | RUS | 1 |
| 5 | GAS | 18 |
| 6 | PIA | 3 |
| 7 | HAD | 8 |
| 8 | LEC | 7 |
| 9 | HAM | 6 |
| 10 | BOR | 14 |

### Actual Top 10 Result (Provisional)

| Pos | Driver |
|---:|:------|
| 1 | RUS (George Russell) |
| 2 | VER (Max Verstappen) |
| 3 | NOR (Lando Norris) |
| 4 | PIA (Oscar Piastri) |
| 5 | ANT (Andrea Kimi Antonelli) |
| 6 | LEC (Charles Leclerc) |
| 7 | HAM (Lewis Hamilton) |
| 8 | ALO (Fernando Alonso) |
| 9 | BEA (Oliver Bearman) |
| 10 | SAI (Carlos Sainz Jr.) |

### Evaluation Metrics

- Top-3 hit rate: 66.7% (matched: VER, NOR)
- Top-5 hit rate: 80.0% (matched: RUS, VER, NOR, ANT; missed: PIA)
- Exact-order accuracy within Top-5: 0/5

Notes:
- Predictions generated using `models/xgboost/xgboost_ranker_model.pkl` with qualifying grid as input features for Singapore 2025 only.
- Actual results sourced from provisional classification provided by the user at the time of writing.


