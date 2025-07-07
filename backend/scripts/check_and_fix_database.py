#!/usr/bin/env python3
"""
Check and Fix Database Schema
Checks the current database schema and adds missing columns for the scraped data
"""

import os
import sys
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def check_database_schema():
    """Check the current database schema and add missing columns"""
    supabase_url = os.getenv('SUPABASE_URL')
    supabase_key = os.getenv('SUPABASE_ANON_KEY')
    
    if not all([supabase_url, supabase_key]):
        logger.error("❌ Supabase credentials not found in environment variables")
        logger.error("Please set: SUPABASE_URL, SUPABASE_ANON_KEY")
        sys.exit(1)
    
    try:
        from supabase.client import create_client, Client
        supabase: Client = create_client(supabase_url, supabase_key)
        logger.info("✅ Supabase client initialized")
    except Exception as e:
        logger.error(f"❌ Failed to initialize Supabase client: {e}")
        sys.exit(1)
    
    # Check if books_accessories table exists
    try:
        response = supabase.table('books_accessories').select('*').limit(1).execute()
        logger.info("✅ books_accessories table exists")
    except Exception as e:
        logger.error(f"❌ books_accessories table does not exist: {e}")
        logger.info("Creating table...")
        create_table_sql = """
        CREATE TABLE books_accessories (
            id SERIAL PRIMARY KEY,
            title TEXT NOT NULL,
            author TEXT NOT NULL,
            price NUMERIC,
            affiliate_link TEXT,
            image_url TEXT,
            category TEXT NOT NULL,
            asin TEXT,
            rating NUMERIC,
            review_count INTEGER,
            description TEXT,
            focus_area TEXT,
            christian_themes TEXT[],
            leadership_topics TEXT[],
            is_active BOOLEAN DEFAULT TRUE,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """
        try:
            # Execute raw SQL to create table
            supabase.rpc('exec_sql', {'sql': create_table_sql}).execute()
            logger.info("✅ Created books_accessories table")
        except Exception as create_error:
            logger.error(f"❌ Failed to create table: {create_error}")
            logger.info("Please create the table manually in Supabase dashboard")
            return
    
    # Check existing columns
    try:
        response = supabase.table('books_accessories').select('*').limit(1).execute()
        if response.data:
            sample_row = response.data[0]
            existing_columns = list(sample_row.keys())
            logger.info(f"📋 Existing columns: {existing_columns}")
            
            # Check for missing columns
            required_columns = [
                'asin', 'rating', 'review_count', 'description', 
                'focus_area', 'christian_themes', 'leadership_topics', 
                'is_active', 'created_at'
            ]
            
            missing_columns = []
            for col in required_columns:
                if col not in existing_columns:
                    missing_columns.append(col)
            
            if missing_columns:
                logger.warning(f"⚠️  Missing columns: {missing_columns}")
                logger.info("Adding missing columns...")
                
                for col in missing_columns:
                    try:
                        if col == 'asin':
                            sql = "ALTER TABLE books_accessories ADD COLUMN asin TEXT;"
                        elif col == 'rating':
                            sql = "ALTER TABLE books_accessories ADD COLUMN rating NUMERIC;"
                        elif col == 'review_count':
                            sql = "ALTER TABLE books_accessories ADD COLUMN review_count INTEGER;"
                        elif col == 'description':
                            sql = "ALTER TABLE books_accessories ADD COLUMN description TEXT;"
                        elif col == 'focus_area':
                            sql = "ALTER TABLE books_accessories ADD COLUMN focus_area TEXT;"
                        elif col == 'christian_themes':
                            sql = "ALTER TABLE books_accessories ADD COLUMN christian_themes TEXT[];"
                        elif col == 'leadership_topics':
                            sql = "ALTER TABLE books_accessories ADD COLUMN leadership_topics TEXT[];"
                        elif col == 'is_active':
                            sql = "ALTER TABLE books_accessories ADD COLUMN is_active BOOLEAN DEFAULT TRUE;"
                        elif col == 'created_at':
                            sql = "ALTER TABLE books_accessories ADD COLUMN created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP;"
                        
                        supabase.rpc('exec_sql', {'sql': sql}).execute()
                        logger.info(f"✅ Added column: {col}")
                        
                    except Exception as col_error:
                        logger.warning(f"⚠️  Could not add column {col}: {col_error}")
                        logger.info("You may need to add this column manually in Supabase dashboard")
            else:
                logger.info("✅ All required columns exist")
                
        else:
            logger.info("📋 Table exists but is empty")
            
    except Exception as e:
        logger.error(f"❌ Error checking schema: {e}")

def main():
    """Main execution function"""
    print("🔍 Checking Database Schema")
    print("=" * 40)
    
    check_database_schema()
    
    print(f"\n✅ Schema check complete!")
    print(f"Next steps:")
    print(f"1. Run the insertion script again")
    print(f"2. Verify items in your Supabase dashboard")

if __name__ == "__main__":
    main() 