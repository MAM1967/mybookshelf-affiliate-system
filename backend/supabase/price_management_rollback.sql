-- Price Management Schema Rollback Script
-- MyBookshelf Affiliate System
-- Date: July 20, 2025
-- Purpose: Rollback Phase 1 pricing schema changes if needed

-- ========================================
-- EMERGENCY ROLLBACK: Phase 1 Changes
-- ========================================

-- WARNING: This will remove ALL price history data
-- Only run this if you need to completely undo the pricing updates

-- 1. Drop the trigger first
DROP TRIGGER IF EXISTS trigger_log_price_change ON books_accessories;

-- 2. Drop the trigger function
DROP FUNCTION IF EXISTS log_price_change();

-- 3. Drop the views
DROP VIEW IF EXISTS price_monitoring_dashboard;
DROP VIEW IF EXISTS items_needing_price_update;

-- 4. Drop the price_history table (WARNING: This deletes all price history)
DROP TABLE IF EXISTS price_history;

-- 5. Remove added columns from books_accessories
ALTER TABLE books_accessories DROP COLUMN IF EXISTS last_price_check;
ALTER TABLE books_accessories DROP COLUMN IF EXISTS price_status;
ALTER TABLE books_accessories DROP COLUMN IF EXISTS price_updated_at;
ALTER TABLE books_accessories DROP COLUMN IF EXISTS price_fetch_attempts;
ALTER TABLE books_accessories DROP COLUMN IF EXISTS last_successful_fetch;
ALTER TABLE books_accessories DROP COLUMN IF EXISTS price_source;

-- 6. Remove price validation constraints
ALTER TABLE books_accessories DROP CONSTRAINT IF EXISTS valid_price_range;

-- 7. Drop indexes
DROP INDEX IF EXISTS idx_books_accessories_price_status;
DROP INDEX IF EXISTS idx_books_accessories_last_price_check;
DROP INDEX IF EXISTS idx_books_accessories_price_updated_at;

-- 8. Restore original price constraint if it existed
-- ALTER TABLE books_accessories ALTER COLUMN price SET NOT NULL;

-- ========================================
-- Rollback Complete
-- ========================================

-- Verify rollback
SELECT 
    'price_history table' as component,
    CASE WHEN EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = 'price_history') 
         THEN '❌ Still exists' 
         ELSE '✅ Removed' 
    END as status
UNION ALL
SELECT 
    'price_status column' as component,
    CASE WHEN EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = 'books_accessories' AND column_name = 'price_status') 
         THEN '❌ Still exists' 
         ELSE '✅ Removed' 
    END as status
UNION ALL
SELECT 
    'trigger_log_price_change' as component,
    CASE WHEN EXISTS (SELECT 1 FROM information_schema.triggers WHERE trigger_name = 'trigger_log_price_change') 
         THEN '❌ Still exists' 
         ELSE '✅ Removed' 
    END as status; 