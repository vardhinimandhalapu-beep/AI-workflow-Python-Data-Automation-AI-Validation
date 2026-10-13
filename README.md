# NovaFlow

NovaFlow is a small Python project for validating a quarterly-metrics CSV, calculating changes, and viewing or exporting the results. It is a student portfolio MVP; calculations are deterministic Python rules. **There is no AI/LLM integration in the current implementation.**

## Features

- CSV schema and value validation with row-level errors.
- Arithmetic change, percentage change, trend direction, summary counts, and configurable threshold alerts.
- Local Flask dashboard and JSON API.
- JSON and Excel downloads.
- CLI validation, analysis, and report generation.
- Sample data for trying the workflow.

## Requirements

Python 3.8 or newer. Runtime dependencies are Flask and openpyxl.

### Windows PowerShell

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python -m pip install pytest
```

### Linux or macOS

```bash
python3 -m venv .venv
. .venv/bin/activate
python -m pip install -r requirements.txt
python -m pip install pytest
```

## Run

From the repository root:

```bash
python app.py
```

Open http://127.0.0.1:5000. The app binds to localhost and uses `data/metrics.csv`. Set `PORT` to change the port.

CLI commands:

```bash
python src/cli.py validate data/metrics.csv
python src/cli.py analyze data/metrics.csv
python src/cli.py report data/metrics.csv
python src/cli.py serve data/metrics.csv
```

Errors return a non-zero exit code. The report command writes timestamped JSON and HTML files to `output/reports/`.

## Data format and calculations

Required columns are `metric,q1,q2,unit`. Extra columns are allowed. Metric names must be unique (case-insensitive), numeric values must be finite, and files are limited to 10 MiB. Zero and negative measurements are allowed.

```csv
metric,q1,q2,unit
users,82400,101600,users
revenue,1.84,2.21,crore_inr
retention,91.1,89.4,percent
```

Absolute change is Q2 minus Q1. Percentage change is unavailable when Q1 is zero; those values are excluded from the average rather than treated as 0%. “UP” and “DOWN” describe arithmetic direction only. The default alert threshold is an absolute change of at least 10%; it does not infer whether a change is good or bad.

## Web endpoints

- `/` — dashboard.
- `/api/summary` — JSON summary, metrics, and threshold alerts.
- `/export/json` — downloadable JSON.
- `/export/excel` — downloadable Excel workbook.
- `/health` — local health response.

## Architecture

- `src/main.py` — validation, calculations, report generation, and workflow orchestration.
- `src/cli.py` — command line interface.
- `app.py` — Flask routes and exports.
- `templates/dashboard.html` — autoescaped Jinja dashboard.
- `data/metrics.csv` — illustrative sample values, not customer data.
- `tests/` — automated regression and route tests.

Root `main.py` is a compatibility entry point; `src/main.py` is the authoritative implementation.

## Tests

Install the runtime requirements and pytest, then run:

```bash
python -m pytest -q
```

## Security and limitations

The app is intended for local use and binds to `127.0.0.1`; it has no authentication, upload feature, or deployment configuration. CSV metric labels are escaped in generated HTML and spreadsheet formula prefixes are neutralized in Excel exports. The 10 MiB CSV limit is intended for a local MVP. Review sample and input data before sharing exports. There is no AI model, business-aware metric direction, persistence layer, or production monitoring.
