"""
Integration tests for cache implementations.

These tests verify the cache functionality with realistic data.
"""

import pytest
import time
import tempfile
from pathlib import Path

from src.infrastructure.cache import PriceCache, FileCache


class TestPriceCache:
    """Integration tests for in-memory PriceCache."""

    @pytest.fixture
    def cache(self):
        """Create a fresh cache instance."""
        return PriceCache(default_ttl=3600)

    def test_basic_cache_operations(self, cache):
        """Test basic get/set operations."""
        # Set a value
        cache.set("key1", "value1")

        # Get the value
        value = cache.get("key1")
        assert value == "value1"

        # Get nonexistent key
        assert cache.get("nonexistent") is None

    def test_cache_with_complex_data(self, cache):
        """Test caching complex data structures."""
        data = {
            "services": ["FedEx 2Day", "FedEx Express Saver"],
            "zones": [2, 3, 4],
            "prices": {"2": {"10": 25.23}},
        }

        cache.set("complex_data", data)

        retrieved = cache.get("complex_data")
        assert retrieved == data
        assert retrieved["services"] == ["FedEx 2Day", "FedEx Express Saver"]

    def test_cache_exists(self, cache):
        """Test checking if keys exist."""
        cache.set("test_key", "test_value")

        assert cache.exists("test_key")
        assert not cache.exists("nonexistent")

    def test_cache_delete(self, cache):
        """Test deleting cache entries."""
        cache.set("key1", "value1")
        assert cache.exists("key1")

        # Delete the key
        result = cache.delete("key1")
        assert result is True
        assert not cache.exists("key1")

        # Delete nonexistent key
        result = cache.delete("nonexistent")
        assert result is False

    def test_cache_clear(self, cache):
        """Test clearing all cache entries."""
        cache.set("key1", "value1")
        cache.set("key2", "value2")
        cache.set("key3", "value3")

        assert cache.size() == 3

        cache.clear()

        assert cache.size() == 0
        assert cache.get("key1") is None

    def test_cache_ttl_expiration(self, cache):
        """Test that entries expire after TTL."""
        # Set with short TTL
        cache.set("short_lived", "value", ttl=1)

        # Should exist immediately
        assert cache.exists("short_lived")

        # Wait for expiration
        time.sleep(1.1)

        # Should be expired
        assert not cache.exists("short_lived")
        assert cache.get("short_lived") is None

    def test_cache_clear_expired(self, cache):
        """Test clearing expired entries."""
        # Set entries with different TTLs
        cache.set("long_lived", "value1", ttl=10)
        cache.set("short_lived", "value2", ttl=1)

        assert cache.size() == 2

        # Wait for short TTL to expire
        time.sleep(1.1)

        # Clear expired
        removed = cache.clear_expired()
        assert removed == 1

        # Long-lived should still exist
        assert cache.exists("long_lived")
        assert not cache.exists("short_lived")

    def test_cache_stats(self, cache):
        """Test getting cache statistics."""
        cache.set("key1", "value1")
        cache.set("key2", "value2", ttl=1)

        stats = cache.get_stats()

        assert stats["total_entries"] == 2
        assert stats["default_ttl"] == 3600

        # Wait for one to expire
        time.sleep(1.1)

        stats = cache.get_stats()
        assert stats["expired_entries"] == 1
        assert stats["active_entries"] == 1

    def test_cache_get_keys(self, cache):
        """Test getting cache keys."""
        cache.set("key1", "value1")
        cache.set("key2", "value2")
        cache.set("key3", "value3")

        keys = cache.get_keys()
        assert len(keys) == 3
        assert "key1" in keys
        assert "key2" in keys
        assert "key3" in keys

    def test_set_default_ttl(self, cache):
        """Test setting default TTL."""
        cache.set_default_ttl(7200)

        stats = cache.get_stats()
        assert stats["default_ttl"] == 7200

        # Invalid TTL should raise error
        with pytest.raises(ValueError):
            cache.set_default_ttl(-1)


