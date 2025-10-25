"""
Basic search example.

This example demonstrates how to perform a simple price search.
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.application.container import Container
from src.application.use_cases.search_price_use_case import SearchPriceUseCase
from src.application.use_cases.load_data_use_case import LoadDataUseCase
from src.application.dto.search_request import SearchRequest


def main():
    """Run basic search example."""
    print("=== PDF Price Search - Basic Example ===\n")

    # 1. Initialize container
    print("1. Initializing application...")
    container = Container()

    # 2. Load PDF data
    print("2. Loading PDF data...")
    load_use_case = LoadDataUseCase(container)
    source_dir = project_root / "source"

    if not source_dir.exists():
        print(f"Error: Source directory not found: {source_dir}")
        print("Please add PDF files to the 'source' directory")
        return

    try:
        result = load_use_case.execute_from_directory(str(source_dir))
        print(f"   Loaded {result.get('loaded_count', 0)} PDF(s)")
    except Exception as e:
        print(f"   Error loading PDFs: {e}")
        return

    # 3. Perform search
    print("\n3. Searching for price...")
    search_use_case = SearchPriceUseCase(container)

    query = "2lb to zone 5"
    print(f"   Query: '{query}'")

    request = SearchRequest(query=query)
    response = search_use_case.execute(request)

    # 4. Display results
    print("\n4. Results:")
    if response.success:
        print(f"   ✓ Price found: ${response.price} {response.currency}")
        print(f"   Service: {response.service}")
        print(f"   Zone: {response.zone}")
        print(f"   Weight: {response.weight} lb")
        print(f"   Source: {response.source_document}")
        print(f"   Search time: {response.search_time_ms:.2f} ms")
    else:
        print(f"   ✗ No price found")
        print(f"   Error: {response.error_message}")

    print("\n=== Example Complete ===")


if __name__ == "__main__":
    main()
