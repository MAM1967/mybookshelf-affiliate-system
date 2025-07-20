-- MINIMAL TEST - Start Here
-- Just check basics and try one simple change

-- 1. Show current table structure
SELECT column_name, data_type 
FROM information_schema.columns 
WHERE table_name = 'books_accessories' 
ORDER BY ordinal_position;

-- 2. Try adding ONE column (run this separately)
-- ALTER TABLE books_accessories ADD COLUMN price_status TEXT DEFAULT 'active';

-- 3. Check if the column was added (run after step 2)
-- SELECT column_name FROM information_schema.columns 
-- WHERE table_name = 'books_accessories' AND column_name = 'price_status'; 