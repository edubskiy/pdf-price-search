"""
Complete workflow example.

This example demonstrates the complete workflow:
1. Load PDFs
2. List services
3. Search prices
4. Display results
"""

import sys
from pathlib import Path
from typing import List

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.application.container import Container
from src.application.use_cases.search_price_use_case import SearchPriceUseCase
from src.application.use_cases.list_services_use_case import ListServicesUseCase
from src.application.use_cases.load_data_use_case import LoadDataUseCase
from src.application.dto.search_request import SearchRequest


def main():
    """Run complete workflow example."""
    print("="* 60)
    print("PDF Price Search - Complete Workflow Example")
    print("=" * 60)

    # Initialize
    container = Container()
    source_dir = project_root / "source"

    # Step 1: Load PDFs
    print("\nStep 1: Loading PDF Data")
    print("-" * 60)

    load_use_case = LoadDataUseCase(container)

    if not source_dir.exists():
        print(f"❌ Error: Source directory not found: {source_dir}")
        print("Please add PDF files to the 'source' directory")
        return

    try:
        result = load_use_case.execute_from_directory(str(source_dir))
        loaded_count = result.get('loaded_count', 0)
        print(f"✓ Successfully loaded {loaded_count} PDF file(s)")

        failed_count = result.get('failed_count', 0)
        if failed_count > 0:
            print(f"\n⚠ Warning: {failed_count} file(s) failed to load")

    except Exception as e:
        print(f"❌ Error loading PDFs: {e}")
        return

    # Step 2: List Services
    print("\nStep 2: Available Services")
    print("-" * 60)

    list_use_case = ListServicesUseCase(container)

    try:
        services = list_use_case.execute()
        print(f"Found {len(services)} service(s):\n")

        for i, service in enumerate(services, 1):
            print(f"{i}. {service.name}")
            print(f"   Zones: {min(service.available_zones)}-{max(service.available_zones)}")
            print(f"   Weight: {service.min_weight}-{service.max_weight} lb")
            print(f"   Source: {service.source_pdf}")
            print()

    except Exception as e:
        print(f"❌ Error listing services: {e}")
        return

    # Step 3: Search Prices
    print("\nStep 3: Searching Prices")
    print("-" * 60)

    search_use_case = SearchPriceUseCase(container)

    # Define test queries
    test_queries = [
        "2lb to zone 5",
        "5lb to zone 8",
        "10lb to zone 2",
    ]

    print(f"Running {len(test_queries)} search queries:\n")

    results = []
    for query in test_queries:
        request = SearchRequest(query=query)
        response = search_use_case.execute(request)

        results.append({
            'query': query,
            'response': response
        })

        print(f"Query: {query}")
        if response.success:
            print(f"  ✓ Price: ${response.price} {response.currency}")
            print(f"    Service: {response.service}")
            print(f"    Time: {response.search_time_ms:.2f} ms")
        else:
            print(f"  ✗ Not found: {response.error_message}")
        print()

    # Step 4: Summary
    print("\nStep 4: Summary")
    print("-" * 60)

    successful = sum(1 for r in results if r['response'].success)
    failed = len(results) - successful

    print(f"Total queries: {len(results)}")
    print(f"Successful: {successful}")
    print(f"Failed: {failed}")

    if successful > 0:
        avg_time = sum(
            r['response'].search_time_ms
            for r in results
            if r['response'].success
        ) / successful
        print(f"Average search time: {avg_time:.2f} ms")

    print("\n" + "=" * 60)
    print("Workflow Complete!")
    print("=" * 60)


if __name__ == "__main__":
    main()
