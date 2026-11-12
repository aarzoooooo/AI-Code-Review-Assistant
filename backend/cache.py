"""Thread-safe in-memory TTL cache for reviews.

Trade-off: per-process and lost on restart. Fine for a single instance; with
several instances you would move this to Redis (see README, "Scaling").
"""
import hashlib
import threading

from cachetools import TTLCache

import config
from schemas import ReviewResult

_cache: TTLCache = TTLCache(maxsize=config.CACHE_MAX_ENTRIES, ttl=config.CACHE_TTL_SECONDS)
_lock = threading.Lock()


def make_key(language: str, code: str) -> str:
    # Trailing whitespace shouldn't cause a cache miss.
    normalized = code.strip()
    return hashlib.sha256(f"{language}\n{normalized}".encode("utf-8")).hexdigest()


def get(key: str) -> ReviewResult | None:
    with _lock:
        return _cache.get(key)


def set(key: str, value: ReviewResult) -> None:  # noqa: A001 - mirrors dict-style API
    with _lock:
        _cache[key] = value


def clear() -> None:
    with _lock:
        _cache.clear()
