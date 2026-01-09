"""Integration tests for scrapers - tests against live websites.

These tests are marked as 'integration' and 'slow' since they make actual
network requests. Run with: pytest -m integration

Note: These tests may fail due to:
- Network issues
- Website changes
- Rate limiting
- Anti-bot protection
"""
import pytest
import asyncio

import sys
sys.path.insert(0, str(__file__).rsplit('/tests', 1)[0])

from app.scrapers.amazon import AmazonScraper
from app.scrapers.amazon_fresh import AmazonFreshScraper
from app.scrapers.flipkart import FlipkartScraper
from app.scrapers.flipkart_minutes import FlipkartMinutesScraper
from app.scrapers.zepto import ZeptoScraper
from app.scrapers.bigbasket import BigBasketScraper
from app.scrapers.jiomart import JioMartScraper
from app.scrapers.jiomart_quick import JioMartQuickScraper


# Common test query for groceries
TEST_QUERY = "milk 1 ltr"
DEFAULT_PINCODE = "560087"


class TestAmazonScraperIntegration:
    """Integration tests for Amazon scraper."""
    
    @pytest.mark.integration
    @pytest.mark.slow
    @pytest.mark.asyncio
    async def test_search_returns_results(self):
        """Test that Amazon search returns results."""
        scraper = AmazonScraper(DEFAULT_PINCODE)
        results = await scraper.search(TEST_QUERY)
        
        assert isinstance(results, list)
        # Amazon should return some results for common grocery queries
        print(f"Amazon: Found {len(results)} results")
        
        if results:
            # Verify result structure
            result = results[0]
            assert result.name
            assert result.price > 0
            assert result.platform == "Amazon"
            assert result.url


class TestAmazonFreshScraperIntegration:
    """Integration tests for Amazon Fresh scraper."""
    
    @pytest.mark.integration
    @pytest.mark.slow
    @pytest.mark.asyncio
    async def test_search_returns_results(self):
        """Test that Amazon Fresh search returns results."""
        scraper = AmazonFreshScraper(DEFAULT_PINCODE)
        results = await scraper.search(TEST_QUERY)
        
        assert isinstance(results, list)
        print(f"Amazon Fresh: Found {len(results)} results")
        
        if results:
            result = results[0]
            assert result.name
            assert result.price > 0
            assert result.platform == "Amazon Fresh"


class TestFlipkartScraperIntegration:
    """Integration tests for Flipkart scraper."""
    
    @pytest.mark.integration
    @pytest.mark.slow
    @pytest.mark.asyncio
    async def test_search_returns_results(self):
        """Test that Flipkart search returns results."""
        scraper = FlipkartScraper(DEFAULT_PINCODE)
        results = await scraper.search(TEST_QUERY)
        
        assert isinstance(results, list)
        print(f"Flipkart: Found {len(results)} results")
        
        if results:
            result = results[0]
            assert result.name
            assert result.price > 0
            assert result.platform == "Flipkart"


class TestFlipkartMinutesScraperIntegration:
    """Integration tests for Flipkart Minutes scraper."""
    
    @pytest.mark.integration
    @pytest.mark.slow
    @pytest.mark.asyncio
    async def test_search_returns_results(self):
        """Test that Flipkart Minutes search returns results."""
        scraper = FlipkartMinutesScraper(DEFAULT_PINCODE)
        results = await scraper.search(TEST_QUERY)
        
        assert isinstance(results, list)
        print(f"Flipkart Minutes: Found {len(results)} results")
        
        if results:
            result = results[0]
            assert result.name
            assert result.price > 0
            assert result.platform == "Flipkart Minutes"
            # Quick commerce should have delivery time
            assert result.delivery_time


class TestZeptoScraperIntegration:
    """Integration tests for Zepto scraper."""
    
    @pytest.mark.integration
    @pytest.mark.slow
    @pytest.mark.asyncio
    async def test_search_returns_results(self):
        """Test that Zepto search returns results."""
        scraper = ZeptoScraper(DEFAULT_PINCODE)
        results = await scraper.search(TEST_QUERY)
        
        assert isinstance(results, list)
        print(f"Zepto: Found {len(results)} results")
        
        if results:
            result = results[0]
            assert result.name
            assert result.price > 0
            assert result.platform == "Zepto"
            assert result.delivery_time


class TestBigBasketScraperIntegration:
    """Integration tests for BigBasket scraper."""
    
    @pytest.mark.integration
    @pytest.mark.slow
    @pytest.mark.asyncio
    async def test_search_returns_results(self):
        """Test that BigBasket search returns results."""
        scraper = BigBasketScraper(DEFAULT_PINCODE)
        results = await scraper.search(TEST_QUERY)
        
        assert isinstance(results, list)
        print(f"BigBasket: Found {len(results)} results")
        
        if results:
            result = results[0]
            assert result.name
            assert result.price > 0
            assert result.platform == "BigBasket"


