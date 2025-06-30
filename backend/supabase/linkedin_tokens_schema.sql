-- LinkedIn Tokens Storage Table
-- Add this to your Supabase database

CREATE TABLE linkedin_tokens (
    id SERIAL PRIMARY KEY,
    admin_email TEXT UNIQUE NOT NULL,
    access_token TEXT NOT NULL,
    token_type TEXT DEFAULT 'Bearer',
    expires_at TIMESTAMP NOT NULL,
    scope TEXT,
    
    -- LinkedIn user info
    linkedin_user_id TEXT,
    linkedin_name TEXT,
    linkedin_email TEXT,
    
    -- Metadata
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    is_active BOOLEAN DEFAULT TRUE,
    
    -- Usage tracking
    last_used_at TIMESTAMP,
    posts_count INTEGER DEFAULT 0
);

-- Create index for performance
CREATE INDEX idx_linkedin_tokens_email ON linkedin_tokens(admin_email);
CREATE INDEX idx_linkedin_tokens_active ON linkedin_tokens(is_active);

-- Function to update timestamp on token updates
CREATE OR REPLACE FUNCTION update_linkedin_token_timestamp()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Trigger for automatic timestamp updates
CREATE TRIGGER linkedin_tokens_updated_at
    BEFORE UPDATE ON linkedin_tokens
    FOR EACH ROW
    EXECUTE FUNCTION update_linkedin_token_timestamp();
