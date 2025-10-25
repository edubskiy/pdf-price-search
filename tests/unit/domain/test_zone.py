"""
Unit tests for Zone value object.
"""

import pytest

from src.domain.value_objects.zone import Zone
from src.domain.exceptions import InvalidZoneException


class TestZoneInitialization:
    """Test Zone initialization and validation."""

    def test_create_zone_with_valid_value(self):
        """Test creating a zone with a valid integer value."""
        zone = Zone(5)
        assert zone.value == 5

    @pytest.mark.parametrize("zone_value", [1, 2, 3, 4, 5, 6, 7, 8])
    def test_create_zone_with_all_valid_values(self, zone_value):
        """Test creating zones with all valid values (1-8)."""
        zone = Zone(zone_value)
        assert zone.value == zone_value

    @pytest.mark.parametrize("invalid_value", [0, 9, 10, -1, -5, 100])
    def test_create_zone_with_invalid_value_raises_exception(self, invalid_value):
        """Test that invalid zone values raise InvalidZoneException."""
        with pytest.raises(InvalidZoneException) as exc_info:
            Zone(invalid_value)
        assert str(invalid_value) in str(exc_info.value)

    def test_create_zone_with_non_integer_raises_exception(self):
        """Test that non-integer values raise InvalidZoneException."""
        with pytest.raises(InvalidZoneException):
            Zone(5.5)

    def test_create_zone_with_string_raises_exception(self):
        """Test that string values in __init__ raise InvalidZoneException."""
        with pytest.raises(InvalidZoneException):
            Zone("5")


class TestZoneParsing:
    """Test Zone.parse() method with various formats."""

    @pytest.mark.parametrize(
        "zone_str,expected",
        [
            ("z2", 2),
            ("Z2", 2),
            ("z8", 8),
            ("Z1", 1),
            ("zone 5", 5),
            ("Zone 5", 5),
            ("ZONE 5", 5),
            ("zone 3", 3),
            ("zone3", 3),
            ("Zone7", 7),
            ("5", 5),
            ("1", 1),
            ("8", 8),
            (5, 5),  # Integer input
            (1, 1),
        ],
    )
    def test_parse_valid_zone_formats(self, zone_str, expected):
        """Test parsing various valid zone formats."""
        zone = Zone.parse(zone_str)
        assert zone.value == expected

    @pytest.mark.parametrize(
        "invalid_str",
        [
            "z0",
            "z9",
            "zone 0",
            "zone 9",
            "zone 10",
            "0",
            "9",
            "abc",
            "zone",
            "z",
            "",
            "  ",
            "zone abc",
            "invalid",
        ],
    )
    def test_parse_invalid_zone_formats_raises_exception(self, invalid_str):
        """Test that invalid zone formats raise InvalidZoneException."""
        with pytest.raises(InvalidZoneException):
            Zone.parse(invalid_str)

    def test_parse_with_whitespace(self):
        """Test parsing with extra whitespace."""
        zone = Zone.parse("  zone 5  ")
        assert zone.value == 5

    def test_parse_non_string_non_int_raises_exception(self):
        """Test that non-string/non-int input raises InvalidZoneException."""
        with pytest.raises(InvalidZoneException):
            Zone.parse(5.5)

        with pytest.raises(InvalidZoneException):
            Zone.parse([5])


class TestZoneEquality:
    """Test Zone equality and hashing."""

    def test_equal_zones_are_equal(self):
        """Test that zones with the same value are equal."""
        zone1 = Zone(5)
        zone2 = Zone(5)
        assert zone1 == zone2

    def test_different_zones_are_not_equal(self):
        """Test that zones with different values are not equal."""
        zone1 = Zone(5)
        zone2 = Zone(6)
        assert zone1 != zone2

    def test_zone_not_equal_to_non_zone(self):
        """Test that zone is not equal to non-zone objects."""
        zone = Zone(5)
        assert zone != 5
        assert zone != "5"
        assert zone != "Zone 5"

    def test_equal_zones_have_same_hash(self):
        """Test that equal zones have the same hash."""
        zone1 = Zone(5)
        zone2 = Zone(5)
        assert hash(zone1) == hash(zone2)

    def test_zones_can_be_used_in_sets(self):
        """Test that zones can be used in sets."""
        zones = {Zone(1), Zone(2), Zone(1), Zone(3)}
        assert len(zones) == 3
        assert Zone(1) in zones

    def test_zones_can_be_used_as_dict_keys(self):
        """Test that zones can be used as dictionary keys."""
        zone_dict = {Zone(1): "first", Zone(2): "second"}
        assert zone_dict[Zone(1)] == "first"
        assert zone_dict[Zone(2)] == "second"


class TestZoneImmutability:
    """Test that Zone is immutable."""

    def test_cannot_modify_value_attribute(self):
        """Test that the value attribute cannot be modified."""
        zone = Zone(5)
        with pytest.raises(AttributeError):
            zone.value = 6

    def test_cannot_add_new_attributes(self):
        """Test that new attributes cannot be added."""
        zone = Zone(5)
        with pytest.raises(AttributeError):
            zone.new_attr = "test"

    def test_cannot_delete_attributes(self):
        """Test that attributes cannot be deleted."""
        zone = Zone(5)
        with pytest.raises(AttributeError):
            del zone.value


class TestZoneStringRepresentation:
    """Test Zone string representations."""

    def test_str_representation(self):
        """Test __str__ method."""
        zone = Zone(5)
        assert str(zone) == "Zone 5"

    def test_repr_representation(self):
        """Test __repr__ method."""
        zone = Zone(5)
        assert repr(zone) == "Zone(value=5)"

    @pytest.mark.parametrize("value", [1, 2, 3, 4, 5, 6, 7, 8])
    def test_str_for_all_values(self, value):
        """Test __str__ for all valid zone values."""
        zone = Zone(value)
        assert str(zone) == f"Zone {value}"
