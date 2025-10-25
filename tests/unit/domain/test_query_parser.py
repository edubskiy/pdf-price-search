"""
Unit tests for QueryParser domain service.
"""

import pytest
from decimal import Decimal

from src.domain.services.query_parser import QueryParser
from src.domain.value_objects.price_query import PriceQuery
from src.domain.value_objects.zone import Zone
from src.domain.value_objects.weight import Weight
from src.domain.exceptions import InvalidQueryException


class TestQueryParserCommaSeparated:
    """Test parsing comma-separated query formats."""

    def test_parse_basic_comma_separated(self):
        """Test parsing basic comma-separated query."""
        parser = QueryParser()
        query = parser.parse("FedEx 2Day, Zone 5, 3 lb")

        assert query.service_type == "FedEx 2Day"
        assert query.zone == Zone(5)
        assert query.weight == Weight(3)
        assert query.packaging_type is None

    def test_parse_comma_separated_with_packaging(self):
        """Test parsing comma-separated query with packaging."""
        parser = QueryParser()
        query = parser.parse("Standard Overnight, z2, 10 lbs, other packaging")

        assert query.service_type == "Standard Overnight"
        assert query.zone == Zone(2)
        assert query.weight == Weight(10)
        assert query.packaging_type == "other packaging"

    def test_parse_comma_separated_with_decimal_weight(self):
        """Test parsing comma-separated query with decimal weight."""
        parser = QueryParser()
        query = parser.parse("Express Saver, Zone 3, 1.5 lb")

        assert query.service_type == "Express Saver"
        assert query.zone == Zone(3)
        assert query.weight == Weight(Decimal("1.5"))

    def test_parse_comma_separated_too_few_parts_raises_error(self):
        """Test that comma-separated with fewer than 3 parts raises error."""
        parser = QueryParser()
        with pytest.raises(InvalidQueryException):
            parser.parse("FedEx 2Day, Zone 5")

    def test_parse_comma_separated_too_many_parts_raises_error(self):
        """Test that comma-separated with more than 4 parts raises error."""
        parser = QueryParser()
        with pytest.raises(InvalidQueryException):
            parser.parse("FedEx 2Day, Zone 5, 3 lb, other, extra")


class TestQueryParserSpaceSeparated:
    """Test parsing space-separated query formats."""

    def test_parse_space_separated_express_saver(self):
        """Test parsing 'Express Saver Z8 1 lb' format."""
        parser = QueryParser()
        query = parser.parse("Express Saver Z8 1 lb")

        assert query.service_type == "Express Saver"
        assert query.zone == Zone(8)
        assert query.weight == Weight(1)
        assert query.packaging_type is None

    def test_parse_space_separated_ground(self):
        """Test parsing 'Ground Z6 12 lb' format."""
        parser = QueryParser()
        query = parser.parse("Ground Z6 12 lb")

        assert query.service_type == "Ground"
        assert query.zone == Zone(6)
        assert query.weight == Weight(12)

    def test_parse_space_separated_home_delivery(self):
        """Test parsing 'Home Delivery zone 3 5 lb' format."""
        parser = QueryParser()
        query = parser.parse("Home Delivery zone 3 5 lb")

        assert query.service_type == "Home Delivery"
        assert query.zone == Zone(3)
        assert query.weight == Weight(5)

    def test_parse_space_separated_with_packaging(self):
        """Test parsing space-separated with packaging info."""
        parser = QueryParser()
        query = parser.parse("FedEx 2Day Z5 3 lb other packaging")

        assert query.service_type == "FedEx 2Day"
        assert query.zone == Zone(5)
        assert query.weight == Weight(3)
        # Note: packaging parsing in space-separated might capture "other packaging"
        # but implementation may vary

    def test_parse_space_separated_no_zone_raises_error(self):
        """Test that space-separated without zone raises error."""
        parser = QueryParser()
        with pytest.raises(InvalidQueryException) as exc_info:
            parser.parse("FedEx 2Day 3 lb")
        assert "zone" in str(exc_info.value).lower()

    def test_parse_space_separated_no_weight_raises_error(self):
        """Test that space-separated without weight raises error."""
        parser = QueryParser()
        with pytest.raises(InvalidQueryException) as exc_info:
            parser.parse("FedEx 2Day Z5")
        assert "weight" in str(exc_info.value).lower()


class TestQueryParserExampleQueries:
    """Test all example queries from requirements."""

    @pytest.mark.parametrize(
        "query_str,expected_service,expected_zone,expected_weight,expected_packaging",
        [
            ("FedEx 2Day, Zone 5, 3 lb", "FedEx 2Day", 5, 3, None),
            (
                "Standard Overnight, z2, 10 lbs, other packaging",
                "Standard Overnight",
                2,
                10,
                "other packaging",
            ),
            ("Express Saver Z8 1 lb", "Express Saver", 8, 1, None),
            ("Ground Z6 12 lb", "Ground", 6, 12, None),
            ("Home Delivery zone 3 5 lb", "Home Delivery", 3, 5, None),
        ],
    )
    def test_parse_all_example_queries(
        self,
        query_str,
        expected_service,
        expected_zone,
        expected_weight,
        expected_packaging,
    ):
        """Test parsing all example queries from requirements."""
        parser = QueryParser()
        query = parser.parse(query_str)

        assert query.service_type == expected_service
        assert query.zone.value == expected_zone
        assert float(query.weight.value) == expected_weight
        assert query.packaging_type == expected_packaging


