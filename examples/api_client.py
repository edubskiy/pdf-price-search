"""
API client example.

This example demonstrates how to interact with the PDF Price Search API.
"""

import requests
import time
from typing import Optional


class PDFPriceSearchClient:
    """Client for PDF Price Search API."""

    def __init__(self, base_url: str = "http://localhost:8000/api"):
        """
        Initialize the API client.

        Args:
            base_url: Base URL of the API.
        """
        self.base_url = base_url.rstrip('/')

    def search_price(self, query: str, use_cache: bool = True) -> dict:
        """
        Search for a shipping price.

        Args:
            query: Search query.
            use_cache: Whether to use cache.

        Returns:
            Search result dictionary.
        """
        response = requests.post(
            f"{self.base_url}/search",
            json={"query": query, "use_cache": use_cache}
        )
        response.raise_for_status()
        return response.json()

    def list_services(self) -> dict:
        """
        List all available services.

        Returns:
            Dictionary with services list.
        """
        response = requests.get(f"{self.base_url}/services")
        response.raise_for_status()
        return response.json()

    def get_service(self, service_name: str) -> dict:
        """
        Get details for a specific service.

        Args:
            service_name: Name of the service.

        Returns:
            Service details dictionary.
        """
        response = requests.get(f"{self.base_url}/services/{service_name}")
        response.raise_for_status()
        return response.json()

    def get_services_summary(self) -> dict:
        """
        Get summary of all services.

        Returns:
            Summary dictionary.
        """
        response = requests.get(f"{self.base_url}/services/summary")
        response.raise_for_status()
        return response.json()

    def load_pdfs(self, directory: Optional[str] = None, recursive: bool = False) -> dict:
        """
        Load PDFs from a directory.

        Args:
            directory: Directory path (optional, uses default if None).
            recursive: Whether to search recursively.

        Returns:
            Load result dictionary.
        """
        payload = {"recursive": recursive}
        if directory:
            payload["directory"] = directory

        response = requests.post(f"{self.base_url}/load", json=payload)
        response.raise_for_status()
        return response.json()

    def health_check(self) -> dict:
        """
        Check API health.

        Returns:
            Health status dictionary.
        """
        response = requests.get(f"{self.base_url}/health")
        response.raise_for_status()
        return response.json()

    def get_cache_stats(self) -> dict:
        """
        Get cache statistics.

        Returns:
            Cache statistics dictionary.
        """
        response = requests.get(f"{self.base_url}/cache/stats")
        response.raise_for_status()
        return response.json()

    def clear_cache(self) -> dict:
        """
        Clear the cache.

        Returns:
            Success message dictionary.
        """
        response = requests.delete(f"{self.base_url}/cache")
        response.raise_for_status()
        return response.json()


def main():
    """Run API client example."""
    print("=== PDF Price Search - API Client Example ===\n")

    # Initialize client
    client = PDFPriceSearchClient()

    # 1. Health check
    print("1. Checking API health...")
    try:
        health = client.health_check()
        print(f"   Status: {health['status']}")
        print(f"   Version: {health['version']}")
        print(f"   Services loaded: {health['services_loaded']}")
    except requests.exceptions.ConnectionError:
        print("   Error: API server not running")
        print("   Please start the API server with: make run")
        return

    # 2. List services
    print("\n2. Listing available services...")
    services = client.list_services()
    print(f"   Found {services['total_count']} service(s)")
    for service in services['services'][:3]:  # Show first 3
        print(f"   - {service['name']}")

    # 3. Search for a price
    print("\n3. Searching for price...")
    query = "2lb to zone 5"
    print(f"   Query: '{query}'")

    result = client.search_price(query)
    if result['success']:
        print(f"   ✓ Price: ${result['price']} {result['currency']}")
        print(f"   Service: {result['service']}")
        print(f"   Search time: {result['search_time_ms']:.2f} ms")
    else:
        print(f"   ✗ Not found: {result['error_message']}")

    # 4. Get cache stats
    print("\n4. Cache statistics...")
    cache_stats = client.get_cache_stats()
    print(f"   Enabled: {cache_stats['enabled']}")
    print(f"   Size: {cache_stats['size']}")

    print("\n=== Example Complete ===")


if __name__ == "__main__":
    main()
