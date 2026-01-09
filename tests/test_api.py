"""API tests for FastAPI endpoints."""
import pytest
from fastapi.testclient import TestClient

import sys
sys.path.insert(0, str(__file__).rsplit('/tests', 1)[0])

from app.main import app


@pytest.fixture
def client():
    """Create a test client."""
    return TestClient(app)


class TestHomeEndpoint:
    """Tests for the home page endpoint."""
    
    @pytest.mark.api
    def test_home_returns_html(self, client):
        """Test that home page returns HTML."""
        response = client.get("/")
        assert response.status_code == 200
        assert "text/html" in response.headers["content-type"]
    
    @pytest.mark.api
    def test_home_contains_title(self, client):
        """Test that home page contains the app title."""
        response = client.get("/")
        assert response.status_code == 200
        # Check for some expected content
        assert "price" in response.text.lower() or "search" in response.text.lower()


class TestSearchEndpoint:
    """Tests for the search API endpoint."""
    
    @pytest.mark.api
    def test_search_requires_query(self, client):
        """Test that search requires a query parameter."""
        response = client.get("/api/search")
        assert response.status_code == 422  # Validation error
    
    @pytest.mark.api
    def test_search_with_query(self, client):
        """Test search with a query parameter."""
        response = client.get("/api/search?q=test")
        assert response.status_code == 200
        data = response.json()
        assert "query" in data
        assert "results" in data
        assert data["query"] == "test"
    
    @pytest.mark.api
    def test_search_with_pincode(self, client):
        """Test search with query and pincode."""
        response = client.get("/api/search?q=milk&pincode=560087")
        assert response.status_code == 200
        data = response.json()
        assert "results" in data
    
    @pytest.mark.api
    def test_search_response_structure(self, client):
        """Test that search response has correct structure."""
        response = client.get("/api/search?q=butter")
        assert response.status_code == 200
        data = response.json()
        
        # Check required fields
        assert "query" in data
        assert "results" in data
        assert "lowest_price" in data
        assert "total_platforms" in data
        
        # Results should be a list
        assert isinstance(data["results"], list)


class TestStreamSearchEndpoint:
    """Tests for the streaming search endpoint."""
    
    @pytest.mark.api
    def test_stream_search_requires_query(self, client):
        """Test that stream search requires a query parameter."""
        response = client.get("/api/search/stream")
        assert response.status_code == 422
    
    @pytest.mark.api
    def test_stream_search_returns_event_stream(self, client):
        """Test that stream search returns event stream."""
        # TestClient doesn't support stream=True, just check status and content-type
        with client:
            response = client.get("/api/search/stream?q=test")
            assert response.status_code == 200
            assert "text/event-stream" in response.headers["content-type"]


class TestPlatformsEndpoint:
    """Tests for the platforms API endpoint."""
    
    @pytest.mark.api
    def test_get_platforms(self, client):
        """Test getting list of platforms."""
        response = client.get("/api/platforms")
        assert response.status_code == 200
        data = response.json()
        assert "platforms" in data
        assert isinstance(data["platforms"], list)
    
    @pytest.mark.api
    def test_platforms_have_required_fields(self, client):
        """Test that platforms have required fields."""
        response = client.get("/api/platforms")
        data = response.json()
        
        for platform in data["platforms"]:
            assert "name" in platform
            assert "type" in platform
            assert "delivery" in platform
            assert "color" in platform
    
    @pytest.mark.api
    def test_platforms_include_expected(self, client):
        """Test that expected platforms are included."""
        response = client.get("/api/platforms")
        data = response.json()
        
        platform_names = [p["name"] for p in data["platforms"]]
        
        # Check for some expected platforms
        expected = ["Amazon", "Flipkart", "Zepto"]
        for name in expected:
            assert any(name in pn for pn in platform_names), f"{name} should be in platforms"


class TestCacheEndpoints:
    """Tests for cache-related endpoints."""
    
    @pytest.mark.api
    def test_cache_stats(self, client):
        """Test getting cache statistics."""
        response = client.get("/api/cache/stats")
        assert response.status_code == 200
        data = response.json()
        
        # Should have some cache stats
        assert isinstance(data, dict)
    
    @pytest.mark.api
    def test_cache_clear(self, client):
        """Test clearing the cache."""
        response = client.post("/api/cache/clear")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "cleared"


class TestHealthEndpoint:
    """Tests for the health check endpoint."""
    
    @pytest.mark.api
    def test_health_check(self, client):
        """Test health check endpoint."""
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert "service" in data


class TestStaticFiles:
    """Tests for static file serving."""
    
    @pytest.mark.api
    def test_css_served(self, client):
        """Test that CSS is served."""
        response = client.get("/static/css/style.css")
        assert response.status_code == 200
        assert "text/css" in response.headers["content-type"]
    
    @pytest.mark.api
    def test_js_served(self, client):
        """Test that JavaScript is served."""
        response = client.get("/static/js/app.js")
        assert response.status_code == 200
        assert "javascript" in response.headers["content-type"]


class TestBulkSearchEndpoint:
    """Tests for bulk search endpoint."""
    
    @pytest.mark.api
    def test_bulk_search(self, client):
        """Test bulk search with multiple products."""
        response = client.post(
            "/api/search/bulk",
            json={
                "products": ["milk", "bread"],
                "pincode": "560087"
            }
        )
        assert response.status_code == 200
        data = response.json()
        assert "comparisons" in data
        assert isinstance(data["comparisons"], list)
    
    @pytest.mark.api
    def test_bulk_search_empty_products(self, client):
        """Test bulk search with empty products list."""
        response = client.post(
            "/api/search/bulk",
            json={
                "products": [],
                "pincode": "560087"
            }
        )
        assert response.status_code == 200
        data = response.json()
        assert data["comparisons"] == []


class TestErrorHandling:
    """Tests for error handling."""
    
    @pytest.mark.api
    def test_404_for_unknown_endpoint(self, client):
        """Test 404 for unknown endpoints."""
        response = client.get("/api/unknown")
        assert response.status_code == 404
    
    @pytest.mark.api
    def test_method_not_allowed(self, client):
        """Test method not allowed."""
        response = client.post("/api/search?q=test")
        assert response.status_code == 405