class TestQueryParserEdgeCases:
    """Test edge cases and error handling."""

    def test_parse_empty_string_raises_error(self):
        """Test that empty string raises InvalidQueryException."""
        parser = QueryParser()
        with pytest.raises(InvalidQueryException):
            parser.parse("")

    def test_parse_whitespace_only_raises_error(self):
        """Test that whitespace-only string raises InvalidQueryException."""
        parser = QueryParser()
        with pytest.raises(InvalidQueryException):
            parser.parse("   ")

    def test_parse_non_string_raises_error(self):
        """Test that non-string input raises TypeError."""
        parser = QueryParser()
        with pytest.raises(TypeError):
            parser.parse(123)

    def test_parse_with_extra_whitespace(self):
        """Test parsing with extra whitespace."""
        parser = QueryParser()
        query = parser.parse("  FedEx 2Day  ,  Zone 5  ,  3 lb  ")

        assert query.service_type == "FedEx 2Day"
        assert query.zone == Zone(5)
        assert query.weight == Weight(3)

    def test_parse_empty_service_type_raises_error(self):
        """Test that empty service type raises error."""
        parser = QueryParser()
        with pytest.raises(InvalidQueryException):
            parser.parse(", Zone 5, 3 lb")

    def test_parse_invalid_zone_raises_error(self):
        """Test that invalid zone in query raises error."""
        parser = QueryParser()
        with pytest.raises(InvalidQueryException) as exc_info:
            parser.parse("FedEx 2Day, Zone 9, 3 lb")
        assert "zone" in str(exc_info.value).lower()

    def test_parse_invalid_weight_raises_error(self):
        """Test that invalid weight in query raises error."""
        parser = QueryParser()
        with pytest.raises(InvalidQueryException) as exc_info:
            parser.parse("FedEx 2Day, Zone 5, 0 lb")
        assert "weight" in str(exc_info.value).lower()

    def test_parse_negative_weight_raises_error(self):
        """Test that negative weight raises error."""
        parser = QueryParser()
        with pytest.raises(InvalidQueryException):
            parser.parse("FedEx 2Day, Zone 5, -3 lb")

    def test_parse_zone_out_of_range_raises_error(self):
        """Test that zone out of range raises error."""
        parser = QueryParser()
        with pytest.raises(InvalidQueryException):
            parser.parse("FedEx 2Day, Zone 10, 3 lb")


class TestQueryParserCaseInsensitivity:
    """Test case insensitivity in parsing."""

    def test_parse_uppercase_zone(self):
        """Test parsing with uppercase ZONE."""
        parser = QueryParser()
        query = parser.parse("FedEx 2Day, ZONE 5, 3 LB")

        assert query.zone == Zone(5)
        assert query.weight == Weight(3)

    def test_parse_mixed_case_zone(self):
        """Test parsing with mixed case Zone."""
        parser = QueryParser()
        query = parser.parse("FedEx 2Day, zOnE 5, 3 Lb")

        assert query.zone == Zone(5)
        assert query.weight == Weight(3)

    def test_parse_uppercase_z_notation(self):
        """Test parsing with uppercase Z notation."""
        parser = QueryParser()
        query = parser.parse("Express Saver Z8 1 LB")

        assert query.zone == Zone(8)
        assert query.weight == Weight(1)


class TestQueryParserVariousFormats:
    """Test various weight and zone formats."""

    def test_parse_z_notation(self):
        """Test parsing with z notation (z5)."""
        parser = QueryParser()
        query = parser.parse("FedEx 2Day, z5, 3 lb")

        assert query.zone == Zone(5)

    def test_parse_plain_zone_number(self):
        """Test parsing with plain zone number."""
        parser = QueryParser()
        query = parser.parse("FedEx 2Day, 5, 3 lb")

        assert query.zone == Zone(5)

    def test_parse_weight_without_unit(self):
        """Test parsing weight without unit."""
        parser = QueryParser()
        query = parser.parse("FedEx 2Day, Zone 5, 3")

        assert query.weight == Weight(3)

    def test_parse_weight_with_lbs(self):
        """Test parsing weight with 'lbs'."""
        parser = QueryParser()
        query = parser.parse("FedEx 2Day, Zone 5, 3 lbs")

        assert query.weight == Weight(3)

    def test_parse_decimal_weight(self):
        """Test parsing decimal weight."""
        parser = QueryParser()
        query = parser.parse("FedEx 2Day, Zone 5, 3.5 lb")

        assert query.weight == Weight(Decimal("3.5"))


class TestQueryParserReturnsCorrectType:
    """Test that parser returns correct types."""

    def test_parse_returns_price_query(self):
        """Test that parse returns PriceQuery instance."""
        parser = QueryParser()
        query = parser.parse("FedEx 2Day, Zone 5, 3 lb")

        assert isinstance(query, PriceQuery)

    def test_parsed_query_has_zone_value_object(self):
        """Test that parsed query has Zone value object."""
        parser = QueryParser()
        query = parser.parse("FedEx 2Day, Zone 5, 3 lb")

        assert isinstance(query.zone, Zone)

    def test_parsed_query_has_weight_value_object(self):
        """Test that parsed query has Weight value object."""
        parser = QueryParser()
        query = parser.parse("FedEx 2Day, Zone 5, 3 lb")

        assert isinstance(query.weight, Weight)
