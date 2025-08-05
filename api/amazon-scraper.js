/**
 * Amazon Web Scraping Service
 * Extracts real prices from Amazon product pages with enhanced reliability
 */

class AmazonScraper {
  constructor() {
    this.userAgents = [
      'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
      'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
      'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
      'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.1 Safari/605.1.15',
      'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/121.0'
    ];
    
    this.retryAttempts = 3;
    this.retryDelay = 2000; // 2 seconds between retries
    this.rateLimitDelay = 1000; // 1 second between requests
    this.lastRequestTime = 0;
  }

  async scrapePrice(asin) {
    try {
      console.log(`   🔍 Scraping Amazon price for ASIN: ${asin}`);
      
      // Rate limiting
      await this.enforceRateLimit();
      
      // Try multiple times with different approaches
      for (let attempt = 1; attempt <= this.retryAttempts; attempt++) {
        console.log(`   📡 Attempt ${attempt}/${this.retryAttempts} for ${asin}`);
        
        const result = await this.attemptScrape(asin, attempt);
        
        if (result.price && result.price > 0) {
          console.log(`   ✅ Success on attempt ${attempt}: $${result.price}`);
          return result;
        }
        
        if (attempt < this.retryAttempts) {
          console.log(`   ⏳ Waiting ${this.retryDelay}ms before retry...`);
          await this.sleep(this.retryDelay);
        }
      }
      
      console.log(`   ❌ All ${this.retryAttempts} attempts failed for ${asin}`);
      return {
        price: null,
        priceText: null,
        inStock: false,
        error: "All scraping attempts failed",
        source: "amazon_scraping_all_attempts_failed",
      };
      
    } catch (error) {
      console.error(`   ❌ Scraping failed for ${asin}:`, error.message);
      return {
        price: null,
        priceText: null,
        inStock: false,
        error: error.message,
        source: "amazon_scraping_failed",
      };
    }
  }

  async attemptScrape(asin, attempt) {
    const url = `https://www.amazon.com/dp/${asin}`;
    const userAgent = this.userAgents[Math.floor(Math.random() * this.userAgents.length)];
    
    // Vary headers based on attempt
    const headers = this.getHeaders(userAgent, attempt);
    
    const response = await fetch(url, {
      method: 'GET',
      headers,
      signal: AbortSignal.timeout(15000), // 15 second timeout
    });

    if (!response.ok) {
      throw new Error(`HTTP ${response.status}: ${response.statusText}`);
    }

    const html = await response.text();
    return this.parsePriceFromHTML(html, asin, attempt);
  }

  getHeaders(userAgent, attempt) {
    const baseHeaders = {
      'User-Agent': userAgent,
      'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
      'Accept-Language': 'en-US,en;q=0.5',
      'Accept-Encoding': 'gzip, deflate, br',
      'Connection': 'keep-alive',
      'Upgrade-Insecure-Requests': '1',
    };

    // Add additional headers on retry attempts
    if (attempt > 1) {
      baseHeaders['Cache-Control'] = 'no-cache';
      baseHeaders['Pragma'] = 'no-cache';
    }

    return baseHeaders;
  }

  async enforceRateLimit() {
    const now = Date.now();
    const timeSinceLastRequest = now - this.lastRequestTime;
    
    if (timeSinceLastRequest < this.rateLimitDelay) {
      const waitTime = this.rateLimitDelay - timeSinceLastRequest;
      console.log(`   ⏳ Rate limiting: waiting ${waitTime}ms`);
      await this.sleep(waitTime);
    }
    
    this.lastRequestTime = Date.now();
  }

  parsePriceFromHTML(html, asin, attempt) {
    try {
      // Enhanced price extraction patterns
      const pricePatterns = [
        // JSON-LD structured data
        /"price":\s*"([^"]+)"/,
        /"price":\s*([0-9.]+)/,
        /"priceAmount":\s*([0-9.]+)/,
        /"priceCurrency":\s*"USD".*?"price":\s*([0-9.]+)/,
        
        // HTML price elements
        /class="[^"]*price[^"]*"[^>]*>[\s]*\$?([0-9,]+\.?[0-9]*)/,
        /id="[^"]*price[^"]*"[^>]*>[\s]*\$?([0-9,]+\.?[0-9]*)/,
        /data-price="([0-9.]+)"/,
        
        // Common price selectors
        /class="a-price-whole"[^>]*>([0-9,]+)/,
        /class="a-price-fraction"[^>]*>([0-9]+)/,
        /class="a-price-symbol"[^>]*>([$€£])/,
        
        // Alternative price formats
        /price[^>]*>[\s]*\$?([0-9,]+\.?[0-9]*)/i,
        /cost[^>]*>[\s]*\$?([0-9,]+\.?[0-9]*)/i,
        /amount[^>]*>[\s]*\$?([0-9,]+\.?[0-9]*)/i,
        
        // Deal price patterns
        /deal-price[^>]*>[\s]*\$?([0-9,]+\.?[0-9]*)/i,
        /sale-price[^>]*>[\s]*\$?([0-9,]+\.?[0-9]*)/i,
        
        // Generic price patterns (fallback)
        /\$([0-9,]+\.?[0-9]*)/,
        /USD\s*([0-9,]+\.?[0-9]*)/,
      ];

