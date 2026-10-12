#!/usr/bin/env python3
"""NovaFlow Data Analysis System.

Professional business-metrics analytics for validating a quarterly dataset,
calculating trend deltas, and exporting a polished HTML report.

Features:
- dataset validation
- Q1 to Q2 change calculations
- trend summaries
- critical metric detection
- HTML report generation
- JSON export
- no third-party dependencies
"""

import csv
import json
import sys
from dataclasses import dataclass
from datetime import datetime
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
                metrics.append(
                    Metric(
                        name=row["metric"].strip(),
                        q1_value=float(row["q1"]),
                        q2_value=float(row["q2"]),
                        unit=row["unit"].strip(),
                    )
                )
            except (KeyError, TypeError, ValueError):
                continue
        return metrics

    @staticmethod
    def calculate_summary(metrics: List[Metric]) -> Dict[str, Any]:
        if not metrics:
            return {}

        up_count = sum(1 for metric in metrics if metric.trend() == "UP")
        down_count = sum(1 for metric in metrics if metric.trend() == "DOWN")
        flat_count = sum(1 for metric in metrics if metric.trend() == "FLAT")

        pct_values = [
            metric.percentage_change()
            for metric in metrics
            if metric.percentage_change() is not None
        ]
        avg_pct = (
            round(sum(pct_values) / len(pct_values), 2) if pct_values else 0.0
        )
        total_points = len(metrics)

        return {
            "total_metrics": total_points,
            "up_trends": up_count,
            "down_trends": down_count,
            "flat_trends": flat_count,
            "avg_percentage_change": avg_pct,
        }

    @staticmethod
    def identify_critical_metrics(
        metrics: List[Metric], threshold_pct: float = 10.0
    ) -> List[Metric]:
        critical: List[Metric] = []
        for metric in metrics:
            pct = metric.percentage_change()
            if pct is not None and abs(pct) >= threshold_pct:
                critical.append(metric)
        return sorted(
            critical,
            key=lambda item: abs(item.percentage_change() or 0),
            reverse=True,
        )


