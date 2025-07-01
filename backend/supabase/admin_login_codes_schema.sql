-- Admin Login Codes Table for Passwordless Authentication
-- MyBookshelf Affiliate System

CREATE TABLE admin_login_codes (
    id SERIAL PRIMARY KEY,
    code VARCHAR(6) NOT NULL,
    expires_at TIMESTAMP NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    used_at TIMESTAMP,
    is_used BOOLEAN DEFAULT FALSE
);

-- Create indexes for performance
CREATE INDEX idx_admin_login_codes_code ON admin_login_codes(code);
CREATE INDEX idx_admin_login_codes_expires ON admin_login_codes(expires_at);
CREATE INDEX idx_admin_login_codes_used ON admin_login_codes(is_used);

-- Function to clean up expired codes
CREATE OR REPLACE FUNCTION cleanup_expired_login_codes()
RETURNS INTEGER AS $$
DECLARE
    deleted_count INTEGER;
BEGIN
    DELETE FROM admin_login_codes 
    WHERE expires_at < CURRENT_TIMESTAMP 
    OR is_used = TRUE;
    
    GET DIAGNOSTICS deleted_count = ROW_COUNT;
    RETURN deleted_count;
END;
$$ LANGUAGE plpgsql;

-- Create a scheduled job to clean up expired codes (optional)
-- This would need to be set up in your Supabase dashboard
-- SELECT cron.schedule('cleanup-login-codes', '0 */6 * * *', 'SELECT cleanup_expired_login_codes();'); 