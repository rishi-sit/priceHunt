# PriceHunt Android - Client-Only Architecture

A detailed architecture for building a **server-less** Android price comparison app.

---

## High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│                            ANDROID APPLICATION                                   │
│                                                                                  │
│  ┌───────────────────────────────────────────────────────────────────────────┐  │
│  │                         PRESENTATION LAYER                                 │  │
│  │  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌─────────────────┐  │  │
│  │  │  HomeScreen │  │SearchScreen │  │ResultScreen │  │ ProductDetail   │  │  │
│  │  │  (Compose)  │  │  (Compose)  │  │  (Compose)  │  │   (Compose)     │  │  │
│  │  └─────────────┘  └─────────────┘  └─────────────┘  └─────────────────┘  │  │
│  │                              │                                            │  │
│  │                              ▼                                            │  │
│  │  ┌───────────────────────────────────────────────────────────────────┐   │  │
│  │  │                      ViewModels (MVVM)                             │   │  │
│  │  │   SearchViewModel  │  ResultViewModel  │  CompareViewModel        │   │  │
│  │  └───────────────────────────────────────────────────────────────────┘   │  │
│  └───────────────────────────────────────────────────────────────────────────┘  │
│                                      │                                           │
│                                      ▼                                           │
│  ┌───────────────────────────────────────────────────────────────────────────┐  │
│  │                          DOMAIN LAYER                                      │  │
│  │  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────────────┐   │  │
│  │  │  SearchUseCase  │  │ CompareUseCase  │  │  GetCachedResultsUseCase│   │  │
│  │  └─────────────────┘  └─────────────────┘  └─────────────────────────┘   │  │
│  │                                                                           │  │
│  │  ┌─────────────────────────────────────────────────────────────────────┐ │  │
│  │  │                         Data Models                                  │ │  │
│  │  │   Product  │  SearchResult  │  Platform  │  PriceComparison         │ │  │
│  │  └─────────────────────────────────────────────────────────────────────┘ │  │
│  └───────────────────────────────────────────────────────────────────────────┘  │
│                                      │                                           │
│                                      ▼                                           │
│  ┌───────────────────────────────────────────────────────────────────────────┐  │
│  │                           DATA LAYER                                       │  │
│  │  ┌─────────────────────────────────────────────────────────────────────┐ │  │
│  │  │                    Scraper Repository                                │ │  │
│  │  │  • Coordinates all platform scrapers                                 │ │  │
│  │  │  • Parallel execution with Coroutines                               │ │  │
│  │  │  • Handles caching logic                                            │ │  │
│  │  └─────────────────────────────────────────────────────────────────────┘ │  │
│  │                                   │                                       │  │
│  │         ┌─────────────────────────┼─────────────────────────┐            │  │
│  │         ▼                         ▼                         ▼            │  │
│  │  ┌─────────────┐          ┌─────────────┐          ┌─────────────┐      │  │
│  │  │ HTTP        │          │ WebView     │          │ Local       │      │  │
│  │  │ Scrapers    │          │ Scrapers    │          │ Cache       │      │  │
│  │  │ (OkHttp)    │          │ (Headless)  │          │ (Room DB)   │      │  │
│  │  └─────────────┘          └─────────────┘          └─────────────┘      │  │
│  └───────────────────────────────────────────────────────────────────────────┘  │
│                                      │                                           │
└──────────────────────────────────────┼───────────────────────────────────────────┘
                                       │
                    Direct HTTP Requests (No Server!)
                                       │
        ┌──────────┬──────────┬────────┼────────┬──────────┬──────────┐
        ▼          ▼          ▼        ▼        ▼          ▼          ▼
     Amazon    Flipkart   JioMart  BigBasket  Zepto    Blinkit   Instamart
