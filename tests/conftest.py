"""Pytest configuration and shared fixtures."""
import pytest
import asyncio
from typing import Generator
from httpx import AsyncClient
from fastapi.testclient import TestClient

# Import the FastAPI app
import sys
sys.path.insert(0, str(__file__).rsplit('/tests', 1)[0])

from app.main import app
from app.scrapers.base import ProductResult


@pytest.fixture(scope="session")
def event_loop() -> Generator[asyncio.AbstractEventLoop, None, None]:
    """Create an instance of the event loop for the test session."""
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
def test_client() -> TestClient:
    """Create a test client for the FastAPI app."""
    return TestClient(app)


@pytest.fixture
async def async_client() -> AsyncClient:
    """Create an async test client for the FastAPI app."""
    async with AsyncClient(app=app, base_url="http://test") as client:
        yield client


@pytest.fixture
def sample_product() -> ProductResult:
    """Sample product result for testing."""
    return ProductResult(
        name="Test Product 500g",
        price=99.0,
        original_price=120.0,
        discount="17% off",
        platform="TestPlatform",
        url="https://example.com/product",
        image_url="https://example.com/image.jpg",
        rating=4.5,
        available=True,
        delivery_time="10-15 mins"
    )


@pytest.fixture
def sample_html_amazon():
    """Sample Amazon search results HTML."""
    return '''
    <div class="s-result-item" data-asin="B123456">
        <h2 class="a-size-mini">
            <a class="a-link-normal" href="/dp/B123456">
                <span>Amul Butter 500g</span>
            </a>
        </h2>
        <span class="a-price">
            <span class="a-offscreen">₹275</span>
        </span>
        <span class="a-price a-text-price">
            <span class="a-offscreen">₹300</span>
        </span>
        <img class="s-image" src="https://m.media-amazon.com/images/I/test.jpg" />
    </div>
    '''


@pytest.fixture
def sample_html_flipkart():
    """Sample Flipkart search results HTML."""
    return '''
    <div class="_1AtVbE">
        <a class="_1fQZEK" href="/product-slug">
            <div class="_4rR01T">Amul Butter 500g</div>
        </a>
        <div class="_30jeq3">₹275</div>
        <div class="_3I9_wc">₹300</div>
        <div class="_3LWZlK">4.2</div>
        <img class="_396cs4" src="https://rukminim1.flixcart.com/image/test.jpg" />
    </div>
    '''


@pytest.fixture
def default_pincode() -> str:
    """Default pincode for testing."""
    return "560087"


# Test data for various search queries
@pytest.fixture
def test_queries():
    """Common search queries for testing."""
    return [
        "milk 1 ltr",
        "amul butter",
        "apple 1kg",
        "rice 5kg",
        "sugar 1kg"
    ]



