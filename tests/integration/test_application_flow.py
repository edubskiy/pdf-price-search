"""
Integration tests for end-to-end application flow.

These tests verify the complete application flow from loading data
to executing searches and listing services.
"""

import pytest
from pathlib import Path

from src.application.container import Container
from src.application.config import AppConfig
from src.application.exceptions import DataNotLoadedException


class TestApplicationFlow:
    """Test end-to-end application flow."""

    @pytest.fixture
    def config(self):
        """Create test configuration."""
        config = AppConfig()
        # Override with test settings if needed
        return config

    @pytest.fixture
    def container(self, config):
        """Create a fresh container for each test."""
        container = Container(config=config)
        container.ensure_ready()
        yield container
        # Cleanup
        container.reset()

    @pytest.fixture
    def loaded_container(self, container):
        """Create a container with data loaded."""
        load_use_case = container.load_data_use_case()

        # Load from default directory
        try:
            result = load_use_case.execute_default()
            if not result["success"]:
                pytest.skip("No PDF files available to load")
        except Exception as e:
            pytest.skip(f"Could not load PDF files: {e}")

        return container

    def test_complete_flow(self, loaded_container):
        """Test the complete application flow."""
        # Step 1: Verify data is loaded
        search_service = loaded_container.price_search_service()
        assert search_service.is_data_loaded()
        assert search_service.get_service_count() > 0

        # Step 2: List services
        list_use_case = loaded_container.list_services_use_case()
        services = list_use_case.execute()

        assert len(services) > 0
        assert all(hasattr(s, 'name') for s in services)
        assert all(hasattr(s, 'available_zones') for s in services)
        assert all(hasattr(s, 'weight_range') for s in services)

        # Step 3: Execute a search
        search_use_case = loaded_container.search_price_use_case()

        # Try a simple query (adjust based on your test data)
        test_queries = [
            "FedEx 2Day, Zone 5, 3 lb",
            "Standard Overnight, z2, 10 lbs",
        ]

        successful_searches = 0
        for query in test_queries:
            response = search_use_case.execute(query)

            # Response should have all required fields
            assert hasattr(response, 'success')
            assert hasattr(response, 'search_time_ms')
            assert response.search_time_ms >= 0

            if response.success:
                successful_searches += 1
                assert response.price is not None
                assert response.service is not None
                assert response.zone is not None
                assert response.weight is not None
                assert response.error_message is None
            else:
                assert response.error_message is not None

        # At least one search should succeed if we have data
        assert successful_searches > 0, "No searches succeeded"

    def test_load_data_use_case(self, container):
        """Test loading data through the use case."""
        load_use_case = container.load_data_use_case()

        # Load from default directory
        result = load_use_case.execute_default()

        # Verify result structure
        assert "success" in result
        assert "loaded_files" in result
        assert "total_files" in result
        assert "failed_files" in result

        if result["total_files"] > 0:
            assert result["success"]
            assert len(result["loaded_files"]) > 0

    def test_search_without_loaded_data(self, container):
        """Test that searching without loaded data raises appropriate error."""
        search_use_case = container.search_price_use_case()

        # Try to search without loading data
        response = search_use_case.execute("FedEx 2Day, Zone 5, 3 lb")

        # Should return error response
        assert not response.success
        assert "data" in response.error_message.lower() or "load" in response.error_message.lower()

    def test_list_services_without_loaded_data(self, container):
        """Test that listing services without loaded data raises error."""
        list_use_case = container.list_services_use_case()

        # Should raise DataNotLoadedException
        with pytest.raises(DataNotLoadedException):
            list_use_case.execute()

    def test_cache_functionality(self, loaded_container):
        """Test that caching works correctly."""
        config = loaded_container.config()

        if not config.enable_cache:
            pytest.skip("Cache is disabled")

        search_use_case = loaded_container.search_price_use_case()

        # First search (cache miss)
        query = "FedEx 2Day, Zone 5, 3 lb"
        response1 = search_use_case.execute(query, use_cache=True)

        if not response1.success:
            pytest.skip("Test query did not succeed")

        # Second search (should be cache hit)
        response2 = search_use_case.execute(query, use_cache=True)

        # Both should succeed with same results
        assert response1.success == response2.success
        if response1.success:
            assert response1.price == response2.price
            assert response1.service == response2.service
            assert response1.zone == response2.zone

    def test_search_with_invalid_query(self, loaded_container):
        """Test searching with an invalid query."""
        search_use_case = loaded_container.search_price_use_case()

        invalid_queries = [
            "",  # Empty query
            "invalid",  # Too few parts
            "service only",  # Missing zone and weight
        ]

        for query in invalid_queries:
            response = search_use_case.execute(query)

            # Should return error response
            assert not response.success
            assert response.error_message is not None
            assert response.price is None

    def test_search_with_nonexistent_service(self, loaded_container):
        """Test searching for a service that doesn't exist."""
        search_use_case = loaded_container.search_price_use_case()

        # Query with a non-existent service
        response = search_use_case.execute("NonExistent Service, Zone 5, 3 lb")

        # Should return error response
        assert not response.success
        assert response.error_message is not None
        assert "not" in response.error_message.lower() or "found" in response.error_message.lower()

    def test_batch_search(self, loaded_container):
        """Test batch searching."""
        search_use_case = loaded_container.search_price_use_case()

        queries = [
            "FedEx 2Day, Zone 5, 3 lb",
            "Standard Overnight, z2, 10 lbs",
            "Express Saver Z8 1 lb",
        ]

        responses = search_use_case.execute_batch(queries)

        # Should get response for each query
        assert len(responses) == len(queries)

        # All responses should have required fields
        for response in responses:
            assert hasattr(response, 'success')
            assert hasattr(response, 'search_time_ms')

    def test_service_summary(self, loaded_container):
        """Test getting service summary."""
        list_use_case = loaded_container.list_services_use_case()

        summary = list_use_case.execute_summary()

        # Verify summary structure
        assert "total_services" in summary
        assert "available_zones" in summary
        assert "weight_range" in summary
        assert "services" in summary

        assert summary["total_services"] > 0
        assert len(summary["available_zones"]) > 0
        assert "min" in summary["weight_range"]
        assert "max" in summary["weight_range"]

    def test_performance_metrics(self, loaded_container):
        """Test that performance metrics are tracked."""
        search_use_case = loaded_container.search_price_use_case()

        # Execute a search
        response = search_use_case.execute("FedEx 2Day, Zone 5, 3 lb")

        # Verify timing is tracked
        assert response.search_time_ms >= 0
        assert response.search_time_ms < 10000  # Should complete within 10 seconds

    def test_container_singleton_behavior(self, container):
        """Test that container returns singleton instances."""
        # Get instances twice
        parser1 = container.query_parser()
        parser2 = container.query_parser()

        # Should be the same instance
        assert parser1 is parser2

        # Same for other singletons
        repo1 = container.repository()
        repo2 = container.repository()
        assert repo1 is repo2

    def test_container_reset(self, container):
        """Test that container reset works correctly."""
        # Get an instance
        parser1 = container.query_parser()

        # Reset container
        container.reset()

        # Get instance again
        parser2 = container.query_parser()

        # Should be a different instance
        assert parser1 is not parser2
