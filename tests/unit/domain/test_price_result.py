"""
Unit tests for PriceResult entity.
"""

import pytest
from decimal import Decimal
from datetime import datetime

from src.domain.entities.price_result import PriceResult
from src.domain.value_objects.zone import Zone
from src.domain.value_objects.weight import Weight


class TestPriceResultCreation:
    """Test PriceResult creation and initialization."""

    def test_create_price_result_with_minimal_args(self):
        """Test creating a price result with minimal required arguments."""
        result = PriceResult(
            price=Decimal("25.50"),
            service_type="FedEx 2Day",
            zone=Zone(5),
            weight=Weight(3),
            source_document="fedex_rates.pdf",
        )
        assert result.price == Decimal("25.50")
        assert result.service_type == "FedEx 2Day"
        assert result.zone == Zone(5)
        assert result.weight == Weight(3)
        assert result.source_document == "fedex_rates.pdf"
        assert result.currency == "USD"
        assert result.id is not None
        assert isinstance(result.timestamp, datetime)

    def test_create_price_result_with_all_args(self):
        """Test creating a price result with all arguments."""
        custom_time = datetime(2024, 1, 15, 10, 30, 0)
        result = PriceResult(
            price=Decimal("25.50"),
            service_type="FedEx 2Day",
            zone=Zone(5),
            weight=Weight(3),
            source_document="fedex_rates.pdf",
            currency="EUR",
            id="custom-id-123",
            timestamp=custom_time,
        )
        assert result.price == Decimal("25.50")
        assert result.currency == "EUR"
        assert result.id == "custom-id-123"
        assert result.timestamp == custom_time

    def test_auto_generated_id_is_unique(self):
        """Test that auto-generated IDs are unique."""
        result1 = PriceResult(
            Decimal("25.50"), "FedEx 2Day", Zone(5), Weight(3), "fedex_rates.pdf"
        )
        result2 = PriceResult(
            Decimal("25.50"), "FedEx 2Day", Zone(5), Weight(3), "fedex_rates.pdf"
        )
        assert result1.id != result2.id

    def test_currency_is_uppercased(self):
        """Test that currency is converted to uppercase."""
        result = PriceResult(
            Decimal("25.50"),
            "FedEx 2Day",
            Zone(5),
            Weight(3),
            "fedex_rates.pdf",
            currency="usd",
        )
        assert result.currency == "USD"

    def test_service_type_is_stripped(self):
        """Test that service_type whitespace is stripped."""
        result = PriceResult(
            Decimal("25.50"),
            "  FedEx 2Day  ",
            Zone(5),
            Weight(3),
            "fedex_rates.pdf",
        )
        assert result.service_type == "FedEx 2Day"

    def test_source_document_is_stripped(self):
        """Test that source_document whitespace is stripped."""
        result = PriceResult(
            Decimal("25.50"),
            "FedEx 2Day",
            Zone(5),
            Weight(3),
            "  fedex_rates.pdf  ",
        )
        assert result.source_document == "fedex_rates.pdf"


class TestPriceResultValidation:
    """Test PriceResult validation."""

    def test_negative_price_raises_error(self):
        """Test that negative price raises ValueError."""
        with pytest.raises(ValueError) as exc_info:
            PriceResult(
                Decimal("-25.50"), "FedEx 2Day", Zone(5), Weight(3), "fedex_rates.pdf"
            )
        assert "non-negative" in str(exc_info.value).lower()

    def test_zero_price_is_allowed(self):
        """Test that zero price is allowed."""
        result = PriceResult(
            Decimal("0"), "FedEx 2Day", Zone(5), Weight(3), "fedex_rates.pdf"
        )
        assert result.price == Decimal("0")

    def test_empty_service_type_raises_error(self):
        """Test that empty service_type raises ValueError."""
        with pytest.raises(ValueError):
            PriceResult(Decimal("25.50"), "", Zone(5), Weight(3), "fedex_rates.pdf")

    def test_empty_source_document_raises_error(self):
        """Test that empty source_document raises ValueError."""
        with pytest.raises(ValueError):
            PriceResult(Decimal("25.50"), "FedEx 2Day", Zone(5), Weight(3), "")

    def test_empty_currency_raises_error(self):
        """Test that empty currency raises ValueError."""
        with pytest.raises(ValueError):
            PriceResult(
                Decimal("25.50"),
                "FedEx 2Day",
                Zone(5),
                Weight(3),
                "fedex_rates.pdf",
                currency="",
            )

    def test_non_decimal_price_raises_error(self):
        """Test that non-Decimal price raises TypeError."""
        with pytest.raises(TypeError):
            PriceResult(25.50, "FedEx 2Day", Zone(5), Weight(3), "fedex_rates.pdf")

    def test_non_string_service_type_raises_error(self):
        """Test that non-string service_type raises TypeError."""
        with pytest.raises(TypeError):
            PriceResult(Decimal("25.50"), 123, Zone(5), Weight(3), "fedex_rates.pdf")

    def test_non_zone_zone_raises_error(self):
        """Test that non-Zone zone raises TypeError."""
        with pytest.raises(TypeError):
            PriceResult(Decimal("25.50"), "FedEx 2Day", 5, Weight(3), "fedex_rates.pdf")

    def test_non_weight_weight_raises_error(self):
        """Test that non-Weight weight raises TypeError."""
        with pytest.raises(TypeError):
            PriceResult(Decimal("25.50"), "FedEx 2Day", Zone(5), 3, "fedex_rates.pdf")

    def test_non_string_source_document_raises_error(self):
        """Test that non-string source_document raises TypeError."""
        with pytest.raises(TypeError):
            PriceResult(Decimal("25.50"), "FedEx 2Day", Zone(5), Weight(3), 123)


