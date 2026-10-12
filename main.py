#!/usr/bin/env python3
"""NovaFlow Data Analysis System.

A professional, dependency-free Python project for validating and analyzing
business datasets. It runs on any Python 3.7+ environment.
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


@dataclass
class EvaluationScore:
    version: str
    data_accuracy: float
    calculation_accuracy: float
    evidence_consistency: float
    completeness: float
    relevance: float
    narrative_structure: float
    visual_usefulness: float
    professional_clarity: float
    speaker_notes: float
    meeting_readiness: float

    WEIGHTS = {
        "data_accuracy": 0.20,
        "calculation_accuracy": 0.15,
        "evidence_consistency": 0.15,
        "completeness": 0.10,
        "relevance": 0.10,
        "narrative_structure": 0.10,
        "visual_usefulness": 0.05,
        "professional_clarity": 0.05,
        "speaker_notes": 0.05,
        "meeting_readiness": 0.05,
    }

    def weighted_score(self) -> float:
        total = 0.0
        for field, weight in self.WEIGHTS.items():
            rating = getattr(self, field, 0) / 100.0
            total += rating * weight * 100
        return round(total, 2)


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

        percentage_values = [
            metric.percentage_change()
            for metric in metrics
            if metric.percentage_change() is not None
        ]
        avg_percentage = (
            round(sum(percentage_values) / len(percentage_values), 2)
            if percentage_values
            else 0.0
        )

        return {
            "total_metrics": len(metrics),
            "up_trends": up_count,
            "down_trends": down_count,
            "flat_trends": flat_count,
            "avg_percentage_change": avg_percentage,
        }

    @staticmethod
    def identify_critical_metrics(
        metrics: List[Metric], threshold_pct: float = 10.0
    ) -> List[Metric]:
        critical = []
        for metric in metrics:
            pct = metric.percentage_change()
            if pct is not None and abs(pct) >= threshold_pct:
                critical.append(metric)
        return sorted(critical, key=lambda m: abs(m.percentage_change() or 0), reverse=True)


class EvaluationEngine:
    @staticmethod
    def load_scores(filepath: Path) -> List[EvaluationScore]:
        if not filepath.exists():
            return []

        rows = DataValidator.load_csv(filepath)
        scores: List[EvaluationScore] = []
        for row in rows:
            try:
                scores.append(
                    EvaluationScore(
                        version=row.get("version", "").strip(),
                        data_accuracy=float(row.get("data_accuracy", 0)),
                        calculation_accuracy=float(row.get("calculation_accuracy", 0)),
                        evidence_consistency=float(row.get("evidence_consistency", 0)),
                        completeness=float(row.get("completeness", 0)),
                        relevance=float(row.get("relevance", 0)),
                        narrative_structure=float(row.get("narrative_structure", 0)),
                        visual_usefulness=float(row.get("visual_usefulness", 0)),
                        professional_clarity=float(row.get("professional_clarity", 0)),
                        speaker_notes=float(row.get("speaker_notes", 0)),
                        meeting_readiness=float(row.get("meeting_readiness", 0)),
                    )
                )
            except (TypeError, ValueError):
                continue
        return scores

    @staticmethod
    def compare_versions(scores: List[EvaluationScore]) -> List[Tuple[str, float]]:
        return sorted(
            [(score.version, score.weighted_score()) for score in scores],
            key=lambda item: item[1],
            reverse=True,
        )


class Reporter:
    @staticmethod
    def print_header(title: str) -> None:
        print("\n" + "=" * 80)
        print(title.center(80))
        print("=" * 80)

    @staticmethod
    def print_summary(summary: Dict[str, Any]) -> None:
        print(f"Total Metrics: {summary.get('total_metrics', 0)}")
        print(f"Improving (↑): {summary.get('up_trends', 0)}")
        print(f"Declining (↓): {summary.get('down_trends', 0)}")
        print(f"Stable (→): {summary.get('flat_trends', 0)}")
        print(f"Average Change: {summary.get('avg_percentage_change', 0):+.2f}%")

    @staticmethod
    def print_metric_report(metrics: List[Metric]) -> None:
        print(f"\n{'Metric':<25} {'Q1':>12} {'Q2':>12} {'Change':>12} {'Trend':>8}")
        print("-" * 80)
        for metric in metrics:
            pct = metric.percentage_change()
            pct_text = f"{pct:+.2f}%" if pct is not None else "N/A"
            print(
                f"{metric.name:<25} {metric.q1_value:>12.2f} {metric.q2_value:>12.2f} "
                f"{pct_text:>12} {metric.trend():>8}"
            )

    @staticmethod
    def print_critical_metrics(metrics: List[Metric]) -> None:
        print(f"\n{'Metric':<25} {'Change %':>12} {'Severity':>15}")
        print("-" * 60)
        for metric in metrics:
            pct = metric.percentage_change() or 0
            severity = "CRITICAL" if abs(pct) > 20 else "HIGH" if abs(pct) > 10 else "MEDIUM"
            print(f"{metric.name:<25} {pct:>12.2f}% {severity:>15}")

    @staticmethod
    def print_evaluation_comparison(comparisons: List[Tuple[str, float]]) -> None:
        print(f"\n{'Version':<12} {'Score':>8}")
        print("-" * 32)
        for version, score in comparisons:
            print(f"{version:<12} {score:>8.2f}")

    @staticmethod
    def export_json(metrics: List[Metric], filepath: Path) -> None:
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


class NovaFlowApp:
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

    def run(self) -> None:
        Reporter.print_header("NOVAFLOW DATA ANALYSIS SYSTEM")
        data_file = self.create_sample_data()
        print(f"Dataset loaded: {data_file}")

        try:
            rows = DataValidator.load_csv(data_file)
            valid, errors = DataValidator.validate_dataset(rows)

            if not valid:
                print("VALIDATION FAILED")
                for error in errors:
                    print(f"  - {error}")
                return

            print("VALIDATION PASSED")
            metrics = DataAnalyzer.load_metrics(rows)
            summary = DataAnalyzer.calculate_summary(metrics)

            Reporter.print_summary(summary)
            Reporter.print_metric_report(metrics)

            critical = DataAnalyzer.identify_critical_metrics(metrics)
            if critical:
                Reporter.print_critical_metrics(critical)

            output_file = self.output_dir / f"analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            Reporter.export_json(metrics, output_file)
            print(f"\nResults exported to: {output_file}")

        except Exception as exc:
            print(f"Error: {exc}")
            sys.exit(1)


if __name__ == "__main__":
    try:
        NovaFlowApp().run()
    except KeyboardInterrupt:
        print("\nProgram interrupted by user.")
        sys.exit(0)
    except Exception as exc:
        print(f"Unexpected error: {exc}")
        sys.exit(1)











































































































































































































































