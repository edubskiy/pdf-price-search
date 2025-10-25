"""
Unit tests for PriceQuery value object.
"""

import pytest
from decimal import Decimal

from src.domain.value_objects.price_query import PriceQuery
from src.domain.value_objects.zone import Zone
from src.domain.value_objects.weight import Weight


class TestPriceQueryCreation:
    """Test PriceQuery creation and validation."""

    def test_create_price_query_without_packaging(self):
        """Test creating a basic price query without packaging type."""
        query = PriceQuery(
            service_type="FedEx 2Day",
            zone=Zone(5),
            weight=Weight(3),
        )
        assert query.service_type == "FedEx 2Day"
        assert query.zone == Zone(5)
        assert query.weight == Weight(3)
        assert query.packaging_type is None

    def test_create_price_query_with_packaging(self):
        """Test creating a price query with packaging type."""
        query = PriceQuery(
            service_type="Standard Overnight",
            zone=Zone(2),
            weight=Weight(10),
            packaging_type="other packaging",
        )
        assert query.service_type == "Standard Overnight"
        assert query.zone == Zone(2)
        assert query.weight == Weight(10)
        assert query.packaging_type == "other packaging"

    def test_service_type_is_stripped(self):
        """Test that service_type whitespace is stripped."""
        query = PriceQuery(
            service_type="  FedEx 2Day  ",
            zone=Zone(5),
            weight=Weight(3),
        )
        assert query.service_type == "FedEx 2Day"

    def test_packaging_type_is_stripped(self):
        """Test that packaging_type whitespace is stripped."""
        query = PriceQuery(
            service_type="FedEx 2Day",
            zone=Zone(5),
            weight=Weight(3),
            packaging_type="  other packaging  ",
        )
        assert query.packaging_type == "other packaging"

    def test_empty_packaging_type_becomes_none(self):
        """Test that empty packaging_type becomes None."""
        query = PriceQuery(
            service_type="FedEx 2Day",
            zone=Zone(5),
            weight=Weight(3),
            packaging_type="   ",
        )
        assert query.packaging_type is None


class TestPriceQueryValidation:
    """Test PriceQuery validation."""

    def test_empty_service_type_raises_error(self):
        """Test that empty service_type raises ValueError."""
        with pytest.raises(ValueError) as exc_info:
            PriceQuery(
                service_type="",
                zone=Zone(5),
                weight=Weight(3),
            )
        assert "empty" in str(exc_info.value).lower()

    def test_whitespace_service_type_raises_error(self):
        """Test that whitespace-only service_type raises ValueError."""
        with pytest.raises(ValueError):
            PriceQuery(
                service_type="   ",
                zone=Zone(5),
                weight=Weight(3),
            )

    def test_non_string_service_type_raises_error(self):
        """Test that non-string service_type raises TypeError."""
        with pytest.raises(TypeError):
            PriceQuery(
                service_type=123,
                zone=Zone(5),
                weight=Weight(3),
            )

    def test_non_zone_zone_raises_error(self):
        """Test that non-Zone zone raises TypeError."""
        with pytest.raises(TypeError):
            PriceQuery(
                service_type="FedEx 2Day",
                zone=5,
                weight=Weight(3),
            )

    def test_non_weight_weight_raises_error(self):
        """Test that non-Weight weight raises TypeError."""
        with pytest.raises(TypeError):
            PriceQuery(
                service_type="FedEx 2Day",
                zone=Zone(5),
                weight=3,
            )

    def test_non_string_packaging_type_raises_error(self):
        """Test that non-string packaging_type raises TypeError."""
        with pytest.raises(TypeError):
            PriceQuery(
                service_type="FedEx 2Day",
                zone=Zone(5),
                weight=Weight(3),
                packaging_type=123,
            )


