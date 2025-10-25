"""
Performance tests for PDF Price Search system.

These tests measure performance metrics such as:
- Search speed
- Concurrent request handling
- Memory usage
- PDF loading time
"""

import pytest
import time
import psutil
import os
from concurrent.futures import ThreadPoolExecutor, as_completed
from decimal import Decimal
from pathlib import Path

from src.application.container import Container
from src.application.use_cases.search_price_use_case import SearchPriceUseCase
from src.application.use_cases.load_data_use_case import LoadDataUseCase
from src.application.dto.search_request import SearchRequest
from src.domain.value_objects.price_query import PriceQuery


class TestSearchPerformance:
    """Test search performance metrics."""

    @pytest.fixture(scope="class")
    def loaded_container(self):
        """Create and load a container for performance testing."""
        container = Container()

        # Load PDFs if they exist
        source_dir = Path(__file__).parent.parent.parent / "source"
        if source_dir.exists():
            load_use_case = LoadDataUseCase(container)
            try:
                load_use_case.execute(str(source_dir))
            except Exception as e:
                pytest.skip(f"Could not load test PDFs: {e}")

        return container

    def test_single_search_speed(self, loaded_container):
        """Test the speed of a single search operation."""
        search_use_case = SearchPriceUseCase(loaded_container)

        request = SearchRequest(query="2lb to zone 5")

        # Warm-up run
        search_use_case.execute(request)

        # Timed run
        start_time = time.time()
        result = search_use_case.execute(request)
        end_time = time.time()

        duration_ms = (end_time - start_time) * 1000

        print(f"\nSingle search completed in: {duration_ms:.2f} ms")

        # Assert reasonable performance (should be under 100ms for cached search)
        assert duration_ms < 100, f"Search took {duration_ms:.2f} ms, expected < 100 ms"

    def test_multiple_sequential_searches(self, loaded_container):
        """Test performance of multiple sequential searches."""
        search_use_case = SearchPriceUseCase(loaded_container)

        queries = [
            "2lb to zone 5",
            "5lb to zone 8",
            "10lb to zone 2",
            "1lb to zone 1",
            "15lb to zone 7",
        ]

        search_times = []

        for query in queries:
            request = SearchRequest(query=query)

            start_time = time.time()
            result = search_use_case.execute(request)
            end_time = time.time()

            duration_ms = (end_time - start_time) * 1000
            search_times.append(duration_ms)

        avg_time = sum(search_times) / len(search_times)
        max_time = max(search_times)
        min_time = min(search_times)

        print(f"\nSequential searches:")
        print(f"  Average: {avg_time:.2f} ms")
        print(f"  Min: {min_time:.2f} ms")
        print(f"  Max: {max_time:.2f} ms")

        # Assert reasonable average performance
        assert avg_time < 100, f"Average search time {avg_time:.2f} ms, expected < 100 ms"

    def test_cache_performance_improvement(self, loaded_container):
        """Test that caching improves performance."""
        search_use_case = SearchPriceUseCase(loaded_container)

        request = SearchRequest(query="5lb to zone 5")

        # First search (may require parsing)
        start_time = time.time()
        result1 = search_use_case.execute(request)
        first_search_time = (time.time() - start_time) * 1000

        # Second search (should be cached)
        start_time = time.time()
        result2 = search_use_case.execute(request)
        cached_search_time = (time.time() - start_time) * 1000

        print(f"\nCache performance:")
        print(f"  First search: {first_search_time:.2f} ms")
        print(f"  Cached search: {cached_search_time:.2f} ms")
        print(f"  Improvement: {(1 - cached_search_time/first_search_time) * 100:.1f}%")

        # Cached search should be equal or faster
        assert cached_search_time <= first_search_time * 1.1  # Allow 10% variance


