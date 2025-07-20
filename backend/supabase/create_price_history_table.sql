-- CREATE PRICE_HISTORY TABLE
-- Run this AFTER adding columns to books_accessories

-- STEP 1: Create price_history table
CREATE TABLE price_history (
    id SERIAL PRIMARY KEY,
    book_id INTEGER NOT NULL,
    old_price NUMERIC,
    new_price NUMERIC,
    price_change NUMERIC,
    price_change_percent NUMERIC,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    update_source TEXT DEFAULT 'automated',
    notes TEXT
);

-- STEP 2: Add foreign key constraint
ALTER TABLE price_history 
ADD CONSTRAINT fk_price_history_book 
FOREIGN KEY (book_id) REFERENCES books_accessories(id) ON DELETE CASCADE;

-- STEP 3: Add indexes for performance
CREATE INDEX idx_price_history_book_id ON price_history(book_id);
CREATE INDEX idx_price_history_updated_at ON price_history(updated_at);

-- STEP 4: Verify table was created
SELECT table_name, column_name, data_type 
FROM information_schema.columns 
WHERE table_name = 'price_history' 
ORDER BY ordinal_position;

-- STEP 5: Test inserting a sample record (optional)
-- INSERT INTO price_history (book_id, old_price, new_price, price_change, notes)
-- VALUES (1, 19.99, 21.99, 2.00, 'Test price change');

-- STEP 6: Verify the insert worked (if you ran step 5)
-- SELECT * FROM price_history ORDER BY updated_at DESC LIMIT 1; 