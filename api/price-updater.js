import { createClient } from "@supabase/supabase-js";

// Environment variables for security
const supabaseUrl = process.env.SUPABASE_URL || "https://ackcgrnizuhauccnbiml.supabase.co";
const supabaseKey = process.env.SUPABASE_ANON_KEY || "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImFja2Nncm5penVoYXVjY25iaW1sIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTEyMjc4MzEsImV4cCI6MjA2NjgwMzgzMX0.SXpIMuNBgUhcEQUHzpEB1zZAdF-UTGvmY81EFUtsAwc";
const supabase = createClient(supabaseUrl, supabaseKey);

// Amazon API credentials from environment
const AMAZON_ACCESS_KEY = process.env.AMAZON_ACCESS_KEY;
const AMAZON_SECRET_KEY = process.env.AMAZON_SECRET_KEY;
const AMAZON_ASSOCIATE_TAG = process.env.AMAZON_ASSOCIATE_TAG || "mybookshelf-20";

class PriceUpdater {
  constructor() {
    this.stats = {
      totalItems: 0,
      processedItems: 0,
      successfulUpdates: 0,
      failedUpdates: 0,
      priceChanges: [],
      errors: [],
      startTime: null,
      endTime: null,
    };
  }

  async getItemsToUpdate(limitHours = 12) {
    try {
      console.log("🔍 Fetching items for price update...");

      // Get items that need updates - prioritize error and out_of_stock items
      const { data: items, error } = await supabase
        .from("books_accessories")
        .select(
          "id, title, affiliate_link, price, price_status, last_price_check, price_fetch_attempts"
        )
        .or("price_status.eq.error,price_status.eq.out_of_stock")
        .limit(20); // Process more items

      if (error) throw error;

      // Filter items that need updates
      const cutoffTime = new Date(Date.now() - limitHours * 60 * 60 * 1000);
      const itemsToUpdate = [];

      for (const item of items) {
        let shouldUpdate = false;
        let reason = "";

        // Always update error and out_of_stock items unless they have too many attempts
        if (
          item.price_status === "error" ||
          item.price_status === "out_of_stock"
        ) {
          shouldUpdate = true;
          reason = `Status: ${item.price_status}`;
        } else {
          // For other items, check time
          if (!item.last_price_check || item.last_price_check === null) {
            shouldUpdate = true;
            reason = "No last_price_check";
          } else {
            const lastCheck = new Date(item.last_price_check);
            if (isNaN(lastCheck.getTime()) || lastCheck < cutoffTime) {
              shouldUpdate = true;
              reason = isNaN(lastCheck.getTime())
                ? "Invalid date"
                : "Older than cutoff";
            }
          }
        }

        // Skip items with too many failed attempts (max 5)
        if (item.price_fetch_attempts >= 5) {
          console.log(
            `   ⚠️ Skipping ${item.title} - too many failed attempts (${item.price_fetch_attempts})`
          );
          continue;
        }

        if (shouldUpdate) {
          console.log(`   ✅ Adding ${item.title} to update list (${reason})`);
          itemsToUpdate.push(item);
        } else {
          console.log(`   ⏭️ Skipping ${item.title} - recently updated`);
        }
      }

      console.log(
        `   📊 Found ${itemsToUpdate.length} items needing price updates`
      );
      this.stats.totalItems = itemsToUpdate.length;
      return itemsToUpdate;
    } catch (error) {
      console.error("❌ Failed to fetch items:", error);
      return [];
    }
  }

  extractASINFromLink(affiliateLink) {
    if (!affiliateLink) return null;

    const patterns = [
      /\/dp\/([A-Z0-9]{10})/,
      /\/gp\/product\/([A-Z0-9]{10})/,
      /ASIN=([A-Z0-9]{10})/,
      /\/([A-Z0-9]{10})\/?$/,
    ];

    for (const pattern of patterns) {
      const match = affiliateLink.match(pattern);
      if (match) return match[1];
    }

    return null;
  }

  async fetchAmazonPrice(asin) {
    try {
      console.log(`   🔍 Fetching price for ASIN: ${asin}`);

      // Check if Amazon API credentials are available
      if (!AMAZON_ACCESS_KEY || !AMAZON_SECRET_KEY) {
        console.log(`   ⚠️ Amazon API credentials not configured`);
        return {
          price: null,
          priceText: null,
          inStock: false,
          error: "Amazon API credentials not configured",
          source: "amazon_api_not_configured",
        };
      }

      // TODO: Implement real Amazon PA API
      // For now, use web scraping as fallback
      const priceData = await this.scrapeAmazonPrice(asin);
      
      if (priceData.price) {
        console.log(`   ✅ Found price: $${priceData.price}`);
        return priceData;
      } else {
        console.log(`   ❌ No price found for ${asin}`);
        return {
          price: null,
          priceText: null,
          inStock: false,
          error: priceData.error || "No price found",
          source: "amazon_scraping_failed",
        };
      }
    } catch (error) {
      console.error(`   ❌ Amazon API error for ${asin}:`, error.message);
      return {
        price: null,
        priceText: null,
        inStock: false,
        error: error.message,
        source: "amazon_api_error",
      };
    }
  }

