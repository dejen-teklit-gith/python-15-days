# Day 09 — HTTP & APIs

## 🎯 Goal
Understand what actually travels over the wire, then write an API client that behaves like production code: timeouts, retries, pagination, auth, rate limits.

## 🧠 First Principles

**1. The web is just text requests and text responses.** Every API call — Stripe, OpenAI, GitHub — is this:
```
GET /users/ada?page=2 HTTP/1.1          ← method + path + query
Host: api.example.com                   ← headers (metadata)
Accept: application/json

HTTP/1.1 200 OK                          ← status code
Content-Type: application/json          ← headers
                                         ← blank line
{"message": "hello"}                     ← body
```
`main.py` opens a raw socket and prints exactly this. Once you've seen it, `requests` stops being magic.

**2. The verbs and codes you need**
| Method | Meaning | | Code | Meaning |
|---|---|---|---|---|
| GET | read | | 2xx | success |
| POST | create | | 3xx | go elsewhere |
| PUT/PATCH | replace/update | | 4xx | **your** fault (400 bad input, 401 no auth, 404 missing, 429 slow down) |
| DELETE | remove | | 5xx | **their** fault → safe to retry |

**3. Production rules for any API client**
- **Always set a timeout.** Without one, a hung server hangs your program forever.
- **Retry only transient errors** (429, 5xx) with backoff (Day 2's idea, now built in via `Retry`).
- **Paginate.** APIs return pages; follow the `next` link until there isn't one.
- **Secrets from environment variables**, never in code or Git.
- **Reuse a `Session`** — keeps the TCP connection open and holds shared headers.

## 🌍 Real-World Scenario
A tech recruiter wants a one-screen summary of a candidate's GitHub: active repos, stars, languages, best projects, abandoned projects. Build it against the real GitHub REST API.

## 💻 Code
```bash
python main.py torvalds              # live API
python main.py --offline             # bundled sample data (fictional user)
export GITHUB_TOKEN=ghp_...          # optional: 5000 req/h instead of 60
```

![code](screenshots/code.png)
![output](screenshots/output.png)

> 💡 Try it on **your own username** — it's a nice screenshot for this repo.

## 🏋️ Exercises
1. Add "most-used language by *stars*" (weighted), not just by repo count.
2. Cache responses to disk with an `ETag` + `If-None-Match` header — GitHub doesn't count 304 responses against your rate limit.
3. Fetch the top repo's README via `/repos/{owner}/{repo}/readme` and print its first line.
4. Rewrite `fetch_all_repos` with `httpx.AsyncClient` (Day 8) to fetch several users concurrently.

## ✅ Takeaways
- HTTP = method + path + headers + body → status + headers + body.
- 4xx: fix your request. 5xx/429: retry with backoff.
- Timeout, retry, paginate, authenticate — every time.
