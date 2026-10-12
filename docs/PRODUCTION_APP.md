# Portfolio-ready production app

This project has been upgraded into a production-style analytics dashboard that can be opened locally in the browser and exported to JSON/Excel.

## Features

- Professional dashboard UI
- Data validation and metrics analysis
- Browser-based dashboard served locally
- Export to JSON and Excel
- Clean project structure and documentation
- Reusable core analysis modules

## Run the web app

```bash
python app.py
```

Then open:

```text
http://127.0.0.1:5000/
```

## CLI commands

```bash
python src/main.py
python src/cli.py validate data/metrics.csv
python src/cli.py analyze data/metrics.csv
python src/cli.py report data/metrics.csv
python src/cli.py serve data/metrics.csv
```

## Reports

Generated output files are saved in:

```text
output/reports/
```

## Requirements

```bash
pip install -r requirements.txt
```

The project now includes:
- Flask for the web dashboard
- openpyxl for Excel export
