# Amazon Product Advertising API Throttling

## 📊 **Amazon API Rate Limits**

### **Official Limits**

- **Requests per second**: 1 request per second
- **Requests per day**: 8,640 requests per day (1 request per 10 seconds average)
- **Burst capacity**: Up to 10 requests in a burst, then must wait
- **Error response**: 429 "Too Many Requests" when exceeded

### **Current Implementation**

- **Delay between requests**: 1 second (1000ms)
- **Items per run**: 5 items (for testing)
- **Total time per run**: ~5-10 seconds

## 🛠️ **Recommended Throttling Strategy**

### **Conservative Approach (Recommended)**

```javascript
// 2-second delay between requests
await new Promise(resolve => setTimeout(resolve, 2000));

// Maximum 5 items per run
.limit(5)
```

### **Aggressive Approach (Not Recommended)**

```javascript
// 1-second delay between requests
await new Promise(resolve => setTimeout(resolve, 1000));

// Maximum 10 items per run
.limit(10)
```

### **Ultra-Conservative Approach (Safest)**

```javascript
// 3-second delay between requests
await new Promise(resolve => setTimeout(resolve, 3000));

// Maximum 3 items per run
.limit(3)
```

## 🎯 **Current Settings Analysis**

### **What We Have Now:**

- ✅ 1-second delay between requests
- ✅ 5 items per run (good for testing)
- ✅ Error handling for 429 responses
- ⚠️ Could be more conservative for production

### **Recommended Changes:**

1. **Increase delay to 2-3 seconds** for production
2. **Add exponential backoff** for 429 errors
3. **Implement request queuing** for large batches
4. **Add daily request tracking** to stay under 8,640 limit

## 📋 **Implementation Plan**

### **Phase 1: Conservative Throttling**

```javascript
// Increase delay to 2 seconds
await new Promise((resolve) => setTimeout(resolve, 2000));

// Add exponential backoff for 429 errors
if (response.status === 429) {
  const backoffDelay = Math.min(1000 * Math.pow(2, retryCount), 30000);
  await new Promise((resolve) => setTimeout(resolve, backoffDelay));
}
```

### **Phase 2: Smart Throttling**

```javascript
// Track daily request count
// Implement adaptive delays based on response times
// Add request queuing for large batches
```

### **Phase 3: Production Optimization**

```javascript
// Distribute requests across multiple time periods
// Implement request batching
// Add comprehensive monitoring and alerting
```

## 🚨 **Risk Assessment**

### **Current Risk Level: LOW**

- ✅ 1-second delays are within Amazon's limits
- ✅ Only 5 items per run (very conservative)
- ✅ Daily limit: 5 items × 1 request = 5 requests/day (well under 8,640)

### **Production Considerations:**

- **97 total items**: Would take ~20 days to update all items
- **Daily cron**: 5 items per day is very conservative
- **Error recovery**: Need better handling of 429 responses

## 📊 **Recommended Production Settings**

### **For 97 Items:**

```javascript
// 10 items per run, 2-second delays
// Total time: ~20 seconds per run
// Daily limit: 10 requests (well under 8,640)
// Complete cycle: ~10 days for all items
```

### **For Maximum Safety:**

```javascript
// 5 items per run, 3-second delays
// Total time: ~15 seconds per run
// Daily limit: 5 requests (very conservative)
// Complete cycle: ~20 days for all items
```

---

**Status**: Current throttling is conservative and safe
**Recommendation**: Increase delay to 2-3 seconds for production
**Priority**: Low - current settings are working well
