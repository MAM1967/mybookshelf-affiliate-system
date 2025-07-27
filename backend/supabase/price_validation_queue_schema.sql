-- Price Validation Queue Schema
-- Created: July 27, 2025
-- Purpose: Store flagged price changes for admin review and approval

-- Create price validation queue table
CREATE TABLE IF NOT EXISTS price_validation_queue (
  id SERIAL PRIMARY KEY,
  item_id INTEGER REFERENCES books_accessories(id) ON DELETE CASCADE,
  old_price DECIMAL(10,2) NOT NULL,
  new_price DECIMAL(10,2) NOT NULL,
  percentage_change DECIMAL(8,2) NOT NULL,
  validation_reason TEXT NOT NULL,
  validation_layer TEXT NOT NULL, -- sanity_checks, threshold_validation, statistical_validation, context_validation
  validation_details JSONB, -- Detailed validation information from enterprise system
  status TEXT DEFAULT 'pending' CHECK (status IN ('pending', 'approved', 'rejected')),
  flagged_at TIMESTAMP DEFAULT NOW(),
  reviewed_at TIMESTAMP,
  reviewed_by TEXT, -- Admin identifier
  admin_notes TEXT,
  created_at TIMESTAMP DEFAULT NOW(),
  updated_at TIMESTAMP DEFAULT NOW()
);

-- Add indexes for efficient querying
CREATE INDEX IF NOT EXISTS idx_price_validation_queue_status ON price_validation_queue(status);
CREATE INDEX IF NOT EXISTS idx_price_validation_queue_item_id ON price_validation_queue(item_id);
CREATE INDEX IF NOT EXISTS idx_price_validation_queue_flagged_at ON price_validation_queue(flagged_at);
CREATE INDEX IF NOT EXISTS idx_price_validation_queue_percentage_change ON price_validation_queue(percentage_change);

-- Add validation tracking columns to books_accessories table
ALTER TABLE books_accessories ADD COLUMN IF NOT EXISTS last_validation_status TEXT;
ALTER TABLE books_accessories ADD COLUMN IF NOT EXISTS validation_notes TEXT;
ALTER TABLE books_accessories ADD COLUMN IF NOT EXISTS requires_approval BOOLEAN DEFAULT FALSE;

-- Create index for requires_approval for efficient filtering
CREATE INDEX IF NOT EXISTS idx_books_accessories_requires_approval ON books_accessories(requires_approval);

-- Add trigger to update updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

CREATE TRIGGER update_price_validation_queue_updated_at 
    BEFORE UPDATE ON price_validation_queue 
    FOR EACH ROW 
    EXECUTE FUNCTION update_updated_at_column();

-- Create view for easy querying of pending approvals with book details
CREATE OR REPLACE VIEW pending_price_approvals AS
SELECT 
    pvq.id,
    pvq.item_id,
    ba.title,
    ba.affiliate_link,
    pvq.old_price,
    pvq.new_price,
    pvq.percentage_change,
    pvq.validation_reason,
    pvq.validation_layer,
    pvq.validation_details,
    pvq.status,
    pvq.flagged_at,
    pvq.reviewed_at,
    pvq.reviewed_by,
    pvq.admin_notes,
    pvq.created_at,
    pvq.updated_at
FROM price_validation_queue pvq
JOIN books_accessories ba ON pvq.item_id = ba.id
WHERE pvq.status = 'pending'
ORDER BY pvq.flagged_at DESC;

-- Insert sample data for testing (optional)
-- INSERT INTO price_validation_queue (item_id, old_price, new_price, percentage_change, validation_reason, validation_layer, validation_details)
-- VALUES 
--   (1, 12.89, 102.99, 698.99, 'extreme_change_699.0pct_exceeds_35pct_limit', 'threshold_validation', '{"priceCategory": "low_value", "maxChangePercent": 35, "actualChange": 698.99}'),
--   (2, 8.77, 92.28, 952.34, 'extreme_change_952.3pct_exceeds_35pct_limit', 'threshold_validation', '{"priceCategory": "low_value", "maxChangePercent": 35, "actualChange": 952.34}');

-- Grant necessary permissions
GRANT SELECT, INSERT, UPDATE, DELETE ON price_validation_queue TO anon;
GRANT SELECT ON pending_price_approvals TO anon;
GRANT UPDATE ON books_accessories TO anon; 