# Day 06 — Pythonic Power Tools

## 🎯 Goal
Master the four tools that separate "Python that works" from "Python that professionals write": **comprehensions, generators, decorators, context managers**.

## 🧠 First Principles

**1. Laziness: compute only what you need, when you need it.**
A list holds *every* item in memory. A **generator** holds *one* item and a recipe for the next.

```python
[x * 2 for x in data]   # list: builds everything now
(x * 2 for x in data)   # generator: builds each value on demand
```
`yield` pauses a function and hands back a value; the next `next()` resumes it right where it stopped. Chain generators and you get a **streaming pipeline** — the same idea behind Unix pipes, Spark and data loaders in PyTorch.

**2. A decorator is just `f = wrap(f)`.** Because functions are objects (Day 2), you can write a function that takes a function and returns an upgraded one.
```python
@timed            # identical to:  slow = timed(slow)
def slow(): ...
```
Used everywhere: `@app.get("/")` in FastAPI, `@pytest.fixture`, `@lru_cache`, `@login_required`.

**3. Context managers = guaranteed setup/teardown.** `with X:` calls `X.__enter__()` then *always* `X.__exit__()` — even on error. Use it for anything you must release: files, locks, DB transactions, timers.

**4. Caching pure functions.** If a function always returns the same output for the same input, remember the answer: `@functools.lru_cache`.

## 🌍 Real-World Scenario
You must compute the average latency of error events from a log far too big for RAM. Compare an **eager** (lists) and a **lazy** (generator) pipeline, measure memory with a context manager and time with a decorator. Then cache a slow shipping-price API call.

## 💻 Code
```bash
python main.py
```
Look at the peak memory numbers: the lazy pipeline uses thousands of times less. And `islice` pulls 3 items from a *trillion-line* stream instantly.

![code](screenshots/code.png)
![output](screenshots/output.png)

## 🏋️ Exercises
1. Write a generator `chunked(iterable, size)` that yields lists of `size` items (batching for DB inserts).
2. Write `@retry(times=3)` as a decorator factory (reuse Day 2's logic).
3. Write a class-based context manager `Timer` with `__enter__`/`__exit__`.
4. Why is `lru_cache` dangerous on a function that reads the current exchange rate?

## ✅ Takeaways
- Generators = constant memory for any data size.
- Decorators add behavior without touching the function body.
- `with` = cleanup you can't forget.
- Only cache **pure** functions.
