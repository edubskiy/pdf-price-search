"""
Batch search example.

This example demonstrates how to search for multiple prices at once.
"""

import sys
from pathlib import Path
from typing import List, Tuple

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.application.container import Container
from src.application.use_cases.search_price_use_case import SearchPriceUseCase
from src.application.use_cases.load_data_use_case import LoadDataUseCase
from src.application.dto.search_request import SearchRequest


def batch_search(queries: List[str]) -> List[Tuple[str, dict]]:
    """
    Perform batch searches.

    Args:
        queries: List of search queries.

    Returns:
        List of tuples (query, result_dict).
    """
    container = Container()

    # Load data
    load_use_case = LoadDataUseCase(container)
    source_dir = project_root / "source"

    if not source_dir.exists():
        raise FileNotFoundError(f"Source directory not found: {source_dir}")

    load_use_case.execute_from_directory(str(source_dir))

    # Search each query
    search_use_case = SearchPriceUseCase(container)
    results = []

    for query in queries:
        request = SearchRequest(query=query)
        response = search_use_case.execute(request)

        results.append((query, {
            'success': response.success,
            'price': response.price,
            'service': response.service,
            'zone': response.zone,
            'weight': response.weight,
            'error': response.error_message
        }))

    return results


def main():
    """Run batch search example."""
    print("=== PDF Price Search - Batch Example ===\n")

    # Define queries
    queries = [
        "2lb to zone 5",
        "5lb to zone 8",
        "10lb to zone 2",
        "1lb to zone 1",
        "15lb to zone 7",
    ]

    print(f"Searching for {len(queries)} queries...\n")

    # Perform batch search
    try:
        results = batch_search(queries)
    except Exception as e:
        print(f"Error: {e}")
        return

    # Display results
    successful = 0
    failed = 0

    print("Results:")
    print("-" * 80)

    for query, result in results:
        if result['success']:
            print(f"✓ {query:30s} → ${result['price']:6.2f} ({result['service']})")
            successful += 1
        else:
            print(f"✗ {query:30s} → Not found ({result['error']})")
            failed += 1

    print("-" * 80)
    print(f"\nSummary: {successful} found, {failed} not found")
    print("\n=== Example Complete ===")


if __name__ == "__main__":
    main()
