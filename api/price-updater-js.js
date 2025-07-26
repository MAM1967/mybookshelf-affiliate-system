// Native JavaScript price updater for Vercel
import { createClient } from "@supabase/supabase-js";

// Initialize Supabase client
const supabaseUrl = process.env.SUPABASE_URL;
const supabaseKey = process.env.SUPABASE_ANON_KEY;
const supabase = createClient(supabaseUrl, supabaseKey);

class PriceUpdater {
  constructor() {
    this.stats = {
      totalItems: 0,
      updatedItems: 0,
      unchangedItems: 0,
      outOfStockItems: 0,
      errorItems: 0,
      priceIncreases: 0,
      priceDecreases: 0,
      totalPriceChange: 0,
      rejectedPriceChanges: 0,
    };
  }

  async getItemsToUpdate(limitHours = 25) {
    try {
      console.log("🔍 Fetching items for price update...");

      const { data: items, error } = await supabase
        .from("books_accessories")
        .select(
          "id, title, affiliate_link, price, price_status, last_price_check, price_fetch_attempts"
        )
        .neq("price_status", "disabled");

      if (error) throw error;

      // Filter items that need updates
      const cutoffTime = new Date(Date.now() - limitHours * 60 * 60 * 1000);
      const itemsToUpdate = [];

      for (const item of items) {
        let shouldUpdate = false;

        // Never been checked
        if (!item.last_price_check) {
          shouldUpdate = true;
        } else {
          // Parse last check time
          const lastCheck = new Date(item.last_price_check);
          if (lastCheck < cutoffTime) {
            shouldUpdate = true;
          }
        }

        // Skip items with too many failed attempts (max 5)
        if (item.price_fetch_attempts >= 5) {
          console.log(
            `   ⚠️ Skipping ${item.title} - too many failed attempts`
          );
          continue;
        }

        if (shouldUpdate) {
          itemsToUpdate.push(item);
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

  extractAsinFromLink(affiliateLink) {
    if (!affiliateLink) return null;

    // Multiple patterns to extract ASIN
    const patterns = [
      /\/dp\/([A-Z0-9]{10})/, // Standard product page
      /\/gp\/product\/([A-Z0-9]{10})/, // Alternative product page
      /ASIN=([A-Z0-9]{10})/, // Query parameter
      /\/([A-Z0-9]{10})\/?$/, // ASIN at end of path
    ];

    for (const pattern of patterns) {
      const match = affiliateLink.match(pattern);
      if (match) {
        return match[1];
      }
    }

    return null;
  }

  async fetchAmazonPrice(affiliateLink, asin = null) {
    if (!asin) {
      asin = this.extractAsinFromLink(affiliateLink);
    }

    if (!asin) {
      return {
        price: null,
        status: "error",
        notes: "Could not extract ASIN from link",
      };
    }

    try {
      console.log(`   🔗 Fetching price for ASIN: ${asin}`);

      // Amazon product page headers to mimic browser
      const headers = {
        "User-Agent":
          "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
        "Accept-Language": "en-US,en;q=0.9",
        "Accept-Encoding": "gzip, deflate, br",
        Accept:
          "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
        Connection: "keep-alive",
        "Upgrade-Insecure-Requests": "1",
      };

      // Construct Amazon URL
      const amazonUrl = `https://www.amazon.com/dp/${asin}`;

      const response = await fetch(amazonUrl, {
        headers,
        timeout: 15000,
        signal: AbortSignal.timeout(15000),
      });

      if (!response.ok) {
        throw new Error(`HTTP ${response.status}`);
      }

      const content = await response.text();

      // Check for out of stock indicators
      const outOfStockPatterns = [
        /Currently unavailable/i,
        /Out of Stock/i,
        /Temporarily out of stock/i,
        /This item is not available/i,
        /Product not available/i,
      ];

      for (const pattern of outOfStockPatterns) {
        if (pattern.test(content)) {
          return {
            price: 0,
            status: "out_of_stock",
            notes: "Product currently unavailable",
          };
        }
      }

      // Price extraction patterns (multiple formats)
      const pricePatterns = [
        /<span class="a-price-whole">([0-9,]+)<\/span><span class="a-price-fraction">([0-9]+)<\/span>/,
        /<span class="a-price a-text-price a-size-medium apb-price-current"><span class="a-offscreen">\$([0-9,]+\.?[0-9]*)<\/span>/,
        /"priceAmount":([0-9]+\.?[0-9]*)/,
        /<span class="a-price-range">.*?\$([0-9,]+\.?[0-9]*)/,
        /id="apex_desktop".*?<span class="a-offscreen">\$([0-9,]+\.?[0-9]*)<\/span>/,
        /<span class="a-offscreen">\$([0-9,]+\.?[0-9]*)<\/span>/,
      ];

      // Try to extract price
      for (const pattern of pricePatterns) {
        const match = content.match(pattern);
        if (match) {
          let priceStr;
          if (match[2]) {
            // whole and fraction parts
            priceStr = `${match[1].replace(/,/g, "")}.${match[2]}`;
          } else {
            priceStr = match[1].replace(/,/g, "");
          }

          try {
            const price = parseFloat(priceStr);
            if (price > 0) {
              console.log(`   ✅ Found price: $${price}`);
              return {
                price,
                status: "active",
                notes: "Price updated successfully",
              };
            } else {
              return {
                price: 0,
                status: "out_of_stock",
                notes: "Price is zero",
              };
            }
          } catch (e) {
            continue;
          }
        }
      }

      // No price found
      return {
        price: null,
        status: "error",
        notes: "Could not parse price from page",
      };
    } catch (error) {
      if (error.name === "AbortError") {
        return { price: null, status: "error", notes: "Request timeout" };
      }
      return {
        price: null,
        status: "error",
        notes: `Request failed: ${error.message.substring(0, 100)}`,
      };
    }
  }

  async updateItemPrice(item, newPrice, status, notes) {
    try {
      const itemId = item.id;
      const oldPrice = parseFloat(item.price) || 0;

      // Prepare update data
      const updateData = {
        last_price_check: new Date().toISOString(),
        price_status: status,
        price_source: "automated",
        price_fetch_attempts: (item.price_fetch_attempts || 0) + 1,
      };

      // Update price if we got a valid price
      if (newPrice !== null) {
        // PRICE VALIDATION: Check for extreme price changes (bidirectional)
        const priceValidation = this.validatePriceChange(
          oldPrice,
          newPrice,
          item.title
        );

        if (!priceValidation.isValid) {
          console.warn(`🚨 Price change REJECTED: ${item.title}`);
          console.warn(
            `   $${oldPrice} → $${newPrice} (${
              priceValidation.percentChange > 0 ? "+" : ""
            }${priceValidation.percentChange.toFixed(1)}%)`
          );
          console.warn(`   Reason: ${priceValidation.reason}`);
          console.warn(
            `   ASIN: ${
              item.affiliate_link
                ? item.affiliate_link.split("/dp/")[1]?.split("/")[0]
                : "unknown"
            }`
          );

          // Track rejected price changes in statistics
          this.stats.rejectedPriceChanges++;

          // Don't update price, but still update check timestamp
          updateData.price_fetch_attempts =
            (item.price_fetch_attempts || 0) + 1;
          notes = `${notes} | REJECTED: ${
            priceValidation.reason
          } (${priceValidation.percentChange.toFixed(1)}%)`;
        } else {
          // Valid price change - proceed with update
          updateData.price = newPrice;
          updateData.price_updated_at = new Date().toISOString();
          updateData.price_fetch_attempts = 0; // Reset attempts on success

          if (Math.abs(priceValidation.percentChange) > 25) {
            console.log(`📊 Large price change APPROVED: ${item.title}`);
            console.log(
              `   $${oldPrice} → $${newPrice} (${
                priceValidation.percentChange > 0 ? "+" : ""
              }${priceValidation.percentChange.toFixed(1)}%)`
            );
            console.log(`   Reason: ${priceValidation.reason}`);
          }
        }
      }

      // Update the main record
      const { error: updateError } = await supabase
        .from("books_accessories")
        .update(updateData)
        .eq("id", itemId);

      if (updateError) throw updateError;

      // Log price change if price actually changed
      if (newPrice !== null && newPrice !== oldPrice) {
        const priceChange = newPrice - oldPrice;
        const priceChangePercent =
          oldPrice > 0 ? (priceChange / oldPrice) * 100 : null;

        // Insert into price history
        const historyData = {
          book_id: itemId,
          old_price: oldPrice,
          new_price: newPrice,
          price_change: priceChange,
          price_change_percent: priceChangePercent,
          update_source: "automated",
          notes: notes,
        };

        const { error: historyError } = await supabase
          .from("price_history")
          .insert(historyData);

        if (historyError) {
          console.warn("Failed to insert price history:", historyError);
        }

        // Update statistics
        if (priceChange > 0) {
          this.stats.priceIncreases++;
        } else if (priceChange < 0) {
          this.stats.priceDecreases++;
        }

        this.stats.totalPriceChange += priceChange;
        this.stats.updatedItems++;

        console.log(
          `   📊 Price change: $${oldPrice} → $${newPrice} (${
            priceChange >= 0 ? "+" : ""
          }${priceChange.toFixed(2)})`
        );
      } else {
        this.stats.unchangedItems++;
      }

      // Update status counters
      if (status === "out_of_stock") {
        this.stats.outOfStockItems++;
      } else if (status === "error") {
        this.stats.errorItems++;
      }

      return true;
    } catch (error) {
      console.error(
        `❌ Failed to update item ${item.title || "unknown"}:`,
        error
      );
      this.stats.errorItems++;
      return false;
    }
  }

  validatePriceChange(oldPrice, newPrice, itemTitle = "") {
    // Configuration
    const MAX_CHANGE_PERCENT = 50; // Maximum allowed price change percentage

    const validation = {
      isValid: true,
      reason: "",
      percentChange: 0,
    };

    // Calculate percentage change
    if (oldPrice > 0) {
      validation.percentChange = ((newPrice - oldPrice) / oldPrice) * 100;
    } else if (newPrice > 0) {
      // 0 → positive price (restocking) - always allowed
      validation.reason = "restocking_from_zero";
      return validation;
    } else {
      // Both prices are 0 - no change
      validation.reason = "no_change";
      return validation;
    }

    // Check for legitimate out-of-stock (price → 0)
    if (oldPrice > 0 && newPrice === 0) {
      validation.reason = "out_of_stock";
      return validation; // Always allow going out of stock
    }

    // Check for extreme price changes (bidirectional)
    const absChangePercent = Math.abs(validation.percentChange);

    if (absChangePercent > MAX_CHANGE_PERCENT) {
      validation.isValid = false;

      if (validation.percentChange > 0) {
        validation.reason = `extreme_increase_${absChangePercent.toFixed(
          1
        )}pct`;
      } else {
        validation.reason = `extreme_decrease_${absChangePercent.toFixed(
          1
        )}pct`;
      }

      return validation;
    }

    // Valid price change
    if (absChangePercent > 25) {
      validation.reason = "large_but_acceptable_change";
    } else if (absChangePercent > 10) {
      validation.reason = "moderate_change";
    } else {
      validation.reason = "normal_change";
    }

    return validation;
  }

  async processPriceUpdates(items, delaySeconds = 2) {
    console.log(`🔄 Starting price updates for ${items.length} items...`);

    for (let i = 0; i < items.length; i++) {
      const item = items[i];
      try {
        console.log(
          `📖 [${i + 1}/${items.length}] Processing: ${item.title.substring(
            0,
            50
          )}...`
        );

        // Fetch current price
        const { price, status, notes } = await this.fetchAmazonPrice(
          item.affiliate_link
        );

        // Update database
        const success = await this.updateItemPrice(item, price, status, notes);

        if (success) {
          console.log(`   ✅ Updated successfully`);
        } else {
          console.log(`   ⚠️ Update failed`);
        }

        // Rate limiting to avoid being blocked
        if (i < items.length - 1) {
          // Don't delay after last item
          await new Promise((resolve) =>
            setTimeout(resolve, delaySeconds * 1000)
          );
        }
      } catch (error) {
        console.error(`❌ Error processing ${item.title}:`, error);
        this.stats.errorItems++;
        continue;
      }
    }
  }

  generateSummaryReport() {
    const totalProcessed =
      this.stats.updatedItems +
      this.stats.unchangedItems +
      this.stats.errorItems;
    const successRate =
      totalProcessed > 0
        ? ((totalProcessed - this.stats.errorItems) / totalProcessed) * 100
        : 0;

    return {
      timestamp: new Date().toISOString(),
      statistics: {
        totalItems: this.stats.totalItems,
        updatedItems: this.stats.updatedItems,
        unchangedItems: this.stats.unchangedItems,
        outOfStockItems: this.stats.outOfStockItems,
        errorItems: this.stats.errorItems,
        priceIncreases: this.stats.priceIncreases,
        priceDecreases: this.stats.priceDecreases,
        rejectedPriceChanges: this.stats.rejectedPriceChanges,
        totalPriceChange: this.stats.totalPriceChange,
        successRate: Math.round(successRate * 10) / 10,
        validationRate:
          this.stats.totalItems > 0
            ? Math.round(
                ((this.stats.totalItems - this.stats.rejectedPriceChanges) /
                  this.stats.totalItems) *
                  100 *
                  10
              ) / 10
            : 100,
      },
    };
  }

  async runDailyUpdate() {
    console.log("🚀 Starting Daily Price Update Process");
    console.log("============================================================");

    const startTime = new Date();

    try {
      // Get items to update
      const items = await this.getItemsToUpdate();

      if (items.length === 0) {
        console.log("ℹ️ No items need price updates at this time");
        return {
          success: true,
          message: "No updates needed",
          statistics: this.stats,
        };
      }

      // Process updates
      await this.processPriceUpdates(items);

      // Generate report
      const report = this.generateSummaryReport();

      // Calculate total time
      const endTime = new Date();
      const duration = Math.round((endTime - startTime) / 1000);

      console.log(`⏱️ Total execution time: ${duration} seconds`);

      return {
        success: true,
        message: "Price update completed successfully",
        ...report,
        executionTimeSeconds: duration,
      };
    } catch (error) {
      console.error("❌ Daily update process failed:", error);
      throw error;
    }
  }
}

export default async function handler(req, res) {
  // Allow GET requests for Vercel cron jobs and POST for manual triggers
  if (req.method !== "GET" && req.method !== "POST") {
    return res.status(405).json({ error: "Method not allowed" });
  }

  // Vercel cron jobs automatically include the bypass header
  // No additional authentication needed for cron-triggered requests

  try {
    const updater = new PriceUpdater();
    const result = await updater.runDailyUpdate();

    return res.status(200).json(result);
  } catch (error) {
    console.error("❌ Price update failed:", error);

    return res.status(500).json({
      success: false,
      error: error.message,
      timestamp: new Date().toISOString(),
    });
  }
}

// Export configuration for Vercel
export const config = {
  maxDuration: 300, // 5 minutes max execution time (hobby plan limit)
  regions: ["iad1"], // US East for better performance
};
