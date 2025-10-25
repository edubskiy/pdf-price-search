"""
Weight value object for package weights.

This module implements an immutable value object representing package weights,
following Domain-Driven Design principles.
"""

import re
from decimal import Decimal, InvalidOperation
from typing import Union

from ..exceptions import InvalidWeightException


class Weight:
    """
    Immutable value object representing a package weight.

    Weights are stored as Decimal values in pounds to ensure precision.
    Can be parsed from various formats:
    - "3 lb", "3lb"
    - "10 lbs", "10 lbs"
    - "1.5 lb", "1.5lb"
    - "2.75 lbs"
    - Numeric: 5.0, 10

    Attributes:
        value: The weight in pounds as a Decimal.
        pounds: Alias for value (for clarity).
    """

    value: Decimal
    pounds: Decimal

    def __init__(self, value: Union[Decimal, float, int]) -> None:
        """
        Initialize a Weight value object.

        Args:
            value: The weight in pounds (must be positive).

        Raises:
            InvalidWeightException: If the weight is not positive or invalid type.
        """
        # Convert to Decimal for precision
        try:
            if isinstance(value, Decimal):
                decimal_value = value
            elif isinstance(value, (int, float)):
                decimal_value = Decimal(str(value))
            else:
                raise InvalidWeightException(
                    str(value),
                    f"Weight must be numeric, got {type(value).__name__}",
                )
        except (InvalidOperation, ValueError) as e:
            raise InvalidWeightException(
                str(value), f"Cannot convert to decimal: {e}"
            ) from e

        if decimal_value <= 0:
            raise InvalidWeightException(
                str(value), "Weight must be positive (greater than 0)"
            )

        # Use object.__setattr__ to bypass immutability for initialization
        object.__setattr__(self, "value", decimal_value)
        object.__setattr__(self, "pounds", decimal_value)

    @classmethod
    def parse(cls, weight_str: Union[str, int, float, Decimal]) -> "Weight":
        """
        Parse a weight from various string formats or numeric value.

        Supported formats:
        - "3 lb", "3lb"
        - "10 lbs", "10 lbs"
        - "1.5 lb"
        - "2.75lbs"
        - 5.0 (float)
        - 10 (int)
        - Decimal("3.5")

        Args:
            weight_str: The weight string or numeric value to parse.

        Returns:
            A Weight value object.

        Raises:
            InvalidWeightException: If the weight cannot be parsed or is invalid.
        """
        # Handle numeric types directly
        if isinstance(weight_str, (int, float, Decimal)):
            return cls(weight_str)

        if not isinstance(weight_str, str):
            raise InvalidWeightException(
                str(weight_str),
                f"Expected string or numeric type, got {type(weight_str).__name__}",
            )

        # Clean up the string
        cleaned = weight_str.strip()

        if not cleaned:
            raise InvalidWeightException(weight_str, "Empty weight string")

        # Pattern to match weight with optional unit
        # Matches: "3 lb", "3lb", "3.5 lbs", "3.5lbs", "3", "3.5"
        pattern = r"^([\d.]+)\s*(lb|lbs|pound|pounds)?$"

        match = re.match(pattern, cleaned, re.IGNORECASE)
        if not match:
            raise InvalidWeightException(
                weight_str,
                "Format not recognized. Expected formats: '3 lb', '3.5 lbs', or numeric value",
            )

        weight_value = match.group(1)

        try:
            return cls(Decimal(weight_value))
        except (InvalidOperation, ValueError) as e:
            raise InvalidWeightException(
                weight_str, f"Cannot convert '{weight_value}' to decimal: {e}"
            ) from e

    def __eq__(self, other: object) -> bool:
        """
        Check equality with another Weight.

        Args:
            other: The object to compare with.

        Returns:
            True if both weights have the same value, False otherwise.
        """
        if not isinstance(other, Weight):
            return NotImplemented
        return self.value == other.value

    def __hash__(self) -> int:
        """
        Generate hash for the Weight.

        Returns:
            Hash value based on the weight.
        """
        return hash(self.value)

    def __repr__(self) -> str:
        """
        Get unambiguous string representation.

        Returns:
            String representation for debugging.
        """
        return f"Weight(value={self.value})"

    def __str__(self) -> str:
        """
        Get human-readable string representation.

        Returns:
            Human-readable string (e.g., "3.5 lb").
        """
        return f"{self.value} lb"

    def __setattr__(self, name: str, value: object) -> None:
        """
        Prevent attribute modification to ensure immutability.

        Raises:
            AttributeError: Always, as Weight is immutable.
        """
        raise AttributeError("Weight is immutable")

    def __delattr__(self, name: str) -> None:
        """
        Prevent attribute deletion to ensure immutability.

        Raises:
            AttributeError: Always, as Weight is immutable.
        """
        raise AttributeError("Weight is immutable")
