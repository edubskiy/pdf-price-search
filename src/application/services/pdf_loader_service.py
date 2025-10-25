"""
PDF Loader Service.

This module provides a service for loading and managing PDF data sources.
"""

import logging
from pathlib import Path
from typing import List

from ...infrastructure.pdf.repository import PriceRepositoryInterface
from ..exceptions import PDFLoadException
from ..config import AppConfig

logger = logging.getLogger(__name__)


class PDFLoaderService:
    """
    Service for loading PDF files into the repository.

    This service handles loading PDF files from various sources
    (single file, directory, default location) and provides
    information about loaded PDFs.
    """

    def __init__(
        self,
        repository: PriceRepositoryInterface,
        config: AppConfig
    ) -> None:
        """
        Initialize the PDF loader service.

        Args:
            repository: The repository to load data into.
            config: Application configuration.
        """
        self.repository = repository
        self.config = config
        self._loaded_pdfs: List[str] = []

    def load_pdfs_from_directory(self, directory: str) -> int:
        """
        Load all PDF files from a directory.

        Args:
            directory: Path to the directory containing PDF files.

        Returns:
            Number of PDFs successfully loaded.

        Raises:
            PDFLoadException: If the directory doesn't exist or loading fails.
        """
        logger.info(f"Loading PDFs from directory: {directory}")

        dir_path = Path(directory)

        # Validate directory
        if not dir_path.exists():
            raise PDFLoadException(
                directory,
                "Directory does not exist"
            )

        if not dir_path.is_dir():
            raise PDFLoadException(
                directory,
                "Path is not a directory"
            )

        # Find all PDF files
        pdf_files = list(dir_path.glob("*.pdf"))

        if not pdf_files:
            logger.warning(f"No PDF files found in directory: {directory}")
            return 0

        # Load each PDF
        loaded_count = 0
        errors = []

        for pdf_file in pdf_files:
            try:
                self._load_single_pdf(str(pdf_file))
                loaded_count += 1
            except Exception as e:
                error_msg = f"{pdf_file.name}: {str(e)}"
                errors.append(error_msg)
                logger.error(f"Failed to load {pdf_file}: {e}")

        logger.info(f"Loaded {loaded_count} of {len(pdf_files)} PDFs from {directory}")

        # If all files failed, raise exception
        if loaded_count == 0 and errors:
            raise PDFLoadException(
                directory,
                f"All PDF loads failed: {'; '.join(errors[:3])}"
            )

        return loaded_count

    def load_default_pdfs(self) -> None:
        """
        Load PDFs from the default directory.

        This loads all PDFs from the directory specified in
        the application configuration.

        Raises:
            PDFLoadException: If loading fails.
        """
        default_dir = self.config.default_pdf_directory
        logger.info(f"Loading PDFs from default directory: {default_dir}")

        try:
            count = self.load_pdfs_from_directory(default_dir)
            logger.info(f"Loaded {count} PDFs from default directory")
        except PDFLoadException:
            raise
        except Exception as e:
            raise PDFLoadException(
                default_dir,
                f"Unexpected error: {str(e)}"
            ) from e

    def load_pdf(self, pdf_path: str) -> None:
        """
        Load a single PDF file.

        Args:
            pdf_path: Path to the PDF file.

        Raises:
            PDFLoadException: If the PDF cannot be loaded.
        """
        logger.info(f"Loading PDF: {pdf_path}")

        try:
            self._load_single_pdf(pdf_path)
            logger.info(f"Successfully loaded PDF: {pdf_path}")
        except PDFLoadException:
            raise
        except Exception as e:
            raise PDFLoadException(
                pdf_path,
                f"Unexpected error: {str(e)}"
            ) from e

    def _load_single_pdf(self, pdf_path: str) -> None:
        """
        Internal method to load a single PDF.

        Args:
            pdf_path: Path to the PDF file.

        Raises:
            PDFLoadException: If the PDF cannot be loaded.
        """
        path = Path(pdf_path)

        # Validate file
        if not path.exists():
            raise PDFLoadException(pdf_path, "File does not exist")

        if not path.is_file():
            raise PDFLoadException(pdf_path, "Path is not a file")

        if path.suffix.lower() != ".pdf":
            raise PDFLoadException(pdf_path, "File is not a PDF")

        # Check file size
        file_size_mb = path.stat().st_size / (1024 * 1024)
        if file_size_mb > self.config.max_pdf_size_mb:
            raise PDFLoadException(
                pdf_path,
                f"File size ({file_size_mb:.1f} MB) exceeds maximum "
                f"({self.config.max_pdf_size_mb} MB)"
            )

        # Load the PDF using the repository
        try:
            services = self.repository.load_from_pdf(pdf_path)
            self._loaded_pdfs.append(pdf_path)
            logger.info(f"Loaded {len(services)} services from {path.name}")
        except FileNotFoundError:
            raise PDFLoadException(pdf_path, "File not found")
        except Exception as e:
            raise PDFLoadException(
                pdf_path,
                f"Failed to parse PDF: {str(e)}"
            ) from e

    def get_loaded_pdfs(self) -> List[str]:
        """
        Get the list of loaded PDF files.

        Returns:
            List of paths to loaded PDF files.
        """
        return self._loaded_pdfs.copy()

    def validate_pdf(self, pdf_path: str) -> bool:
        """
        Validate a PDF file without loading it.

        Args:
            pdf_path: Path to the PDF file.

        Returns:
            True if the PDF is valid, False otherwise.
        """
        try:
            path = Path(pdf_path)

            # Check existence
            if not path.exists():
                logger.debug(f"PDF validation failed: file does not exist - {pdf_path}")
                return False

            # Check it's a file
            if not path.is_file():
                logger.debug(f"PDF validation failed: not a file - {pdf_path}")
                return False

            # Check extension
            if path.suffix.lower() != ".pdf":
                logger.debug(f"PDF validation failed: not a PDF file - {pdf_path}")
                return False

            # Check file size
            file_size_mb = path.stat().st_size / (1024 * 1024)
            if file_size_mb > self.config.max_pdf_size_mb:
                logger.debug(
                    f"PDF validation failed: file too large ({file_size_mb:.1f} MB) - {pdf_path}"
                )
                return False

            logger.debug(f"PDF validation passed: {pdf_path}")
            return True

        except Exception as e:
            logger.error(f"Error validating PDF {pdf_path}: {e}")
            return False

    def clear_loaded_pdfs(self) -> None:
        """Clear the list of loaded PDFs."""
        self._loaded_pdfs.clear()
        logger.debug("Cleared loaded PDFs list")

    def get_loaded_count(self) -> int:
        """
        Get the number of loaded PDFs.

        Returns:
            Number of PDFs currently loaded.
        """
        return len(self._loaded_pdfs)
