# API Reference

## Core Classes

### Metric

Represents a single quarterly business metric.

```python
from src.main import Metric

metric = Metric(
    name="users",
    q1_value=82400,
    q2_value=101600,
    unit="users"
)

# Calculate changes
abs_change = metric.absolute_change()      # 19200
pct_change = metric.percentage_change()    # 23.29
trend = metric.trend()                     # "UP"
```

### DataValidator

Validates CSV datasets.

```python
from src.main import DataValidator

rows = DataValidator.load_csv(Path("data/metrics.csv"))
valid, errors = DataValidator.validate_dataset(rows)
```

### DataAnalyzer

Analyzes metrics and generates insights.

```python
from src.main import DataAnalyzer

metrics = DataAnalyzer.load_metrics(rows)
summary = DataAnalyzer.calculate_summary(metrics)
critical = DataAnalyzer.identify_critical_metrics(metrics)
```

### ReportGenerator

Generates HTML dashboards.

```python
from src.main import ReportGenerator

html = ReportGenerator.build_dashboard(metrics, summary)
ReportGenerator.export_dashboard(metrics, summary, Path("output.html"))
```

### App

Main application controller.

```python
from src.main import App

app = App()
app.run()  # Run complete workflow
reports = app.generate_reports(Path("data/metrics.csv"))
app.serve_report(Path("output/report.html"))
```
