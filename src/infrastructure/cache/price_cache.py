"""
In-memory cache for price data.

This module provides a simple in-memory cache with TTL (time-to-live)
support for caching parsed PDF data and shipping services.
"""

import logging
import time
from dataclasses import dataclass
from typing import Any, Dict, Optional

logger = logging.getLogger(__name__)


@dataclass
class CacheEntry:
    """
    Cache entry with value and expiration time.

    Attributes:
        value: The cached value.
        expires_at: Unix timestamp when this entry expires.
    """

    value: Any
    expires_at: float


class PriceCache:
    """
    In-memory cache with TTL support.

    This cache stores key-value pairs with optional expiration times.
    Expired entries are removed on access or explicitly cleared.
    """

    def __init__(self, default_ttl: int = 3600) -> None:
        """
        Initialize the cache.

        Args:
            default_ttl: Default time-to-live in seconds (default: 1 hour).
        """
        self.default_ttl = default_ttl
        self._cache: Dict[str, CacheEntry] = {}

    def get(self, key: str) -> Optional[Any]:
        """
        Get a value from the cache.

        Args:
            key: The cache key.

        Returns:
            The cached value if found and not expired, None otherwise.
        """
        if key not in self._cache:
            logger.debug(f"Cache miss: {key}")
            return None

        entry = self._cache[key]

        # Check if expired
        if self._is_expired(entry):
            logger.debug(f"Cache expired: {key}")
            del self._cache[key]
            return None

        logger.debug(f"Cache hit: {key}")
        return entry.value

    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> None:
        """
        Set a value in the cache.

        Args:
            key: The cache key.
            value: The value to cache.
            ttl: Optional time-to-live in seconds (uses default if None).
        """
        if ttl is None:
            ttl = self.default_ttl

        expires_at = time.time() + ttl

        entry = CacheEntry(value=value, expires_at=expires_at)
        self._cache[key] = entry

        logger.debug(f"Cache set: {key} (ttl={ttl}s)")

    def exists(self, key: str) -> bool:
        """
        Check if a key exists in the cache and is not expired.

        Args:
            key: The cache key to check.

        Returns:
            True if key exists and is not expired, False otherwise.
        """
        if key not in self._cache:
            return False

        entry = self._cache[key]

        if self._is_expired(entry):
            del self._cache[key]
            return False

        return True

    def delete(self, key: str) -> bool:
        """
        Delete a key from the cache.

        Args:
            key: The cache key to delete.

        Returns:
            True if key was deleted, False if it didn't exist.
        """
        if key in self._cache:
            del self._cache[key]
            logger.debug(f"Cache deleted: {key}")
            return True

        return False

    def clear(self) -> None:
        """Clear all entries from the cache."""
        count = len(self._cache)
        self._cache.clear()
        logger.info(f"Cache cleared: {count} entries removed")

    def clear_expired(self) -> int:
        """
        Remove all expired entries from the cache.

        Returns:
            Number of entries removed.
        """
        expired_keys = [
            key for key, entry in self._cache.items() if self._is_expired(entry)
        ]

        for key in expired_keys:
            del self._cache[key]

        if expired_keys:
            logger.info(f"Cleared {len(expired_keys)} expired cache entries")

        return len(expired_keys)

    def size(self) -> int:
        """
        Get the number of entries in the cache.

        Returns:
            Number of cache entries (including expired).
        """
        return len(self._cache)

    def get_stats(self) -> Dict[str, Any]:
        """
        Get cache statistics.

        Returns:
            Dict with cache statistics.
        """
        total = len(self._cache)
        expired = sum(
            1 for entry in self._cache.values() if self._is_expired(entry)
        )
        active = total - expired

        return {
            "total_entries": total,
            "active_entries": active,
            "expired_entries": expired,
            "default_ttl": self.default_ttl,
        }

    def _is_expired(self, entry: CacheEntry) -> bool:
        """
        Check if a cache entry is expired.

        Args:
            entry: The cache entry to check.

        Returns:
            True if expired, False otherwise.
        """
        return time.time() >= entry.expires_at

    def set_default_ttl(self, ttl: int) -> None:
        """
        Set the default TTL for new cache entries.

        Args:
            ttl: Time-to-live in seconds.
        """
        if ttl <= 0:
            raise ValueError("TTL must be positive")

        self.default_ttl = ttl
        logger.info(f"Default TTL updated to {ttl}s")

    def get_keys(self) -> list[str]:
        """
        Get all cache keys (including expired).

        Returns:
            List of all cache keys.
        """
        return list(self._cache.keys())

    def get_active_keys(self) -> list[str]:
        """
        Get all non-expired cache keys.

        Returns:
            List of active cache keys.
        """
        return [
            key
            for key, entry in self._cache.items()
            if not self._is_expired(entry)
        ]
