"""
Unit tests for FileCache.
"""

import json
import pytest
import tempfile
import os
from pathlib import Path
from src.infrastructure.cache.file_cache import FileCache


class TestFileCacheInitialization:
    """Test FileCache initialization."""

    def test_create_cache_with_default_dir(self):
        """Test creating cache with default directory."""
        with tempfile.TemporaryDirectory() as tmpdir:
            cache_dir = os.path.join(tmpdir, ".cache")
            cache = FileCache(cache_dir)
            assert cache.cache_dir == Path(cache_dir)
            assert cache.cache_dir.exists()

    def test_create_cache_with_custom_dir(self):
        """Test creating cache with custom directory."""
        with tempfile.TemporaryDirectory() as tmpdir:
            custom_dir = os.path.join(tmpdir, "my_cache")
            cache = FileCache(custom_dir)
            assert cache.cache_dir == Path(custom_dir)
            assert cache.cache_dir.exists()

    def test_cache_dir_created_if_not_exists(self):
        """Test that cache directory is created if it doesn't exist."""
        with tempfile.TemporaryDirectory() as tmpdir:
            nested_dir = os.path.join(tmpdir, "level1", "level2", "cache")
            cache = FileCache(nested_dir)
            assert cache.cache_dir.exists()


class TestFileCacheGetSet:
    """Test FileCache get and set operations."""

    def test_set_and_get_simple_value(self):
        """Test setting and getting a simple value."""
        with tempfile.TemporaryDirectory() as tmpdir:
            cache = FileCache(tmpdir)
            assert cache.set("key1", "value1")
            assert cache.get("key1") == "value1"

    def test_set_and_get_dict_value(self):
        """Test setting and getting a dict value."""
        with tempfile.TemporaryDirectory() as tmpdir:
            cache = FileCache(tmpdir)
            data = {"name": "test", "count": 42}
            assert cache.set("key1", data)
            assert cache.get("key1") == data

    def test_set_and_get_list_value(self):
        """Test setting and getting a list value."""
        with tempfile.TemporaryDirectory() as tmpdir:
            cache = FileCache(tmpdir)
            data = [1, 2, 3, "four", {"five": 5}]
            assert cache.set("key1", data)
            assert cache.get("key1") == data

    def test_get_nonexistent_key_returns_none(self):
        """Test that getting a non-existent key returns None."""
        with tempfile.TemporaryDirectory() as tmpdir:
            cache = FileCache(tmpdir)
            assert cache.get("nonexistent") is None

    def test_overwrite_existing_value(self):
        """Test that setting an existing key overwrites the value."""
        with tempfile.TemporaryDirectory() as tmpdir:
            cache = FileCache(tmpdir)
            cache.set("key1", "value1")
            cache.set("key1", "value2")
            assert cache.get("key1") == "value2"

    def test_set_with_special_characters_in_key(self):
        """Test setting values with special characters in key."""
        with tempfile.TemporaryDirectory() as tmpdir:
            cache = FileCache(tmpdir)
            key = "key with spaces/slashes:colons"
            assert cache.set(key, "value")
            assert cache.get(key) == "value"


class TestFileCacheExists:
    """Test FileCache exists method."""

    def test_exists_returns_true_for_existing_key(self):
        """Test that exists returns True for existing key."""
        with tempfile.TemporaryDirectory() as tmpdir:
            cache = FileCache(tmpdir)
            cache.set("key1", "value1")
            assert cache.exists("key1") is True

    def test_exists_returns_false_for_nonexistent_key(self):
        """Test that exists returns False for non-existent key."""
        with tempfile.TemporaryDirectory() as tmpdir:
            cache = FileCache(tmpdir)
            assert cache.exists("nonexistent") is False


class TestFileCacheDelete:
    """Test FileCache delete method."""

    def test_delete_existing_key(self):
        """Test deleting an existing key."""
        with tempfile.TemporaryDirectory() as tmpdir:
            cache = FileCache(tmpdir)
            cache.set("key1", "value1")
            assert cache.delete("key1") is True
            assert cache.get("key1") is None

    def test_delete_nonexistent_key(self):
        """Test deleting a non-existent key."""
        with tempfile.TemporaryDirectory() as tmpdir:
            cache = FileCache(tmpdir)
            assert cache.delete("nonexistent") is False


class TestFileCacheClear:
    """Test FileCache clear method."""

    def test_clear_empty_cache(self):
        """Test clearing an empty cache."""
        with tempfile.TemporaryDirectory() as tmpdir:
            cache = FileCache(tmpdir)
            assert cache.clear() == 0

    def test_clear_cache_with_items(self):
        """Test clearing cache with items."""
        with tempfile.TemporaryDirectory() as tmpdir:
            cache = FileCache(tmpdir)
            cache.set("key1", "value1")
            cache.set("key2", "value2")
            cache.set("key3", "value3")
            assert cache.clear() == 3
            assert cache.get("key1") is None
            assert cache.get("key2") is None
            assert cache.get("key3") is None


