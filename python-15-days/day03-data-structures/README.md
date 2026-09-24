# Day 03 — Data Structures

## 🎯 Goal
Choose the right container instantly — because the right structure turns a slow, messy program into a fast, obvious one.

## 🧠 First Principles

**Pick the structure by the question you'll ask of it.**

| Question you'll ask | Structure | Lookup cost | Why |
|---|---|---|---|
| "What's the *n*-th item?" / keep order | `list` | O(1) by index, **O(n)** by value | contiguous array |
| "What's the value for this key?" | `dict` | **O(1)** | hash table |
| "Have I seen this before?" | `set` | **O(1)** | hash table without values |
| "A fixed record that must not change" | `tuple` / `namedtuple` | O(1) index | immutable → hashable → can be a dict key |
| "How many of each?" | `collections.Counter` | O(1) | dict specialised for counting |
| "Group items by key" | `collections.defaultdict(list)` | O(1) | no `if key not in d` boilerplate |
| "Last N items / queue" | `collections.deque(maxlen=N)` | O(1) at both ends | ring buffer |
| "Top-k / next most urgent" | `heapq` | O(log n) push/pop | binary heap |

**Why is `dict` O(1)?** Python hashes the key to a number, uses it as an index into an array, and jumps straight there. That's also why keys must be **immutable** (a key that changes would change its hash and get lost).

**Rule of thumb:** if you write `if x in some_list` inside a loop, you probably want a `set`.

## 🌍 Real-World Scenario
You're on call. The website is slow and someone might be brute-forcing logins. You have `access.log` (~700 lines). Answer in seconds:
- Top endpoints & error rate
- 95th-percentile latency per endpoint (the number SREs actually watch)
- IPs with suspicious bursts of failed logins (sliding window)
- Unique visitors

## 💻 Code
```bash
python main.py            # analyzes access.log
```

![code](screenshots/code.png)
![output](screenshots/output.png)

## 🏋️ Exercises
1. Time `x in big_list` vs `x in big_set` with 1,000,000 items using `timeit`. Explain the gap.
2. Add "requests per minute" and print the busiest minute.
3. Use `heapq.nlargest` to show the 5 slowest individual requests.
4. Make the brute-force detector configurable: N failures within T seconds.

## ✅ Takeaways
- `dict`/`set` membership is O(1); `list` membership is O(n).
- `Counter`, `defaultdict`, `deque` remove 90% of hand-written bookkeeping.
- Parse → structure → query. Get the data into the right shape first; the answers become one-liners.
