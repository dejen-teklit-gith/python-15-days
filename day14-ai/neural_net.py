"""Day 14 · Part A — A neural network from scratch (NumPy only).

A linear model can only draw straight lines. Stack linear layers with a
non-linear "bend" in between and the network can learn any shape.
"""
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
from matplotlib.colors import ListedColormap  # noqa: E402
from sklearn.datasets import make_moons  # noqa: E402

HERE = Path(__file__).parent
BLUE, ORANGE, INK, MUTED = "#2a78d6", "#eb6834", "#0b0b0b", "#52514e"


def sigmoid(z):
    return 1 / (1 + np.exp(-z))


class TinyNet:
    """2 inputs → hidden layer (tanh) → 1 output (sigmoid probability)."""

    def __init__(self, hidden=16, lr=0.5, seed=0):
        rng = np.random.default_rng(seed)
        self.W1 = rng.normal(0, 1, (2, hidden)) * np.sqrt(1 / 2)   # small random start
        self.b1 = np.zeros(hidden)
        self.W2 = rng.normal(0, 1, (hidden, 1)) * np.sqrt(1 / hidden)
        self.b2 = np.zeros(1)
        self.lr = lr

    def forward(self, X):
        self.h = np.tanh(X @ self.W1 + self.b1)       # linear + BEND  ← the whole trick
        return sigmoid(self.h @ self.W2 + self.b2).ravel()

    def train_step(self, X, y):
        p = self.forward(X)
        loss = -np.mean(y * np.log(p + 1e-9) + (1 - y) * np.log(1 - p + 1e-9))

        # Backpropagation = the chain rule, applied layer by layer from the output back
        n = len(X)
        d_out = (p - y).reshape(-1, 1) / n            # dLoss/dLogit for sigmoid + cross-entropy
        dW2 = self.h.T @ d_out
        db2 = d_out.sum(axis=0)
        d_h = (d_out @ self.W2.T) * (1 - self.h ** 2) # through tanh: derivative = 1 - tanh²
        dW1 = X.T @ d_h
        db1 = d_h.sum(axis=0)

        for param, grad in [(self.W1, dW1), (self.b1, db1), (self.W2, dW2), (self.b2, db2)]:
            param -= self.lr * grad                   # same downhill step as Day 12
        return loss

    def predict(self, X):
        return (self.forward(X) >= 0.5).astype(int)


class LogisticRegression:
    """No hidden layer → can only learn a straight boundary."""

    def __init__(self, lr=0.5):
        self.w, self.b, self.lr = np.zeros(2), 0.0, lr

    def train_step(self, X, y):
        p = sigmoid(X @ self.w + self.b)
        self.w -= self.lr * X.T @ (p - y) / len(X)
        self.b -= self.lr * np.mean(p - y)

    def predict(self, X):
        return (sigmoid(X @ self.w + self.b) >= 0.5).astype(int)


def plot_boundaries(models, X, y, path):
    xx, yy = np.meshgrid(np.linspace(-2, 3, 300), np.linspace(-1.5, 2, 300))
    grid = np.c_[xx.ravel(), yy.ravel()]
    fig, axes = plt.subplots(1, 2, figsize=(12, 4.8))
    for ax, (title, model) in zip(axes, models.items()):
        zz = model.predict(grid).reshape(xx.shape)
        ax.contourf(xx, yy, zz, levels=[-0.5, 0.5, 1.5], cmap=ListedColormap(["#dbe8f8", "#fbe0d4"]))
        ax.scatter(*X[y == 0].T, s=12, color=BLUE, label="class 0")
        ax.scatter(*X[y == 1].T, s=12, color=ORANGE, label="class 1")
        acc = (model.predict(X) == y).mean()
        ax.set_title(f"{title} — accuracy {acc:.0%}", loc="left", color=INK, fontweight="bold")
        ax.set_xticks([])
        ax.set_yticks([])
        ax.legend(frameon=False, loc="lower left")
    fig.tight_layout()
    fig.savefig(path, dpi=150)
    plt.close(fig)


if __name__ == "__main__":
    X, y = make_moons(n_samples=500, noise=0.18, random_state=0)   # two interleaved half-moons

    linear, net = LogisticRegression(), TinyNet(hidden=16)
    for epoch in range(3001):
        linear.train_step(X, y)
        loss = net.train_step(X, y)
        if epoch % 500 == 0:
            print(f"epoch {epoch:>4}  net loss {loss:.3f}  "
                  f"acc: linear {(linear.predict(X) == y).mean():.0%} | "
                  f"network {(net.predict(X) == y).mean():.0%}")

    (HERE / "output").mkdir(exist_ok=True)
    plot_boundaries({"Linear model (no hidden layer)": linear, "Neural net (16 hidden neurons)": net},
                    X, y, HERE / "output" / "decision_boundary.png")
    print("\nSaved → output/decision_boundary.png")
