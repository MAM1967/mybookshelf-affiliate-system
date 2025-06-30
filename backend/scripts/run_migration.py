#!/usr/bin/env python3
"""
Database Migration Script
Adds missing columns for LinkedIn posting tracking
"""

import os
import sys

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from supabase.client import create_client, Client
from config import Config

def run_migration():
    """Run the database migration"""
    try:
        # Initialize Supabase client
        supabase: Client = create_client(Config.SUPABASE_URL, Config.SUPABASE_ANON_KEY)
        
        print("🔄 Running database migration...")
        
        # Read the migration SQL
        with open('scripts/add_posting_columns.sql', 'r') as f:
            migration_sql = f.read()
        
        # Execute the migration
        response = supabase.rpc('exec_sql', {'sql': migration_sql}).execute()
        
        print("✅ Migration completed successfully!")
        print("Added columns:")
        print("  - posted_at (timestamp with time zone)")
        print("  - post_status (text, default 'pending')")
        print("  - post_content (text)")
        
    except Exception as e:
        print(f"❌ Migration failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    run_migration() 