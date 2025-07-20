-- ADD PRICE TRACKING COLUMNS - Step by Step
-- Current table has: id, title, author, price, affiliate_link, image_url, category, timestamp
-- Run each step individually and verify before proceeding

-- STEP 1: Add price_status column
ALTER TABLE books_accessories ADD COLUMN price_status TEXT DEFAULT 'active';

-- Verify Step 1:
SELECT column_name FROM information_schema.columns 
WHERE table_name = 'books_accessories' AND column_name = 'price_status';

-- STEP 2: Add last_price_check column
ALTER TABLE books_accessories ADD COLUMN last_price_check TIMESTAMP;

-- Verify Step 2:
SELECT column_name FROM information_schema.columns 
WHERE table_name = 'books_accessories' AND column_name = 'last_price_check';

-- STEP 3: Add price_updated_at column
ALTER TABLE books_accessories ADD COLUMN price_updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP;

-- Verify Step 3:
SELECT column_name FROM information_schema.columns 
WHERE table_name = 'books_accessories' AND column_name = 'price_updated_at';

-- STEP 4: Add price_source column
ALTER TABLE books_accessories ADD COLUMN price_source TEXT DEFAULT 'manual';

-- Verify Step 4:
SELECT column_name FROM information_schema.columns 
WHERE table_name = 'books_accessories' AND column_name = 'price_source';

-- STEP 5: Add price_fetch_attempts column
ALTER TABLE books_accessories ADD COLUMN price_fetch_attempts INTEGER DEFAULT 0;

-- Verify Step 5:
SELECT column_name FROM information_schema.columns 
WHERE table_name = 'books_accessories' AND column_name = 'price_fetch_attempts';

-- STEP 6: Initialize existing records with default values
UPDATE books_accessories 
SET 
    price_status = CASE 
        WHEN price IS NULL OR price = 0 THEN 'out_of_stock'
        ELSE 'active'
    END,
    price_updated_at = COALESCE(timestamp, CURRENT_TIMESTAMP),
    last_price_check = COALESCE(timestamp, CURRENT_TIMESTAMP),
    price_source = 'manual',
    price_fetch_attempts = 0
WHERE price_status IS NULL;

-- STEP 7: Verify all new columns exist
SELECT column_name, data_type, column_default
FROM information_schema.columns 
WHERE table_name = 'books_accessories' 
  AND column_name IN ('price_status', 'last_price_check', 'price_updated_at', 'price_source', 'price_fetch_attempts')
ORDER BY column_name; 