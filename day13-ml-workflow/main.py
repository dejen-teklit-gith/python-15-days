"""Day 13 — Customer churn prediction: the real scikit-learn workflow.

Pipeline → cross-validation → model comparison → business-driven threshold → save.
"""
from pathlib import Path

import joblib
import numpy as np
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.dummy import DummyClassifier
from sklearn.ensemble import HistGradientBoostingClassifier, RandomForestClassifier
from sklearn.impute import SimpleImputer
from sklearn.inspection import permutation_importance
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (classification_report, confusion_matrix, precision_score,
                             recall_score, roc_auc_score)
from sklearn.model_selection import StratifiedKFold, cross_val_score, train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler

HERE = Path(__file__).parent
NUMERIC = ["tenure_months", "monthly_fee", "support_tickets_90d", "autopay", "logins_30d"]
CATEGORICAL = ["contract", "plan"]
TARGET = "churned"

# Business numbers (ask your stakeholders for these!)
VALUE_OF_SAVED_CUSTOMER = 400      # CHF of future revenue kept if we retain them
COST_OF_OFFER = 50                 # CHF discount given to everyone we flag
SAVE_RATE = 0.3                    # share of real churners the offer convinces to stay


def build_pipeline(model) -> Pipeline:
    """Preprocessing + model in ONE object → no leakage, one thing to save and deploy."""
    preprocess = ColumnTransformer([
        ("num", Pipeline([("impute", SimpleImputer(strategy="median")),
                          ("scale", StandardScaler())]), NUMERIC),
        ("cat", OneHotEncoder(handle_unknown="ignore"), CATEGORICAL),
    ])
    return Pipeline([("prep", preprocess), ("model", model)])


def profit_at(threshold: float, y_true, proba) -> float:
    flagged = proba >= threshold
    true_churners_flagged = (flagged & (y_true == 1)).sum()
    return (true_churners_flagged * SAVE_RATE * VALUE_OF_SAVED_CUSTOMER
            - flagged.sum() * COST_OF_OFFER)


if __name__ == "__main__":
    df = pd.read_csv(HERE / "customers.csv")
    X, y = df[NUMERIC + CATEGORICAL], df[TARGET]
    print(f"{len(df)} customers, churn rate {y.mean():.1%} (imbalanced!)\n")

    # stratify keeps the churn rate identical in train and test
    X_tr, X_te, y_tr, y_te = train_test_split(X, y, test_size=0.25, stratify=y, random_state=0)

    candidates = {
        "Baseline (always 'stays')": DummyClassifier(strategy="most_frequent"),
        "Logistic regression": LogisticRegression(max_iter=1000, class_weight="balanced"),
        "Random forest": RandomForestClassifier(n_estimators=300, min_samples_leaf=5,
                                                class_weight="balanced", random_state=0, n_jobs=-1),
        "Gradient boosting": HistGradientBoostingClassifier(max_depth=3, learning_rate=0.05,
                                                            random_state=0),
    }

    print("5-fold cross-validated ROC-AUC on the TRAINING set (0.5 = coin flip, 1.0 = perfect)")
    cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=0)
    scores = {}
    for name, model in candidates.items():
        s = cross_val_score(build_pipeline(model), X_tr, y_tr, cv=cv, scoring="roc_auc")
        scores[name] = s.mean()
        print(f"  {name:<28} {s.mean():.3f} ± {s.std():.3f}")

    best_name = max(scores, key=scores.get)
    print(f"\n🏆 Best: {best_name} — now evaluated ONCE on the untouched test set")
    best = build_pipeline(candidates[best_name]).fit(X_tr, y_tr)
    proba = best.predict_proba(X_te)[:, 1]
    print(f"   Test ROC-AUC: {roc_auc_score(y_te, proba):.3f}")

    print("\n⚠️  Accuracy trap: the dummy model is "
          f"{(y_te == 0).mean():.0%} 'accurate' while catching 0 churners.")

    # Choose the threshold by MONEY, not by the default 0.5
    thresholds = np.linspace(0.05, 0.9, 86)
    profits = [profit_at(t, y_te.to_numpy(), proba) for t in thresholds]
    best_t = thresholds[int(np.argmax(profits))]
    print("\n💰 Threshold chosen by expected campaign profit:")
    for t in [0.5, best_t]:
        pred = (proba >= t).astype(int)
        print(f"   t={t:.2f}  flagged={pred.sum():>4}  precision={precision_score(y_te, pred):.2f}"
              f"  recall={recall_score(y_te, pred):.2f}  profit=CHF {profit_at(t, y_te.to_numpy(), proba):>7,.0f}")

    pred = (proba >= best_t).astype(int)
    print(f"\nConfusion matrix at t={best_t:.2f}  [[TN FP] [FN TP]]:\n{confusion_matrix(y_te, pred)}")
    print(classification_report(y_te, pred, target_names=["stays", "churns"], digits=2))

    imp = permutation_importance(best, X_te, y_te, scoring="roc_auc", n_repeats=5, random_state=0)
    order = np.argsort(imp.importances_mean)[::-1]
    print("What drives churn (permutation importance = AUC lost when a column is shuffled):")
    for i in order:
        print(f"   {X.columns[i]:<22} {imp.importances_mean[i]:.3f}")

    joblib.dump({"pipeline": best, "threshold": float(best_t), "features": NUMERIC + CATEGORICAL},
                HERE / "churn_model.joblib")
    print("\nSaved → churn_model.joblib (used by Day 15's API)")
