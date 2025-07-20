-- Price Management Schema Updates - Phase 1
-- MyBookshelf Affiliate System
-- Date: July 20, 2025
-- Purpose: Add price tracking, validation, and out-of-stock handling

-- ========================================
-- Phase 1: Database Schema Updates
-- ========================================

-- 1. Create price_history table for tracking all price changes
CREATE TABLE IF NOT EXISTS price_history (
    id SERIAL PRIMARY KEY,
    book_id INTEGER NOT NULL REFERENCES books_accessories(id) ON DELETE CASCADE,
    old_price NUMERIC,
    new_price NUMERIC,
    price_change NUMERIC GENERATED ALWAYS AS (new_price - COALESCE(old_price, 0)) STORED,
    price_change_percent NUMERIC,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    update_source TEXT DEFAULT 'automated' CHECK (update_source IN ('automated', 'manual', 'admin', 'api_fetch')),
    notes TEXT,
    amazon_status TEXT, -- HTTP status from Amazon request
    fetch_duration_ms INTEGER, -- Time taken to fetch price
    
    -- Indexes for performance
    INDEX idx_price_history_book_id (book_id),
    INDEX idx_price_history_updated_at (updated_at),
    INDEX idx_price_history_update_source (update_source)
);

-- 2. Add price metadata columns to books_accessories table
ALTER TABLE books_accessories ADD COLUMN IF NOT EXISTS last_price_check TIMESTAMP;
ALTER TABLE books_accessories ADD COLUMN IF NOT EXISTS price_status TEXT DEFAULT 'active' 
    CHECK (price_status IN ('active', 'out_of_stock', 'unavailable', 'price_error', 'discontinued'));
ALTER TABLE books_accessories ADD COLUMN IF NOT EXISTS price_updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP;
ALTER TABLE books_accessories ADD COLUMN IF NOT EXISTS price_fetch_attempts INTEGER DEFAULT 0;
ALTER TABLE books_accessories ADD COLUMN IF NOT EXISTS last_successful_fetch TIMESTAMP;
ALTER TABLE books_accessories ADD COLUMN IF NOT EXISTS price_source TEXT DEFAULT 'manual' 
    CHECK (price_source IN ('manual', 'amazon_api', 'scraping', 'admin_override'));

-- 3. Add price validation constraints
ALTER TABLE books_accessories DROP CONSTRAINT IF EXISTS valid_price_range;
ALTER TABLE books_accessories ADD CONSTRAINT valid_price_range 
    CHECK (price IS NULL OR price >= 0);

-- 4. Add price change tracking triggers
CREATE OR REPLACE FUNCTION log_price_change()
RETURNS TRIGGER AS $$
BEGIN
    -- Only log if price actually changed
    IF OLD.price IS DISTINCT FROM NEW.price THEN
        INSERT INTO price_history (
            book_id, 
            old_price, 
            new_price,
            price_change_percent,
            update_source,
            notes
        ) VALUES (
            NEW.id,
            OLD.price,
            NEW.price,
            CASE 
                WHEN OLD.price > 0 THEN ROUND(((NEW.price - OLD.price) / OLD.price * 100)::numeric, 2)
                ELSE NULL
            END,
            COALESCE(NEW.price_source, 'manual'),
            CASE 
                WHEN NEW.price_status = 'out_of_stock' THEN 'Item went out of stock'
                WHEN OLD.price_status = 'out_of_stock' AND NEW.price_status = 'active' THEN 'Item back in stock'
                WHEN NEW.price > OLD.price THEN 'Price increased'
                WHEN NEW.price < OLD.price THEN 'Price decreased'
                ELSE 'Price updated'
            END
        );
        
        -- Update the price_updated_at timestamp
        NEW.price_updated_at = CURRENT_TIMESTAMP;
    END IF;
    
    -- Update last_price_check timestamp
    NEW.last_price_check = CURRENT_TIMESTAMP;
    
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Create trigger for automatic price change logging
DROP TRIGGER IF EXISTS trigger_log_price_change ON books_accessories;
CREATE TRIGGER trigger_log_price_change
    BEFORE UPDATE ON books_accessories
    FOR EACH ROW
    EXECUTE FUNCTION log_price_change();

