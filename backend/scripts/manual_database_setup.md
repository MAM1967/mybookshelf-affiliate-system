# Manual Database Setup Guide

## Price Validation Queue Table Creation

Since the `exec_sql` function is not available, please create the table manually in the Supabase dashboard:

### 1. Open Supabase Dashboard

- Go to: https://supabase.com/dashboard/project/ackcgrnizuhauccnbiml
- Navigate to SQL Editor

### 2. Execute This SQL:

```sql
-- Create price validation queue table
CREATE TABLE IF NOT EXISTS price_validation_queue (
  id SERIAL PRIMARY KEY,
  item_id INTEGER REFERENCES books_accessories(id) ON DELETE CASCADE,
  old_price DECIMAL(10,2) NOT NULL,
  new_price DECIMAL(10,2) NOT NULL,
  percentage_change DECIMAL(8,2) NOT NULL,
  validation_reason TEXT NOT NULL,
  validation_layer TEXT NOT NULL,
  validation_details JSONB,
  status TEXT DEFAULT 'pending' CHECK (status IN ('pending', 'approved', 'rejected')),
  flagged_at TIMESTAMP DEFAULT NOW(),
  reviewed_at TIMESTAMP,
  reviewed_by TEXT,
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

-- Grant necessary permissions
GRANT SELECT, INSERT, UPDATE, DELETE ON price_validation_queue TO anon;
GRANT UPDATE ON books_accessories TO anon;
```

### 3. Verify Table Creation

After executing the SQL, verify the table exists by running:

```sql
SELECT * FROM price_validation_queue LIMIT 1;
```

### 4. Test API Endpoint

Once the table is created, test the API:

```bash
curl -X GET "https://mybookshelf.shop/api/price-approvals"
```

Expected response:

```json
{
  "success": true,
  "data": [],
  "statistics": {
    "pending": 0,
    "approved_today": 0,
    "rejected_today": 0,
    "total_flagged": 0
  },
  "pagination": {
    "limit": 50,
    "offset": 0,
    "total": 0
  }
}
```

## Next Steps After Database Setup

1. Test the admin interface at: https://mybookshelf.shop/admin
2. Navigate to the "🚨 Price Approvals" tab
3. Verify statistics cards show correct data
4. Test approval/rejection functionality
5. Monitor for flagged price changes from the validation system
