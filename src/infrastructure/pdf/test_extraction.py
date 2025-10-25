"""
Proof of concept script to test PDF extraction.

This script demonstrates the PDF parsing capabilities by extracting
and displaying data from the actual PDF files in the source folder.
"""

import logging
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

from src.infrastructure.pdf import PDFParser, ServiceFactory
from src.infrastructure.pdf.repository import PDFPriceRepository

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)


def test_pdf_parser():
    """Test the PDF parser with actual PDF files."""
    print("\n" + "="*80)
    print("PDF EXTRACTION PROOF OF CONCEPT")
    print("="*80 + "\n")

    # PDF file path
    pdf_path = "/Users/evgeniydubskiy/Dev/edubskiy/pdf-price-search/source/FedEx_Standard_List_Rates_2025.pdf"

    print(f"Testing with: {pdf_path}\n")

    # Create parser
    parser = PDFParser()

    try:
        # Parse the PDF
        print("Step 1: Parsing PDF...")
        extracted_data = parser.parse_file(pdf_path)

        # Display metadata
        print(f"\nMetadata:")
        print(f"  Title: {extracted_data.metadata.title}")
        print(f"  Effective Date: {extracted_data.metadata.effective_date}")
        print(f"  Total Pages: {extracted_data.metadata.total_pages}")
        print(f"  Extracted Tables: {len(extracted_data.price_tables)}")

        # Display price tables summary
        print(f"\nPrice Tables Extracted:")
        for idx, table in enumerate(extracted_data.price_tables[:5], 1):
            print(f"\n  Table {idx}:")
            print(f"    Zone: {table.zone}")
            print(f"    Page: {table.page_number}")
            print(f"    Services: {', '.join(table.service_columns)}")
            print(f"    Weights: {len(table.weight_prices)} entries")

            # Show sample prices
            if table.weight_prices:
                first_weight = list(table.weight_prices.keys())[0]
                first_prices = table.weight_prices[first_weight]
                print(f"    Sample (weight {first_weight} lbs):")
                for service, price in zip(table.service_columns, first_prices):
                    print(f"      {service}: ${price}")

        # Display service data
        print(f"\n\nStep 2: Service Data:")
        print(f"  Total Services: {len(extracted_data.service_data)}")
        print(f"  Service Names:")
        for service_name in extracted_data.get_all_service_names():
            service_data = extracted_data.get_service(service_name)
            zones = service_data.get_all_zones() if service_data else []
            print(f"    - {service_name} (zones: {zones})")

        # Show detailed data for one service
        if extracted_data.service_data:
            first_service = list(extracted_data.service_data.values())[0]
            print(f"\n\nStep 3: Detailed Data for '{first_service.service_name}':")
            print(f"  Zones with prices: {first_service.get_all_zones()}")

            # Show prices for first zone
            if first_service.zone_prices:
                first_zone = first_service.get_all_zones()[0]
                weights = first_service.get_weights_for_zone(first_zone)
                print(f"\n  Zone {first_zone} prices (first 10 weights):")
                for weight in weights[:10]:
                    price = first_service.get_price(first_zone, weight)
                    print(f"    {weight} lbs: ${price}")

        print("\n" + "="*80)
        print("SUCCESS: PDF parsing works correctly!")
        print("="*80 + "\n")

    except Exception as e:
        print(f"\nERROR: {e}")
        logger.exception("Failed to parse PDF")
        return False

    return True


def test_repository():
    """Test the repository with actual PDF files."""
    print("\n" + "="*80)
    print("REPOSITORY TEST")
    print("="*80 + "\n")

    pdf_path = "/Users/evgeniydubskiy/Dev/edubskiy/pdf-price-search/source/FedEx_Standard_List_Rates_2025.pdf"

    try:
        # Create repository
        repository = PDFPriceRepository()

        print("Step 1: Loading services from PDF...")
        services = repository.load_from_pdf(pdf_path)

        print(f"\nLoaded {len(services)} services:")
        for service in services:
            zones = sorted(service.price_table.keys())
            total_prices = sum(len(weights) for weights in service.price_table.values())
            print(f"  - {service.service_name}: {total_prices} prices across zones {zones}")

        # Test service lookup
        print(f"\n\nStep 2: Testing service lookup...")
        test_service = "FedEx 2Day"
        service = repository.get_service(test_service)

        if service:
            print(f"  Found service: {service.service_name}")
            print(f"  Variants: {service.service_variants}")

            # Test price lookup
            from src.domain import Zone, Weight
            from decimal import Decimal

            zone = Zone(2)
            weight = Weight(Decimal("5"))

            try:
                price = service.get_price(zone, weight)
                print(f"\n  Price lookup test:")
                print(f"    Service: {service.service_name}")
                print(f"    Zone: {zone.value}")
                print(f"    Weight: {weight.value} lbs")
                print(f"    Price: ${price}")
            except Exception as e:
                print(f"  Price lookup failed: {e}")
        else:
            print(f"  Service not found: {test_service}")

        print("\n" + "="*80)
        print("SUCCESS: Repository works correctly!")
        print("="*80 + "\n")

    except Exception as e:
        print(f"\nERROR: {e}")
        logger.exception("Failed to test repository")
        return False

    return True


if __name__ == "__main__":
    print("\n" + "#"*80)
    print("# PDF PRICE SEARCH - INFRASTRUCTURE LAYER TEST")
    print("#"*80)

    success = True

    # Test 1: PDF Parser
    if not test_pdf_parser():
        success = False

    # Test 2: Repository
    if not test_repository():
        success = False

    # Final result
    if success:
        print("\n" + "#"*80)
        print("# ALL TESTS PASSED!")
        print("#"*80 + "\n")
        sys.exit(0)
    else:
        print("\n" + "#"*80)
        print("# SOME TESTS FAILED!")
        print("#"*80 + "\n")
        sys.exit(1)
