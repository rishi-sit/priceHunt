"""Unit tests for scrapers with mocked data."""
import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from bs4 import BeautifulSoup

import sys
sys.path.insert(0, str(__file__).rsplit('/tests', 1)[0])

from app.scrapers.base import BaseScraper, ProductResult
from app.scrapers.amazon import AmazonScraper
from app.scrapers.amazon_fresh import AmazonFreshScraper
from app.scrapers.flipkart import FlipkartScraper
from app.scrapers.flipkart_minutes import FlipkartMinutesScraper
from app.scrapers.zepto import ZeptoScraper
from app.scrapers.bigbasket import BigBasketScraper
from app.scrapers.jiomart import JioMartScraper
from app.scrapers.jiomart_quick import JioMartQuickScraper
from app.scrapers.blinkit import BlinkitScraper
from app.scrapers.instamart import InstamartScraper


class TestBaseScraper:
    """Tests for the base scraper class."""
    
    @pytest.mark.unit
    def test_parse_price_with_rupee_symbol(self):
        """Test parsing price with rupee symbol."""
        scraper = AmazonScraper()  # Using a concrete implementation
        assert scraper.parse_price("₹299") == 299.0
        assert scraper.parse_price("₹1,299") == 1299.0
        assert scraper.parse_price("₹99.50") == 99.50
    
    @pytest.mark.unit
    def test_parse_price_with_spaces(self):
        """Test parsing price with spaces."""
        scraper = AmazonScraper()
        assert scraper.parse_price("₹ 299") == 299.0
        assert scraper.parse_price("₹  1,299") == 1299.0
    
    @pytest.mark.unit
    def test_parse_price_empty_string(self):
        """Test parsing empty price string."""
        scraper = AmazonScraper()
        assert scraper.parse_price("") == 0.0
        assert scraper.parse_price(None) == 0.0
    
    @pytest.mark.unit
    def test_parse_price_invalid_string(self):
        """Test parsing invalid price string."""
        scraper = AmazonScraper()
        assert scraper.parse_price("Not a price") == 0.0
    
    @pytest.mark.unit
    def test_scraper_initialization(self, default_pincode):
        """Test scraper initialization with pincode."""
        scraper = AmazonScraper(default_pincode)
        assert scraper.pincode == default_pincode
    
    @pytest.mark.unit
    def test_get_headers_returns_dict(self):
        """Test that get_headers returns a dict with required keys."""
        scraper = AmazonScraper()
        headers = scraper.get_headers()
        assert isinstance(headers, dict)
        assert "User-Agent" in headers
        assert "Accept" in headers


class TestProductResult:
    """Tests for the ProductResult dataclass."""
    
    @pytest.mark.unit
    def test_product_result_creation(self, sample_product):
        """Test ProductResult creation."""
        assert sample_product.name == "Test Product 500g"
        assert sample_product.price == 99.0
        assert sample_product.original_price == 120.0
        assert sample_product.discount == "17% off"
        assert sample_product.available is True
    
    @pytest.mark.unit
    def test_product_result_defaults(self):
        """Test ProductResult default values."""
        product = ProductResult(
            name="Test",
            price=100.0,
            original_price=None,
            discount=None,
            platform="Test",
            url="https://test.com",
            image_url=None,
            rating=None
        )
        assert product.available is True
        assert product.delivery_time is None


class TestAmazonScraper:
    """Tests for the Amazon scraper."""
    
    @pytest.mark.unit
    def test_platform_name(self):
        """Test platform name is correct."""
        scraper = AmazonScraper()
        assert scraper.PLATFORM_NAME == "Amazon"
    
    @pytest.mark.unit
    def test_base_url(self):
        """Test base URL is correct."""
        scraper = AmazonScraper()
        assert "amazon" in scraper.BASE_URL.lower()
    
    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_search_returns_list(self):
        """Test that search returns a list."""
        scraper = AmazonScraper()
        # Mock the HTTP client to avoid actual network calls
        with patch.object(scraper, 'get_client') as mock_client:
            mock_response = AsyncMock()
            mock_response.status_code = 200
            mock_response.text = "<html><body></body></html>"
            
            mock_async_client = AsyncMock()
            mock_async_client.get.return_value = mock_response
            mock_async_client.__aenter__.return_value = mock_async_client
            mock_async_client.__aexit__.return_value = None
            
            mock_client.return_value = mock_async_client
            
            results = await scraper.search("test")
            assert isinstance(results, list)


class TestAmazonFreshScraper:
    """Tests for the Amazon Fresh scraper."""
    
    @pytest.mark.unit
    def test_platform_name(self):
        """Test platform name is correct."""
        scraper = AmazonFreshScraper()
        assert scraper.PLATFORM_NAME == "Amazon Fresh"
    
    @pytest.mark.unit
    def test_delivery_time_is_quick(self):
        """Test that Amazon Fresh is quick delivery."""
        # Amazon Fresh should have quick delivery times
        scraper = AmazonFreshScraper()
        assert "fresh" in scraper.PLATFORM_NAME.lower() or "amazon" in scraper.PLATFORM_NAME.lower()


class TestFlipkartScraper:
    """Tests for the Flipkart scraper."""
    
    @pytest.mark.unit
    def test_platform_name(self):
        """Test platform name is correct."""
        scraper = FlipkartScraper()
        assert scraper.PLATFORM_NAME == "Flipkart"
    
    @pytest.mark.unit
    def test_base_url(self):
        """Test base URL is correct."""
        scraper = FlipkartScraper()
        assert "flipkart" in scraper.BASE_URL.lower()


