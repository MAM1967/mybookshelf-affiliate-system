-- FIXED SCHEMA DIAGNOSTICS
-- Run this to understand current database state

-- 1. Check current books_accessories table structure
SELECT 
    column_name, 
    data_type, 
    is_nullable, 
    column_default,
    character_maximum_length
FROM information_schema.columns 
WHERE table_name = 'books_accessories' 
ORDER BY ordinal_position;

-- 2. Check if price_history table exists
SELECT EXISTS (
    SELECT 1 FROM information_schema.tables 
    WHERE table_name = 'price_history'
) as price_history_exists;

-- 3. Check current constraints on books_accessories (FIXED)
SELECT 
    tc.constraint_name,
    tc.constraint_type,
    ccu.column_name,
    tc.table_name
FROM information_schema.table_constraints tc
JOIN information_schema.constraint_column_usage ccu 
    ON tc.constraint_name = ccu.constraint_name
WHERE tc.table_name = 'books_accessories';

-- 4. Sample data from books_accessories to see current state
SELECT 
    id, 
    title, 
    price, 
    CASE 
        WHEN price IS NULL THEN 'NULL'
        WHEN price = 0 THEN 'ZERO'
        ELSE 'HAS_VALUE'
    END as price_status
FROM books_accessories 
LIMIT 5;

-- 5. Check database version and capabilities
SELECT version();

-- 6. Check if we have necessary permissions
SELECT 
    has_table_privilege('books_accessories', 'INSERT') as can_insert,
    has_table_privilege('books_accessories', 'UPDATE') as can_update,
    has_schema_privilege('public', 'CREATE') as can_create_tables; 