      let price = null;
      let priceText = null;
      let priceCurrency = '$';

      // Try each pattern
      for (const pattern of pricePatterns) {
        const match = html.match(pattern);
        if (match) {
          priceText = match[1];
          
          // Clean up the price text
          priceText = priceText.replace(/[$,]/g, '');
          
          // Handle decimal prices
          if (priceText.includes('.')) {
            price = parseFloat(priceText);
          } else {
            // Look for fraction part
            const fractionMatch = html.match(/class="a-price-fraction"[^>]*>([0-9]+)/);
            if (fractionMatch) {
              price = parseFloat(priceText) + parseFloat(fractionMatch[1]) / 100;
            } else {
              price = parseFloat(priceText);
            }
          }
          
          if (price && price > 0 && price < 10000) { // Sanity check
            break;
          }
        }
      }

      // Enhanced stock detection
      const inStock = this.checkStockStatus(html);
      
      // Enhanced error detection
      const error = this.detectErrors(html);

      if (price && price > 0) {
        console.log(`   ✅ Found price: $${price} for ${asin} (attempt ${attempt})`);
        return {
          price: price,
          priceText: `${priceCurrency}${price.toFixed(2)}`,
          inStock: inStock,
          error: null,
          source: `amazon_scraping_success_attempt_${attempt}`,
        };
      } else {
        console.log(`   ❌ No valid price found for ${asin} (attempt ${attempt})`);
        return {
          price: null,
          priceText: null,
          inStock: false,
          error: error || "No price found in HTML",
          source: `amazon_scraping_no_price_attempt_${attempt}`,
        };
      }
    } catch (error) {
      return {
        price: null,
        priceText: null,
        inStock: false,
        error: `HTML parsing failed: ${error.message}`,
        source: "amazon_scraping_parse_error",
      };
    }
  }

  checkStockStatus(html) {
    const outOfStockPatterns = [
      /out of stock/i,
      /unavailable/i,
      /temporarily out of stock/i,
      /currently unavailable/i,
      /we don't know when or if this item will be back in stock/i,
      /sold out/i,
      /no longer available/i,
    ];

    const inStockPatterns = [
      /in stock/i,
      /available/i,
      /add to cart/i,
      /buy now/i,
      /order now/i,
    ];

    // Check for out of stock indicators
    for (const pattern of outOfStockPatterns) {
      if (pattern.test(html)) {
        return false;
      }
    }

    // Check for in stock indicators
    for (const pattern of inStockPatterns) {
      if (pattern.test(html)) {
        return true;
      }
    }

    // Default to true if no clear indicators
    return true;
  }

  detectErrors(html) {
    const errorPatterns = [
      /page not found/i,
      /sorry, we couldn't find that page/i,
      /this item is no longer available/i,
      /product not available/i,
      /access denied/i,
      /blocked/i,
    ];

    for (const pattern of errorPatterns) {
      if (pattern.test(html)) {
        return `Page error detected: ${pattern.source}`;
      }
    }

    return null;
  }

  sleep(ms) {
    return new Promise(resolve => setTimeout(resolve, ms));
  }
}

// Vercel function handler for testing
export default async function handler(req, res) {
  if (req.method !== "POST") {
    return res.status(405).json({ error: "Method not allowed" });
  }

  try {
    const { asin } = req.body;
    
    if (!asin) {
      return res.status(400).json({ error: "ASIN is required" });
    }

    const scraper = new AmazonScraper();
    const result = await scraper.scrapePrice(asin);

    res.status(200).json(result);
  } catch (error) {
    console.error("Amazon scraper error:", error);
    res.status(500).json({
      error: "Scraping failed",
      message: error.message,
    });
  }
}

export { AmazonScraper }; 