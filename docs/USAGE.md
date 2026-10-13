# Usage

See the root [README](../README.md) for environment setup, CLI commands, web routes, data schema, and calculation semantics.

## CLI examples

Run these from the repository root:

```bash
python src/cli.py validate data/metrics.csv
python src/cli.py analyze data/metrics.csv
python src/cli.py report data/metrics.csv
python app.py
```

The web dashboard binds to localhost at port 5000 by default. Set the `PORT` environment variable to use another port. Report files created by the CLI are written under `output/reports/`.

The sample CSV contains illustrative data only. See the README for the exact required columns and zero-baseline behavior.
