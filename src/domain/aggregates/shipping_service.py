"""
ShippingService aggregate root.

This module implements the ShippingService aggregate root, which encapsulates
shipping service data and price lookup logic, following Domain-Driven Design principles.
"""

from decimal import Decimal
from typing import Dict, List, Optional

from ..value_objects.zone import Zone
from ..value_objects.weight import Weight
from ..exceptions import PriceNotFoundException


class ShippingService:
    """
    Aggregate root representing a shipping service with its price table.

    This is the main entry point for working with shipping service data.
    It encapsulates the service name, variants (aliases), and price table.

    Attributes:
        service_name: The canonical name of the service (e.g., "FedEx 2Day").
        service_variants: List of service name aliases/variations.
        price_table: Nested dict mapping zone -> weight -> price.
    """

    def __init__(
        self,
        service_name: str,
        service_variants: Optional[List[str]] = None,
        price_table: Optional[Dict[int, Dict[str, Decimal]]] = None,
    ) -> None:
        """
        Initialize a ShippingService aggregate.

        Args:
            service_name: The canonical name of the service.
            service_variants: Optional list of service name variants/aliases.
            price_table: Optional price table (zone -> weight -> price).

        Raises:
            TypeError: If arguments have incorrect types.
            ValueError: If service_name is empty.
        """
        if not isinstance(service_name, str):
            raise TypeError(
                f"service_name must be a string, got {type(service_name).__name__}"
            )

        if not service_name.strip():
            raise ValueError("service_name cannot be empty")

        if service_variants is not None and not isinstance(service_variants, list):
            raise TypeError(
                f"service_variants must be a list or None, got {type(service_variants).__name__}"
            )

        if price_table is not None and not isinstance(price_table, dict):
            raise TypeError(
                f"price_table must be a dict or None, got {type(price_table).__name__}"
            )

        self.service_name = service_name.strip()
        self.service_variants = service_variants if service_variants else []
        self.price_table = price_table if price_table else {}

    def get_price(self, zone: Zone, weight: Weight) -> Decimal:
        """
        Get the price for a specific zone and weight.

        This method looks up the price in the price table. The implementation
        may need to handle weight ranges or exact matches depending on the
        price table structure.

        Args:
            zone: The Zone value object.
            weight: The Weight value object.

        Returns:
            The price as a Decimal.

        Raises:
            PriceNotFoundException: If no price is found for the zone/weight combination.
            TypeError: If arguments have incorrect types.
        """
        if not isinstance(zone, Zone):
            raise TypeError(f"zone must be a Zone instance, got {type(zone).__name__}")

        if not isinstance(weight, Weight):
            raise TypeError(
                f"weight must be a Weight instance, got {type(weight).__name__}"
            )

        # Check if zone exists in price table
        if zone.value not in self.price_table:
            raise PriceNotFoundException(
                self.service_name, zone.value, float(weight.value)
            )

        zone_prices = self.price_table[zone.value]

        # Try to find exact weight match first
        weight_key = str(weight.value)
        if weight_key in zone_prices:
            return zone_prices[weight_key]

        # Try to find weight with different formatting (e.g., "3.0" vs "3")
        # Convert to float for comparison
        weight_float = float(weight.value)
        for key, price in zone_prices.items():
            try:
                if float(key) == weight_float:
                    return price
            except (ValueError, TypeError):
                continue

        # No matching price found
        raise PriceNotFoundException(self.service_name, zone.value, float(weight.value))

    def is_service_match(self, query_service: str) -> bool:
        """
        Check if a query service name matches this service.

        This method checks if the query matches the canonical service name
        or any of the service variants (case-insensitive).

        Args:
            query_service: The service name from the query.

        Returns:
            True if the query matches this service, False otherwise.

        Raises:
            TypeError: If query_service is not a string.
        """
        if not isinstance(query_service, str):
            raise TypeError(
                f"query_service must be a string, got {type(query_service).__name__}"
            )

        query_normalized = query_service.strip().lower()

        # Check canonical name
        if self.service_name.lower() == query_normalized:
            return True

        # Check variants
        for variant in self.service_variants:
            if variant.lower() == query_normalized:
                return True

        return False

    def add_variant(self, variant: str) -> None:
        """
        Add a service name variant/alias.

        Args:
            variant: The variant name to add.

        Raises:
            TypeError: If variant is not a string.
            ValueError: If variant is empty or already exists.
        """
        if not isinstance(variant, str):
            raise TypeError(f"variant must be a string, got {type(variant).__name__}")

        variant = variant.strip()
        if not variant:
            raise ValueError("variant cannot be empty")

        if variant in self.service_variants:
            raise ValueError(f"variant '{variant}' already exists")

        self.service_variants.append(variant)

    def set_price(self, zone: Zone, weight: Weight, price: Decimal) -> None:
        """
        Set the price for a specific zone and weight.

        Args:
            zone: The Zone value object.
            weight: The Weight value object.
            price: The price as a Decimal.

        Raises:
            TypeError: If arguments have incorrect types.
            ValueError: If price is negative.
        """
        if not isinstance(zone, Zone):
            raise TypeError(f"zone must be a Zone instance, got {type(zone).__name__}")

        if not isinstance(weight, Weight):
            raise TypeError(
                f"weight must be a Weight instance, got {type(weight).__name__}"
            )

        if not isinstance(price, Decimal):
            raise TypeError(f"price must be a Decimal, got {type(price).__name__}")

        if price < 0:
            raise ValueError(f"price must be non-negative, got {price}")

        # Ensure zone exists in price table
        if zone.value not in self.price_table:
            self.price_table[zone.value] = {}

        # Set the price using string representation of weight
        self.price_table[zone.value][str(weight.value)] = price

    def __repr__(self) -> str:
        """
        Get unambiguous string representation.

        Returns:
            String representation for debugging.
        """
        return (
            f"ShippingService(service_name='{self.service_name}', "
            f"variants={self.service_variants}, "
            f"price_entries={sum(len(weights) for weights in self.price_table.values())})"
        )

    def __str__(self) -> str:
        """
        Get human-readable string representation.

        Returns:
            Human-readable string describing the service.
        """
        return f"{self.service_name}"
