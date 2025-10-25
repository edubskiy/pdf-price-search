"""
Repository implementation for price data.

This module provides the repository pattern implementation for loading
and managing shipping service price data from PDF files.
"""

import logging
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Dict, List, Optional

from ...domain import ShippingService
from .pdf_parser import PDFParser
from .service_factory import ServiceFactory

logger = logging.getLogger(__name__)


class PriceRepositoryInterface(ABC):
    """
    Abstract interface for price repository.

    This defines the contract for loading and accessing shipping service
    price data.
    """

    @abstractmethod
    def load_from_pdf(self, file_path: str) -> List[ShippingService]:
        """
        Load shipping services from a PDF file.

        Args:
            file_path: Path to the PDF file.

        Returns:
            List of ShippingService objects.

        Raises:
            Exception: If loading fails.
        """
        pass

    @abstractmethod
    def get_all_services(self) -> List[ShippingService]:
        """
        Get all loaded shipping services.

        Returns:
            List of all ShippingService objects.
        """
        pass

    @abstractmethod
    def get_service(self, service_name: str) -> Optional[ShippingService]:
        """
        Get a specific shipping service by name.

        Args:
            service_name: The service name to look up.

        Returns:
            ShippingService if found, None otherwise.
        """
        pass

    @abstractmethod
    def refresh_data(self) -> None:
        """
        Refresh all data by reloading from source PDFs.

        This clears the current data and reloads from all configured sources.
        """
        pass


class PDFPriceRepository(PriceRepositoryInterface):
    """
    Repository implementation that loads price data from PDF files.

    This implementation uses PDFParser and ServiceFactory to load
    and manage shipping service data.
    """

    def __init__(
        self,
        pdf_parser: Optional[PDFParser] = None,
        service_factory: Optional[ServiceFactory] = None,
    ) -> None:
        """
        Initialize the repository.

        Args:
            pdf_parser: Optional PDFParser instance (creates new if None).
            service_factory: Optional ServiceFactory instance (creates new if None).
        """
        self.pdf_parser = pdf_parser or PDFParser()
        self.service_factory = service_factory or ServiceFactory()

        # Storage for loaded services
        self._services: Dict[str, ShippingService] = {}

        # Track source files for refresh
        self._source_files: List[str] = []

    def load_from_pdf(self, file_path: str) -> List[ShippingService]:
        """
        Load shipping services from a PDF file.

        Args:
            file_path: Path to the PDF file.

        Returns:
            List of ShippingService objects loaded from the PDF.

        Raises:
            FileNotFoundError: If file doesn't exist.
            Exception: If parsing or loading fails.
        """
        logger.info(f"Loading services from PDF: {file_path}")

        # Validate file exists
        path = Path(file_path)
        if not path.exists():
            raise FileNotFoundError(f"PDF file not found: {file_path}")

        # Parse the PDF
        extracted_data = self.pdf_parser.parse_file(file_path)

        # Convert to domain objects
        service_data_list = list(extracted_data.service_data.values())
        services = self.service_factory.create_shipping_services(service_data_list)

        # Store services
        for service in services:
            self._services[service.service_name] = service

        # Track source file
        if file_path not in self._source_files:
            self._source_files.append(file_path)

        logger.info(f"Loaded {len(services)} services from {file_path}")

        return services

    def load_from_multiple_pdfs(self, file_paths: List[str]) -> List[ShippingService]:
        """
        Load shipping services from multiple PDF files.

        Args:
            file_paths: List of paths to PDF files.

        Returns:
            List of all ShippingService objects loaded.
        """
        all_services: List[ShippingService] = []

        for file_path in file_paths:
            try:
                services = self.load_from_pdf(file_path)
                all_services.extend(services)
            except Exception as e:
                logger.error(f"Failed to load {file_path}: {e}")
                continue

        return all_services

    def get_all_services(self) -> List[ShippingService]:
        """
        Get all loaded shipping services.

        Returns:
            List of all ShippingService objects.
        """
        return list(self._services.values())

    def get_service(self, service_name: str) -> Optional[ShippingService]:
        """
        Get a specific shipping service by name.

        This method checks both the canonical name and variants.

        Args:
            service_name: The service name to look up.

        Returns:
            ShippingService if found, None otherwise.
        """
        # First try exact match
        if service_name in self._services:
            return self._services[service_name]

        # Try case-insensitive match
        service_name_lower = service_name.lower()
        for service in self._services.values():
            if service.is_service_match(service_name):
                return service

        return None

    def refresh_data(self) -> None:
        """
        Refresh all data by reloading from source PDFs.

        This clears the current data and reloads from all previously
        loaded source files.
        """
        logger.info("Refreshing repository data")

        # Save source files list
        source_files = self._source_files.copy()

        # Clear current data
        self._services.clear()
        self._source_files.clear()

        # Reload from sources
        for file_path in source_files:
            try:
                self.load_from_pdf(file_path)
            except Exception as e:
                logger.error(f"Failed to reload {file_path}: {e}")
                continue

        logger.info(f"Refreshed {len(self._services)} services")

    def get_service_count(self) -> int:
        """
        Get the count of loaded services.

        Returns:
            Number of services currently loaded.
        """
        return len(self._services)

    def get_service_names(self) -> List[str]:
        """
        Get a list of all service names.

        Returns:
            List of service names (canonical names).
        """
        return sorted(self._services.keys())

    def clear(self) -> None:
        """Clear all loaded data."""
        logger.info("Clearing repository data")
        self._services.clear()
        self._source_files.clear()

    def has_service(self, service_name: str) -> bool:
        """
        Check if a service exists.

        Args:
            service_name: The service name to check.

        Returns:
            True if service exists, False otherwise.
        """
        return self.get_service(service_name) is not None
