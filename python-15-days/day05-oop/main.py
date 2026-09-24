"""Day 05 — Shopping cart with pluggable pricing rules (Strategy pattern)."""
from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from decimal import Decimal

CENT = Decimal("0.01")


@dataclass(frozen=True)              # immutable: a product's identity never changes
class Product:
    sku: str
    name: str
    price: Decimal
    stock: int


@dataclass
class LineItem:
    product: Product
    qty: int

    @property
    def total(self) -> Decimal:
        return self.product.price * self.qty


# ── Discounts: one interface, many implementations ──────────────────────────
class Discount(ABC):
    label: str

    @abstractmethod
    def apply(self, cart: Cart) -> Decimal:
        """Return the amount to subtract (>= 0)."""


class PercentOff(Discount):
    def __init__(self, percent: int):
        if not 0 < percent <= 100:
            raise ValueError("percent must be in 1..100")
        self.percent = percent
        self.label = f"{percent}% off"

    def apply(self, cart: Cart) -> Decimal:
        return cart.subtotal * self.percent / 100


class BuyXPayY(Discount):
    def __init__(self, sku: str, x: int, y: int):
        self.sku, self.x, self.y = sku, x, y
        self.label = f"Buy {x} pay {y} on {sku}"

    def apply(self, cart: Cart) -> Decimal:
        item = cart.items.get(self.sku)
        if not item:
            return Decimal(0)
        free_units = (item.qty // self.x) * (self.x - self.y)
        return free_units * item.product.price


class FreeShippingOver(Discount):
    def __init__(self, threshold: Decimal):
        self.threshold = threshold
        self.label = f"Free shipping over {threshold}"

    def apply(self, cart: Cart) -> Decimal:
        return cart.shipping if cart.subtotal >= self.threshold else Decimal(0)


# ── The cart: owns the invariants ───────────────────────────────────────────
@dataclass
class Cart:
    shipping: Decimal = Decimal("9.90")
    items: dict[str, LineItem] = field(default_factory=dict)
    discounts: list[Discount] = field(default_factory=list)

    def add(self, product: Product, qty: int = 1) -> None:
        if qty <= 0:
            raise ValueError("quantity must be positive")
        current = self.items[product.sku].qty if product.sku in self.items else 0
        if current + qty > product.stock:
            raise ValueError(f"only {product.stock} × {product.name} in stock")
        self.items[product.sku] = LineItem(product, current + qty)

    def add_discount(self, discount: Discount) -> None:
        self.discounts.append(discount)

    @property
    def subtotal(self) -> Decimal:
        return sum((i.total for i in self.items.values()), Decimal(0))

    def breakdown(self) -> list[tuple[str, Decimal]]:
        return [(d.label, d.apply(self).quantize(CENT)) for d in self.discounts]

    @property
    def total(self) -> Decimal:
        savings = sum((amt for _, amt in self.breakdown()), Decimal(0))
        return max(Decimal(0), self.subtotal + self.shipping - savings).quantize(CENT)

    # Dunder methods: make Cart feel like a built-in container
    def __len__(self) -> int:
        return sum(i.qty for i in self.items.values())

    def __iter__(self):
        return iter(self.items.values())

    def __repr__(self) -> str:
        return f"Cart({len(self)} items, total={self.total})"


if __name__ == "__main__":
    socks = Product("SKU-1", "Merino socks", Decimal("12.50"), stock=10)
    bottle = Product("SKU-2", "Steel bottle", Decimal("29.00"), stock=3)
    mug = Product("SKU-3", "Coffee mug", Decimal("18.00"), stock=5)

    cart = Cart()
    cart.add(socks, 3)
    cart.add(bottle, 2)
    cart.add(mug)

    for bad in [lambda: cart.add(bottle, 5), lambda: cart.add(mug, 0)]:
        try:
            bad()
        except ValueError as err:
            print(f"Rejected: {err}")

    cart.add_discount(BuyXPayY("SKU-1", x=3, y=2))
    cart.add_discount(PercentOff(10))
    cart.add_discount(FreeShippingOver(Decimal("100")))

    print("\n🧾 Receipt")
    for item in cart:
        print(f"  {item.qty} × {item.product.name:<20} {item.total:>8}")
    print(f"  {'Subtotal':<24} {cart.subtotal:>8}")
    print(f"  {'Shipping':<24} {cart.shipping:>8}")
    for label, amount in cart.breakdown():
        print(f"  {label:<24} {-amount:>8}")
    print(f"  {'TOTAL':<24} {cart.total:>8}")
    print(f"\nrepr → {cart!r}")
