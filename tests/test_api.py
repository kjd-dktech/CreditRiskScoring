from fastapi.testclient import TestClient
import os

from API.main import app

client = TestClient(app)


def test_health_endpoint():
    r = client.get("/health")
    assert r.status_code == 200
    data = r.json()
    assert "status" in data
    assert data["status"] == "healthy"
    # model_loaded may be True or False depending on presence of model files
    assert "model_loaded" in data
    assert "explainer_loaded" in data


def test_proba_endpoint():
    payload = {
        "Total_Amount": 1000.0,
        "Total_Amount_to_Repay": 1200.0,
        "duration": 90,
        "Lender_portion_to_be_repaid": 1200.0,
        "New_versus_Repeat": "Repeat Loan",
        "loan_type": "Type_7",
    }

    # Use API_KEY from env if defined; otherwise rely on permissive dev mode in the app
    headers = {}
    api_key = os.getenv("API_KEY")
    if api_key:
        headers["x-api-key"] = api_key

    r = client.post("/proba", json=payload, headers=headers)

    # If model not loaded, service returns 503; otherwise 200 with a probability field
    assert r.status_code in (200, 503)
    if r.status_code == 200:
        data = r.json()
        assert "probability" in data
        assert isinstance(data["probability"], float) or isinstance(
            data["probability"], int
        )
