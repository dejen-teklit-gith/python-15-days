# Day 05 — Object-Oriented Design

## 🎯 Goal
Know **when** a class helps, and design classes that make wrong states impossible.

## 🧠 First Principles

**1. A class bundles data with the rules that protect it.** A `dict` for a cart lets anyone set `quantity = -5`. A `Cart` class can refuse. That's the whole point: **invariants** (things that must always be true) live next to the data.

**2. Four ideas, in plain words**
| Idea | Plain meaning | In this project |
|---|---|---|
| Encapsulation | Change state only through methods that check the rules | `cart.add()` rejects bad quantities |
| Composition | An object *has* other objects | `Cart` has `LineItem`s and `Discount`s |
| Polymorphism | Different objects, same method name | every discount has `.apply(subtotal)` |
| Inheritance | "is-a" reuse — use sparingly | `PercentOff` *is a* `Discount` |

> **Prefer composition over inheritance.** Deep class trees are the #1 OOP mistake in real codebases.

**3. Dunder methods plug your objects into Python.** `__len__` → `len(cart)`, `__iter__` → `for item in cart`, `__repr__` → readable debugging, `__eq__` → comparisons. Your objects then feel native.

**4. `@dataclass` removes boilerplate** (`__init__`, `__repr__`, `__eq__`) for classes that are mostly data. `frozen=True` makes them immutable.

**5. When NOT to use a class:** if it has one method and no state, it's a function.

## 🌍 Real-World Scenario
An online shop's cart: products, quantities, stock limits, and **pluggable pricing rules** (10% off, "buy 3 pay 2", free shipping over CHF 100). Marketing invents new promos weekly — adding one must not require editing the cart.

This is the **Strategy pattern**: the cart doesn't know *how* a discount works, only that it has `.apply()`.

## 💻 Code
```bash
python main.py
```

![code](screenshots/code.png)
![output](screenshots/output.png)

## 🏋️ Exercises
1. Add `FixedAmountOff(amount, min_subtotal)` — no changes to `Cart` allowed.
2. Add `__contains__` so `"SKU-1" in cart` works.
3. Make `Product` frozen and try to change its price. What happens and why is that good?
4. Add a `remove(sku, qty)` method that keeps all invariants.
5. **Business-logic bug hunt:** the 10% is calculated on the subtotal *before* the "buy 3 pay 2" saving, so the customer gets 10% off a free pair of socks. Real shops decide a **stacking order**. Make each discount see the price *after* the previous ones.

## ✅ Takeaways
- Classes exist to protect invariants, not to "organise code".
- Program to an interface (`.apply()`), not to a concrete class.
- Dunder methods make your objects behave like built-ins.
