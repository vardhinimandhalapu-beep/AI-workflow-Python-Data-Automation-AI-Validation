from flask import Flask, jsonify, render_template, request, send_file
from pathlib import Path
from openpyxl import Workbook

from src.main import App, DataAnalyzer, DataValidator

app = Flask(__name__, template_folder="../templates", static_folder="../static")


def load_analysis(csv_path: str = "data/metrics.csv"):
    path = Path(csv_path)
    if not path.exists():
        raise FileNotFoundError(f"Dataset not found: {csv_path}")

    rows = DataValidator.load_csv(path)
    valid, errors = DataValidator.validate_dataset(rows)
    if not valid:
        raise ValueError("\n".join(errors))

    metrics = DataAnalyzer.load_metrics(rows)
    summary = DataAnalyzer.calculate_summary(metrics)
    critical = DataAnalyzer.identify_critical_metrics(metrics)
    return metrics, summary, critical


@app.route("/")
def dashboard():
    metrics, summary, critical = load_analysis()
    return render_template(
        "dashboard.html",
        metrics=metrics,
        summary=summary,
        critical=critical,
        generated_at="Now"
    )


@app.route("/api/summary")
def api_summary():
    metrics, summary, critical = load_analysis()
    return jsonify({
        "summary": summary,
        "metrics": [
            {
                "name": m.name,
                "q1": m.q1_value,
                "q2": m.q2_value,
                "unit": m.unit,
                "absolute_change": m.absolute_change(),
                "percentage_change": m.percentage_change(),
                "trend": m.trend(),
            }
            for m in metrics
        ],
        "critical": [m.name for m in critical]
    })


@app.route("/export/json")
def export_json():
    metrics, summary, critical = load_analysis()
    output_dir = Path("output/reports")
    output_dir.mkdir(exist_ok=True, parents=True)
    report_path = output_dir / "novaflow_export.json"

    payload = [
        {
            "name": m.name,
            "q1": m.q1_value,
            "q2": m.q2_value,
            "unit": m.unit,
            "absolute_change": m.absolute_change(),
            "percentage_change": m.percentage_change(),
            "trend": m.trend(),
        }
        for m in metrics
    ]

    with report_path.open("w", encoding="utf-8") as file:
        import json
        json.dump(payload, file, indent=2)

    return send_file(report_path, as_attachment=True, download_name="novaflow_export.json")


@app.route("/export/excel")
def export_excel():
    metrics, summary, critical = load_analysis()
    output_dir = Path("output/reports")
    output_dir.mkdir(exist_ok=True, parents=True)
    report_path = output_dir / "novaflow_export.xlsx"

    workbook = Workbook()
    sheet = workbook.active
    sheet.title = "NovaFlow Metrics"
    sheet.append(["Metric", "Q1", "Q2", "Absolute Change", "Percentage Change", "Trend"])

    for metric in metrics:
        sheet.append([
            metric.name,
            metric.q1_value,
            metric.q2_value,
            metric.absolute_change(),
            metric.percentage_change(),
            metric.trend(),
        ])

    workbook.save(report_path)
    return send_file(report_path, as_attachment=True, download_name="novaflow_export.xlsx")


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=True)
