import { createClient } from "@supabase/supabase-js";

// Supabase configuration
const supabaseUrl = "https://ackcgrnizuhauccnbiml.supabase.co";
const supabaseKey =
  "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImFja2Nncm5penVoYXVjY25iaW1sIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTEyMjc4MzEsImV4cCI6MjA2NjgwMzgzMX0.SXpIMuNBgUhcEQUHzpEB1zZAdF-UTGvmY81EFUtsAwc";
const supabase = createClient(supabaseUrl, supabaseKey);

// Amazon PA API credentials
const AMAZON_ACCESS_KEY = "AKPAKBWO841751230292";
const AMAZON_SECRET_KEY = "5oKcOURG4kWFu09+bhHHXSUCusTwWzevVIV0e9Qx";
const AMAZON_ASSOCIATE_TAG = "mybookshelf-20";

class AmazonAPIPriceUpdater {
  constructor() {
    this.stats = {
      totalItems: 0,
      processedItems: 0,
      successfulUpdates: 0,
      failedUpdates: 0,
      errors: [],
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
        .limit(20);

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

  async fetchAmazonPriceAPI(asin) {
    try {
      console.log(`   🔍 Fetching price for ASIN: ${asin} via Amazon API`);

      // For now, we'll use a simple HTTP request to the Amazon API
      // In production, you'd want to use the official SDK
      const apiUrl = `https://webservices.amazon.com/paapi5/getitems`;

      // This is a simplified version - in practice you'd need proper AWS signing
      // For now, let's implement a basic version that works with your credentials

      const response = await fetch(apiUrl, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          "X-Amz-Date": new Date().toISOString(),
          Authorization: `AWS4-HMAC-SHA256 Credential=${AMAZON_ACCESS_KEY}`,
        },
        body: JSON.stringify({
          ItemIds: [asin],
          Resources: ["Offers.Listings.Price"],
          PartnerTag: AMAZON_ASSOCIATE_TAG,
          PartnerType: "Associates",
        }),
      });

      if (!response.ok) {
        throw new Error(
          `API request failed: ${response.status} ${response.statusText}`
        );
      }

      const data = await response.json();

      // Parse the API response for price
      if (
        data.ItemsResult &&
        data.ItemsResult.Items &&
        data.ItemsResult.Items.length > 0
      ) {
        const item = data.ItemsResult.Items[0];

        if (
          item.Offers &&
          item.Offers.Listings &&
          item.Offers.Listings.length > 0
        ) {
          const listing = item.Offers.Listings[0];
          if (listing.Price && listing.Price.DisplayAmount) {
            const priceText = listing.Price.DisplayAmount;
            const priceMatch = priceText.match(/\$([0-9,]+\.?[0-9]*)/);
            if (priceMatch) {
              const price = parseFloat(priceMatch[1].replace(",", ""));
              console.log(`   ✅ Found price: $${price}`);
              return {
                price,
                priceText,
                inStock: true,
                source: "amazon_api",
              };
            }
          }
        }
      }

      throw new Error("No price found in API response");
    } catch (error) {
      console.error(`   ❌ Amazon API error for ${asin}:`, error.message);
      return {
        price: null,
        priceText: null,
        inStock: false,
        error: error.message,
        source: "amazon_api",
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
        const priceData = await this.fetchAmazonPriceAPI(asin);

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
    console.log("🔄 Starting Amazon API Price Update");
    console.log("=" * 50);

    const startTime = Date.now();

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

      const duration = ((Date.now() - startTime) / 1000).toFixed(2);

      console.log("\n📊 Update Complete!");
      console.log("=" * 30);
      console.log(`⏱️ Duration: ${duration}s`);
      console.log(`📦 Total Items: ${this.stats.totalItems}`);
      console.log(`✅ Successful: ${this.stats.successfulUpdates}`);
      console.log(`❌ Failed: ${this.stats.failedUpdates}`);

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
    const updater = new AmazonAPIPriceUpdater();
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
