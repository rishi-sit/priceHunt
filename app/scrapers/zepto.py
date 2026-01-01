"""Zepto scraper using Playwright browser automation.

Note: This scraper works best when run directly (CLI) rather than
through the web server due to Playwright/uvicorn compatibility issues.
"""
from typing import List
import os
import re
from .base import BaseScraper, ProductResult


class ZeptoScraper(BaseScraper):
    """Scraper for Zepto."""
    
    PLATFORM_NAME = "Zepto"
    BASE_URL = "https://www.zeptonow.com"
    
    def __init__(self, pincode: str = "560087"):
        super().__init__(pincode)
        # Check if we're running in web server context
        self._is_web_server = os.environ.get("UVICORN_RUNNING", "").lower() == "true"
        
    async def search(self, query: str) -> List[ProductResult]:
        """Search for products on Zepto."""
        # Skip browser automation in web server context for stability
        if self._is_web_server:
            return []
        
        try:
            return await self._browser_search(query)
        except Exception as e:
            print(f"Zepto search error: {e}")
            return []
    
    async def _browser_search(self, query: str) -> List[ProductResult]:
        """Search using Playwright browser."""
        from playwright.async_api import async_playwright
        
        results = []
        search_url = f"{self.BASE_URL}/search?query={query.replace(' ', '%20')}"
        
        playwright = await async_playwright().start()
        
        try:
            browser = await playwright.chromium.launch(headless=True)
            context = await browser.new_context(
                viewport={'width': 1920, 'height': 1080},
                user_agent='Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36',
                locale='en-IN',
            )
            
            page = await context.new_page()
            await page.goto(search_url, wait_until='networkidle', timeout=25000)
            await page.wait_for_timeout(2000)
            
            # Get page text
            body_text = await page.evaluate('() => document.body.innerText')
            
            # Parse products
            results = self._parse_products(body_text, query)
            
            await context.close()
            await browser.close()
            
        except Exception as e:
            print(f"Zepto browser error: {e}")
        finally:
            await playwright.stop()
            
        return results[:5]
    
    def _parse_products(self, body_text: str, query: str) -> List[ProductResult]:
        """Parse products from page text."""
        results = []
        
        parts = body_text.split('\nADD\n')
        
        for part in parts:
            if not part.strip():
                continue
            
            lines = [l.strip() for l in part.split('\n') if l.strip()]
            if len(lines) < 2:
                continue
            
            price = None
            name = None
            quantity = None
            rating = None
            
            for line in lines:
                price_match = re.match(r'^₹(\d+)$', line)
                if price_match and not price:
                    price = float(price_match.group(1))
                    continue
                
                if re.match(r'^[0-4]\.[0-9]$', line):
                    rating = float(line)
                    continue
                
                if re.match(r'^\([\d.]+k?\)$', line):
                    continue
                
                if 'OFF' in line:
                    continue
                
                if re.match(r'^\d+\s*(pack|ml|g|kg|L|pc|pcs)', line, re.I):
                    quantity = line
                    continue
                
                if not name and len(line) > 5 and not line.startswith('₹'):
                    name = line
            
            if name and price and price > 0:
                full_name = f"{name} ({quantity})" if quantity else name
                
                result = ProductResult(
                    name=full_name[:120],
                    price=price,
                    original_price=None,
                    discount=None,
                    platform=self.PLATFORM_NAME,
                    url=f"{self.BASE_URL}/search?query={query}",
                    image_url=None,
                    rating=rating,
                    available=True,
                    delivery_time="10-15 mins"
                )
                results.append(result)
        
        return results
