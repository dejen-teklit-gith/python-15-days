"""Day 08 — Concurrency: I/O-bound (threads, asyncio) vs CPU-bound (processes).

python main.py          → simulated network (works offline, deterministic)
python main.py --real   → checks real websites with httpx (needs internet)
"""
import asyncio
import hashlib
import sys
import time
from concurrent.futures import ProcessPoolExecutor, ThreadPoolExecutor

SITES = {
    "https://www.python.org": 0.35,
    "https://pypi.org": 0.25,
    "https://github.com": 0.40,
    "https://docs.python.org": 0.30,
    "https://www.wikipedia.org": 0.45,
    "https://news.ycombinator.com": 0.20,
    "https://this-site-does-not-exist.invalid": None,     # simulated failure
    "https://example.com": 0.15,
}


# ── I/O-bound: the CPU mostly WAITS ─────────────────────────────────────────
def check_sync(url: str) -> tuple[str, str]:
    delay = SITES[url]
    if delay is None:
        time.sleep(0.1)
        return url, "DOWN (DNS error)"
    time.sleep(delay)                              # blocks this thread while "waiting"
    return url, f"UP   {int(delay * 1000)} ms"


async def check_async(url: str) -> tuple[str, str]:
    delay = SITES[url]
    if delay is None:
        await asyncio.sleep(0.1)
        return url, "DOWN (DNS error)"
    await asyncio.sleep(delay)                     # yields control to other tasks
    return url, f"UP   {int(delay * 1000)} ms"


async def check_real(client, url: str) -> tuple[str, str]:
    start = time.perf_counter()
    try:
        r = await client.get(url, timeout=5, follow_redirects=True)
        return url, f"UP   {r.status_code} {int((time.perf_counter() - start) * 1000)} ms"
    except Exception as err:                       # report, don't crash the batch
        return url, f"DOWN ({type(err).__name__})"


async def run_async(real: bool):
    if real:
        import httpx
        async with httpx.AsyncClient() as client:
            return await asyncio.gather(*(check_real(client, u) for u in SITES))
    return await asyncio.gather(*(check_async(u) for u in SITES))


# ── CPU-bound: the CPU is BUSY the whole time ───────────────────────────────
def crack_pin(target_hash: str) -> str | None:
    """Brute-force a 6-digit PIN from its SHA-256 hash (pure computation)."""
    for pin in range(1_000_000):
        candidate = f"{pin:06d}"
        if hashlib.sha256(candidate.encode()).hexdigest() == target_hash:
            return candidate
    return None


def pool_map(executor_cls, fn, items, workers):
    with executor_cls(max_workers=workers) as pool:     # `with` shuts the pool down
        return list(pool.map(fn, items))


def timed(label, fn):
    start = time.perf_counter()
    result = fn()
    print(f"  {label:<32} {time.perf_counter() - start:6.2f}s")
    return result


if __name__ == "__main__":
    real = "--real" in sys.argv
    urls = list(SITES)

    print("=== I/O-bound: uptime check of 8 sites ===")
    if not real:
        timed("sequential", lambda: [check_sync(u) for u in urls])
        timed("threads (ThreadPoolExecutor)",
              lambda: pool_map(ThreadPoolExecutor, check_sync, urls, 8))
    results = timed("asyncio.gather", lambda: asyncio.run(run_async(real)))
    for url, status in results:
        print(f"    {'🟢' if status.startswith('UP') else '🔴'} {status:<18} {url}")

    print("\n=== CPU-bound: crack 4 PIN hashes ===")
    pins = ["934871", "120394", "777001", "552310"]
    hashes = [hashlib.sha256(p.encode()).hexdigest() for p in pins]
    timed("sequential", lambda: [crack_pin(h) for h in hashes])
    timed("threads (GIL → no speed-up)",
          lambda: pool_map(ThreadPoolExecutor, crack_pin, hashes, 4))
    found = timed("processes (true parallelism)",
                  lambda: pool_map(ProcessPoolExecutor, crack_pin, hashes, 4))
    print(f"    recovered PINs: {found}")
