"""Train the churn model and save it WITH metadata (so the API can report what it serves)."""
import json
from datetime import datetime, timezone
from pathlib import Path

import joblib
import numpy as np
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import roc_auc_score
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler

HERE = Path(__file__).parent
MODEL_PATH = HERE / "model" / "churn_model.joblib"
NUMERIC = ["tenure_months", "monthly_fee", "support_tickets_90d", "autopay", "logins_30d"]
CATEGORICAL = ["contract", "plan"]
MIN_AUC = 0.75                                   # quality gate: refuse to ship a worse model

# Same business economics as Day 13
VALUE_SAVED, OFFER_COST, SAVE_RATE = 400, 50, 0.3


def main() -> None:
    df = pd.read_csv(HERE / "data" / "customers.csv")
    X, y = df[NUMERIC + CATEGORICAL], df["churned"]
    X_tr, X_te, y_tr, y_te = train_test_split(X, y, test_size=0.25, stratify=y, random_state=0)

    pipeline = Pipeline([
        ("prep", ColumnTransformer([
            ("num", Pipeline([("impute", SimpleImputer(strategy="median")),
                              ("scale", StandardScaler())]), NUMERIC),
            ("cat", OneHotEncoder(handle_unknown="ignore"), CATEGORICAL),
        ])),
        ("model", LogisticRegression(max_iter=1000, class_weight="balanced")),
    ]).fit(X_tr, y_tr)

    proba = pipeline.predict_proba(X_te)[:, 1]
    auc = roc_auc_score(y_te, proba)
    if auc < MIN_AUC:
        raise SystemExit(f"❌ AUC {auc:.3f} below quality gate {MIN_AUC} — not saving")

    thresholds = np.linspace(0.05, 0.95, 91)
    profit = [((proba >= t) & (y_te == 1)).sum() * SAVE_RATE * VALUE_SAVED
              - (proba >= t).sum() * OFFER_COST for t in thresholds]
    threshold = float(thresholds[int(np.argmax(profit))])

    metadata = {
        "version": datetime.now(timezone.utc).strftime("%Y%m%d-%H%M%S"),
        "trained_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "test_auc": round(float(auc), 4),
        "threshold": round(threshold, 2),
        "n_train": len(X_tr),
        "features": NUMERIC + CATEGORICAL,
    }
    MODEL_PATH.parent.mkdir(exist_ok=True)
    joblib.dump({"pipeline": pipeline, "metadata": metadata}, MODEL_PATH)
    print(json.dumps(metadata, indent=2))
    print(f"✅ saved {MODEL_PATH.relative_to(HERE)}")


if __name__ == "__main__":
    main()
