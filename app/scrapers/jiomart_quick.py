"""JioMart Quick scraper - for groceries with quick delivery (10-30 mins).

URL: https://www.jiomart.com/search/{query}?tab=groceries
"""
from typing import Optional, List
import re
import json
from bs4 import BeautifulSoup
from .base import BaseScraper, ProductResult


class JioMartQuickScraper(BaseScraper):
    """Scraper for JioMart Quick (groceries, 10-30 mins delivery)."""
    
    PLATFORM_NAME = "JioMart Quick"
    BASE_URL = "https://www.jiomart.com"
    
    def __init__(self, pincode: str = "560087"):
        super().__init__(pincode)
        
    def get_headers(self) -> dict:
        headers = super().get_headers()
        headers.update({
            "Host": "www.jiomart.com",
            "Referer": "https://www.jiomart.com/",
            "Accept": "application/json, text/plain, */*",
        })
        return headers
    
    async def search(self, query: str) -> List[ProductResult]:
        """Search for products on JioMart Quick (groceries)."""
        results = []
        
        # JioMart search URL for groceries
        search_url = f"{self.BASE_URL}/search/{query.replace(' ', '%20')}?tab=groceries"
        
        print(f"JioMart Quick: Searching with {search_url}")
        
        try:
            async with await self.get_client() as client:
                # Set cookies for location/pincode
                cookies = {
                    "pincode": self.pincode,
                    "city_id": "3",  # Default city
                }
                
                response = await client.get(
                    search_url,
                    cookies=cookies,
                    headers=self.get_headers()
                )
                
                if response.status_code == 200:
                    soup = BeautifulSoup(response.text, "lxml")
                    
                    # Try to extract from Next.js data
                    script_data = self._extract_next_data(soup)
                    if script_data:
                        results = self._parse_next_data(script_data)
                    
                    # Fallback to HTML parsing
                    if not results:
                        results = self._parse_html_products(soup)
                    
                    print(f"JioMart Quick: Found {len(results)} products")
                else:
                    print(f"JioMart Quick: Got status {response.status_code}")
                            
        except Exception as e:
            print(f"JioMart Quick search error: {e}")
        
        return results[:5]
    
    def _extract_next_data(self, soup) -> Optional[dict]:
        """Extract __NEXT_DATA__ from script tag."""
        try:
            script = soup.find("script", {"id": "__NEXT_DATA__"})
            if script and script.string:
                return json.loads(script.string)
        except Exception as e:
            print(f"JioMart Quick: Next data extraction error: {e}")
        return None
    
    def _parse_next_data(self, data: dict) -> List[ProductResult]:
        """Parse products from Next.js data."""
        results = []
        
        try:
            # Navigate to products in the data structure
            page_props = data.get("props", {}).get("pageProps", {})
            
            # Try different paths where products might be
            products = []
            
            # Path 1: searchData -> products
            search_data = page_props.get("searchData", {})
            products = search_data.get("products", [])
            
            # Path 2: initialData -> products
            if not products:
                initial_data = page_props.get("initialData", {})
                products = initial_data.get("products", [])
            
            # Path 3: data -> products
            if not products:
                products = page_props.get("data", {}).get("products", [])
            
            for product in products[:10]:
                try:
                    result = self._parse_product_json(product)
                    if result and result.price > 0:
                        results.append(result)
                except Exception:
                    continue
                    
        except Exception as e:
            print(f"JioMart Quick: JSON parse error: {e}")
        
        return results
    
    def _parse_product_json(self, product: dict) -> Optional[ProductResult]:
        """Parse a product from JSON data."""
        try:
            # Get product name
            name = (product.get("name") or 
                   product.get("productName") or 
                   product.get("title") or "")
            
            if not name:
                return None
            
            # Get price (selling price)
            price = 0.0
            sp = (product.get("selling_price") or 
                  product.get("sellingPrice") or 
                  product.get("sp") or
                  product.get("price"))
            if sp:
                price = float(str(sp).replace(",", ""))
            
            if price <= 0:
                return None
            
            # Original price (MRP)
            original_price = None
            mrp = (product.get("mrp") or 
                   product.get("maximum_retail_price") or
                   product.get("originalPrice"))
            if mrp:
                orig = float(str(mrp).replace(",", ""))
                if orig > price:
                    original_price = orig
            
            # Discount
            discount = None
            disc = product.get("discount") or product.get("discountPercent")
            if disc:
                discount = f"{disc}% off" if isinstance(disc, (int, float)) else disc
            elif original_price and original_price > price:
                discount_pct = int(((original_price - price) / original_price) * 100)
                discount = f"{discount_pct}% off"
            
            # URL
            slug = product.get("slug") or product.get("url") or product.get("id", "")
            url = f"{self.BASE_URL}/p/{slug}" if slug else self.BASE_URL
            
            # Image
            image_url = (product.get("image") or 
                        product.get("imageUrl") or 
                        product.get("image_url") or
                        product.get("thumbnail"))
            
            # Rating
            rating = None
            if product.get("rating") or product.get("averageRating"):
                try:
                    rating = float(product.get("rating") or product.get("averageRating"))
                except:
                    pass
            
            # Availability
            available = product.get("inStock", True)
            if isinstance(available, str):
                available = available.lower() not in ["false", "0", "no"]
            
            return ProductResult(
                name=name[:120],
                price=price,
                original_price=original_price,
                discount=discount,
                platform=self.PLATFORM_NAME,
                url=url,
                image_url=image_url,
                rating=rating,
                available=available,
                delivery_time="10-30 mins"
            )
            
        except Exception:
            return None
    
    def _parse_html_products(self, soup) -> List[ProductResult]:
        """Parse products from HTML."""
        results = []
        
        try:
            # Try various product card selectors
            product_selectors = [
                '[data-testid="product-card"]',
                '.product-card',
                '[class*="ProductCard"]',
                '[class*="product-item"]',
                '.plp-card',
            ]
            
            products = []
            for selector in product_selectors:
                products = soup.select(selector)[:15]
                if products:
                    break
            
            for product in products:
                try:
                    result = self._parse_product_html(product)
                    if result and result.price > 0:
                        results.append(result)
                except Exception:
                    continue
                    
        except Exception as e:
            print(f"JioMart Quick: HTML parse error: {e}")
        
        return results
    
    def _parse_product_html(self, product) -> Optional[ProductResult]:
        """Parse a product element from HTML."""
        try:
            # Get product name
            name = ""
            name_selectors = ['h3', '.product-name', '[class*="name"]', 'a[title]']
            
            for selector in name_selectors:
                name_elem = product.select_one(selector)
                if name_elem:
                    name = name_elem.get_text(strip=True) or name_elem.get('title', '')
                    if name and len(name) > 3:
                        break
            
            if not name:
                return None
            
            # Get price
            price = 0.0
            price_selectors = ['.selling-price', '.sp', '[class*="price"]']
            
            for selector in price_selectors:
                price_elem = product.select_one(selector)
                if price_elem:
                    price = self.parse_price(price_elem.get_text())
                    if price > 0:
                        break
            
            if price <= 0:
                # Find any price-like text
                price_text = product.find(string=re.compile(r'₹\s*\d+'))
                if price_text:
                    price = self.parse_price(str(price_text))
            
            if price <= 0:
                return None
            
            # Original price
            original_price = None
            mrp_selectors = ['.mrp', 'del', 's', '[class*="original"]']
            for selector in mrp_selectors:
                mrp_elem = product.select_one(selector)
                if mrp_elem:
                    orig = self.parse_price(mrp_elem.get_text())
                    if orig > price:
                        original_price = orig
                        break
            
            # Discount
            discount = None
            if original_price and original_price > price:
                discount_pct = int(((original_price - price) / original_price) * 100)
                discount = f"{discount_pct}% off"
            
            # URL
            url = self.BASE_URL
            link_elem = product.select_one('a[href]')
            if link_elem and link_elem.get('href'):
                href = link_elem['href']
                url = f"{self.BASE_URL}{href}" if href.startswith('/') else href
            
            # Image
            image_url = None
            img_elem = product.select_one('img[src]')
            if img_elem:
                image_url = img_elem.get('src') or img_elem.get('data-src')
            
            return ProductResult(
                name=name[:120],
                price=price,
                original_price=original_price,
                discount=discount,
                platform=self.PLATFORM_NAME,
                url=url,
                image_url=image_url,
                rating=None,
                available=True,
                delivery_time="10-30 mins"
            )
            
        except Exception:
            return None

