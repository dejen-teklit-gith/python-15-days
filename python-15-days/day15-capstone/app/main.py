"""Churn prediction API — the capstone. Everything from Days 1–14 in one deployable service.

Run locally:  uvicorn app.main:app --reload     → http://127.0.0.1:8000/docs
"""
import logging
import os
import time
from contextlib import asynccontextmanager
from pathlib import Path
from typing import Literal

import joblib
import pandas as pd
from fastapi import FastAPI, HTTPException, Request
from pydantic import BaseModel, Field

MODEL_PATH = Path(os.getenv("MODEL_PATH", Path(__file__).parent.parent / "model" / "churn_model.joblib"))
MAX_BATCH = 1000

logging.basicConfig(level=os.getenv("LOG_LEVEL", "INFO"),
                    format="%(asctime)s %(levelname)s %(name)s: %(message)s")
log = logging.getLogger("churn-api")
state: dict = {}


# ── Schemas: the API contract ───────────────────────────────────────────────
class Customer(BaseModel):
    tenure_months: int = Field(..., ge=0, le=600, examples=[4])
    contract: Literal["monthly", "one_year", "two_year"] = Field(..., examples=["monthly"])
    plan: Literal["basic", "standard", "premium"] = Field(..., examples=["standard"])
    monthly_fee: float | None = Field(None, ge=0, le=10_000, examples=[89.0])
    support_tickets_90d: int = Field(0, ge=0, le=1000, examples=[3])
    autopay: bool = Field(False, examples=[False])
    logins_30d: int = Field(0, ge=0, le=10_000, examples=[2])


class Prediction(BaseModel):
    churn_probability: float
    risk: Literal["low", "medium", "high"]
    send_retention_offer: bool
    model_version: str


class BatchRequest(BaseModel):
    customers: list[Customer] = Field(..., min_length=1, max_length=MAX_BATCH)


# ── Lifecycle: load the model ONCE at startup, not per request ──────────────
@asynccontextmanager
async def lifespan(_: FastAPI):
    if not MODEL_PATH.exists():
        raise RuntimeError(f"Model not found at {MODEL_PATH}. Run `python train.py` first.")
    bundle = joblib.load(MODEL_PATH)
    state["pipeline"], state["meta"] = bundle["pipeline"], bundle["metadata"]
    log.info("loaded model %s (AUC %.3f)", state["meta"]["version"], state["meta"]["test_auc"])
    yield
    state.clear()


app = FastAPI(title="Churn Prediction API", version="1.0.0", lifespan=lifespan,
              description="Scores customers' churn risk and recommends who gets a retention offer.")


@app.middleware("http")
async def log_requests(request: Request, call_next):
    start = time.perf_counter()
    response = await call_next(request)
    log.info("%s %s → %s in %.1f ms", request.method, request.url.path,
             response.status_code, (time.perf_counter() - start) * 1000)
    return response


# ── Core logic: pure function, easy to test ─────────────────────────────────
def score(customers: list[Customer]) -> list[Prediction]:
    meta = state["meta"]
    frame = pd.DataFrame([c.model_dump() for c in customers])
    frame["autopay"] = frame["autopay"].astype(int)
    probabilities = state["pipeline"].predict_proba(frame[meta["features"]])[:, 1]
    threshold = meta["threshold"]
    return [
        Prediction(
            churn_probability=round(float(p), 4),
            risk="high" if p >= threshold else "medium" if p >= threshold / 2 else "low",
            send_retention_offer=bool(p >= threshold),
            model_version=meta["version"],
        )
        for p in probabilities
    ]


# ── Routes ──────────────────────────────────────────────────────────────────
@app.get("/health")
def health() -> dict:
    return {"status": "ok", "model_loaded": "pipeline" in state}


@app.get("/model")
def model_info() -> dict:
    return state["meta"]


@app.post("/predict", response_model=Prediction)
def predict(customer: Customer) -> Prediction:
    return score([customer])[0]


@app.post("/predict/batch", response_model=list[Prediction])
def predict_batch(body: BatchRequest) -> list[Prediction]:
    try:
        return score(body.customers)
    except Exception:
        log.exception("batch scoring failed")
        raise HTTPException(500, "scoring failed") from None
