"""Day 09 — GitHub profile analyzer: consuming a real REST API properly.

python main.py <username>             → live GitHub API
python main.py <username> --offline   → uses sample_response.json (no internet needed)
Optional: set GITHUB_TOKEN to raise the rate limit from 60 to 5000 requests/hour.
"""
import json
import os
import socket
import sys
import threading
from collections import Counter
from datetime import datetime, timezone
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

API = "https://api.github.com"
HERE = Path(__file__).parent


# ── Part 1: HTTP is just text. See it with a raw socket. ────────────────────
class HelloHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        body = json.dumps({"message": "hello", "path": self.path}).encode()
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, *args):          # silence default logging
        pass


def show_raw_http() -> None:
    server = HTTPServer(("127.0.0.1", 0), HelloHandler)
    threading.Thread(target=server.handle_request, daemon=True).start()
    port = server.server_address[1]

    request = f"GET /users/ada?page=2 HTTP/1.1\r\nHost: localhost:{port}\r\nAccept: application/json\r\n\r\n"
    with socket.create_connection(("127.0.0.1", port)) as sock:
        sock.sendall(request.encode())
        chunks = []
        while chunk := sock.recv(4096):            # read until the server closes
            chunks.append(chunk)
        response = b"".join(chunks).decode()
    server.server_close()
    print("──── what the client sent ────")
    print(request.strip())
    print("──── what the server replied ────")
    print(response.strip())


# ── Part 2: a well-behaved API client ───────────────────────────────────────
def make_session() -> requests.Session:
    session = requests.Session()                                  # reuses TCP connections
    retry = Retry(total=3, backoff_factor=0.5, status_forcelist=[429, 500, 502, 503, 504])
    session.mount("https://", HTTPAdapter(max_retries=retry))     # auto-retry transient errors
    session.headers.update({
        "Accept": "application/vnd.github+json",
        "User-Agent": "python-15-days-profile-analyzer",
    })
    if token := os.getenv("GITHUB_TOKEN"):                        # secrets from env, never code
        session.headers["Authorization"] = f"Bearer {token}"
    return session


def fetch_all_repos(session: requests.Session, username: str) -> list[dict]:
    """Follow pagination via the `Link` header until there's no next page."""
    repos, url = [], f"{API}/users/{username}/repos"
    params = {"per_page": 100, "sort": "pushed"}
    while url:
        resp = session.get(url, params=params, timeout=10)
        if resp.status_code == 404:
            raise SystemExit(f"User {username!r} not found")
        if resp.status_code == 403 and resp.headers.get("X-RateLimit-Remaining") == "0":
            raise SystemExit("Rate limit hit — set GITHUB_TOKEN or wait an hour")
        resp.raise_for_status()
        repos.extend(resp.json())
        url = resp.links.get("next", {}).get("url")
        params = None                       # the next URL already contains them
    return repos


def fetch_live(username: str) -> tuple[dict, list[dict]]:
    session = make_session()
    user = session.get(f"{API}/users/{username}", timeout=10)
    user.raise_for_status()
    return user.json(), fetch_all_repos(session, username)


def fetch_offline() -> tuple[dict, list[dict]]:
    data = json.loads((HERE / "sample_response.json").read_text())
    return data["user"], data["repos"]


# ── Part 3: turn JSON into insight (pure function → easy to test) ───────────
def analyze(user: dict, repos: list[dict], now: datetime | None = None) -> dict:
    now = now or datetime.now(timezone.utc)
    own = [r for r in repos if not r["fork"] and not r.get("archived")]
    langs = Counter(r["language"] for r in own if r["language"])
    stale = [
        r["name"] for r in own
        if (now - datetime.fromisoformat(r["pushed_at"].replace("Z", "+00:00"))).days > 180
    ]
    return {
        "login": user["login"],
        "name": user.get("name"),
        "active_repos": len(own),
        "total_stars": sum(r["stargazers_count"] for r in own),
        "top_languages": langs.most_common(3),
        "top_repos": sorted(own, key=lambda r: r["stargazers_count"], reverse=True)[:3],
        "stale_repos": stale,
    }


def print_report(a: dict) -> None:
    print(f"\n👤 {a['name'] or a['login']} (@{a['login']})")
    print(f"   Active repos: {a['active_repos']}   ⭐ Total stars: {a['total_stars']}")
    print("   Languages:   " + ", ".join(f"{lang} ({n})" for lang, n in a["top_languages"]))
    print("   Top repos:")
    for r in a["top_repos"]:
        print(f"     ⭐ {r['stargazers_count']:>4}  {r['name']:<20} {r['html_url']}")
    print(f"   Not pushed in 6 months: {', '.join(a['stale_repos']) or 'none'}")


if __name__ == "__main__":
    show_raw_http()
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    offline = "--offline" in sys.argv or not args
    user, repos = fetch_offline() if offline else fetch_live(args[0])
    fixed_now = datetime(2026, 9, 24, tzinfo=timezone.utc) if offline else None
    print_report(analyze(user, repos, now=fixed_now))
