"""
Domain exceptions for the PDF Price Search application.

This module defines all custom exceptions that can occur within the domain layer,
following Domain-Driven Design principles.
"""


class DomainException(Exception):
    """Base exception for all domain-related errors."""

    def __init__(self, message: str) -> None:
        """
        Initialize the domain exception.

        Args:
            message: Human-readable error message describing the issue.
        """
        self.message = message
        super().__init__(self.message)


class InvalidZoneException(DomainException):
    """Raised when a zone value is invalid or cannot be parsed."""

    def __init__(
        self, value: str, reason: str = "Invalid zone format or value"
    ) -> None:
        """
        Initialize the invalid zone exception.

        Args:
            value: The invalid zone value that was provided.
            reason: Additional context about why the zone is invalid.
        """
        super().__init__(f"Invalid zone '{value}': {reason}")
        self.value = value


class InvalidWeightException(DomainException):
    """Raised when a weight value is invalid or cannot be parsed."""

    def __init__(
        self, value: str, reason: str = "Invalid weight format or value"
    ) -> None:
        """
        Initialize the invalid weight exception.

        Args:
            value: The invalid weight value that was provided.
            reason: Additional context about why the weight is invalid.
        """
        super().__init__(f"Invalid weight '{value}': {reason}")
        self.value = value


class InvalidQueryException(DomainException):
    """Raised when a price query cannot be parsed or is malformed."""

    def __init__(self, query: str, reason: str = "Cannot parse query") -> None:
        """
        Initialize the invalid query exception.

        Args:
            query: The malformed query string.
            reason: Additional context about why the query is invalid.
        """
        super().__init__(f"Invalid query '{query}': {reason}")
        self.query = query


class ServiceNotFoundException(DomainException):
    """Raised when a shipping service cannot be found or matched."""

    def __init__(self, service_name: str) -> None:
        """
        Initialize the service not found exception.

        Args:
            service_name: The name of the service that could not be found.
        """
        super().__init__(f"Service '{service_name}' not found")
        self.service_name = service_name


class PriceNotFoundException(DomainException):
    """Raised when a price cannot be found for the given query parameters."""

    def __init__(self, service: str, zone: int, weight: float) -> None:
        """
        Initialize the price not found exception.

        Args:
            service: The service name for which price was not found.
            zone: The zone number.
            weight: The weight in pounds.
        """
        super().__init__(
            f"Price not found for service '{service}', zone {zone}, weight {weight} lb"
        )
        self.service = service
        self.zone = zone
        self.weight = weight
