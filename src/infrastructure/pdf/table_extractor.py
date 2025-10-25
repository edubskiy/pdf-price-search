"""
Table extraction utilities for PDF parsing.

This module provides utilities to extract and normalize price tables from PDFs.
It handles different table formats, merged cells, and complex layouts.
"""

import logging
import re
from decimal import Decimal, InvalidOperation
from typing import Dict, List, Optional, Tuple

logger = logging.getLogger(__name__)


class TableExtractor:
    """
    Utility class for extracting and normalizing price tables from PDFs.

    This class handles the complexity of extracting structured data from
    PDF tables, including:
    - Identifying service columns from headers
    - Extracting weight rows and price values
    - Handling merged cells and multi-line headers
    - Normalizing extracted data
    """

    # Service name patterns to identify in headers
    SERVICE_PATTERNS = [
        r"FedEx\s+First\s+Overnight",
        r"FedEx\s+Priority\s+Overnight",
        r"FedEx\s+Standard\s+Overnight",
        r"FedEx\s+2Day\s+A\.?M\.?",
        r"FedEx\s+2Day",
        r"FedEx\s+Express\s+Saver",
        r"FedEx\s+Ground",
    ]

    def __init__(self) -> None:
        """Initialize the TableExtractor."""
        self.service_patterns = [re.compile(p, re.IGNORECASE) for p in self.SERVICE_PATTERNS]

    def extract_zone_from_text(self, text: str) -> Optional[int]:
        """
        Extract zone number from page text.

        Args:
            text: The text content of a page.

        Returns:
            Zone number if found, None otherwise.
        """
        if not text:
            return None

        # Look for "Zone X" pattern
        match = re.search(r'Zone\s+(\d+)', text, re.IGNORECASE)
        if match:
            try:
                return int(match.group(1))
            except (ValueError, IndexError):
                pass

        return None

    def extract_service_columns(self, header_rows: List[List[Optional[str]]]) -> List[Tuple[int, str]]:
        """
        Extract service columns from table header rows.

        Args:
            header_rows: List of header rows from the table.

        Returns:
            List of tuples (column_index, service_name).
        """
        service_columns: List[Tuple[int, str]] = []

        if not header_rows:
            return service_columns

        # Combine header rows to handle multi-line service names
        for row in header_rows:
            for col_idx, cell in enumerate(row):
                if cell is None:
                    continue

                # Clean the cell text
                cell_text = self._clean_text(cell)

                # Check if it matches any service pattern
                for pattern in self.service_patterns:
                    if pattern.search(cell_text):
                        # Extract the service name
                        service_name = self._normalize_service_name(cell_text)
                        if service_name:
                            # Check if this column is already recorded
                            if not any(idx == col_idx for idx, _ in service_columns):
                                service_columns.append((col_idx, service_name))
                        break

        return sorted(service_columns, key=lambda x: x[0])

    def extract_weight_prices(
        self,
        table: List[List[Optional[str]]],
        service_columns: List[Tuple[int, str]],
        skip_header_rows: int = 2,
    ) -> Dict[str, List[Decimal]]:
        """
        Extract weight and price data from table rows.

        Args:
            table: The complete table data.
            service_columns: List of (column_index, service_name) tuples.
            skip_header_rows: Number of header rows to skip.

        Returns:
            Dict mapping weight string to list of prices (one per service).
        """
        weight_prices: Dict[str, List[Decimal]] = {}

        if len(table) <= skip_header_rows:
            return weight_prices

        # Process data rows
        for row_idx in range(skip_header_rows, len(table)):
            row = table[row_idx]

            # Extract weights from the first column(s)
            weights = self._extract_weights_from_cell(row[0] if row else None)

            # If no weights found in first column, try second column
            if not weights and len(row) > 1:
                weights = self._extract_weights_from_cell(row[1])

            if not weights:
                continue

            # Extract prices for each service column
            for weight in weights:
                prices: List[Decimal] = []

                for col_idx, _ in service_columns:
                    if col_idx < len(row):
                        price = self._extract_price_from_cell(row[col_idx], weight)
                        if price is not None:
                            prices.append(price)

                # Only add if we have prices for all services
                if len(prices) == len(service_columns):
                    weight_prices[weight] = prices

        return weight_prices

    def _clean_text(self, text: str) -> str:
        """
        Clean and normalize text.

        Args:
            text: The text to clean.

        Returns:
            Cleaned text.
        """
        if not text:
            return ""

        # Remove extra whitespace and newlines
        text = re.sub(r'\s+', ' ', text)
        return text.strip()

    def _normalize_service_name(self, text: str) -> Optional[str]:
        """
        Normalize service name from extracted text.

        Args:
            text: The raw text containing a service name.

        Returns:
            Normalized service name, or None if not recognized.
        """
        text = self._clean_text(text)

        # Map patterns to canonical names
        name_map = {
            r"First\s+Overnight": "FedEx First Overnight",
            r"Priority\s+Overnight": "FedEx Priority Overnight",
            r"Standard\s+Overnight": "FedEx Standard Overnight",
            r"2Day\s+A\.?M\.?": "FedEx 2Day A.M.",
            r"2Day(?!\s+A)": "FedEx 2Day",
            r"Express\s+Saver": "FedEx Express Saver",
            r"Ground": "FedEx Ground",
        }

        for pattern, canonical_name in name_map.items():
            if re.search(pattern, text, re.IGNORECASE):
                return canonical_name

        return None

    def _extract_weights_from_cell(self, cell: Optional[str]) -> List[str]:
        """
        Extract weight values from a cell.

        Args:
            cell: The cell text.

        Returns:
            List of weight strings (e.g., ["1", "2", "3"]).
        """
        if not cell:
            return []

        weights: List[str] = []

        # Clean the text
        text = self._clean_text(cell)

        # Look for patterns like "1lb.", "2 lbs.", "3", "50lbs.", etc.
        # Split on newlines and spaces
        parts = re.split(r'[\n\s]+', text)

        for part in parts:
            # Remove "lbs", "lb", ".", and other non-numeric characters
            weight_str = re.sub(r'(lbs?\.?|[^\d.])', '', part, flags=re.IGNORECASE)

            if weight_str:
                try:
                    # Validate it's a number
                    float(weight_str)
                    weights.append(weight_str)
                except ValueError:
                    continue

        return weights

    def _extract_price_from_cell(self, cell: Optional[str], weight: str) -> Optional[Decimal]:
        """
        Extract price value from a cell for a specific weight.

        Args:
            cell: The cell text.
            weight: The weight string we're looking for.

        Returns:
            Decimal price if found, None otherwise.
        """
        if not cell:
            return None

        # Clean the text
        text = self._clean_text(cell)

        # Look for price patterns like "$ 65.71", "$65.71", "65.71"
        # The cell might contain multiple prices for multiple weights
        # Split by newline to handle multi-weight cells
        lines = text.split('\n')

        # If there's only one line, it's likely a single price
        if len(lines) == 1:
            return self._parse_price(text)

        # If multiple lines, we need to match the weight position
        # This is complex - for now, return the first valid price
        for line in lines:
            price = self._parse_price(line)
            if price is not None:
                return price

        return None

    def _parse_price(self, text: str) -> Optional[Decimal]:
        """
        Parse a price value from text.

        Args:
            text: The text containing a price.

        Returns:
            Decimal price if found, None otherwise.
        """
        if not text or text.strip() == '*':
            return None

        # Remove currency symbols, commas, and whitespace
        cleaned = re.sub(r'[$€£¥\s,]', '', text)

        # Try to extract a decimal number
        match = re.search(r'(\d+\.?\d*)', cleaned)
        if match:
            try:
                return Decimal(match.group(1))
            except InvalidOperation:
                pass

        return None

    def validate_table_structure(
        self, table: List[List[Optional[str]]]
    ) -> Tuple[bool, Optional[str]]:
        """
        Validate the structure of an extracted table.

        Args:
            table: The table to validate.

        Returns:
            Tuple of (is_valid, error_message).
        """
        if not table:
            return False, "Table is empty"

        if len(table) < 3:
            return False, "Table has fewer than 3 rows (need headers + data)"

        # Check that rows have consistent column counts
        col_counts = [len(row) for row in table]
        if len(set(col_counts)) > 2:  # Allow some variation
            return False, f"Inconsistent column counts: {col_counts}"

        return True, None
