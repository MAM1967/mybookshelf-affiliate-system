# Amazon Price Extraction Fix Plan

## 🎯 **Objective**

Fix the "Could not parse price from page" errors by updating price extraction patterns to match Amazon's current page structure.

## 📊 **Current Status**

- **89 items** with error status
- **10 items** specifically failing with "Could not parse price from page"
- **6 regex patterns** currently implemented, all failing

## 🔍 **Root Cause Analysis**

### **Why Current Patterns Fail:**

1. **Outdated Patterns**: Amazon frequently changes HTML structure
2. **Incomplete Coverage**: Only 6 patterns can't cover all page variations
3. **No Debugging**: Can't see what HTML we're actually getting
4. **No Fallback**: No alternative extraction methods

## 🛠️ **Phase 1: Diagnostic & Analysis (2 hours)**

### **Step 1.1: Add Debug Logging**

- [ ] Add HTML content logging for failed extractions
- [ ] Log the actual HTML structure when patterns fail
- [ ] Create sample page analysis for failed items

### **Step 1.2: Analyze Current Amazon Page Structure**

- [ ] Manually visit failed product pages
- [ ] Inspect current price element structures
- [ ] Document all price display variations
- [ ] Identify common patterns across different product types

### **Step 1.3: Create Test Suite**

- [ ] Build test cases with known working/failing items
- [ ] Create HTML samples for each failure type
- [ ] Set up automated pattern testing

## 🔧 **Phase 2: Pattern Updates (3 hours)**

### **Step 2.1: Research Current Amazon Patterns**

- [ ] Analyze live Amazon book pages
- [ ] Document all price element variations:
  - Primary price displays
  - Deal price displays
  - Used/New price variations
  - Kindle/Paperback/Hardcover options
  - Marketplace seller prices

### **Step 2.2: Update Regex Patterns**

- [ ] Add patterns for current Amazon structures
- [ ] Include multiple price format variations
- [ ] Add support for different currency formats
- [ ] Handle decimal and whole number prices

### **Step 2.3: Implement Fallback Methods**

- [ ] Add JSON-LD structured data extraction
- [ ] Implement microdata parsing
- [ ] Add CSS selector fallbacks
- [ ] Create price range handling

## 🧪 **Phase 3: Testing & Validation (2 hours)**

### **Step 3.1: Test with Failed Items**

- [ ] Test updated patterns against known failing items
- [ ] Verify extraction accuracy
- [ ] Measure success rate improvement

### **Step 3.2: Comprehensive Testing**

- [ ] Test across different book categories
- [ ] Test with different price formats
- [ ] Test with marketplace vs Amazon direct
- [ ] Test with used vs new items

### **Step 3.3: Performance Optimization**

- [ ] Optimize regex patterns for speed
- [ ] Add early termination for successful matches
- [ ] Implement caching for repeated patterns

## 🚀 **Phase 4: Implementation (2 hours)**

### **Step 4.1: Update Price Extraction Code**

- [ ] Replace current regex patterns with updated ones
- [ ] Add comprehensive error logging
- [ ] Implement fallback extraction methods
- [ ] Add price validation logic

### **Step 4.2: Add Monitoring**

- [ ] Track extraction success rates
- [ ] Monitor pattern effectiveness
- [ ] Alert on pattern failures
- [ ] Create extraction analytics

### **Step 4.3: Deploy & Monitor**

- [ ] Deploy updated extraction logic
- [ ] Monitor error reduction
- [ ] Track price update success rates
- [ ] Validate data quality

## 📋 **Implementation Steps**

### **Immediate Actions (Today):**

1. **Add Debug Logging**

```javascript
// Add to fetchAmazonPrice function
if (!priceFound) {
  console.log(`   🔍 DEBUG: No price found for ${asin}`);
  console.log(`   📄 HTML Preview: ${content.substring(0, 500)}...`);
  // Log specific price-related HTML sections
}
```

2. **Test Current Patterns**

```javascript
// Test each pattern individually
for (const [index, pattern] of pricePatterns.entries()) {
  const match = content.match(pattern);
  if (match) {
    console.log(`   ✅ Pattern ${index} matched: ${match[0]}`);
  } else {
    console.log(`   ❌ Pattern ${index} failed`);
  }
}
```

3. **Add New Patterns**

```javascript
// Add current Amazon patterns
const updatedPatterns = [
  // Current patterns...
  /<span class="a-price a-text-price a-size-base a-color-price">.*?<span class="a-offscreen">\$([0-9,]+\.?[0-9]*)<\/span>/,
  /<span class="a-price a-color-price a-text-price">.*?<span class="a-offscreen">\$([0-9,]+\.?[0-9]*)<\/span>/,
  /<span class="a-price-range">.*?<span class="a-offscreen">\$([0-9,]+\.?[0-9]*)<\/span>/,
  // JSON-LD structured data
  /"price":\s*"([0-9,]+\.?[0-9]*)"/,
  // Microdata
  /itemprop="price".*?content="([0-9,]+\.?[0-9]*)"/,
];
```

### **Advanced Features:**

1. **Structured Data Extraction**

```javascript
// Extract JSON-LD structured data
const jsonLdMatch = content.match(
  /<script type="application\/ld\+json">(.*?)<\/script>/
);
if (jsonLdMatch) {
  try {
    const structuredData = JSON.parse(jsonLdMatch[1]);
    if (structuredData.offers && structuredData.offers.price) {
      return parseFloat(structuredData.offers.price);
    }
  } catch (e) {
    // Continue with regex patterns
  }
}
```

2. **CSS Selector Fallback**

```javascript
// Use CSS selectors as fallback
const priceSelectors = [
  ".a-price .a-offscreen",
  ".a-price-whole",
  ".a-price-range .a-offscreen",
  "[data-a-price-whole]",
];
```

## 📊 **Success Metrics**

### **Target Improvements:**

- [ ] Reduce "Could not parse price from page" errors by 90%
- [ ] Achieve 95%+ price extraction success rate
- [ ] Handle all major Amazon page variations
- [ ] Maintain extraction speed under 2 seconds

### **Monitoring:**

- [ ] Track extraction success rates daily
- [ ] Monitor pattern effectiveness weekly
- [ ] Alert on pattern failures
- [ ] Generate extraction analytics

## 🎯 **Expected Outcomes**

1. **Immediate**: 90% reduction in parsing errors
2. **Short-term**: 95%+ price extraction success rate
3. **Long-term**: Robust extraction system that adapts to Amazon changes

---

**Priority**: High - This directly impacts revenue and data quality
**Timeline**: 1 week for complete implementation
**Dependencies**: None - can be implemented independently

**Last Updated**: July 29, 2025
**Status**: Ready for implementation
