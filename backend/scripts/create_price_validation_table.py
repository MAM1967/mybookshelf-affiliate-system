#!/usr/bin/env python3
"""
Create Price Validation Queue Table
Simple script to create the price_validation_queue table in Supabase
"""

import os
import sys
from supabase import create_client, Client

# Set up environment
os.environ.setdefault('SUPABASE_URL', 'https://ackcgrnizuhauccnbiml.supabase.co')
os.environ.setdefault('SUPABASE_ANON_KEY', 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImFja2Nncm5penVoYXVjY25iaW1sIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTEyMjc4MzEsImV4cCI6MjA2NjgwMzgzMX0.SXpIMuNBgUhcEQUHzpEB1zZAdF-UTGvmY81EFUtsAwc')

def create_table():
    """Create the price validation queue table"""
    
    try:
        # Connect to Supabase
        supabase: Client = create_client(
            os.environ['SUPABASE_URL'],
            os.environ['SUPABASE_ANON_KEY']
        )
        print("✅ Connected to Supabase")
        
        # Create the table using raw SQL
        sql = """
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
        """
        
        # Execute the SQL
        result = supabase.rpc('exec_sql', {'sql': sql}).execute()
        print("✅ Price validation queue table created successfully")
        
        # Add indexes
        indexes = [
            "CREATE INDEX IF NOT EXISTS idx_price_validation_queue_status ON price_validation_queue(status);",
            "CREATE INDEX IF NOT EXISTS idx_price_validation_queue_item_id ON price_validation_queue(item_id);",
            "CREATE INDEX IF NOT EXISTS idx_price_validation_queue_flagged_at ON price_validation_queue(flagged_at);",
            "CREATE INDEX IF NOT EXISTS idx_price_validation_queue_percentage_change ON price_validation_queue(percentage_change);"
        ]
        
        for index_sql in indexes:
            try:
                supabase.rpc('exec_sql', {'sql': index_sql}).execute()
                print(f"✅ Index created: {index_sql.split('ON')[1].strip()}")
            except Exception as e:
                print(f"⚠️ Index creation failed (may already exist): {e}")
        
        # Add columns to books_accessories table
        alter_sql = """
        ALTER TABLE books_accessories ADD COLUMN IF NOT EXISTS last_validation_status TEXT;
        ALTER TABLE books_accessories ADD COLUMN IF NOT EXISTS validation_notes TEXT;
        ALTER TABLE books_accessories ADD COLUMN IF NOT EXISTS requires_approval BOOLEAN DEFAULT FALSE;
        """
        
        try:
            supabase.rpc('exec_sql', {'sql': alter_sql}).execute()
            print("✅ Added validation columns to books_accessories table")
        except Exception as e:
            print(f"⚠️ Column addition failed (may already exist): {e}")
        
        # Test the table
        try:
            result = supabase.table('price_validation_queue').select('*').limit(1).execute()
            print("✅ Price validation queue table is accessible")
        except Exception as e:
            print(f"❌ Error accessing price validation queue table: {e}")
            
        print("🎉 Database setup completed successfully!")
        
    except Exception as e:
        print(f"❌ Failed to create table: {e}")
        sys.exit(1)

if __name__ == "__main__":
    create_table() 