"""
PriceQuery value object for shipping price queries.

This module implements an immutable composite value object representing
a complete price query, following Domain-Driven Design principles.
"""

from typing import Optional

from .zone import Zone
from .weight import Weight


class PriceQuery:
    """
    Immutable composite value object representing a shipping price query.

    A PriceQuery combines all the information needed to look up a shipping price:
    service type, zone, weight, and optional packaging type.

    Attributes:
        service_type: The shipping service name (e.g., "FedEx 2Day").
        zone: The shipping zone (Zone value object).
        weight: The package weight (Weight value object).
        packaging_type: Optional packaging type (e.g., "other packaging").
    """

    service_type: str
    zone: Zone
    weight: Weight
    packaging_type: Optional[str]

    def __init__(
        self,
        service_type: str,
        zone: Zone,
        weight: Weight,
        packaging_type: Optional[str] = None,
    ) -> None:
        """
        Initialize a PriceQuery value object.

        Args:
            service_type: The shipping service name.
            zone: The Zone value object.
            weight: The Weight value object.
            packaging_type: Optional packaging type specification.

        Raises:
            TypeError: If service_type is not a string, or zone/weight are not value objects.
            ValueError: If service_type is empty.
        """
        if not isinstance(service_type, str):
            raise TypeError(
                f"service_type must be a string, got {type(service_type).__name__}"
            )

        if not service_type.strip():
            raise ValueError("service_type cannot be empty")

        if not isinstance(zone, Zone):
            raise TypeError(f"zone must be a Zone instance, got {type(zone).__name__}")

        if not isinstance(weight, Weight):
            raise TypeError(
                f"weight must be a Weight instance, got {type(weight).__name__}"
            )

        if packaging_type is not None and not isinstance(packaging_type, str):
            raise TypeError(
                f"packaging_type must be a string or None, got {type(packaging_type).__name__}"
            )

        # Use object.__setattr__ to bypass immutability for initialization
        object.__setattr__(self, "service_type", service_type.strip())
        object.__setattr__(self, "zone", zone)
        object.__setattr__(self, "weight", weight)

        # Handle packaging_type - strip and convert empty to None
        cleaned_packaging = packaging_type.strip() if packaging_type else None
        object.__setattr__(
            self, "packaging_type", cleaned_packaging if cleaned_packaging else None
        )

    def __eq__(self, other: object) -> bool:
        """
        Check equality with another PriceQuery.

        Two PriceQueries are equal if all their components are equal.

        Args:
            other: The object to compare with.

        Returns:
            True if all components are equal, False otherwise.
        """
        if not isinstance(other, PriceQuery):
            return NotImplemented

        return (
            self.service_type == other.service_type
            and self.zone == other.zone
            and self.weight == other.weight
            and self.packaging_type == other.packaging_type
        )

    def __hash__(self) -> int:
        """
        Generate hash for the PriceQuery.

        Returns:
            Hash value based on all components.
        """
        return hash((self.service_type, self.zone, self.weight, self.packaging_type))

    def __repr__(self) -> str:
        """
        Get unambiguous string representation.

        Returns:
            String representation for debugging.
        """
        return (
            f"PriceQuery(service_type='{self.service_type}', "
            f"zone={self.zone!r}, "
            f"weight={self.weight!r}, "
            f"packaging_type={self.packaging_type!r})"
        )

    def __str__(self) -> str:
        """
        Get human-readable string representation.

        Returns:
            Human-readable string describing the query.
        """
        base = f"{self.service_type}, {self.zone}, {self.weight}"
        if self.packaging_type:
            base += f", {self.packaging_type}"
        return base

    def __setattr__(self, name: str, value: object) -> None:
        """
        Prevent attribute modification to ensure immutability.

        Raises:
            AttributeError: Always, as PriceQuery is immutable.
        """
        raise AttributeError("PriceQuery is immutable")

    def __delattr__(self, name: str) -> None:
        """
        Prevent attribute deletion to ensure immutability.

        Raises:
            AttributeError: Always, as PriceQuery is immutable.
        """
        raise AttributeError("PriceQuery is immutable")
