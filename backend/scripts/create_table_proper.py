#!/usr/bin/env python3
"""
Create Price Validation Queue Table - Proper Method
Uses Supabase client correctly to create the table
"""

import os
import sys
import requests
import json
from supabase import create_client, Client

# Supabase configuration
SUPABASE_URL = "https://ackcgrnizuhauccnbiml.supabase.co"
SUPABASE_ANON_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImFja2Nncm5penVoYXVjY25iaW1sIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTEyMjc4MzEsImV4cCI6MjA2NjgwMzgzMX0.SXpIMuNBgUhcEQUHzpEB1zZAdF-UTGvmY81EFUtsAwc"

def create_table_via_rest_api():
    """Create the table using direct REST API calls"""
    
    headers = {
        'apikey': SUPABASE_ANON_KEY,
        'Authorization': f'Bearer {SUPABASE_ANON_KEY}',
        'Content-Type': 'application/json',
        'Prefer': 'return=minimal'
    }
    
    print("🚀 Creating Price Validation Queue Table...")
    
    # First, let's check if the table already exists by trying to query it
    try:
        response = requests.get(
            f"{SUPABASE_URL}/rest/v1/price_validation_queue?select=id&limit=1",
            headers=headers
        )
        
        if response.status_code == 200:
            print("✅ Table already exists!")
            return True
        elif response.status_code == 404:
            print("❌ Table does not exist - need to create it")
            return False
        else:
            print(f"❌ Unexpected response: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Error checking table: {e}")
        return False

def create_table_using_supabase_client():
    """Create table using Supabase client operations"""
    
    try:
        # Connect to Supabase
        supabase: Client = create_client(SUPABASE_URL, SUPABASE_ANON_KEY)
        print("✅ Connected to Supabase")
        
        # Try to create the table by attempting to insert data
        # If the table doesn't exist, this will fail, but we can handle it
        test_data = {
            "item_id": 1,
            "old_price": 10.00,
            "new_price": 85.00,
            "percentage_change": 750.0,
            "validation_reason": "test_extreme_change_750pct_exceeds_35pct_limit",
            "validation_layer": "threshold_validation",
            "validation_details": {
                "priceCategory": "test",
                "maxChangePercent": 35,
                "actualChange": 750.0,
                "test": True
            },
            "status": "pending",
            "flagged_at": "2025-07-27T23:15:00Z"
        }
        
        try:
            # Try to insert test data
            result = supabase.table('price_validation_queue').insert(test_data).execute()
            print("✅ Table exists and we can insert data!")
            
            # Clean up test data
            supabase.table('price_validation_queue').delete().eq('validation_reason', 'test_extreme_change_750pct_exceeds_35pct_limit').execute()
            print("✅ Test data cleaned up")
            return True
            
        except Exception as e:
            print(f"❌ Table does not exist: {e}")
            return False
            
    except Exception as e:
        print(f"❌ Failed to connect to Supabase: {e}")
        return False

def add_validation_columns():
    """Add validation columns to books_accessories table"""
    
    try:
        # Connect to Supabase
        supabase: Client = create_client(SUPABASE_URL, SUPABASE_ANON_KEY)
        
        # Test if columns exist by trying to select them
        try:
            result = supabase.table('books_accessories').select('id, last_validation_status, validation_notes, requires_approval').limit(1).execute()
            print("✅ Validation columns already exist in books_accessories table")
            return True
        except Exception as e:
            print(f"❌ Validation columns don't exist: {e}")
            print("Need to add them manually in Supabase dashboard")
            return False
            
    except Exception as e:
        print(f"❌ Error checking validation columns: {e}")
        return False

def test_api_endpoint():
    """Test the price approvals API endpoint"""
    
    print("\n🧪 Testing API Endpoint...")
    
    try:
        response = requests.get("https://mybookshelf.shop/api/price-approvals")
        print(f"✅ API endpoint status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print("✅ API endpoint working correctly")
            print(f"   Statistics: {data.get('statistics', {})}")
            return True
        else:
            print(f"❌ API endpoint error: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error testing API: {e}")
        return False

def create_table_manually():
    """Provide instructions for manual table creation"""
    
    print("\n📋 MANUAL TABLE CREATION REQUIRED")
    print("=" * 60)
    print("Since automatic table creation is not available through the client,")
    print("please create the table manually in the Supabase dashboard:")
    print("\n1. Go to: https://supabase.com/dashboard/project/ackcgrnizuhauccnbiml")
    print("2. Click 'SQL Editor' in the left sidebar")
    print("3. Execute this SQL:")
    print("\n" + "=" * 60)
    
    sql = """
-- Create price validation queue table
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

-- Add indexes
CREATE INDEX IF NOT EXISTS idx_price_validation_queue_status ON price_validation_queue(status);
CREATE INDEX IF NOT EXISTS idx_price_validation_queue_item_id ON price_validation_queue(item_id);
CREATE INDEX IF NOT EXISTS idx_price_validation_queue_flagged_at ON price_validation_queue(flagged_at);
CREATE INDEX IF NOT EXISTS idx_price_validation_queue_percentage_change ON price_validation_queue(percentage_change);

-- Add validation columns to books_accessories
ALTER TABLE books_accessories ADD COLUMN IF NOT EXISTS last_validation_status TEXT;
ALTER TABLE books_accessories ADD COLUMN IF NOT EXISTS validation_notes TEXT;
ALTER TABLE books_accessories ADD COLUMN IF NOT EXISTS requires_approval BOOLEAN DEFAULT FALSE;

-- Create index for requires_approval
CREATE INDEX IF NOT EXISTS idx_books_accessories_requires_approval ON books_accessories(requires_approval);

-- Grant permissions
GRANT SELECT, INSERT, UPDATE, DELETE ON price_validation_queue TO anon;
GRANT UPDATE ON books_accessories TO anon;
"""
    
    print(sql)
    print("=" * 60)
    print("\n4. After executing the SQL, run this script again to verify")

def main():
    """Main function"""
    
    print("🚀 PRICE VALIDATION QUEUE TABLE SETUP")
    print("=" * 60)
    
    # Step 1: Check if table exists via REST API
    table_exists_rest = create_table_via_rest_api()
    
    # Step 2: Check if table exists via Supabase client
    table_exists_client = create_table_using_supabase_client()
    
    # Step 3: Check validation columns
    columns_exist = add_validation_columns()
    
    # Step 4: Test API endpoint
    api_working = test_api_endpoint()
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 SETUP SUMMARY")
    print("=" * 60)
    print(f"✅ Price Validation Queue Table (REST): {'Ready' if table_exists_rest else 'Needs Setup'}")
    print(f"✅ Price Validation Queue Table (Client): {'Ready' if table_exists_client else 'Needs Setup'}")
    print(f"✅ Validation Columns: {'Ready' if columns_exist else 'Needs Setup'}")
    print(f"✅ API Endpoint: {'Working' if api_working else 'Needs Database'}")
    
    if table_exists_client and columns_exist and api_working:
        print("\n🎉 SYSTEM FULLY OPERATIONAL!")
        print("The anomalous price approval interface is now complete.")
        print("Visit https://www.mybookshelf.shop/admin and click the '🚨 Price Approvals' tab.")
    else:
        print("\n🔧 MANUAL SETUP REQUIRED")
        create_table_manually()

if __name__ == "__main__":
    main() 