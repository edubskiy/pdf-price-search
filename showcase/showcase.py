"""
PDF Price Search - Complete Showcase

This script demonstrates all features of the PDF Price Search system
using real PDFs from the /source folder.
"""

import sys
import time
from pathlib import Path
from typing import List, Dict, Any
from decimal import Decimal

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.application.container import Container
from src.application.use_cases.search_price_use_case import SearchPriceUseCase
from src.application.use_cases.list_services_use_case import ListServicesUseCase
from src.application.use_cases.load_data_use_case import LoadDataUseCase
from src.application.dto.search_request import SearchRequest


def print_section(title: str):
    """Print a formatted section header."""
    print("\n" + "=" * 70)
    print(f"  {title}")
    print("=" * 70)


def print_subsection(title: str):
    """Print a formatted subsection header."""
    print(f"\n--- {title} ---")


class Showcase:
    """Showcase demonstration class."""

    def __init__(self):
        """Initialize showcase."""
        self.container = Container()
        self.source_dir = project_root / "source"
        self.load_use_case = LoadDataUseCase(self.container)
        self.search_use_case = SearchPriceUseCase(self.container)
        self.list_use_case = ListServicesUseCase(self.container)
        self.metrics: Dict[str, Any] = {}

    def run(self):
        """Run complete showcase."""
        print_section("PDF PRICE SEARCH - COMPLETE SHOWCASE")

        print("\nThis showcase demonstrates:")
        print("  ✓ PDF loading from /source folder")
        print("  ✓ Natural language query parsing")
        print("  ✓ Price search functionality")
        print("  ✓ Service listing")
        print("  ✓ Error handling")
        print("  ✓ Performance metrics")
        print("  ✓ Caching effectiveness")

        # Run demonstrations
        self.demo_1_load_pdfs()
        self.demo_2_list_services()
        self.demo_3_basic_search()
        self.demo_4_advanced_search()
        self.demo_5_batch_search()
        self.demo_6_error_handling()
        self.demo_7_performance()
        self.demo_8_summary()

        print_section("SHOWCASE COMPLETE")

    def demo_1_load_pdfs(self):
        """Demonstrate PDF loading."""
        print_section("1. PDF LOADING")

        if not self.source_dir.exists():
            print(f"\n❌ Error: Source directory not found: {self.source_dir}")
            print("Please add PDF files to the 'source' directory")
            sys.exit(1)

        print(f"\nLoading PDFs from: {self.source_dir}")

        start_time = time.time()
        try:
            result = self.load_use_case.execute_from_directory(str(self.source_dir))
            load_time = time.time() - start_time

            loaded_count = result.get('loaded_count', 0)
            print(f"\n✓ Successfully loaded {loaded_count} PDF file(s)")
            print(f"  Load time: {load_time:.2f} seconds")

            self.metrics['load_time'] = load_time
            self.metrics['files_loaded'] = loaded_count

        except Exception as e:
            print(f"\n❌ Error loading PDFs: {e}")
            sys.exit(1)

    def demo_2_list_services(self):
        """Demonstrate service listing."""
        print_section("2. AVAILABLE SERVICES")

        try:
            services = self.list_use_case.execute()
            summary = self.list_use_case.execute_summary()

            print(f"\nTotal services: {len(services)}")
            print(f"Available zones: {summary['available_zones']}")
            print(f"Weight range: {summary['weight_range']['min']}-{summary['weight_range']['max']} lb")

            print_subsection("Service Details")

            for i, service in enumerate(services, 1):
                print(f"\n{i}. {service.name}")
                print(f"   Zones: {service.available_zones}")
                print(f"   Weight: {service.min_weight}-{service.max_weight} lb")
                print(f"   Source: {service.source_pdf}")

            self.metrics['total_services'] = len(services)

        except Exception as e:
            print(f"\n❌ Error listing services: {e}")

    def demo_3_basic_search(self):
        """Demonstrate basic search."""
        print_section("3. BASIC SEARCH")

        test_queries = [
            "2lb to zone 5",
            "5 pounds zone 8",
            "zone 2, 10 lbs",
        ]

        print("\nTesting basic search queries:\n")

        for query in test_queries:
            print(f"Query: '{query}'")

            start_time = time.time()
            request = SearchRequest(query=query)
            response = self.search_use_case.execute(request)
            search_time = (time.time() - start_time) * 1000

            if response.success:
                print(f"  ✓ Price: ${response.price} {response.currency}")
                print(f"    Service: {response.service}")
                print(f"    Zone: {response.zone}, Weight: {response.weight} lb")
                print(f"    Search time: {search_time:.2f} ms")
            else:
                print(f"  ✗ Not found: {response.error_message}")
            print()

    def demo_4_advanced_search(self):
        """Demonstrate advanced search with service filters."""
        print_section("4. ADVANCED SEARCH")

        # Get first service name for filtering
        services = self.list_use_case.execute()
        if not services:
            print("\nNo services available for advanced search")
            return

        service_name = services[0].name

        print(f"\nSearching with service filter: '{service_name}'")

        queries = [
            f"{service_name}, 3lb, zone 5",
            f"5 pounds to zone 8 {service_name}",
        ]

        for query in queries:
            print(f"\nQuery: '{query}'")

            request = SearchRequest(query=query)
            response = self.search_use_case.execute(request)

            if response.success:
                print(f"  ✓ Price: ${response.price}")
                print(f"    Service: {response.service}")
                print(f"    Source: {response.source_document}")
            else:
                print(f"  ✗ {response.error_message}")

    def demo_5_batch_search(self):
        """Demonstrate batch searching."""
        print_section("5. BATCH SEARCH")

        # Generate queries for different zones and weights
        zones = [1, 2, 3, 4, 5, 6, 7, 8]
        weights = [1, 2, 5, 10, 15, 20]

        queries = [
            f"{weight}lb to zone {zone}"
            for weight in weights[:3]
            for zone in zones[:4]
        ]

        print(f"\nSearching {len(queries)} queries in batch...\n")

        results = []
        total_time = 0

        for query in queries:
            start_time = time.time()
            request = SearchRequest(query=query)
            response = self.search_use_case.execute(request)
            search_time = (time.time() - start_time) * 1000

            total_time += search_time

            if response.success:
                results.append({
                    'query': query,
                    'price': response.price,
                    'service': response.service,
                    'time': search_time
                })

        # Show results
        successful = len(results)
        print(f"Results: {successful}/{len(queries)} queries successful")

        if results:
            avg_price = sum(r['price'] for r in results) / len(results)
            avg_time = total_time / len(queries)

            print(f"Average price: ${avg_price:.2f}")
            print(f"Average search time: {avg_time:.2f} ms")
            print(f"Total time: {total_time:.2f} ms")

            print_subsection("Sample Results")
            for result in results[:5]:
                print(f"  {result['query']:20s} → ${result['price']:6.2f} ({result['time']:.1f}ms)")

        self.metrics['batch_searches'] = len(queries)
        self.metrics['batch_successful'] = successful
        self.metrics['batch_avg_time'] = total_time / len(queries) if queries else 0

    def demo_6_error_handling(self):
        """Demonstrate error handling."""
        print_section("6. ERROR HANDLING")

        print("\nTesting error handling with invalid queries:\n")

        invalid_queries = [
            "",                          # Empty query
            "invalid query format",      # No zone or weight
            "zone 99, 5lb",             # Invalid zone
            "0lb to zone 5",            # Invalid weight
        ]

        for query in invalid_queries:
            print(f"Query: '{query}'")

            try:
                request = SearchRequest(query=query)
                response = self.search_use_case.execute(request)

                if not response.success:
                    print(f"  ✓ Handled gracefully: {response.error_message}")
                else:
                    print(f"  ⚠ Unexpected success")

            except Exception as e:
                print(f"  ✓ Exception caught: {type(e).__name__}: {e}")

            print()

    def demo_7_performance(self):
        """Demonstrate performance and caching."""
        print_section("7. PERFORMANCE & CACHING")

        query = "5lb to zone 5"

        print(f"\nQuery: '{query}'")
        print("\nTesting cache effectiveness:\n")

        # First search (cold cache)
        start_time = time.time()
        request = SearchRequest(query=query)
        response1 = self.search_use_case.execute(request)
        first_time = (time.time() - start_time) * 1000

        print(f"1st search (cold):   {first_time:.2f} ms")

        # Second search (warm cache)
        start_time = time.time()
        response2 = self.search_use_case.execute(request)
        second_time = (time.time() - start_time) * 1000

        print(f"2nd search (warm):   {second_time:.2f} ms")

        if second_time < first_time:
            improvement = ((first_time - second_time) / first_time) * 100
            print(f"Cache improvement:   {improvement:.1f}%")
        else:
            print(f"Cache improvement:   No significant improvement")

        # Third search
        start_time = time.time()
        response3 = self.search_use_case.execute(request)
        third_time = (time.time() - start_time) * 1000

        print(f"3rd search (cached): {third_time:.2f} ms")

        self.metrics['first_search_time'] = first_time
        self.metrics['cached_search_time'] = min(second_time, third_time)

    def demo_8_summary(self):
        """Show final summary and metrics."""
        print_section("8. SUMMARY & METRICS")

        print("\nPerformance Metrics:")
        print("-" * 50)
        print(f"PDF Loading:")
        print(f"  Files loaded:        {self.metrics.get('files_loaded', 0)}")
        print(f"  Load time:           {self.metrics.get('load_time', 0):.2f}s")

        print(f"\nServices:")
        print(f"  Total services:      {self.metrics.get('total_services', 0)}")

        print(f"\nSearch Performance:")
        if 'first_search_time' in self.metrics:
            print(f"  First search:        {self.metrics['first_search_time']:.2f} ms")
            print(f"  Cached search:       {self.metrics['cached_search_time']:.2f} ms")

        if 'batch_searches' in self.metrics:
            print(f"\nBatch Operations:")
            print(f"  Total queries:       {self.metrics['batch_searches']}")
            print(f"  Successful:          {self.metrics['batch_successful']}")
            print(f"  Average time:        {self.metrics['batch_avg_time']:.2f} ms")

        print("\nFeatures Demonstrated:")
        print("  ✓ PDF parsing and data extraction")
        print("  ✓ Natural language query parsing")
        print("  ✓ Price lookup and matching")
        print("  ✓ Service discovery and filtering")
        print("  ✓ Error handling and validation")
        print("  ✓ Caching and performance optimization")
        print("  ✓ Batch processing capabilities")


def main():
    """Run showcase."""
    try:
        showcase = Showcase()
        showcase.run()
    except KeyboardInterrupt:
        print("\n\nShowcase interrupted by user")
    except Exception as e:
        print(f"\n\n❌ Showcase error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
