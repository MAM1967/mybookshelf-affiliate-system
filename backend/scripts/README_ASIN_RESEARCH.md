# MyBookshelf ASIN Research & Database Insertion Workflow

This directory contains scripts to research Amazon ASINs for 75 books and 25 accessories, then insert them into the Supabase database.

## 📋 Overview

The workflow consists of three main phases:

1. **Bulk ASIN Research** - Automated and manual research of Amazon ASINs
2. **Manual Research Helper** - Interactive tool for manual ASIN research
3. **Database Insertion** - Insert researched items into Supabase database

## 🚀 Quick Start

### Prerequisites

1. **Install required packages:**

   ```bash
   pip install amazon-paapi5 supabase
   ```

2. **Set up environment variables:**

   ```bash
   export SUPABASE_URL="your_supabase_url"
   export SUPABASE_ANON_KEY="your_supabase_anon_key"
   export SUPABASE_SERVICE_ROLE_KEY="your_supabase_service_role_key"
   ```

3. **Optional - Amazon PA API credentials:**
   ```bash
   export AMAZON_ACCESS_KEY="your_amazon_access_key"
   export AMAZON_SECRET_KEY="your_amazon_secret_key"
   export AMAZON_ASSOCIATE_TAG="mybookshelf-20"
   ```

### Step 1: Initial Research

Run the bulk research script to identify items needing manual research:

```bash
python3 bulk_asin_research.py
```

This will:

- Load the inventory from `books_and_accessories_2025.json`
- Attempt to find ASINs using Amazon PA API (if credentials available)
- Generate a research results file with all items marked for manual research
- Create Amazon search URLs for each item

**Output:** `asin_research_results_YYYYMMDD_HHMMSS.json`

### Step 2: Manual Research

Use the interactive helper to research ASINs manually:

```bash
python3 manual_asin_research_helper.py asin_research_results_YYYYMMDD_HHMMSS.json
```

**Options:**

- **Option 1:** Interactive research session (recommended)
- **Option 2:** Generate research report with search URLs
- **Option 3:** Exit

**Interactive Session Features:**

- Displays one item at a time with Amazon search URL
- Prompts for ASIN, price, image URL, rating, and review count
- Auto-saves progress after each item
- Can be interrupted and resumed later

**Output:** `asin_research_results_YYYYMMDD_HHMMSS_updated.json`

### Step 3: Database Insertion

Insert researched items into the database:

```bash
# Dry run (preview what would be inserted)
python3 database_insertion_script.py asin_research_results_YYYYMMDD_HHMMSS_updated.json --dry-run

# Actual insertion
python3 database_insertion_script.py asin_research_results_YYYYMMDD_HHMMSS_updated.json
```

## 📊 Expected Results

### Research Phase

- **Total Items:** 100 (75 books + 25 accessories)
- **Initial Success Rate:** 0% (all items need manual research)
- **Target Success Rate:** 90%+ (90+ items with valid ASINs)

### Database Phase

- **Items Ready:** Based on research results
- **Items Inserted:** New items added to database
- **Items Skipped:** Already existing in database
- **Success Rate:** 95%+ insertion success

## 🔧 Script Details

### 1. `bulk_asin_research.py`

**Purpose:** Initial research and inventory analysis

**Features:**

- Loads inventory from JSON file
- Attempts Amazon PA API search (if credentials available)
- Generates Amazon search URLs for manual research
- Creates comprehensive research file with all metadata

**Input:** `books_and_accessories_2025.json`
**Output:** `asin_research_results_YYYYMMDD_HHMMSS.json`

### 2. `manual_asin_research_helper.py`

**Purpose:** Interactive manual research tool

**Features:**

- Interactive session for manual ASIN research
- Amazon search URL generation
- Progress tracking and auto-save
- Research report generation
- Data validation and formatting

**Input:** Research results file
**Output:** Updated research file with ASINs

### 3. `database_insertion_script.py`

**Purpose:** Database insertion with validation