class TestConcurrentPerformance:
    """Test concurrent request handling."""

    @pytest.fixture(scope="class")
    def loaded_container(self):
        """Create and load a container for performance testing."""
        container = Container()

        source_dir = Path(__file__).parent.parent.parent / "source"
        if source_dir.exists():
            load_use_case = LoadDataUseCase(container)
            try:
                load_use_case.execute(str(source_dir))
            except Exception:
                pytest.skip("Could not load test PDFs")

        return container

    def test_concurrent_searches(self, loaded_container):
        """Test handling multiple concurrent search requests."""
        search_use_case = SearchPriceUseCase(loaded_container)

        queries = [
            "2lb to zone 5",
            "5lb to zone 8",
            "10lb to zone 2",
            "1lb to zone 1",
            "15lb to zone 7",
        ] * 4  # 20 total queries

        def perform_search(query):
            """Perform a single search and return timing."""
            start = time.time()
            request = SearchRequest(query=query)
            result = search_use_case.execute(request)
            duration = (time.time() - start) * 1000
            return duration, result

        # Execute searches concurrently
        start_time = time.time()

        with ThreadPoolExecutor(max_workers=10) as executor:
            futures = [executor.submit(perform_search, q) for q in queries]
            results = [f.result() for f in as_completed(futures)]

        total_time = (time.time() - start_time) * 1000

        durations = [r[0] for r in results]
        avg_duration = sum(durations) / len(durations)
        max_duration = max(durations)

        print(f"\nConcurrent searches (20 requests, 10 workers):")
        print(f"  Total time: {total_time:.2f} ms")
        print(f"  Average per request: {avg_duration:.2f} ms")
        print(f"  Max per request: {max_duration:.2f} ms")
        print(f"  Requests per second: {len(queries) / (total_time / 1000):.2f}")

        # Assert all searches completed successfully
        assert len(results) == len(queries)

        # Assert reasonable throughput
        requests_per_second = len(queries) / (total_time / 1000)
        assert requests_per_second > 10, f"Only {requests_per_second:.2f} req/s, expected > 10"


class TestMemoryUsage:
    """Test memory usage during operations."""

    def get_memory_usage_mb(self):
        """Get current process memory usage in MB."""
        process = psutil.Process(os.getpid())
        return process.memory_info().rss / (1024 * 1024)

    def test_memory_usage_during_pdf_loading(self):
        """Test memory usage when loading PDFs."""
        initial_memory = self.get_memory_usage_mb()

        container = Container()
        source_dir = Path(__file__).parent.parent.parent / "source"

        if not source_dir.exists():
            pytest.skip("Source directory not found")

        load_use_case = LoadDataUseCase(container)

        try:
            load_use_case.execute(str(source_dir))
        except Exception as e:
            pytest.skip(f"Could not load PDFs: {e}")

        after_loading_memory = self.get_memory_usage_mb()

        memory_increase = after_loading_memory - initial_memory

        print(f"\nMemory usage during PDF loading:")
        print(f"  Initial: {initial_memory:.2f} MB")
        print(f"  After loading: {after_loading_memory:.2f} MB")
        print(f"  Increase: {memory_increase:.2f} MB")

        # Assert memory usage is reasonable (should be under 100MB for typical PDFs)
        assert memory_increase < 100, f"Memory increased by {memory_increase:.2f} MB, expected < 100 MB"

    def test_memory_usage_during_searches(self):
        """Test memory usage during repeated searches."""
        container = Container()
        source_dir = Path(__file__).parent.parent.parent / "source"

        if source_dir.exists():
            load_use_case = LoadDataUseCase(container)
            try:
                load_use_case.execute(str(source_dir))
            except Exception:
                pytest.skip("Could not load PDFs")

        initial_memory = self.get_memory_usage_mb()

        search_use_case = SearchPriceUseCase(container)

        # Perform many searches
        for i in range(100):
            query = f"{i % 20 + 1}lb to zone {i % 8 + 1}"
            request = SearchRequest(query=query)
            search_use_case.execute(request)

        after_searches_memory = self.get_memory_usage_mb()

        memory_increase = after_searches_memory - initial_memory

        print(f"\nMemory usage during 100 searches:")
        print(f"  Initial: {initial_memory:.2f} MB")
        print(f"  After searches: {after_searches_memory:.2f} MB")
        print(f"  Increase: {memory_increase:.2f} MB")

        # Memory should not grow significantly during searches
        assert memory_increase < 50, f"Memory increased by {memory_increase:.2f} MB during searches"


