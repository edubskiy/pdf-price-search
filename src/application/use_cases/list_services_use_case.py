"""
List Services Use Case.

This module implements the use case for listing available shipping services.
"""

import logging
from typing import List

from ..services.price_search_service import PriceSearchService
from ..dto import ServiceInfo
from ..exceptions import DataNotLoadedException

logger = logging.getLogger(__name__)


class ListServicesUseCase:
    """
    Use case for listing available shipping services.

    This use case retrieves metadata about all available services,
    including zones, weight ranges, and source documents.
    """

    def __init__(self, search_service: PriceSearchService) -> None:
        """
        Initialize the use case.

        Args:
            search_service: The price search service.
        """
        self.search_service = search_service

    def execute(self) -> List[ServiceInfo]:
        """
        Execute the list services operation.

        Returns:
            List of ServiceInfo objects describing available services.

        Raises:
            DataNotLoadedException: If no data is loaded.
        """
        logger.info("Executing list services use case")

        # Check if data is loaded
        if not self.search_service.is_data_loaded():
            logger.warning("No data loaded when attempting to list services")
            raise DataNotLoadedException()

        # Get service information
        services = self.search_service.get_available_services()

        logger.info(f"Found {len(services)} services")

        # Log service details
        for service in services:
            logger.debug(
                f"Service: {service.name}, "
                f"Zones: {service.available_zones}, "
                f"Weight: {service.min_weight}-{service.max_weight} lb"
            )

        return services

    def execute_summary(self) -> dict:
        """
        Execute and return a summary of available services.

        Returns:
            Dictionary with summary statistics.

        Raises:
            DataNotLoadedException: If no data is loaded.
        """
        logger.info("Executing list services summary")

        services = self.execute()

        # Calculate summary statistics
        total_services = len(services)

        all_zones = set()
        min_weight = float('inf')
        max_weight = float('-inf')

        for service in services:
            all_zones.update(service.available_zones)
            min_weight = min(min_weight, service.min_weight)
            max_weight = max(max_weight, service.max_weight)

        # Handle edge case of no services
        if total_services == 0:
            min_weight = 0.0
            max_weight = 0.0

        summary = {
            "total_services": total_services,
            "available_zones": sorted(all_zones),
            "weight_range": {
                "min": min_weight,
                "max": max_weight
            },
            "services": [
                {
                    "name": s.name,
                    "zones": len(s.available_zones),
                    "weight_range": f"{s.min_weight}-{s.max_weight} lb"
                }
                for s in services
            ]
        }

        logger.info(f"Service summary: {total_services} services, {len(all_zones)} zones")

        return summary

    def get_service_by_name(self, service_name: str) -> ServiceInfo:
        """
        Get information about a specific service.

        Args:
            service_name: The service name to look up.

        Returns:
            ServiceInfo for the requested service.

        Raises:
            ValueError: If the service is not found.
            DataNotLoadedException: If no data is loaded.
        """
        logger.debug(f"Looking up service: {service_name}")

        services = self.execute()

        # Search for the service (case-insensitive)
        service_name_lower = service_name.lower()
        for service in services:
            if service.name.lower() == service_name_lower:
                logger.debug(f"Found service: {service.name}")
                return service

        # Not found
        available_names = [s.name for s in services]
        logger.warning(f"Service not found: {service_name}")
        raise ValueError(
            f"Service '{service_name}' not found. "
            f"Available services: {', '.join(available_names[:5])}"
        )
