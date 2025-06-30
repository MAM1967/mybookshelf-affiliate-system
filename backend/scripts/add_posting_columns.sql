-- Add missing columns for LinkedIn posting tracking
ALTER TABLE pending_books ADD COLUMN IF NOT EXISTS posted_at timestamp with time zone;
ALTER TABLE pending_books ADD COLUMN IF NOT EXISTS post_status text DEFAULT 'pending';
ALTER TABLE pending_books ADD COLUMN IF NOT EXISTS post_content text;
