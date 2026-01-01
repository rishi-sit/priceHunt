# PriceHunt Architecture

## System Overview

PriceHunt is a real-time price comparison application that aggregates prices from 10 e-commerce platforms in India. It uses **Server-Sent Events (SSE)** for streaming results and an **LRU cache** for fast repeated searches.

---

## Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────────────────────────┐
│                                    CLIENT (Browser)                                  │
│  ┌─────────────────────────────────────────────────────────────────────────────┐   │
│  │                              Frontend (SPA)                                  │   │
│  │  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐    │   │
│  │  │  index.html  │  │   app.js     │  │  style.css   │  │  EventSource │    │   │
│  │  │  (Jinja2)    │  │  (Streaming) │  │  (Animations)│  │   (SSE)      │    │   │
│  │  └──────────────┘  └──────────────┘  └──────────────┘  └──────────────┘    │   │
│  └─────────────────────────────────────────────────────────────────────────────┘   │
└───────────────────────────────────────┬─────────────────────────────────────────────┘
                                        │
                                        │ HTTP/SSE
                                        ▼
┌─────────────────────────────────────────────────────────────────────────────────────┐
│                              BACKEND (FastAPI + Uvicorn)                            │
│                                                                                      │
│  ┌─────────────────────────────────────────────────────────────────────────────┐   │
│  │                              API Layer (main.py)                             │   │
│  │                                                                              │   │
│  │   ┌─────────────┐  ┌─────────────────┐  ┌─────────────┐  ┌─────────────┐   │   │
│  │   │ GET /       │  │ GET /api/search │  │ GET /api/   │  │ GET /api/   │   │   │
│  │   │ (Home Page) │  │ /stream (SSE)   │  │ cache/stats │  │ platforms   │   │   │
│  │   └─────────────┘  └────────┬────────┘  └─────────────┘  └─────────────┘   │   │
│  │                             │                                               │   │
│  └─────────────────────────────┼───────────────────────────────────────────────┘   │
│                                │                                                    │
│  ┌─────────────────────────────┼───────────────────────────────────────────────┐   │
│  │                    Cache Layer (cache.py)                                    │   │
│  │   ┌─────────────────────────┴─────────────────────────┐                     │   │
│  │   │              LRU Cache Manager                     │                     │   │
│  │   │  ┌─────────────────┐  ┌─────────────────────────┐ │                     │   │
│  │   │  │ Quick Commerce  │  │     E-Commerce          │ │                     │   │
│  │   │  │   TTL: 5 min    │  │     TTL: 15 min         │ │                     │   │
│  │   │  └─────────────────┘  └─────────────────────────┘ │                     │   │
│  │   │  • Stale-while-revalidate  • Max 500 entries     │                     │   │
│  │   └───────────────────────────────────────────────────┘                     │   │
│  └─────────────────────────────────────────────────────────────────────────────┘   │
│                                │                                                    │
│  ┌─────────────────────────────┼───────────────────────────────────────────────┐   │
│  │                    Scraper Layer (scrapers/)                                 │   │
│  │                             │                                                │   │
│  │   ┌─────────────────────────┴─────────────────────────────────────────┐     │   │
│  │   │                    BaseScraper (base.py)                          │     │   │
│  │   │  • HTTP Client (httpx)  • Random User-Agent  • Price Parser       │     │   │
│  │   │  • Browser Support (Playwright)  • Timeout Handling               │     │   │
│  │   └───────────────────────────────────────────────────────────────────┘     │   │
│  │                             │                                                │   │
│  │   ┌─────────────────────────┴─────────────────────────────────────────┐     │   │
│  │   │                    Platform Scrapers                               │     │   │
│  │   │  ┌─────────────────────────────────────────────────────────────┐  │     │   │
│  │   │  │              QUICK COMMERCE (10-30 min delivery)            │  │     │   │
│  │   │  │  ┌──────────────┐ ┌──────────────┐ ┌──────────────────────┐│  │     │   │
│  │   │  │  │Amazon Fresh  │ │Flipkart Mins │ │    JioMart Quick     ││  │     │   │
│  │   │  │  │(2-4 hours)   │ │(10-45 mins)  │ │    (10-30 mins)      ││  │     │   │
│  │   │  │  └──────────────┘ └──────────────┘ └──────────────────────┘│  │     │   │
│  │   │  │  ┌──────────────┐ ┌──────────────┐ ┌──────────────────────┐│  │     │   │
│  │   │  │  │  BigBasket   │ │    Zepto     │ │      Blinkit         ││  │     │   │
│  │   │  │  │(2-4 hours)   │ │(10-15 mins)  │ │    (8-12 mins)       ││  │     │   │
│  │   │  │  └──────────────┘ └──────────────┘ └──────────────────────┘│  │     │   │
│  │   │  │  ┌──────────────┐                                          │  │     │   │
│  │   │  │  │  Instamart   │                                          │  │     │   │
│  │   │  │  │(15-30 mins)  │                                          │  │     │   │
│  │   │  │  └──────────────┘                                          │  │     │   │
│  │   │  └─────────────────────────────────────────────────────────────┘  │     │   │
│  │   │  ┌─────────────────────────────────────────────────────────────┐  │     │   │
│  │   │  │              E-COMMERCE (1-3 days delivery)                 │  │     │   │
│  │   │  │  ┌──────────────┐ ┌──────────────┐ ┌──────────────────────┐│  │     │   │
│  │   │  │  │    Amazon    │ │   Flipkart   │ │       JioMart        ││  │     │   │
│  │   │  │  │(1-3 days)    │ │(2-4 days)    │ │     (1-3 days)       ││  │     │   │
│  │   │  │  └──────────────┘ └──────────────┘ └──────────────────────┘│  │     │   │
│  │   │  └─────────────────────────────────────────────────────────────┘  │     │   │
│  │   └───────────────────────────────────────────────────────────────────┘     │   │
│  └─────────────────────────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────────────────────────┘
                                        │
                                        │ HTTP Requests
                                        ▼