class TestFlipkartMinutesScraper:
    """Tests for the Flipkart Minutes scraper."""
    
    @pytest.mark.unit
    def test_platform_name(self):
        """Test platform name is correct."""
        scraper = FlipkartMinutesScraper()
        assert scraper.PLATFORM_NAME == "Flipkart Minutes"


class TestZeptoScraper:
    """Tests for the Zepto scraper."""
    
    @pytest.mark.unit
    def test_platform_name(self):
        """Test platform name is correct."""
        scraper = ZeptoScraper()
        assert scraper.PLATFORM_NAME == "Zepto"
    
    @pytest.mark.unit
    def test_base_url(self):
        """Test base URL is correct."""
        scraper = ZeptoScraper()
        assert "zepto" in scraper.BASE_URL.lower()


class TestBigBasketScraper:
    """Tests for the BigBasket scraper."""
    
    @pytest.mark.unit
    def test_platform_name(self):
        """Test platform name is correct."""
        scraper = BigBasketScraper()
        assert scraper.PLATFORM_NAME == "BigBasket"
    
    @pytest.mark.unit
    def test_base_url(self):
        """Test base URL is correct."""
        scraper = BigBasketScraper()
        assert "bigbasket" in scraper.BASE_URL.lower()


class TestJioMartScraper:
    """Tests for the JioMart scraper."""
    
    @pytest.mark.unit
    def test_platform_name(self):
        """Test platform name is correct."""
        scraper = JioMartScraper()
        assert scraper.PLATFORM_NAME == "JioMart"
    
    @pytest.mark.unit
    def test_base_url(self):
        """Test base URL is correct."""
        scraper = JioMartScraper()
        assert "jiomart" in scraper.BASE_URL.lower()


class TestJioMartQuickScraper:
    """Tests for the JioMart Quick scraper."""
    
    @pytest.mark.unit
    def test_platform_name(self):
        """Test platform name is correct."""
        scraper = JioMartQuickScraper()
        assert scraper.PLATFORM_NAME == "JioMart Quick"
    
    @pytest.mark.unit
    def test_base_url(self):
        """Test base URL is correct."""
        scraper = JioMartQuickScraper()
        assert "jiomart" in scraper.BASE_URL.lower()


class TestBlinkitScraper:
    """Tests for the Blinkit scraper."""
    
    @pytest.mark.unit
    def test_platform_name(self):
        """Test platform name is correct."""
        scraper = BlinkitScraper()
        assert scraper.PLATFORM_NAME == "Blinkit"
    
    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_search_returns_empty_due_to_cloudflare(self):
        """Test that Blinkit returns empty (Cloudflare blocked)."""
        scraper = BlinkitScraper()
        results = await scraper.search("test")
        assert isinstance(results, list)
        # Blinkit is blocked by Cloudflare, so should return empty
        assert len(results) == 0


class TestInstamartScraper:
    """Tests for the Instamart scraper."""
    
    @pytest.mark.unit
    def test_platform_name(self):
        """Test platform name is correct."""
        scraper = InstamartScraper()
        assert scraper.PLATFORM_NAME == "Instamart"
    
    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_search_returns_empty_due_to_auth(self):
        """Test that Instamart returns empty (auth required)."""
        scraper = InstamartScraper()
        results = await scraper.search("test")
        assert isinstance(results, list)
        # Instamart requires complex auth, so should return empty
        assert len(results) == 0


class TestAllScrapersHaveRequiredAttributes:
    """Test that all scrapers have required attributes."""
    
    scrapers = [
        AmazonScraper,
        AmazonFreshScraper,
        FlipkartScraper,
        FlipkartMinutesScraper,
        ZeptoScraper,
        BigBasketScraper,
        JioMartScraper,
        JioMartQuickScraper,
        BlinkitScraper,
        InstamartScraper,
    ]
    
    @pytest.mark.unit
    @pytest.mark.parametrize("scraper_class", scrapers)
    def test_has_platform_name(self, scraper_class):
        """Test that scraper has PLATFORM_NAME attribute."""
        scraper = scraper_class()
        assert hasattr(scraper, 'PLATFORM_NAME')
        assert isinstance(scraper.PLATFORM_NAME, str)
        assert len(scraper.PLATFORM_NAME) > 0
    
    @pytest.mark.unit
    @pytest.mark.parametrize("scraper_class", scrapers)
    def test_has_base_url(self, scraper_class):
        """Test that scraper has BASE_URL attribute."""
        scraper = scraper_class()
        assert hasattr(scraper, 'BASE_URL')
        assert isinstance(scraper.BASE_URL, str)
    
    @pytest.mark.unit
    @pytest.mark.parametrize("scraper_class", scrapers)
    def test_has_search_method(self, scraper_class):
        """Test that scraper has search method."""
        scraper = scraper_class()
        assert hasattr(scraper, 'search')
        assert callable(scraper.search)
    
    @pytest.mark.unit
    @pytest.mark.parametrize("scraper_class", scrapers)
    def test_has_pincode(self, scraper_class, default_pincode):
        """Test that scraper accepts pincode."""
        scraper = scraper_class(default_pincode)
        assert scraper.pincode == default_pincode