```

---

## Module Structure

```
app/
├── build.gradle.kts
├── src/main/
│   ├── AndroidManifest.xml
│   └── java/com/pricehunt/
│       │
│       ├── di/                          # Dependency Injection (Hilt)
│       │   ├── AppModule.kt
│       │   ├── ScraperModule.kt
│       │   └── DatabaseModule.kt
│       │
│       ├── data/                        # Data Layer
│       │   ├── repository/
│       │   │   └── ScraperRepository.kt
│       │   │
│       │   ├── scrapers/                # Platform Scrapers
│       │   │   ├── base/
│       │   │   │   ├── BaseScraper.kt
│       │   │   │   ├── HttpScraper.kt
│       │   │   │   └── WebViewScraper.kt
│       │   │   │
│       │   │   ├── http/                # HTTP-based (fast)
│       │   │   │   ├── AmazonScraper.kt
│       │   │   │   ├── FlipkartScraper.kt
│       │   │   │   ├── FlipkartMinutesScraper.kt
│       │   │   │   ├── JioMartScraper.kt
│       │   │   │   ├── JioMartQuickScraper.kt
│       │   │   │   ├── BigBasketScraper.kt
│       │   │   │   ├── BlinkitScraper.kt
│       │   │   │   └── InstamartScraper.kt
│       │   │   │
│       │   │   └── webview/             # WebView-based (JS sites)
│       │   │       ├── ZeptoScraper.kt
│       │   │       └── AmazonFreshScraper.kt
│       │   │
│       │   ├── local/                   # Local Database
│       │   │   ├── PriceHuntDatabase.kt
│       │   │   ├── dao/
│       │   │   │   ├── ProductDao.kt
│       │   │   │   └── SearchHistoryDao.kt
│       │   │   └── entity/
│       │   │       ├── CachedProduct.kt
│       │   │       └── SearchHistory.kt
│       │   │
│       │   └── model/                   # Data Models
│       │       ├── Product.kt
│       │       ├── SearchResult.kt
│       │       └── Platform.kt
│       │
│       ├── domain/                      # Domain Layer
│       │   ├── usecase/
│       │   │   ├── SearchProductsUseCase.kt
│       │   │   ├── GetCachedResultsUseCase.kt
│       │   │   └── CompareProductsUseCase.kt
│       │   └── model/
│       │       └── PriceComparison.kt
│       │
│       ├── presentation/                # Presentation Layer
│       │   ├── theme/
│       │   │   ├── Color.kt
│       │   │   ├── Theme.kt
│       │   │   └── Typography.kt
│       │   │
│       │   ├── components/              # Reusable UI Components
│       │   │   ├── ProductCard.kt
│       │   │   ├── PlatformBadge.kt
│       │   │   ├── BestDealCard.kt
│       │   │   ├── LoadingIndicator.kt
│       │   │   └── PlatformStatusRow.kt
│       │   │
│       │   ├── screens/
│       │   │   ├── home/
│       │   │   │   ├── HomeScreen.kt
│       │   │   │   └── HomeViewModel.kt
│       │   │   ├── search/
│       │   │   │   ├── SearchScreen.kt
│       │   │   │   └── SearchViewModel.kt
│       │   │   └── result/
│       │   │       ├── ResultScreen.kt
│       │   │       └── ResultViewModel.kt
│       │   │
│       │   └── navigation/
│       │       └── NavGraph.kt
│       │
│       └── util/
│           ├── NetworkUtils.kt
│           ├── HtmlParser.kt
│           └── Constants.kt
```

---

## Core Components

### 1. Base Scraper (Abstract)

```kotlin
// BaseScraper.kt
abstract class BaseScraper {
    abstract val platformName: String
    abstract val platformColor: Int
    abstract val deliveryTime: String
    
    abstract suspend fun search(query: String, pincode: String): List<Product>
    
    protected fun parsePrice(priceStr: String): Double {
        return priceStr.replace(Regex("[₹,\\s]"), "")
            .toDoubleOrNull() ?: 0.0
    }
}
```

### 2. HTTP Scraper (For most sites)

```kotlin
// HttpScraper.kt
abstract class HttpScraper : BaseScraper() {
    
    protected val client = OkHttpClient.Builder()
        .connectTimeout(15, TimeUnit.SECONDS)
        .readTimeout(15, TimeUnit.SECONDS)
        .addInterceptor(UserAgentInterceptor())
        .build()
    
    protected suspend fun fetchHtml(url: String): Document? {
        return withContext(Dispatchers.IO) {
            try {
                val request = Request.Builder()
                    .url(url)
                    .headers(getHeaders())
                    .build()
                
                val response = client.newCall(request).execute()
                if (response.isSuccessful) {
                    Jsoup.parse(response.body?.string() ?: "")
                } else null
            } catch (e: Exception) {
                null
            }
        }
    }
    
