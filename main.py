"""Compatibility entry point for the core workflow."""
from src.main import App, DataAnalyzer, DataValidator, Metric, ReportGenerator


if __name__ == "__main__":
    App().run()
