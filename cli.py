#!/usr/bin/env python3
"""CLI tool for the NovaFlow project."""

import sys
from pathlib import Path

from main import DataAnalyzer, DataValidator, EvaluationEngine, Reporter


def print_usage() -> None:
    print("\nNovaFlow CLI")
    print("Usage:")
    print("  python cli.py validate <data.csv>")
    print("  python cli.py analyze <data.csv>")
    print("  python cli.py score <scores.csv>")
    print("  python cli.py help")


def run_validate(filepath: str) -> None:
    path = Path(filepath)
    if not path.exists():
        print(f"File not found: {filepath}")
        return

    rows = DataValidator.load_csv(path)
    valid, errors = DataValidator.validate_dataset(rows)
    if valid:
        print("VALIDATION PASSED")
    else:
        print("VALIDATION FAILED")
        for error in errors:
            print(f"  - {error}")


def run_analyze(filepath: str) -> None:
    path = Path(filepath)
    if not path.exists():
        print(f"File not found: {filepath}")
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
    Reporter.print_summary(summary)
    Reporter.print_metric_report(metrics)

    critical = DataAnalyzer.identify_critical_metrics(metrics)
    if critical:
        Reporter.print_critical_metrics(critical)


def run_score(filepath: str) -> None:
    path = Path(filepath)
    if not path.exists():
        print(f"File not found: {filepath}")
        return

    scores = EvaluationEngine.load_scores(path)
    if not scores:
        print("No valid scores found in the file.")
        return

    comparisons = EvaluationEngine.compare_versions(scores)
    Reporter.print_evaluation_comparison(comparisons)


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
            run_validate(sys.argv[2])
    elif command == "analyze":
        if len(sys.argv) < 3:
            print("Please provide a CSV file path.")
        else:
            run_analyze(sys.argv[2])
    elif command == "score":
        if len(sys.argv) < 3:
            print("Please provide a scores CSV file path.")
        else:
            run_score(sys.argv[2])
    else:
        print(f"Unknown command: {command}")
        print_usage()
