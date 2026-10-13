# Architecture

NovaFlow is a local CSV analytics MVP with one Python core used by both its CLI and Flask app.

## Data flow

```
CSV file
  -> DataValidator.load_csv
  -> DataValidator.validate_dataset
  -> DataAnalyzer
  -> Flask dashboard / JSON API / JSON and Excel downloads
                    \-> CLI analysis and generated HTML/JSON reports
```

## Responsibilities

- `src/main.py` owns CSV validation, metric calculations, and standalone report generation.
- `src/cli.py` exposes validation, analysis, report, and local serving commands.
- `app.py` exposes the local Flask dashboard, API, health, and export routes.
- `templates/dashboard.html` is an autoescaped Jinja template.
- `tests/` covers core calculations, validation, report generation, and Flask routes.

The root `main.py` is a compatibility launcher that delegates to `src/main.py`. Runtime dependencies are Flask and openpyxl; the standard library handles CSV and JSON. The current implementation does not call an AI model or external service.
