from src.cli import main


def test_cli_validation_returns_nonzero_for_invalid_input(tmp_path):
    path = tmp_path / "bad.csv"
    path.write_text("metric,q1,q2,unit\nusers,nan,3,people\n", encoding="utf-8")
    assert main(["validate", str(path)]) == 1


def test_cli_help_is_available():
    try:
        main(["--help"])
    except SystemExit as exc:
        assert exc.code == 0
    else:
        raise AssertionError("argparse help should exit successfully")