┌─────────────────────────────────────────────────────────────────────────────────────┐
│                           EXTERNAL E-COMMERCE PLATFORMS                             │
│                                                                                      │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐    │
│  │ Amazon   │ │ Flipkart │ │ JioMart  │ │BigBasket │ │  Zepto   │ │ Blinkit  │    │
│  │   .in    │ │   .com   │ │   .com   │ │   .com   │ │   .com   │ │   .com   │    │
│  └──────────┘ └──────────┘ └──────────┘ └──────────┘ └──────────┘ └──────────┘    │
│  ┌──────────┐                                                                       │
│  │Instamart │                                                                       │
│  │(Swiggy)  │                                                                       │
│  └──────────┘                                                                       │
└─────────────────────────────────────────────────────────────────────────────────────┘
```

---

## Data Flow

```
┌──────────────────────────────────────────────────────────────────────────────────┐
│                           SEARCH FLOW (SSE Streaming)                            │
└──────────────────────────────────────────────────────────────────────────────────┘

     User Search
         │
         ▼
    ┌─────────┐     EventSource      ┌─────────────────┐
    │ Browser │ ◄──── SSE ──────────►│ /api/search/    │
    │  (JS)   │                      │    stream       │
    └─────────┘                      └────────┬────────┘
         │                                    │
         │  Receives events:                  │
         │  • init (platforms)                │
         │  • platform (results)              ▼
         │  • refresh (cache update)   ┌─────────────────┐
         │  • complete (done)          │  Cache Check    │
         │                             │  (per platform) │
         ▼                             └────────┬────────┘
    ┌─────────────┐                            │
    │ Dynamic UI  │                   ┌────────┴────────┐
    │  Updates    │                   │                 │
    │ • Products  │              CACHED?           NOT CACHED
    │ • Best Deal │                   │                 │
    │ • Platform  │                   ▼                 ▼
    │   Status    │           ┌─────────────┐   ┌─────────────┐
    └─────────────┘           │ Return from │   │ Run Scraper │
                              │ Cache (⚡)   │   │  (async)    │
                              └──────┬──────┘   └──────┬──────┘
                                     │                 │
                                     │                 ▼
                                     │          ┌─────────────┐
                                     │          │ Update Cache│
                                     │          └──────┬──────┘
                                     │                 │
                                     └────────┬────────┘
                                              │
                                              ▼
                                       ┌─────────────┐
                                       │ SSE Event   │
                                       │ to Client   │
                                       └─────────────┘
