"""
Unit tests for Weight value object.
"""

import pytest
from decimal import Decimal

from src.domain.value_objects.weight import Weight
from src.domain.exceptions import InvalidWeightException


class TestWeightInitialization:
    """Test Weight initialization and validation."""

    def test_create_weight_with_decimal(self):
        """Test creating weight with Decimal value."""
        weight = Weight(Decimal("3.5"))
        assert weight.value == Decimal("3.5")

    def test_create_weight_with_float(self):
        """Test creating weight with float value."""
        weight = Weight(3.5)
        assert weight.value == Decimal("3.5")

    def test_create_weight_with_int(self):
        """Test creating weight with integer value."""
        weight = Weight(5)
        assert weight.value == Decimal("5")

    @pytest.mark.parametrize(
        "value", [1, 1.5, 10, 100, 0.1, 0.01, 999.99, Decimal("2.5")]
    )
    def test_create_weight_with_valid_values(self, value):
        """Test creating weights with various valid values."""
        weight = Weight(value)
        assert weight.value > 0

    def test_create_weight_with_zero_raises_exception(self):
        """Test that zero weight raises InvalidWeightException."""
        with pytest.raises(InvalidWeightException) as exc_info:
            Weight(0)
        assert "positive" in str(exc_info.value).lower()

    def test_create_weight_with_negative_raises_exception(self):
        """Test that negative weight raises InvalidWeightException."""
        with pytest.raises(InvalidWeightException):
            Weight(-5)

    def test_create_weight_with_invalid_type_raises_exception(self):
        """Test that invalid type raises InvalidWeightException."""
        with pytest.raises(InvalidWeightException):
            Weight("5")

    def test_weight_has_pounds_alias(self):
        """Test that weight has a pounds attribute as alias."""
        weight = Weight(3.5)
        assert weight.pounds == weight.value
        assert weight.pounds == Decimal("3.5")


class TestWeightParsing:
    """Test Weight.parse() method with various formats."""

    @pytest.mark.parametrize(
        "weight_str,expected",
        [
            ("3 lb", Decimal("3")),
            ("3lb", Decimal("3")),
            ("10 lbs", Decimal("10")),
            ("10lbs", Decimal("10")),
            ("1.5 lb", Decimal("1.5")),
            ("1.5lb", Decimal("1.5")),
            ("2.75 lbs", Decimal("2.75")),
            ("2.75lbs", Decimal("2.75")),
            ("3 pound", Decimal("3")),
            ("3 pounds", Decimal("3")),
            ("5", Decimal("5")),
            ("5.5", Decimal("5.5")),
            ("0.5", Decimal("0.5")),
            ("100.25", Decimal("100.25")),
            (5, Decimal("5")),  # Integer
            (5.5, Decimal("5.5")),  # Float
            (Decimal("3.5"), Decimal("3.5")),  # Decimal
        ],
    )
    def test_parse_valid_weight_formats(self, weight_str, expected):
        """Test parsing various valid weight formats."""
        weight = Weight.parse(weight_str)
        assert weight.value == expected

    @pytest.mark.parametrize(
        "invalid_str",
        [
            "0 lb",
            "0",
            "-5 lb",
            "-5",
            "abc",
            "lb",
            "",
            "  ",
            "5 kg",  # Wrong unit
            "5 g",
        ],
    )
    def test_parse_invalid_weight_formats_raises_exception(self, invalid_str):
        """Test that invalid weight formats raise InvalidWeightException."""
        with pytest.raises(InvalidWeightException):
            Weight.parse(invalid_str)

    def test_parse_with_whitespace(self):
        """Test parsing with extra whitespace."""
        weight = Weight.parse("  3.5 lb  ")
        assert weight.value == Decimal("3.5")

    def test_parse_case_insensitive_units(self):
        """Test that unit parsing is case-insensitive."""
        weight1 = Weight.parse("3 LB")
        weight2 = Weight.parse("3 Lb")
        weight3 = Weight.parse("3 LBS")
        assert weight1.value == Decimal("3")
        assert weight2.value == Decimal("3")
        assert weight3.value == Decimal("3")

    def test_parse_non_string_non_numeric_raises_exception(self):
        """Test that non-string/non-numeric input raises exception."""
        with pytest.raises(InvalidWeightException):
            Weight.parse([5])

        with pytest.raises(InvalidWeightException):
            Weight.parse({"weight": 5})


