#!/usr/bin/env python3
"""NovaFlow Advanced Analytics Dashboard.

This version turns the project into a more professional data-analytics workflow:
- validates quarter-over-quarter business data
- computes trend insights
- generates a polished HTML dashboard
- exports JSON analysis
- serves a local dashboard in browser

No external dependencies required. Works with Python 3.8+.
"""

import csv
import json
import os
import sys
import webbrowser
from dataclasses import dataclass
from datetime import datetime
from http.server import ThreadingHTTPServer, SimpleHTTPRequestHandler
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple


@dataclass
class Metric:
    name: str
    q1_value: float
    q2_value: float
    unit: str

    def absolute_change(self) -> float:
        return self.q2_value - self.q1_value

    def percentage_change(self) -> Optional[float]:
        if self.q1_value == 0:
            return None
        return ((self.q2_value - self.q1_value) / self.q1_value) * 100

    def trend(self) -> str:
        change = self.absolute_change()
        if change > 0:
            return "UP"
        if change < 0:
            return "DOWN"
        return "FLAT"


class DataValidator:
    REQUIRED_FIELDS = {"metric", "q1", "q2", "unit"}

    @staticmethod
    def load_csv(filepath: Path) -> List[Dict[str, str]]:
        if not filepath.exists():
            raise FileNotFoundError(f"File not found: {filepath}")
        with filepath.open("r", encoding="utf-8", newline="") as file:
            return list(csv.DictReader(file))

    @staticmethod
    def validate_dataset(rows: List[Dict[str, str]]) -> Tuple[bool, List[str]]:
        if not rows:
            return False, ["Dataset is empty."]

        errors: List[str] = []
        for row_number, row in enumerate(rows, start=2):
            missing = DataValidator.REQUIRED_FIELDS - set(row.keys())
            if missing:
                errors.append(f"Row {row_number}: missing fields {sorted(missing)}")

            for field in ["metric", "unit", "q1", "q2"]:
                if not row.get(field, "").strip():
                    errors.append(f"Row {row_number}: empty {field}")

            for field in ["q1", "q2"]:
                try:
                    float(row.get(field, "0"))
                except (TypeError, ValueError):
                    errors.append(f"Row {row_number}: {field} is not numeric")

        return len(errors) == 0, errors


class DataAnalyzer:
    @staticmethod
    def load_metrics(rows: List[Dict[str, str]]) -> List[Metric]:
        metrics: List[Metric] = []
        for row in rows:
            try:
                metric = Metric(
                    name=row["metric"].strip(),
                    q1_value=float(row["q1"]),
                    q2_value=float(row["q2"]),
                    unit=row["unit"].strip(),
                )
                metrics.append(metric)
            except (KeyError, TypeError, ValueError):
                continue
        return metrics

    @staticmethod
    def calculate_summary(metrics: List[Metric]) -> Dict[str, Any]:
        if not metrics:
            return {"total_metrics": 0, "up_trends": 0, "down_trends": 0, "flat_trends": 0, "avg_percentage_change": 0.0}

        up_count = sum(1 for metric in metrics if metric.trend() == "UP")
        down_count = sum(1 for metric in metrics if metric.trend() == "DOWN")
        flat_count = sum(1 for metric in metrics if metric.trend() == "FLAT")

        pct_values = [
            metric.percentage_change()
            for metric in metrics
            if metric.percentage_change() is not None
        ]
        avg_pct = round(sum(pct_values) / len(pct_values), 2) if pct_values else 0.0

        return {
            "total_metrics": len(metrics),
            "up_trends": up_count,
            "down_trends": down_count,
            "flat_trends": flat_count,
            "avg_percentage_change": avg_pct,
        }

    @staticmethod
    def identify_critical_metrics(metrics: List[Metric], threshold_pct: float = 10.0) -> List[Metric]:
        critical: List[Metric] = []
        for metric in metrics:
            pct = metric.percentage_change()
            if pct is not None and abs(pct) >= threshold_pct:
                critical.append(metric)
        return sorted(critical, key=lambda item: abs(item.percentage_change() or 0), reverse=True)


