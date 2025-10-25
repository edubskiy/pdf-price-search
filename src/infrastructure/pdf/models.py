"""
Infrastructure data models for PDF parsing.

These models represent the raw extracted data from PDFs before
mapping to domain objects. They serve as DTOs (Data Transfer Objects)
between the parser and the domain layer.
"""

from dataclasses import dataclass, field
from decimal import Decimal
from typing import Dict, List, Optional


@dataclass
class PriceTableData:
    """
    Raw price table data extracted from PDF.

    This represents a single table extracted from a PDF, containing
    prices for different services, zones, and weights.

    Attributes:
        zone: The shipping zone (e.g., 2, 3, 4).
        service_columns: List of service names extracted from header.
        weight_prices: Dict mapping weight (as string) to list of prices.
                      Each price corresponds to a service in service_columns.
        page_number: The page number where this table was found.
    """

    zone: int
    service_columns: List[str]
    weight_prices: Dict[str, List[Decimal]]
    page_number: int

    def __post_init__(self) -> None:
        """Validate the data after initialization."""
        if not self.service_columns:
            raise ValueError("service_columns cannot be empty")

        if not self.weight_prices:
            raise ValueError("weight_prices cannot be empty")

        # Validate that each weight has the correct number of prices
        expected_count = len(self.service_columns)
        for weight, prices in self.weight_prices.items():
            if len(prices) != expected_count:
                raise ValueError(
                    f"Weight '{weight}' has {len(prices)} prices but "
                    f"expected {expected_count} (number of service columns)"
                )


@dataclass
class ServicePriceData:
    """
    Structured service price data for a single service across zones.

    This represents all price data for a single service extracted from
    one or more tables.

    Attributes:
        service_name: The canonical name of the service.
        service_variants: List of alternative names/aliases for the service.
        zone_prices: Dict mapping zone number to weight-price dict.
                    Inner dict maps weight (as string) to Decimal price.
    """

    service_name: str
    service_variants: List[str] = field(default_factory=list)
    zone_prices: Dict[int, Dict[str, Decimal]] = field(default_factory=dict)

    def __post_init__(self) -> None:
        """Validate the data after initialization."""
        if not self.service_name.strip():
            raise ValueError("service_name cannot be empty")

    def add_price(self, zone: int, weight: str, price: Decimal) -> None:
        """
        Add a price for a specific zone and weight.

        Args:
            zone: The zone number.
            weight: The weight as a string (e.g., "1", "2.5").
            price: The price as a Decimal.
        """
        if zone not in self.zone_prices:
            self.zone_prices[zone] = {}

        self.zone_prices[zone][weight] = price

    def get_price(self, zone: int, weight: str) -> Optional[Decimal]:
        """
        Get the price for a specific zone and weight.

        Args:
            zone: The zone number.
            weight: The weight as a string.

        Returns:
            The price as a Decimal, or None if not found.
        """
        if zone not in self.zone_prices:
            return None

        return self.zone_prices[zone].get(weight)

    def get_all_zones(self) -> List[int]:
        """Get a list of all zones with prices."""
        return sorted(self.zone_prices.keys())

    def get_weights_for_zone(self, zone: int) -> List[str]:
        """
        Get a list of all weights with prices for a specific zone.

        Args:
            zone: The zone number.

        Returns:
            List of weight strings, sorted numerically.
        """
        if zone not in self.zone_prices:
            return []

        # Sort weights numerically
        weights = self.zone_prices[zone].keys()
        try:
            return sorted(weights, key=lambda w: float(w))
        except (ValueError, TypeError):
            # If conversion fails, sort as strings
            return sorted(weights)


@dataclass
class PDFMetadata:
    """
    Metadata extracted from PDF.

    Attributes:
        file_path: Path to the PDF file.
        title: Title extracted from PDF.
        effective_date: Effective date of the rates (if available).
        total_pages: Total number of pages in the PDF.
        extracted_pages: Number of pages actually processed.
    """

    file_path: str
    title: Optional[str] = None
    effective_date: Optional[str] = None
    total_pages: int = 0
    extracted_pages: int = 0

    def __post_init__(self) -> None:
        """Validate the data after initialization."""
        if not self.file_path.strip():
            raise ValueError("file_path cannot be empty")


@dataclass
class ExtractedPDFData:
    """
    Complete data extracted from a PDF file.

    This is the top-level container for all data extracted from a PDF.

    Attributes:
        metadata: PDF metadata.
        price_tables: List of extracted price tables.
        service_data: Dict mapping service name to ServicePriceData.
    """

    metadata: PDFMetadata
    price_tables: List[PriceTableData] = field(default_factory=list)
    service_data: Dict[str, ServicePriceData] = field(default_factory=dict)

    def add_price_table(self, table: PriceTableData) -> None:
        """
        Add a price table to the extracted data.

        Args:
            table: The PriceTableData to add.
        """
        self.price_tables.append(table)

    def get_service(self, service_name: str) -> Optional[ServicePriceData]:
        """
        Get service price data by name.

        Args:
            service_name: The service name to look up.

        Returns:
            ServicePriceData if found, None otherwise.
        """
        return self.service_data.get(service_name)

    def get_all_service_names(self) -> List[str]:
        """Get a list of all service names in the extracted data."""
        return sorted(self.service_data.keys())

    def add_service_data(self, service_data: ServicePriceData) -> None:
        """
        Add or update service price data.

        Args:
            service_data: The ServicePriceData to add/update.
        """
        self.service_data[service_data.service_name] = service_data
