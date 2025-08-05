/**
 * Amazon Web Scraping Service
 * Extracts real prices from Amazon product pages
 */

class AmazonScraper {
  constructor() {
    this.userAgents = [
      'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
      'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
      'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    ];
  }

  async scrapePrice(asin) {
    try {
      console.log(`   🔍 Scraping Amazon price for ASIN: ${asin}`);
      
      const url = `https://www.amazon.com/dp/${asin}`;
      const userAgent = this.userAgents[Math.floor(Math.random() * this.userAgents.length)];
      
      const response = await fetch(url, {
        method: 'GET',
        headers: {
          'User-Agent': userAgent,
          'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
          'Accept-Language': 'en-US,en;q=0.5',
          'Accept-Encoding': 'gzip, deflate, br',
          'Connection': 'keep-alive',
          'Upgrade-Insecure-Requests': '1',
        },
        signal: AbortSignal.timeout(10000), // 10 second timeout
      });

      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`);
      }

      const html = await response.text();
      return this.parsePriceFromHTML(html, asin);
      
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

  parsePriceFromHTML(html, asin) {
    try {
      // Extract price using various patterns
      const pricePatterns = [
        /"price":\s*"([^"]+)"/,
        /"price":\s*([0-9.]+)/,
        /class="[^"]*price[^"]*"[^>]*>[\s]*\$?([0-9,]+\.?[0-9]*)/
      ];

      let price = null;
      let priceText = null;

      for (const pattern of pricePatterns) {
        const match = html.match(pattern);
        if (match) {
          priceText = match[1];
          price = parseFloat(priceText.replace(/[$,]/g, ''));
          if (price && price > 0) {
            break;
          }
        }
      }

      // Check if product is in stock
      const inStock = !html.includes('out of stock') && 
                     !html.includes('unavailable') &&
                     !html.includes('temporarily out of stock');

      if (price && price > 0) {
        console.log(`   ✅ Found price: $${price} for ${asin}`);
        return {
          price: price,
          priceText: `$${price}`,
          inStock: inStock,
          error: null,
          source: "amazon_scraping_success",
        };
      } else {
        console.log(`   ❌ No price found for ${asin}`);
        return {
          price: null,
          priceText: null,
          inStock: false,
          error: "No price found in HTML",
          source: "amazon_scraping_no_price",
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