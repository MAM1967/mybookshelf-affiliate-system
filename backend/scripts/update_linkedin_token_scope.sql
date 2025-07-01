-- Update LinkedIn Token Scope to include rw_organization_admin
-- Run this in your Supabase SQL editor

-- First, let's see the current token scope
SELECT admin_email, scope, created_at, updated_at 
FROM linkedin_tokens 
WHERE is_active = true;

-- Update the scope to include rw_organization_admin
UPDATE linkedin_tokens 
SET 
    scope = 'email,openid,profile,w_member_social,rw_organization_admin',
    updated_at = CURRENT_TIMESTAMP
WHERE is_active = true;

-- Verify the update
SELECT admin_email, scope, created_at, updated_at 
FROM linkedin_tokens 
WHERE is_active = true;

-- Note: This is a temporary fix. The proper solution is to re-authenticate 
-- with LinkedIn to get a fresh token that includes the rw_organization_admin scope.
-- This update just ensures the database reflects the expected scope. 