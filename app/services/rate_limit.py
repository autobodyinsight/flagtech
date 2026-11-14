"""In-process fixed-window rate limiter for login and other sensitive routes."""

from __future__ import annotations

import time
from collections import defaultdict


_HITS: dict[str, list[float]] = defaultdict(list)


def allow(key: str, *, limit: int = 20, window_seconds: int = 60) -> bool:
    now = time.monotonic()
    bucket = _HITS[key]
    cutoff = now - window_seconds
    while bucket and bucket[0] < cutoff:
        bucket.pop(0)
    if len(bucket) >= limit:
        return False
    bucket.append(now)
    return True
