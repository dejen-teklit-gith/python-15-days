"""API tests — no server needed. Run: pytest -v"""
import importlib

import pytest
from fastapi.testclient import TestClient


@pytest.fixture()
def client(tmp_path, monkeypatch):
    monkeypatch.setenv("SHORTENER_DB", str(tmp_path / "test.db"))   # fresh DB per test
    import app as app_module
    importlib.reload(app_module)
    with TestClient(app_module.app) as c:
        yield c


def test_health(client):
    assert client.get("/health").json() == {"status": "ok"}


def test_create_and_follow_counts_clicks(client):
    created = client.post("/links", json={"url": "https://www.python.org"}).json()
    code = created["code"]
    assert len(code) == 6

    r = client.get(f"/{code}", follow_redirects=False)
    assert r.status_code == 307
    assert r.headers["location"] == "https://www.python.org/"

    assert client.get(f"/links/{code}").json()["clicks"] == 1


def test_custom_code_conflict(client):
    body = {"url": "https://example.com", "custom_code": "promo"}
    assert client.post("/links", json=body).status_code == 201
    assert client.post("/links", json=body).status_code == 409


@pytest.mark.parametrize("bad", [
    {"url": "not a url"},
    {"url": "https://ok.com", "custom_code": "x"},             # too short
    {"url": "https://ok.com", "custom_code": "bad code!"},     # invalid chars
])
def test_validation_rejects_bad_input(client, bad):
    assert client.post("/links", json=bad).status_code == 422


def test_delete_then_404(client):
    code = client.post("/links", json={"url": "https://example.com"}).json()["code"]
    assert client.delete(f"/links/{code}").status_code == 204
    assert client.get(f"/{code}", follow_redirects=False).status_code == 404
