"""
End-to-end tests for the API application.

These tests verify the API interface works correctly with real data.
"""

import pytest
from fastapi.testclient import TestClient

from src.presentation.api.main import app


@pytest.fixture
def client():
    """Create test client."""
    return TestClient(app)


@pytest.mark.e2e
class TestAPISearch:
    """Test API search endpoint."""

    def test_search_basic_query(self, client):
        """Test basic search query."""
        response = client.post(
            "/api/v1/search",
            json={
                "query": "FedEx 2Day, Zone 5, 3 lb",
                "use_cache": True
            }
        )

        assert response.status_code == 200
        data = response.json()
        assert "success" in data
        assert "search_time_ms" in data

    def test_search_with_cache_disabled(self, client):
        """Test search with cache disabled."""
        response = client.post(
            "/api/v1/search",
            json={
                "query": "Standard Overnight, Zone 2, 10 lb",
                "use_cache": False
            }
        )

        assert response.status_code == 200
        data = response.json()
        assert "success" in data

    def test_search_invalid_query_empty(self, client):
        """Test search with empty query."""
        response = client.post(
            "/api/v1/search",
            json={
                "query": "",
                "use_cache": True
            }
        )

        # Should return validation error
        assert response.status_code in [400, 422]

    def test_search_missing_query_field(self, client):
        """Test search with missing query field."""
        response = client.post(
            "/api/v1/search",
            json={
                "use_cache": True
            }
        )

        # Should return validation error
        assert response.status_code == 422

    def test_search_multiple_queries(self, client):
        """Test multiple search queries."""
        queries = [
            "FedEx 2Day, Zone 5, 3 lb",
            "Standard Overnight, Zone 2, 10 lb",
            "Express Saver, Zone 8, 1 lb"
        ]

        for query in queries:
            response = client.post(
                "/api/v1/search",
                json={"query": query, "use_cache": True}
            )

            assert response.status_code == 200
            assert "success" in response.json()


@pytest.mark.e2e
class TestAPIServices:
    """Test API services endpoints."""

    def test_list_services(self, client):
        """Test list services endpoint."""
        response = client.get("/api/v1/services")

        assert response.status_code == 200
        data = response.json()
        assert "services" in data
        assert "total_count" in data
        assert isinstance(data["services"], list)

    def test_get_services_summary(self, client):
        """Test services summary endpoint."""
        response = client.get("/api/v1/services/summary")

        assert response.status_code == 200
        data = response.json()
        assert "total_services" in data
        assert "available_zones" in data
        assert "weight_range" in data

    def test_get_service_details_existing(self, client):
        """Test get service details for existing service."""
        # First get list of services
        list_response = client.get("/api/v1/services")
        services = list_response.json()["services"]

        if services:
            # Get details for first service
            service_name = services[0]["name"]
            response = client.get(f"/api/v1/services/{service_name}")

            assert response.status_code == 200
            data = response.json()
            assert data["name"] == service_name
            assert "available_zones" in data
            assert "min_weight" in data
            assert "max_weight" in data

    def test_get_service_details_nonexistent(self, client):
        """Test get service details for non-existent service."""
        response = client.get("/api/v1/services/NonExistentService")

        assert response.status_code == 404


@pytest.mark.e2e
class TestAPILoad:
    """Test API load endpoint."""

    def test_load_default_directory(self, client):
        """Test load from default directory."""
        response = client.post(
            "/api/v1/load",
            json={"recursive": False}
        )

        assert response.status_code in [200, 500]  # 500 if directory doesn't exist
        if response.status_code == 200:
            data = response.json()
            assert "success" in data
            assert "total_files" in data
            assert "loaded_count" in data
            assert "failed_count" in data

    def test_load_with_recursive(self, client):
        """Test load with recursive option."""
        response = client.post(
            "/api/v1/load",
            json={"recursive": True}
        )

        assert response.status_code in [200, 500]


@pytest.mark.e2e
class TestAPIHealth:
    """Test API health endpoint."""

    def test_health_check(self, client):
        """Test health check endpoint."""
        response = client.get("/api/v1/health")

        assert response.status_code == 200
        data = response.json()
        assert "status" in data
        assert "version" in data
        assert "services_loaded" in data
        assert "cache_enabled" in data


@pytest.mark.e2e
class TestAPICache:
    """Test API cache endpoints."""

    def test_get_cache_stats(self, client):
        """Test get cache statistics."""
        response = client.get("/api/v1/cache/stats")

        assert response.status_code == 200
        data = response.json()
        assert "enabled" in data
        assert "size" in data
        assert "hits" in data
        assert "misses" in data
        assert "hit_rate" in data

    def test_clear_cache(self, client):
        """Test clear cache endpoint."""
        response = client.delete("/api/v1/cache")

        # Should succeed if cache is enabled, or fail with 400 if disabled
        assert response.status_code in [200, 400]


@pytest.mark.e2e
class TestAPIRoot:
    """Test API root endpoints."""

    def test_root_endpoint(self, client):
        """Test root endpoint."""
        response = client.get("/")

        assert response.status_code == 200
        data = response.json()
        assert "name" in data
        assert "version" in data
        assert "documentation" in data
        assert "endpoints" in data

    def test_docs_endpoint(self, client):
        """Test OpenAPI docs endpoint."""
        response = client.get("/docs")

        assert response.status_code == 200

    def test_redoc_endpoint(self, client):
        """Test ReDoc endpoint."""
        response = client.get("/redoc")

        assert response.status_code == 200


@pytest.mark.e2e
class TestAPIConcurrency:
    """Test API concurrent requests."""

    def test_concurrent_searches(self, client):
        """Test multiple concurrent search requests."""
        import concurrent.futures

        queries = [
            "FedEx 2Day, Zone 5, 3 lb",
            "Standard Overnight, Zone 2, 10 lb",
            "Express Saver, Zone 8, 1 lb",
            "Ground, Zone 6, 12 lb",
            "Priority Overnight, Zone 3, 5 lb"
        ]

        def make_request(query):
            return client.post(
                "/api/v1/search",
                json={"query": query, "use_cache": True}
            )

        # Execute concurrent requests
        with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
            futures = [executor.submit(make_request, q) for q in queries]
            responses = [f.result() for f in concurrent.futures.as_completed(futures)]

        # All requests should succeed
        for response in responses:
            assert response.status_code == 200
            assert "success" in response.json()