class ReportBuilder:
    @staticmethod
    def render_bar(value: float, max_value: float, color: str = "#1f77b4") -> str:
        if max_value == 0:
            width = 0
        else:
            width = min(100, max(0, (abs(value) / max_value) * 100))
        return (
            f'<div class="bar-track"><div class="bar-fill" '
            f'style="width:{width:.1f}%; background:{color};"></div></div>'
        )

    @staticmethod
    def build_html(metrics: List[Metric], summary: Dict[str, Any]) -> str:
        max_change = max(
            (abs(metric.percentage_change() or 0) for metric in metrics),
            default=1,
        )

        rows_html = "\n".join(
            [
                """
                <tr>
                  <td>{name}</td>
                  <td>{q1}</td>
                  <td>{q2}</td>
                  <td>{abs_change:+.2f}</td>
                  <td>{pct:+.2f}%</td>
                  <td><span class="pill {trend_class}">{trend}</span></td>
                  <td>{bar}</td>
                </tr>
                """.format(
                    name=metric.name,
                    q1=f"{metric.q1_value:.2f}",
                    q2=f"{metric.q2_value:.2f}",
                    abs_change=metric.absolute_change(),
                    pct=metric.percentage_change() if metric.percentage_change() is not None else 0,
                    trend=metric.trend(),
                    trend_class=metric.trend().lower(),
                    bar=ReportBuilder.render_bar(
                        metric.percentage_change() if metric.percentage_change() is not None else 0,
                        max_change,
                        color="#2563eb" if metric.trend() == "UP" else "#dc2626" if metric.trend() == "DOWN" else "#6b7280",
                    ),
                )
                for metric in metrics
            ]
        )

        html = f"""<!DOCTYPE html>
<html lang=\"en\">
<head>
  <meta charset=\"UTF-8\" />
  <meta name=\"viewport\" content=\"width=device-width, initial-scale=1.0\" />
  <title>NovaFlow Data Analysis</title>
  <style>
    :root {{
      --bg: #f8fafc;
      --panel: #ffffff;
      --primary: #2563eb;
      --primary-soft: #dbeafe;
      --success: #16a34a;
      --danger: #dc2626;
      --neutral: #6b7280;
      --text: #0f172a;
      --muted: #475569;
      --border: #e2e8f0;
    }}
    * {{ box-sizing: border-box; }}
    body {{
      margin: 0;
      font-family: Arial, Helvetica, sans-serif;
      background: var(--bg);
      color: var(--text);
    }}
    .container {{ max-width: 1200px; margin: 32px auto; padding: 0 20px; }}
    .header {{
      background: linear-gradient(135deg, #0f172a, #1d4ed8);
      color: white;
      border-radius: 16px;
      padding: 32px;
      margin-bottom: 24px;
      box-shadow: 0 12px 24px rgba(15, 23, 42, 0.15);
    }}
    h1 {{ margin: 0; font-size: 2.2rem; }}
    .sub {{ opacity: 0.9; margin-top: 12px; }}
    .cards {{
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
      gap: 18px;
      margin: 24px 0;
    }}
    .card {{
      background: var(--panel);
      border: 1px solid var(--border);
      border-radius: 14px;
      padding: 20px;
      box-shadow: 0 4px 12px rgba(15, 23, 42, 0.04);
    }}
    .label {{ color: var(--muted); font-size: 0.8rem; text-transform: uppercase; letter-spacing: 0.05em; }}
    .value {{ font-size: 2rem; font-weight: 700; margin-top: 10px; }}
    table {{
      width: 100%;
      border-collapse: collapse;
      background: var(--panel);
      border: 1px solid var(--border);
      border-radius: 12px;
      overflow: hidden;
    }}
    th, td {{
      padding: 14px 12px;
      border-bottom: 1px solid var(--border);
      text-align: left;
    }}
    th {{ background: #f8fafc; }}
    .pill {{
      display: inline-block;
      padding: 7px 10px;
      border-radius: 999px;
      font-size: 0.75rem;
      font-weight: 700;
      letter-spacing: 0.04em;
      text-transform: uppercase;
    }}
    .pill.up {{ background: rgba(22, 163, 74, 0.12); color: var(--success); }}
    .pill.down {{ background: rgba(220, 38, 38, 0.12); color: var(--danger); }}
    .pill.flat {{ background: rgba(107, 114, 128, 0.12); color: var(--neutral); }}
    .bar-track {{
      width: 180px;
      height: 12px;
      background: #e5e7eb;
      border-radius: 999px;
      overflow: hidden;
    }}
    .bar-fill {{
      height: 100%;
      border-radius: 999px;
      min-width: 4px;
    }}
    .note {{ margin-top: 18px; color: var(--muted); }}
  </style>
</head>
<body>
  <div class=\"container\">
    <div class=\"header\">
      <h1>NovaFlow Performance Summary</h1>
      <div class=\"sub\">Quarterly business metric review and trend analysis</div>
    </div>

    <div class=\"cards\">
      <div class=\"card\">
        <div class=\"label\">Total Metrics</div>
        <div class=\"value\">{summary.get('total_metrics', 0)}</div>
      </div>
      <div class=\"card\">
        <div class=\"label\">Improving</div>
        <div class=\"value\" style=\"color: var(--success);\">{summary.get('up_trends', 0)}</div>
      </div>
      <div class=\"card\">
        <div class=\"label\">Declining</div>
        <div class=\"value\" style=\"color: var(--danger);\">{summary.get('down_trends', 0)}</div>
      </div>
      <div class=\"card\">
        <div class=\"label\">Avg Change</div>
        <div class=\"value\" style=\"color: var(--primary);\">{summary.get('avg_percentage_change', 0):+.2f}%</div>
      </div>
    </div>

    <table>
      <thead>
        <tr>
          <th>Metric</th>
          <th>Q1</th>
          <th>Q2</th>
          <th>Abs Change</th>
          <th>% Change</th>
          <th>Trend</th>
          <th>Visual</th>
        </tr>
      </thead>
      <tbody>
        {rows_html}
      </tbody>
    </table>

    <div class=\"note\">
      Generated on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}.
    </div>
  </div>
</body>
</html>
"""
        return html


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

        sample_rows = [
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
            writer.writerows(sample_rows)
        return filepath

    def run_analysis(self, file_path: Path) -> Dict[str, Any]:
        rows = DataValidator.load_csv(file_path)
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

    def export_json(self, metrics: List[Metric], filepath: Path) -> None:
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
        with filepath.open("w", encoding="utf-8") as file:
            json.dump(payload, file, indent=2)

    def export_html(self, metrics: List[Metric], summary: Dict[str, Any], filepath: Path) -> None:
        html = ReportBuilder.build_html(metrics, summary)
        with filepath.open("w", encoding="utf-8") as file:
            file.write(html)

    def run(self) -> None:
        data_file = self.create_sample_data()
        print("NovaFlow Analytics Dashboard")
        print("=" * 40)
        print(f"Using dataset: {data_file}")

        try:
            result = self.run_analysis(data_file)
        except Exception as exc:
            print(f"Validation failed: {exc}")
            sys.exit(1)

        metrics = result["metrics"]
        summary = result["summary"]
        critical = result["critical"]

        print("\nSummary")
        print(f"Total Metrics: {summary.get('total_metrics', 0)}")
        print(f"Improving: {summary.get('up_trends', 0)}")
        print(f"Declining: {summary.get('down_trends', 0)}")
        print(f"Average Change: {summary.get('avg_percentage_change', 0):+.2f}%")

        print("\nCritical metrics")
        if critical:
            for metric in critical:
                pct = metric.percentage_change()
                print(f"- {metric.name}: {pct:+.2f}% ({metric.trend()})")
        else:
            print("No critical metrics above threshold")

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        json_path = self.output_dir / f"novaflow_report_{timestamp}.json"
        html_path = self.output_dir / f"novaflow_report_{timestamp}.html"

        self.export_json(metrics, json_path)
        self.export_html(metrics, summary, html_path)

        print(f"\nJSON report written to: {json_path}")
        print(f"HTML dashboard written to: {html_path}")
        print("\nProject is running successfully.")


if __name__ == "__main__":
    try:
        App().run()
    except KeyboardInterrupt:
        print("\nExecution interrupted by user.")
        sys.exit(0)
    except Exception as exc:
        print(f"Unexpected error: {exc}")
        sys.exit(1)


















































































































