**Features:**

- Duplicate detection (prevents re-insertion)
- Data formatting for database schema
- Dry run mode for testing
- Comprehensive reporting
- Error handling and logging

**Input:** Updated research file
**Output:** Database records in `books_accessories` table

## 📋 Manual Research Process

### For Each Item:

1. **Click the Amazon search URL** provided by the helper
2. **Find the correct item** (usually first result)
3. **Copy the ASIN** from the product URL:
   - URL format: `https://amazon.com/dp/B08XXXXX`
   - ASIN is the `B08XXXXX` part
4. **Note the current price** (e.g., $29.99)
5. **Copy the main product image URL**:
   - Right-click on main product image
   - Copy image address
6. **Note the rating** (e.g., 4.5 out of 5)
7. **Note the review count** (e.g., 1,250 reviews)

### Research Tips:

- **Books:** Search by title + author for best results
- **Accessories:** Search by exact product name
- **Multiple editions:** Choose the most popular/main edition
- **Pricing:** Use current Amazon price (may vary)
- **Images:** Use high-quality main product image
- **Ratings:** Include both rating and review count if available

## 🗄️ Database Schema

Items are inserted into the `books_accessories` table with these fields:

```sql
CREATE TABLE books_accessories (
    id SERIAL PRIMARY KEY,
    title TEXT NOT NULL,
    author TEXT NOT NULL,
    price NUMERIC NOT NULL,
    affiliate_link TEXT NOT NULL,
    image_url TEXT NOT NULL,
    category TEXT NOT NULL,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

**Field Mapping:**

- `title` → Item title
- `author` → Author name (or "N/A" for accessories)
- `price` → Current Amazon price
- `affiliate_link` → Generated affiliate link with `mybookshelf-20` tag
- `image_url` → Product image URL
- `category` → "book" or "accessory"

## 📈 Success Metrics

### Research Success:

- **90%+ items** with valid ASINs
- **All items** with current pricing
- **All items** with product images
- **Complete affiliate links** for revenue tracking

### Database Success:

- **95%+ insertion rate** for new items
- **No duplicate entries** (proper duplicate detection)
- **Valid data** in all required fields
- **Ready for LinkedIn posting** automation

## 🔄 Workflow Automation

### Batch Processing:

The scripts support batch processing for large inventories:

```bash
# Process all items in one session
python3 manual_asin_research_helper.py research_file.json

# Resume interrupted session
python3 manual_asin_research_helper.py research_file_updated.json
```

### Progress Tracking:

- Research progress saved after each item
- Can interrupt and resume at any time
- Comprehensive logging of all operations
- Detailed reports of success/failure rates

## 🚨 Troubleshooting

### Common Issues:

1. **Amazon API not working:**

   - Check credentials in environment variables
   - Verify API access and rate limits
   - Fall back to manual research

2. **Supabase connection failed:**

   - Verify environment variables
   - Check network connectivity
   - Ensure Supabase project is active

3. **Duplicate items:**

   - Script automatically detects and skips existing items
   - Check database for existing titles

4. **Invalid ASINs:**
   - Verify ASIN format (B08XXXXX)
   - Test affiliate links manually
   - Re-research problematic items

### Error Recovery:

- **Interrupted research:** Resume with updated file
- **Failed insertions:** Check logs and retry
- **Invalid data:** Manually correct and re-run

## 📞 Support

For issues or questions:

1. Check the logs for detailed error messages
2. Verify environment variables are set correctly
3. Test individual components (Amazon API, Supabase connection)
4. Review the research data for data quality issues

## 🎯 Next Steps

After successful database insertion:

1. **Verify items** in Supabase dashboard
2. **Test LinkedIn posting** with new items
3. **Monitor affiliate revenue** from expanded catalog
4. **Optimize content** based on performance data
5. **Scale up** with additional items as needed

---

**Status:** Ready for production use
**Last Updated:** July 4, 2025
**Version:** 1.0
