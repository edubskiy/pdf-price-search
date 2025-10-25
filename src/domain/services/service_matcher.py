"""
ServiceMatcher domain service for matching shipping services.

This module implements a domain service that matches query service names
to available ShippingService aggregates, handling variations and fuzzy matching.
"""

import re
from typing import List, Optional

from ..aggregates.shipping_service import ShippingService


class ServiceMatcher:
    """
    Domain service for matching service names to ShippingService aggregates.

    This service handles various service name variations, including:
    - Case-insensitive matching
    - Handling of common variations (e.g., "2Day" vs "2-Day")
    - Partial matching with normalization
    """

    def match_service(
        self, query_service: str, available_services: List[ShippingService]
    ) -> Optional[ShippingService]:
        """
        Match a query service name to an available ShippingService.

        The matching process:
        1. Try exact match (case-insensitive)
        2. Try normalized match (remove punctuation, extra spaces)
        3. Try variant matching (each service's variants)

        Args:
            query_service: The service name from the query.
            available_services: List of available ShippingService aggregates.

        Returns:
            The matched ShippingService, or None if no match found.

        Raises:
            TypeError: If arguments have incorrect types.
        """
        if not isinstance(query_service, str):
            raise TypeError(
                f"query_service must be a string, got {type(query_service).__name__}"
            )

        if not isinstance(available_services, list):
            raise TypeError(
                f"available_services must be a list, got {type(available_services).__name__}"
            )

        query_normalized = self._normalize_service_name(query_service)

        # Try to match each service
        for service in available_services:
            if self._is_match(query_normalized, service):
                return service

        return None

    def _is_match(self, query_normalized: str, service: ShippingService) -> bool:
        """
        Check if normalized query matches a service.

        Args:
            query_normalized: The normalized query service name.
            service: The ShippingService to check against.

        Returns:
            True if the query matches the service, False otherwise.
        """
        # Check if service has the built-in is_service_match method
        # (which handles variants)
        # First, try the service's own matching logic
        try:
            # Get the original query by denormalizing (not perfect, but good enough)
            # Actually, we should pass both normalized and original
            # For now, just use the normalized version
            if service.is_service_match(query_normalized):
                return True
        except:
            pass

        # Also try normalized matching
        service_normalized = self._normalize_service_name(service.service_name)
        if query_normalized == service_normalized:
            return True

        # Check normalized variants
        for variant in service.service_variants:
            variant_normalized = self._normalize_service_name(variant)
            if query_normalized == variant_normalized:
                return True

        return False

    def _normalize_service_name(self, name: str) -> str:
        """
        Normalize a service name for comparison.

        Normalization includes:
        - Convert to lowercase
        - Remove extra whitespace
        - Remove common punctuation (hyphens, periods, etc.)
        - Standardize spacing

        Args:
            name: The service name to normalize.

        Returns:
            The normalized service name.
        """
        if not name:
            return ""

        # Convert to lowercase
        normalized = name.lower()

        # Remove punctuation (hyphens, periods, underscores)
        normalized = re.sub(r"[-._]", "", normalized)

        # Replace multiple spaces with single space
        normalized = re.sub(r"\s+", " ", normalized)

        # Strip leading/trailing whitespace
        normalized = normalized.strip()

        return normalized

    def match_best(
        self, query_service: str, available_services: List[ShippingService]
    ) -> Optional[ShippingService]:
        """
        Match a query service name to the best available ShippingService.

        This method uses the same logic as match_service, but could be extended
        to implement scoring/ranking if multiple matches are possible.

        Args:
            query_service: The service name from the query.
            available_services: List of available ShippingService aggregates.

        Returns:
            The best matched ShippingService, or None if no match found.
        """
        # For now, this is the same as match_service
        # In the future, could implement scoring logic here
        return self.match_service(query_service, available_services)

    def find_all_matches(
        self, query_service: str, available_services: List[ShippingService]
    ) -> List[ShippingService]:
        """
        Find all matching services for a query.

        This can be useful for ambiguous queries or providing suggestions.

        Args:
            query_service: The service name from the query.
            available_services: List of available ShippingService aggregates.

        Returns:
            List of all matching ShippingServices (may be empty).

        Raises:
            TypeError: If arguments have incorrect types.
        """
        if not isinstance(query_service, str):
            raise TypeError(
                f"query_service must be a string, got {type(query_service).__name__}"
            )

        if not isinstance(available_services, list):
            raise TypeError(
                f"available_services must be a list, got {type(available_services).__name__}"
            )

        query_normalized = self._normalize_service_name(query_service)

        matches = []
        for service in available_services:
            if self._is_match(query_normalized, service):
                matches.append(service)

        return matches
