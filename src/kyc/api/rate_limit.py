from __future__ import annotations

from collections import defaultdict, deque
from time import monotonic


class FixedWindowRateLimiter:
    """Small per-process guard; deploy a shared limiter for multi-instance production use."""

    def __init__(self, limit: int, window_seconds: float = 60) -> None:
        self.limit = limit
        self.window_seconds = window_seconds
        self.events: dict[str, deque[float]] = defaultdict(deque)

    def allow(self, key: str, now: float | None = None) -> bool:
        current = monotonic() if now is None else now
        bucket = self.events[key]
        while bucket and bucket[0] <= current - self.window_seconds:
            bucket.popleft()
        if len(bucket) >= self.limit:
            return False
        bucket.append(current)
        return True
