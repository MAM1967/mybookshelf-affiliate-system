-- Add organization admin scope column to LinkedIn tokens table
-- Run this in your Supabase SQL editor

-- Add the column
ALTER TABLE linkedin_tokens 
ADD COLUMN has_organization_admin BOOLEAN DEFAULT FALSE;

-- Update existing tokens to reflect current scope
UPDATE linkedin_tokens 
SET has_organization_admin = TRUE 
WHERE scope LIKE '%rw_organization_admin%' OR scope LIKE '%organization%';

-- Create index for performance
CREATE INDEX idx_linkedin_tokens_org_admin ON linkedin_tokens(has_organization_admin);

-- Verify the changes
SELECT admin_email, scope, has_organization_admin, created_at 
FROM linkedin_tokens 
WHERE is_active = true; 