```

---

## File Structure

```
price-comparator/
├── run.py                    # Entry point - starts Uvicorn server
├── cli.py                    # Command line interface
├── requirements.txt          # Python dependencies
├── README.md                 # Project documentation
├── ARCHITECTURE.md           # This file
│
└── app/
    ├── __init__.py
    ├── main.py               # FastAPI application & routes
    ├── cache.py              # LRU Cache with TTL
    │
    ├── scrapers/             # Platform scrapers
    │   ├── __init__.py       # Exports all scrapers
    │   ├── base.py           # BaseScraper abstract class
    │   │
    │   ├── amazon_fresh.py   # Amazon Fresh (quick commerce)
    │   ├── amazon.py         # Amazon India (e-commerce)
    │   ├── flipkart_minutes.py # Flipkart Minutes (quick)
    │   ├── flipkart.py       # Flipkart (e-commerce)
    │   ├── jiomart_quick.py  # JioMart Quick (quick)
    │   ├── jiomart.py        # JioMart (e-commerce)
    │   ├── bigbasket.py      # BigBasket (quick)
    │   ├── zepto.py          # Zepto (quick)
    │   ├── blinkit.py        # Blinkit (quick)
    │   └── instamart.py      # Swiggy Instamart (quick)
    │
    ├── static/
    │   ├── css/
    │   │   └── style.css     # Styles & animations
    │   └── js/
    │       └── app.js        # Frontend JavaScript (SSE client)
    │
    └── templates/
        └── index.html        # Jinja2 template
```

---

## Component Details

### 1. Frontend (`app.js`)

```
┌─────────────────────────────────────────────────────────────┐
│                     PriceHuntApp Class                      │
├─────────────────────────────────────────────────────────────┤
│  State Management                                           │
│  • streamingResults[]     - Accumulated products            │
│  • platformsLoading       - Set of loading platforms        │
│  • platformsCompleted     - Set of completed platforms      │
│  • platformsCached        - Set of cached platforms         │
├─────────────────────────────────────────────────────────────┤
│  SSE Event Handlers                                         │
│  • init     → Initialize platform statuses                  │
│  • platform → Add results, update UI                        │
│  • refresh  → Update stale cached data                      │
│  • complete → Finalize results, cleanup                     │
├─────────────────────────────────────────────────────────────┤
│  UI Updates                                                 │
│  • renderStreamingProducts()  - Product cards               │
│  • updateBestDeal()           - Best deal card              │
│  • updatePlatformLoadingStates() - Platform badges          │
└─────────────────────────────────────────────────────────────┘
```

### 2. Cache Manager (`cache.py`)

```
┌─────────────────────────────────────────────────────────────┐
│                     CacheManager                            │
├─────────────────────────────────────────────────────────────┤
│  Configuration                                              │
│  • max_entries: 500                                         │
│  • Quick Commerce TTL: 5 minutes                            │
│  • E-Commerce TTL: 15 minutes                               │
├─────────────────────────────────────────────────────────────┤
│  Features                                                   │
│  • LRU Eviction (Least Recently Used)                       │
│  • Per-platform caching                                     │
│  • Stale-while-revalidate (80% TTL threshold)              │
│  • Thread-safe with RLock                                   │
├─────────────────────────────────────────────────────────────┤
│  Methods                                                    │
│  • get(platform, query, pincode) → (data, is_stale)        │
│  • set(platform, query, pincode, results)                   │
│  • get_stats() → hit_rate, entries, etc.                   │
└─────────────────────────────────────────────────────────────┘
```

### 3. Base Scraper (`base.py`)

```
┌─────────────────────────────────────────────────────────────┐
│                     BaseScraper (Abstract)                  │
├─────────────────────────────────────────────────────────────┤
│  Properties                                                 │
│  • PLATFORM_NAME: str                                       │
│  • BASE_URL: str                                            │
│  • pincode: str (delivery location)                         │
├─────────────────────────────────────────────────────────────┤
│  HTTP Features                                              │
│  • Randomized User-Agent (fake_useragent)                  │
│  • Anti-detection headers                                   │
│  • Async HTTP client (httpx)                               │
│  • Rate limiting delays                                     │
├─────────────────────────────────────────────────────────────┤
│  Browser Features (Playwright)                              │
│  • Headless Chrome                                          │
│  • Stealth mode                                             │
│  • Used for JS-heavy sites (Zepto, Amazon Fresh)           │
├─────────────────────────────────────────────────────────────┤
│  Abstract Methods                                           │
│  • search(query) → List[ProductResult]                     │
└─────────────────────────────────────────────────────────────┘
```

---

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/` | Home page (Jinja2 template) |
| GET | `/api/search?q={query}&pincode={code}` | Single search (JSON) |
| GET | `/api/search/stream?q={query}&pincode={code}` | **Streaming search (SSE)** |
| POST | `/api/search/bulk` | Bulk product search |
| GET | `/api/platforms` | List all platforms |
| GET | `/api/cache/stats` | Cache statistics |
| POST | `/api/cache/clear` | Clear cache |
| GET | `/health` | Health check |

