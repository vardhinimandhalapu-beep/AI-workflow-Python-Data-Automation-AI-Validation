# Usage Guide

## Quick Start

### Running the Main Analysis

```bash
python src/main.py
```

This will:
1. Load or create sample data
2. Validate the dataset
3. Run analysis
4. Generate reports
5. Display summary

### Using the CLI

#### Validate Data
```bash
python src/cli.py validate data/metrics.csv
```

#### Run Analysis
```bash
python src/cli.py analyze data/metrics.csv
```

#### Generate Reports
```bash
python src/cli.py report data/metrics.csv
```

#### View Dashboard in Browser
```bash
python src/cli.py serve data/metrics.csv
```

## Data Format

The CSV file must have 4 columns:

```csv
metric,q1,q2,unit
users,82400,101600,users
revenue,1.84,2.21,crore_inr
retention,91.1,89.4,percent
```

## Output Files

Reports are saved to `output/reports/`:

- `report_YYYYMMDD_HHMMSS.json` - JSON data export
- `report_YYYYMMDD_HHMMSS.html` - Interactive dashboard

## Interpreting Results

### Trend Indicators
- **UP** (↑) - Metric increased from Q1 to Q2
- **DOWN** (↓) - Metric decreased from Q1 to Q2
- **FLAT** (→) - No change from Q1 to Q2

### Critical Metrics
Metrics with >10% change are flagged as critical and highlighted in the dashboard.

## Customization

Edit `config/settings.py` to adjust:
- Critical metric threshold
- Server host/port
- Output directories
