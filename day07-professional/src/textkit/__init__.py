"""textkit — small, tested text utilities for a publishing platform."""
from .core import mask_pii, reading_time, slugify, summarize

__all__ = ["slugify", "reading_time", "mask_pii", "summarize"]
__version__ = "0.1.0"
