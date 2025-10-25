"""
Input validation for presentation layer.

This module provides validation and sanitization for user input
from both CLI and API interfaces.
"""

import re
from pathlib import Path
from typing import Optional


class ValidationError(ValueError):
    """Raised when input validation fails."""
    pass


class InputValidator:
    """
    Validates and sanitizes user input.

    This class provides static methods for validating various types
    of user input to ensure security and data integrity.
    """

    # Regular expression patterns
    QUERY_PATTERN = re.compile(r'^[\w\s,.\-]+$')
    ZONE_PATTERN = re.compile(r'[zZ]?(\d+)')
    WEIGHT_PATTERN = re.compile(r'(\d+(?:\.\d+)?)\s*(?:lb|lbs?|pound|pounds)?')

    # Constraints
    MAX_QUERY_LENGTH = 500
    MAX_FILE_SIZE_MB = 100
    ALLOWED_EXTENSIONS = {'.pdf'}

    @staticmethod
    def validate_query(query: str) -> str:
        """
        Validate and sanitize a search query.

        Args:
            query: The search query string.

        Returns:
            The sanitized query string.

        Raises:
            ValidationError: If the query is invalid.
        """
        if not query:
            raise ValidationError("Query cannot be empty")

        # Strip whitespace
        query = query.strip()

        # Check length
        if len(query) > InputValidator.MAX_QUERY_LENGTH:
            raise ValidationError(
                f"Query too long (max {InputValidator.MAX_QUERY_LENGTH} characters)"
            )

        # Check for valid characters
        if not InputValidator.QUERY_PATTERN.match(query):
            raise ValidationError(
                "Query contains invalid characters. "
                "Only letters, numbers, spaces, commas, dots, and hyphens are allowed."
            )

        return query

    @staticmethod
    def validate_file_path(file_path: str, must_exist: bool = True) -> Path:
        """
        Validate a file path.

        Args:
            file_path: The file path to validate.
            must_exist: Whether the file must exist (default: True).

        Returns:
            The validated Path object.

        Raises:
            ValidationError: If the file path is invalid.
        """
        if not file_path:
            raise ValidationError("File path cannot be empty")

        # Convert to Path object
        try:
            path = Path(file_path).resolve()
        except Exception as e:
            raise ValidationError(f"Invalid file path: {e}")

        # Check if file exists
        if must_exist and not path.exists():
            raise ValidationError(f"File does not exist: {path}")

        # Check if it's a file (not a directory)
        if must_exist and not path.is_file():
            raise ValidationError(f"Path is not a file: {path}")

        return path

    @staticmethod
    def validate_directory_path(
        dir_path: str,
        must_exist: bool = True,
        create_if_missing: bool = False
    ) -> Path:
        """
        Validate a directory path.

        Args:
            dir_path: The directory path to validate.
            must_exist: Whether the directory must exist (default: True).
            create_if_missing: Whether to create the directory if it doesn't exist.

        Returns:
            The validated Path object.

        Raises:
            ValidationError: If the directory path is invalid.
        """
        if not dir_path:
            raise ValidationError("Directory path cannot be empty")

        # Convert to Path object
        try:
            path = Path(dir_path).resolve()
        except Exception as e:
            raise ValidationError(f"Invalid directory path: {e}")

        # Create if requested
        if create_if_missing and not path.exists():
            try:
                path.mkdir(parents=True, exist_ok=True)
            except Exception as e:
                raise ValidationError(f"Failed to create directory: {e}")

        # Check if directory exists
        if must_exist and not path.exists():
            raise ValidationError(f"Directory does not exist: {path}")

        # Check if it's a directory
        if path.exists() and not path.is_dir():
            raise ValidationError(f"Path is not a directory: {path}")

        return path

    @staticmethod
    def validate_pdf_file(file_path: str) -> Path:
        """
        Validate a PDF file path.

        Args:
            file_path: The PDF file path to validate.

        Returns:
            The validated Path object.

        Raises:
            ValidationError: If the file is not a valid PDF.
        """
        path = InputValidator.validate_file_path(file_path)

        # Check extension
        if path.suffix.lower() not in InputValidator.ALLOWED_EXTENSIONS:
            raise ValidationError(
                f"Invalid file type. Must be PDF, got: {path.suffix}"
            )

        # Check file size
        file_size_mb = path.stat().st_size / (1024 * 1024)
        if file_size_mb > InputValidator.MAX_FILE_SIZE_MB:
            raise ValidationError(
                f"File too large: {file_size_mb:.2f} MB "
                f"(max {InputValidator.MAX_FILE_SIZE_MB} MB)"
            )

        return path

    @staticmethod
    def validate_zone(zone_input: str) -> int:
        """
        Validate and extract zone number.

        Args:
            zone_input: Zone input string (e.g., "5", "Z5", "zone 5").

        Returns:
            The zone number as an integer.

        Raises:
            ValidationError: If the zone is invalid.
        """
        if not zone_input:
            raise ValidationError("Zone cannot be empty")

        # Try to extract zone number
        match = InputValidator.ZONE_PATTERN.search(zone_input.strip())
        if not match:
            raise ValidationError(f"Invalid zone format: {zone_input}")

        zone = int(match.group(1))

        # Validate range (typical shipping zones are 2-8)
        if zone < 1 or zone > 10:
            raise ValidationError(f"Zone out of range: {zone} (expected 1-10)")

        return zone

    @staticmethod
    def validate_weight(weight_input: str) -> float:
        """
        Validate and extract weight value.

        Args:
            weight_input: Weight input string (e.g., "3", "3.5 lb", "10 pounds").

        Returns:
            The weight in pounds as a float.

        Raises:
            ValidationError: If the weight is invalid.
        """
        if not weight_input:
            raise ValidationError("Weight cannot be empty")

        # Try to extract weight value
        match = InputValidator.WEIGHT_PATTERN.search(weight_input.strip())
        if not match:
            raise ValidationError(f"Invalid weight format: {weight_input}")

        weight = float(match.group(1))

        # Validate range
        if weight <= 0:
            raise ValidationError(f"Weight must be positive, got: {weight}")

        if weight > 150:
            raise ValidationError(f"Weight too large: {weight} lb (max 150 lb)")

        return weight

    @staticmethod
    def sanitize_filename(filename: str) -> str:
        """
        Sanitize a filename by removing dangerous characters.

        Args:
            filename: The filename to sanitize.

        Returns:
            The sanitized filename.
        """
        # Remove path separators and dangerous characters
        sanitized = re.sub(r'[/\\:*?"<>|]', '_', filename)

        # Remove leading/trailing spaces and dots
        sanitized = sanitized.strip('. ')

        # Ensure filename is not empty
        if not sanitized:
            sanitized = "unnamed"

        return sanitized

    @staticmethod
    def validate_page_number(page: int, max_pages: Optional[int] = None) -> int:
        """
        Validate a page number.

        Args:
            page: The page number to validate.
            max_pages: Optional maximum number of pages.

        Returns:
            The validated page number.

        Raises:
            ValidationError: If the page number is invalid.
        """
        if page < 1:
            raise ValidationError(f"Page number must be at least 1, got: {page}")

        if max_pages is not None and page > max_pages:
            raise ValidationError(
                f"Page number {page} exceeds maximum {max_pages}"
            )

        return page

    @staticmethod
    def validate_limit(limit: int, max_limit: int = 1000) -> int:
        """
        Validate a result limit.

        Args:
            limit: The limit value to validate.
            max_limit: The maximum allowed limit (default: 1000).

        Returns:
            The validated limit.

        Raises:
            ValidationError: If the limit is invalid.
        """
        if limit < 1:
            raise ValidationError(f"Limit must be at least 1, got: {limit}")

        if limit > max_limit:
            raise ValidationError(
                f"Limit {limit} exceeds maximum {max_limit}"
            )

        return limit
