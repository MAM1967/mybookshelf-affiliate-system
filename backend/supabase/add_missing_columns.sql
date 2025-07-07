-- Add missing columns to books_accessories table
-- Run this in your Supabase SQL Editor

-- Add ASIN column for Amazon product identification
ALTER TABLE books_accessories ADD COLUMN IF NOT EXISTS asin TEXT;

-- Add rating column for product ratings
ALTER TABLE books_accessories ADD COLUMN IF NOT EXISTS rating NUMERIC;

-- Add review count column
ALTER TABLE books_accessories ADD COLUMN IF NOT EXISTS review_count INTEGER;

-- Add description column
ALTER TABLE books_accessories ADD COLUMN IF NOT EXISTS description TEXT;

-- Add focus area column
ALTER TABLE books_accessories ADD COLUMN IF NOT EXISTS focus_area TEXT;

-- Add christian themes array column
ALTER TABLE books_accessories ADD COLUMN IF NOT EXISTS christian_themes TEXT[];

-- Add leadership topics array column
ALTER TABLE books_accessories ADD COLUMN IF NOT EXISTS leadership_topics TEXT[];

-- Add is_active boolean column
ALTER TABLE books_accessories ADD COLUMN IF NOT EXISTS is_active BOOLEAN DEFAULT TRUE;

-- Add created_at timestamp column
ALTER TABLE books_accessories ADD COLUMN IF NOT EXISTS created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP;

-- Make price and affiliate_link nullable since some items might not have prices initially
ALTER TABLE books_accessories ALTER COLUMN price DROP NOT NULL;
ALTER TABLE books_accessories ALTER COLUMN affiliate_link DROP NOT NULL;
ALTER TABLE books_accessories ALTER COLUMN image_url DROP NOT NULL;

-- Add index on ASIN for faster lookups
CREATE INDEX IF NOT EXISTS idx_books_accessories_asin ON books_accessories(asin);

-- Add index on category for filtering
CREATE INDEX IF NOT EXISTS idx_books_accessories_category ON books_accessories(category);

-- Add index on is_active for filtering active items
CREATE INDEX IF NOT EXISTS idx_books_accessories_active ON books_accessories(is_active); 