class TestFileCache:
    """Integration tests for file-based FileCache."""

    @pytest.fixture
    def cache_dir(self):
        """Create a temporary cache directory."""
        temp_dir = tempfile.mkdtemp()
        yield temp_dir
        # Cleanup after test
        import shutil
        shutil.rmtree(temp_dir, ignore_errors=True)

    @pytest.fixture
    def cache(self, cache_dir):
        """Create a FileCache instance."""
        return FileCache(cache_dir=cache_dir)

    def test_basic_file_cache_operations(self, cache):
        """Test basic file cache operations."""
        # Set a value
        cache.set("key1", {"data": "value1"})

        # Get the value
        value = cache.get("key1")
        assert value == {"data": "value1"}

        # Get nonexistent key
        assert cache.get("nonexistent") is None

    def test_cache_persistence(self, cache_dir):
        """Test that cache persists across instances."""
        # Create first cache instance
        cache1 = FileCache(cache_dir=cache_dir)
        cache1.set("persistent_key", {"data": "persistent_value"})

        # Create second cache instance
        cache2 = FileCache(cache_dir=cache_dir)

        # Should be able to retrieve from second instance
        value = cache2.get("persistent_key")
        assert value == {"data": "persistent_value"}

    def test_cache_complex_data(self, cache):
        """Test caching complex data structures."""
        data = {
            "services": ["FedEx 2Day", "FedEx Express Saver"],
            "zones": [2, 3, 4, 5, 6, 7, 8],
            "prices": {
                "2": {"1": 25.23, "2": 26.26, "3": 26.68},
                "3": {"1": 26.30, "2": 27.59, "3": 28.48},
            },
        }

        cache.set("complex_data", data)
        retrieved = cache.get("complex_data")

        assert retrieved == data
        assert retrieved["services"] == data["services"]
        assert retrieved["zones"] == data["zones"]

    def test_cache_exists(self, cache):
        """Test checking if keys exist in file cache."""
        cache.set("test_key", "test_value")

        assert cache.exists("test_key")
        assert not cache.exists("nonexistent")

    def test_cache_delete(self, cache):
        """Test deleting cache files."""
        cache.set("key1", "value1")
        assert cache.exists("key1")

        # Delete the key
        result = cache.delete("key1")
        assert result is True
        assert not cache.exists("key1")

        # Delete nonexistent key
        result = cache.delete("nonexistent")
        assert result is False

    def test_cache_clear(self, cache):
        """Test clearing all cache files."""
        cache.set("key1", "value1")
        cache.set("key2", "value2")
        cache.set("key3", "value3")

        assert cache.get_cache_count() == 3

        # Clear cache
        removed = cache.clear()
        assert removed == 3

        assert cache.get_cache_count() == 0

    def test_cache_stats(self, cache):
        """Test getting cache statistics."""
        cache.set("key1", "value1")
        cache.set("key2", "value2")

        stats = cache.get_stats()

        assert stats["file_count"] == 2
        assert stats["total_size_bytes"] > 0
        assert stats["total_size_mb"] >= 0
        assert "cache_dir" in stats

    def test_get_key_for_file(self, cache, tmp_path):
        """Test generating cache keys for files."""
        # Create a test file
        test_file = tmp_path / "test.txt"
        test_file.write_text("test content")

        # Get cache key
        key1 = cache.get_key_for_file(str(test_file))
        assert key1

        # Modify file
        time.sleep(0.1)
        test_file.write_text("modified content")

        # Key should be different
        key2 = cache.get_key_for_file(str(test_file))
        assert key2 != key1

    def test_is_file_cached(self, cache, tmp_path):
        """Test checking if a file's data is cached."""
        # Create a test file
        test_file = tmp_path / "test.txt"
        test_file.write_text("test content")

        # Not cached initially
        assert not cache.is_file_cached(str(test_file))

        # Cache the file's data
        key = cache.get_key_for_file(str(test_file))
        cache.set(key, {"data": "parsed"})

        # Now should be cached
        assert cache.is_file_cached(str(test_file))

    def test_cache_size_calculation(self, cache):
        """Test calculating cache size."""
        # Start with empty cache
        assert cache.get_cache_size() == 0

        # Add some data
        cache.set("small", {"data": "x"})
        size1 = cache.get_cache_size()
        assert size1 > 0

        # Add more data
        cache.set("large", {"data": "x" * 1000})
        size2 = cache.get_cache_size()
        assert size2 > size1

    def test_nonexistent_file_raises_error(self, cache):
        """Test that getting key for nonexistent file raises error."""
        with pytest.raises(FileNotFoundError):
            cache.get_key_for_file("/nonexistent/file.txt")
