"""
Quick Demo - Simple working example of PDF Price Search
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from src.application.container import Container


def main():
    print("=" * 70)
    print("  PDF PRICE SEARCH - QUICK DEMO")
    print("=" * 70)

    # Initialize container
    print("\n1. Initializing system...")
    container = Container()
    container.ensure_ready()
    print("   ✓ System initialized")

    # Load PDFs
    print("\n2. Loading PDF data...")
    source_dir = project_root / "source"

    if not source_dir.exists():
        print(f"   ✗ Source directory not found: {source_dir}")
        return

    pdf_files = list(source_dir.glob("*.pdf"))
    print(f"   Found {len(pdf_files)} PDF file(s):")
    for pdf in pdf_files:
        print(f"      - {pdf.name}")

    # Use the container's load_data_use_case
    load_use_case = container.load_data_use_case()

    try:
        result = load_use_case.execute_from_directory(str(source_dir))
        loaded = result.get('loaded_count', 0)
        failed = result.get('failed_count', 0)

        print(f"\n   ✓ Loaded: {loaded} file(s)")
        if failed > 0:
            print(f"   ✗ Failed: {failed} file(s)")
            for fail in result.get('failed_files', []):
                print(f"      - {Path(fail['file']).name}: {fail['error']}")
    except Exception as e:
        print(f"   ✗ Error loading PDFs: {e}")
        import traceback
        traceback.print_exc()
        return

    # List services
    print("\n3. Available services:")
    list_use_case = container.list_services_use_case()

    try:
        services = list_use_case.execute()
        print(f"   Found {len(services)} service(s):\n")

        for i, service in enumerate(services, 1):
            print(f"   {i}. {service.name}")
            print(f"      Zones: {min(service.available_zones)}-{max(service.available_zones)}")
            print(f"      Weight: {service.min_weight}-{service.max_weight} lb")
            print(f"      Source: {service.source_pdf}")
            print()
    except Exception as e:
        print(f"   ✗ Error listing services: {e}")
        import traceback
        traceback.print_exc()
        return

    # Search prices
    print("\n4. Testing price searches:")
    search_use_case = container.search_price_use_case()

    test_queries = [
        "2lb to zone 5",           # Space-separated format (now works!)
        "5lb to zone 8",           # Space-separated format (now works!)
        "10lb to zone 2",          # Space-separated format (now works!)
    ]

    print(f"   Running {len(test_queries)} test queries:\n")

    for query in test_queries:
        response = search_use_case.execute(query)

        print(f"   Query: '{query}'")
        if response.success:
            print(f"      ✓ Price: ${response.price} {response.currency}")
            print(f"        Service: {response.service}")
            print(f"        Zone: {response.zone}, Weight: {response.weight} lb")
            print(f"        Time: {response.search_time_ms:.2f} ms")
        else:
            print(f"      ✗ {response.error_message}")
        print()

    print("=" * 70)
    print("  DEMO COMPLETE")
    print("=" * 70)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nDemo interrupted by user")
    except Exception as e:
        print(f"\n\n❌ Demo error: {e}")
        import traceback
        traceback.print_exc()
