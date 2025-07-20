-- SIMPLE PRICE HISTORY TABLE
-- Execute this after adding columns to books_accessories

-- Step 1: Create basic price_history table
CREATE TABLE price_history (
    id SERIAL PRIMARY KEY,
    book_id INTEGER NOT NULL,
    old_price NUMERIC,
    new_price NUMERIC,
    price_change NUMERIC,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    notes TEXT
);

-- Step 2: Add foreign key constraint (run separately if needed)
ALTER TABLE price_history 
ADD CONSTRAINT fk_price_history_book 
FOREIGN KEY (book_id) REFERENCES books_accessories(id);

-- Step 3: Verify table was created
SELECT table_name, column_name, data_type 
FROM information_schema.columns 
WHERE table_name = 'price_history' 
ORDER BY ordinal_position; 