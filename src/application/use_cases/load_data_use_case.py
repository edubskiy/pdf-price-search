"""
Load Data Use Case.

This module implements the use case for loading PDF data.
"""

import logging
from pathlib import Path
from typing import List, Dict, Any

from ..services.pdf_loader_service import PDFLoaderService
from ..exceptions import PDFLoadException

logger = logging.getLogger(__name__)


class LoadDataUseCase:
    """
    Use case for loading PDF price data.

    This use case handles loading data from various sources
    with progress tracking and error reporting.
    """

    def __init__(self, loader_service: PDFLoaderService) -> None:
        """
        Initialize the use case.

        Args:
            loader_service: The PDF loader service.
        """
        self.loader_service = loader_service

    def execute_from_file(self, pdf_path: str) -> Dict[str, Any]:
        """
        Execute loading from a single PDF file.

        Args:
            pdf_path: Path to the PDF file.

        Returns:
            Dictionary with loading results.

        Raises:
            PDFLoadException: If loading fails.
        """
        logger.info(f"Executing load data use case: file={pdf_path}")

        # Validate the PDF first
        if not self.loader_service.validate_pdf(pdf_path):
            raise PDFLoadException(pdf_path, "PDF validation failed")

        # Load the PDF
        self.loader_service.load_pdf(pdf_path)

        result = {
            "success": True,
            "loaded_files": [pdf_path],
            "total_files": 1,
            "failed_files": []
        }

        logger.info(f"Successfully loaded PDF: {pdf_path}")
        return result

    def execute_from_directory(self, directory: str) -> Dict[str, Any]:
        """
        Execute loading from a directory of PDF files.

        Args:
            directory: Path to the directory.

        Returns:
            Dictionary with loading results including progress.

        Raises:
            PDFLoadException: If directory loading fails completely.
        """
        logger.info(f"Executing load data use case: directory={directory}")

        dir_path = Path(directory)

        # Validate directory
        if not dir_path.exists():
            raise PDFLoadException(directory, "Directory does not exist")

        if not dir_path.is_dir():
            raise PDFLoadException(directory, "Path is not a directory")

        # Get list of PDF files
        pdf_files = list(dir_path.glob("*.pdf"))
        total_files = len(pdf_files)

        logger.info(f"Found {total_files} PDF files in {directory}")

        if total_files == 0:
            return {
                "success": True,
                "loaded_files": [],
                "total_files": 0,
                "failed_files": [],
                "message": "No PDF files found in directory"
            }

        # Load PDFs with progress tracking
        loaded_files = []
        failed_files = []

        for i, pdf_file in enumerate(pdf_files, 1):
            pdf_path = str(pdf_file)
            logger.info(f"Loading PDF {i}/{total_files}: {pdf_file.name}")

            try:
                self.loader_service.load_pdf(pdf_path)
                loaded_files.append(pdf_path)
                logger.info(f"Successfully loaded {pdf_file.name}")
            except Exception as e:
                failed_files.append({
                    "file": pdf_path,
                    "error": str(e)
                })
                logger.error(f"Failed to load {pdf_file.name}: {e}")

        # Create result
        result = {
            "success": len(loaded_files) > 0,
            "loaded_files": loaded_files,
            "total_files": total_files,
            "failed_files": failed_files,
            "loaded_count": len(loaded_files),
            "failed_count": len(failed_files)
        }

        if result["success"]:
            logger.info(
                f"Directory load complete: {len(loaded_files)}/{total_files} successful"
            )
        else:
            logger.error(f"All PDF loads failed in directory: {directory}")

        return result

    def execute_default(self) -> Dict[str, Any]:
        """
        Execute loading from the default PDF directory.

        Returns:
            Dictionary with loading results.

        Raises:
            PDFLoadException: If loading fails.
        """
        logger.info("Executing load data use case: default directory")

        default_dir = self.loader_service.config.default_pdf_directory

        return self.execute_from_directory(default_dir)

    def get_loaded_pdfs(self) -> List[str]:
        """
        Get the list of currently loaded PDF files.

        Returns:
            List of paths to loaded PDF files.
        """
        return self.loader_service.get_loaded_pdfs()

    def validate_and_report(self, pdf_paths: List[str]) -> Dict[str, Any]:
        """
        Validate multiple PDF files without loading them.

        Args:
            pdf_paths: List of PDF file paths to validate.

        Returns:
            Dictionary with validation results.
        """
        logger.info(f"Validating {len(pdf_paths)} PDF files")

        valid_files = []
        invalid_files = []

        for pdf_path in pdf_paths:
            if self.loader_service.validate_pdf(pdf_path):
                valid_files.append(pdf_path)
            else:
                invalid_files.append(pdf_path)

        result = {
            "total_files": len(pdf_paths),
            "valid_files": valid_files,
            "invalid_files": invalid_files,
            "valid_count": len(valid_files),
            "invalid_count": len(invalid_files)
        }

        logger.info(
            f"Validation complete: {len(valid_files)}/{len(pdf_paths)} valid"
        )

        return result
