-- Admin Approval System Database Schema
-- MyBookshelf Affiliate System

-- Pending books awaiting admin approval
CREATE TABLE pending_books (
    id SERIAL PRIMARY KEY,
    title TEXT NOT NULL,
    author TEXT NOT NULL,
    isbn TEXT,
    amazon_asin TEXT,
    suggested_price NUMERIC,
    affiliate_link TEXT,
    image_url TEXT,
    category TEXT NOT NULL CHECK (category IN ('Books', 'Accessories')),
    
    -- Content analysis
    content_summary TEXT,
    christian_themes TEXT[],
    leadership_topics TEXT[],
    target_audience TEXT,
    
    -- Filtering flags
    passes_content_filter BOOLEAN DEFAULT TRUE,
    content_filter_notes TEXT,
    
    -- Approval workflow
    status TEXT NOT NULL DEFAULT 'pending' CHECK (status IN ('pending', 'approved', 'rejected', 'needs_review')),
    submitted_by TEXT DEFAULT 'system',
    submitted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    -- Admin decision
    reviewed_by TEXT,
    reviewed_at TIMESTAMP,
    admin_notes TEXT,
    rejection_reason TEXT,
    
    -- Scheduling
    scheduled_post_date DATE,
    week_of_year INTEGER,
    
    UNIQUE(amazon_asin),
    UNIQUE(title, author)
);

-- Admin approval sessions (Sunday workflow)
CREATE TABLE approval_sessions (
    id SERIAL PRIMARY KEY,
    session_date DATE NOT NULL,
    admin_email TEXT NOT NULL,
    
    -- Session status
    status TEXT NOT NULL DEFAULT 'pending' CHECK (status IN ('pending', 'in_progress', 'completed', 'expired')),
    started_at TIMESTAMP,
    completed_at TIMESTAMP,
    expires_at TIMESTAMP DEFAULT (CURRENT_TIMESTAMP + INTERVAL '7 days'),
    
    -- Session stats
    books_reviewed INTEGER DEFAULT 0,
    books_approved INTEGER DEFAULT 0,
    books_rejected INTEGER DEFAULT 0,
    
    -- Access control
    access_token TEXT UNIQUE,
    last_accessed TIMESTAMP,
    
    UNIQUE(session_date)
);

