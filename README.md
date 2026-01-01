# 🔍 PriceHunt - Smart Price Comparison Agent

A powerful price comparison tool that searches across **Amazon**, **Flipkart**, **Zepto**, **Instamart**, and **Blinkit** to find you the best deals instantly.

![Python](https://img.shields.io/badge/Python-3.10+-blue)
![FastAPI](https://img.shields.io/badge/FastAPI-0.109-green)
![License](https://img.shields.io/badge/License-MIT-yellow)

## ✨ Features

- **Multi-Platform Search**: Compare prices across 5 major platforms
- **Single & Bulk Search**: Search one product or multiple products at once
- **Real-time Comparison**: Get instant price comparisons
- **Best Deal Detection**: Automatically highlights the lowest price
- **Location-based Pricing**: Supports pincode for accurate quick-commerce prices
- **Beautiful UI**: Modern, dark-themed interface with smooth animations

## 🏪 Supported Platforms

| Platform | Type | Typical Delivery |
|----------|------|------------------|
| Amazon | E-commerce | 2-4 days |
| Flipkart | E-commerce | 2-5 days |
| Zepto | Quick Commerce | 10-15 mins |
| Instamart | Quick Commerce | 15-30 mins |
| Blinkit | Quick Commerce | 8-12 mins |

## 🚀 Quick Start

### Prerequisites

- Python 3.10 or higher
- pip (Python package manager)

### Installation

1. **Clone or navigate to the project directory**:
   ```bash
   cd price-comparator
   ```

2. **Create a virtual environment** (recommended):
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Install Playwright browsers** (for advanced scraping):
   ```bash
   playwright install chromium
   ```

### Running the Application

1. **Start the server**:
   ```bash
   uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
   ```

2. **Open your browser** and navigate to:
   ```
   http://localhost:8000
   ```

## 📖 Usage

### Web Interface

1. **Single Product Search**:
   - Enter a product name (e.g., "Amul Butter", "iPhone 15")
   - Click "Compare" or press Enter
   - View prices across all platforms

2. **Bulk Product Search**:
   - Switch to "Multiple Products" mode
   - Enter products (one per line)
   - Click "Compare All"

3. **Change Location**:
   - Update the pincode for accurate local pricing
   - Default: 560087 (Bangalore)

### API Endpoints

#### Search Single Product
```bash
GET /api/search?q=<product_name>&pincode=<pincode>
```

Example:
```bash
curl "http://localhost:8000/api/search?q=milk&pincode=560087"
```

#### Search Multiple Products
```bash
POST /api/search/bulk
Content-Type: application/json

{
  "products": ["Amul Butter", "Tata Salt", "Maggi Noodles"],
  "pincode": "560087"
}
```

#### Get Supported Platforms
```bash
GET /api/platforms
```

#### Health Check
```bash
GET /health
```

## 📁 Project Structure

```
price-comparator/
├── app/
│   ├── __init__.py
│   ├── main.py              # FastAPI application
│   ├── scrapers/
│   │   ├── __init__.py
│   │   ├── base.py          # Base scraper class
│   │   ├── amazon.py        # Amazon scraper
│   │   ├── flipkart.py      # Flipkart scraper
│   │   ├── zepto.py         # Zepto scraper
│   │   ├── instamart.py     # Instamart scraper
│   │   └── blinkit.py       # Blinkit scraper
│   ├── static/
│   │   ├── css/
│   │   │   └── style.css    # Styles
│   │   └── js/
│   │       └── app.js       # Frontend JavaScript
│   └── templates/
│       └── index.html       # Main HTML template
├── requirements.txt
└── README.md
```

## ⚠️ Important Notes

### Legal Disclaimer
- This tool is for **educational purposes only**
- Web scraping may violate the Terms of Service of some platforms
- Use responsibly and respect rate limits
- Consider using official APIs where available

### Limitations
- Prices may not always be accurate due to:
  - Anti-bot measures on platforms
  - Dynamic pricing
  - Location-based variations
  - Stock availability
- Quick commerce platforms (Zepto, Blinkit, Instamart) require accurate pincode for results
- Some searches may return empty results if platforms block the requests

### Best Practices
- Don't make too many requests in a short time
- Cache results where possible
- Consider adding delays between searches
- Use this tool for personal use only

## 🛠️ Development

### Running in Development Mode
```bash
uvicorn app.main:app --reload --port 8000
```

### Adding a New Platform

1. Create a new scraper in `app/scrapers/`
2. Extend the `BaseScraper` class
3. Implement the `search()` method
4. Register in `app/scrapers/__init__.py`
5. Add to the scrapers list in `app/main.py`

### Example New Scraper
```python
from .base import BaseScraper, ProductResult

class NewPlatformScraper(BaseScraper):
    PLATFORM_NAME = "NewPlatform"
    BASE_URL = "https://newplatform.com"
    
    async def search(self, query: str) -> list[ProductResult]:
        # Implement search logic
        pass
```

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

---

**Built with ❤️ for smart shoppers**

