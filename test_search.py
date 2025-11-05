"""
Test different query formats
"""

import sys
from pathlib import Path

project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from src.application.container import Container


def main():
    print("=" * 70)
    print("  TESTING QUERY FORMATS")
    print("=" * 70)

    # Initialize
    container = Container()
    container.ensure_ready()

    # Load data
    load_use_case = container.load_data_use_case()
    source_dir = project_root / "source"
    result = load_use_case.execute_from_directory(str(source_dir))

    print(f"\nLoaded {result.get('loaded_count', 0)} PDF file(s)")

    # List services first
    list_use_case = container.list_services_use_case()
    services = list_use_case.execute()

    if not services:
        print("\nNo services loaded!")
        return

    service_name = services[0].name
    print(f"\nUsing service: {service_name}")
    print(f"Available zones: {services[0].available_zones}")
    print(f"Weight range: {services[0].min_weight}-{services[0].max_weight} lb")

    # Test different query formats
    search_use_case = container.search_price_use_case()

    test_queries = [
        # Comma-separated format (should work)
        f"{service_name}, zone 5, 2 lb",
        f"{service_name}, zone 8, 5 lb",
        f"FedEx 2Day, zone 2, 10 lb",
        f"FedEx First Overnight, zone 3, 3 lb",
        f"FedEx Express Saver, zone 5, 1 lb",

        # Space separated (might not work due to bug)
        # "FedEx 2Day zone 5 2lb",
    ]

    print("\n" + "=" * 70)
    print("  SEARCH RESULTS")
    print("=" * 70)

    for query in test_queries:
        print(f"\nQuery: '{query}'")
        response = search_use_case.execute(query)

        if response.success:
            print(f"  ✓ SUCCESS!")
            print(f"    Price: ${response.price} {response.currency}")
            print(f"    Service: {response.service}")
            print(f"    Zone: {response.zone}, Weight: {response.weight} lb")
            print(f"    Time: {response.search_time_ms:.2f} ms")
        else:
            print(f"  ✗ FAILED: {response.error_message}")


if __name__ == "__main__":
    main()
