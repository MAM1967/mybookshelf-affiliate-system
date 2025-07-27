#!/usr/bin/env python3
"""
Create Price Validation Queue Table via REST SQL
Uses Supabase REST API to execute SQL directly
"""

import os
import sys
import requests
import json

# Supabase configuration
SUPABASE_URL = "https://ackcgrnizuhauccnbiml.supabase.co"
SUPABASE_ANON_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImFja2Nncm5penVoYXVjY25iaW1sIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTEyMjc4MzEsImV4cCI6MjA2NjgwMzgzMX0.SXpIMuNBgUhcEQUHzpEB1zZAdF-UTGvmY81EFUtsAwc"

def execute_sql_via_rest(sql):
    """Execute SQL via Supabase REST API"""
    
    headers = {
        'apikey': SUPABASE_ANON_KEY,
        'Authorization': f'Bearer {SUPABASE_ANON_KEY}',
        'Content-Type': 'application/json',
        'Prefer': 'return=minimal'
    }
    
    # Try to execute SQL via REST API
    try:
        # First, let's try the rpc endpoint
        response = requests.post(
            f"{SUPABASE_URL}/rest/v1/rpc/exec_sql",
            headers=headers,
            json={"sql": sql}
        )
        
        if response.status_code == 200:
            print("✅ SQL executed successfully via RPC")
            return True
        else:
            print(f"❌ RPC execution failed: {response.status_code} - {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error executing SQL via RPC: {e}")
        return False

def create_table_step_by_step():
    """Create the table step by step using REST API"""
    
    print("🚀 Creating Price Validation Queue Table Step by Step...")
    
    # Step 1: Create the main table
    print("\n1. Creating price_validation_queue table...")
    create_table_sql = """
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
    
    if execute_sql_via_rest(create_table_sql):
        print("✅ Table created successfully")
    else:
        print("❌ Failed to create table")
        return False
    
    # Step 2: Add indexes
    print("\n2. Adding indexes...")
    indexes_sql = """
    CREATE INDEX IF NOT EXISTS idx_price_validation_queue_status ON price_validation_queue(status);
    CREATE INDEX IF NOT EXISTS idx_price_validation_queue_item_id ON price_validation_queue(item_id);
    CREATE INDEX IF NOT EXISTS idx_price_validation_queue_flagged_at ON price_validation_queue(flagged_at);
    CREATE INDEX IF NOT EXISTS idx_price_validation_queue_percentage_change ON price_validation_queue(percentage_change);
    """
    
    if execute_sql_via_rest(indexes_sql):
        print("✅ Indexes created successfully")
    else:
        print("❌ Failed to create indexes")
        return False
    
    # Step 3: Add validation columns to books_accessories
    print("\n3. Adding validation columns to books_accessories...")
    columns_sql = """
    ALTER TABLE books_accessories ADD COLUMN IF NOT EXISTS last_validation_status TEXT;
    ALTER TABLE books_accessories ADD COLUMN IF NOT EXISTS validation_notes TEXT;
    ALTER TABLE books_accessories ADD COLUMN IF NOT EXISTS requires_approval BOOLEAN DEFAULT FALSE;
    """
    
    if execute_sql_via_rest(columns_sql):
        print("✅ Validation columns added successfully")
    else:
        print("❌ Failed to add validation columns")
        return False
    
    # Step 4: Create index for requires_approval
    print("\n4. Creating index for requires_approval...")
    index_sql = """
    CREATE INDEX IF NOT EXISTS idx_books_accessories_requires_approval ON books_accessories(requires_approval);
    """
    
    if execute_sql_via_rest(index_sql):
        print("✅ Index created successfully")
    else:
        print("❌ Failed to create index")
        return False
    
    # Step 5: Grant permissions
    print("\n5. Granting permissions...")
    permissions_sql = """
    GRANT SELECT, INSERT, UPDATE, DELETE ON price_validation_queue TO anon;
    GRANT UPDATE ON books_accessories TO anon;
    """
    
    if execute_sql_via_rest(permissions_sql):
        print("✅ Permissions granted successfully")
    else:
        print("❌ Failed to grant permissions")
        return False
    
    return True

def test_table_creation():
    """Test if the table was created successfully"""
    
    print("\n🧪 Testing table creation...")
    
    try:
        # Connect to Supabase
        from supabase import create_client, Client
        supabase: Client = create_client(SUPABASE_URL, SUPABASE_ANON_KEY)
        
        # Test 1: Check if table exists
        try:
            result = supabase.table('price_validation_queue').select('*').limit(1).execute()
            print("✅ Price validation queue table exists and is accessible")
            table_exists = True
        except Exception as e:
            print(f"❌ Price validation queue table error: {e}")
            table_exists = False
        
        # Test 2: Check if validation columns exist
        try:
            result = supabase.table('books_accessories').select('id, last_validation_status, validation_notes, requires_approval').limit(1).execute()
            print("✅ Validation columns exist in books_accessories table")
            columns_exist = True
        except Exception as e:
            print(f"❌ Validation columns error: {e}")
            columns_exist = False
        
        # Test 3: Test API endpoint
        try:
            response = requests.get("https://mybookshelf.shop/api/price-approvals")
            if response.status_code == 200:
                data = response.json()
                print("✅ API endpoint working correctly")
                print(f"   Statistics: {data.get('statistics', {})}")
                api_working = True
            else:
                print(f"❌ API endpoint error: {response.status_code} - {response.text}")
                api_working = False
        except Exception as e:
            print(f"❌ API endpoint error: {e}")
            api_working = False
        
        return table_exists and columns_exist and api_working
        
    except Exception as e:
        print(f"❌ Error testing table creation: {e}")
        return False

def main():
    """Main function"""
    
    print("🚀 PRICE VALIDATION QUEUE TABLE CREATION")
    print("=" * 60)
    
    # Try to create the table via REST API
    success = create_table_step_by_step()
    
    if success:
        print("\n✅ Table creation completed!")
        
        # Test the creation
        if test_table_creation():
            print("\n🎉 SYSTEM FULLY OPERATIONAL!")
            print("The anomalous price approval interface is now complete.")
            print("Visit https://www.mybookshelf.shop/admin and click the '🚨 Price Approvals' tab.")
        else:
            print("\n❌ Table creation may have failed. Please check manually.")
    else:
        print("\n❌ Table creation failed. Manual setup required.")
        print("Please execute the SQL manually in the Supabase dashboard.")

if __name__ == "__main__":
    main() 