class TestWeightEquality:
    """Test Weight equality and hashing."""

    def test_equal_weights_are_equal(self):
        """Test that weights with the same value are equal."""
        weight1 = Weight(Decimal("3.5"))
        weight2 = Weight(Decimal("3.5"))
        assert weight1 == weight2

    def test_weights_from_different_sources_are_equal(self):
        """Test that weights created from different sources but same value are equal."""
        weight1 = Weight(3.5)
        weight2 = Weight(Decimal("3.5"))
        weight3 = Weight.parse("3.5 lb")
        assert weight1 == weight2
        assert weight2 == weight3

    def test_different_weights_are_not_equal(self):
        """Test that weights with different values are not equal."""
        weight1 = Weight(3.5)
        weight2 = Weight(4.5)
        assert weight1 != weight2

    def test_weight_not_equal_to_non_weight(self):
        """Test that weight is not equal to non-weight objects."""
        weight = Weight(3.5)
        assert weight != 3.5
        assert weight != Decimal("3.5")
        assert weight != "3.5 lb"

    def test_equal_weights_have_same_hash(self):
        """Test that equal weights have the same hash."""
        weight1 = Weight(Decimal("3.5"))
        weight2 = Weight(Decimal("3.5"))
        assert hash(weight1) == hash(weight2)

    def test_weights_can_be_used_in_sets(self):
        """Test that weights can be used in sets."""
        weights = {Weight(1), Weight(2), Weight(1), Weight(3.5)}
        assert len(weights) == 3
        assert Weight(1) in weights

    def test_weights_can_be_used_as_dict_keys(self):
        """Test that weights can be used as dictionary keys."""
        weight_dict = {Weight(1): "one", Weight(2): "two"}
        assert weight_dict[Weight(1)] == "one"


class TestWeightImmutability:
    """Test that Weight is immutable."""

    def test_cannot_modify_value_attribute(self):
        """Test that the value attribute cannot be modified."""
        weight = Weight(3.5)
        with pytest.raises(AttributeError):
            weight.value = 4.5

    def test_cannot_modify_pounds_attribute(self):
        """Test that the pounds attribute cannot be modified."""
        weight = Weight(3.5)
        with pytest.raises(AttributeError):
            weight.pounds = 4.5

    def test_cannot_add_new_attributes(self):
        """Test that new attributes cannot be added."""
        weight = Weight(3.5)
        with pytest.raises(AttributeError):
            weight.new_attr = "test"

    def test_cannot_delete_attributes(self):
        """Test that attributes cannot be deleted."""
        weight = Weight(3.5)
        with pytest.raises(AttributeError):
            del weight.value


class TestWeightStringRepresentation:
    """Test Weight string representations."""

    def test_str_representation(self):
        """Test __str__ method."""
        weight = Weight(3.5)
        assert str(weight) == "3.5 lb"

    def test_str_representation_integer_weight(self):
        """Test __str__ method with integer weight."""
        weight = Weight(5)
        assert str(weight) == "5 lb"

    def test_repr_representation(self):
        """Test __repr__ method."""
        weight = Weight(3.5)
        assert repr(weight) == "Weight(value=3.5)"

    @pytest.mark.parametrize("value", [1, 2.5, 10, 100.25])
    def test_str_for_various_values(self, value):
        """Test __str__ for various weight values."""
        weight = Weight(value)
        assert " lb" in str(weight)


class TestWeightPrecision:
    """Test Weight decimal precision."""

    def test_weight_maintains_decimal_precision(self):
        """Test that weight maintains decimal precision."""
        weight = Weight(Decimal("3.123456"))
        assert weight.value == Decimal("3.123456")

    def test_parse_maintains_precision(self):
        """Test that parsing maintains precision."""
        weight = Weight.parse("3.123456 lb")
        assert weight.value == Decimal("3.123456")

    def test_float_conversion_precision(self):
        """Test precision when converting from float."""
        # Note: floats have limited precision
        weight = Weight(3.14)
        # Should be close to 3.14, but may have floating point artifacts
        assert abs(float(weight.value) - 3.14) < 0.0001
