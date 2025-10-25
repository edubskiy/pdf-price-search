"""
File-based cache for price data.

This module provides file-based caching for parsed PDF data,
allowing faster startup after initial parsing.
"""

import hashlib
import json
import logging
import os
from pathlib import Path
from typing import Any, Optional

logger = logging.getLogger(__name__)


class FileCache:
    """
    File-based cache with JSON serialization.

    This cache persists data to disk, allowing it to survive
    application restarts. Useful for caching expensive operations
    like PDF parsing.
    """

    def __init__(self, cache_dir: str = ".cache") -> None:
        """
        Initialize the file cache.

        Args:
            cache_dir: Directory to store cache files (default: .cache).
        """
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        logger.info(f"File cache initialized at: {self.cache_dir}")

    def get(self, key: str) -> Optional[Any]:
        """
        Get a value from the cache.

        Args:
            key: The cache key.

        Returns:
            The cached value if found, None otherwise.
        """
        cache_file = self._get_cache_file_path(key)

        if not cache_file.exists():
            logger.debug(f"File cache miss: {key}")
            return None

        try:
            with open(cache_file, 'r', encoding='utf-8') as f:
                data = json.load(f)

            logger.debug(f"File cache hit: {key}")
            return data

        except (json.JSONDecodeError, IOError) as e:
            logger.warning(f"Failed to read cache file {cache_file}: {e}")
            return None

    def set(self, key: str, value: Any) -> bool:
        """
        Set a value in the cache.

        Args:
            key: The cache key.
            value: The value to cache (must be JSON serializable).

        Returns:
            True if successfully cached, False otherwise.
        """
        cache_file = self._get_cache_file_path(key)

        try:
            with open(cache_file, 'w', encoding='utf-8') as f:
                json.dump(value, f, indent=2, default=str)

            logger.debug(f"File cache set: {key}")
            return True

        except (TypeError, IOError) as e:
            logger.error(f"Failed to write cache file {cache_file}: {e}")
            return False

    def exists(self, key: str) -> bool:
        """
        Check if a key exists in the cache.

        Args:
            key: The cache key to check.

        Returns:
            True if key exists, False otherwise.
        """
        cache_file = self._get_cache_file_path(key)
        return cache_file.exists()

    def delete(self, key: str) -> bool:
        """
        Delete a key from the cache.

        Args:
            key: The cache key to delete.

        Returns:
            True if key was deleted, False if it didn't exist.
        """
        cache_file = self._get_cache_file_path(key)

        if cache_file.exists():
            try:
                cache_file.unlink()
                logger.debug(f"File cache deleted: {key}")
                return True
            except OSError as e:
                logger.error(f"Failed to delete cache file {cache_file}: {e}")
                return False

        return False

    def clear(self) -> int:
        """
        Clear all cache files.

        Returns:
            Number of files deleted.
        """
        count = 0

        try:
            for cache_file in self.cache_dir.glob("*.json"):
                try:
                    cache_file.unlink()
                    count += 1
                except OSError as e:
                    logger.error(f"Failed to delete {cache_file}: {e}")

            logger.info(f"File cache cleared: {count} files removed")

        except Exception as e:
            logger.error(f"Failed to clear cache: {e}")

        return count

    def get_cache_size(self) -> int:
        """
        Get the total size of all cache files in bytes.

        Returns:
            Total size in bytes.
        """
        total_size = 0

        try:
            for cache_file in self.cache_dir.glob("*.json"):
                total_size += cache_file.stat().st_size
        except Exception as e:
            logger.error(f"Failed to calculate cache size: {e}")

        return total_size

    def get_cache_count(self) -> int:
        """
        Get the number of cache files.

        Returns:
            Number of cache files.
        """
        try:
            return len(list(self.cache_dir.glob("*.json")))
        except Exception as e:
            logger.error(f"Failed to count cache files: {e}")
            return 0

    def get_stats(self) -> dict[str, Any]:
        """
        Get cache statistics.

        Returns:
            Dict with cache statistics.
        """
        return {
            "cache_dir": str(self.cache_dir),
            "file_count": self.get_cache_count(),
            "total_size_bytes": self.get_cache_size(),
            "total_size_mb": round(self.get_cache_size() / (1024 * 1024), 2),
        }

    def _get_cache_file_path(self, key: str) -> Path:
        """
        Get the file path for a cache key.

        Args:
            key: The cache key.

        Returns:
            Path to the cache file.
        """
        # Hash the key to create a safe filename
        key_hash = hashlib.sha256(key.encode()).hexdigest()
        return self.cache_dir / f"{key_hash}.json"

    def get_key_for_file(self, file_path: str) -> str:
        """
        Generate a cache key for a file based on path and modification time.

        Args:
            file_path: Path to the file.

        Returns:
            Cache key string.
        """
        path = Path(file_path)

        if not path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")

        # Include file path and modification time in key
        mtime = os.path.getmtime(file_path)
        key = f"{file_path}:{mtime}"

        return key

    def is_file_cached(self, file_path: str) -> bool:
        """
        Check if a file's parsed data is cached and still valid.

        Args:
            file_path: Path to the file.

        Returns:
            True if cached and valid, False otherwise.
        """
        try:
            key = self.get_key_for_file(file_path)
            return self.exists(key)
        except FileNotFoundError:
            return False
