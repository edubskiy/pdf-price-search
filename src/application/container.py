"""
Dependency Injection Container.

This module provides a container for managing application dependencies
and wiring up the dependency graph.
"""

import logging
from typing import Optional

from ..domain.services.query_parser import QueryParser
from ..domain.services.service_matcher import ServiceMatcher
from ..infrastructure.pdf.repository import PDFPriceRepository
from ..infrastructure.pdf.pdf_parser import PDFParser
from ..infrastructure.pdf.service_factory import ServiceFactory
from ..infrastructure.cache.price_cache import PriceCache

from .config import AppConfig
from .services.pdf_loader_service import PDFLoaderService
from .services.price_search_service import PriceSearchService
from .use_cases.search_price_use_case import SearchPriceUseCase
from .use_cases.list_services_use_case import ListServicesUseCase
from .use_cases.load_data_use_case import LoadDataUseCase

logger = logging.getLogger(__name__)


class Container:
    """
    Dependency injection container.

    This container manages the creation and lifecycle of application
    components, implementing the Service Locator pattern with
    lazy initialization and singleton management.
    """

    def __init__(self, config: Optional[AppConfig] = None) -> None:
        """
        Initialize the container.

        Args:
            config: Optional application configuration (creates new if None).
        """
        # Configuration
        self._config = config or AppConfig()

        # Infrastructure layer - Singletons
        self._pdf_parser: Optional[PDFParser] = None
        self._service_factory: Optional[ServiceFactory] = None
        self._repository: Optional[PDFPriceRepository] = None
        self._cache: Optional[PriceCache] = None

        # Domain layer - Singletons
        self._query_parser: Optional[QueryParser] = None
        self._service_matcher: Optional[ServiceMatcher] = None

        # Application layer - Singletons
        self._pdf_loader_service: Optional[PDFLoaderService] = None
        self._price_search_service: Optional[PriceSearchService] = None

        # Use cases - New instances
        # (Could be singletons, but new instances allow for better testability)

        logger.debug("Container initialized")

    # Configuration

    def config(self) -> AppConfig:
        """
        Get the application configuration.

        Returns:
            The AppConfig instance.
        """
        return self._config

    # Infrastructure Layer

    def pdf_parser(self) -> PDFParser:
        """
        Get the PDF parser instance.

        Returns:
            Singleton PDFParser instance.
        """
        if self._pdf_parser is None:
            logger.debug("Creating PDFParser instance")
            self._pdf_parser = PDFParser()
        return self._pdf_parser

    def service_factory(self) -> ServiceFactory:
        """
        Get the service factory instance.

        Returns:
            Singleton ServiceFactory instance.
        """
        if self._service_factory is None:
            logger.debug("Creating ServiceFactory instance")
            self._service_factory = ServiceFactory()
        return self._service_factory

    def repository(self) -> PDFPriceRepository:
        """
        Get the repository instance.

        Returns:
            Singleton PDFPriceRepository instance.
        """
        if self._repository is None:
            logger.debug("Creating PDFPriceRepository instance")
            self._repository = PDFPriceRepository(
                pdf_parser=self.pdf_parser(),
                service_factory=self.service_factory()
            )
        return self._repository

    def cache(self) -> Optional[PriceCache]:
        """
        Get the cache instance.

        Returns:
            Singleton PriceCache instance if caching is enabled, None otherwise.
        """
        if not self._config.enable_cache:
            return None

        if self._cache is None:
            logger.debug("Creating PriceCache instance")
            self._cache = PriceCache(default_ttl=self._config.cache_ttl)

        return self._cache

    # Domain Layer

    def query_parser(self) -> QueryParser:
        """
        Get the query parser instance.

        Returns:
            Singleton QueryParser instance.
        """
        if self._query_parser is None:
            logger.debug("Creating QueryParser instance")
            self._query_parser = QueryParser()
        return self._query_parser

    def service_matcher(self) -> ServiceMatcher:
        """
        Get the service matcher instance.

        Returns:
            Singleton ServiceMatcher instance.
        """
        if self._service_matcher is None:
            logger.debug("Creating ServiceMatcher instance")
            self._service_matcher = ServiceMatcher()
        return self._service_matcher

    # Application Layer - Services

    def pdf_loader_service(self) -> PDFLoaderService:
        """
        Get the PDF loader service instance.

        Returns:
            Singleton PDFLoaderService instance.
        """
        if self._pdf_loader_service is None:
            logger.debug("Creating PDFLoaderService instance")
            self._pdf_loader_service = PDFLoaderService(
                repository=self.repository(),
                config=self._config
            )
        return self._pdf_loader_service

    def price_search_service(self) -> PriceSearchService:
        """
        Get the price search service instance.

        Returns:
            Singleton PriceSearchService instance.
        """
        if self._price_search_service is None:
            logger.debug("Creating PriceSearchService instance")
            self._price_search_service = PriceSearchService(
                repository=self.repository(),
                query_parser=self.query_parser(),
                service_matcher=self.service_matcher(),
                cache=self.cache()
            )
        return self._price_search_service

    # Application Layer - Use Cases

    def search_price_use_case(self) -> SearchPriceUseCase:
        """
        Create a new search price use case instance.

        Returns:
            New SearchPriceUseCase instance.
        """
        logger.debug("Creating SearchPriceUseCase instance")
        return SearchPriceUseCase(
            search_service=self.price_search_service()
        )

    def list_services_use_case(self) -> ListServicesUseCase:
        """
        Create a new list services use case instance.

        Returns:
            New ListServicesUseCase instance.
        """
        logger.debug("Creating ListServicesUseCase instance")
        return ListServicesUseCase(
            search_service=self.price_search_service()
        )

    def load_data_use_case(self) -> LoadDataUseCase:
        """
        Create a new load data use case instance.

        Returns:
            New LoadDataUseCase instance.
        """
        logger.debug("Creating LoadDataUseCase instance")
        return LoadDataUseCase(
            loader_service=self.pdf_loader_service()
        )

    # Container Management

    def reset(self) -> None:
        """
        Reset all singleton instances.

        This is primarily useful for testing purposes.
        """
        logger.info("Resetting container")

        self._pdf_parser = None
        self._service_factory = None
        self._repository = None
        self._cache = None
        self._query_parser = None
        self._service_matcher = None
        self._pdf_loader_service = None
        self._price_search_service = None

    def validate(self) -> list[str]:
        """
        Validate the container configuration.

        Returns:
            List of validation error messages (empty if valid).
        """
        logger.debug("Validating container configuration")
        return self._config.validate()

    def ensure_ready(self) -> None:
        """
        Ensure the container is ready for use.

        This creates necessary directories and validates configuration.

        Raises:
            ValueError: If configuration is invalid.
        """
        logger.info("Ensuring container is ready")

        # Validate configuration
        errors = self.validate()
        if errors:
            error_msg = f"Configuration validation failed: {'; '.join(errors)}"
            logger.error(error_msg)
            raise ValueError(error_msg)

        # Ensure directories exist
        self._config.ensure_directories()

        logger.info("Container is ready")


# Global container instance
_global_container: Optional[Container] = None


def get_container(config: Optional[AppConfig] = None) -> Container:
    """
    Get the global container instance.

    Args:
        config: Optional configuration (only used on first call).

    Returns:
        The global Container instance.
    """
    global _global_container

    if _global_container is None:
        _global_container = Container(config=config)

    return _global_container


def reset_container() -> None:
    """
    Reset the global container instance.

    This is primarily useful for testing purposes.
    """
    global _global_container
    _global_container = None
