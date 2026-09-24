"""Tests read like a specification. Run: pytest -v"""
import logging

import pytest

from textkit import mask_pii, reading_time, slugify, summarize


# ── slugify ─────────────────────────────────────────────────────────────────
@pytest.mark.parametrize(
    ("title", "expected"),
    [
        ("Hello World", "hello-world"),
        ("Zürich's Best Café!", "zurichs-best-cafe"),
        ("  Python   3.12 -- What's New?  ", "python-3-12-whats-new"),
        ("Ünïcödé ñ", "unicode-n"),
    ],
)
def test_slugify_examples(title, expected):
    assert slugify(title) == expected


def test_slugify_does_not_cut_words():
    slug = slugify("word " * 30, max_len=22)
    assert len(slug) <= 22
    assert not slug.endswith("-")
    assert all(part == "word" for part in slug.split("-"))


@pytest.mark.parametrize("bad", ["", "   "])
def test_slugify_rejects_empty(bad):
    with pytest.raises(ValueError, match="empty"):
        slugify(bad)


# ── reading_time ────────────────────────────────────────────────────────────
def test_reading_time_minimum_is_one_minute():
    assert reading_time("short") == 1


def test_reading_time_rounds_up():
    assert reading_time("w " * 231) == 2


def test_reading_time_rejects_bad_wpm():
    with pytest.raises(ValueError):
        reading_time("text", wpm=0)


# ── mask_pii ────────────────────────────────────────────────────────────────
def test_mask_pii_hides_email_and_phone(caplog):
    caplog.set_level(logging.INFO)
    out = mask_pii("Contact anna.meier@example.ch or +41 79 123 45 67.")
    assert "anna.meier" not in out
    assert "a***@example.ch" in out
    assert "[phone]" in out
    assert "masked 1 phone" in caplog.text           # we can test logs too


def test_mask_pii_leaves_clean_text_alone():
    assert mask_pii("Nothing to hide here.") == "Nothing to hide here."


# ── summarize ───────────────────────────────────────────────────────────────
def test_summarize_takes_first_sentences():
    text = "One. Two! Three? Four."
    assert summarize(text, 2) == "One. Two!"
