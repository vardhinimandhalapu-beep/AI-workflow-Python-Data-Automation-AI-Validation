# NovaFlow

NovaFlow validates a quarterly metrics CSV, calculates deterministic comparisons, and provides a local dashboard, CLI, and downloadable reports. It is a student portfolio MVP, not a deployed production service.

## Features

- CSV schema and value validation with row-level diagnostics.
- Absolute and percentage changes, arithmetic trend direction, summary counts, and threshold alerts.
- Local Flask dashboard and JSON API.
- JSON and Excel downloads, with formula-like text neutralized in Excel exports.
- CLI validation, analysis, and report generation.
- Optional, user-triggered OpenAI explanation of metric changes. Core functionality does not depend on AI.

## Requirements and setup

Python 3.10 or newer is required. Runtime dependencies are pinned in `requirements.txt`; pytest is included in development requirements.

### Windows PowerShell

```powershell
py -3.10 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r requirements-dev.txt
```

### Linux or macOS

```bash
python3.10 -m venv .venv
. .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -r requirements-dev.txt
```

## Run the application

From the repository root:

```bash
python app.py
```

Open http://127.0.0.1:5000. It binds to localhost and reads `data/metrics.csv`. Set `PORT` to change the port.

CLI commands:

```bash
python src/cli.py validate data/metrics.csv
python src/cli.py analyze data/metrics.csv
python src/cli.py report data/metrics.csv
python src/cli.py serve data/metrics.csv
```

The report command writes timestamped JSON and HTML files to `output/reports/`. Invalid input and file errors produce a non-zero CLI exit status.

## CSV schema and calculations

The required headers are `metric,q1,q2,unit`. Additional columns are accepted. Header names must match the required names exactly. Data rows must have the required values; metric names are unique case-insensitively, metric names and units cannot be blank, and numeric values must be finite. Empty/header-only files, malformed CSV, invalid UTF-8, duplicate headers, and files larger than 10 MiB are rejected. Zero and negative measurements are allowed.

```csv
metric,q1,q2,unit
users,82400,101600,users
revenue,1.84,2.21,crore_inr
retention,91.1,89.4,percent
```

Absolute change is Q2 minus Q1. Percentage change is undefined when Q1 is zero; undefined values are excluded from the average. “UP” and “DOWN” describe arithmetic direction only, not whether a change is desirable. The default alert threshold is an absolute percentage change of at least 10%.

## Web routes

- `/` — dashboard.
- `/api/summary` — JSON summary, metric values, calculations, and threshold alerts.
- `/api/ai-insights` — POST endpoint used by the explicit dashboard action; requires JSON `{"confirm": true}`.
- `/export/json` — downloadable JSON.
- `/export/excel` — downloadable XLSX workbook.
- `/health` — local health response.

## Optional AI explanations

AI is disabled by default. The dashboard never contacts a model on page load. When enabled, a user must press **Generate AI explanation**. That action sends only the validated metric names, units, Q1/Q2 values, and calculated changes—not the CSV file—to the OpenAI API configured for the project. Do not enable this for sensitive or confidential metrics; labels and values leave the local machine and are subject to the configured provider's terms and data handling.

Set the credentials and model name in your local process environment. The model must be one available to your OpenAI account; NovaFlow does not choose or invent a default.

Windows PowerShell:

```powershell
$env:NOVAFLOW_AI_ENABLED = "true"
$env:OPENAI_API_KEY = "<your API key>"
$env:OPENAI_MODEL = "<model available to your account>"
python app.py
```

Linux or macOS:

```bash
export NOVAFLOW_AI_ENABLED=true
export OPENAI_API_KEY="<your API key>"
export OPENAI_MODEL="<model available to your account>"
python app.py
```

Keep keys private. Do not paste them into source files, commits, screenshots, or issue reports. `.env` is ignored by Git; the app does not automatically load dotenv files. The API request uses a 20-second timeout, no automatic retries, bounded metric count/output, and `store=False`. Provider errors are returned as safe messages. If AI is off, unconfigured, or unavailable, the CSV validation, calculations, dashboard, CLI, and exports remain usable. AI text is a generated interpretation, may be inaccurate, and is not financial, medical, or authoritative business advice. The deterministic values shown by NovaFlow remain the source of truth.

## Architecture and checks

- `src/main.py` — CSV validation, calculations, reports, and workflow orchestration.
- `src/cli.py` — command line interface.
- `src/ai_insights.py` — bounded optional OpenAI integration.
- `app.py` — Flask routes and downloads.
- `templates/dashboard.html` — autoescaped dashboard.
- `data/metrics.csv` — illustrative sample values, not customer data.
- `tests/` — automated regression tests.

Run all tests and the sample CLI workflow:

```bash
python -m pytest -q
python src/cli.py validate data/metrics.csv
python src/cli.py analyze data/metrics.csv
python src/cli.py report data/metrics.csv
```

GitHub Actions tests Python 3.10 and 3.12 on Ubuntu and Windows. AI tests use a mocked provider; a real API key is not required. A live provider request and browser-based visual review are not part of automated verification.

## Security and project limits

The app is intended for local use and binds to `127.0.0.1`; it has no authentication, upload feature, deployment configuration, or production monitoring. HTML templates escape metric labels, generated HTML reports escape text, and untrusted Excel labels/units are neutralized. Review source data and exports before sharing. The project has no persistence layer or business-aware interpretation of metric direction.
