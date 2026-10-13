#!/usr/bin/env python3
"""NovaFlow CSV validation, analysis, and report generation."""

import csv
import html
import json
import math
import os
import sys
import webbrowser
from dataclasses import dataclass
from datetime import datetime
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple


@dataclass
class Metric:
    """A single metric observed in two periods."""

    name: str
    q1_value: float
    q2_value: float
    unit: str

    def absolute_change(self) -> float:
        return self.q2_value - self.q1_value

    def percentage_change(self) -> Optional[float]:
        if self.q1_value == 0:
            return None
        return (self.absolute_change() / self.q1_value) * 100

    def trend(self) -> str:
        change = self.absolute_change()
        return "UP" if change > 0 else "DOWN" if change < 0 else "FLAT"


class DataValidator:
    """Loads and validates the documented CSV schema."""

    REQUIRED_FIELDS = {"metric", "q1", "q2", "unit"}
    MAX_FILE_BYTES = 10 * 1024 * 1024

    @staticmethod
    def load_csv(filepath: Path) -> List[Dict[str, str]]:
        filepath = Path(filepath)
        if not filepath.is_file():
            raise FileNotFoundError("CSV file not found: {}".format(filepath))
        if filepath.stat().st_size > DataValidator.MAX_FILE_BYTES:
            raise ValueError("CSV file exceeds the 10 MiB size limit.")
        try:
            with filepath.open("r", encoding="utf-8-sig", newline="") as source:
                reader = csv.DictReader(source, strict=True)
                headers = reader.fieldnames or []
                if not headers:
                    return []
                if len(headers) != len(set(headers)):
                    raise ValueError("CSV contains duplicate column names.")
                missing = DataValidator.REQUIRED_FIELDS - set(headers)
                if missing:
                    raise ValueError("CSV is missing required columns: {}".format(", ".join(sorted(missing))))
                return list(reader)
        except UnicodeDecodeError as exc:
            raise ValueError("CSV must use UTF-8 encoding.") from exc
        except csv.Error as exc:
            raise ValueError("Malformed CSV: {}".format(exc)) from exc

    @staticmethod
    def validate_dataset(rows: List[Dict[str, str]]) -> Tuple[bool, List[str]]:
        if not rows:
            return False, ["Dataset is empty or contains a header only."]
        errors: List[str] = []
        seen = set()
        for row_number, row in enumerate(rows, start=2):
            if None in row:
                errors.append("Row {}: contains more values than the header.".format(row_number))
            missing = DataValidator.REQUIRED_FIELDS - set(row.keys())
            if missing:
                errors.append("Row {}: missing fields {}.".format(row_number, ", ".join(sorted(missing))))
                continue
            name = (row.get("metric") or "").strip()
            unit = (row.get("unit") or "").strip()
            if not name:
                errors.append("Row {}: metric name is blank.".format(row_number))
            elif name.casefold() in seen:
                errors.append("Row {}: duplicate metric name {!r}.".format(row_number, name))
            else:
                seen.add(name.casefold())
            if not unit:
                errors.append("Row {}: unit is blank.".format(row_number))
            for field in ("q1", "q2"):
                raw = row.get(field)
                if raw is None or not str(raw).strip():
                    errors.append("Row {}: {} is blank.".format(row_number, field))
                    continue
                try:
                    value = float(raw)
                    if not math.isfinite(value):
                        errors.append("Row {}: {} must be a finite number.".format(row_number, field))
                except (TypeError, ValueError):
                    errors.append("Row {}: {} must be numeric.".format(row_number, field))
        return not errors, errors


class DataAnalyzer:
    """Converts validated rows to metrics and calculates summaries."""

    @staticmethod
    def load_metrics(rows: List[Dict[str, str]]) -> List[Metric]:
        return [
            Metric(row["metric"].strip(), float(row["q1"]), float(row["q2"]), row["unit"].strip())
            for row in rows
        ]

    @staticmethod
    def calculate_summary(metrics: List[Metric]) -> Dict[str, Any]:
        changes = [m.percentage_change() for m in metrics]
        defined = [value for value in changes if value is not None]
        return {
            "total_metrics": len(metrics),
            "up_trends": sum(m.trend() == "UP" for m in metrics),
            "down_trends": sum(m.trend() == "DOWN" for m in metrics),
            "flat_trends": sum(m.trend() == "FLAT" for m in metrics),
            "avg_percentage_change": round(sum(defined) / len(defined), 2) if defined else None,
        }

    @staticmethod
    def identify_critical_metrics(metrics: List[Metric], threshold_pct: float = 10.0) -> List[Metric]:
        if threshold_pct < 0 or not math.isfinite(threshold_pct):
            raise ValueError("threshold_pct must be a finite, non-negative number.")
        critical = [m for m in metrics if m.percentage_change() is not None and abs(m.percentage_change()) >= threshold_pct]
        return sorted(critical, key=lambda m: abs(m.percentage_change() or 0), reverse=True)


