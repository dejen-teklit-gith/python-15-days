# Day 10 — Web Backends

## 🎯 Goal
Build a real REST API with a database, input validation, proper status codes, auto-generated docs and tests.

## 🧠 First Principles

**1. An API is a function exposed over the network.**
```python
@app.get("/links/{code}")          # HTTP method + URL pattern  →  which function
def link_stats(code: str): ...      # path/query/body            →  function arguments
                                    # return value               →  JSON response
```
A web framework is just a **router** (URL → function) plus **conversion** (HTTP text ↔ Python objects). That's all Flask, Django and FastAPI fundamentally do.

**2. Validate at the boundary — with types.** `LinkIn(url: HttpUrl)` means FastAPI (via Pydantic) rejects bad input with a `422` *before* your function runs. Your code only ever sees valid data.

**3. A database is a file with guarantees.** SQLite gives you **transactions**: a group of changes either all happens or none does (`commit` / `rollback`). Always use `?` placeholders — building SQL with f-strings is how SQL-injection attacks happen.

**4. Dependency injection.** `db = Depends(get_db)` — the framework opens a connection for each request and closes it afterwards. Tests can swap it out.

**5. Status codes are part of your API's contract.** `201` created · `204` deleted · `307` redirect · `404` missing · `409` conflict · `422` invalid input.

## 🧩 Which framework?
| | FastAPI | Flask | Django |
|---|---|---|---|
| Best for | APIs, ML serving | small apps | full sites (admin, auth, ORM) |
| Async | ✅ native | partial | partial |
| Validation & docs | ✅ built-in | add-ons | DRF add-on |

## 🌍 Real-World Scenario
Marketing needs short links (`/promo`) for campaigns and wants to see click counts. Build **Shorty**: create, list, stats, delete, redirect.

## 💻 Code
```bash
uvicorn app:app --reload          # then open http://127.0.0.1:8000/docs
pytest -v                         # 7 tests, no server needed
```
```bash
curl -X POST localhost:8000/links -H "content-type: application/json" \
     -d '{"url": "https://docs.python.org/3/", "custom_code": "pydocs"}'
curl -i localhost:8000/pydocs     # 307 redirect
```

![swagger docs](screenshots/docs.png)
![tests](screenshots/tests.png)

> 💡 The `/docs` page (Swagger UI) is generated automatically from your type hints — the best screenshot of the day.

## 🏋️ Exercises
1. Add an `expires_at` field; expired links return `410 Gone`.
2. Add a simple API key: requests to `POST /links` need header `X-API-Key` (read the key from an env var).
3. Log each click (timestamp, user-agent) in a second table and add `/links/{code}/clicks`.
4. Replace raw SQL with **SQLModel** or **SQLAlchemy** and compare.

## ✅ Takeaways
- Route + validation + DB + status codes = a backend.
- Type hints do triple duty: validation, editor help, API docs.
- Parameterised SQL only. Always.
