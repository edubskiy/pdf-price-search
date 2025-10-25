"""
Core PDF parsing logic.

This module provides the main PDFParser class that uses pdfplumber
to extract tables and structured data from PDF files.
"""

import logging
from pathlib import Path
from typing import List, Optional

import pdfplumber

from .models import (
    ExtractedPDFData,
    PDFMetadata,
    PriceTableData,
    ServicePriceData,
)
from .table_extractor import TableExtractor

logger = logging.getLogger(__name__)


class PDFParserError(Exception):
    """Base exception for PDF parsing errors."""

    pass


class PDFParser:
    """
    Core PDF parser using pdfplumber.

    This class handles:
    - Opening and reading PDF files
    - Extracting tables from pages
    - Parsing price data from tables
    - Building structured data models
    """

    def __init__(self) -> None:
        """Initialize the PDFParser."""
        self.table_extractor = TableExtractor()

    def parse_file(self, file_path: str) -> ExtractedPDFData:
        """
        Parse a PDF file and extract all price data.

        Args:
            file_path: Path to the PDF file.

        Returns:
            ExtractedPDFData containing all parsed data.

        Raises:
            PDFParserError: If parsing fails.
            FileNotFoundError: If file doesn't exist.
        """
        path = Path(file_path)
        if not path.exists():
            raise FileNotFoundError(f"PDF file not found: {file_path}")

        logger.info(f"Starting to parse PDF: {file_path}")

        try:
            with pdfplumber.open(file_path) as pdf:
                # Extract metadata
                metadata = self._extract_metadata(pdf, file_path)

                # Initialize result
                result = ExtractedPDFData(metadata=metadata)

                # Process each page
                for page_num, page in enumerate(pdf.pages, 1):
                    logger.debug(f"Processing page {page_num}/{len(pdf.pages)}")

                    try:
                        tables = self._extract_tables_from_page(page, page_num)
                        for table in tables:
                            result.add_price_table(table)
                    except Exception as e:
                        logger.warning(f"Error processing page {page_num}: {e}")
                        continue

                # Update extracted pages count
                result.metadata.extracted_pages = len(result.price_tables)

                # Build service data from tables
                self._build_service_data(result)

                logger.info(
                    f"Successfully parsed PDF. "
                    f"Extracted {len(result.price_tables)} tables, "
                    f"{len(result.service_data)} services."
                )

                return result

        except Exception as e:
            logger.error(f"Failed to parse PDF {file_path}: {e}")
            raise PDFParserError(f"Failed to parse PDF: {e}") from e

    def _extract_metadata(self, pdf: pdfplumber.PDF, file_path: str) -> PDFMetadata:
        """
        Extract metadata from PDF.

        Args:
            pdf: The pdfplumber PDF object.
            file_path: Path to the PDF file.

        Returns:
            PDFMetadata object.
        """
        metadata = PDFMetadata(file_path=file_path, total_pages=len(pdf.pages))

        # Try to extract title from first page
        if pdf.pages:
            first_page = pdf.pages[0]
            text = first_page.extract_text()

            if text:
                lines = text.split('\n')
                # First non-empty line is usually the title
                for line in lines:
                    if line.strip():
                        metadata.title = line.strip()
                        break

                # Look for effective date
                for line in lines[:10]:
                    if 'effective' in line.lower() and any(c.isdigit() for c in line):
                        metadata.effective_date = line.strip()
                        break

        return metadata

    def _extract_tables_from_page(
        self, page: pdfplumber.page.Page, page_num: int
    ) -> List[PriceTableData]:
        """
        Extract price tables from a page.

        Args:
            page: The pdfplumber page object.
            page_num: The page number (1-indexed).

        Returns:
            List of PriceTableData objects.
        """
        result: List[PriceTableData] = []

        # Extract page text to find zone
        text = page.extract_text()
        zone = self.table_extractor.extract_zone_from_text(text)

        if zone is None:
            logger.debug(f"No zone found on page {page_num}, skipping")
            return result

        # Extract tables from page
        tables = page.extract_tables()

        for table_idx, table in enumerate(tables):
            try:
                # Validate table structure
                is_valid, error = self.table_extractor.validate_table_structure(table)
                if not is_valid:
                    logger.debug(
                        f"Skipping invalid table {table_idx} on page {page_num}: {error}"
                    )
                    continue

                # Extract service columns from header
                header_rows = table[:2]  # Usually first 2 rows are headers
                service_columns = self.table_extractor.extract_service_columns(header_rows)

                if not service_columns:
                    logger.debug(
                        f"No service columns found in table {table_idx} on page {page_num}"
                    )
                    continue

                # Extract just the service names
                service_names = [name for _, name in service_columns]

                # Extract weight and price data
                weight_prices = self.table_extractor.extract_weight_prices(
                    table, service_columns, skip_header_rows=2
                )

                if not weight_prices:
                    logger.debug(
                        f"No price data found in table {table_idx} on page {page_num}"
                    )
                    continue

                # Create PriceTableData
                table_data = PriceTableData(
                    zone=zone,
                    service_columns=service_names,
                    weight_prices=weight_prices,
                    page_number=page_num,
                )

                result.append(table_data)
                logger.debug(
                    f"Extracted table {table_idx} from page {page_num}: "
                    f"zone={zone}, services={len(service_names)}, "
                    f"weights={len(weight_prices)}"
                )

            except Exception as e:
                logger.warning(
                    f"Error extracting table {table_idx} from page {page_num}: {e}"
                )
                continue

        return result

    def _build_service_data(self, extracted_data: ExtractedPDFData) -> None:
        """
        Build ServicePriceData objects from PriceTableData.

        This method consolidates data from multiple tables into
        per-service data structures.

        Args:
            extracted_data: The ExtractedPDFData to update.
        """
        # Map service names to ServicePriceData
        service_map: dict[str, ServicePriceData] = {}

        for table in extracted_data.price_tables:
            zone = table.zone
            service_names = table.service_columns

            # Process each weight/price row
            for weight, prices in table.weight_prices.items():
                # Each price corresponds to a service
                for service_idx, service_name in enumerate(service_names):
                    if service_idx >= len(prices):
                        continue

                    price = prices[service_idx]

                    # Get or create ServicePriceData
                    if service_name not in service_map:
                        service_map[service_name] = ServicePriceData(
                            service_name=service_name
                        )

                    # Add the price
                    service_map[service_name].add_price(zone, weight, price)

        # Add to extracted data
        for service_data in service_map.values():
            extracted_data.add_service_data(service_data)

    def parse_multiple_files(self, file_paths: List[str]) -> List[ExtractedPDFData]:
        """
        Parse multiple PDF files.

        Args:
            file_paths: List of paths to PDF files.

        Returns:
            List of ExtractedPDFData objects.
        """
        results: List[ExtractedPDFData] = []

        for file_path in file_paths:
            try:
                result = self.parse_file(file_path)
                results.append(result)
            except Exception as e:
                logger.error(f"Failed to parse {file_path}: {e}")
                continue

        return results
