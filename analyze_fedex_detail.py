"""Detailed analysis of FedEx PDF structure."""

import pdfplumber
import re

def analyze_fedex_detail(pdf_path: str) -> None:
    """Analyze FedEx PDF in detail."""
    print(f"Analyzing FedEx PDF structure...\n")

    with pdfplumber.open(pdf_path) as pdf:
        # Look at pages with Zone 2 and Zone 3 data
        for page_num in [2, 3, 4, 5, 6, 7]:
            if page_num > len(pdf.pages):
                break

            page = pdf.pages[page_num - 1]
            text = page.extract_text()

            # Extract zone information
            zone_match = re.search(r'Zone (\d+)', text)
            if zone_match:
                zone = zone_match.group(1)
                print(f"\n{'='*80}")
                print(f"PAGE {page_num} - ZONE {zone}")
                print(f"{'='*80}")

            tables = page.extract_tables()

            for table_idx, table in enumerate(tables, 1):
                print(f"\nTable {table_idx} on page {page_num}:")
                print(f"  Dimensions: {len(table)} rows x {len(table[0]) if table else 0} columns\n")

                if table and len(table) >= 3:
                    # Print header rows
                    print(f"  Header Row 1: {table[0]}")
                    print(f"  Header Row 2: {table[1]}")

                    # Print some data rows
                    print(f"\n  Sample Data Rows:")
                    for row_idx in range(2, min(8, len(table))):
                        print(f"    Row {row_idx}: {table[row_idx]}")

if __name__ == "__main__":
    pdf_path = "/Users/evgeniydubskiy/Dev/edubskiy/pdf-price-search/source/FedEx_Standard_List_Rates_2025.pdf"
    analyze_fedex_detail(pdf_path)
