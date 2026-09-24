"""Day 11 — E-commerce sales report with pandas: clean → shape → answer → chart."""
from pathlib import Path

import matplotlib

matplotlib.use("Agg")                       # render to file, no window needed
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402

HERE = Path(__file__).parent
OUT = HERE / "output"
BLUE, INK, MUTED, GRID = "#2a78d6", "#0b0b0b", "#52514e", "#e6e5e0"


def vectorization_demo() -> None:
    """Why pandas/numpy: operate on whole columns in C, not row-by-row in Python."""
    import time
    prices = np.random.default_rng(0).random(2_000_000) * 100
    as_list = prices.tolist()
    t = time.perf_counter()
    loop = [p * 1.077 for p in as_list]                       # plain Python loop
    t_loop = time.perf_counter() - t
    t = time.perf_counter()
    vec = prices * 1.077                                      # one vectorized op
    t_vec = time.perf_counter() - t
    assert np.allclose(loop, vec)
    print(f"Add 7.7% VAT to 2M prices: loop {t_loop:.3f}s vs vectorized {t_vec:.4f}s "
          f"(≈{t_loop / t_vec:.0f}× faster)\n")


def load_and_clean(path: Path) -> pd.DataFrame:
    df = pd.read_csv(path, parse_dates=["order_date"])
    before = len(df)
    df = df.drop_duplicates()
    df = df[df["quantity"] > 0]                               # boolean mask filter
    df = df.dropna(subset=["unit_price"])
    print(f"Cleaning: {before} rows → {len(df)} "
          f"(removed duplicates, negative quantities, missing prices)")
    return df.assign(
        revenue=lambda d: d["unit_price"] * d["quantity"],    # new column, whole column at once
        month=lambda d: d["order_date"].dt.to_period("M"),
    )


def analyze(df: pd.DataFrame) -> dict:
    sold = df[df["status"] == "delivered"]

    monthly = sold.groupby("month")["revenue"].sum()
    # Trap: the last month is usually incomplete → it looks like a crash. Drop it.
    last_day = df["order_date"].max()
    if last_day < last_day.to_period("M").to_timestamp(how="end").normalize():
        print(f"Note: {monthly.index[-1]} is incomplete (data ends {last_day:%d %b}) → excluded")
        monthly = monthly.iloc[:-1]
    by_category = (
        sold.groupby("category")
        .agg(revenue=("revenue", "sum"), orders=("order_id", "nunique"),
             avg_order=("revenue", "mean"))
        .sort_values("revenue", ascending=False)
    )
    return_rate = (
        df.assign(returned=df["status"].eq("returned"))
        .groupby("category")["returned"].mean()
        .sort_values(ascending=False)
    )
    country_x_cat = sold.pivot_table(index="country", columns="category",
                                     values="revenue", aggfunc="sum").round(0)
    # Top 10% of customers: what share of revenue do they bring? (Pareto check)
    per_customer = sold.groupby("customer_id")["revenue"].sum().sort_values(ascending=False)
    top_n = max(1, len(per_customer) // 10)
    top_share = per_customer.head(top_n).sum() / per_customer.sum()

    return {"monthly": monthly, "by_category": by_category, "return_rate": return_rate,
            "pivot": country_x_cat, "top_share": top_share}


def style(ax, title: str) -> None:
    ax.set_title(title, loc="left", fontsize=12, color=INK, pad=12, fontweight="bold")
    ax.spines[["top", "right", "left"]].set_visible(False)
    ax.spines["bottom"].set_color(GRID)
    ax.tick_params(colors=MUTED, length=0)
    ax.grid(axis="y", color=GRID, linewidth=0.8)
    ax.set_axisbelow(True)


def chart(results: dict, path: Path) -> None:
    monthly = results["monthly"]
    cats = results["by_category"]["revenue"].sort_values()

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(13, 4.8), gridspec_kw={"width_ratios": [1.6, 1]})
    fig.patch.set_facecolor("white")

    x = monthly.index.to_timestamp()
    ax1.plot(x, monthly.values / 1000, color=BLUE, linewidth=2)
    peak = monthly.idxmax()
    ax1.scatter([peak.to_timestamp()], [monthly.max() / 1000], color=BLUE, s=40, zorder=3)
    ax1.annotate(f"Peak: {peak.strftime('%b %Y')}\nCHF {monthly.max() / 1000:.0f}k",
                 (peak.to_timestamp(), monthly.max() / 1000), xytext=(10, -6),
                 textcoords="offset points", color=INK, fontsize=9, va="top")
    style(ax1, "Monthly delivered revenue (CHF thousands)")
    ax1.set_ylim(bottom=0)

    ax2.barh(cats.index, cats.values / 1000, color=BLUE, height=0.6)
    for i, v in enumerate(cats.values / 1000):
        ax2.text(v + 3, i, f"{v:.0f}k", va="center", color=MUTED, fontsize=9)
    style(ax2, "Revenue by category (CHF thousands)")
    ax2.grid(axis="y", visible=False)
    ax2.grid(axis="x", color=GRID, linewidth=0.8)

    fig.tight_layout()
    fig.savefig(path, dpi=150)
    plt.close(fig)


if __name__ == "__main__":
    pd.set_option("display.width", 120)
    vectorization_demo()
    df = load_and_clean(HERE / "orders.csv")
    r = analyze(df)

    print("\n📦 Revenue by category")
    print(r["by_category"].round(1).to_string())
    print("\n↩️  Return rate by category")
    print((r["return_rate"] * 100).round(1).astype(str).add("%").to_string())
    print("\n🌍 Revenue: country × category")
    print(r["pivot"].to_string())
    print(f"\n👑 Top 10% of customers bring {r['top_share']:.0%} of revenue")

    OUT.mkdir(exist_ok=True)
    chart(r, OUT / "sales_report.png")
    r["by_category"].to_csv(OUT / "by_category.csv")
    print(f"\nSaved chart → {OUT / 'sales_report.png'}")