  async scrapeAmazonPrice(asin) {
    try {
      console.log(`   🔍 Scraping price for ASIN: ${asin}`);
      
      // Use a simple web scraping approach as fallback
      const url = `https://www.amazon.com/dp/${asin}`;
      
      // For now, return null to indicate no real pricing
      // This prevents fake data from being stored
      console.log(`   ⚠️ Web scraping not implemented - skipping ${asin}`);
      return {
        price: null,
        priceText: null,
        inStock: false,
        error: "Web scraping not implemented",
        source: "amazon_scraping_not_implemented",
      };
    } catch (error) {
      return {
        price: null,
        priceText: null,
        inStock: false,
        error: error.message,
        source: "amazon_scraping_error",
      };
    }
  }

  async updateItemPrice(item, priceData) {
    try {
      console.log(`   📝 Updating price for: ${item.title}`);

      const currentPrice = item.price || 0;
      const newPrice = priceData.price || 0;

      // Calculate price change percentage
      const priceChange =
        newPrice > 0 ? ((newPrice - currentPrice) / currentPrice) * 100 : 0;

      const updateData = {
        price: newPrice,
        price_status: priceData.inStock ? "in_stock" : "out_of_stock",
        last_price_check: new Date().toISOString(),
        price_fetch_attempts: 0, // Reset attempts on success
        validation_notes: `Updated via Amazon API - ${priceData.source}`,
      };

      // If price changed significantly, mark for approval
      if (Math.abs(priceChange) > 50) {
        updateData.requires_approval = true;
        updateData.validation_notes = `Large price change detected: $${currentPrice} → $${newPrice} (${priceChange.toFixed(
          1
        )}%) - requires approval`;
      }

      const { error } = await supabase
        .from("books_accessories")
        .update(updateData)
        .eq("id", item.id);

      if (error) throw error;

      // Record price change for reporting
      if (currentPrice !== newPrice) {
        this.stats.priceChanges.push({
          title: item.title,
          oldPrice: currentPrice,
          newPrice: newPrice,
          changePercent: priceChange,
          changeAmount: newPrice - currentPrice,
        });
      }

      console.log(`   ✅ Successfully updated ${item.title}: $${newPrice}`);
      this.stats.successfulUpdates++;

      return true;
    } catch (error) {
      console.error(`   ❌ Failed to update ${item.title}:`, error);
      this.stats.errors.push(
        `Update failed for ${item.title}: ${error.message}`
      );
      this.stats.failedUpdates++;
      return false;
    }
  }

  async processItems(items) {
    console.log(`\n🚀 Processing ${items.length} items...`);

    for (const item of items) {
      this.stats.processedItems++;

      const asin = this.extractASINFromLink(item.affiliate_link);
      if (!asin) {
        console.log(`   ⚠️ No ASIN found for ${item.title}`);
        continue;
      }

      try {
        const priceData = await this.fetchAmazonPrice(asin);

        if (priceData.price) {
          await this.updateItemPrice(item, priceData);
        } else {
          // Mark as failed
          await supabase
            .from("books_accessories")
            .update({
              price_status: "error",
              price_fetch_attempts: (item.price_fetch_attempts || 0) + 1,
              validation_notes: `Amazon API failed: ${
                priceData.error || "No price found"
              }`,
            })
            .eq("id", item.id);

          console.log(`   ❌ Failed to get price for ${item.title}`);
          this.stats.failedUpdates++;
        }

        // Add delay to avoid rate limiting
        await new Promise((resolve) => setTimeout(resolve, 1000));
      } catch (error) {
        console.error(`   ❌ Error processing ${item.title}:`, error);
        this.stats.errors.push(
          `Processing error for ${item.title}: ${error.message}`
        );
        this.stats.failedUpdates++;
      }
    }
  }

  async run() {
    console.log("🔄 Starting Price Update");
    console.log("=" * 60);

    this.stats.startTime = Date.now();

    try {
      const items = await this.getItemsToUpdate();

      if (items.length === 0) {
        console.log("✅ No items need updating");
        return {
          success: true,
          message: "No updates needed",
          stats: this.stats,
        };
      }

      await this.processItems(items);

      this.stats.endTime = Date.now();
      const duration = ((this.stats.endTime - this.stats.startTime) / 1000).toFixed(2);

      console.log("\n📊 Update Complete!");
      console.log("=" * 30);
      console.log(`⏱️ Duration: ${duration}s`);
      console.log(`📦 Total Items: ${this.stats.totalItems}`);
      console.log(`✅ Successful: ${this.stats.successfulUpdates}`);
      console.log(`❌ Failed: ${this.stats.failedUpdates}`);
      console.log(`💰 Price Changes: ${this.stats.priceChanges.length}`);

      if (this.stats.errors.length > 0) {
        console.log(`⚠️ Errors: ${this.stats.errors.length}`);
        this.stats.errors.forEach((error) => console.log(`   - ${error}`));
      }

      return {
        success: this.stats.failedUpdates === 0,
        message: `Updated ${this.stats.successfulUpdates} items successfully`,
        stats: this.stats,
      };
    } catch (error) {
      console.error("❌ Price update failed:", error);
      return {
        success: false,
        message: `Update failed: ${error.message}`,
        stats: this.stats,
      };
    }
  }
}

// Vercel function handler
export default async function handler(req, res) {
  if (req.method !== "GET" && req.method !== "POST") {
    return res.status(405).json({ error: "Method not allowed" });
  }

  try {
    const updater = new PriceUpdater();
    const result = await updater.run();

    res.status(200).json(result);
  } catch (error) {
    console.error("Price update error:", error);
    res.status(500).json({
      error: "Price update failed",
      message: error.message,
    });
  }
} 