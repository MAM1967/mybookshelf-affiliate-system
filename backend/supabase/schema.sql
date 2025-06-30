CREATE TABLE books_accessories (
    id SERIAL PRIMARY KEY,
    title TEXT NOT NULL,
    author TEXT NOT NULL,
    price NUMERIC NOT NULL,
    affiliate_link TEXT NOT NULL,
    image_url TEXT NOT NULL,
    category TEXT NOT NULL,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

ALTER TABLE pending_books ADD COLUMN IF NOT EXISTS scheduled_post_at timestamp with time zone;
ALTER TABLE pending_books ADD COLUMN IF NOT EXISTS posted_at timestamp with time zone;
ALTER TABLE pending_books ADD COLUMN IF NOT EXISTS post_status text DEFAULT 'pending';
ALTER TABLE pending_books ADD COLUMN IF NOT EXISTS post_content text;
