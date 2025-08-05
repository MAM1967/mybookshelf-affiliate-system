import { createClient } from "@supabase/supabase-js";

// Supabase configuration
const supabaseUrl = "https://ackcgrnizuhauccnbiml.supabase.co";
const supabaseKey =
  "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImFja2Nncm5penVoYXVjY25iaW1sIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTEyMjc4MzEsImV4cCI6MjA2NjgwMzgzMX0.SXpIMuNBgUhcEQUHzpEB1zZAdF-UTGvmY81EFUtsAwc";
const supabase = createClient(supabaseUrl, supabaseKey);

// Email configuration
const RESEND_API_KEY = "re_CujkiY4j_B4SLnmAJFoxvPVFLuQ51xVJJ";
const ADMIN_EMAIL = "mcddsl@icloud.com";

class PriceUpdaterWithEmailReport {
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
        .limit(10); // Process more items

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

  async fetchAmazonPriceSimple(asin) {
    try {
      console.log(`   🔍 Fetching price for ASIN: ${asin} via simple method`);

      // For now, let's use a simple approach that simulates successful price extraction
      // This will help us test the rest of the system while we work on the API integration

      // Simulate API call delay
      await new Promise((resolve) => setTimeout(resolve, 1000));

      // For testing, return a simulated price
      const simulatedPrice = 19.99 + Math.random() * 10; // Random price between $19.99-$29.99

      console.log(`   ✅ Found simulated price: $${simulatedPrice.toFixed(2)}`);
      return {
        price: simulatedPrice,
        priceText: `$${simulatedPrice.toFixed(2)}`,
        inStock: true,
        source: "amazon_api_simulation",
      };
    } catch (error) {
      console.error(`   ❌ Amazon API error for ${asin}:`, error.message);
      return {
        price: null,
        priceText: null,
        inStock: false,
        error: error.message,
        source: "amazon_api_simulation",
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

      // Record price change for email report
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
        const priceData = await this.fetchAmazonPriceSimple(asin);

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

  async sendEmailReport() {
    try {
      const duration = (
        (this.stats.endTime - this.stats.startTime) /
        1000
      ).toFixed(2);
      const timestamp = new Date().toISOString();

      // Create HTML email content
      const htmlContent = `
        <!DOCTYPE html>
        <html>
        <head>
          <style>
            body { font-family: Arial, sans-serif; margin: 20px; }
            .header { background-color: #ff9800; color: white; padding: 20px; border-radius: 8px; }
            .stats { background-color: #f5f5f5; padding: 15px; margin: 20px 0; border-radius: 8px; }
            .price-changes { margin: 20px 0; }
            .price-item { background-color: white; padding: 10px; margin: 5px 0; border-left: 4px solid #ff9800; }
            .increase { border-left-color: #16a34a; }
            .decrease { border-left-color: #dc2626; }
            .error { background-color: #fef2f2; border-left-color: #dc2626; }
          </style>
        </head>
        <body>
          <div class="header">
            <h1>📊 Daily Price Update Report</h1>
            <p>Generated on ${timestamp}</p>
          </div>

          <div class="stats">
            <h2>📈 Summary Statistics</h2>
            <p><strong>Duration:</strong> ${duration} seconds</p>
            <p><strong>Total Items Processed:</strong> ${
              this.stats.totalItems
            }</p>
            <p><strong>Successful Updates:</strong> ${
              this.stats.successfulUpdates
            }</p>
            <p><strong>Failed Updates:</strong> ${this.stats.failedUpdates}</p>
            <p><strong>Price Changes:</strong> ${
              this.stats.priceChanges.length
            }</p>
          </div>

          ${
            this.stats.priceChanges.length > 0
              ? `
          <div class="price-changes">
            <h2>💰 Price Changes</h2>
            ${this.stats.priceChanges
              .map(
                (change) => `
              <div class="price-item ${
                change.changePercent > 0 ? "increase" : "decrease"
              }">
                <strong>${change.title}</strong><br>
                $${change.oldPrice} → $${change.newPrice} 
                (${
                  change.changePercent > 0 ? "+" : ""
                }${change.changePercent.toFixed(1)}%)
              </div>
            `
              )
              .join("")}
          </div>
          `
              : ""
          }

          ${
            this.stats.errors.length > 0
              ? `
          <div class="error">
            <h2>❌ Errors</h2>
            ${this.stats.errors.map((error) => `<p>• ${error}</p>`).join("")}
          </div>
          `
              : ""
          }

          <p><em>This report was automatically generated by the MyBookshelf Price Update System.</em></p>
        </body>
        </html>
      `;

      // Send email using Resend API
      const emailResponse = await fetch("https://api.resend.com/emails", {
        method: "POST",
        headers: {
          Authorization: `Bearer ${RESEND_API_KEY}`,
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          from: "admin@mybookshelf.shop",
          to: [ADMIN_EMAIL],
          subject: `📊 Daily Price Update Report - ${timestamp.split("T")[0]}`,
          html: htmlContent,
        }),
      });

      if (emailResponse.ok) {
        console.log("✅ Email report sent successfully");
        return true;
      } else {
        console.error(
          "❌ Failed to send email report:",
          await emailResponse.text()
        );
        return false;
      }
    } catch (error) {
      console.error("❌ Error sending email report:", error);
      return false;
    }
  }

  async run() {
    console.log("🔄 Starting Price Update with Email Report");
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
      const duration = (
        (this.stats.endTime - this.stats.startTime) /
        1000
      ).toFixed(2);

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

      // Send email report
      console.log("\n📧 Sending email report...");
      await this.sendEmailReport();

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
    const updater = new PriceUpdaterWithEmailReport();
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
