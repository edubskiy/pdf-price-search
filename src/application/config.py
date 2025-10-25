"""
Application configuration.

This module provides application-level configuration management using
environment variables and sensible defaults.
"""

import os
import logging
from pathlib import Path
from typing import Optional


class AppConfig:
    """
    Application configuration with environment variable support.

    This class follows the singleton pattern to ensure a single
    configuration instance across the application.

    Attributes:
        default_pdf_directory: Directory containing PDF files (default: "source").
        enable_cache: Whether to enable caching (default: True).
        cache_ttl: Cache time-to-live in seconds (default: 3600 - 1 hour).
        max_pdf_size_mb: Maximum PDF file size in MB (default: 100).
        log_level: Logging level (default: "INFO").
    """

    _instance: Optional["AppConfig"] = None

    def __new__(cls) -> "AppConfig":
        """
        Create or return the singleton instance.

        Returns:
            The singleton AppConfig instance.
        """
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self) -> None:
        """Initialize the configuration from environment variables."""
        # Only initialize once
        if self._initialized:
            return

        # Get the project root directory (assuming config.py is in src/application/)
        self._project_root = Path(__file__).parent.parent.parent

        # Load configuration from environment variables with defaults
        self.default_pdf_directory = os.getenv(
            "PDF_DIRECTORY",
            str(self._project_root / "source")
        )

        self.enable_cache = os.getenv("ENABLE_CACHE", "true").lower() in (
            "true", "1", "yes", "on"
        )

        self.cache_ttl = int(os.getenv("CACHE_TTL", "3600"))

        self.max_pdf_size_mb = int(os.getenv("MAX_PDF_SIZE_MB", "100"))

        self.log_level = os.getenv("LOG_LEVEL", "INFO").upper()

        # Additional configuration
        self.cache_directory = os.getenv(
            "CACHE_DIRECTORY",
            str(self._project_root / ".cache")
        )

        self.max_search_results = int(os.getenv("MAX_SEARCH_RESULTS", "10"))

        self.search_timeout_seconds = int(os.getenv("SEARCH_TIMEOUT", "30"))

        # Configure logging
        self._configure_logging()

        self._initialized = True

    def _configure_logging(self) -> None:
        """Configure application logging based on log_level."""
        # Map string level to logging constant
        level_map = {
            "DEBUG": logging.DEBUG,
            "INFO": logging.INFO,
            "WARNING": logging.WARNING,
            "ERROR": logging.ERROR,
            "CRITICAL": logging.CRITICAL,
        }

        log_level = level_map.get(self.log_level, logging.INFO)

        # Configure root logger
        logging.basicConfig(
            level=log_level,
            format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )

        # Set level for application loggers
        app_logger = logging.getLogger("src")
        app_logger.setLevel(log_level)

    def get_pdf_directory(self) -> Path:
        """
        Get the PDF directory as a Path object.

        Returns:
            Path object for the PDF directory.
        """
        return Path(self.default_pdf_directory)

    def get_cache_directory(self) -> Path:
        """
        Get the cache directory as a Path object.

        Returns:
            Path object for the cache directory.
        """
        return Path(self.cache_directory)

    def validate(self) -> list[str]:
        """
        Validate the configuration.

        Returns:
            List of validation error messages (empty if valid).
        """
        errors = []

        # Validate PDF directory exists
        pdf_dir = self.get_pdf_directory()
        if not pdf_dir.exists():
            errors.append(f"PDF directory does not exist: {pdf_dir}")
        elif not pdf_dir.is_dir():
            errors.append(f"PDF directory path is not a directory: {pdf_dir}")

        # Validate cache TTL
        if self.cache_ttl <= 0:
            errors.append(f"Cache TTL must be positive, got: {self.cache_ttl}")

        # Validate max PDF size
        if self.max_pdf_size_mb <= 0:
            errors.append(f"Max PDF size must be positive, got: {self.max_pdf_size_mb}")

        # Validate search timeout
        if self.search_timeout_seconds <= 0:
            errors.append(f"Search timeout must be positive, got: {self.search_timeout_seconds}")

        return errors

    def ensure_directories(self) -> None:
        """
        Ensure required directories exist.

        Creates directories if they don't exist.
        """
        # Create cache directory if it doesn't exist
        cache_dir = self.get_cache_directory()
        cache_dir.mkdir(parents=True, exist_ok=True)

    @property
    def project_root(self) -> Path:
        """
        Get the project root directory.

        Returns:
            Path object for the project root.
        """
        return self._project_root

    def __repr__(self) -> str:
        """Get string representation of the configuration."""
        return (
            f"AppConfig("
            f"pdf_directory='{self.default_pdf_directory}', "
            f"enable_cache={self.enable_cache}, "
            f"cache_ttl={self.cache_ttl}, "
            f"log_level='{self.log_level}')"
        )

    @classmethod
    def reset(cls) -> None:
        """
        Reset the singleton instance.

        This is primarily useful for testing purposes.
        """
        cls._instance = None


# Convenience function to get the config instance
def get_config() -> AppConfig:
    """
    Get the application configuration instance.

    Returns:
        The singleton AppConfig instance.
    """
    return AppConfig()
