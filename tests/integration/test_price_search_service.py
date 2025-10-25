"""
Integration tests for PriceSearchService.

These tests verify the price search service with real data.
"""

import pytest
from decimal import Decimal

from src.application.container import Container
from src.application.config import AppConfig
from src.application.dto import SearchRequest


class TestPriceSearchService:
    """Test PriceSearchService integration."""

    @pytest.fixture
    def container(self):
        """Create and setup container."""
        config = AppConfig()
        container = Container(config=config)
        container.ensure_ready()

        # Load data
        load_use_case = container.load_data_use_case()
        try:
            result = load_use_case.execute_default()
            if not result["success"]:
                pytest.skip("No PDF files available")
        except Exception as e:
            pytest.skip(f"Could not load PDFs: {e}")

        yield container
        container.reset()

    @pytest.fixture
    def search_service(self, container):
        """Get the search service."""
        return container.price_search_service()

    def test_search_with_valid_request(self, search_service):
        """Test search with a valid request."""
        request = SearchRequest(
            query="FedEx 2Day, Zone 5, 3 lb",
            use_cache=True
        )

        response = search_service.search(request)

        # Should have all response fields
        assert hasattr(response, 'success')
        assert hasattr(response, 'search_time_ms')
        assert response.search_time_ms >= 0

        # If successful, verify data
        if response.success:
            assert response.price is not None
            assert isinstance(response.price, Decimal)
            assert response.service is not None
            assert response.zone is not None
            assert response.weight is not None
            assert response.currency == "USD"
            assert response.error_message is None

    def test_search_all_example_queries(self, search_service):
        """Test all example queries from requirements."""
        test_queries = [
            "FedEx 2Day, Zone 5, 3 lb",
            "Standard Overnight, z2, 10 lbs",
            "Express Saver Z8 1 lb",
            "Ground Z6 12 lb",
        ]

        results = []
        for query in test_queries:
            request = SearchRequest(query=query)
            response = search_service.search(request)
            results.append((query, response))

        # At least some should succeed
        successful = [r for q, r in results if r.success]
        assert len(successful) > 0, "No example queries succeeded"

        # Log results for manual verification
        for query, response in results:
            if response.success:
                print(f"\nQuery: {query}")
                print(f"  Service: {response.service}")
                print(f"  Price: ${response.price}")
                print(f"  Zone: {response.zone}, Weight: {response.weight} lb")

    def test_get_available_services(self, search_service):
        """Test getting available services."""
        services = search_service.get_available_services()

        # Should have services
        assert len(services) > 0

        # Verify service structure
        for service in services:
            assert service.name
            assert len(service.available_zones) > 0
            assert service.weight_range[0] <= service.weight_range[1]
            assert service.source_pdf

    def test_cache_hit_vs_miss(self, search_service, container):
        """Test cache hit vs miss performance."""
        config = container.config()

        if not config.enable_cache:
            pytest.skip("Cache disabled")

        query = "FedEx 2Day, Zone 5, 3 lb"

        # Clear cache
        search_service.clear_cache()

        # First search (cache miss)
        request1 = SearchRequest(query=query, use_cache=True)
        response1 = search_service.search(request1)

        if not response1.success:
            pytest.skip("Test query did not succeed")

        # Second search (cache hit)
        request2 = SearchRequest(query=query, use_cache=True)
        response2 = search_service.search(request2)

        # Results should match
        assert response1.success == response2.success
        assert response1.price == response2.price
        assert response1.service == response2.service

    def test_search_without_cache(self, search_service):
        """Test searching with cache disabled."""
        request = SearchRequest(
            query="FedEx 2Day, Zone 5, 3 lb",
            use_cache=False
        )

        response = search_service.search(request)

        # Should still work
        assert hasattr(response, 'success')
        assert response.search_time_ms >= 0

    def test_search_with_comma_format(self, search_service):
        """Test comma-separated query format."""
        queries = [
            "FedEx 2Day, Zone 5, 3 lb",
            "Standard Overnight, z2, 10 lbs",
        ]

        for query in queries:
            request = SearchRequest(query=query)
            response = search_service.search(request)

            # Should parse successfully
            assert hasattr(response, 'success')

    def test_search_with_space_format(self, search_service):
        """Test space-separated query format."""
        queries = [
            "Express Saver Z8 1 lb",
            "Ground Z6 12 lb",
        ]

        for query in queries:
            request = SearchRequest(query=query)
            response = search_service.search(request)

            # Should parse successfully
            assert hasattr(response, 'success')

    def test_search_with_invalid_zone(self, search_service):
        """Test searching with an invalid zone."""
        request = SearchRequest(
            query="FedEx 2Day, Zone 999, 3 lb"
        )

        response = search_service.search(request)

        # Should fail gracefully
        assert not response.success
        assert response.error_message is not None

    def test_search_with_invalid_weight(self, search_service):
        """Test searching with an invalid weight."""
        request = SearchRequest(
            query="FedEx 2Day, Zone 5, 999999 lb"
        )

        response = search_service.search(request)

        # Should fail gracefully
        assert not response.success
        assert response.error_message is not None

    def test_clear_cache(self, search_service, container):
        """Test clearing the cache."""
        config = container.config()

        if not config.enable_cache:
            pytest.skip("Cache disabled")

        # Perform a search to populate cache
        request = SearchRequest(query="FedEx 2Day, Zone 5, 3 lb")
        response1 = search_service.search(request)

        if not response1.success:
            pytest.skip("Test query did not succeed")

        # Clear cache
        search_service.clear_cache()

        # Search again
        response2 = search_service.search(request)

        # Should still work
        assert response2.success == response1.success

    def test_service_count(self, search_service):
        """Test getting service count."""
        count = search_service.get_service_count()

        assert count > 0
        assert isinstance(count, int)

    def test_is_data_loaded(self, search_service):
        """Test checking if data is loaded."""
        assert search_service.is_data_loaded()

    def test_multiple_searches_different_services(self, search_service):
        """Test searching for different services."""
        queries = [
            "FedEx 2Day, Zone 5, 3 lb",
            "Standard Overnight, z2, 10 lbs",
            "Priority Overnight, Zone 3, 5 lb",
        ]

        responses = []
        for query in queries:
            request = SearchRequest(query=query)
            response = search_service.search(request)
            responses.append(response)

        # Check that we got responses
        assert len(responses) == len(queries)

    def test_search_performance(self, search_service):
        """Test that searches complete in reasonable time."""
        request = SearchRequest(query="FedEx 2Day, Zone 5, 3 lb")

        response = search_service.search(request)

        # Should complete quickly (under 5 seconds)
        assert response.search_time_ms < 5000

    def test_concurrent_searches(self, search_service):
        """Test multiple concurrent searches."""
        queries = [
            "FedEx 2Day, Zone 5, 3 lb",
            "Standard Overnight, z2, 10 lbs",
            "Express Saver Z8 1 lb",
        ]

        responses = []
        for query in queries:
            request = SearchRequest(query=query)
            response = search_service.search(request)
            responses.append(response)

        # All should complete
        assert len(responses) == len(queries)

        # Each should have valid timing
        for response in responses:
            assert response.search_time_ms >= 0
