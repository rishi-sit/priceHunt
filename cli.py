#!/usr/bin/env python3
"""CLI tool for full price comparison including Zepto (browser automation)."""
import asyncio
import argparse
import sys


async def compare_prices(query: str, pincode: str = "560087"):
    """Compare prices across all platforms including Zepto."""
    from app.scrapers import (
        AmazonScraper,
        AmazonFreshScraper,
        FlipkartScraper,
        FlipkartMinutesScraper,
        ZeptoScraper,
    )
    
    print(f"\n🔎 Searching for '{query}' in pincode {pincode}...")
    print("=" * 60)
    
    scrapers = [
        ("Amazon", AmazonScraper(pincode)),
        ("Amazon Fresh", AmazonFreshScraper(pincode)),
        ("Flipkart", FlipkartScraper(pincode)),
        ("Flipkart Minutes", FlipkartMinutesScraper(pincode)),
        ("Zepto", ZeptoScraper(pincode)),
    ]
    
    async def run_scraper(name, scraper, query):
        try:
            results = await asyncio.wait_for(scraper.search(query), timeout=35.0)
            return name, results
        except asyncio.TimeoutError:
            print(f"⚠️  {name}: timeout")
            return name, []
        except Exception as e:
            print(f"❌ {name}: {e}")
            return name, []
    
    tasks = [run_scraper(name, scraper, query) for name, scraper in scrapers]
    results = await asyncio.gather(*tasks)
    
    all_products = []
    platforms_with_results = 0
    
    for name, platform_results in results:
        if platform_results:
            platforms_with_results += 1
            print(f"\n📦 {name} ({len(platform_results)} products):")
            for r in platform_results[:5]:
                print(f"   ₹{r.price:,.0f} - {r.name[:50]}")
                all_products.append(r)
    
    if all_products:
        lowest = min(all_products, key=lambda x: x.price)
        print("\n" + "=" * 60)
        print(f"🏆 LOWEST PRICE: ₹{lowest.price:,.0f}")
        print(f"   {lowest.name}")
        print(f"   Platform: {lowest.platform}")
        print(f"   Delivery: {lowest.delivery_time or 'N/A'}")
        print("=" * 60)
    else:
        print("\n❌ No results found from any platform")
    
    return all_products


def main():
    parser = argparse.ArgumentParser(
        description="Compare prices across Amazon, Flipkart, and Zepto",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python cli.py "milk"
  python cli.py "atta 5kg" --pincode 560034
  python cli.py "bread" "eggs" "butter"
        """
    )
    parser.add_argument(
        "products",
        nargs="+",
        help="Product(s) to search for"
    )
    parser.add_argument(
        "--pincode", "-p",
        default="560087",
        help="Delivery pincode (default: 560087 - Bangalore)"
    )
    
    args = parser.parse_args()
    
    for product in args.products:
        asyncio.run(compare_prices(product, args.pincode))
        if len(args.products) > 1:
            print("\n" + "─" * 60 + "\n")


if __name__ == "__main__":
    main()

