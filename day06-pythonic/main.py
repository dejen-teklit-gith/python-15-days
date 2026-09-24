"""Day 06 — Pythonic power tools: generators, decorators, context managers."""
import functools
import random
import time
import tracemalloc
from contextlib import contextmanager
from itertools import islice


# ── Decorators: functions that wrap functions ───────────────────────────────
def timed(func):
    """Print how long a call took. @functools.wraps keeps the original name/docs."""
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        start = time.perf_counter()
        result = func(*args, **kwargs)
        print(f"  ⏱ {func.__name__} took {time.perf_counter() - start:.3f}s")
        return result
    return wrapper


def validate_positive(*arg_names):
    """Decorator FACTORY (takes arguments) → returns a decorator."""
    def decorator(func):
        @functools.wraps(func)
        def wrapper(**kwargs):
            for name in arg_names:
                if kwargs[name] <= 0:
                    raise ValueError(f"{name} must be > 0, got {kwargs[name]}")
            return func(**kwargs)
        return wrapper
    return decorator


# ── Context manager: setup / guaranteed teardown ────────────────────────────
@contextmanager
def memory_peak(label: str):
    tracemalloc.start()
    try:
        yield
    finally:                                   # runs even if the block raises
        _, peak = tracemalloc.get_traced_memory()
        tracemalloc.stop()
        print(f"  🧠 {label}: peak memory {peak / 1024:,.0f} KB")


# ── Generators: a lazy pipeline over a "huge" log stream ────────────────────
def read_events(n: int):
    """Simulates reading a giant file line by line. Nothing is stored."""
    rng = random.Random(42)
    for i in range(n):
        yield f"{i},{rng.choice(['info', 'warn', 'error'])},{rng.randint(5, 900)}"


def parse(lines):
    for line in lines:
        idx, level, ms = line.split(",")
        yield {"id": int(idx), "level": level, "ms": int(ms)}


def only(level, events):
    return (e for e in events if e["level"] == level)      # generator expression


@timed
def eager_pipeline(n: int) -> float:
    lines = [line for line in read_events(n)]               # materialise everything
    events = [e for e in parse(lines)]
    errors = [e for e in events if e["level"] == "error"]
    return sum(e["ms"] for e in errors) / len(errors)


@timed
def lazy_pipeline(n: int) -> float:
    total = count = 0
    for e in only("error", parse(read_events(n))):         # one item in flight
        total += e["ms"]
        count += 1
    return total / count


# ── Caching: remember results of pure functions ─────────────────────────────
@functools.lru_cache(maxsize=None)
def shipping_quote(weight_kg: int, zone: int) -> float:
    time.sleep(0.2)                     # pretend this calls a slow carrier API
    return round(4.9 + weight_kg * 1.2 * zone, 2)


@validate_positive("amount", "rate")
def monthly_payment(*, amount: float, rate: float, months: int) -> float:
    r = rate / 12
    return round(amount * r / (1 - (1 + r) ** -months), 2)


if __name__ == "__main__":
    N = 300_000
    print("=== Eager (lists) vs lazy (generators) ===")
    with memory_peak("eager"):
        print(f"  avg error latency = {eager_pipeline(N):.1f} ms")
    with memory_peak("lazy"):
        print(f"  avg error latency = {lazy_pipeline(N):.1f} ms")

    print("\n=== First 3 warnings, without reading the rest (islice) ===")
    for e in islice(only("warn", parse(read_events(10**12))), 3):   # 1 trillion "lines"!
        print(f"  {e}")

    print("\n=== lru_cache ===")
    for _ in range(3):
        t = time.perf_counter()
        quote = shipping_quote(5, 2)
        print(f"  quote={quote}  in {time.perf_counter() - t:.3f}s")
    print(f"  {shipping_quote.cache_info()}")

    print("\n=== Decorator with arguments ===")
    print(f"  mortgage payment: {monthly_payment(amount=500_000, rate=0.02, months=300)}")
    try:
        monthly_payment(amount=-1, rate=0.02, months=12)
    except ValueError as err:
        print(f"  rejected: {err}")
