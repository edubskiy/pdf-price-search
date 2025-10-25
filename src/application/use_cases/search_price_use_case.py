"""
Search Price Use Case.

This module implements the use case for searching prices.
"""

import logging
import time
from typing import Optional

from ..services.price_search_service import PriceSearchService
from ..dto import SearchRequest, SearchResponse
from ..exceptions import ApplicationException

logger = logging.getLogger(__name__)


class SearchPriceUseCase:
    """
    Use case for searching shipping prices.

    This use case encapsulates the business logic for price searches,
    including validation, logging, and error handling.
    """

    def __init__(self, search_service: PriceSearchService) -> None:
        """
        Initialize the use case.

        Args:
            search_service: The price search service.
        """
        self.search_service = search_service

    def execute(self, query: str, use_cache: bool = True) -> SearchResponse:
        """
        Execute a price search.

        Args:
            query: The search query string.
            use_cache: Whether to use cached results (default: True).

        Returns:
            SearchResponse with the result or error.
        """
        start_time = time.time()

        logger.info(f"Executing search use case: query='{query}', use_cache={use_cache}")

        try:
            # Create request DTO
            request = SearchRequest(
                query=query,
                use_cache=use_cache
            )

            # Execute search
            response = self.search_service.search(request)

            # Log result
            elapsed_ms = (time.time() - start_time) * 1000
            if response.success:
                logger.info(
                    f"Search successful: {response.service} - "
                    f"${response.price} (total time: {elapsed_ms:.2f}ms)"
                )
            else:
                logger.warning(
                    f"Search failed: {response.error_message} "
                    f"(total time: {elapsed_ms:.2f}ms)"
                )

            return response

        except Exception as e:
            elapsed_ms = (time.time() - start_time) * 1000
            logger.error(f"Use case execution failed: {e}", exc_info=True)

            return SearchResponse.error_response(
                error_message=f"Search failed: {str(e)}",
                search_time_ms=elapsed_ms
            )

    def execute_batch(
        self,
        queries: list[str],
        use_cache: bool = True
    ) -> list[SearchResponse]:
        """
        Execute multiple price searches.

        Args:
            queries: List of search query strings.
            use_cache: Whether to use cached results (default: True).

        Returns:
            List of SearchResponse objects.
        """
        logger.info(f"Executing batch search: {len(queries)} queries")

        responses = []
        for query in queries:
            response = self.execute(query, use_cache=use_cache)
            responses.append(response)

        successful = sum(1 for r in responses if r.success)
        logger.info(f"Batch search complete: {successful}/{len(queries)} successful")

        return responses
