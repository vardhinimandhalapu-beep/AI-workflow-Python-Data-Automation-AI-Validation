# API and core usage

NovaFlow exposes a small Python API and local Flask routes. The authoritative implementation is `src/main.py`.

## Python classes

```python
from pathlib import Path
from src.main import App, DataAnalyzer, DataValidator, Metric

metric = Metric("users", 82400, 101600, "users")
print(metric.absolute_change())   # 19200
print(metric.percentage_change()) # about 23.30
print(metric.trend())             # UP (direction only)

rows = DataValidator.load_csv(Path("data/metrics.csv"))
valid, errors = DataValidator.validate_dataset(rows)
if not valid:
    raise ValueError("\n".join(errors))
metrics = DataAnalyzer.load_metrics(rows)
summary = DataAnalyzer.calculate_summary(metrics)
alerts = DataAnalyzer.identify_critical_metrics(metrics, threshold_pct=10.0)
```

A zero Q1 baseline has no defined percentage change and is excluded from the average. The default alert threshold uses absolute percentage magnitude. Trend labels do not infer business impact.

## Flask routes

- `GET /` — renders the dashboard.
- `GET /api/summary` — returns a JSON object containing `summary`, `metrics`, and `critical`.
- `GET /export/json` — downloads summary, metric values, and alerts as JSON.
- `GET /export/excel` — downloads an Excel workbook.
- `GET /health` — returns a local service status.

The web app reads the path in `app.config["DATASET_PATH"]`, defaulting to `data/metrics.csv` at the repository root. Missing files return 404; invalid CSV data returns 400.
