"""
Unit tests for ShippingService aggregate root.
"""

import pytest
from decimal import Decimal

from src.domain.aggregates.shipping_service import ShippingService
from src.domain.value_objects.zone import Zone
from src.domain.value_objects.weight import Weight
from src.domain.exceptions import PriceNotFoundException


class TestShippingServiceCreation:
    """Test ShippingService creation and initialization."""

    def test_create_service_with_minimal_args(self):
        """Test creating a service with minimal arguments."""
        service = ShippingService(service_name="FedEx 2Day")
        assert service.service_name == "FedEx 2Day"
        assert service.service_variants == []
        assert service.price_table == {}

    def test_create_service_with_variants(self):
        """Test creating a service with variants."""
        service = ShippingService(
            service_name="FedEx 2Day",
            service_variants=["2Day", "2-Day", "FedEx Two Day"],
        )
        assert service.service_name == "FedEx 2Day"
        assert len(service.service_variants) == 3
        assert "2Day" in service.service_variants

    def test_create_service_with_price_table(self):
        """Test creating a service with a price table."""
        price_table = {
            5: {"3": Decimal("25.50"), "5": Decimal("30.00")},
            6: {"3": Decimal("28.50"), "5": Decimal("33.00")},
        }
        service = ShippingService(service_name="FedEx 2Day", price_table=price_table)
        assert service.price_table == price_table

    def test_service_name_is_stripped(self):
        """Test that service_name whitespace is stripped."""
        service = ShippingService(service_name="  FedEx 2Day  ")
        assert service.service_name == "FedEx 2Day"


class TestShippingServiceValidation:
    """Test ShippingService validation."""

    def test_empty_service_name_raises_error(self):
        """Test that empty service_name raises ValueError."""
        with pytest.raises(ValueError):
            ShippingService(service_name="")

    def test_whitespace_service_name_raises_error(self):
        """Test that whitespace-only service_name raises ValueError."""
        with pytest.raises(ValueError):
            ShippingService(service_name="   ")

    def test_non_string_service_name_raises_error(self):
        """Test that non-string service_name raises TypeError."""
        with pytest.raises(TypeError):
            ShippingService(service_name=123)

    def test_non_list_variants_raises_error(self):
        """Test that non-list service_variants raises TypeError."""
        with pytest.raises(TypeError):
            ShippingService(service_name="FedEx 2Day", service_variants="2Day")

    def test_non_dict_price_table_raises_error(self):
        """Test that non-dict price_table raises TypeError."""
        with pytest.raises(TypeError):
            ShippingService(service_name="FedEx 2Day", price_table="invalid")


