#!/usr/bin/env python3
"""
Apply Price Schema Changes Directly
Uses Supabase client to check schema and generate manual SQL
"""

import os
import sys
import logging
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Set up environment
os.environ.setdefault('SUPABASE_URL', 'https://ackcgrnizuhauccnbiml.supabase.co')
os.environ.setdefault('SUPABASE_ANON_KEY', 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImFja2Nncm5penVoYXVjY25iaW1sIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTEyMjc4MzEsImV4cCI6MjA2NjgwMzgzMX0.SXpIMuNBgUhcEQUHzpEB1zZAdF-UTGvmY81EFUtsAwc')

class DirectSchemaUpdater:
    """Apply schema changes using Supabase client"""
    
    def __init__(self):
        """Initialize database connection"""
        try:
            from supabase import create_client, Client
            self.supabase: Client = create_client(
                os.environ['SUPABASE_URL'],
                os.environ['SUPABASE_ANON_KEY']
            )
            logger.info("✅ Connected to Supabase")
        except Exception as e:
            logger.error(f"❌ Failed to connect to Supabase: {e}")
            sys.exit(1)
    
    def use_supabase_api_approach(self) -> bool:
        """Try using Supabase REST API to modify schema"""
        logger.info("🔧 Attempting Supabase API approach...")
        
        try:
            # Method: Try updating a record with new columns
            logger.info("   Trying to update with new columns...")
            
            # Get a sample record
            response = self.supabase.table('books_accessories').select('*').limit(1).execute()
            if not response.data:
                logger.error("   ❌ No sample data found")
                return False
            
            sample_record = response.data[0]
            sample_id = sample_record['id']
            
            logger.info(f"   Updating record {sample_id} with new price_status field...")
            
            # Try updating with new fields - this might auto-create columns in some systems
            update_data = {
                'price_status': 'active',
                'price_source': 'manual',
                'price_fetch_attempts': 0
            }
            
            update_response = self.supabase.table('books_accessories').update(update_data).eq('id', sample_id).execute()
            
            if update_response.data:
                logger.info("   ✅ Update successful - columns may have been auto-created")
                return True
            else:
                logger.warning("   ⚠️ Update failed - columns don't exist")
                return False
                
        except Exception as e:
            logger.error(f"   ❌ API approach failed: {e}")
            return False
    
    def verify_schema_changes(self) -> dict:
        """Verify that schema changes were applied"""
        logger.info("🔍 Verifying schema changes...")
        
        results = {
            'columns_added': [],
            'columns_missing': [],
            'price_history_exists': False,
            'overall_success': False
        }
        
        # Check columns
        expected_columns = ['price_status', 'last_price_check', 'price_updated_at', 'price_source', 'price_fetch_attempts']
        
        for column in expected_columns:
            try:
                response = self.supabase.table('books_accessories').select(column).limit(1).execute()
                results['columns_added'].append(column)
                logger.info(f"   ✅ Column exists: {column}")
            except Exception:
                results['columns_missing'].append(column)
                logger.warning(f"   ❌ Column missing: {column}")
        
        # Check price_history table
        try:
            response = self.supabase.table('price_history').select('id').limit(1).execute()
            results['price_history_exists'] = True
            logger.info("   ✅ price_history table exists")
        except Exception:
            results['price_history_exists'] = False
            logger.warning("   ❌ price_history table missing")
        
        results['overall_success'] = (
            len(results['columns_missing']) == 0 and 
            results['price_history_exists']
        )
        
        return results
    
    def generate_manual_sql(self) -> str:
        """Generate the SQL commands that need to be run manually"""
        sql_commands = """-- MANUAL SQL COMMANDS TO RUN IN SUPABASE DASHBOARD
-- Copy and paste each section into the SQL Editor

-- 1. Add price tracking columns
ALTER TABLE books_accessories ADD COLUMN IF NOT EXISTS price_status TEXT DEFAULT 'active';
ALTER TABLE books_accessories ADD COLUMN IF NOT EXISTS last_price_check TIMESTAMP;
ALTER TABLE books_accessories ADD COLUMN IF NOT EXISTS price_updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP;
ALTER TABLE books_accessories ADD COLUMN IF NOT EXISTS price_source TEXT DEFAULT 'manual';
ALTER TABLE books_accessories ADD COLUMN IF NOT EXISTS price_fetch_attempts INTEGER DEFAULT 0;

-- 2. Create price_history table
CREATE TABLE IF NOT EXISTS price_history (
    id SERIAL PRIMARY KEY,
    book_id INTEGER NOT NULL REFERENCES books_accessories(id) ON DELETE CASCADE,
    old_price NUMERIC,
    new_price NUMERIC,
    price_change NUMERIC,
    price_change_percent NUMERIC,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    update_source TEXT DEFAULT 'automated',
    notes TEXT
);

-- 3. Add indexes
CREATE INDEX IF NOT EXISTS idx_price_history_book_id ON price_history(book_id);
CREATE INDEX IF NOT EXISTS idx_price_history_updated_at ON price_history(updated_at);

-- 4. Initialize existing records
UPDATE books_accessories 
SET 
    price_status = CASE 
        WHEN price IS NULL OR price = 0 THEN 'out_of_stock'
        ELSE 'active'
    END,
    price_updated_at = COALESCE(timestamp, CURRENT_TIMESTAMP),
    last_price_check = COALESCE(timestamp, CURRENT_TIMESTAMP),
    price_source = 'manual',
    price_fetch_attempts = 0
WHERE price_status IS NULL;

-- 5. Verify changes
SELECT column_name FROM information_schema.columns 
WHERE table_name = 'books_accessories' 
  AND column_name IN ('price_status', 'last_price_check', 'price_updated_at', 'price_source', 'price_fetch_attempts');
"""
        return sql_commands

def main():
    """Main execution function"""
    logger.info("🚀 Starting Direct Schema Update")
    logger.info("=" * 60)
    
    updater = DirectSchemaUpdater()
    
    try:
        # Try API approach first
        api_success = updater.use_supabase_api_approach()
        
        if api_success:
            logger.info("✅ API approach worked!")
        else:
            logger.warning("⚠️ API approach failed, checking current state...")
        
        # Check current schema state
        verification_results = updater.verify_schema_changes()
        
        if verification_results['overall_success']:
            logger.info("🎉 ALL SCHEMA CHANGES SUCCESSFUL!")
            logger.info("✅ Ready for Phase 2 (Daily Price Updates)")
        else:
            logger.warning("⚠️ Schema changes incomplete")
            logger.info("📋 Generating manual SQL commands...")
            
            # Save manual SQL to file
            manual_sql = updater.generate_manual_sql()
            sql_filename = f"manual_schema_commands_{datetime.now().strftime('%Y%m%d_%H%M%S')}.sql"
            
            with open(sql_filename, 'w') as f:
                f.write(manual_sql)
            
            logger.info(f"📄 Manual SQL saved to: {sql_filename}")
            logger.info("📖 Copy and paste these commands in Supabase SQL Editor:")
            logger.info("   1. Go to your Supabase Dashboard")
            logger.info("   2. Click on 'SQL Editor'") 
            logger.info(f"   3. Copy the contents of {sql_filename}")
            logger.info("   4. Paste and run each section")
            
            # Show what's missing
            if verification_results['columns_missing']:
                logger.info(f"❌ Missing columns: {', '.join(verification_results['columns_missing'])}")
            if not verification_results['price_history_exists']:
                logger.info("❌ Missing price_history table")
        
        logger.info("=" * 60)
        
    except Exception as e:
        logger.error(f"❌ Schema update failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main() 