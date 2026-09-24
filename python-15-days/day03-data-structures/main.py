"""Day 03 — Server log analyzer: the right data structure makes every answer a one-liner."""
import re
from collections import Counter, defaultdict, deque
from datetime import datetime
from pathlib import Path
from typing import NamedTuple

LOG_PATTERN = re.compile(
    r'(?P<ip>\S+) - - \[(?P<ts>[^\]]+)\] "(?P<method>\w+) (?P<path>\S+) [^"]+" '
    r"(?P<status>\d{3}) (?P<ms>\d+)ms"
)


class Request(NamedTuple):           # immutable, lightweight record
    ip: str
    ts: datetime
    method: str
    path: str
    status: int
    ms: int


def parse(lines) -> tuple[list[Request], int]:
    requests, bad = [], 0
    for line in lines:
        m = LOG_PATTERN.match(line)
        if not m:
            bad += 1
            continue
        d = m.groupdict()
        requests.append(Request(
            ip=d["ip"],
            ts=datetime.strptime(d["ts"], "%d/%b/%Y:%H:%M:%S %z"),
            method=d["method"],
            path=d["path"].split("?")[0],           # drop query string
            status=int(d["status"]),
            ms=int(d["ms"]),
        ))
    return requests, bad


def percentile(values: list[int], p: float) -> int:
    ordered = sorted(values)
    idx = min(len(ordered) - 1, round(p / 100 * (len(ordered) - 1)))
    return ordered[idx]


def brute_force_suspects(reqs: list[Request], max_fails=5, window_s=10) -> set[str]:
    """IPs with >= max_fails failed logins inside any `window_s`-second window."""
    recent: dict[str, deque] = defaultdict(deque)
    suspects: set[str] = set()
    for r in reqs:
        if r.path != "/login" or r.status != 401:
            continue
        q = recent[r.ip]
        q.append(r.ts)
        while (r.ts - q[0]).total_seconds() > window_s:   # slide the window
            q.popleft()
        if len(q) >= max_fails:
            suspects.add(r.ip)
    return suspects


def report(reqs: list[Request], bad: int) -> None:
    print(f"Parsed {len(reqs)} requests ({bad} malformed lines skipped)")
    print(f"Unique visitors (set): {len({r.ip for r in reqs})}")

    print("\nTop endpoints (Counter):")
    for path, n in Counter(r.path for r in reqs).most_common(5):
        print(f"  {path:<16} {n:>4}")

    errors = sum(r.status >= 500 for r in reqs)
    print(f"\nServer error rate (5xx): {errors / len(reqs):.1%}")

    latency: dict[str, list[int]] = defaultdict(list)     # group by key
    for r in reqs:
        latency[r.path].append(r.ms)
    print("\nLatency per endpoint (p50 / p95 ms):")
    rows = sorted(latency.items(), key=lambda kv: percentile(kv[1], 95), reverse=True)
    for path, ms in rows:
        flag = "  ⚠️ slow" if percentile(ms, 95) > 300 else ""
        print(f"  {path:<16} {percentile(ms, 50):>5} / {percentile(ms, 95):>5}{flag}")

    suspects = brute_force_suspects(reqs)
    print(f"\n🚨 Brute-force suspects (≥5 failed logins in 10s): {suspects or 'none'}")


if __name__ == "__main__":
    log_file = Path(__file__).parent / "access.log"
    reqs, bad = parse(log_file.read_text().splitlines())
    report(reqs, bad)