class TestPriceQueryEquality:
    """Test PriceQuery equality and hashing."""

    def test_equal_queries_are_equal(self):
        """Test that queries with same values are equal."""
        query1 = PriceQuery(
            service_type="FedEx 2Day",
            zone=Zone(5),
            weight=Weight(3),
        )
        query2 = PriceQuery(
            service_type="FedEx 2Day",
            zone=Zone(5),
            weight=Weight(3),
        )
        assert query1 == query2

    def test_equal_queries_with_packaging_are_equal(self):
        """Test that queries with same values including packaging are equal."""
        query1 = PriceQuery(
            service_type="FedEx 2Day",
            zone=Zone(5),
            weight=Weight(3),
            packaging_type="other",
        )
        query2 = PriceQuery(
            service_type="FedEx 2Day",
            zone=Zone(5),
            weight=Weight(3),
            packaging_type="other",
        )
        assert query1 == query2

    def test_different_service_type_not_equal(self):
        """Test that queries with different service types are not equal."""
        query1 = PriceQuery(
            service_type="FedEx 2Day",
            zone=Zone(5),
            weight=Weight(3),
        )
        query2 = PriceQuery(
            service_type="Express Saver",
            zone=Zone(5),
            weight=Weight(3),
        )
        assert query1 != query2

    def test_different_zone_not_equal(self):
        """Test that queries with different zones are not equal."""
        query1 = PriceQuery(
            service_type="FedEx 2Day",
            zone=Zone(5),
            weight=Weight(3),
        )
        query2 = PriceQuery(
            service_type="FedEx 2Day",
            zone=Zone(6),
            weight=Weight(3),
        )
        assert query1 != query2

    def test_different_weight_not_equal(self):
        """Test that queries with different weights are not equal."""
        query1 = PriceQuery(
            service_type="FedEx 2Day",
            zone=Zone(5),
            weight=Weight(3),
        )
        query2 = PriceQuery(
            service_type="FedEx 2Day",
            zone=Zone(5),
            weight=Weight(4),
        )
        assert query1 != query2

    def test_different_packaging_not_equal(self):
        """Test that queries with different packaging are not equal."""
        query1 = PriceQuery(
            service_type="FedEx 2Day",
            zone=Zone(5),
            weight=Weight(3),
            packaging_type="other",
        )
        query2 = PriceQuery(
            service_type="FedEx 2Day",
            zone=Zone(5),
            weight=Weight(3),
            packaging_type=None,
        )
        assert query1 != query2

    def test_query_not_equal_to_non_query(self):
        """Test that query is not equal to non-query objects."""
        query = PriceQuery(
            service_type="FedEx 2Day",
            zone=Zone(5),
            weight=Weight(3),
        )
        assert query != "FedEx 2Day, Zone 5, 3 lb"
        assert query != {"service": "FedEx 2Day"}

    def test_equal_queries_have_same_hash(self):
        """Test that equal queries have the same hash."""
        query1 = PriceQuery(
            service_type="FedEx 2Day",
            zone=Zone(5),
            weight=Weight(3),
        )
        query2 = PriceQuery(
            service_type="FedEx 2Day",
            zone=Zone(5),
            weight=Weight(3),
        )
        assert hash(query1) == hash(query2)

    def test_queries_can_be_used_in_sets(self):
        """Test that queries can be used in sets."""
        query1 = PriceQuery("FedEx 2Day", Zone(5), Weight(3))
        query2 = PriceQuery("FedEx 2Day", Zone(5), Weight(3))
        query3 = PriceQuery("Express Saver", Zone(5), Weight(3))

        queries = {query1, query2, query3}
        assert len(queries) == 2

    def test_queries_can_be_used_as_dict_keys(self):
        """Test that queries can be used as dictionary keys."""
        query1 = PriceQuery("FedEx 2Day", Zone(5), Weight(3))
        query2 = PriceQuery("Express Saver", Zone(5), Weight(3))

        query_dict = {query1: "price1", query2: "price2"}
        assert query_dict[query1] == "price1"


class TestPriceQueryImmutability:
    """Test that PriceQuery is immutable."""

    def test_cannot_modify_service_type(self):
        """Test that service_type cannot be modified."""
        query = PriceQuery("FedEx 2Day", Zone(5), Weight(3))
        with pytest.raises(AttributeError):
            query.service_type = "Express Saver"

    def test_cannot_modify_zone(self):
        """Test that zone cannot be modified."""
        query = PriceQuery("FedEx 2Day", Zone(5), Weight(3))
        with pytest.raises(AttributeError):
            query.zone = Zone(6)

    def test_cannot_modify_weight(self):
        """Test that weight cannot be modified."""
        query = PriceQuery("FedEx 2Day", Zone(5), Weight(3))
        with pytest.raises(AttributeError):
            query.weight = Weight(4)

    def test_cannot_modify_packaging_type(self):
        """Test that packaging_type cannot be modified."""
        query = PriceQuery("FedEx 2Day", Zone(5), Weight(3))
        with pytest.raises(AttributeError):
            query.packaging_type = "other"

    def test_cannot_add_new_attributes(self):
        """Test that new attributes cannot be added."""
        query = PriceQuery("FedEx 2Day", Zone(5), Weight(3))
        with pytest.raises(AttributeError):
            query.new_attr = "test"

    def test_cannot_delete_attributes(self):
        """Test that attributes cannot be deleted."""
        query = PriceQuery("FedEx 2Day", Zone(5), Weight(3))
        with pytest.raises(AttributeError):
            del query.service_type


class TestPriceQueryStringRepresentation:
    """Test PriceQuery string representations."""

    def test_str_representation_without_packaging(self):
        """Test __str__ method without packaging."""
        query = PriceQuery("FedEx 2Day", Zone(5), Weight(3))
        result = str(query)
        assert "FedEx 2Day" in result
        assert "Zone 5" in result
        assert "3 lb" in result

    def test_str_representation_with_packaging(self):
        """Test __str__ method with packaging."""
        query = PriceQuery("FedEx 2Day", Zone(5), Weight(3), "other packaging")
        result = str(query)
        assert "FedEx 2Day" in result
        assert "Zone 5" in result
        assert "3 lb" in result
        assert "other packaging" in result

    def test_repr_representation(self):
        """Test __repr__ method."""
        query = PriceQuery("FedEx 2Day", Zone(5), Weight(3))
        result = repr(query)
        assert "PriceQuery" in result
        assert "FedEx 2Day" in result
