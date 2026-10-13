#!/usr/bin/env python3
"""Command-line workflows for NovaFlow."""
import argparse
import json
import sys
from pathlib import Path

PROJECT_DIR = Path(__file__).resolve().parents[1]
if str(PROJECT_DIR) not in sys.path:
    sys.path.insert(0, str(PROJECT_DIR))

from src.main import App, DataValidator  # noqa: E402


def build_parser():
    parser = argparse.ArgumentParser(description="Validate and analyze NovaFlow metric CSV files.")
    commands = parser.add_subparsers(dest="command", required=True)
    for name, help_text in (
        ("validate", "Validate a CSV file"),
        ("analyze", "Analyze a CSV file and print a JSON summary"),
        ("report", "Generate JSON and HTML reports"),
        ("serve", "Generate a report and open it locally"),
    ):
        command = commands.add_parser(name, help=help_text)
        command.add_argument("csv_file", type=Path, help="Path to a CSV using metric,q1,q2,unit columns")
    return parser


def main(argv=None):
    args = build_parser().parse_args(argv)
    app = App(PROJECT_DIR)
    try:
        if args.command == "validate":
            rows = DataValidator.load_csv(args.csv_file)
            valid, errors = DataValidator.validate_dataset(rows)
            if not valid:
                for error in errors:
                    print(error, file=sys.stderr)
                return 1
            print("Validation passed: {} data rows.".format(len(rows)))
            return 0

        analysis = app.analyze_data(args.csv_file)
        if args.command == "analyze":
            summary = analysis["summary"]
            payload = {
                "summary": summary,
                "metrics": [{
                    "name": metric.name, "q1": metric.q1_value, "q2": metric.q2_value,
                    "unit": metric.unit, "absolute_change": metric.absolute_change(),
                    "percentage_change": metric.percentage_change(), "trend": metric.trend(),
                } for metric in analysis["metrics"]],
                "critical": [metric.name for metric in analysis["critical"]],
            }
            print(json.dumps(payload, indent=2, allow_nan=False))
        elif args.command in ("report", "serve"):
            reports = app.generate_reports(args.csv_file)
            print(json.dumps(reports, indent=2))
            if args.command == "serve":
                app.serve_report(Path(reports["html"]))
        return 0
    except (OSError, ValueError) as exc:
        print("Error: {}".format(exc), file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
