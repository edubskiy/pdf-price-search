"""
Application layer exceptions.

This module defines exceptions specific to the application layer,
providing clear error handling for use cases and services.
"""


class ApplicationException(Exception):
    """
    Base exception for all application layer errors.

    All application-specific exceptions should inherit from this class.
    This allows for consistent error handling at the presentation layer.
    """

    def __init__(self, message: str, details: str = None) -> None:
        """
        Initialize the exception.

        Args:
            message: The main error message.
            details: Optional additional error details.
        """
        self.message = message
        self.details = details
        super().__init__(message)

    def __str__(self) -> str:
        """Get string representation of the exception."""
        if self.details:
            return f"{self.message}: {self.details}"
        return self.message


class SearchException(ApplicationException):
    """
    Exception raised when a price search operation fails.

    This can occur due to parsing errors, service matching failures,
    or price lookup failures.
    """

    def __init__(self, query: str, reason: str) -> None:
        """
        Initialize the search exception.

        Args:
            query: The original search query.
            reason: The reason for the failure.
        """
        self.query = query
        self.reason = reason
        super().__init__(
            f"Search failed for query: '{query}'",
            reason
        )


class PDFLoadException(ApplicationException):
    """
    Exception raised when loading PDF data fails.

    This can occur due to file access issues, parsing errors,
    or invalid data in the PDF.
    """

    def __init__(self, file_path: str, reason: str) -> None:
        """
        Initialize the PDF load exception.

        Args:
            file_path: The path to the PDF file that failed to load.
            reason: The reason for the failure.
        """
        self.file_path = file_path
        self.reason = reason
        super().__init__(
            f"Failed to load PDF: '{file_path}'",
            reason
        )


class ServiceNotAvailableException(ApplicationException):
    """
    Exception raised when a requested shipping service is not available.

    This occurs when the service matcher cannot find a matching service
    in the loaded data.
    """

    def __init__(self, service_name: str, available_services: list[str] = None) -> None:
        """
        Initialize the service not available exception.

        Args:
            service_name: The service name that was not found.
            available_services: Optional list of available service names.
        """
        self.service_name = service_name
        self.available_services = available_services or []

        details = f"Service '{service_name}' not found"
        if self.available_services:
            details += f". Available services: {', '.join(self.available_services[:5])}"
            if len(self.available_services) > 5:
                details += f" and {len(self.available_services) - 5} more"

        super().__init__(
            f"Service not available: '{service_name}'",
            details
        )


class InvalidRequestException(ApplicationException):
    """
    Exception raised when a request is invalid.

    This can occur due to missing required fields, invalid field values,
    or other validation errors.
    """

    def __init__(self, field: str, reason: str) -> None:
        """
        Initialize the invalid request exception.

        Args:
            field: The field that is invalid.
            reason: The reason for the invalidity.
        """
        self.field = field
        self.reason = reason
        super().__init__(
            f"Invalid request field: '{field}'",
            reason
        )


class DataNotLoadedException(ApplicationException):
    """
    Exception raised when attempting to search without loaded data.

    This occurs when a search is attempted before any PDF data has been loaded.
    """

    def __init__(self) -> None:
        """Initialize the data not loaded exception."""
        super().__init__(
            "No price data loaded",
            "Please load PDF data before performing searches"
        )


class CacheException(ApplicationException):
    """
    Exception raised when a cache operation fails.

    This is typically a non-critical error that should be logged
    but not prevent the operation from continuing.
    """

    def __init__(self, operation: str, reason: str) -> None:
        """
        Initialize the cache exception.

        Args:
            operation: The cache operation that failed (get, set, clear, etc.).
            reason: The reason for the failure.
        """
        self.operation = operation
        self.reason = reason
        super().__init__(
            f"Cache operation '{operation}' failed",
            reason
        )