class TestShippingServiceGetPrice:
    """Test ShippingService.get_price() method."""

    def test_get_price_exact_match(self):
        """Test getting price with exact match."""
        price_table = {5: {"3": Decimal("25.50")}}
        service = ShippingService(service_name="FedEx 2Day", price_table=price_table)

        price = service.get_price(Zone(5), Weight(3))
        assert price == Decimal("25.50")

    def test_get_price_with_decimal_weight(self):
        """Test getting price with decimal weight."""
        price_table = {5: {"3.5": Decimal("27.00")}}
        service = ShippingService(service_name="FedEx 2Day", price_table=price_table)

        price = service.get_price(Zone(5), Weight(Decimal("3.5")))
        assert price == Decimal("27.00")

    def test_get_price_float_equivalence(self):
        """Test that float-equivalent weights match (e.g., '3.0' matches '3')."""
        price_table = {5: {"3.0": Decimal("25.50")}}
        service = ShippingService(service_name="FedEx 2Day", price_table=price_table)

        price = service.get_price(Zone(5), Weight(3))
        assert price == Decimal("25.50")

    def test_get_price_zone_not_found_raises_error(self):
        """Test that missing zone raises PriceNotFoundException."""
        price_table = {5: {"3": Decimal("25.50")}}
        service = ShippingService(service_name="FedEx 2Day", price_table=price_table)

        with pytest.raises(PriceNotFoundException) as exc_info:
            service.get_price(Zone(6), Weight(3))
        assert "6" in str(exc_info.value)

    def test_get_price_weight_not_found_raises_error(self):
        """Test that missing weight raises PriceNotFoundException."""
        price_table = {5: {"3": Decimal("25.50")}}
        service = ShippingService(service_name="FedEx 2Day", price_table=price_table)

        with pytest.raises(PriceNotFoundException) as exc_info:
            service.get_price(Zone(5), Weight(5))
        assert "5" in str(exc_info.value)

    def test_get_price_empty_price_table_raises_error(self):
        """Test that empty price table raises PriceNotFoundException."""
        service = ShippingService(service_name="FedEx 2Day")

        with pytest.raises(PriceNotFoundException):
            service.get_price(Zone(5), Weight(3))

    def test_get_price_non_zone_raises_error(self):
        """Test that non-Zone argument raises TypeError."""
        service = ShippingService(service_name="FedEx 2Day")

        with pytest.raises(TypeError):
            service.get_price(5, Weight(3))

    def test_get_price_non_weight_raises_error(self):
        """Test that non-Weight argument raises TypeError."""
        service = ShippingService(service_name="FedEx 2Day")

        with pytest.raises(TypeError):
            service.get_price(Zone(5), 3)


class TestShippingServiceIsServiceMatch:
    """Test ShippingService.is_service_match() method."""

    def test_exact_match_canonical_name(self):
        """Test exact match with canonical name."""
        service = ShippingService(service_name="FedEx 2Day")
        assert service.is_service_match("FedEx 2Day")

    def test_case_insensitive_match(self):
        """Test case-insensitive matching."""
        service = ShippingService(service_name="FedEx 2Day")
        assert service.is_service_match("fedex 2day")
        assert service.is_service_match("FEDEX 2DAY")

    def test_match_with_variant(self):
        """Test matching with service variant."""
        service = ShippingService(
            service_name="FedEx 2Day", service_variants=["2Day", "2-Day"]
        )
        assert service.is_service_match("2Day")
        assert service.is_service_match("2-Day")

    def test_match_variant_case_insensitive(self):
        """Test variant matching is case-insensitive."""
        service = ShippingService(service_name="FedEx 2Day", service_variants=["2Day"])
        assert service.is_service_match("2day")
        assert service.is_service_match("2DAY")

    def test_no_match_returns_false(self):
        """Test that non-matching service returns False."""
        service = ShippingService(service_name="FedEx 2Day")
        assert not service.is_service_match("Express Saver")

    def test_match_with_whitespace(self):
        """Test matching with whitespace."""
        service = ShippingService(service_name="FedEx 2Day")
        assert service.is_service_match("  FedEx 2Day  ")

    def test_non_string_query_raises_error(self):
        """Test that non-string query raises TypeError."""
        service = ShippingService(service_name="FedEx 2Day")
        with pytest.raises(TypeError):
            service.is_service_match(123)


class TestShippingServiceAddVariant:
    """Test ShippingService.add_variant() method."""

    def test_add_variant(self):
        """Test adding a variant."""
        service = ShippingService(service_name="FedEx 2Day")
        service.add_variant("2Day")
        assert "2Day" in service.service_variants

    def test_add_multiple_variants(self):
        """Test adding multiple variants."""
        service = ShippingService(service_name="FedEx 2Day")
        service.add_variant("2Day")
        service.add_variant("2-Day")
        assert len(service.service_variants) == 2

    def test_add_duplicate_variant_raises_error(self):
        """Test that adding duplicate variant raises ValueError."""
        service = ShippingService(service_name="FedEx 2Day")
        service.add_variant("2Day")
        with pytest.raises(ValueError) as exc_info:
            service.add_variant("2Day")
        assert "already exists" in str(exc_info.value)

    def test_add_empty_variant_raises_error(self):
        """Test that adding empty variant raises ValueError."""
        service = ShippingService(service_name="FedEx 2Day")
        with pytest.raises(ValueError):
            service.add_variant("")

    def test_add_whitespace_variant_raises_error(self):
        """Test that adding whitespace-only variant raises ValueError."""
        service = ShippingService(service_name="FedEx 2Day")
        with pytest.raises(ValueError):
            service.add_variant("   ")

    def test_add_non_string_variant_raises_error(self):
        """Test that adding non-string variant raises TypeError."""
        service = ShippingService(service_name="FedEx 2Day")
        with pytest.raises(TypeError):
            service.add_variant(123)