class TestPDFLoadingPerformance:
    """Test PDF loading performance."""

    def test_pdf_loading_time(self):
        """Test time required to load PDFs."""
        container = Container()
        source_dir = Path(__file__).parent.parent.parent / "source"

        if not source_dir.exists():
            pytest.skip("Source directory not found")

        pdf_files = list(source_dir.glob("*.pdf"))
        if not pdf_files:
            pytest.skip("No PDF files found")

        load_use_case = LoadDataUseCase(container)

        start_time = time.time()
        result = load_use_case.execute(str(source_dir))
        loading_time = (time.time() - start_time) * 1000

        print(f"\nPDF loading performance:")
        print(f"  Files loaded: {len(result.loaded_files)}")
        print(f"  Total time: {loading_time:.2f} ms")
        print(f"  Average per file: {loading_time / len(result.loaded_files):.2f} ms")

        # Assert reasonable loading time (under 5 seconds per PDF on average)
        avg_time_per_file = loading_time / len(result.loaded_files)
        assert avg_time_per_file < 5000, f"Average loading time {avg_time_per_file:.2f} ms, expected < 5000 ms"

    def test_cached_pdf_loading_time(self):
        """Test time required to load cached PDFs."""
        container = Container()
        source_dir = Path(__file__).parent.parent.parent / "source"

        if not source_dir.exists():
            pytest.skip("Source directory not found")

        load_use_case = LoadDataUseCase(container)

        # First load (may create cache)
        start_time = time.time()
        result1 = load_use_case.execute(str(source_dir))
        first_load_time = (time.time() - start_time) * 1000

        # Create a new container for second load
        container2 = Container()
        load_use_case2 = LoadDataUseCase(container2)

        # Second load (should use cache)
        start_time = time.time()
        result2 = load_use_case2.execute(str(source_dir))
        cached_load_time = (time.time() - start_time) * 1000

        print(f"\nCached PDF loading:")
        print(f"  First load: {first_load_time:.2f} ms")
        print(f"  Cached load: {cached_load_time:.2f} ms")
        print(f"  Improvement: {(1 - cached_load_time/first_load_time) * 100:.1f}%")

        # Cached loading should be significantly faster
        assert cached_load_time < first_load_time * 0.8  # At least 20% faster


class TestScalability:
    """Test system scalability."""

    def test_search_performance_with_varying_data_size(self):
        """Test how search performance scales with data size."""
        # This test would require multiple PDFs of different sizes
        # For now, we'll just verify search works consistently
        container = Container()
        source_dir = Path(__file__).parent.parent.parent / "source"

        if not source_dir.exists():
            pytest.skip("Source directory not found")

        load_use_case = LoadDataUseCase(container)
        try:
            load_use_case.execute(str(source_dir))
        except Exception:
            pytest.skip("Could not load PDFs")

        search_use_case = SearchPriceUseCase(container)

        # Test searches with different complexity
        simple_queries = ["2lb zone 5", "5lb zone 8"]
        complex_queries = ["2 pounds to zone 5", "5 lbs shipped to zone 8"]

        simple_times = []
        for query in simple_queries:
            start = time.time()
            search_use_case.execute(SearchRequest(query=query))
            simple_times.append((time.time() - start) * 1000)

        complex_times = []
        for query in complex_queries:
            start = time.time()
            search_use_case.execute(SearchRequest(query=query))
            complex_times.append((time.time() - start) * 1000)

        avg_simple = sum(simple_times) / len(simple_times)
        avg_complex = sum(complex_times) / len(complex_times)

        print(f"\nQuery complexity impact:")
        print(f"  Simple queries avg: {avg_simple:.2f} ms")
        print(f"  Complex queries avg: {avg_complex:.2f} ms")

        # Both should still be reasonably fast
        assert avg_simple < 100
        assert avg_complex < 150


if __name__ == "__main__":
    # Run performance tests with detailed output
    pytest.main([__file__, "-v", "-s"])
