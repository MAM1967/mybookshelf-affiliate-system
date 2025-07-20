-- SIMPLE PRICE COLUMNS - Step by Step
-- Execute each statement individually and check for errors

-- Step 1: Add basic price status column
ALTER TABLE books_accessories ADD COLUMN price_status TEXT DEFAULT 'active';

-- Step 2: Add last price check column  
ALTER TABLE books_accessories ADD COLUMN last_price_check TIMESTAMP;

-- Step 3: Add price updated timestamp
ALTER TABLE books_accessories ADD COLUMN price_updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP;

-- Step 4: Add price source column
ALTER TABLE books_accessories ADD COLUMN price_source TEXT DEFAULT 'manual';

-- Step 5: Add fetch attempts counter
ALTER TABLE books_accessories ADD COLUMN price_fetch_attempts INTEGER DEFAULT 0;

-- Step 6: Verify columns were added
SELECT column_name, data_type, is_nullable, column_default
FROM information_schema.columns 
WHERE table_name = 'books_accessories' 
  AND column_name IN ('price_status', 'last_price_check', 'price_updated_at', 'price_source', 'price_fetch_attempts')
ORDER BY column_name; 