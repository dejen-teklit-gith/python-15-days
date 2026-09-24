"""End-to-end API tests. Run: pytest -v   (trains the model first if it's missing)"""
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

ROOT = Path(__file__).parent.parent

RISKY = {"tenure_months": 2, "contract": "monthly", "plan": "basic", "monthly_fee": 120,
         "support_tickets_90d": 6, "autopay": False, "logins_30d": 0}
LOYAL = {"tenure_months": 70, "contract": "two_year", "plan": "premium", "monthly_fee": 60,
         "support_tickets_90d": 0, "autopay": True, "logins_30d": 40}


@pytest.fixture(scope="session")
def client():
    if not (ROOT / "model" / "churn_model.joblib").exists():
        import train
        train.main()
    from app.main import app
    with TestClient(app) as c:
        yield c


def test_health(client):
    assert client.get("/health").json() == {"status": "ok", "model_loaded": True}


def test_model_info_exposes_quality(client):
    meta = client.get("/model").json()
    assert meta["test_auc"] >= 0.75
    assert 0 < meta["threshold"] < 1


def test_risky_customer_scores_higher_than_loyal(client):
    risky = client.post("/predict", json=RISKY).json()
    loyal = client.post("/predict", json=LOYAL).json()
    assert risky["churn_probability"] > loyal["churn_probability"]
    assert risky["send_retention_offer"] is True
    assert loyal["risk"] == "low"


def test_missing_fee_is_imputed(client):
    body = {**RISKY, "monthly_fee": None}
    assert client.post("/predict", json=body).status_code == 200


@pytest.mark.parametrize("bad", [
    {**RISKY, "contract": "weekly"},          # not an allowed value
    {**RISKY, "tenure_months": -1},           # out of range
    {k: v for k, v in RISKY.items() if k != "plan"},   # required field missing
])
def test_invalid_input_rejected(client, bad):
    assert client.post("/predict", json=bad).status_code == 422


def test_batch(client):
    r = client.post("/predict/batch", json={"customers": [RISKY, LOYAL, RISKY]})
    assert r.status_code == 200
    assert [p["send_retention_offer"] for p in r.json()] == [True, False, True]


def test_empty_batch_rejected(client):
    assert client.post("/predict/batch", json={"customers": []}).status_code == 422
