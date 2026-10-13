import json

from openpyxl import load_workbook

import app as flask_app


def test_dashboard_api_and_exports(tmp_path):
    data = tmp_path / "metrics.csv"
    data.write_text("metric,q1,q2,unit\nusers,10,12,people\n", encoding="utf-8")
    flask_app.app.config.update(TESTING=True, DATASET_PATH=data)
    client = flask_app.app.test_client()

    page = client.get("/")
    assert page.status_code == 200
    assert b"NovaFlow" in page.data
    assert b"users" in page.data

    response = client.get("/api/summary")
    assert response.status_code == 200
    payload = response.get_json()
    assert payload["summary"]["total_metrics"] == 1
    assert payload["metrics"][0]["percentage_change"] == 20

    exported_json = client.get("/export/json")
    assert exported_json.status_code == 200
    assert json.loads(exported_json.data)["metrics"][0]["name"] == "users"

    exported_excel = client.get("/export/excel")
    assert exported_excel.status_code == 200
    workbook = load_workbook(filename=__import__("io").BytesIO(exported_excel.data), read_only=True)
    assert workbook.active["A2"].value == "users"


def test_invalid_and_missing_dataset_return_actionable_errors(tmp_path):
    flask_app.app.config.update(TESTING=True, DATASET_PATH=tmp_path / "absent.csv")
    client = flask_app.app.test_client()
    assert client.get("/").status_code == 404

    bad = tmp_path / "bad.csv"
    bad.write_text("metric,q1,q2,unit\nusers,nan,3,people\n", encoding="utf-8")
    flask_app.app.config["DATASET_PATH"] = bad
    response = client.get("/api/summary")
    assert response.status_code == 400
    assert "finite number" in response.get_json()["error"]
