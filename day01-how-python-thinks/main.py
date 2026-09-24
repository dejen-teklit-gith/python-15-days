"""Day 01 — How Python Thinks: the object model + a trip expense splitter."""
from decimal import Decimal


# ── Part 1: the mental model ────────────────────────────────────────────────
def demo_object_model() -> None:
    print("=== Names are labels ===")
    a = [1, 2, 3]
    b = a                       # second label, SAME object
    b.append(4)
    print(f"a={a}  b={b}  same object? {a is b}")

    c = a.copy()                # new object with equal value
    print(f"c == a: {c == a}   c is a: {c is a}")

    print("\n=== Immutable 'changes' create new objects ===")
    s = "hello"
    before = id(s)
    s += " world"
    print(f"id changed after += on str? {before != id(s)}")

    print("\n=== Floats are approximations ===")
    print(f"0.1 + 0.2 == 0.3 -> {0.1 + 0.2 == 0.3}  ({0.1 + 0.2!r})")
    print(f"Decimal: {Decimal('0.1') + Decimal('0.2') == Decimal('0.3')}")


# ── Part 2: real-world — who owes whom? ─────────────────────────────────────
CENT = Decimal("0.01")

EXPENSES = [
    {"payer": "Amina", "amount": "240.00", "what": "Hotel"},
    {"payer": "Bruno", "amount": "86.40", "what": "Dinner"},
    {"payer": "Chen", "amount": "45.10", "what": "Fuel"},
    {"payer": "Amina", "amount": "30.00", "what": "Museum"},
]
PEOPLE = ["Amina", "Bruno", "Chen", "Dawit"]


def balances(expenses: list[dict], people: list[str]) -> dict[str, Decimal]:
    """Positive = is owed money. Negative = owes money."""
    total = sum(Decimal(e["amount"]) for e in expenses)
    # Work in whole cents so no money is created or lost by rounding.
    total_cents = int(total / CENT)
    base, leftover = divmod(total_cents, len(people))
    # The first `leftover` people pay one extra cent → shares sum EXACTLY to total.
    bal = {p: -Decimal(base + (1 if i < leftover else 0)) * CENT
           for i, p in enumerate(people)}
    for e in expenses:
        bal[e["payer"]] += Decimal(e["amount"])
    return bal


def settle(bal: dict[str, Decimal]) -> list[tuple[str, str, Decimal]]:
    """Greedy: biggest debtor pays biggest creditor. Gives at most n-1 transfers."""
    debtors = sorted(([p, -v] for p, v in bal.items() if v < 0), key=lambda x: -x[1])
    creditors = sorted(([p, v] for p, v in bal.items() if v > 0), key=lambda x: -x[1])
    transfers, i, j = [], 0, 0
    while i < len(debtors) and j < len(creditors):
        amount = min(debtors[i][1], creditors[j][1])
        transfers.append((debtors[i][0], creditors[j][0], amount))
        debtors[i][1] -= amount
        creditors[j][1] -= amount
        if debtors[i][1] == 0:
            i += 1
        if creditors[j][1] == 0:
            j += 1
    return transfers


if __name__ == "__main__":
    demo_object_model()

    print("\n=== Trip Settle-Up ===")
    bal = balances(EXPENSES, PEOPLE)
    for person, value in bal.items():
        print(f"{person:<6} {value:>+9}")
    print(f"Sum of balances (must be 0): {sum(bal.values())}")

    print("\nTransfers:")
    for frm, to, amt in settle(bal):
        print(f"  {frm} → {to}: CHF {amt}")