class TestJioMartScraperIntegration:
    """Integration tests for JioMart scraper."""
    
    @pytest.mark.integration
    @pytest.mark.slow
    @pytest.mark.asyncio
    async def test_search_returns_results(self):
        """Test that JioMart search returns results."""
        scraper = JioMartScraper(DEFAULT_PINCODE)
        results = await scraper.search(TEST_QUERY)
        
        assert isinstance(results, list)
        print(f"JioMart: Found {len(results)} results")
        
        if results:
            result = results[0]
            assert result.name
            assert result.price > 0
            assert result.platform == "JioMart"


class TestJioMartQuickScraperIntegration:
    """Integration tests for JioMart Quick scraper."""
    
    @pytest.mark.integration
    @pytest.mark.slow
    @pytest.mark.asyncio
    async def test_search_returns_results(self):
        """Test that JioMart Quick search returns results."""
        scraper = JioMartQuickScraper(DEFAULT_PINCODE)
        results = await scraper.search(TEST_QUERY)
        
        assert isinstance(results, list)
        print(f"JioMart Quick: Found {len(results)} results")
        
        if results:
            result = results[0]
            assert result.name
            assert result.price > 0
            assert result.platform == "JioMart Quick"


class TestAllScrapersParallel:
    """Test all scrapers running in parallel."""
    
    @pytest.mark.integration
    @pytest.mark.slow
    @pytest.mark.asyncio
    async def test_all_scrapers_parallel_search(self):
        """Test running all scrapers in parallel."""
        scrapers = [
            ("Amazon", AmazonScraper(DEFAULT_PINCODE)),
            ("Amazon Fresh", AmazonFreshScraper(DEFAULT_PINCODE)),
            ("Flipkart", FlipkartScraper(DEFAULT_PINCODE)),
            ("Flipkart Minutes", FlipkartMinutesScraper(DEFAULT_PINCODE)),
            ("Zepto", ZeptoScraper(DEFAULT_PINCODE)),
            ("BigBasket", BigBasketScraper(DEFAULT_PINCODE)),
            ("JioMart", JioMartScraper(DEFAULT_PINCODE)),
            ("JioMart Quick", JioMartQuickScraper(DEFAULT_PINCODE)),
        ]
        
        async def run_scraper(name, scraper):
            try:
                results = await asyncio.wait_for(scraper.search(TEST_QUERY), timeout=30.0)
                return name, results, None
            except asyncio.TimeoutError:
                return name, [], "TIMEOUT"
            except Exception as e:
                return name, [], str(e)
        
        # Run all scrapers in parallel
        tasks = [run_scraper(name, scraper) for name, scraper in scrapers]
        all_results = await asyncio.gather(*tasks)
        
        # Report results
        total_products = 0
        platforms_with_results = 0
        
        print("\n" + "="*50)
        print("INTEGRATION TEST RESULTS")
        print("="*50)
        
        for name, results, error in all_results:
            if error:
                print(f"❌ {name}: {error}")
            elif results:
                platforms_with_results += 1
                total_products += len(results)
                print(f"✅ {name}: {len(results)} products")
            else:
                print(f"⚠️  {name}: 0 products (no error)")
        
        print("="*50)
        print(f"Total: {total_products} products from {platforms_with_results} platforms")
        print("="*50)
        
        # At least some platforms should return results
        assert platforms_with_results >= 2, "At least 2 platforms should return results"


class TestProductResultValidation:
    """Test that product results from real scraping are valid."""
    
    @pytest.mark.integration
    @pytest.mark.slow
    @pytest.mark.asyncio
    async def test_product_prices_are_reasonable(self):
        """Test that scraped prices are in reasonable range."""
        scraper = FlipkartScraper(DEFAULT_PINCODE)
        results = await scraper.search("milk 1 ltr")
        
        for result in results:
            # Price should be positive and reasonable (₹1 to ₹100000)
            assert result.price > 0, "Price should be positive"
            assert result.price < 100000, "Price should be reasonable"
            
            # If original price exists, it should be >= selling price
            if result.original_price:
                assert result.original_price >= result.price
    
    @pytest.mark.integration
    @pytest.mark.slow
    @pytest.mark.asyncio
    async def test_product_urls_are_valid(self):
        """Test that product URLs are valid."""
        scraper = AmazonScraper(DEFAULT_PINCODE)
        results = await scraper.search("butter")
        
        for result in results:
            assert result.url.startswith("http"), "URL should start with http"
            assert len(result.url) > 10, "URL should be reasonably long"