class TestPriceResultEquality:
    """Test PriceResult equality based on identity."""

    def test_same_id_entities_are_equal(self):
        """Test that entities with same id are equal."""
        result1 = PriceResult(
            Decimal("25.50"),
            "FedEx 2Day",
            Zone(5),
            Weight(3),
            "fedex_rates.pdf",
            id="same-id",
        )
        result2 = PriceResult(
            Decimal("30.00"),
            "Express Saver",
            Zone(6),
            Weight(5),
            "other.pdf",
            id="same-id",
        )
        assert result1 == result2

    def test_different_id_entities_are_not_equal(self):
        """Test that entities with different ids are not equal."""
        result1 = PriceResult(
            Decimal("25.50"),
            "FedEx 2Day",
            Zone(5),
            Weight(3),
            "fedex_rates.pdf",
            id="id-1",
        )
        result2 = PriceResult(
            Decimal("25.50"),
            "FedEx 2Day",
            Zone(5),
            Weight(3),
            "fedex_rates.pdf",
            id="id-2",
        )
        assert result1 != result2

    def test_entity_not_equal_to_non_entity(self):
        """Test that entity is not equal to non-entity objects."""
        result = PriceResult(
            Decimal("25.50"), "FedEx 2Day", Zone(5), Weight(3), "fedex_rates.pdf"
        )
        assert result != "PriceResult"
        assert result != 25.50

    def test_same_id_entities_have_same_hash(self):
        """Test that entities with same id have same hash."""
        result1 = PriceResult(
            Decimal("25.50"),
            "FedEx 2Day",
            Zone(5),
            Weight(3),
            "fedex_rates.pdf",
            id="same-id",
        )
        result2 = PriceResult(
            Decimal("30.00"),
            "Express Saver",
            Zone(6),
            Weight(5),
            "other.pdf",
            id="same-id",
        )
        assert hash(result1) == hash(result2)

    def test_entities_can_be_used_in_sets(self):
        """Test that entities can be used in sets."""
        result1 = PriceResult(
            Decimal("25.50"),
            "FedEx 2Day",
            Zone(5),
            Weight(3),
            "fedex_rates.pdf",
            id="id-1",
        )
        result2 = PriceResult(
            Decimal("25.50"),
            "FedEx 2Day",
            Zone(5),
            Weight(3),
            "fedex_rates.pdf",
            id="id-1",
        )
        result3 = PriceResult(
            Decimal("30.00"),
            "Express Saver",
            Zone(6),
            Weight(5),
            "other.pdf",
            id="id-2",
        )

        results = {result1, result2, result3}
        assert len(results) == 2


class TestPriceResultStringRepresentation:
    """Test PriceResult string representations."""

    def test_str_representation(self):
        """Test __str__ method."""
        result = PriceResult(
            Decimal("25.50"), "FedEx 2Day", Zone(5), Weight(3), "fedex_rates.pdf"
        )
        result_str = str(result)
        assert "FedEx 2Day" in result_str
        assert "USD" in result_str
        assert "25.50" in result_str
        assert "Zone 5" in result_str
        assert "3 lb" in result_str

    def test_repr_representation(self):
        """Test __repr__ method."""
        result = PriceResult(
            Decimal("25.50"), "FedEx 2Day", Zone(5), Weight(3), "fedex_rates.pdf"
        )
        result_repr = repr(result)
        assert "PriceResult" in result_repr
        assert result.id in result_repr
        assert "25.50" in result_repr


class TestPriceResultMutability:
    """Test PriceResult mutability (entities can be mutable)."""

    def test_can_modify_price(self):
        """Test that price can be modified (entities are mutable)."""
        result = PriceResult(
            Decimal("25.50"), "FedEx 2Day", Zone(5), Weight(3), "fedex_rates.pdf"
        )
        result.price = Decimal("30.00")
        assert result.price == Decimal("30.00")

    def test_can_modify_service_type(self):
        """Test that service_type can be modified."""
        result = PriceResult(
            Decimal("25.50"), "FedEx 2Day", Zone(5), Weight(3), "fedex_rates.pdf"
        )
        result.service_type = "Express Saver"
        assert result.service_type == "Express Saver"

    def test_id_should_not_be_modified(self):
        """Test that id should remain stable (by convention)."""
        result = PriceResult(
            Decimal("25.50"), "FedEx 2Day", Zone(5), Weight(3), "fedex_rates.pdf"
        )
        original_id = result.id
        # While technically we can modify id, we shouldn't
        # This test just documents the behavior
        result.id = "new-id"
        assert result.id == "new-id"
        # In production, consider making id read-only with @property