    protected open fun getHeaders(): Headers {
        return Headers.Builder()
            .add("Accept", "text/html,application/xhtml+xml")
            .add("Accept-Language", "en-IN,en;q=0.9")
            .add("Cache-Control", "no-cache")
            .build()
    }
}
```

### 3. WebView Scraper (For JS-heavy sites)

```kotlin
// WebViewScraper.kt
abstract class WebViewScraper(
    private val context: Context
) : BaseScraper() {
    
    @SuppressLint("SetJavaScriptEnabled")
    protected suspend fun fetchWithWebView(url: String): String? {
        return withContext(Dispatchers.Main) {
            suspendCancellableCoroutine { continuation ->
                val webView = WebView(context).apply {
                    settings.javaScriptEnabled = true
                    settings.domStorageEnabled = true
                    settings.userAgentString = getRandomUserAgent()
                }
                
                webView.webViewClient = object : WebViewClient() {
                    override fun onPageFinished(view: WebView?, url: String?) {
                        // Wait for JS to render
                        view?.postDelayed({
                            view.evaluateJavascript(
                                "(function() { return document.documentElement.outerHTML; })();"
                            ) { html ->
                                continuation.resume(html?.removeSurrounding("\""))
                            }
                        }, 2000)
                    }
                }
                
                webView.loadUrl(url)
            }
        }
    }
}
```

### 4. Example: Flipkart HTTP Scraper

```kotlin
// FlipkartScraper.kt
class FlipkartScraper @Inject constructor() : HttpScraper() {
    
    override val platformName = "Flipkart"
    override val platformColor = 0xFF2874F0.toInt()
    override val deliveryTime = "2-4 days"
    
    override suspend fun search(query: String, pincode: String): List<Product> {
        val url = "https://www.flipkart.com/search?q=${query.urlEncode()}"
        val doc = fetchHtml(url) ?: return emptyList()
        
        return doc.select("div[data-id]").take(10).mapNotNull { element ->
            try {
                val name = element.select("div._4rR01T, a.s1Q9rs").text()
                val priceText = element.select("div._30jeq3").text()
                val price = parsePrice(priceText)
                
                if (name.isNotEmpty() && price > 0) {
                    Product(
                        name = name,
                        price = price,
                        platform = platformName,
                        platformColor = platformColor,
                        deliveryTime = deliveryTime,
                        url = "https://www.flipkart.com" + element.select("a").attr("href"),
                        imageUrl = element.select("img").attr("src")
                    )
                } else null
            } catch (e: Exception) {
                null
            }
        }
    }
}
```

### 5. Scraper Repository (Coordinates all scrapers)

```kotlin
// ScraperRepository.kt
class ScraperRepository @Inject constructor(
    private val amazonScraper: AmazonScraper,
    private val amazonFreshScraper: AmazonFreshScraper,
    private val flipkartScraper: FlipkartScraper,
    private val flipkartMinutesScraper: FlipkartMinutesScraper,
    private val jioMartScraper: JioMartScraper,
    private val jioMartQuickScraper: JioMartQuickScraper,
    private val bigBasketScraper: BigBasketScraper,
    private val zeptoScraper: ZeptoScraper,
    private val blinkitScraper: BlinkitScraper,
    private val instamartScraper: InstamartScraper,
    private val cache: ProductCache
) {
    
    private val scrapers = listOf(
        amazonFreshScraper,
        flipkartMinutesScraper,
        jioMartQuickScraper,
        bigBasketScraper,
        zeptoScraper,
        blinkitScraper,
        instamartScraper,
        amazonScraper,
        flipkartScraper,
        jioMartScraper
    )
    
    // Stream results as they arrive (like SSE in web version)
    fun searchWithFlow(
        query: String,
        pincode: String
    ): Flow<SearchEvent> = flow {
        
        emit(SearchEvent.Started(scrapers.map { it.platformName }))
        
        // Check cache first
        val cachedResults = cache.get(query, pincode)
        cachedResults.forEach { (platform, products) ->
            emit(SearchEvent.PlatformResult(platform, products, cached = true))
        }
        
        // Fetch fresh data for non-cached platforms
        val platformsToFetch = scrapers.filter { 
            !cachedResults.containsKey(it.platformName) 
        }
        
        // Run all scrapers in parallel
        coroutineScope {
            platformsToFetch.map { scraper ->
                async {
                    try {
                        val results = withTimeout(25_000) {
                            scraper.search(query, pincode)
                        }
                        cache.set(scraper.platformName, query, pincode, results)
                        SearchEvent.PlatformResult(scraper.platformName, results, cached = false)
                    } catch (e: Exception) {
                        SearchEvent.PlatformResult(scraper.platformName, emptyList(), cached = false)
                    }
                }
            }.forEach { deferred ->
                emit(deferred.await())
            }
        }
        
        emit(SearchEvent.Completed)
    }
}