-- Content filtering rules
CREATE TABLE content_filter_rules (
    id SERIAL PRIMARY KEY,
    rule_type TEXT NOT NULL CHECK (rule_type IN ('forbidden_words', 'required_themes', 'author_blacklist', 'publisher_blacklist')),
    rule_value TEXT NOT NULL,
    description TEXT,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Weekly content calendar
CREATE TABLE content_calendar (
    id SERIAL PRIMARY KEY,
    week_start_date DATE NOT NULL,
    year INTEGER NOT NULL,
    week_number INTEGER NOT NULL,
    
    -- Planned content (3 books + 1 accessory)
    book_1_id INTEGER REFERENCES books_accessories(id),
    book_2_id INTEGER REFERENCES books_accessories(id),
    book_3_id INTEGER REFERENCES books_accessories(id),
    accessory_id INTEGER REFERENCES books_accessories(id),
    
    -- Content themes
    weekly_theme TEXT,
    leadership_focus TEXT,
    
    -- Status
    status TEXT NOT NULL DEFAULT 'planning' CHECK (status IN ('planning', 'approved', 'published', 'completed')),
    approved_at TIMESTAMP,
    published_at TIMESTAMP,
    
    UNIQUE(year, week_number)
);

-- Author diversity tracking
CREATE TABLE author_stats (
    id SERIAL PRIMARY KEY,
    author_name TEXT NOT NULL,
    books_published INTEGER DEFAULT 0,
    last_published_date DATE,
    diversity_score NUMERIC DEFAULT 0,
    
    -- Author metadata
    author_background TEXT,
    expertise_areas TEXT[],
    christian_perspective BOOLEAN DEFAULT TRUE,
    
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    UNIQUE(author_name)
);

-- Approval workflow audit log
CREATE TABLE approval_audit_log (
    id SERIAL PRIMARY KEY,
    book_id INTEGER REFERENCES pending_books(id),
    session_id INTEGER REFERENCES approval_sessions(id),
    
    action TEXT NOT NULL CHECK (action IN ('submitted', 'reviewed', 'approved', 'rejected', 'scheduled', 'published')),
    performed_by TEXT NOT NULL,
    performed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    -- Action details
    old_status TEXT,
    new_status TEXT,
    notes TEXT,
    metadata JSONB
);

-- Insert default content filtering rules
INSERT INTO content_filter_rules (rule_type, rule_value, description) VALUES
('forbidden_words', 'blasphemy,goddamn,jesus christ,christ almighty', 'Blasphemous language'),
('forbidden_words', 'allah,mohammed,buddha,krishna,hindu,muslim,islam,buddhist', 'Other religious references as business principles'),
('forbidden_words', 'denial of jesus,jesus myth,fictional jesus', 'Jesus denial content'),
('required_themes', 'christian leadership,faith-based,biblical principles,christian worldview', 'Required Christian themes'),
('author_blacklist', 'richard dawkins,christopher hitchens,sam harris', 'Known anti-Christian authors');

-- Create indexes for performance
CREATE INDEX idx_pending_books_status ON pending_books(status);
CREATE INDEX idx_pending_books_submitted_at ON pending_books(submitted_at);
CREATE INDEX idx_approval_sessions_date ON approval_sessions(session_date);
CREATE INDEX idx_approval_sessions_status ON approval_sessions(status);
CREATE INDEX idx_content_calendar_week ON content_calendar(year, week_number);
CREATE INDEX idx_author_stats_name ON author_stats(author_name);
CREATE INDEX idx_audit_log_book_id ON approval_audit_log(book_id);

-- Create a view for the admin dashboard
CREATE OR REPLACE VIEW admin_dashboard_summary AS
SELECT 
    -- Current session info
    (SELECT COUNT(*) FROM approval_sessions WHERE status = 'pending') as pending_sessions,
    (SELECT COUNT(*) FROM approval_sessions WHERE status = 'in_progress') as active_sessions,
    
    -- Books awaiting approval
    (SELECT COUNT(*) FROM pending_books WHERE status = 'pending') as books_pending,
    (SELECT COUNT(*) FROM pending_books WHERE status = 'needs_review') as books_needs_review,
    (SELECT COUNT(*) FROM pending_books WHERE status = 'approved' AND scheduled_post_date IS NULL) as books_approved_unscheduled,
    
    -- Content filter stats
    (SELECT COUNT(*) FROM pending_books WHERE passes_content_filter = FALSE) as books_filtered_out,
    
    -- Weekly calendar status
    (SELECT COUNT(*) FROM content_calendar WHERE status = 'planning') as weeks_in_planning,
    (SELECT COUNT(*) FROM content_calendar WHERE status = 'approved') as weeks_approved,
    
    -- Author diversity
    (SELECT COUNT(DISTINCT author) FROM books_accessories) as unique_authors_published,
    (SELECT COUNT(DISTINCT author) FROM pending_books WHERE status = 'approved') as unique_authors_approved;

-- Function to create a new approval session
CREATE OR REPLACE FUNCTION create_approval_session(admin_email_param TEXT)
RETURNS TABLE(session_id INTEGER, access_token TEXT) AS $$
DECLARE
    new_session_id INTEGER;
    new_access_token TEXT;
    session_date DATE := CURRENT_DATE;
BEGIN
    -- Generate a secure access token
    new_access_token := encode(digest(admin_email_param || session_date::TEXT || extract(epoch from now())::TEXT, 'sha256'), 'hex');
    
    -- Insert new session (or update if exists for today)
    INSERT INTO approval_sessions (session_date, admin_email, access_token, status)
    VALUES (session_date, admin_email_param, new_access_token, 'pending')
    ON CONFLICT (session_date) 
    DO UPDATE SET 
        access_token = EXCLUDED.access_token,
        status = 'pending',
        expires_at = CURRENT_TIMESTAMP + INTERVAL '7 days'
    RETURNING id INTO new_session_id;
    
    RETURN QUERY SELECT new_session_id, new_access_token;
END;
$$ LANGUAGE plpgsql;

-- Function to approve/reject a book
CREATE OR REPLACE FUNCTION approve_reject_book(
    book_id_param INTEGER,
    session_token TEXT,
    action_param TEXT,
    admin_notes_param TEXT DEFAULT NULL,
    rejection_reason_param TEXT DEFAULT NULL
)
RETURNS BOOLEAN AS $$
DECLARE
    session_record approval_sessions%ROWTYPE;
    book_record pending_books%ROWTYPE;
BEGIN
    -- Validate session
    SELECT * INTO session_record 
    FROM approval_sessions 
    WHERE access_token = session_token 
    AND status IN ('pending', 'in_progress')
    AND expires_at > CURRENT_TIMESTAMP;
    
    IF NOT FOUND THEN
        RETURN FALSE;
    END IF;
    
    -- Update session status to in_progress if pending
    IF session_record.status = 'pending' THEN
        UPDATE approval_sessions 
        SET status = 'in_progress', started_at = CURRENT_TIMESTAMP
        WHERE id = session_record.id;
    END IF;
    
    -- Get book record
    SELECT * INTO book_record FROM pending_books WHERE id = book_id_param;
    IF NOT FOUND THEN
        RETURN FALSE;
    END IF;
    
    -- Update book status
    UPDATE pending_books SET
        status = action_param,
        reviewed_by = session_record.admin_email,
        reviewed_at = CURRENT_TIMESTAMP,
        admin_notes = admin_notes_param,
        rejection_reason = CASE WHEN action_param = 'rejected' THEN rejection_reason_param ELSE NULL END
    WHERE id = book_id_param;
    
    -- Update session stats
    UPDATE approval_sessions SET
        books_reviewed = books_reviewed + 1,
        books_approved = books_approved + CASE WHEN action_param = 'approved' THEN 1 ELSE 0 END,
        books_rejected = books_rejected + CASE WHEN action_param = 'rejected' THEN 1 ELSE 0 END,
        last_accessed = CURRENT_TIMESTAMP
    WHERE id = session_record.id;
    
    -- Log the action
    INSERT INTO approval_audit_log (book_id, session_id, action, performed_by, old_status, new_status, notes)
    VALUES (book_id_param, session_record.id, action_param, session_record.admin_email, book_record.status, action_param, admin_notes_param);
    
    RETURN TRUE;
END;
$$ LANGUAGE plpgsql; 