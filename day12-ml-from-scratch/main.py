"""Day 12 — Machine learning from scratch: linear regression + gradient descent in NumPy.

No scikit-learn until the very end — where we use it only to CHECK our answer.
"""
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402

HERE = Path(__file__).parent
FEATURES = ["size_m2", "rooms", "age_years", "km_to_center"]
BLUE, INK, MUTED, GRID = "#2a78d6", "#0b0b0b", "#52514e", "#e6e5e0"


# ── 1. Split: never judge a model on data it trained on ─────────────────────
def train_test_split(X, y, test_ratio=0.2, seed=0):
    idx = np.random.default_rng(seed).permutation(len(X))
    cut = int(len(X) * (1 - test_ratio))
    return X[idx[:cut]], X[idx[cut:]], y[idx[:cut]], y[idx[cut:]]


# ── 2. Scale: put features on the same footing so one step size fits all ────
class StandardScaler:
    def fit(self, X):
        self.mean, self.std = X.mean(axis=0), X.std(axis=0)
        return self

    def transform(self, X):
        return (X - self.mean) / self.std


# ── 3. The model: prediction = X · w + b ────────────────────────────────────
class LinearRegressionGD:
    def __init__(self, lr=0.1, epochs=300):
        self.lr, self.epochs = lr, epochs
        self.history: list[float] = []

    def predict(self, X):
        return X @ self.w + self.b

    def fit(self, X, y):
        n, d = X.shape
        self.w, self.b = np.zeros(d), 0.0              # start knowing nothing
        for _ in range(self.epochs):
            error = self.predict(X) - y                # how wrong are we, per house?
            loss = np.mean(error ** 2)                 # MSE: one number to minimise
            self.history.append(loss)
            grad_w = 2 / n * X.T @ error               # slope of the loss w.r.t. each weight
            grad_b = 2 / n * error.sum()
            self.w -= self.lr * grad_w                 # step DOWNHILL
            self.b -= self.lr * grad_b
        return self


def metrics(y_true, y_pred) -> dict:
    mae = np.mean(np.abs(y_true - y_pred))
    rmse = np.sqrt(np.mean((y_true - y_pred) ** 2))
    r2 = 1 - np.sum((y_true - y_pred) ** 2) / np.sum((y_true - y_true.mean()) ** 2)
    return {"MAE": mae, "RMSE": rmse, "R2": r2}


def plot(model, y_test, y_pred, path):
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 4.5))
    ax1.plot(np.array(model.history) / 1e9, color=BLUE, linewidth=2)
    ax1.set_yscale("log")
    ax1.set_title("Training loss (MSE, log scale) — learning = going downhill",
                  loc="left", fontsize=11, color=INK, fontweight="bold")
    ax1.set_xlabel("epoch", color=MUTED)

    lim = [y_test.min() / 1000, y_test.max() / 1000]
    ax2.plot(lim, lim, color=MUTED, linewidth=1, linestyle="--", label="perfect prediction")
    ax2.scatter(y_test / 1000, y_pred / 1000, s=14, color=BLUE, alpha=0.7, label="test houses")
    ax2.set_title("Predicted vs actual price (CHF k, unseen houses)",
                  loc="left", fontsize=11, color=INK, fontweight="bold")
    ax2.set_xlabel("actual", color=MUTED)
    ax2.set_ylabel("predicted", color=MUTED)
    ax2.legend(frameon=False)
    for ax in (ax1, ax2):
        ax.spines[["top", "right"]].set_visible(False)
        ax.grid(color=GRID, linewidth=0.8)
        ax.set_axisbelow(True)
        ax.tick_params(colors=MUTED)
    fig.tight_layout()
    fig.savefig(path, dpi=150)
    plt.close(fig)


if __name__ == "__main__":
    df = pd.read_csv(HERE / "houses.csv")
    X, y = df[FEATURES].to_numpy(float), df["price_chf"].to_numpy(float)
    X_tr, X_te, y_tr, y_te = train_test_split(X, y)

    scaler = StandardScaler().fit(X_tr)                 # fit on TRAIN only (no leakage)
    Xs_tr, Xs_te = scaler.transform(X_tr), scaler.transform(X_te)

    baseline = np.full_like(y_te, y_tr.mean())          # "always guess the average"
    model = LinearRegressionGD(lr=0.1, epochs=300).fit(Xs_tr, y_tr)
    pred = model.predict(Xs_te)

    print(f"Loss: epoch 0 = {model.history[0]:.3e}  →  epoch {model.epochs} = {model.history[-1]:.3e}\n")
    print(f"{'':<22}{'MAE':>12}{'RMSE':>12}{'R²':>8}")
    for name, p in [("Baseline (mean)", baseline), ("Our model", pred)]:
        m = metrics(y_te, p)
        print(f"{name:<22}{m['MAE']:>12,.0f}{m['RMSE']:>12,.0f}{m['R2']:>8.3f}")

    # Convert weights back to real units: CHF per m², per room, per year, per km
    real_w = model.w / scaler.std
    print("\nWhat the model learned (CHF per unit):")
    for f, w in zip(FEATURES, real_w):
        print(f"  {f:<14} {w:>+10,.0f}")

    try:                                                # sanity check vs a library
        from sklearn.linear_model import LinearRegression
        sk = LinearRegression().fit(Xs_tr, y_tr)
        print(f"\nscikit-learn weights match ours: {np.allclose(sk.coef_, model.w, rtol=1e-3)}")
    except ImportError:
        pass

    house = np.array([[110, 4, 15, 3.5]])
    print(f"\n🏠 110 m², 4 rooms, 15 y old, 3.5 km out → "
          f"CHF {model.predict(scaler.transform(house))[0]:,.0f}")

    (HERE / "output").mkdir(exist_ok=True)
    plot(model, y_te, pred, HERE / "output" / "training.png")
