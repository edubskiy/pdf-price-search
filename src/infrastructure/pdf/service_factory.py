"""
Service factory for creating domain objects from infrastructure data.

This module provides the factory that converts infrastructure data models
(ServicePriceData) into domain objects (ShippingService).
"""

import logging
from decimal import Decimal
from typing import Dict, List

from ...domain import ShippingService, Zone, Weight
from .models import ServicePriceData

logger = logging.getLogger(__name__)


class ServiceFactory:
    """
    Factory for creating ShippingService domain objects.

    This factory handles the conversion from infrastructure layer
    data models to domain layer objects, ensuring proper validation
    and mapping.
    """

    # Service variant mappings (canonical name -> list of variants)
    SERVICE_VARIANTS: Dict[str, List[str]] = {
        "FedEx First Overnight": [
            "FedEx First Overnight",
            "First Overnight",
            "FO",
        ],
        "FedEx Priority Overnight": [
            "FedEx Priority Overnight",
            "Priority Overnight",
            "PO",
        ],
        "FedEx Standard Overnight": [
            "FedEx Standard Overnight",
            "Standard Overnight",
            "SO",
        ],
        "FedEx 2Day A.M.": [
            "FedEx 2Day A.M.",
            "FedEx 2Day AM",
            "2Day A.M.",
            "2Day AM",
        ],
        "FedEx 2Day": [
            "FedEx 2Day",
            "2Day",
            "FedEx Second Day",
        ],
        "FedEx Express Saver": [
            "FedEx Express Saver",
            "Express Saver",
            "ES",
        ],
        "FedEx Ground": [
            "FedEx Ground",
            "Ground",
        ],
    }

    def create_shipping_service(
        self, service_data: ServicePriceData
    ) -> ShippingService:
        """
        Create a ShippingService domain object from ServicePriceData.

        Args:
            service_data: The ServicePriceData from infrastructure layer.

        Returns:
            ShippingService domain object.

        Raises:
            ValueError: If service_data is invalid.
        """
        if not service_data.service_name:
            raise ValueError("service_name cannot be empty")

        # Get variants for this service
        variants = self.SERVICE_VARIANTS.get(service_data.service_name, [])

        # Create the ShippingService
        service = ShippingService(
            service_name=service_data.service_name,
            service_variants=variants.copy(),
        )

        # Add prices from service_data
        for zone_num, weight_prices in service_data.zone_prices.items():
            try:
                zone = Zone(zone_num)
            except Exception as e:
                logger.warning(
                    f"Invalid zone {zone_num} for service "
                    f"{service_data.service_name}: {e}"
                )
                continue

            for weight_str, price in weight_prices.items():
                try:
                    # Convert weight string to Decimal
                    weight_value = Decimal(weight_str)
                    weight = Weight(weight_value)

                    # Add price to service
                    service.set_price(zone, weight, price)

                except Exception as e:
                    logger.warning(
                        f"Error adding price for {service_data.service_name} "
                        f"zone {zone_num} weight {weight_str}: {e}"
                    )
                    continue

        logger.debug(
            f"Created ShippingService: {service_data.service_name} "
            f"with {sum(len(w) for w in service.price_table.values())} prices"
        )

        return service

    def create_shipping_services(
        self, service_data_list: List[ServicePriceData]
    ) -> List[ShippingService]:
        """
        Create multiple ShippingService objects.

        Args:
            service_data_list: List of ServicePriceData objects.

        Returns:
            List of ShippingService domain objects.
        """
        services: List[ShippingService] = []

        for service_data in service_data_list:
            try:
                service = self.create_shipping_service(service_data)
                services.append(service)
            except Exception as e:
                logger.error(
                    f"Failed to create service from {service_data.service_name}: {e}"
                )
                continue

        return services

    def add_custom_variant(self, service_name: str, variant: str) -> None:
        """
        Add a custom variant for a service.

        Args:
            service_name: The canonical service name.
            variant: The variant to add.
        """
        if service_name not in self.SERVICE_VARIANTS:
            self.SERVICE_VARIANTS[service_name] = [service_name]

        if variant not in self.SERVICE_VARIANTS[service_name]:
            self.SERVICE_VARIANTS[service_name].append(variant)