class ReportGenerator:
    """Builds escaped standalone HTML reports."""

    @staticmethod
    def build_dashboard(metrics: List[Metric], summary: Dict[str, Any]) -> str:
        rows = []
        for metric in metrics:
            pct = metric.percentage_change()
            pct_label = "N/A" if pct is None else "{:+.2f}%".format(pct)
            rows.append(
                "<tr><td>{}</td><td>{:.2f}</td><td>{:.2f}</td><td>{:+.2f}</td>"
                "<td>{}</td><td>{}</td><td>{}</td></tr>".format(
                    html.escape(metric.name), metric.q1_value, metric.q2_value,
                    metric.absolute_change(), pct_label, html.escape(metric.unit), metric.trend()
                )
            )
        average = summary.get("avg_percentage_change")
        average_label = "N/A" if average is None else "{:+.2f}%".format(average)
        return """<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>NovaFlow report</title><style>
body{font:16px system-ui,sans-serif;max-width:1100px;margin:2rem auto;padding:0 1rem;color:#172033;background:#f7f9fc}
header,.panel{background:white;border:1px solid #dfe5ef;border-radius:12px;padding:1.25rem;margin-bottom:1rem}
h1{margin:.2rem 0;color:#12356b}table{width:100%;border-collapse:collapse}th,td{text-align:left;padding:.7rem;border-bottom:1px solid #e4e9f1}
th{background:#f1f5fb}small{color:#526176}
</style></head><body><header><h1>NovaFlow</h1><p>Quarterly metric analysis report</p>
<p>{} metrics · average defined percentage change: {}</p></header><section class="panel"><h2>Metrics</h2>
<table><thead><tr><th>Metric</th><th>Q1</th><th>Q2</th><th>Change</th><th>Change %</th><th>Unit</th><th>Trend</th></tr></thead>
<tbody>{}</tbody></table></section><small>Generated locally from the supplied CSV. Trend is arithmetic direction, not a judgment of business impact.</small>
</body></html>""".format(summary.get("total_metrics", 0), average_label, "".join(rows))

    @staticmethod
    def export_dashboard(metrics: List[Metric], summary: Dict[str, Any], output_path: Path) -> None:
        Path(output_path).write_text(ReportGenerator.build_dashboard(metrics, summary), encoding="utf-8")


class App:
    """Orchestrates the sample workflow and local report generation."""

    def __init__(self, project_dir: Optional[Path] = None) -> None:
        self.project_dir = Path(project_dir or Path(__file__).resolve().parents[1])
        self.data_dir = self.project_dir / "data"
        self.output_dir = self.project_dir / "output" / "reports"

    def create_sample_data(self) -> Path:
        self.data_dir.mkdir(exist_ok=True, parents=True)
        filepath = self.data_dir / "metrics.csv"
        if not filepath.exists():
            filepath.write_text(
                "metric,q1,q2,unit\nusers,82400,101600,users\nrevenue,1.84,2.21,crore_inr\n"
                "retention,91.1,89.4,percent\nsupport_time,7.2,10.6,hours\n"
                "crash_rate,1.4,2.7,percent\nai_assistant_adoption,24,38,percent\n",
                encoding="utf-8",
            )
        return filepath

    def analyze_data(self, csv_path: Path) -> Dict[str, Any]:
        rows = DataValidator.load_csv(csv_path)
        valid, errors = DataValidator.validate_dataset(rows)
        if not valid:
            raise ValueError("\n".join(errors))
        metrics = DataAnalyzer.load_metrics(rows)
        return {
            "metrics": metrics,
            "summary": DataAnalyzer.calculate_summary(metrics),
            "critical": DataAnalyzer.identify_critical_metrics(metrics),
        }

    def export_json(self, metrics: List[Metric], output_path: Path) -> None:
        payload = []
        for metric in metrics:
            payload.append({
                "name": metric.name, "q1": metric.q1_value, "q2": metric.q2_value, "unit": metric.unit,
                "absolute_change": metric.absolute_change(), "percentage_change": metric.percentage_change(),
                "trend": metric.trend(),
            })
        Path(output_path).write_text(json.dumps(payload, indent=2, allow_nan=False), encoding="utf-8")

    def generate_reports(self, csv_path: Path) -> Dict[str, str]:
        analysis = self.analyze_data(csv_path)
        self.output_dir.mkdir(exist_ok=True, parents=True)
        stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        json_path = self.output_dir / "report_{}.json".format(stamp)
        html_path = self.output_dir / "report_{}.html".format(stamp)
        self.export_json(analysis["metrics"], json_path)
        ReportGenerator.export_dashboard(analysis["metrics"], analysis["summary"], html_path)
        return {"json": str(json_path), "html": str(html_path)}

    def serve_report(self, html_path: Path) -> None:
        path = Path(html_path).resolve()
        if not path.is_file():
            raise FileNotFoundError("HTML report not found: {}".format(path))
        os.chdir(str(path.parent))
        server = ThreadingHTTPServer(("127.0.0.1", 8000), SimpleHTTPRequestHandler)
        print("Serving {} at http://127.0.0.1:8000/{}".format(path.name, path.name))
        webbrowser.open("http://127.0.0.1:8000/{}".format(path.name))
        try:
            server.serve_forever()
        except KeyboardInterrupt:
            pass
        finally:
            server.server_close()

    def run(self) -> None:
        data_file = self.create_sample_data()
        analysis = self.analyze_data(data_file)
        print(json.dumps(analysis["summary"], indent=2))
        print("Reports: {}".format(self.generate_reports(data_file)))


if __name__ == "__main__":
    try:
        App().run()
    except (OSError, ValueError) as exc:
        print("Error: {}".format(exc), file=sys.stderr)
        sys.exit(1)
