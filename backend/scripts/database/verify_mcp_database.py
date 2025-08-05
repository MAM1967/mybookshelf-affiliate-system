#!/usr/bin/env python3
"""
Verify MCP Server Database Schema
Checks if required tables exist and are accessible
"""

import os
import sys
import logging
from datetime import datetime

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def verify_database_schema():
    """Verify all required tables exist for MCP server"""
    print("🔍 Verifying MCP Server Database Schema...")
    print("=" * 50)
    
    # Check environment variables
    supabase_url = os.getenv('SUPABASE_URL')
    supabase_key = os.getenv('SUPABASE_ANON_KEY')
    
    if not supabase_url or not supabase_key:
        print("❌ Missing Supabase environment variables")
        print("   Set SUPABASE_URL and SUPABASE_ANON_KEY")
        return False
    
    try:
        from supabase.client import create_client, Client
        if not supabase_url or not supabase_key:
            raise ValueError("Missing Supabase credentials")
        supabase: Client = create_client(supabase_url, supabase_key)
        print("✅ Supabase client initialized")
    except ImportError:
        print("❌ Supabase library not found. Install with: pip install supabase")
        return False
    except Exception as e:
        print(f"❌ Failed to initialize Supabase: {e}")
        return False
    
    # Required tables for MCP server
    required_tables = [
        'linkedin_tokens',
        'books_accessories',
        'pending_books',
        'approval_sessions'
    ]
    
    results = {}
    
    for table_name in required_tables:
        print(f"\n📋 Checking table: {table_name}")
        try:
            # Try to query the table
            result = supabase.table(table_name).select('count').limit(1).execute()
            if result.data is not None:
                print(f"   ✅ {table_name}: EXISTS and accessible")
                results[table_name] = True
            else:
                print(f"   ❌ {table_name}: EXISTS but not accessible")
                results[table_name] = False
        except Exception as e:
            print(f"   ❌ {table_name}: ERROR - {str(e)}")
            results[table_name] = False
    
    # Summary
    print("\n" + "=" * 50)
    print("📊 VERIFICATION SUMMARY")
    print("=" * 50)
    
    all_good = True
    for table_name, status in results.items():
        status_icon = "✅" if status else "❌"
        print(f"{status_icon} {table_name}: {'OK' if status else 'ISSUE'}")
        if not status:
            all_good = False
    
    if all_good:
        print("\n🎉 All tables verified successfully!")
        return True
    else:
        print("\n⚠️  Some tables have issues. Check the details above.")
        return False

def create_missing_tables():
    """Create missing tables if they don't exist"""
    print("\n🔧 Creating missing tables...")
    
    try:
        from supabase.client import create_client, Client
        supabase_url = os.getenv('SUPABASE_URL')
        supabase_key = os.getenv('SUPABASE_ANON_KEY')
        if not supabase_url or not supabase_key:
            raise ValueError("Missing Supabase credentials")
        supabase: Client = create_client(supabase_url, supabase_key)
    except Exception as e:
        print(f"❌ Cannot create tables: {e}")
        return False
    
    # LinkedIn tokens table schema
    linkedin_tokens_schema = """
    CREATE TABLE IF NOT EXISTS linkedin_tokens (
        id SERIAL PRIMARY KEY,
        admin_email TEXT UNIQUE NOT NULL,
        access_token TEXT NOT NULL,
        token_type TEXT DEFAULT 'Bearer',
        expires_at TIMESTAMP NOT NULL,
        scope TEXT,
        linkedin_user_id TEXT,
        linkedin_name TEXT,
        linkedin_email TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        is_active BOOLEAN DEFAULT TRUE,
        last_used_at TIMESTAMP,
        posts_count INTEGER DEFAULT 0,
        has_organization_admin BOOLEAN DEFAULT FALSE
    );
    """
    
    try:
        # Execute schema creation
        supabase.rpc('exec_sql', {'sql': linkedin_tokens_schema}).execute()
        print("✅ linkedin_tokens table created/verified")
    except Exception as e:
        print(f"⚠️  Could not create linkedin_tokens table: {e}")
        print("   You may need to create it manually in Supabase dashboard")
    
    return True

if __name__ == "__main__":
    success = verify_database_schema()
    
    if not success:
        print("\n🔧 Attempting to create missing tables...")
        create_missing_tables()
        
        print("\n🔄 Re-verifying after table creation...")
        verify_database_schema()
    
    print(f"\n📅 Verification completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}") 