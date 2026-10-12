#!/usr/bin/env python3
"""Command-line interface for NovaFlow analytics."""

import sys
from pathlib import Path

from main import App, DataAnalyzer, DataValidator


def print_usage() -> None:
    print("\nNovaFlow CLI")
    print("Usage:")
    print("  python cli.py validate <file.csv>")
    print("  python cli.py analyze <file.csv>")
    print("  python cli.py report <file.csv>")
    print("  python cli.py help")


def validate_file(path_str: str) -> None:
    path = Path(path_str)
    if not path.exists():
        print(f"File not found: {path_str}")
        return

    rows = DataValidator.load_csv(path)
    valid, errors = DataValidator.validate_dataset(rows)

    if valid:
        print("VALIDATION PASSED")
        print(f"Rows checked: {len(rows)}")
    else:
        print("VALIDATION FAILED")
        for error in errors:
            print(f"  - {error}")


def analyze_file(path_str: str) -> None:
    path = Path(path_str)
    if not path.exists():
        print(f"File not found: {path_str}")
        return

    rows = DataValidator.load_csv(path)
    valid, errors = DataValidator.validate_dataset(rows)
    if not valid:
        print("VALIDATION FAILED")
        for error in errors:
            print(f"  - {error}")
        return

    metrics = DataAnalyzer.load_metrics(rows)
    summary = DataAnalyzer.calculate_summary(metrics)

    print("\nSummary")
    print(f"Total Metrics: {summary.get('total_metrics', 0)}")
    print(f"Improving: {summary.get('up_trends', 0)}")
    print(f"Declining: {summary.get('down_trends', 0)}")
    print(f"Average Change: {summary.get('avg_percentage_change', 0):+.2f}%")

    for metric in metrics:
        pct = metric.percentage_change()
        print(f"- {metric.name}: {pct:+.2f}% ({metric.trend()})")


def generate_report(path_str: str) -> None:
    app = App()
    data_path = Path(path_str)
    if not data_path.exists():
        print(f"File not found: {path_str}")
        return

    result = app.run_analysis(data_path)
    metrics = result["metrics"]
    summary = result["summary"]

    output_dir = app.output_dir
    output_dir.mkdir(exist_ok=True)
    timestamp = Path("_" + str(__import__('datetime').datetime.now().strftime("%Y%m%d_%H%M%S")))
    json_path = output_dir / f"report{timestamp}.json"
    html_path = output_dir / f"report{timestamp}.html"

    app.export_json(metrics, json_path)
    app.export_html(metrics, summary, html_path)

    print(f"JSON report written to: {json_path}")
    print(f"HTML report written to: {html_path}")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print_usage()
        sys.exit(0)

    command = sys.argv[1].lower()

    if command == "help":
        print_usage()
    elif command == "validate":
        if len(sys.argv) < 3:
            print("Please provide a CSV file path.")
        else:
            validate_file(sys.argv[2])
    elif command == "analyze":
        if len(sys.argv) < 3:
            print("Please provide a CSV file path.")
        else:
            analyze_file(sys.argv[2])
    elif command == "report":
        if len(sys.argv) < 3:
            print("Please provide a CSV file path.")
        else:
            generate_report(sys.argv[2])
    else:
        print(f"Unknown command: {command}")
        print_usage()