---

## Technology Stack

```
┌─────────────────────────────────────────────────────────────┐
│                      TECHNOLOGY STACK                       │
├─────────────────────────────────────────────────────────────┤
│  Backend                                                    │
│  • Python 3.9+                                              │
│  • FastAPI (async web framework)                            │
│  • Uvicorn (ASGI server)                                    │
│  • httpx (async HTTP client)                                │
│  • Playwright (browser automation)                          │
│  • BeautifulSoup + lxml (HTML parsing)                     │
├─────────────────────────────────────────────────────────────┤
│  Frontend                                                   │
│  • Vanilla JavaScript (ES6+)                                │
│  • EventSource API (SSE)                                    │
│  • CSS3 (animations, grid)                                  │
│  • Jinja2 (templating)                                      │
├─────────────────────────────────────────────────────────────┤
│  Key Libraries                                              │
│  • fake_useragent - Random user agents                     │
│  • asyncio - Concurrent scraping                           │
│  • threading - Cache thread safety                         │
└─────────────────────────────────────────────────────────────┘
```

---

## Performance Optimizations

1. **Parallel Scraping**: All scrapers run concurrently using `asyncio.as_completed()`
2. **Streaming Results**: SSE pushes results as they arrive (no waiting for all)
3. **LRU Caching**: Repeated searches are instant (< 100ms)
4. **Stale-While-Revalidate**: Serve cached data immediately, refresh in background
5. **Per-Platform TTL**: Quick commerce (5 min) vs E-commerce (15 min)

---

## Platform Summary

| Platform | Type | Delivery | Scraping Method |
|----------|------|----------|-----------------|
| Amazon Fresh | Quick | 2-4 hours | Playwright |
| Flipkart Minutes | Quick | 10-45 mins | HTTP |
| JioMart Quick | Quick | 10-30 mins | HTTP |
| BigBasket | Quick | 2-4 hours | HTTP |
| Zepto | Quick | 10-15 mins | Playwright |
| Blinkit | Quick | 8-12 mins | HTTP |
| Instamart | Quick | 15-30 mins | HTTP |
| Amazon | E-commerce | 1-3 days | HTTP |
| Flipkart | E-commerce | 2-4 days | HTTP |
| JioMart | E-commerce | 1-3 days | HTTP |

