# Day 02 — Functions & Control Flow

## 🎯 Goal
Write functions that are small, testable and reusable — and understand *why* Python lets you pass functions around like data.

## 🧠 First Principles

**1. A function is an object.** `def` creates a function object and binds a name to it. So you can store functions in lists, pass them as arguments, and return them from other functions.

```python
rules = [has_digit, has_upper, long_enough]   # a list of functions
all(rule(pw) for rule in rules)               # run them all
```
This one idea is the root of decorators, callbacks, web route handlers and ML loss functions.

**2. Scope = where Python looks up a name: LEGB.**
`L`ocal → `E`nclosing function → `G`lobal (module) → `B`uilt-ins. First match wins.

**3. Closures remember.** An inner function keeps access to the variables of the function that created it — even after that function has returned. That's how you build "function factories".

**4. Default arguments are evaluated ONCE**, at `def` time. So `def f(items=[])` shares one list across all calls. Use `None` and create inside.

**5. Control flow is just decisions + repetition.** `if/elif/else`, `for` (over any iterable), `while` (until a condition), `match` (structural pattern matching, 3.10+). Prefer `for` — it can't loop forever.

## 🌍 Real-World Scenario
1. **Password policy engine** — a sign-up form checks passwords against rules. Rules are plain functions, so the security team can add a rule without touching the engine.
2. **Retry with exponential backoff** — every production system that calls a network service retries failures with growing delays (1s, 2s, 4s…).
3. **Command router** with `match` — how CLIs and chatbots dispatch commands.

## 💻 Code
```bash
python main.py
```

![code](screenshots/code.png)
![output](screenshots/output.png)

## 🏋️ Exercises
1. Add a rule `not_common(pw)` that rejects passwords in a small set of common passwords.
2. Make `make_min_length_rule(n)` — a closure that returns a rule for any length.
3. Add *jitter* (random ±20%) to the retry delay. Why do big systems need jitter? (Hint: thundering herd.)
4. Show the mutable-default bug in 3 lines, then fix it.

## ✅ Takeaways
- Functions are values → you can compose behavior instead of writing `if` chains.
- Closures = function + the variables it remembers.
- Never use a mutable object as a default argument.
