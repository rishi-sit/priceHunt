"""BigBasket scraper for grocery products."""
from typing import Optional, List
import re
import json
from bs4 import BeautifulSoup
from .base import BaseScraper, ProductResult


class BigBasketScraper(BaseScraper):
    """Scraper for BigBasket grocery delivery."""
    
    PLATFORM_NAME = "BigBasket"
    BASE_URL = "https://www.bigbasket.com"
    
    def __init__(self, pincode: str = "560087"):
        super().__init__(pincode)
        
    def get_headers(self) -> dict:
        headers = super().get_headers()
        headers.update({
            "Host": "www.bigbasket.com",
            "Referer": "https://www.bigbasket.com/",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8",
        })
        return headers
    
    async def search(self, query: str) -> List[ProductResult]:
        """Search for products on BigBasket."""
        results = []
        
        # BigBasket search URL
        search_url = f"{self.BASE_URL}/ps/?q={query.replace(' ', '%20')}"
        
        print(f"BigBasket: Searching with {search_url}")
        
        try:
            async with await self.get_client() as client:
                # Set cookies for location/pincode
                cookies = {
                    "x-entry-context-id": "100",
                    "x-channel": "web",
                    "_bb_locSrc": "default",
                    "bb2_enabled": "true",
                    "_bb_pin_code": self.pincode,
                }
                
                response = await client.get(
                    search_url,
                    cookies=cookies,
                    headers=self.get_headers()
                )
                
                if response.status_code == 200:
                    soup = BeautifulSoup(response.text, "lxml")
                    
                    # Try to find product data in JSON script tags (BigBasket often uses SSR)
                    script_data = self._extract_script_data(soup)
                    if script_data:
                        results = self._parse_script_products(script_data)
                    
                    # Fallback: Parse HTML directly
                    if not results:
                        results = self._parse_html_products(soup)
                    
                    print(f"BigBasket: Found {len(results)} products")
                else:
                    print(f"BigBasket: Got status {response.status_code}")
                            
        except Exception as e:
            print(f"BigBasket search error: {e}")
        
        return results[:5]
    
    def _extract_script_data(self, soup) -> Optional[dict]:
        """Extract product data from script tags."""
        try:
            # Look for __NEXT_DATA__ or similar SSR data
            for script in soup.find_all("script"):
                if script.string and "__NEXT_DATA__" in str(script):
                    # Extract JSON from Next.js data
                    text = script.string
                    if "props" in text:
                        data = json.loads(text)
                        return data
                
                # Also try looking for inline product data
                if script.string and '"products"' in str(script.string):
                    try:
                        # Try to extract JSON object containing products
                        text = script.string
                        match = re.search(r'\{[^{}]*"products"\s*:\s*\[[^\]]*\][^{}]*\}', text)
                        if match:
                            return json.loads(match.group())
                    except:
                        pass
        except Exception as e:
            print(f"BigBasket script extraction error: {e}")
        
        return None
    
    def _parse_script_products(self, data: dict) -> List[ProductResult]:
        """Parse products from script data."""
        results = []
        
        try:
            # Navigate through Next.js data structure
            products = []
            
            if "props" in data:
                page_props = data.get("props", {}).get("pageProps", {})
                products = page_props.get("products", [])
                
                # Alternative path
                if not products:
                    tab_data = page_props.get("tabData", {})
                    products = tab_data.get("products", [])
            
            for product in products[:10]:
                try:
                    result = self._parse_product_json(product)
                    if result and result.price > 0:
                        results.append(result)
                except Exception:
                    continue
                    
        except Exception as e:
            print(f"BigBasket JSON parse error: {e}")
        
        return results
    
    def _parse_product_json(self, product: dict) -> Optional[ProductResult]:
        """Parse a product from JSON data."""
        try:
            name = product.get("p_desc") or product.get("name") or product.get("product_name", "")
            if not name:
                return None
            
            # Get price
            price = 0.0
            sp = product.get("sp") or product.get("sale_price") or product.get("price")
            if sp:
                price = float(sp)
            
            if price <= 0:
                return None
            
            # Original price (MRP)
            original_price = None
            mrp = product.get("mrp") or product.get("original_price")
            if mrp:
                orig = float(mrp)
                if orig > price:
                    original_price = orig
            
            # Discount
            discount = None
            if original_price and original_price > price:
                discount_pct = int(((original_price - price) / original_price) * 100)
                discount = f"{discount_pct}% off"
            
            # URL
            product_id = product.get("p_id") or product.get("id") or product.get("product_id", "")
            slug = product.get("slug") or product.get("url_key", "")
            url = f"{self.BASE_URL}/pd/{product_id}/{slug}" if product_id else self.BASE_URL
            
            # Image
            image_url = product.get("p_img_url") or product.get("image") or product.get("image_url")
            
            # Rating
            rating = None
            if product.get("rating"):
                try:
                    rating = float(product["rating"])
                except:
                    pass
            
            # Availability
            available = product.get("availability", True)
            if isinstance(available, str):
                available = available.lower() != "out_of_stock"
            
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
                delivery_time="2-4 hours"
            )
            
        except Exception:
            return None
    
    def _parse_html_products(self, soup) -> List[ProductResult]:
        """Parse products from HTML when JSON is not available."""
        results = []
        
        try:
            # Try various selectors BigBasket might use
            product_selectors = [
                '[data-qa="product"]',
                '.PaginateItems___StyledLi-sc-1yrbjdr-0',
                '.product-card',
                '[class*="ProductCard"]',
                'li[class*="product"]',
                '.prod-deck',
            ]
            
            products = []
            for selector in product_selectors:
                products = soup.select(selector)[:15]
                if products:
                    break
            
            # Alternative: Look for product containers with price info
            if not products:
                products = soup.find_all(
                    lambda tag: tag.name in ['div', 'li', 'article'] and 
                    tag.find(string=re.compile(r'₹\s*\d+'))
                )[:15]
            
            for product in products:
                try:
                    result = self._parse_product_html(product)
                    if result and result.price > 0:
                        results.append(result)
                except Exception:
                    continue
                    
        except Exception as e:
            print(f"BigBasket HTML parse error: {e}")
        
        return results
    
    def _parse_product_html(self, product) -> Optional[ProductResult]:
        """Parse a product element from HTML."""
        try:
            # Get product name
            name = ""
            name_selectors = [
                '[data-qa="product-title"]',
                '.PaginateItems___StyledH3-sc-1yrbjdr-1',
                '.product-name',
                'h3',
                '[class*="ProductName"]',
                'a[title]',
            ]
            
            for selector in name_selectors:
                name_elem = product.select_one(selector)
                if name_elem:
                    name = name_elem.get_text(strip=True) or name_elem.get('title', '')
                    if name and len(name) > 3:
                        break
            
            if not name or len(name) < 3:
                return None
            
            # Get price
            price = 0.0
            price_selectors = [
                '[data-qa="product-price"]',
                '.discnt-price',
                '.sale-price',
                '[class*="Price"]',
                'span[class*="price"]',
            ]
            
            for selector in price_selectors:
                price_elem = product.select_one(selector)
                if price_elem:
                    price = self.parse_price(price_elem.get_text())
                    if price > 0:
                        break
            
            # Fallback: find any price-like text
            if price <= 0:
                price_text = product.find(string=re.compile(r'₹\s*\d+'))
                if price_text:
                    price = self.parse_price(str(price_text))
            
            if price <= 0:
                return None
            
            # Get original price (MRP)
            original_price = None
            mrp_selectors = [
                '.mrp-price',
                '[class*="MRP"]',
                '.original-price',
                'del',
                's',
            ]
            
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
            link_elem = product.select_one('a[href*="/pd/"]') or product.select_one('a[href]')
            if link_elem and link_elem.get('href'):
                href = link_elem['href']
                url = f"{self.BASE_URL}{href}" if href.startswith('/') else href
            
            # Image
            image_url = None
            img_elem = product.select_one('img[src]')
            if img_elem:
                image_url = img_elem.get('src') or img_elem.get('data-src')
            
            # Rating
            rating = None
            rating_elem = product.select_one('[class*="rating"]')
            if rating_elem:
                try:
                    rating_text = rating_elem.get_text(strip=True)
                    rating = float(re.search(r'(\d+\.?\d*)', rating_text).group(1))
                except:
                    pass
            
            return ProductResult(
                name=name[:120],
                price=price,
                original_price=original_price,
                discount=discount,
                platform=self.PLATFORM_NAME,
                url=url,
                image_url=image_url,
                rating=rating,
                available=True,
                delivery_time="2-4 hours"
            )
            
        except Exception:
            return None

