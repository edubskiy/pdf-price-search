"""Domain layer for PDF Price Search application."""

from .exceptions import (
    DomainException,
    InvalidZoneException,
    InvalidWeightException,
    InvalidQueryException,
    ServiceNotFoundException,
    PriceNotFoundException,
)
from .value_objects import Zone, Weight, PriceQuery
from .entities import PriceResult
from .aggregates import ShippingService
from .services import QueryParser, ServiceMatcher

__all__ = [
    # Exceptions
    "DomainException",
    "InvalidZoneException",
    "InvalidWeightException",
    "InvalidQueryException",
    "ServiceNotFoundException",
    "PriceNotFoundException",
    # Value Objects
    "Zone",
    "Weight",
    "PriceQuery",
    # Entities
    "PriceResult",
    # Aggregates
    "ShippingService",
    # Services
    "QueryParser",
    "ServiceMatcher",
]