sealed class SearchEvent {
    data class Started(val platforms: List<String>) : SearchEvent()
    data class PlatformResult(
        val platform: String,
        val products: List<Product>,
        val cached: Boolean
    ) : SearchEvent()
    object Completed : SearchEvent()
}
```

### 6. ViewModel (Collects Flow)

```kotlin
// SearchViewModel.kt
@HiltViewModel
class SearchViewModel @Inject constructor(
    private val scraperRepository: ScraperRepository
) : ViewModel() {
    
    private val _uiState = MutableStateFlow(SearchUiState())
    val uiState: StateFlow<SearchUiState> = _uiState.asStateFlow()
    
    fun search(query: String, pincode: String) {
        viewModelScope.launch {
            _uiState.update { it.copy(isLoading = true, products = emptyList()) }
            
            scraperRepository.searchWithFlow(query, pincode)
                .collect { event ->
                    when (event) {
                        is SearchEvent.Started -> {
                            _uiState.update { 
                                it.copy(loadingPlatforms = event.platforms.toSet()) 
                            }
                        }
                        is SearchEvent.PlatformResult -> {
                            _uiState.update { state ->
                                state.copy(
                                    products = state.products + event.products,
                                    loadingPlatforms = state.loadingPlatforms - event.platform,
                                    completedPlatforms = state.completedPlatforms + event.platform,
                                    cachedPlatforms = if (event.cached) 
                                        state.cachedPlatforms + event.platform 
                                    else state.cachedPlatforms
                                )
                            }
                        }
                        SearchEvent.Completed -> {
                            _uiState.update { it.copy(isLoading = false) }
                        }
                    }
                }
        }
    }
}

