"""
In-Memory TTL Cache Wrapper.
Used exclusively for performance optimization (2-5 min TTL).
NOTE: Source of truth is always the live Monday.com GraphQL API.
No data is persisted to disk.
"""

import time
from typing import Any, Optional, Dict, Tuple

class TTLCache:
    """Simple thread-safe in-memory cache with Time-To-Live (TTL) expiration."""
    def __init__(self, ttl_seconds: int = 180):
        self.ttl_seconds = ttl_seconds
        self._store: Dict[str, Tuple[float, Any]] = {}

    def get(self, key: str) -> Optional[Any]:
        if key in self._store:
            timestamp, value = self._store[key]
            if time.time() - timestamp < self.ttl_seconds:
                return value
            del self._store[key]
        return None

    def set(self, key: str, value: Any) -> None:
        self._store[key] = (time.time(), value)

    def clear(self) -> None:
        self._store.clear()
