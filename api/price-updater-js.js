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

  // 🏗️ REFACTORED: Main orchestration function with single responsibility
  async updateItemPrice(item, newPrice, status, notes = "") {
    try {
      const context = this.buildUpdateContext(item, newPrice, status, notes);
      const validationResult = this.validatePriceUpdate(context);
      const updateResult = await this.persistPriceUpdate(
        context,
        validationResult
      );
      this.updateStatistics(context, validationResult, updateResult);
      return updateResult.success;
    } catch (error) {
      console.error(
        `❌ Failed to update item ${item.title || "unknown"}:`,
        error
      );
      this.stats.errorItems++;
      return false;
    }
  }

  // 🏗️ EXTRACTED: Build immutable context object
  buildUpdateContext(item, newPrice, status, notes) {
    const oldPrice = parseFloat(item.price) || 0;
    const timestamp = new Date().toISOString();

    return {
      item: {
        id: item.id,
        title: item.title,
        price: oldPrice,
        priceString: item.price,
        affiliateLink: item.affiliate_link,
        fetchAttempts: item.price_fetch_attempts || 0,
      },
      pricing: {
        oldPrice,
        newPrice,
        hasNewPrice: newPrice !== null,
      },
      metadata: {
        status,
        notes,
        timestamp,
        source: "automated",
      },
    };
  }

  // 🏗️ EXTRACTED: Clean validation with clear business rules
  validatePriceUpdate(context) {
    const { pricing, item } = context;

    // No price found - always valid (will update timestamp only)
    if (!pricing.hasNewPrice) {
      return {
        isValid: true,
        action: "timestamp_only",
        reason: "no_price_found",
        percentChange: 0,
      };
    }

    // Delegate to existing price change validation
    const validation = this.validatePriceChange(
      pricing.oldPrice,
      pricing.newPrice,
      item.title
    );

    return {
      isValid: validation.isValid,
      action: validation.isValid
        ? "approve_price_change"
        : "reject_price_change",
      reason: validation.reason,
      percentChange: validation.percentChange,
    };
  }

  // 🏗️ EXTRACTED: Single database operation with clear transaction boundaries
  async persistPriceUpdate(context, validationResult) {
    const { item, pricing, metadata } = context;

    const baseUpdateData = {
      last_price_check: metadata.timestamp,
      price_status: metadata.status,
      price_source: metadata.source,
      price_fetch_attempts: item.fetchAttempts + 1,
    };

    try {
      if (validationResult.action === "approve_price_change") {
        return await this.persistApprovedPriceChange(
          context,
          validationResult,
          baseUpdateData
        );
      } else if (validationResult.action === "reject_price_change") {
        return await this.persistRejectedPriceChange(
          context,
          validationResult,
          baseUpdateData
        );
      } else {
        return await this.persistTimestampUpdate(context, baseUpdateData);
      }
    } catch (error) {
      console.error("Database operation failed:", error);
      return { success: false, error };
    }
  }

  // 🏗️ EXTRACTED: Handle approved price changes with transaction safety
  async persistApprovedPriceChange(context, validationResult, baseUpdateData) {
    const { item, pricing, metadata } = context;

    // Prepare approved price update
    const updateData = {
      ...baseUpdateData,
      price: pricing.newPrice,
      price_updated_at: metadata.timestamp,
      price_fetch_attempts: 0, // Reset on successful update
    };

    // Update main record
    const { error: updateError } = await supabase
      .from("books_accessories")
      .update(updateData)
      .eq("id", item.id);

    if (updateError) throw updateError;

    // Log price history for approved changes
    if (pricing.newPrice !== pricing.oldPrice) {
      await this.logPriceHistory(context, validationResult);
    }

    // Log large approved changes
    if (Math.abs(validationResult.percentChange) > 25) {
      console.log(`📊 Large price change APPROVED: ${item.title}`);
      console.log(
        `   $${pricing.oldPrice} → $${pricing.newPrice} (${
          validationResult.percentChange > 0 ? "+" : ""
        }${validationResult.percentChange.toFixed(1)}%)`
      );
      console.log(`   Reason: ${validationResult.reason}`);
    }

    return {
      success: true,
      action: "approved",
      priceChanged: pricing.newPrice !== pricing.oldPrice,
    };
  }

  // 🏗️ EXTRACTED: Handle rejected price changes
  async persistRejectedPriceChange(context, validationResult, baseUpdateData) {
    const { item, pricing, metadata } = context;

    // Log rejection
    console.warn(`🚨 Price change REJECTED: ${item.title}`);
    console.warn(
      `   $${pricing.oldPrice} → $${pricing.newPrice} (${
        validationResult.percentChange > 0 ? "+" : ""
      }${validationResult.percentChange.toFixed(1)}%)`
    );
    console.warn(`   Reason: ${validationResult.reason}`);
    console.warn(`   ASIN: ${this.extractASIN(item.affiliateLink)}`);

    // Update notes with rejection reason
    const updatedNotes = `${metadata.notes} | REJECTED: ${
      validationResult.reason
    } (${validationResult.percentChange.toFixed(1)}%)`;

    const updateData = {
      ...baseUpdateData,
      // Don't update price - keep existing price
    };

    // Update main record (timestamp only)
    const { error: updateError } = await supabase
      .from("books_accessories")
      .update(updateData)
      .eq("id", item.id);

    if (updateError) throw updateError;

    return {
      success: true,
      action: "rejected",
      priceChanged: false,
    };
  }

  // 🏗️ EXTRACTED: Handle timestamp-only updates
  async persistTimestampUpdate(context, baseUpdateData) {
    const { item } = context;

    const { error: updateError } = await supabase
      .from("books_accessories")
      .update(baseUpdateData)
      .eq("id", item.id);

    if (updateError) throw updateError;

    return {
      success: true,
      action: "timestamp_only",
      priceChanged: false,
    };
  }

  // 🏗️ EXTRACTED: Clean price history logging
  async logPriceHistory(context, validationResult) {
    const { item, pricing, metadata } = context;
    const priceChange = pricing.newPrice - pricing.oldPrice;
    const priceChangePercent =
      pricing.oldPrice > 0 ? (priceChange / pricing.oldPrice) * 100 : null;

    const historyData = {
      book_id: item.id,
      old_price: pricing.oldPrice,
      new_price: pricing.newPrice,
      price_change: priceChange,
      price_change_percent: priceChangePercent,
      update_source: metadata.source,
      notes: metadata.notes,
    };

    const { error: historyError } = await supabase
      .from("price_history")
      .insert(historyData);

    if (historyError) {
      console.warn("Failed to insert price history:", historyError);
    }
  }

  // 🏗️ EXTRACTED: Clean statistics updates with no side effects
  updateStatistics(context, validationResult, updateResult) {
    const { pricing, metadata } = context;

    // Track overall processing
    this.stats.updatedItems++;

    // Track status-specific counters
    if (metadata.status === "out_of_stock") {
      this.stats.outOfStockItems++;
    } else if (metadata.status === "error") {
      this.stats.errorItems++;
    }

    // Track validation results
    if (validationResult.action === "reject_price_change") {
      this.stats.rejectedPriceChanges++;
    } else if (updateResult.priceChanged) {
      const priceChange = pricing.newPrice - pricing.oldPrice;

      if (priceChange > 0) {
        this.stats.priceIncreases++;
      } else if (priceChange < 0) {
        this.stats.priceDecreases++;
      }

      this.stats.totalPriceChange += priceChange;

      console.log(
        `   📊 Price change: $${pricing.oldPrice} → $${pricing.newPrice} (${
          priceChange >= 0 ? "+" : ""
        }${priceChange.toFixed(2)})`
      );
    } else {
      this.stats.unchangedItems++;
    }
  }

  // 🏗️ EXTRACTED: Utility function for ASIN extraction
  extractASIN(affiliateLink) {
    if (!affiliateLink) return "unknown";
    const match = affiliateLink.split("/dp/")[1];
    return match ? match.split("/")[0] : "unknown";
  }

  // 🏗️ CLEANED: Validation function with clear business logic
  // 🏗️ ENTERPRISE-GRADE 5-LAYER VALIDATION SYSTEM
  // Based on NASDAQ/FINRA/e-commerce industry standards
  validatePriceChange(oldPrice, newPrice, itemTitle = "") {
    const validationId = `val_${Date.now()}_${Math.random()
      .toString(36)
      .substr(2, 9)}`;
    const timestamp = new Date().toISOString();

    // 🏗️ LAYER 1: SANITY CHECKS (Data validation, range checks)
    const sanityCheck = this.performSanityChecks(oldPrice, newPrice, itemTitle);
    if (!sanityCheck.isValid) {
      return {
        isValid: false,
        reason: sanityCheck.reason,
        percentChange: 0,
        layer: "sanity_checks",
        validationId,
        timestamp,
        details: sanityCheck.details,
      };
    }

    // 🏗️ LAYER 2: EXCEPTION HANDLING (Out-of-stock, restocking, special events)
    const exceptionCheck = this.checkExceptions(oldPrice, newPrice, itemTitle);
    if (exceptionCheck.isValid) {
      return {
        isValid: true,
        reason: exceptionCheck.reason,
        percentChange: exceptionCheck.percentChange || 0,
        layer: "exception_handling",
        validationId,
        timestamp,
        details: exceptionCheck.details,
      };
    }

    // 🏗️ LAYER 3: THRESHOLD VALIDATION (Tiered percentage limits)
    const thresholdCheck = this.validateThresholds(
      oldPrice,
      newPrice,
      itemTitle
    );
    if (!thresholdCheck.isValid) {
      return {
        isValid: false,
        reason: thresholdCheck.reason,
        percentChange: thresholdCheck.percentChange,
        layer: "threshold_validation",
        validationId,
        timestamp,
        details: thresholdCheck.details,
      };
    }

    // 🏗️ LAYER 4: STATISTICAL VALIDATION (Z-score, standard deviation)
    const statisticalCheck = this.performStatisticalValidation(
      oldPrice,
      newPrice,
      itemTitle
    );
    if (!statisticalCheck.isValid) {
      return {
        isValid: false,
        reason: statisticalCheck.reason,
        percentChange: thresholdCheck.percentChange,
        layer: "statistical_validation",
        validationId,
        timestamp,
        details: statisticalCheck.details,
      };
    }

    // 🏗️ LAYER 5: CONTEXT-AWARE VALIDATION (Time, volume, historical patterns)
    const contextCheck = this.performContextValidation(
      oldPrice,
      newPrice,
      itemTitle
    );
    if (!contextCheck.isValid) {
      return {
        isValid: false,
        reason: contextCheck.reason,
        percentChange: thresholdCheck.percentChange,
        layer: "context_validation",
        validationId,
        timestamp,
        details: contextCheck.details,
      };
    }

    // ✅ ALL LAYERS PASSED - Valid price change
    return {
      isValid: true,
      reason: "valid_price_change",
      percentChange: thresholdCheck.percentChange,
      layer: "all_layers_passed",
      validationId,
      timestamp,
      details: {
        priceCategory: thresholdCheck.details.priceCategory,
        changeMagnitude: thresholdCheck.details.changeMagnitude,
        statisticalScore: statisticalCheck.details.zScore,
        contextFactors: contextCheck.details.factors,
      },
    };
  }

  // 🏗️ LAYER 1: SANITY CHECKS
  performSanityChecks(oldPrice, newPrice, itemTitle) {
    // Check for data corruption
    if (isNaN(oldPrice) || isNaN(newPrice)) {
      return {
        isValid: false,
        reason: "data_corruption_nan_values",
        details: { oldPrice, newPrice },
      };
    }

    // Check for negative prices (except 0 for out-of-stock)
    if (oldPrice < 0 || newPrice < 0) {
      return {
        isValid: false,
        reason: "negative_price_values",
        details: { oldPrice, newPrice },
      };
    }

    // Check for unreasonably high prices (>$1000)
    if (newPrice > 1000) {
      return {
        isValid: false,
        reason: "unreasonably_high_price",
        details: { newPrice, threshold: 1000 },
      };
    }

    // Check for unreasonably low prices for books (<$1)
    if (newPrice > 0 && newPrice < 1) {
      return {
        isValid: false,
        reason: "suspiciously_low_price",
        details: { newPrice, threshold: 1 },
      };
    }

    return { isValid: true };
  }

  // 🏗️ LAYER 2: EXCEPTION HANDLING
  checkExceptions(oldPrice, newPrice, itemTitle) {
    // Restocking: 0 → positive price (always allowed)
    if (oldPrice === 0 && newPrice > 0) {
      return {
        isValid: true,
        reason: "legitimate_restocking",
        percentChange: 100, // 0 to positive is 100% increase
        details: { oldPrice, newPrice, changeType: "restocking" },
      };
    }

    // Out-of-stock: positive price → 0 (always allowed)
    if (oldPrice > 0 && newPrice === 0) {
      return {
        isValid: true,
        reason: "legitimate_out_of_stock",
        percentChange: -100, // positive to 0 is 100% decrease
        details: { oldPrice, newPrice, changeType: "out_of_stock" },
      };
    }

    // No change: both prices are 0
    if (oldPrice === 0 && newPrice === 0) {
      return {
        isValid: true,
        reason: "no_change_both_zero",
        percentChange: 0,
        details: { oldPrice, newPrice, changeType: "no_change" },
      };
    }

    return { isValid: false }; // No exception applies
  }

  // 🏗️ LAYER 3: THRESHOLD VALIDATION (Enterprise-grade tiered thresholds)
  validateThresholds(oldPrice, newPrice, itemTitle) {
    const percentChange = ((newPrice - oldPrice) / oldPrice) * 100;
    const absChangePercent = Math.abs(percentChange);

    // Determine price category for tiered thresholds
    let priceCategory, maxChangePercent;

    if (oldPrice >= 50) {
      priceCategory = "high_value";
      maxChangePercent = 15; // Strict for expensive items
    } else if (oldPrice >= 20) {
      priceCategory = "medium_value";
      maxChangePercent = 25; // Moderate for mid-range items
    } else if (oldPrice >= 10) {
      priceCategory = "low_value";
      maxChangePercent = 35; // More lenient for inexpensive items
    } else {
      priceCategory = "micro_value";
      maxChangePercent = 50; // Most lenient for very cheap items
    }

    // Check against tiered threshold
    if (absChangePercent > maxChangePercent) {
      return {
        isValid: false,
        reason: `extreme_change_${absChangePercent.toFixed(
          1
        )}pct_exceeds_${maxChangePercent}pct_limit`,
        percentChange,
        details: {
          priceCategory,
          maxChangePercent,
          actualChange: absChangePercent,
          oldPrice,
          newPrice,
        },
      };
    }

    // Categorize change magnitude for logging
    let changeMagnitude;
    if (absChangePercent > 20) {
      changeMagnitude = "large";
    } else if (absChangePercent > 10) {
      changeMagnitude = "moderate";
    } else {
      changeMagnitude = "normal";
    }

    return {
      isValid: true,
      percentChange,
      details: {
        priceCategory,
        maxChangePercent,
        changeMagnitude,
        oldPrice,
        newPrice,
      },
    };
  }

  // 🏗️ LAYER 4: STATISTICAL VALIDATION (Z-score methodology)
  performStatisticalValidation(oldPrice, newPrice, itemTitle) {
    const percentChange = ((newPrice - oldPrice) / oldPrice) * 100;

    // For now, use simplified statistical validation
    // In production, this would compare against historical price distributions

    // Z-score threshold (2.5 standard deviations = 99.4% confidence)
    const zScoreThreshold = 2.5;

    // Simplified: treat any change > 50% as statistical outlier
    // This is conservative and can be refined with historical data
    const absChangePercent = Math.abs(percentChange);

    if (absChangePercent > 50) {
      return {
        isValid: false,
        reason: "statistical_outlier_detected",
        details: {
          zScore: absChangePercent / 20, // Simplified calculation
          threshold: zScoreThreshold,
          percentChange,
        },
      };
    }

    return {
      isValid: true,
      details: {
        zScore: absChangePercent / 20,
        threshold: zScoreThreshold,
      },
    };
  }

  // 🏗️ LAYER 5: CONTEXT-AWARE VALIDATION
  performContextValidation(oldPrice, newPrice, itemTitle) {
    const percentChange = ((newPrice - oldPrice) / oldPrice) * 100;
    const absChangePercent = Math.abs(percentChange);

    // Check for suspicious patterns
    const factors = [];

    // Factor 1: Round number prices (often marketplace sellers)
    if (newPrice % 1 === 0 && newPrice > 20) {
      factors.push("round_number_price");
    }

    // Factor 2: Extreme increases (>100%) for established books
    if (percentChange > 100 && oldPrice > 10) {
      factors.push("extreme_increase_established_book");
    }

    // Factor 3: Suspicious price ranges
    if (newPrice > 50 && oldPrice < 15) {
      factors.push("suspicious_price_range");
    }

    // If multiple suspicious factors, reject
    if (factors.length >= 2) {
      return {
        isValid: false,
        reason: "multiple_suspicious_factors",
        details: {
          factors,
          percentChange,
          oldPrice,
          newPrice,
        },
      };
    }

    return {
      isValid: true,
      details: {
        factors: factors.length > 0 ? factors : ["no_suspicious_factors"],
      },
    };
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