class ReportGenerator:
    @staticmethod
    def build_svg_chart(metrics: List[Metric], width: int = 760, height: int = 240) -> str:
        if not metrics:
            return "<svg width='760' height='240'></svg>"

        values = [metric.percentage_change() if metric.percentage_change() is not None else 0.0 for metric in metrics]
        max_abs = max(abs(v) for v in values) or 1.0
        margin_left = 40
        margin_right = 20
        margin_top = 20
        margin_bottom = 30
        chart_width = width - margin_left - margin_right
        chart_height = height - margin_top - margin_bottom

        points = []
        for index, value in enumerate(values):
            x = margin_left + (index * chart_width / max(1, len(values) - 1)) if len(values) > 1 else width / 2
            y = margin_top + chart_height - ((value + max_abs) / (2 * max_abs)) * chart_height
            points.append((x, y))

        polyline = " ".join(f"{x:.1f},{y:.1f}" for x, y in points)
        grid_lines = "".join(
            f"<line x1='{margin_left}' x2='{width - margin_right}' y1='{margin_top + i}' y2='{margin_top + i}' stroke='#e2e8f0' stroke-width='1' />"
            for i in range(0, chart_height + 1, 40)
        )

        return f"""
        <svg width='{width}' height='{height}' viewBox='0 0 {width} {height}' xmlns='http://www.w3.org/2000/svg'>
          {grid_lines}
          <polyline fill='none' stroke='#2563eb' stroke-width='4' points='{polyline}' stroke-linecap='round' stroke-linejoin='round' />
          {''.join(f"<circle cx='{x}' cy='{y}' r='5' fill='#1d4ed8' />" for x, y in points)}
        </svg>
        """

    @staticmethod
    def build_metrics_table(metrics: List[Metric]) -> str:
        rows = []
        for metric in metrics:
            pct = metric.percentage_change() if metric.percentage_change() is not None else 0.0
            trend = metric.trend()
            trend_class = trend.lower()
            rows.append(
                f"""
                <tr>
                  <td>{metric.name}</td>
                  <td>{metric.q1_value:.2f}</td>
                  <td>{metric.q2_value:.2f}</td>
                  <td>{metric.absolute_change():+.2f}</td>
                  <td>{pct:+.2f}%</td>
                  <td><span class='badge {trend_class}'>{trend}</span></td>
                </tr>
                """
            )
        return "\n".join(rows)

    @staticmethod
    def build_dashboard(metrics: List[Metric], summary: Dict[str, Any]) -> str:
        chart_svg = ReportGenerator.build_svg_chart(metrics)
        metric_rows = ReportGenerator.build_metrics_table(metrics)

        return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>NovaFlow Dashboard</title>
  <style>
    :root {{
      --bg: #f8fafc;
      --panel: #ffffff;
      --primary: #1d4ed8;
      --primary-soft: #dbeafe;
      --success: #16a34a;
      --danger: #dc2626;
      --neutral: #475569;
      --text: #0f172a;
      --muted: #64748b;
      --border: #e2e8f0;
    }}
    * {{ box-sizing: border-box; }}
    body {{
      margin: 0;
      font-family: Arial, Helvetica, sans-serif;
      background: linear-gradient(180deg, #f8fafc 0%, #eef4ff 100%);
      color: var(--text);
    }}
    .container {{ max-width: 1200px; margin: 0 auto; padding: 28px 20px 60px; }}
    .header {{
      background: linear-gradient(135deg, #0f172a, #1d4ed8);
      color: white;
      border-radius: 18px;
      padding: 28px 30px;
      box-shadow: 0 12px 30px rgba(15, 23, 42, 0.12);
    }}
    h1 {{ margin: 0; font-size: 2.3rem; }}
    .sub {{ margin-top: 12px; opacity: 0.9; font-size: 1rem; }}
    .cards {{
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
      gap: 18px;
      margin: 28px 0;
    }}
    .card {{
      background: var(--panel);
      border: 1px solid var(--border);
      border-radius: 16px;
      padding: 20px 18px;
      box-shadow: 0 6px 18px rgba(15, 23, 42, 0.04);
    }}
    .label {{
      font-size: 0.76rem;
      color: var(--muted);
      text-transform: uppercase;
      letter-spacing: 0.08em;
    }}
    .value {{
      margin-top: 12px;
      font-size: 2rem;
      font-weight: 700;
    }}
    .panel {{
      background: var(--panel);
      border: 1px solid var(--border);
      border-radius: 16px;
      padding: 22px;
      box-shadow: 0 6px 18px rgba(15, 23, 42, 0.04);
      margin-top: 20px;
    }}
    .panel h2 {{ margin-top: 0; font-size: 1.3rem; }}
    table {{
      width: 100%;
      border-collapse: collapse;
      margin-top: 12px;
    }}
    th, td {{
      padding: 12px 10px;
      text-align: left;
      border-bottom: 1px solid var(--border);
    }}
    th {{ background: #f8fafc; }}
    .badge {{
      display: inline-block;
      padding: 6px 10px;
      border-radius: 999px;
      font-size: 0.72rem;
      font-weight: 700;
      letter-spacing: 0.04em;
      text-transform: uppercase;
    }}
    .badge.up {{ background: rgba(22,163,74,0.12); color: var(--success); }}
    .badge.down {{ background: rgba(220,38,38,0.12); color: var(--danger); }}
    .badge.flat {{ background: rgba(71,85,105,0.12); color: var(--neutral); }}
    .chart-wrap {{
      border: 1px solid var(--border);
      border-radius: 12px;
      padding: 12px;
      background: linear-gradient(180deg, rgba(219,234,254,0.3) 0%, rgba(255,255,255,0.4) 100%);
    }}
    .meta {{
      margin-top: 14px;
      color: var(--muted);
      font-size: 0.95rem;
    }}
  </style>
</head>
<body>
  <div class="container">
    <div class="header">
      <h1>NovaFlow Quarterly Dashboard</h1>
      <div class="sub">Executive performance review with automated metric analysis</div>
    </div>

    <div class="cards">
      <div class="card">
        <div class="label">Total Metrics</div>
        <div class="value">{summary.get('total_metrics', 0)}</div>
      </div>
      <div class="card">
        <div class="label">Improving</div>
        <div class="value" style="color: var(--success);">{summary.get('up_trends', 0)}</div>
      </div>
      <div class="card">
        <div class="label">Declining</div>
        <div class="value" style="color: var(--danger);">{summary.get('down_trends', 0)}</div>
      </div>
      <div class="card">
        <div class="label">Avg Change</div>
        <div class="value" style="color: var(--primary);">{summary.get('avg_percentage_change', 0):+.2f}%</div>
      </div>
    </div>

    <div class="panel">
      <h2>Change Trend</h2>
      <div class="chart-wrap">{chart_svg}</div>
      <div class="meta">Percentage change by metric across Q1 and Q2</div>
    </div>

    <div class="panel">
      <h2>Metric Table</h2>
      <table>
        <thead>
          <tr>
            <th>Metric</th>
            <th>Q1</th>
            <th>Q2</th>
            <th>Abs Change</th>
            <th>% Change</th>
            <th>Trend</th>
          </tr>
        </thead>
        <tbody>
          {metric_rows}
        </tbody>
      </table>
    </div>
  </div>
</body>
</html>
"""

    @staticmethod
    def export_dashboard(metrics: List[Metric], summary: Dict[str, Any], output_path: Path) -> None:
        html = ReportGenerator.build_dashboard(metrics, summary)
        with output_path.open("w", encoding="utf-8") as file:
            file.write(html)


class App:
    def __init__(self) -> None:
        self.data_dir = Path("data")
        self.output_dir = Path("output")
        self.data_dir.mkdir(exist_ok=True)
        self.output_dir.mkdir(exist_ok=True)

    def create_sample_data(self) -> Path:
        filepath = self.data_dir / "metrics.csv"
        if filepath.exists():
            return filepath

        rows = [
            ["metric", "q1", "q2", "unit"],
            ["users", "82400", "101600", "users"],
            ["revenue", "1.84", "2.21", "crore_inr"],
            ["retention", "91.1", "89.4", "percent"],
            ["support_time", "7.2", "10.6", "hours"],
            ["crash_rate", "1.4", "2.7", "percent"],
            ["ai_assistant_adoption", "24", "38", "percent"],
        ]

        with filepath.open("w", encoding="utf-8", newline="") as file:
            writer = csv.writer(file)
            writer.writerows(rows)
        return filepath

    def analyze_data(self, csv_path: Path) -> Dict[str, Any]:
        rows = DataValidator.load_csv(csv_path)
        valid, errors = DataValidator.validate_dataset(rows)
        if not valid:
            raise ValueError("\n".join(errors))

        metrics = DataAnalyzer.load_metrics(rows)
        summary = DataAnalyzer.calculate_summary(metrics)
        critical = DataAnalyzer.identify_critical_metrics(metrics)

        return {
            "metrics": metrics,
            "summary": summary,
            "critical": critical,
        }

    def export_json(self, metrics: List[Metric], output_path: Path) -> None:
        payload = [
            {
                "name": metric.name,
                "q1": metric.q1_value,
                "q2": metric.q2_value,
                "unit": metric.unit,
                "absolute_change": metric.absolute_change(),
                "percentage_change": metric.percentage_change(),
                "trend": metric.trend(),
            }
            for metric in metrics
        ]

        with output_path.open("w", encoding="utf-8") as file:
            json.dump(payload, file, indent=2)

    def export_dashboard(self, metrics: List[Metric], summary: Dict[str, Any], output_path: Path) -> None:
        ReportGenerator.export_dashboard(metrics, summary, output_path)

    def generate_reports(self, csv_path: Path) -> Dict[str, str]:
        analysis = self.analyze_data(csv_path)
        metrics = analysis["metrics"]
        summary = analysis["summary"]

        stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        json_path = self.output_dir / f"novaflow_report_{stamp}.json"
        html_path = self.output_dir / f"novaflow_report_{stamp}.html"

        self.export_json(metrics, json_path)
        self.export_dashboard(metrics, summary, html_path)

        return {
            "json": str(json_path),
            "html": str(html_path),
        }

    def serve_report(self, html_path: Path) -> None:
        directory = str(html_path.parent)
        file = html_path.name
        os.chdir(directory)
        handler = SimpleHTTPRequestHandler
        httpd = ThreadingHTTPServer(("127.0.0.1", 8000), handler)
        print(f"Serving dashboard at http://127.0.0.1:8000/{file}")
        webbrowser.open(f"http://127.0.0.1:8000/{file}")
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\nServer shut down.")
            httpd.server_close()

    def run(self) -> None:
        data_file = self.create_sample_data()
        print("NovaFlow Advanced Analytics")
        print("=" * 40)
        print(f"Dataset: {data_file}")

        try:
            analysis = self.analyze_data(data_file)
        except Exception as exc:
            print(f"Validation failed: {exc}")
            sys.exit(1)

        metrics = analysis["metrics"]
        summary = analysis["summary"]
        critical = analysis["critical"]

        print("\nSummary")
        print(f"Total metrics: {summary.get('total_metrics', 0)}")
        print(f"Improving: {summary.get('up_trends', 0)}")
        print(f"Declining: {summary.get('down_trends', 0)}")
        print(f"Average change: {summary.get('avg_percentage_change', 0):+.2f}%")

        print("\nCritical metrics")
        if critical:
            for metric in critical:
                pct = metric.percentage_change()
                print(f"- {metric.name}: {pct:+.2f}%")
        else:
            print("No critical metrics above threshold.")

        reports = self.generate_reports(data_file)
        print(f"\nJSON report: {reports['json']}")
        print(f"HTML dashboard: {reports['html']}")
        print("\nRun complete.")


if __name__ == "__main__":
    try:
        App().run()
    except KeyboardInterrupt:
        print("\nExecution interrupted by user.")
        sys.exit(0)
    except Exception as exc:
        print(f"Unexpected error: {exc}")
        sys.exit(1)








































































