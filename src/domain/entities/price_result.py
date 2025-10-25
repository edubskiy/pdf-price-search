"""
PriceResult entity for shipping price results.

This module implements an entity representing the result of a price lookup,
following Domain-Driven Design principles.
"""

import uuid
from datetime import datetime
from decimal import Decimal
from typing import Optional

from ..value_objects.zone import Zone
from ..value_objects.weight import Weight


class PriceResult:
    """
    Entity representing the result of a shipping price lookup.

    Unlike value objects, entities have identity (id) and lifecycle.
    Two PriceResults with the same price but different IDs are different entities.

    Attributes:
        id: Unique identifier (UUID string).
        price: The shipping price as a Decimal.
        currency: Currency code (default "USD").
        service_type: The shipping service name.
        zone: The Zone value object.
        weight: The Weight value object.
        source_document: Reference to the source PDF or data file.
        timestamp: When this result was created.
    """

    def __init__(
        self,
        price: Decimal,
        service_type: str,
        zone: Zone,
        weight: Weight,
        source_document: str,
        currency: str = "USD",
        id: Optional[str] = None,
        timestamp: Optional[datetime] = None,
    ) -> None:
        """
        Initialize a PriceResult entity.

        Args:
            price: The shipping price (must be non-negative).
            service_type: The shipping service name.
            zone: The Zone value object.
            weight: The Weight value object.
            source_document: Reference to source file (e.g., "fedex_rates_2024.pdf").
            currency: Currency code (default "USD").
            id: Optional unique identifier (UUID generated if not provided).
            timestamp: Optional timestamp (current time if not provided).

        Raises:
            TypeError: If arguments have incorrect types.
            ValueError: If price is negative or strings are empty.
        """
        # Validate types
        if not isinstance(price, Decimal):
            raise TypeError(f"price must be a Decimal, got {type(price).__name__}")

        if not isinstance(service_type, str):
            raise TypeError(
                f"service_type must be a string, got {type(service_type).__name__}"
            )

        if not isinstance(zone, Zone):
            raise TypeError(f"zone must be a Zone instance, got {type(zone).__name__}")

        if not isinstance(weight, Weight):
            raise TypeError(
                f"weight must be a Weight instance, got {type(weight).__name__}"
            )

        if not isinstance(source_document, str):
            raise TypeError(
                f"source_document must be a string, got {type(source_document).__name__}"
            )

        if not isinstance(currency, str):
            raise TypeError(f"currency must be a string, got {type(currency).__name__}")

        # Validate values
        if price < 0:
            raise ValueError(f"price must be non-negative, got {price}")

        if not service_type.strip():
            raise ValueError("service_type cannot be empty")

        if not source_document.strip():
            raise ValueError("source_document cannot be empty")

        if not currency.strip():
            raise ValueError("currency cannot be empty")

        # Set attributes
        self.id = id if id is not None else str(uuid.uuid4())
        self.price = price
        self.currency = currency.strip().upper()
        self.service_type = service_type.strip()
        self.zone = zone
        self.weight = weight
        self.source_document = source_document.strip()
        self.timestamp = timestamp if timestamp is not None else datetime.utcnow()

    def __eq__(self, other: object) -> bool:
        """
        Check equality based on entity identity (id).

        Args:
            other: The object to compare with.

        Returns:
            True if both entities have the same id, False otherwise.
        """
        if not isinstance(other, PriceResult):
            return NotImplemented
        return self.id == other.id

    def __hash__(self) -> int:
        """
        Generate hash based on entity identity.

        Returns:
            Hash value based on the id.
        """
        return hash(self.id)

    def __repr__(self) -> str:
        """
        Get unambiguous string representation.

        Returns:
            String representation for debugging.
        """
        return (
            f"PriceResult(id='{self.id}', "
            f"price={self.price}, "
            f"currency='{self.currency}', "
            f"service_type='{self.service_type}', "
            f"zone={self.zone!r}, "
            f"weight={self.weight!r}, "
            f"source_document='{self.source_document}', "
            f"timestamp={self.timestamp.isoformat()})"
        )

    def __str__(self) -> str:
        """
        Get human-readable string representation.

        Returns:
            Human-readable string describing the result.
        """
        return (
            f"{self.service_type}: {self.currency} {self.price} "
            f"({self.zone}, {self.weight})"
        )
