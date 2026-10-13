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


def test_blank_duplicate_and_malformed_headers_are_rejected(tmp_path):
    cases = [
        ("blank.csv", "metric,q1,q2,unit,\nusers,1,2,people,x\n", "blank column"),
        ("duplicate.csv", "metric,q1,q2,unit,unit\nusers,1,2,people,people\n", "duplicate column"),
        ("malformed.csv", 'metric,q1,q2,unit\n"users,1,2,people\n', "Malformed CSV"),
    ]
    for filename, content, message in cases:
        path = tmp_path / filename
        path.write_text(content, encoding="utf-8")
        with pytest.raises(ValueError, match=message):
            DataValidator.load_csv(path)


def test_empty_header_only_and_invalid_encoding_are_rejected(tmp_path):
    empty = tmp_path / "empty.csv"
    empty.write_bytes(b"")
    assert DataValidator.load_csv(empty) == []
    header_only = tmp_path / "header.csv"
    header_only.write_text("metric,q1,q2,unit\n", encoding="utf-8")
    rows = DataValidator.load_csv(header_only)
    assert DataValidator.validate_dataset(rows)[0] is False
    invalid = tmp_path / "encoding.csv"
    invalid.write_bytes(b"metric,q1,q2,unit\nusers,1,2,pe\xffple\n")
    with pytest.raises(ValueError, match="UTF-8"):
        DataValidator.load_csv(invalid)


def test_short_and_extra_rows_are_reported(tmp_path):
    short = tmp_path / "short.csv"
    short.write_text("metric,q1,q2,unit\nusers,1,,people\n", encoding="utf-8")
    rows = DataValidator.load_csv(short)
    valid, errors = DataValidator.validate_dataset(rows)
    assert not valid
    assert any("q2 is blank" in error for error in errors)

    extra = tmp_path / "extra.csv"
    extra.write_text("metric,q1,q2,unit\nusers,1,2,people,extra\n", encoding="utf-8")
    rows = DataValidator.load_csv(extra)
    valid, errors = DataValidator.validate_dataset(rows)
    assert not valid
    assert any("more values than the header" in error for error in errors)


def test_csv_size_limit_accepts_exact_boundary_and_rejects_one_byte_over(tmp_path):
    path = tmp_path / "boundary.csv"
    prefix = b"metric,q1,q2,unit\nusers,1,2,people\n"
    padding_size = DataValidator.MAX_FILE_BYTES - len(prefix)
    path.write_bytes(prefix + b"\n" * padding_size)
    rows = DataValidator.load_csv(path)
    assert len(rows) == 1
    assert DataValidator.validate_dataset(rows)[0]

    path.write_bytes(prefix + b"\\n" * padding_size + b"x")
    with pytest.raises(ValueError, match="10 MiB"):
        DataValidator.load_csv(path)


def test_negative_values_have_arithmetic_change_and_direction():
    metric = Metric("balance", -10, -15, "units")
    assert metric.absolute_change() == -5
    assert metric.percentage_change() == 50
    assert metric.trend() == "DOWN"
