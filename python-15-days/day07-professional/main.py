"""Day 07 — Using the textkit package like a real app would (with logging configured)."""
import logging
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / "src"))    # not needed after `pip install -e .`

from textkit import mask_pii, reading_time, slugify, summarize  # noqa: E402

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)-5s %(name)s: %(message)s")
log = logging.getLogger("publisher")

ARTICLE = {
    "title": "Zürich's Best Café Guide — 2026 Edition!",
    "body": (
        "Zürich has a coffee scene that rivals Vienna. We visited 40 cafés in two weeks. "
        "Our favourite roaster is near the lake. Questions? Write to lena.huber@example.ch "
        "or call +41 44 555 12 34. " + "More tasting notes follow. " * 120
    ),
}

if __name__ == "__main__":
    log.info("publishing article")
    print("slug          :", slugify(ARTICLE["title"]))
    print("reading time  :", reading_time(ARTICLE["body"]), "min")
    print("summary       :", summarize(ARTICLE["body"]))
    print("safe preview  :", mask_pii(ARTICLE["body"][:220]))
    log.info("done")
