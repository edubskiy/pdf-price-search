"""
Price Search Service.

This module provides the main orchestration service for price searches.
"""

import logging
import time
from decimal import Decimal
from typing import List, Optional

from ...domain.services.query_parser import QueryParser
from ...domain.services.service_matcher import ServiceMatcher
from ...domain.exceptions import InvalidQueryException, PriceNotFoundException
from ...infrastructure.pdf.repository import PriceRepositoryInterface
from ...infrastructure.cache.price_cache import PriceCache

from ..dto import SearchRequest, SearchResponse, ServiceInfo
from ..exceptions import (
    SearchException,
    ServiceNotAvailableException,
    DataNotLoadedException,
)

logger = logging.getLogger(__name__)


class PriceSearchService:
    """
    Main orchestration service for price searches.

    This service coordinates the complete search flow:
    1. Parse query using QueryParser
    2. Load/get services from repository
    3. Match service using ServiceMatcher
    4. Get price from matched service
    5. Return formatted response

    It also manages caching and error handling.
    """

    def __init__(
        self,
        repository: PriceRepositoryInterface,
        query_parser: QueryParser,
        service_matcher: ServiceMatcher,
        cache: Optional[PriceCache] = None,
    ) -> None:
        """
        Initialize the price search service.

        Args:
            repository: The repository to access price data.
            query_parser: Service to parse queries.
            service_matcher: Service to match service names.
            cache: Optional cache for search results.
        """
        self.repository = repository
        self.query_parser = query_parser
        self.service_matcher = service_matcher
        self.cache = cache

    def search(self, request: SearchRequest) -> SearchResponse:
        """
        Execute a price search.

        This is the main entry point for searching prices.
        It orchestrates the entire search flow and handles errors.

        Args:
            request: The search request.

        Returns:
            SearchResponse with the result or error.
        """
        start_time = time.time()

        try:
            logger.info(f"Searching for: {request.query}")

            # Check if we have any data loaded
            if self.repository.get_service_count() == 0:
                raise DataNotLoadedException()

            # Check cache if enabled
            if request.use_cache and self.cache is not None:
                cached_result = self._check_cache(request.query)
                if cached_result is not None:
                    search_time_ms = (time.time() - start_time) * 1000
                    logger.info(f"Cache hit for query: {request.query}")
                    cached_result.search_time_ms = search_time_ms
                    return cached_result

            # Parse the query
            try:
                price_query = self.query_parser.parse(request.query)
                logger.debug(f"Parsed query: {price_query}")
            except InvalidQueryException as e:
                search_time_ms = (time.time() - start_time) * 1000
                logger.warning(f"Invalid query: {request.query} - {e}")
                return SearchResponse.error_response(
                    error_message=f"Invalid query: {e.reason}",
                    search_time_ms=search_time_ms
                )

            # Get available services
            available_services = self.repository.get_all_services()

            if not available_services:
                raise DataNotLoadedException()

            # Match the service
            matched_service = self.service_matcher.match_service(
                price_query.service_type,
                available_services
            )

            # If no exact match and service is generic/default, try first available service
            if matched_service is None:
                # Check if this is a generic query (e.g., "Standard" from "2lb to zone 5")
                if price_query.service_type.lower() in ["standard", "default", "generic"]:
                    logger.info(f"Generic service query, using first available service")
                    matched_service = available_services[0] if available_services else None

            if matched_service is None:
                # Get available service names for error message
                service_names = [s.service_name for s in available_services]
                raise ServiceNotAvailableException(
                    price_query.service_type,
                    service_names
                )

            logger.debug(f"Matched service: {matched_service.service_name}")

            # Get the price
            try:
                price = matched_service.get_price(
                    price_query.zone,
                    price_query.weight
                )
            except PriceNotFoundException as e:
                search_time_ms = (time.time() - start_time) * 1000
                logger.warning(f"Price not found: {e}")
                return SearchResponse.error_response(
                    error_message=str(e),
                    search_time_ms=search_time_ms
                )

            # Create success response
            search_time_ms = (time.time() - start_time) * 1000

            response = SearchResponse.success_response(
                price=price,
                service=matched_service.service_name,
                zone=price_query.zone.value,
                weight=float(price_query.weight.value),
                source_document="loaded_pdf",  # Could track actual source
                search_time_ms=search_time_ms
            )

            # Cache the result if enabled
            if request.use_cache and self.cache is not None:
                self._cache_result(request.query, response)

            logger.info(
                f"Search successful: {matched_service.service_name}, "
                f"Zone {price_query.zone.value}, "
                f"{price_query.weight.value} lb = ${price}"
            )

            return response

        except (DataNotLoadedException, ServiceNotAvailableException) as e:
            search_time_ms = (time.time() - start_time) * 1000
            logger.warning(f"Search failed: {e}")
            return SearchResponse.error_response(
                error_message=str(e),
                search_time_ms=search_time_ms
            )

        except Exception as e:
            search_time_ms = (time.time() - start_time) * 1000
            logger.error(f"Unexpected error during search: {e}", exc_info=True)
            return SearchResponse.error_response(
                error_message=f"Internal error: {str(e)}",
                search_time_ms=search_time_ms
            )

    def get_available_services(self) -> List[ServiceInfo]:
        """
        Get information about all available services.

        Returns:
            List of ServiceInfo objects describing available services.
        """
        logger.debug("Getting available services")

        services = self.repository.get_all_services()

        service_infos = []
        for service in services:
            # Extract zone and weight information from price table
            zones = sorted(service.price_table.keys())

            # Calculate weight range
            weights = []
            for zone_prices in service.price_table.values():
                for weight_str in zone_prices.keys():
                    try:
                        weights.append(float(weight_str))
                    except (ValueError, TypeError):
                        continue

            if not weights:
                min_weight = 0.0
                max_weight = 0.0
            else:
                min_weight = min(weights)
                max_weight = max(weights)

            service_info = ServiceInfo(
                name=service.service_name,
                available_zones=zones,
                weight_range=(min_weight, max_weight),
                source_pdf="loaded_pdf"  # Could track actual source
            )

            service_infos.append(service_info)

        logger.info(f"Found {len(service_infos)} available services")
        return service_infos

    def load_pdf_data(self, pdf_path: str) -> None:
        """
        Load price data from a PDF file.

        Args:
            pdf_path: Path to the PDF file.

        Raises:
            PDFLoadException: If loading fails.
        """
        logger.info(f"Loading price data from: {pdf_path}")
        self.repository.load_from_pdf(pdf_path)

    def clear_cache(self) -> None:
        """Clear the search cache."""
        if self.cache is not None:
            self.cache.clear()
            logger.info("Search cache cleared")
        else:
            logger.debug("No cache to clear")

    def _check_cache(self, query: str) -> Optional[SearchResponse]:
        """
        Check if a query result is in the cache.

        Args:
            query: The query string.

        Returns:
            Cached SearchResponse or None if not found.
        """
        if self.cache is None:
            return None

        try:
            cache_key = self._make_cache_key(query)
            cached = self.cache.get(cache_key)

            if cached is not None and isinstance(cached, SearchResponse):
                return cached

            return None

        except Exception as e:
            logger.warning(f"Cache check failed: {e}")
            return None

    def _cache_result(self, query: str, response: SearchResponse) -> None:
        """
        Cache a search result.

        Args:
            query: The query string.
            response: The response to cache.
        """
        if self.cache is None:
            return

        try:
            cache_key = self._make_cache_key(query)
            self.cache.set(cache_key, response)
            logger.debug(f"Cached result for query: {query}")

        except Exception as e:
            logger.warning(f"Failed to cache result: {e}")

    def _make_cache_key(self, query: str) -> str:
        """
        Create a cache key from a query.

        Args:
            query: The query string.

        Returns:
            A cache key string.
        """
        # Normalize query for cache key
        normalized = query.strip().lower()
        return f"search:{normalized}"

    def get_service_count(self) -> int:
        """
        Get the count of loaded services.

        Returns:
            Number of services currently loaded.
        """
        return self.repository.get_service_count()

    def is_data_loaded(self) -> bool:
        """
        Check if any price data is loaded.

        Returns:
            True if data is loaded, False otherwise.
        """
        return self.repository.get_service_count() > 0
