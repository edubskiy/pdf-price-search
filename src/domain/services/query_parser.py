"""
QueryParser domain service for parsing price queries.

This module implements a domain service that parses natural language queries
into structured PriceQuery value objects, following Domain-Driven Design principles.
"""

import re
from typing import Match, Optional, Tuple

from ..value_objects.zone import Zone
from ..value_objects.weight import Weight
from ..value_objects.price_query import PriceQuery
from ..exceptions import InvalidQueryException


class QueryParser:
    """
    Domain service for parsing price query strings.

    This service converts natural language queries into structured PriceQuery objects.
    It handles various query formats and extracts service type, zone, weight, and
    optional packaging information.

    Supported formats:
    - "FedEx 2Day, Zone 5, 3 lb"
    - "Standard Overnight, z2, 10 lbs, other packaging"
    - "Express Saver Z8 1 lb"
    - "Ground Z6 12 lb"
    - "Home Delivery zone 3 5 lb"
    """

    def parse(self, query: str) -> PriceQuery:
        """
        Parse a query string into a PriceQuery value object.

        This method attempts to extract:
        1. Service type (required)
        2. Zone (required)
        3. Weight (required)
        4. Packaging type (optional)

        Args:
            query: The query string to parse.

        Returns:
            A PriceQuery value object.

        Raises:
            InvalidQueryException: If the query cannot be parsed.
            TypeError: If query is not a string.
        """
        if not isinstance(query, str):
            raise TypeError(f"query must be a string, got {type(query).__name__}")

        query = query.strip()

        if not query:
            raise InvalidQueryException(query, "Empty query string")

        # Try comma-separated format first: "Service, Zone, Weight" or "Service, Zone, Weight, Packaging"
        if "," in query:
            return self._parse_comma_separated(query)

        # Try space-separated format: "Service Zone Weight" or "Service Zone Weight Packaging"
        return self._parse_space_separated(query)

    def _parse_comma_separated(self, query: str) -> PriceQuery:
        """
        Parse comma-separated query format.

        Format: "Service, Zone, Weight[, Packaging]"
        Example: "FedEx 2Day, Zone 5, 3 lb, other packaging"

        Args:
            query: The query string to parse.

        Returns:
            A PriceQuery value object.

        Raises:
            InvalidQueryException: If the query cannot be parsed.
        """
        parts = [p.strip() for p in query.split(",")]

        if len(parts) < 3:
            raise InvalidQueryException(
                query,
                "Comma-separated format requires at least 3 parts: service, zone, weight",
            )

        if len(parts) > 4:
            raise InvalidQueryException(
                query,
                "Comma-separated format supports at most 4 parts: service, zone, weight, packaging",
            )

        service_type = parts[0]
        zone_str = parts[1]
        weight_str = parts[2]
        packaging_type = parts[3] if len(parts) == 4 else None

        if not service_type:
            raise InvalidQueryException(query, "Service type is empty")

        # Parse zone and weight
        try:
            zone = Zone.parse(zone_str)
        except Exception as e:
            raise InvalidQueryException(query, f"Invalid zone: {e}") from e

        try:
            weight = Weight.parse(weight_str)
        except Exception as e:
            raise InvalidQueryException(query, f"Invalid weight: {e}") from e

        return PriceQuery(
            service_type=service_type,
            zone=zone,
            weight=weight,
            packaging_type=packaging_type,
        )

    def _parse_space_separated(self, query: str) -> PriceQuery:
        """
        Parse space-separated query format.

        This format expects the zone and weight to be identifiable by patterns,
        with the service name being everything before the zone.

        Format: "Service Zone Weight [Packaging]"
        Example: "Express Saver Z8 1 lb"

        Args:
            query: The query string to parse.

        Returns:
            A PriceQuery value object.

        Raises:
            InvalidQueryException: If the query cannot be parsed.
        """
        # Extract zone and weight using patterns
        zone_match, weight_match = self._find_zone_and_weight(query)

        if not zone_match:
            raise InvalidQueryException(query, "Cannot find zone in query")

        if not weight_match:
            raise InvalidQueryException(query, "Cannot find weight in query")

        # Determine if weight is before or after zone
        weight_before_zone = weight_match.start() < zone_match.start()

        if weight_before_zone:
            # Weight is before zone: "2lb to zone 5"
            # Service type is before weight
            service_end = weight_match.start()
            service_type = query[:service_end].strip()

            # Packaging is after zone (if any)
            weight_absolute_end = zone_match.end()
            packaging_type = (
                query[weight_absolute_end:].strip()
                if weight_absolute_end < len(query)
                else None
            )
        else:
            # Weight is after zone: "zone 5 2lb" or "Service zone 5 2lb"
            # Service type is before zone
            service_end = zone_match.start()
            service_type = query[:service_end].strip()

            # Calculate absolute position of weight match (it's relative to zone_match.end())
            weight_absolute_end = zone_match.end() + weight_match.end()
            packaging_type = (
                query[weight_absolute_end:].strip()
                if weight_absolute_end < len(query)
                else None
            )

        # If service type is empty, try to infer a default or raise error
        if not service_type:
            # For queries like "2lb to zone 5", use a generic service name
            # This allows the ServiceMatcher to find the best match later
            service_type = "Standard"  # Default service type

        if packaging_type and not packaging_type:
            packaging_type = None

        # Parse zone and weight
        try:
            zone = Zone.parse(zone_match.group(0))
        except Exception as e:
            raise InvalidQueryException(query, f"Invalid zone: {e}") from e

        try:
            weight = Weight.parse(weight_match.group(0))
        except Exception as e:
            raise InvalidQueryException(query, f"Invalid weight: {e}") from e

        return PriceQuery(
            service_type=service_type,
            zone=zone,
            weight=weight,
            packaging_type=packaging_type,
        )

    def _find_zone_and_weight(
        self, query: str
    ) -> Tuple[Optional[Match[str]], Optional[Match[str]]]:
        """
        Find zone and weight patterns in the query string.

        Args:
            query: The query string to search.

        Returns:
            A tuple of (zone_match, weight_match) where each is a regex Match object or None.
        """
        # Zone patterns: z2, Z8, zone 5, Zone 3, etc.
        zone_pattern = r"(?:z|zone)\s*\d+"

        # Weight patterns: 3 lb, 10 lbs, 1.5 lb, 3lb, 2lb, etc.
        # Made lb/lbs/pound/pounds required with \s* to match both "2lb" and "2 lb"
        weight_pattern = r"[\d.]+\s*(?:lb|lbs|pound|pounds)\b"

        zone_match = re.search(zone_pattern, query, re.IGNORECASE)

        # Find weight - search in entire query since it can be before OR after zone
        weight_match = None
        if zone_match:
            # First try to find weight after the zone (preferred location)
            remaining_after = query[zone_match.end() :]
            weight_match = re.search(weight_pattern, remaining_after, re.IGNORECASE)

            # If not found after zone, try before zone (e.g., "2lb to zone 5")
            if not weight_match:
                before_zone = query[: zone_match.start()]
                weight_match = re.search(weight_pattern, before_zone, re.IGNORECASE)

        return zone_match, weight_match
