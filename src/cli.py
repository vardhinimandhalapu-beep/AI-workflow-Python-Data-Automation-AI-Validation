#!/usr/bin/env python3
"""CLI for NovaFlow Analytics.

Command-line interface for data validation, analysis, and reporting.
"""

import sys
from pathlib import Path

from main import App, DataAnalyzer, DataValidator


def print_usage() -> None:
    """Print CLI usage information."""
    print("\nNovaFlow CLI")
    print("="*50)
    print("Usage:")
    print("  python cli.py validate <csv-file>   Validate data")
    print("  python cli.py analyze <csv-file>    Run analysis")
    print("  python cli.py report <csv-file>     Generate reports")
    print("  python cli.py serve <csv-file>      View in browser")
    print("  python cli.py help                  Show this help")
    print()


def validate_file(file_path: str) -> None:
    """Validate a CSV file."""
    path = Path(file_path)
    if not path.exists():
        print(f"File not found: {file_path}")
        return

    rows = DataValidator.load_csv(path)
    valid, errors = DataValidator.validate_dataset(rows)
    if valid:
        print("✓ VALIDATION PASSED")
        print(f"  Rows checked: {len(rows)}")
    else:
        print("✗ VALIDATION FAILED")
        for error in errors:
            print(f"  - {error}")


def analyze_file(file_path: str) -> None:
    """Analyze a CSV file."""
    path = Path(file_path)
    if not path.exists():
        print(f"File not found: {file_path}")
        return

    rows = DataValidator.load_csv(path)
    valid, errors = DataValidator.validate_dataset(rows)
    if not valid:
        print("✗ VALIDATION FAILED")
        for error in errors:
            print(f"  - {error}")
        return

    metrics = DataAnalyzer.load_metrics(rows)
    summary = DataAnalyzer.calculate_summary(metrics)

    print("\nSummary")
    print(f"Total metrics: {summary.get('total_metrics', 0)}")
    print(f"Improving: {summary.get('up_trends', 0)}")
    print(f"Declining: {summary.get('down_trends', 0)}")
    print(f"Average change: {summary.get('avg_percentage_change', 0):+.2f}%")

    print("\nMetrics")
    for metric in metrics:
        pct = metric.percentage_change()
        print(f"  {metric.name:<25} {pct:+8.2f}% ({metric.trend()})")


def generate_report(file_path: str) -> None:
    """Generate reports for a CSV file."""
    app = App()
    path = Path(file_path)
    if not path.exists():
        print(f"File not found: {file_path}")
        return

    reports = app.generate_reports(path)
    print("\n✓ Reports generated")
    print(f"  JSON: {reports['json']}")
    print(f"  HTML: {reports['html']}")


def serve_dashboard(file_path: str) -> None:
    """Generate and serve dashboard in browser."""
    app = App()
    path = Path(file_path)
    if not path.exists():
        print(f"File not found: {file_path}")
        return

    reports = app.generate_reports(path)
    html_path = Path(reports["html"])
    app.serve_report(html_path)


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
    elif command == "serve":
        if len(sys.argv) < 3:
            print("Please provide a CSV file path.")
        else:
            serve_dashboard(sys.argv[2])
    else:
        print(f"Unknown command: {command}")
        print_usage()
