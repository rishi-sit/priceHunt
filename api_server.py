"""
FastAPI server to provide product search API for Android app.
Uses the existing scrapers with Playwright to bypass anti-bot protection.
"""
from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
from typing import List, Dict
import asyncio
from app.scrapers.amazon import AmazonScraper
from app.scrapers.amazon_fresh import AmazonFreshScraper
from app.scrapers.flipkart import FlipkartScraper
from app.scrapers.flipkart_minutes import FlipkartMinutesScraper
from app.scrapers.bigbasket import BigBasketScraper
from app.scrapers.jiomart import JioMartScraper
from app.scrapers.jiomart_quick import JioMartQuickScraper
from app.scrapers.zepto import ZeptoScraper
from app.scrapers.blinkit import BlinkitScraper
from app.scrapers.instamart import InstamartScraper

app = FastAPI(title="PriceHunt API", version="1.0.0")

# Allow CORS for Android app
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize scrapers
scrapers = {}

def get_scrapers(pincode: str):
    """Get or create scrapers for the given pincode."""
    if pincode not in scrapers:
        scrapers[pincode] = {
            "Amazon Fresh": AmazonFreshScraper(pincode),
            "Flipkart Minutes": FlipkartMinutesScraper(pincode),
            "JioMart Quick": JioMartQuickScraper(pincode),
            "BigBasket": BigBasketScraper(pincode),
            "Zepto": ZeptoScraper(pincode),
            "Amazon": AmazonScraper(pincode),
            "Flipkart": FlipkartScraper(pincode),
            "JioMart": JioMartScraper(pincode),
            "Blinkit": BlinkitScraper(pincode),
            "Instamart": InstamartScraper(pincode),
        }
    return scrapers[pincode]


@app.get("/api/search")
async def search_products(
    q: str = Query(..., description="Search query"),
    pincode: str = Query("560001", description="Delivery pincode")
) -> Dict:
    """
    Search for products across all platforms.
    Returns results as they become available.
    """
    platform_scrapers = get_scrapers(pincode)
    results = {}
    
    # Run all scrapers in parallel
    tasks = []
    for platform_name, scraper in platform_scrapers.items():
        tasks.append(search_platform(platform_name, scraper, q))
    
    # Wait for all to complete
    platform_results = await asyncio.gather(*tasks, return_exceptions=True)
    
    # Combine results into a flat list
    all_products = []
    for platform_name, products in zip(platform_scrapers.keys(), platform_results):
        if not isinstance(products, Exception) and products:
            for p in products:
                all_products.append({
                    "name": p.name,
                    "price": p.price,
                    "original_price": p.original_price,
                    "discount": p.discount,
                    "platform": p.platform,
                    "url": p.url,
                    "image_url": p.image_url,
                    "rating": p.rating,
                    "delivery_time": p.delivery_time,
                    "available": p.available
                })
    
    # Find lowest price
    lowest = None
    if all_products:
        lowest = min(all_products, key=lambda x: x["price"])
    
    return {
        "query": q,
        "pincode": pincode,
        "results": all_products,
        "lowest_price": lowest,
        "total_platforms": len([p for p in platform_results if not isinstance(p, Exception) and p])
    }


async def search_platform(platform_name: str, scraper, query: str):
    """Search a single platform."""
    try:
        print(f"{platform_name}: Searching for '{query}'...")
        products = await scraper.search(query)
        print(f"{platform_name}: Found {len(products)} products")
        return products
    except Exception as e:
        print(f"{platform_name}: Error - {e}")
        return []


@app.get("/api/platforms")
async def get_platforms():
    """Get list of all supported platforms."""
    return {
        "platforms": [
            {"name": "Amazon Fresh", "delivery_time": "2-4 hours"},
            {"name": "Flipkart Minutes", "delivery_time": "10-45 mins"},
            {"name": "JioMart Quick", "delivery_time": "10-30 mins"},
            {"name": "BigBasket", "delivery_time": "2-4 hours"},
            {"name": "Zepto", "delivery_time": "10-15 mins"},
            {"name": "Amazon", "delivery_time": "1-3 days"},
            {"name": "Flipkart", "delivery_time": "2-4 days"},
            {"name": "JioMart", "delivery_time": "2-5 days"},
            {"name": "Blinkit", "delivery_time": "10-20 mins"},
            {"name": "Instamart", "delivery_time": "15-30 mins"},
        ]
    }


@app.get("/")
async def root():
    """API root endpoint."""
    return {
        "message": "PriceHunt API - Product Price Comparison",
        "version": "1.0.0",
        "endpoints": {
            "/api/search": "Search products across platforms",
            "/api/platforms": "Get supported platforms",
            "/docs": "API documentation"
        }
    }


if __name__ == "__main__":
    import uvicorn
    print("🚀 Starting PriceHunt API server...")
    print("📱 Android app should connect to: http://YOUR_MAC_IP:8000")
    print("📚 API docs available at: http://localhost:8000/docs")
    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info")

