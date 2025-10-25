"""
FastAPI dependency injection.

This module provides dependency injection functions for FastAPI endpoints.
"""

from functools import lru_cache
from typing import Generator

from ...application.container import Container, get_container
from ...application.config import AppConfig
from ...application.use_cases.search_price_use_case import SearchPriceUseCase
from ...application.use_cases.list_services_use_case import ListServicesUseCase
from ...application.use_cases.load_data_use_case import LoadDataUseCase
from ...application.services.price_search_service import PriceSearchService


@lru_cache()
def get_app_config() -> AppConfig:
    """
    Get application configuration.

    Returns:
        AppConfig instance (cached).
    """
    return AppConfig()


@lru_cache()
def get_app_container() -> Container:
    """
    Get application container.

    Returns:
        Container instance (cached).
    """
    config = get_app_config()
    container = get_container(config)
    container.ensure_ready()
    return container


def get_search_use_case() -> Generator[SearchPriceUseCase, None, None]:
    """
    Get search price use case dependency.

    Yields:
        SearchPriceUseCase instance.
    """
    container = get_app_container()
    yield container.search_price_use_case()


def get_list_use_case() -> Generator[ListServicesUseCase, None, None]:
    """
    Get list services use case dependency.

    Yields:
        ListServicesUseCase instance.
    """
    container = get_app_container()
    yield container.list_services_use_case()


def get_load_use_case() -> Generator[LoadDataUseCase, None, None]:
    """
    Get load data use case dependency.

    Yields:
        LoadDataUseCase instance.
    """
    container = get_app_container()
    yield container.load_data_use_case()


def get_search_service() -> Generator[PriceSearchService, None, None]:
    """
    Get price search service dependency.

    Yields:
        PriceSearchService instance.
    """
    container = get_app_container()
    yield container.price_search_service()
