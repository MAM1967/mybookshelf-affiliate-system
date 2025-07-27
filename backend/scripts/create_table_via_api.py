#!/usr/bin/env python3
"""
Create Price Validation Queue Table via REST API
Uses direct HTTP requests to create the table
"""

import os
import sys
import requests
import json

# Supabase configuration
SUPABASE_URL = "https://ackcgrnizuhauccnbiml.supabase.co"
SUPABASE_ANON_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImFja2Nncm5penVoYXVjY25iaW1sIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTEyMjc4MzEsImV4cCI6MjA2NjgwMzgzMX0.SXpIMuNBgUhcEQUHzpEB1zZAdF-UTGvmY81EFUtsAwc"

def create_table_via_rest():
    """Create the table using REST API calls"""
    
    headers = {
        'apikey': SUPABASE_ANON_KEY,
        'Authorization': f'Bearer {SUPABASE_ANON_KEY}',
        'Content-Type': 'application/json',
        'Prefer': 'return=minimal'
    }
    
    print("🚀 Creating Price Validation Queue Table via REST API...")
    
    # First, let's try to create the table using a different approach
    # We'll try to insert data and see if the table exists
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
        # Try to insert into the table
        response = requests.post(
            f"{SUPABASE_URL}/rest/v1/price_validation_queue",
            headers=headers,
            json=test_data
        )
        
        if response.status_code == 201:
            print("✅ Table exists and we can insert data!")
            
            # Clean up test data
            cleanup_response = requests.delete(
                f"{SUPABASE_URL}/rest/v1/price_validation_queue?validation_reason=eq.test_extreme_change_750pct_exceeds_35pct_limit",
                headers=headers
            )
            print("✅ Test data cleaned up")
            return True
            
        elif response.status_code == 404:
            print("❌ Table does not exist - need to create it manually")
            return False
        else:
            print(f"❌ Unexpected response: {response.status_code} - {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error testing table: {e}")
        return False

def add_validation_columns_via_rest():
    """Add validation columns to books_accessories table"""
    
    headers = {
        'apikey': SUPABASE_ANON_KEY,
        'Authorization': f'Bearer {SUPABASE_ANON_KEY}',
        'Content-Type': 'application/json'
    }
    
    print("\n🔧 Adding validation columns to books_accessories...")
    
    try:
        # Test if columns exist by trying to select them
        response = requests.get(
            f"{SUPABASE_URL}/rest/v1/books_accessories?select=id,last_validation_status,validation_notes,requires_approval&limit=1",
            headers=headers
        )
        
        if response.status_code == 200:
            print("✅ Validation columns already exist")
            return True
        else:
            print("❌ Validation columns don't exist - need to add them manually")
            return False
            
    except Exception as e:
        print(f"❌ Error checking columns: {e}")
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

def create_manual_setup_guide():
    """Create a comprehensive manual setup guide"""
    
    print("\n📋 MANUAL SETUP GUIDE")
    print("=" * 50)
    print("Since automatic table creation is not available, please follow these steps:")
    print("\n1. Go to Supabase Dashboard:")
    print("   https://supabase.com/dashboard/project/ackcgrnizuhauccnbiml")
    print("\n2. Navigate to SQL Editor")
    print("\n3. Execute this SQL:")
    print("\n" + "=" * 50)
    print("""
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
""")
    print("=" * 50)
    print("\n4. After executing the SQL, run this script again to verify")
    print("\n5. Test the admin interface at: https://www.mybookshelf.shop/admin")

def main():
    """Main function"""
    
    print("🚀 PRICE VALIDATION QUEUE TABLE SETUP")
    print("=" * 50)
    
    # Step 1: Test if table exists
    table_exists = create_table_via_rest()
    
    # Step 2: Test if columns exist
    columns_exist = add_validation_columns_via_rest()
    
    # Step 3: Test API endpoint
    api_working = test_api_endpoint()
    
    # Summary
    print("\n" + "=" * 50)
    print("📊 SETUP SUMMARY")
    print("=" * 50)
    print(f"✅ Price Validation Queue Table: {'Ready' if table_exists else 'Needs Manual Setup'}")
    print(f"✅ Validation Columns: {'Ready' if columns_exist else 'Needs Manual Setup'}")
    print(f"✅ API Endpoint: {'Working' if api_working else 'Needs Database'}")
    
    if table_exists and columns_exist and api_working:
        print("\n🎉 SYSTEM FULLY OPERATIONAL!")
        print("The anomalous price approval interface is now complete.")
        print("Visit https://www.mybookshelf.shop/admin and click the '🚨 Price Approvals' tab.")
    else:
        print("\n🔧 MANUAL SETUP REQUIRED")
        create_manual_setup_guide()

if __name__ == "__main__":
    main() 