-- 5. Create indexes for optimal performance
CREATE INDEX IF NOT EXISTS idx_books_accessories_price_status ON books_accessories(price_status);
CREATE INDEX IF NOT EXISTS idx_books_accessories_last_price_check ON books_accessories(last_price_check);
CREATE INDEX IF NOT EXISTS idx_books_accessories_price_updated_at ON books_accessories(price_updated_at);

-- 6. Initialize existing records with default values
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

-- 7. Create helpful views for price monitoring
CREATE OR REPLACE VIEW price_monitoring_dashboard AS
SELECT 
    ba.id,
    ba.title,
    ba.author,
    ba.price,
    ba.price_status,
    ba.last_price_check,
    ba.price_updated_at,
    ba.price_fetch_attempts,
    ph.price_change,
    ph.price_change_percent,
    ph.updated_at as last_price_change
FROM books_accessories ba
LEFT JOIN LATERAL (
    SELECT price_change, price_change_percent, updated_at
    FROM price_history 
    WHERE book_id = ba.id 
    ORDER BY updated_at DESC 
    LIMIT 1
) ph ON true
ORDER BY ba.price_updated_at DESC;

-- 8. Create view for items needing price updates
CREATE OR REPLACE VIEW items_needing_price_update AS
SELECT 
    id,
    title,
    author,
    price,
    price_status,
    last_price_check,
    EXTRACT(EPOCH FROM (CURRENT_TIMESTAMP - COALESCE(last_price_check, '1970-01-01'::timestamp))) / 3600 as hours_since_check,
    price_fetch_attempts
FROM books_accessories
WHERE 
    price_status IN ('active', 'price_error') 
    AND (
        last_price_check IS NULL 
        OR last_price_check < CURRENT_TIMESTAMP - INTERVAL '24 hours'
        OR (price_status = 'price_error' AND last_price_check < CURRENT_TIMESTAMP - INTERVAL '1 hour')
    )
ORDER BY 
    CASE 
        WHEN last_price_check IS NULL THEN 0  -- Highest priority: never checked
        WHEN price_status = 'price_error' THEN 1  -- High priority: errors
        ELSE 2  -- Normal priority: regular updates
    END,
    last_price_check ASC NULLS FIRST;

-- 9. Grant necessary permissions (adjust as needed for your setup)
-- GRANT SELECT, INSERT, UPDATE ON price_history TO authenticated;
-- GRANT SELECT ON price_monitoring_dashboard TO authenticated;
-- GRANT SELECT ON items_needing_price_update TO authenticated;

-- 10. Add comments for documentation
COMMENT ON TABLE price_history IS 'Tracks all price changes with full audit trail';
COMMENT ON COLUMN books_accessories.price_status IS 'Current availability status: active, out_of_stock, unavailable, price_error, discontinued';
COMMENT ON COLUMN books_accessories.last_price_check IS 'Timestamp of last price check attempt (success or failure)';
COMMENT ON COLUMN books_accessories.price_updated_at IS 'Timestamp when price was last successfully updated';
COMMENT ON VIEW price_monitoring_dashboard IS 'Admin dashboard view for monitoring price changes and status';
COMMENT ON VIEW items_needing_price_update IS 'Items that need price updates based on last check time and status';

-- ========================================
-- Schema Update Complete
-- ========================================

-- Verify the changes
SELECT 
    'price_history table' as component,
    CASE WHEN EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = 'price_history') 
         THEN '✅ Created' 
         ELSE '❌ Missing' 
    END as status
UNION ALL
SELECT 
    'price_status column' as component,
    CASE WHEN EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = 'books_accessories' AND column_name = 'price_status') 
         THEN '✅ Added' 
         ELSE '❌ Missing' 
    END as status
UNION ALL
SELECT 
    'price_monitoring_dashboard view' as component,
    CASE WHEN EXISTS (SELECT 1 FROM information_schema.views WHERE table_name = 'price_monitoring_dashboard') 
         THEN '✅ Created' 
         ELSE '❌ Missing' 
    END as status; 