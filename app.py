"""Flask dashboard and download endpoints for NovaFlow."""
import json
import os
from io import BytesIO
from pathlib import Path

from flask import Flask, jsonify, render_template, request, send_file
from openpyxl import Workbook

from datetime import datetime

from src.ai_insights import AIInsightError, generate_ai_insight, is_ai_enabled
from src.main import DataAnalyzer, DataValidator

PROJECT_DIR = Path(__file__).resolve().parent
app = Flask(
    __name__,
    template_folder=str(PROJECT_DIR / "templates"),
    static_folder=str(PROJECT_DIR / "static"),
)
app.config.setdefault("DATASET_PATH", PROJECT_DIR / "data" / "metrics.csv")


def load_analysis(csv_path=None):
    """Load and validate the configured CSV before calculating results."""
    path = Path(csv_path or app.config["DATASET_PATH"])
    rows = DataValidator.load_csv(path)
    valid, errors = DataValidator.validate_dataset(rows)
    if not valid:
        raise ValueError("\n".join(errors))
    metrics = DataAnalyzer.load_metrics(rows)
    return metrics, DataAnalyzer.calculate_summary(metrics), DataAnalyzer.identify_critical_metrics(metrics)


def _safe_spreadsheet_text(value):
    """Prefix formula-like untrusted text so Excel treats it as a label."""
    text = str(value)
    if text.lstrip().startswith(("=", "+", "-", "@")) or text.startswith(("\t", "\r")):
        return "'" + text
    return text


def _metric_payload(metric):
    return {
        "name": metric.name,
        "q1": metric.q1_value,
        "q2": metric.q2_value,
        "unit": metric.unit,
        "absolute_change": metric.absolute_change(),
        "percentage_change": metric.percentage_change(),
        "trend": metric.trend(),
    }


@app.errorhandler(FileNotFoundError)
def missing_data(error):
    return jsonify({"error": str(error)}), 404


@app.errorhandler(ValueError)
def invalid_data(error):
    return jsonify({"error": str(error)}), 400


@app.route("/")
def dashboard():
    metrics, summary, critical = load_analysis()
    return render_template(
        "dashboard.html",
        metrics=metrics,
        summary=summary,
        critical=critical,
        generated_at=datetime.now().astimezone().strftime("%Y-%m-%d %H:%M %Z"),
        ai_enabled=is_ai_enabled(),
    )


@app.route("/api/summary")
def api_summary():
    metrics, summary, critical = load_analysis()
    return jsonify({
        "summary": summary,
        "metrics": [_metric_payload(metric) for metric in metrics],
        "critical": [metric.name for metric in critical],
    })


@app.route("/export/json")
def export_json():
    metrics, summary, critical = load_analysis()
    payload = json.dumps(
        {"summary": summary, "metrics": [_metric_payload(metric) for metric in metrics],
         "critical": [metric.name for metric in critical]},
        indent=2, allow_nan=False,
    ).encode("utf-8")
    return send_file(BytesIO(payload), mimetype="application/json", as_attachment=True,
                     download_name="novaflow_export.json")


@app.route("/export/excel")
def export_excel():
    metrics, summary, critical = load_analysis()
    workbook = Workbook()
    sheet = workbook.active
    sheet.title = "NovaFlow Metrics"
    sheet.append(["Metric", "Q1", "Q2", "Absolute Change", "Percentage Change", "Unit", "Trend"])
    for metric in metrics:
        # Guard both untrusted text columns against spreadsheet formulas.
        sheet.append([_safe_spreadsheet_text(metric.name), metric.q1_value, metric.q2_value,
                      metric.absolute_change(), metric.percentage_change(),
                      _safe_spreadsheet_text(metric.unit), metric.trend()])
    stream = BytesIO()
    workbook.save(stream)
    stream.seek(0)
    return send_file(stream, mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                     as_attachment=True, download_name="novaflow_export.xlsx")


@app.route("/api/ai-insights", methods=["POST"])
def api_ai_insights():
    """Make an explicit, user-triggered request for an AI explanation."""
    if not is_ai_enabled():
        return jsonify({"error": "AI insights are disabled. Enable them in local configuration."}), 503
    if not request.is_json or request.get_json(silent=True) != {"confirm": True}:
        return jsonify({"error": "Confirm the AI data-sharing request using JSON."}), 400
    try:
        metrics, summary, critical = load_analysis()
        insight = generate_ai_insight(metrics)
    except AIInsightError as error:
        return jsonify({"error": str(error)}), 503
    except FileNotFoundError as error:
        return jsonify({"error": str(error)}), 404
    except ValueError as error:
        return jsonify({"error": str(error)}), 400
    return jsonify({
        "insight": insight,
        "generated_by": "AI",
        "notice": "AI-generated interpretation; verify it against the measured values.",
    })


@app.route("/health")
def health_check():
    return jsonify({"status": "ok", "service": "NovaFlow"})


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=int(os.environ.get("PORT", "5000")), debug=False)