data class SearchUiState(
    val isLoading: Boolean = false,
    val products: List<Product> = emptyList(),
    val loadingPlatforms: Set<String> = emptySet(),
    val completedPlatforms: Set<String> = emptySet(),
    val cachedPlatforms: Set<String> = emptySet()
)
```

### 7. Compose UI (Result Screen)

```kotlin
// ResultScreen.kt
@Composable
fun ResultScreen(
    viewModel: SearchViewModel = hiltViewModel()
) {
    val uiState by viewModel.uiState.collectAsState()
    
    Column(modifier = Modifier.fillMaxSize()) {
        // Platform status row
        LazyRow(
            horizontalArrangement = Arrangement.spacedBy(8.dp),
            contentPadding = PaddingValues(16.dp)
        ) {
            items(uiState.loadingPlatforms.toList()) { platform ->
                PlatformStatusChip(
                    platform = platform,
                    isLoading = true,
                    isCached = false
                )
            }
            items(uiState.completedPlatforms.toList()) { platform ->
                PlatformStatusChip(
                    platform = platform,
                    isLoading = false,
                    isCached = platform in uiState.cachedPlatforms
                )
            }
        }
        
        // Best deal card
        uiState.products.minByOrNull { it.price }?.let { bestDeal ->
            BestDealCard(product = bestDeal)
        }
        
        // Product grid
        LazyVerticalGrid(
            columns = GridCells.Fixed(2),
            contentPadding = PaddingValues(16.dp),
            horizontalArrangement = Arrangement.spacedBy(12.dp),
            verticalArrangement = Arrangement.spacedBy(12.dp)
        ) {
            items(uiState.products.sortedBy { it.price }) { product ->
                ProductCard(
                    product = product,
                    isLowestPrice = product == uiState.products.minByOrNull { it.price }
                )
            }
        }
    }
}
```

---

## Tech Stack

| Layer | Technology |
|-------|------------|
| **Language** | Kotlin |
| **UI** | Jetpack Compose |
| **Architecture** | MVVM + Clean Architecture |
| **DI** | Hilt |
| **Async** | Coroutines + Flow |
| **HTTP** | OkHttp |
| **HTML Parsing** | Jsoup |
| **JS Rendering** | WebView |
| **Local DB** | Room |
| **Navigation** | Navigation Compose |

---

## Dependencies (build.gradle.kts)

```kotlin
dependencies {
    // Core
    implementation("androidx.core:core-ktx:1.12.0")
    implementation("androidx.lifecycle:lifecycle-runtime-ktx:2.7.0")
    
    // Compose
    implementation(platform("androidx.compose:compose-bom:2024.01.00"))
    implementation("androidx.compose.ui:ui")
    implementation("androidx.compose.material3:material3")
    implementation("androidx.compose.ui:ui-tooling-preview")
    implementation("androidx.activity:activity-compose:1.8.2")
    implementation("androidx.navigation:navigation-compose:2.7.6")
    
    // Hilt
    implementation("com.google.dagger:hilt-android:2.48")
    kapt("com.google.dagger:hilt-compiler:2.48")
    implementation("androidx.hilt:hilt-navigation-compose:1.1.0")
    
    // Network
    implementation("com.squareup.okhttp3:okhttp:4.12.0")
    implementation("org.jsoup:jsoup:1.17.2")
    
    // Room
    implementation("androidx.room:room-runtime:2.6.1")
    implementation("androidx.room:room-ktx:2.6.1")
    kapt("androidx.room:room-compiler:2.6.1")
    
    // Image Loading
    implementation("io.coil-kt:coil-compose:2.5.0")
}
```

---

## Platform Scraper Mapping

| Platform | Scraper Type | Reason |
|----------|--------------|--------|
| Amazon | HTTP (Jsoup) | HTML is server-rendered |
| Amazon Fresh | **WebView** | Requires JS for location |
| Flipkart | HTTP (Jsoup) | HTML is server-rendered |
| Flipkart Minutes | HTTP (Jsoup) | HTML is server-rendered |
| JioMart | HTTP (Jsoup) | Next.js SSR data |
| JioMart Quick | HTTP (Jsoup) | Next.js SSR data |
| BigBasket | HTTP (Jsoup) | HTML is server-rendered |
| Zepto | **WebView** | Heavy JS SPA |
| Blinkit | HTTP (Jsoup) | API-like responses |
| Instamart | HTTP (Jsoup) | HTML is server-rendered |

---

## Caching Strategy (Same as Web)

```kotlin
// ProductCache.kt
class ProductCache @Inject constructor(
    private val database: PriceHuntDatabase
) {
    companion object {
        const val QUICK_COMMERCE_TTL = 5 * 60 * 1000L  // 5 minutes
        const val ECOMMERCE_TTL = 15 * 60 * 1000L     // 15 minutes
    }
    
    private val quickCommercePlatforms = setOf(
        "Amazon Fresh", "Flipkart Minutes", "JioMart Quick",
        "BigBasket", "Zepto", "Blinkit", "Instamart"
    )
    
    suspend fun get(query: String, pincode: String): Map<String, List<Product>> {
        val now = System.currentTimeMillis()
        return database.productDao()
            .getCachedProducts(query, pincode)
            .filter { cached ->
                val ttl = if (cached.platform in quickCommercePlatforms) 
                    QUICK_COMMERCE_TTL else ECOMMERCE_TTL
                now - cached.timestamp < ttl
            }
            .groupBy { it.platform }
            .mapValues { it.value.map { cached -> cached.toProduct() } }
    }
    
    suspend fun set(platform: String, query: String, pincode: String, products: List<Product>) {
        database.productDao().insertAll(
            products.map { it.toCachedProduct(query, pincode) }
        )
    }
}
```

---

## Pros & Cons Summary

### ✅ Pros
- **No server costs** - runs entirely on device
- **Works offline** - cached results available
- **Privacy** - no data leaves the device
- **Low latency** - direct requests

### ❌ Cons
- **Battery usage** - scraping is resource-intensive
- **Data usage** - each search fetches HTML
- **Update friction** - scraper changes need app update
- **App Store risk** - may violate ToS

---

## Recommendation

For **personal use**: This architecture works great!

For **public app**: Consider a lightweight serverless backend (Cloudflare Workers) to:
- Centralize scraping logic (easy updates)
- Handle rate limiting
- Reduce device battery/data usage

