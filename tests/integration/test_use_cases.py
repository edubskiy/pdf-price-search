"""
Integration tests for use cases.

These tests verify the use case implementations.
"""

import pytest

from src.application.container import Container
from src.application.config import AppConfig
from src.application.exceptions import DataNotLoadedException


class TestUseCases:
    """Test use case implementations."""

    @pytest.fixture
    def container(self):
        """Create and setup container."""
        config = AppConfig()
        container = Container(config=config)
        container.ensure_ready()
        yield container
        container.reset()

    @pytest.fixture
    def loaded_container(self, container):
        """Create a container with data loaded."""
        load_use_case = container.load_data_use_case()

        try:
            result = load_use_case.execute_default()
            if not result["success"]:
                pytest.skip("No PDF files available")
        except Exception as e:
            pytest.skip(f"Could not load PDFs: {e}")

        return container

    def test_load_data_use_case_default(self, container):
        """Test LoadDataUseCase with default directory."""
        load_use_case = container.load_data_use_case()

        result = load_use_case.execute_default()

        # Verify result structure
        assert "success" in result
        assert "loaded_files" in result
        assert "total_files" in result
        assert "failed_files" in result

    def test_load_data_use_case_get_loaded_pdfs(self, loaded_container):
        """Test getting loaded PDF list."""
        load_use_case = loaded_container.load_data_use_case()

        loaded_pdfs = load_use_case.get_loaded_pdfs()

        # Should have some PDFs loaded
        assert len(loaded_pdfs) > 0
        assert all(isinstance(p, str) for p in loaded_pdfs)

    def test_search_price_use_case_execute(self, loaded_container):
        """Test SearchPriceUseCase execution."""
        search_use_case = loaded_container.search_price_use_case()

        response = search_use_case.execute("FedEx 2Day, Zone 5, 3 lb")

        # Should return a response
        assert hasattr(response, 'success')
        assert hasattr(response, 'search_time_ms')

    def test_search_price_use_case_batch(self, loaded_container):
        """Test SearchPriceUseCase batch execution."""
        search_use_case = loaded_container.search_price_use_case()

        queries = [
            "FedEx 2Day, Zone 5, 3 lb",
            "Standard Overnight, z2, 10 lbs",
        ]

        responses = search_use_case.execute_batch(queries)

        # Should get response for each query
        assert len(responses) == len(queries)

        # All should have required fields
        for response in responses:
            assert hasattr(response, 'success')
            assert hasattr(response, 'search_time_ms')

    def test_list_services_use_case_execute(self, loaded_container):
        """Test ListServicesUseCase execution."""
        list_use_case = loaded_container.list_services_use_case()

        services = list_use_case.execute()

        # Should return services
        assert len(services) > 0

        # Verify service structure
        for service in services:
            assert hasattr(service, 'name')
            assert hasattr(service, 'available_zones')
            assert hasattr(service, 'weight_range')

    def test_list_services_use_case_without_data(self, container):
        """Test ListServicesUseCase without loaded data."""
        list_use_case = container.list_services_use_case()

        # Should raise exception
        with pytest.raises(DataNotLoadedException):
            list_use_case.execute()

    def test_list_services_use_case_summary(self, loaded_container):
        """Test ListServicesUseCase summary."""
        list_use_case = loaded_container.list_services_use_case()

        summary = list_use_case.execute_summary()

        # Verify summary structure
        assert "total_services" in summary
        assert "available_zones" in summary
        assert "weight_range" in summary
        assert "services" in summary

        assert summary["total_services"] > 0

    def test_list_services_use_case_get_by_name(self, loaded_container):
        """Test getting service by name."""
        list_use_case = loaded_container.list_services_use_case()

        # Get all services first
        services = list_use_case.execute()

        if len(services) == 0:
            pytest.skip("No services available")

        # Try to get the first service by name
        first_service = services[0]
        found_service = list_use_case.get_service_by_name(first_service.name)

        # Should find it
        assert found_service.name == first_service.name

    def test_list_services_use_case_invalid_name(self, loaded_container):
        """Test getting service with invalid name."""
        list_use_case = loaded_container.list_services_use_case()

        # Should raise ValueError
        with pytest.raises(ValueError):
            list_use_case.get_service_by_name("NonExistent Service")

    def test_use_case_error_handling(self, loaded_container):
        """Test use case error handling."""
        search_use_case = loaded_container.search_price_use_case()

        # Invalid query
        response = search_use_case.execute("")

        # Should return error response
        assert not response.success
        assert response.error_message is not None

    def test_use_case_logging(self, loaded_container):
        """Test that use cases perform logging."""
        search_use_case = loaded_container.search_price_use_case()

        # Execute a search (this should log)
        response = search_use_case.execute("FedEx 2Day, Zone 5, 3 lb")

        # If we get here, logging didn't crash
        assert hasattr(response, 'success')