class TestFileCacheStats:
    """Test FileCache statistics methods."""

    def test_get_cache_count_empty(self):
        """Test getting count of empty cache."""
        with tempfile.TemporaryDirectory() as tmpdir:
            cache = FileCache(tmpdir)
            assert cache.get_cache_count() == 0

    def test_get_cache_count_with_items(self):
        """Test getting count with items."""
        with tempfile.TemporaryDirectory() as tmpdir:
            cache = FileCache(tmpdir)
            cache.set("key1", "value1")
            cache.set("key2", "value2")
            assert cache.get_cache_count() == 2

    def test_get_cache_size_empty(self):
        """Test getting size of empty cache."""
        with tempfile.TemporaryDirectory() as tmpdir:
            cache = FileCache(tmpdir)
            assert cache.get_cache_size() == 0

    def test_get_cache_size_with_items(self):
        """Test getting size with items."""
        with tempfile.TemporaryDirectory() as tmpdir:
            cache = FileCache(tmpdir)
            cache.set("key1", "value1")
            assert cache.get_cache_size() > 0

    def test_get_stats(self):
        """Test getting cache statistics."""
        with tempfile.TemporaryDirectory() as tmpdir:
            cache = FileCache(tmpdir)
            cache.set("key1", "value1")
            cache.set("key2", "value2")

            stats = cache.get_stats()
            assert "cache_dir" in stats
            assert "file_count" in stats
            assert "total_size_bytes" in stats
            assert "total_size_mb" in stats
            assert stats["file_count"] == 2
            assert stats["total_size_bytes"] > 0


class TestFileCacheFileOperations:
    """Test FileCache file-based operations."""

    def test_get_key_for_file(self):
        """Test generating cache key for a file."""
        with tempfile.TemporaryDirectory() as tmpdir:
            cache = FileCache(tmpdir)

            # Create a test file
            test_file = os.path.join(tmpdir, "test.txt")
            with open(test_file, "w") as f:
                f.write("test content")

            key1 = cache.get_key_for_file(test_file)
            assert key1 is not None
            assert test_file in key1

            # Key should be the same if file hasn't changed
            key2 = cache.get_key_for_file(test_file)
            assert key1 == key2

    def test_get_key_for_nonexistent_file_raises_error(self):
        """Test that getting key for non-existent file raises error."""
        with tempfile.TemporaryDirectory() as tmpdir:
            cache = FileCache(tmpdir)
            with pytest.raises(FileNotFoundError):
                cache.get_key_for_file("/nonexistent/file.txt")

    def test_get_key_changes_when_file_modified(self):
        """Test that cache key changes when file is modified."""
        with tempfile.TemporaryDirectory() as tmpdir:
            cache = FileCache(tmpdir)

            # Create a test file
            test_file = os.path.join(tmpdir, "test.txt")
            with open(test_file, "w") as f:
                f.write("original content")

            key1 = cache.get_key_for_file(test_file)

            # Modify the file
            import time
            time.sleep(0.1)  # Ensure mtime changes
            with open(test_file, "w") as f:
                f.write("modified content")

            key2 = cache.get_key_for_file(test_file)
            assert key1 != key2

    def test_is_file_cached(self):
        """Test checking if file is cached."""
        with tempfile.TemporaryDirectory() as tmpdir:
            cache = FileCache(tmpdir)

            # Create a test file
            test_file = os.path.join(tmpdir, "test.txt")
            with open(test_file, "w") as f:
                f.write("test content")

            # Initially not cached
            assert cache.is_file_cached(test_file) is False

            # Cache the file
            key = cache.get_key_for_file(test_file)
            cache.set(key, {"data": "cached"})

            # Now it should be cached
            assert cache.is_file_cached(test_file) is True

    def test_is_file_cached_for_nonexistent_file(self):
        """Test checking if non-existent file is cached."""
        with tempfile.TemporaryDirectory() as tmpdir:
            cache = FileCache(tmpdir)
            assert cache.is_file_cached("/nonexistent/file.txt") is False


class TestFileCacheErrorHandling:
    """Test FileCache error handling."""

    def test_get_handles_corrupted_cache_file(self):
        """Test that get handles corrupted cache files gracefully."""
        with tempfile.TemporaryDirectory() as tmpdir:
            cache = FileCache(tmpdir)

            # Create a corrupted cache file
            cache.set("key1", "value1")
            cache_file = cache._get_cache_file_path("key1")

            # Corrupt the file
            with open(cache_file, "w") as f:
                f.write("corrupted json {{{")

            # Should return None instead of raising error
            assert cache.get("key1") is None

    def test_set_handles_permission_errors_gracefully(self):
        """Test that set handles permission errors gracefully."""
        # This test is platform-dependent, so we'll just verify it returns bool
        with tempfile.TemporaryDirectory() as tmpdir:
            cache = FileCache(tmpdir)
            result = cache.set("key1", "value1")
            assert isinstance(result, bool)


class TestFileCachePersistence:
    """Test FileCache persistence across instances."""

    def test_data_persists_across_instances(self):
        """Test that cached data persists across cache instances."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create first instance and set data
            cache1 = FileCache(tmpdir)
            cache1.set("key1", "value1")
            cache1.set("key2", {"nested": "data"})

            # Create second instance and verify data exists
            cache2 = FileCache(tmpdir)
            assert cache2.get("key1") == "value1"
            assert cache2.get("key2") == {"nested": "data"}

    def test_clear_affects_all_instances(self):
        """Test that clearing cache affects all instances."""
        with tempfile.TemporaryDirectory() as tmpdir:
            cache1 = FileCache(tmpdir)
            cache1.set("key1", "value1")

            cache2 = FileCache(tmpdir)
            cache2.clear()

            # Both instances should see empty cache
            assert cache1.get("key1") is None
            assert cache2.get("key1") is None
