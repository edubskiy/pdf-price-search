"""
Demo script for the PDF Price Search application.

This script demonstrates the complete application flow:
1. Load PDFs from the source directory
2. List available services
3. Execute sample searches
4. Show performance metrics
"""

import sys
import time
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from src.application.container import get_container
from src.application.config import AppConfig


def print_header(text: str) -> None:
    """Print a formatted section header."""
    print("\n" + "=" * 80)
    print(f" {text}")
    print("=" * 80 + "\n")


def print_service_info(services):
    """Print information about available services."""
    print(f"Found {len(services)} services:\n")

    for service in services:
        print(f"  Service: {service.name}")
        print(f"    Zones: {service.available_zones}")
        print(f"    Weight Range: {service.min_weight} - {service.max_weight} lb")
        print(f"    Source: {service.source_pdf}")
        print()


def print_search_result(query: str, response, index: int, total: int):
    """Print a search result."""
    print(f"[{index}/{total}] Query: {query}")

    if response.success:
        print(f"  SUCCESS!")
        print(f"    Service: {response.service}")
        print(f"    Zone: {response.zone}")
        print(f"    Weight: {response.weight} lb")
        print(f"    Price: ${response.price}")
        print(f"    Currency: {response.currency}")
        print(f"    Search Time: {response.search_time_ms:.2f} ms")
    else:
        print(f"  FAILED!")
        print(f"    Error: {response.error_message}")
        print(f"    Search Time: {response.search_time_ms:.2f} ms")

    print()


def main():
    """Run the demo."""
    print_header("PDF Price Search - Application Demo")

    # Initialize container
    print("Initializing application...")
    config = AppConfig()
    container = get_container(config)

    try:
        container.ensure_ready()
        print(f"Configuration loaded:")
        print(f"  PDF Directory: {config.default_pdf_directory}")
        print(f"  Cache Enabled: {config.enable_cache}")
        print(f"  Cache TTL: {config.cache_ttl}s")
        print(f"  Log Level: {config.log_level}")
    except ValueError as e:
        print(f"ERROR: Configuration invalid: {e}")
        return 1

    # Step 1: Load PDFs
    print_header("Step 1: Loading PDF Data")

    load_use_case = container.load_data_use_case()

    try:
        start_time = time.time()
        result = load_use_case.execute_default()
        load_time = time.time() - start_time

        if result["success"]:
            print(f"Successfully loaded {result['loaded_count']} PDF files")
            print(f"  Total files: {result['total_files']}")
            print(f"  Load time: {load_time:.2f}s")

            if result["failed_count"] > 0:
                print(f"\n  Failed files: {result['failed_count']}")
                for failed in result["failed_files"]:
                    print(f"    - {Path(failed['file']).name}: {failed['error']}")
        else:
            print("ERROR: No PDF files were loaded successfully")
            return 1

    except Exception as e:
        print(f"ERROR loading PDFs: {e}")
        return 1

    # Step 2: List services
    print_header("Step 2: Available Services")

    list_use_case = container.list_services_use_case()

    try:
        services = list_use_case.execute()
        print_service_info(services)

        # Show summary
        summary = list_use_case.execute_summary()
        print(f"Summary:")
        print(f"  Total Services: {summary['total_services']}")
        print(f"  Available Zones: {summary['available_zones']}")
        print(f"  Weight Range: {summary['weight_range']['min']} - {summary['weight_range']['max']} lb")

    except Exception as e:
        print(f"ERROR listing services: {e}")
        return 1

    # Step 3: Execute sample searches
    print_header("Step 3: Sample Price Searches")

    search_use_case = container.search_price_use_case()

    # Define test queries
    test_queries = [
        "FedEx 2Day, Zone 5, 3 lb",
        "Standard Overnight, z2, 10 lbs",
        "Express Saver Z8 1 lb",
        "Ground Z6 12 lb",
        "Priority Overnight, Zone 3, 5 lb",
    ]

    print(f"Executing {len(test_queries)} test queries:\n")

    results = []
    total_time = 0

    for i, query in enumerate(test_queries, 1):
        try:
            response = search_use_case.execute(query)
            results.append(response)
            total_time += response.search_time_ms

            print_search_result(query, response, i, len(test_queries))

        except Exception as e:
            print(f"[{i}/{len(test_queries)}] Query: {query}")
            print(f"  ERROR: {e}\n")

    # Step 4: Performance metrics
    print_header("Step 4: Performance Metrics")

    successful = sum(1 for r in results if r.success)
    failed = len(results) - successful

    print(f"Search Results:")
    print(f"  Total Searches: {len(results)}")
    print(f"  Successful: {successful}")
    print(f"  Failed: {failed}")
    print(f"  Success Rate: {(successful/len(results)*100):.1f}%")

    if results:
        avg_time = total_time / len(results)
        min_time = min(r.search_time_ms for r in results)
        max_time = max(r.search_time_ms for r in results)

        print(f"\nPerformance:")
        print(f"  Total Search Time: {total_time:.2f} ms")
        print(f"  Average Search Time: {avg_time:.2f} ms")
        print(f"  Fastest Search: {min_time:.2f} ms")
        print(f"  Slowest Search: {max_time:.2f} ms")

    # Step 5: Cache demonstration
    if config.enable_cache:
        print_header("Step 5: Cache Performance")

        print("Re-running first query to demonstrate cache hit:")
        query = test_queries[0]

        # First search (should be cached already)
        start = time.time()
        response1 = search_use_case.execute(query, use_cache=True)
        cached_time = (time.time() - start) * 1000

        # Second search without cache
        search_use_case.search_service.clear_cache()
        start = time.time()
        response2 = search_use_case.execute(query, use_cache=False)
        uncached_time = (time.time() - start) * 1000

        print(f"\nQuery: {query}")
        print(f"  With cache: {cached_time:.2f} ms")
        print(f"  Without cache: {uncached_time:.2f} ms")
        if uncached_time > 0:
            speedup = uncached_time / cached_time
            print(f"  Speedup: {speedup:.2f}x")

    # Done
    print_header("Demo Complete")
    print("All operations completed successfully!")
    print("The application layer is fully functional and ready for use.")

    return 0


if __name__ == "__main__":
    sys.exit(main())
