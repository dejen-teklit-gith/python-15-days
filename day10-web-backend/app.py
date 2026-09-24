"""Day 10 — URL shortener: FastAPI + SQLite + Pydantic.

Run:   uvicorn app:app --reload
Docs:  http://127.0.0.1:8000/docs   (interactive, auto-generated)
"""
import os
import secrets
import sqlite3
from collections.abc import Iterator
from contextlib import asynccontextmanager, contextmanager
from datetime import datetime, timezone

from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.responses import RedirectResponse
from pydantic import BaseModel, Field, HttpUrl

DB_PATH = os.getenv("SHORTENER_DB", "shortener.db")
ALPHABET = "abcdefghijkmnopqrstuvwxyzABCDEFGHJKLMNPQRSTUVWXYZ23456789"   # no 0/O/1/l/I

# ── Database layer ──────────────────────────────────────────────────────────
def init_db() -> None:
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS links (
                code       TEXT PRIMARY KEY,
                url        TEXT NOT NULL,
                clicks     INTEGER NOT NULL DEFAULT 0,
                created_at TEXT NOT NULL
            )""")


@contextmanager
def connect() -> Iterator[sqlite3.Connection]:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
        conn.commit()               # all-or-nothing: commit only if no exception
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


def get_db() -> Iterator[sqlite3.Connection]:
    """Dependency: FastAPI calls this per request and cleans up afterwards."""
    with connect() as conn:
        yield conn


# ── Schemas: validation at the boundary (Day 4's principle) ────────────────
class LinkIn(BaseModel):
    url: HttpUrl
    custom_code: str | None = Field(None, min_length=3, max_length=20, pattern=r"^[A-Za-z0-9_-]+$")


class LinkOut(BaseModel):
    code: str
    url: str
    short_url: str
    clicks: int
    created_at: str


def to_out(row: sqlite3.Row) -> LinkOut:
    return LinkOut(**dict(row), short_url=f"/{row['code']}")


# ── App + routes: each route is just a function exposed over HTTP ───────────
@asynccontextmanager
async def lifespan(_: FastAPI):
    init_db()                 # runs once at startup
    yield                     # app serves requests here
    # (shutdown cleanup would go here)


app = FastAPI(title="Shorty", version="1.0", description="A tiny, real URL shortener.",
              lifespan=lifespan)


@app.get("/health")
def health() -> dict:
    return {"status": "ok"}


@app.post("/links", response_model=LinkOut, status_code=status.HTTP_201_CREATED)
def create_link(body: LinkIn, db: sqlite3.Connection = Depends(get_db)) -> LinkOut:
    code = body.custom_code or "".join(secrets.choice(ALPHABET) for _ in range(6))
    try:
        db.execute(
            "INSERT INTO links (code, url, created_at) VALUES (?, ?, ?)",   # ? = no SQL injection
            (code, str(body.url), datetime.now(timezone.utc).isoformat(timespec="seconds")),
        )
    except sqlite3.IntegrityError:
        raise HTTPException(status.HTTP_409_CONFLICT, f"code {code!r} is already taken") from None
    row = db.execute("SELECT * FROM links WHERE code = ?", (code,)).fetchone()
    return to_out(row)


@app.get("/links", response_model=list[LinkOut])
def list_links(limit: int = 20, db: sqlite3.Connection = Depends(get_db)) -> list[LinkOut]:
    rows = db.execute("SELECT * FROM links ORDER BY clicks DESC LIMIT ?", (min(limit, 100),))
    return [to_out(r) for r in rows]


@app.get("/links/{code}", response_model=LinkOut)
def link_stats(code: str, db: sqlite3.Connection = Depends(get_db)) -> LinkOut:
    row = db.execute("SELECT * FROM links WHERE code = ?", (code,)).fetchone()
    if row is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "link not found")
    return to_out(row)


@app.delete("/links/{code}", status_code=status.HTTP_204_NO_CONTENT)
def delete_link(code: str, db: sqlite3.Connection = Depends(get_db)) -> None:
    if db.execute("DELETE FROM links WHERE code = ?", (code,)).rowcount == 0:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "link not found")


@app.get("/{code}")
def follow(code: str, db: sqlite3.Connection = Depends(get_db)) -> RedirectResponse:
    row = db.execute("SELECT url FROM links WHERE code = ?", (code,)).fetchone()
    if row is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "link not found")
    db.execute("UPDATE links SET clicks = clicks + 1 WHERE code = ?", (code,))
    return RedirectResponse(row["url"], status_code=status.HTTP_307_TEMPORARY_REDIRECT)
