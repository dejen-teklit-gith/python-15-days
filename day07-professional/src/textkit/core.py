"""Core text functions. Pure functions → trivial to test."""
import logging
import math
import re
import unicodedata

log = logging.getLogger(__name__)          # module-level logger, configured by the app

WORDS_PER_MINUTE = 230
EMAIL_RE = re.compile(r"\b([\w.+-])[\w.+-]*@([\w-]+\.[\w.-]+)\b")
PHONE_RE = re.compile(r"\+?\d[\d\s-]{7,}\d")


def slugify(title: str, max_len: int = 60) -> str:
    """'Zürich's Best Café!' → 'zurichs-best-cafe'. Used for URLs."""
    if not title or not title.strip():
        raise ValueError("title must not be empty")
    # Decompose accents (é → e + ´) then drop the non-ASCII marks
    ascii_text = unicodedata.normalize("NFKD", title).encode("ascii", "ignore").decode()
    ascii_text = ascii_text.replace("'", "")
    slug = re.sub(r"[^a-z0-9]+", "-", ascii_text.lower()).strip("-")
    if len(slug) > max_len:
        slug = slug[:max_len].rsplit("-", 1)[0]       # don't cut a word in half
        log.debug("slug truncated to %d chars", len(slug))
    return slug


def reading_time(text: str, wpm: int = WORDS_PER_MINUTE) -> int:
    """Minutes to read, rounded up, minimum 1."""
    if wpm <= 0:
        raise ValueError("wpm must be positive")
    words = len(text.split())
    return max(1, math.ceil(words / wpm))


def mask_pii(text: str) -> str:
    """Hide emails and phone numbers before logging or sharing text."""
    masked = EMAIL_RE.sub(r"\1***@\2", text)
    masked, n = PHONE_RE.subn("[phone]", masked)
    if n:
        log.info("masked %d phone number(s)", n)
    return masked


def summarize(text: str, max_sentences: int = 2) -> str:
    """Naive extractive summary: first N sentences."""
    sentences = re.split(r"(?<=[.!?])\s+", text.strip())
    return " ".join(sentences[:max_sentences])
