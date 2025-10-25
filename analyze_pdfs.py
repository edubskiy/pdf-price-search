"""Script to analyze the structure of PDF files."""

import pdfplumber
import sys

def analyze_pdf(pdf_path: str) -> None:
    """Analyze PDF structure and print findings."""
    print(f"\n{'='*80}")
    print(f"Analyzing: {pdf_path}")
    print(f"{'='*80}\n")

    with pdfplumber.open(pdf_path) as pdf:
        print(f"Total pages: {len(pdf.pages)}\n")

        # Analyze first few pages
        for page_num, page in enumerate(pdf.pages[:5], 1):
            print(f"\n--- Page {page_num} ---")
            print(f"Size: {page.width} x {page.height}")

            # Extract text
            text = page.extract_text()
            if text:
                lines = text.split('\n')[:10]
                print(f"\nFirst 10 lines of text:")
                for i, line in enumerate(lines, 1):
                    print(f"  {i}. {line[:100]}")

            # Extract tables
            tables = page.extract_tables()
            print(f"\nTables found: {len(tables)}")

            for table_idx, table in enumerate(tables[:2], 1):
                print(f"\n  Table {table_idx}:")
                print(f"    Rows: {len(table)}")
                print(f"    Columns: {len(table[0]) if table else 0}")

                if table:
                    # Print first few rows
                    print(f"    First 3 rows:")
                    for row_idx, row in enumerate(table[:3], 1):
                        print(f"      Row {row_idx}: {row}")

            print(f"\n{'-'*80}")

if __name__ == "__main__":
    # Analyze both PDFs
    pdf1 = "/Users/evgeniydubskiy/Dev/edubskiy/pdf-price-search/source/FedEx_Standard_List_Rates_2025.pdf"
    pdf2 = "/Users/evgeniydubskiy/Dev/edubskiy/pdf-price-search/source/PriceAnnex.xlsx.pdf"

    analyze_pdf(pdf1)
    analyze_pdf(pdf2)
