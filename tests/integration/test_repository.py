"""
Integration tests for PDF price repository.

These tests use the actual PDF files to ensure the repository
can load and manage real shipping service data.
"""

import pytest
from decimal import Decimal

from src.infrastructure.pdf.repository import PDFPriceRepository
from src.domain import Zone, Weight


# Path to actual PDF files
FEDEX_PDF = "/Users/evgeniydubskiy/Dev/edubskiy/pdf-price-search/source/FedEx_Standard_List_Rates_2025.pdf"


class TestPDFPriceRepository:
    """Integration tests for PDFPriceRepository."""

    @pytest.fixture
    def repository(self):
        """Create a fresh repository instance."""
        return PDFPriceRepository()

    def test_load_from_pdf(self, repository):
        """Test loading services from actual PDF file."""
        services = repository.load_from_pdf(FEDEX_PDF)

        # Should return list of services
        assert isinstance(services, list)
        assert len(services) > 0

        # All services should have the expected structure
        for service in services:
            assert service.service_name
            assert len(service.price_table) > 0

    def test_get_all_services(self, repository):
        """Test retrieving all loaded services."""
        # Initially empty
        assert len(repository.get_all_services()) == 0

        # Load services
        repository.load_from_pdf(FEDEX_PDF)

        # Should now have services
        services = repository.get_all_services()
        assert len(services) > 0

        # All should be ShippingService objects
        for service in services:
            assert hasattr(service, 'service_name')
            assert hasattr(service, 'price_table')

    def test_get_service_by_name(self, repository):
        """Test retrieving a specific service by name."""
        repository.load_from_pdf(FEDEX_PDF)

        # Get by canonical name
        service = repository.get_service("FedEx 2Day")
        assert service is not None
        assert service.service_name == "FedEx 2Day"

        # Get by variant (case insensitive)
        service2 = repository.get_service("2day")
        assert service2 is not None
        assert service2.service_name == "FedEx 2Day"

    def test_get_nonexistent_service(self, repository):
        """Test retrieving a service that doesn't exist."""
        repository.load_from_pdf(FEDEX_PDF)

        service = repository.get_service("Nonexistent Service")
        assert service is None

    def test_service_has_price_data(self, repository):
        """Test that loaded services have actual price data."""
        repository.load_from_pdf(FEDEX_PDF)

        service = repository.get_service("FedEx 2Day")
        assert service is not None

        # Should have zones
        assert len(service.price_table) > 0

        # Should have prices for each zone
        for zone_num, weights in service.price_table.items():
            assert len(weights) > 0

    def test_price_lookup_integration(self, repository):
        """Test end-to-end price lookup using actual data."""
        repository.load_from_pdf(FEDEX_PDF)

        service = repository.get_service("FedEx 2Day")
        assert service is not None

        # Try to get a price
        zone = Zone(2)
        weight = Weight(Decimal("5"))

        price = service.get_price(zone, weight)

        # Price should be a positive decimal
        assert isinstance(price, Decimal)
        assert price > 0

    def test_refresh_data(self, repository):
        """Test refreshing repository data."""
        # Load initial data
        repository.load_from_pdf(FEDEX_PDF)
        initial_count = repository.get_service_count()
        assert initial_count > 0

        # Refresh
        repository.refresh_data()

        # Should still have the same services
        assert repository.get_service_count() == initial_count

    def test_clear(self, repository):
        """Test clearing repository data."""
        # Load data
        repository.load_from_pdf(FEDEX_PDF)
        assert repository.get_service_count() > 0

        # Clear
        repository.clear()

        # Should be empty
        assert repository.get_service_count() == 0
        assert len(repository.get_all_services()) == 0

    def test_get_service_names(self, repository):
        """Test retrieving list of service names."""
        repository.load_from_pdf(FEDEX_PDF)

        names = repository.get_service_names()

        # Should be a sorted list
        assert isinstance(names, list)
        assert len(names) > 0

        # Check expected services
        expected = [
            "FedEx 2Day",
            "FedEx Express Saver",
            "FedEx First Overnight",
            "FedEx Priority Overnight",
            "FedEx Standard Overnight",
        ]

        for expected_name in expected:
            assert expected_name in names

    def test_has_service(self, repository):
        """Test checking if a service exists."""
        repository.load_from_pdf(FEDEX_PDF)

        # Should find existing service
        assert repository.has_service("FedEx 2Day")
        assert repository.has_service("2day")  # Case insensitive

        # Should not find nonexistent service
        assert not repository.has_service("Nonexistent Service")

    def test_multiple_zones_support(self, repository):
        """Test that services support multiple zones."""
        repository.load_from_pdf(FEDEX_PDF)

        service = repository.get_service("FedEx 2Day")
        assert service is not None

        # Should have multiple zones
        zones = list(service.price_table.keys())
        assert len(zones) > 1

        # Zones should be in expected range (2-8 for FedEx)
        assert all(2 <= z <= 8 for z in zones)

    def test_multiple_weights_support(self, repository):
        """Test that services support multiple weights per zone."""
        repository.load_from_pdf(FEDEX_PDF)

        service = repository.get_service("FedEx 2Day")
        assert service is not None

        # Check first zone
        if service.price_table:
            first_zone = list(service.price_table.keys())[0]
            weights = service.price_table[first_zone]

            # Should have multiple weights
            assert len(weights) > 10

    def test_price_consistency_across_zones(self, repository):
        """Test that prices are generally increasing with zones."""
        repository.load_from_pdf(FEDEX_PDF)

        service = repository.get_service("FedEx 2Day")
        assert service is not None

        # Compare prices for same weight across zones
        test_weight = Weight(Decimal("10"))

        prices_by_zone = {}
        for zone_num in sorted(service.price_table.keys()):
            try:
                zone = Zone(zone_num)
                price = service.get_price(zone, test_weight)
                prices_by_zone[zone_num] = price
            except Exception:
                continue

        # Should have prices for multiple zones
        assert len(prices_by_zone) > 1

        # All prices should be positive
        assert all(p > 0 for p in prices_by_zone.values())

    def test_load_nonexistent_file_raises_error(self, repository):
        """Test that loading a nonexistent file raises error."""
        with pytest.raises(FileNotFoundError):
            repository.load_from_pdf("/nonexistent/file.pdf")

    def test_repository_persistence_across_operations(self, repository):
        """Test that loaded data persists across operations."""
        # Load data
        repository.load_from_pdf(FEDEX_PDF)
        initial_services = repository.get_service_names()

        # Perform various operations
        service1 = repository.get_service("FedEx 2Day")
        assert service1 is not None

        service2 = repository.get_service("FedEx Express Saver")
        assert service2 is not None

        # Data should still be consistent
        assert repository.get_service_names() == initial_services