class TestShippingServiceSetPrice:
    """Test ShippingService.set_price() method."""

    def test_set_price_creates_entry(self):
        """Test that set_price creates a price entry."""
        service = ShippingService(service_name="FedEx 2Day")
        service.set_price(Zone(5), Weight(3), Decimal("25.50"))

        price = service.get_price(Zone(5), Weight(3))
        assert price == Decimal("25.50")

    def test_set_price_creates_zone_if_not_exists(self):
        """Test that set_price creates zone in price table if it doesn't exist."""
        service = ShippingService(service_name="FedEx 2Day")
        service.set_price(Zone(5), Weight(3), Decimal("25.50"))

        assert 5 in service.price_table

    def test_set_price_updates_existing_price(self):
        """Test that set_price updates existing price."""
        service = ShippingService(service_name="FedEx 2Day")
        service.set_price(Zone(5), Weight(3), Decimal("25.50"))
        service.set_price(Zone(5), Weight(3), Decimal("30.00"))

        price = service.get_price(Zone(5), Weight(3))
        assert price == Decimal("30.00")

    def test_set_price_negative_raises_error(self):
        """Test that setting negative price raises ValueError."""
        service = ShippingService(service_name="FedEx 2Day")
        with pytest.raises(ValueError):
            service.set_price(Zone(5), Weight(3), Decimal("-25.50"))

    def test_set_price_zero_is_allowed(self):
        """Test that zero price is allowed."""
        service = ShippingService(service_name="FedEx 2Day")
        service.set_price(Zone(5), Weight(3), Decimal("0"))

        price = service.get_price(Zone(5), Weight(3))
        assert price == Decimal("0")

    def test_set_price_non_zone_raises_error(self):
        """Test that non-Zone argument raises TypeError."""
        service = ShippingService(service_name="FedEx 2Day")
        with pytest.raises(TypeError):
            service.set_price(5, Weight(3), Decimal("25.50"))

    def test_set_price_non_weight_raises_error(self):
        """Test that non-Weight argument raises TypeError."""
        service = ShippingService(service_name="FedEx 2Day")
        with pytest.raises(TypeError):
            service.set_price(Zone(5), 3, Decimal("25.50"))

    def test_set_price_non_decimal_raises_error(self):
        """Test that non-Decimal price raises TypeError."""
        service = ShippingService(service_name="FedEx 2Day")
        with pytest.raises(TypeError):
            service.set_price(Zone(5), Weight(3), 25.50)


class TestShippingServiceStringRepresentation:
    """Test ShippingService string representations."""

    def test_str_representation(self):
        """Test __str__ method."""
        service = ShippingService(service_name="FedEx 2Day")
        assert str(service) == "FedEx 2Day"

    def test_repr_representation(self):
        """Test __repr__ method."""
        service = ShippingService(
            service_name="FedEx 2Day",
            service_variants=["2Day", "2-Day"],
        )
        service.set_price(Zone(5), Weight(3), Decimal("25.50"))
        service.set_price(Zone(5), Weight(5), Decimal("30.00"))

        result = repr(service)
        assert "ShippingService" in result
        assert "FedEx 2Day" in result
        assert "2" in result  # 2 price entries
