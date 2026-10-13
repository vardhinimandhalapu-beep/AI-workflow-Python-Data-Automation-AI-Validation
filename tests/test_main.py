import json

import pytest

from src.main import App, DataAnalyzer, DataValidator, Metric, ReportGenerator


def test_validates_finite_values_and_duplicate_metrics():
    rows = [
        {"metric": "Revenue", "q1": "0", "q2": "4", "unit": "USD"},
        {"metric": "revenue", "q1": "2", "q2": "3", "unit": "USD"},
    ]
    valid, errors = DataValidator.validate_dataset(rows)
    assert not valid
    assert any("duplicate metric" in error for error in errors)
    rows[1]["metric"] = "Users"
    rows[0]["q2"] = "nan"
    valid, errors = DataValidator.validate_dataset(rows)
    assert not valid
    assert any("finite number" in error for error in errors)


def test_csv_requires_expected_headers_and_handles_empty_data(tmp_path):
    path = tmp_path / "bad.csv"
    path.write_text("metric,q1\nusers,1\n", encoding="utf-8")
    with pytest.raises(ValueError, match="required columns"):
        DataValidator.load_csv(path)
    assert DataValidator.validate_dataset([]) == (False, ["Dataset is empty or contains a header only."])


def test_zero_baseline_is_undefined_and_excluded_from_average():
    metrics = [
        Metric("new", 0, 5, "items"),
        Metric("up", 10, 12, "items"),
        Metric("flat", 5, 5, "items"),
    ]
    assert metrics[0].percentage_change() is None
    assert DataAnalyzer.calculate_summary(metrics) == {
        "total_metrics": 3, "up_trends": 2, "down_trends": 0, "flat_trends": 1,
        "avg_percentage_change": 10.0,
    }
    assert [m.name for m in DataAnalyzer.identify_critical_metrics(metrics, 10)] == ["up"]


def test_html_report_escapes_untrusted_labels():
    metric = Metric("<script>alert(1)</script>", 1, 2, "units")
    report = ReportGenerator.build_dashboard([metric], DataAnalyzer.calculate_summary([metric]))
    assert "<script>" not in report
    assert "&lt;script&gt;" in report


def test_sample_pipeline_generates_readable_reports(tmp_path):
    app = App(tmp_path)
    source = app.create_sample_data()
    analysis = app.analyze_data(source)
    reports = app.generate_reports(source)
    assert analysis["summary"]["total_metrics"] == 6
    assert json.loads(open(reports["json"], encoding="utf-8").read())[0]["name"] == "users"
    assert "<!doctype html>" in open(reports["html"], encoding="utf-8").read().lower()
