"""
Zone value object for shipping zones.

This module implements an immutable value object representing shipping zones (1-8),
following Domain-Driven Design principles.
"""

import re
from typing import Union

from ..exceptions import InvalidZoneException


class Zone:
    """
    Immutable value object representing a shipping zone.

    Zones are normalized to integer values (1-8) and can be parsed from various formats:
    - "z2", "Z2"
    - "zone 5", "Zone 5", "ZONE 5"
    - "zone 3", "zone3"
    - "Z8", "z8"
    - Integer: 5
    - String: "5"

    Attributes:
        value: The normalized zone number (1-8).
    """

    MIN_ZONE = 1
    MAX_ZONE = 8

    value: int

    def __init__(self, value: int) -> None:
        """
        Initialize a Zone value object.

        Args:
            value: The zone number (must be between 1 and 8).

        Raises:
            InvalidZoneException: If the zone value is not between 1 and 8.
        """
        if not isinstance(value, int):
            raise InvalidZoneException(
                str(value), f"Zone value must be an integer, got {type(value).__name__}"
            )

        if not (self.MIN_ZONE <= value <= self.MAX_ZONE):
            raise InvalidZoneException(
                str(value), f"Zone must be between {self.MIN_ZONE} and {self.MAX_ZONE}"
            )

        # Use object.__setattr__ to bypass immutability for initialization
        object.__setattr__(self, "value", value)

    @classmethod
    def parse(cls, zone_str: Union[str, int]) -> "Zone":
        """
        Parse a zone from various string formats or integer.

        Supported formats:
        - "z2", "Z2"
        - "zone 5", "Zone 5", "ZONE 5"
        - "zone3", "Zone3"
        - "5" (plain number string)
        - 5 (integer)

        Args:
            zone_str: The zone string or integer to parse.

        Returns:
            A Zone value object.

        Raises:
            InvalidZoneException: If the zone cannot be parsed or is invalid.
        """
        if isinstance(zone_str, int):
            return cls(zone_str)

        if not isinstance(zone_str, str):
            raise InvalidZoneException(
                str(zone_str), f"Expected string or int, got {type(zone_str).__name__}"
            )

        # Clean up the string
        cleaned = zone_str.strip()

        if not cleaned:
            raise InvalidZoneException(zone_str, "Empty zone string")

        # Try different patterns
        patterns = [
            r"^z(\d+)$",  # z2, Z8
            r"^zone\s*(\d+)$",  # zone 5, zone5, Zone 3
            r"^(\d+)$",  # 5
        ]

        for pattern in patterns:
            match = re.match(pattern, cleaned, re.IGNORECASE)
            if match:
                try:
                    zone_number = int(match.group(1))
                    return cls(zone_number)
                except ValueError as e:
                    raise InvalidZoneException(
                        zone_str, f"Cannot convert '{match.group(1)}' to integer"
                    ) from e

        raise InvalidZoneException(
            zone_str, "Format not recognized. Expected formats: 'z2', 'zone 5', or '5'"
        )

    def __eq__(self, other: object) -> bool:
        """
        Check equality with another Zone.

        Args:
            other: The object to compare with.

        Returns:
            True if both zones have the same value, False otherwise.
        """
        if not isinstance(other, Zone):
            return NotImplemented
        return self.value == other.value

    def __hash__(self) -> int:
        """
        Generate hash for the Zone.

        Returns:
            Hash value based on the zone number.
        """
        return hash(self.value)

    def __repr__(self) -> str:
        """
        Get unambiguous string representation.

        Returns:
            String representation for debugging.
        """
        return f"Zone(value={self.value})"

    def __str__(self) -> str:
        """
        Get human-readable string representation.

        Returns:
            Human-readable string (e.g., "Zone 5").
        """
        return f"Zone {self.value}"

    def __setattr__(self, name: str, value: object) -> None:
        """
        Prevent attribute modification to ensure immutability.

        Raises:
            AttributeError: Always, as Zone is immutable.
        """
        raise AttributeError("Zone is immutable")

    def __delattr__(self, name: str) -> None:
        """
        Prevent attribute deletion to ensure immutability.

        Raises:
            AttributeError: Always, as Zone is immutable.
        """
        raise AttributeError("Zone is immutable")
