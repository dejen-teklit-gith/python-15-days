# Day 08 — Concurrency

## 🎯 Goal
Make programs faster by doing several things at once — and know **which** tool to use, because the wrong one gives zero speed-up.

## 🧠 First Principles

**Waiting ≠ working.** Ask one question: *while my program is slow, is the CPU busy or idle?*

| Your program is… | Example | CPU during the wait | Use |
|---|---|---|---|
| **I/O-bound** (waiting) | HTTP calls, DB queries, file downloads | idle 😴 | `asyncio` or threads |
| **CPU-bound** (working) | hashing, image processing, number crunching | 100% 🔥 | `multiprocessing` / `ProcessPoolExecutor` |

**Why threads don't speed up CPU work in Python: the GIL.** The standard interpreter (CPython) runs Python bytecode on **one thread at a time** (the Global Interpreter Lock). Threads still help for I/O because a thread *releases* the GIL while it waits on the network. For CPU work you need separate **processes** — each has its own interpreter and its own GIL.
> Python 3.13+ ships an optional *free-threaded* build without the GIL — still experimental, but the direction of travel.

**asyncio in one sentence:** a single thread runs an *event loop*; every `await` says "I'm waiting — run someone else meanwhile". Thousands of concurrent connections, one thread, no locks. This is how FastAPI serves requests (Day 10).

```
sequential:  [site1----][site2---][site3-----]      total = sum of waits
concurrent:  [site1----]
             [site2---]                             total ≈ longest wait
             [site3-----]
```

**Rules**
- Never call a blocking function (`time.sleep`, `requests.get`) inside `async def` — it freezes the whole loop. Use `await asyncio.sleep`, `httpx.AsyncClient`.
- Shared mutable state + threads = race conditions. Prefer passing data in and returning results out (as `pool.map` does).

## 🌍 Real-World Scenario
1. **Uptime monitor** (like Pingdom/UptimeRobot): check 8 websites every minute. Sequential takes the *sum* of all response times; concurrent takes the *longest*.
2. **Security audit**: recover 6-digit PINs from leaked SHA-256 hashes (shows why unsalted short PINs are unsafe — and why CPU work needs processes).

## 💻 Code
```bash
python main.py           # offline simulation, reproducible timings
python main.py --real    # real HTTP checks (pip install httpx)
```

![code](screenshots/code.png)
![output](screenshots/output.png)

Typical result: I/O 2.2s → 0.45s with threads/asyncio. CPU: threads give **no** gain; processes scale with your cores.

## 🏋️ Exercises
1. Add a `asyncio.Semaphore(3)` so at most 3 requests run at once (be polite to servers).
2. Run the uptime check every 10 s in a loop and print only **status changes**.
3. Increase to 8 hashes and compare process-pool time with `os.cpu_count()` workers.
4. Explain why a salted hash (`sha256(salt + pin)`) defeats precomputed lookup tables.

## ✅ Takeaways
- I/O-bound → `asyncio` / threads. CPU-bound → processes.
- Concurrency turns *sum of waits* into *max of waits*.
- Measure first: the speed-up is a hypothesis until timed.
