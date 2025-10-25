"""
Integration tests for PDF parser.

These tests use the actual PDF files in the source folder to ensure
the parser can extract real data correctly.
"""

import pytest
from pathlib import Path

from src.infrastructure.pdf import PDFParser, PDFParserError


# Path to actual PDF files
FEDEX_PDF = "/Users/evgeniydubskiy/Dev/edubskiy/pdf-price-search/source/FedEx_Standard_List_Rates_2025.pdf"


class TestPDFParser:
    """Integration tests for PDFParser."""

    @pytest.fixture
    def parser(self):
        """Create a PDFParser instance."""
        return PDFParser()

    def test_parse_fedex_pdf(self, parser):
        """Test parsing the actual FedEx PDF file."""
        # Parse the PDF
        result = parser.parse_file(FEDEX_PDF)

        # Verify metadata
        assert result.metadata is not None
        assert result.metadata.file_path == FEDEX_PDF
        assert result.metadata.total_pages > 0
        assert "FedEx" in result.metadata.title
        assert "2025" in result.metadata.effective_date

        # Verify tables were extracted
        assert len(result.price_tables) > 0
        assert result.metadata.extracted_pages == len(result.price_tables)

        # Verify service data was built
        assert len(result.service_data) > 0

    def test_extracted_services_are_valid(self, parser):
        """Test that extracted services contain expected FedEx services."""
        result = parser.parse_file(FEDEX_PDF)

        service_names = result.get_all_service_names()

        # Expected FedEx services
        expected_services = [
            "FedEx First Overnight",
            "FedEx Priority Overnight",
            "FedEx Standard Overnight",
            "FedEx 2Day",
            "FedEx Express Saver",
        ]

        for expected in expected_services:
            assert expected in service_names, f"Expected service '{expected}' not found"

    def test_extracted_zones_are_valid(self, parser):
        """Test that extracted zones are within expected range."""
        result = parser.parse_file(FEDEX_PDF)

        # Check zones across all tables
        zones = set()
        for table in result.price_tables:
            zones.add(table.zone)

        # FedEx typically has zones 2-8
        assert len(zones) > 0
        assert all(2 <= z <= 8 for z in zones), f"Invalid zones found: {zones}"

    def test_extracted_prices_are_valid(self, parser):
        """Test that extracted prices are valid decimals."""
        result = parser.parse_file(FEDEX_PDF)

        # Check first service
        if result.service_data:
            first_service = list(result.service_data.values())[0]

            # Check that we have prices
            assert len(first_service.zone_prices) > 0

            # Check price validity
            for zone, weight_prices in first_service.zone_prices.items():
                assert len(weight_prices) > 0

                for weight, price in weight_prices.items():
                    # Price should be positive
                    assert price > 0, f"Invalid price: {price}"

                    # Weight should be parseable as float
                    try:
                        float(weight)
                    except ValueError:
                        pytest.fail(f"Invalid weight format: {weight}")

    def test_price_tables_have_consistent_structure(self, parser):
        """Test that extracted price tables have consistent structure."""
        result = parser.parse_file(FEDEX_PDF)

        for table in result.price_tables:
            # Each table should have a zone
            assert table.zone > 0

            # Each table should have service columns
            assert len(table.service_columns) > 0

            # Each table should have weight-price mappings
            assert len(table.weight_prices) > 0

            # Each weight should have prices for all services
            for weight, prices in table.weight_prices.items():
                assert len(prices) == len(table.service_columns), (
                    f"Weight {weight} has {len(prices)} prices but "
                    f"{len(table.service_columns)} services"
                )

    def test_service_data_completeness(self, parser):
        """Test that service data is complete across zones."""
        result = parser.parse_file(FEDEX_PDF)

        for service_name, service_data in result.service_data.items():
            # Each service should have multiple zones
            assert len(service_data.zone_prices) > 0, (
                f"Service {service_name} has no zone prices"
            )

            # Each zone should have weights
            for zone, weight_prices in service_data.zone_prices.items():
                assert len(weight_prices) > 0, (
                    f"Service {service_name} zone {zone} has no weights"
                )

    def test_parse_nonexistent_file_raises_error(self, parser):
        """Test that parsing a nonexistent file raises FileNotFoundError."""
        with pytest.raises(FileNotFoundError):
            parser.parse_file("/nonexistent/file.pdf")

    def test_multiple_parses_return_consistent_results(self, parser):
        """Test that parsing the same file multiple times gives consistent results."""
        result1 = parser.parse_file(FEDEX_PDF)
        result2 = parser.parse_file(FEDEX_PDF)

        # Should have same number of tables
        assert len(result1.price_tables) == len(result2.price_tables)

        # Should have same services
        assert set(result1.service_data.keys()) == set(result2.service_data.keys())

        # Check first service has same data
        if result1.service_data:
            first_service_name = list(result1.service_data.keys())[0]
            service1 = result1.service_data[first_service_name]
            service2 = result2.service_data[first_service_name]

            assert service1.service_name == service2.service_name
            assert service1.get_all_zones() == service2.get_all_zones()


class TestTableExtraction:
    """Tests specifically for table extraction."""

    @pytest.fixture
    def parser(self):
        """Create a PDFParser instance."""
        return PDFParser()

    def test_zone_extraction(self, parser):
        """Test that zones are correctly extracted from pages."""
        result = parser.parse_file(FEDEX_PDF)

        # Group tables by zone
        zones_found = {}
        for table in result.price_tables:
            zone = table.zone
            if zone not in zones_found:
                zones_found[zone] = []
            zones_found[zone].append(table)

        # Should have multiple zones
        assert len(zones_found) > 1

        # Each zone should have at least one table
        for zone, tables in zones_found.items():
            assert len(tables) > 0

    def test_weight_extraction_format(self, parser):
        """Test that weight values are extracted in correct format."""
        result = parser.parse_file(FEDEX_PDF)

        if result.price_tables:
            first_table = result.price_tables[0]

            for weight in first_table.weight_prices.keys():
                # Weight should be numeric string
                try:
                    weight_float = float(weight)
                    assert weight_float > 0
                except ValueError:
                    pytest.fail(f"Invalid weight format: {weight}")
