-- MANUAL SQL COMMANDS TO RUN IN SUPABASE DASHBOARD
-- Copy and paste each section into the SQL Editor

-- 1. Add price tracking columns
ALTER TABLE books_accessories ADD COLUMN IF NOT EXISTS price_status TEXT DEFAULT 'active';
ALTER TABLE books_accessories ADD COLUMN IF NOT EXISTS last_price_check TIMESTAMP;
ALTER TABLE books_accessories ADD COLUMN IF NOT EXISTS price_updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP;
ALTER TABLE books_accessories ADD COLUMN IF NOT EXISTS price_source TEXT DEFAULT 'manual';
ALTER TABLE books_accessories ADD COLUMN IF NOT EXISTS price_fetch_attempts INTEGER DEFAULT 0;

-- 2. Create price_history table
CREATE TABLE IF NOT EXISTS price_history (
    id SERIAL PRIMARY KEY,
    book_id INTEGER NOT NULL REFERENCES books_accessories(id) ON DELETE CASCADE,
    old_price NUMERIC,
    new_price NUMERIC,
    price_change NUMERIC,
    price_change_percent NUMERIC,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    update_source TEXT DEFAULT 'automated',
    notes TEXT
);

-- 3. Add indexes
CREATE INDEX IF NOT EXISTS idx_price_history_book_id ON price_history(book_id);
CREATE INDEX IF NOT EXISTS idx_price_history_updated_at ON price_history(updated_at);

-- 4. Initialize existing records
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

-- 5. Verify changes
SELECT column_name FROM information_schema.columns 
WHERE table_name = 'books_accessories' 
  AND column_name IN ('price_status', 'last_price_check', 'price_updated_at', 'price_source', 'price_fetch_attempts');
