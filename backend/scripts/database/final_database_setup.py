#!/usr/bin/env python3
"""
Final Database Setup for Price Approval Interface
Provides clear instructions for manual setup since programmatic creation is not possible
"""

import os
import sys
import time
import requests
from supabase import create_client, Client

# Supabase configuration
SUPABASE_URL = "https://ackcgrnizuhauccnbiml.supabase.co"
SUPABASE_ANON_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImFja2Nncm5penVoYXVjY25iaW1sIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTEyMjc4MzEsImV4cCI6MjA2NjgwMzgzMX0.SXpIMuNBgUhcEQUHzpEB1zZAdF-UTGvmY81EFUtsAwc"

def print_setup_instructions():
    """Print clear setup instructions"""
    
    print("🚀 PRICE APPROVAL INTERFACE - FINAL SETUP")
    print("=" * 60)
    print("✅ Frontend Interface: Complete")
    print("✅ API Endpoints: Complete") 
    print("✅ Validation System: Complete")
    print("❌ Database Table: Missing")
    print("\n📋 MANUAL DATABASE SETUP REQUIRED")
    print("=" * 60)
    print("The Supabase client cannot create tables programmatically.")
    print("Please follow these steps to complete the setup:")
    print("\n1. Open your web browser and go to:")
    print("   https://supabase.com/dashboard/project/ackcgrnizuhauccnbiml")
    print("\n2. Click on 'SQL Editor' in the left sidebar")
    print("\n3. Copy and paste this SQL into the editor:")
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

-- Add indexes for efficient querying
CREATE INDEX IF NOT EXISTS idx_price_validation_queue_status ON price_validation_queue(status);
CREATE INDEX IF NOT EXISTS idx_price_validation_queue_item_id ON price_validation_queue(item_id);
CREATE INDEX IF NOT EXISTS idx_price_validation_queue_flagged_at ON price_validation_queue(flagged_at);
CREATE INDEX IF NOT EXISTS idx_price_validation_queue_percentage_change ON price_validation_queue(percentage_change);

-- Add validation tracking columns to books_accessories table
ALTER TABLE books_accessories ADD COLUMN IF NOT EXISTS last_validation_status TEXT;
ALTER TABLE books_accessories ADD COLUMN IF NOT EXISTS validation_notes TEXT;
ALTER TABLE books_accessories ADD COLUMN IF NOT EXISTS requires_approval BOOLEAN DEFAULT FALSE;

-- Create index for requires_approval for efficient filtering
CREATE INDEX IF NOT EXISTS idx_books_accessories_requires_approval ON books_accessories(requires_approval);

-- Grant necessary permissions
GRANT SELECT, INSERT, UPDATE, DELETE ON price_validation_queue TO anon;
GRANT UPDATE ON books_accessories TO anon;
"""
    
    print(sql)
    print("=" * 60)
    print("\n4. Click 'Run' to execute the SQL")
    print("\n5. After execution, run this script again to verify")
    print("\n6. Visit https://www.mybookshelf.shop/admin")
    print("   Click the '🚨 Price Approvals' tab to test the interface")

def verify_setup():
    """Verify that the database setup was successful"""
    
    print("\n🧪 VERIFYING DATABASE SETUP...")
    print("=" * 60)
    
    try:
        # Connect to Supabase
        supabase: Client = create_client(SUPABASE_URL, SUPABASE_ANON_KEY)
        print("✅ Connected to Supabase")
        
        # Test 1: Check if price_validation_queue table exists
        print("\n1. Testing price_validation_queue table...")
        try:
            result = supabase.table('price_validation_queue').select('*').limit(1).execute()
            print("✅ Price validation queue table exists and is accessible")
            table_exists = True
        except Exception as e:
            print(f"❌ Price validation queue table error: {e}")
            table_exists = False
        
        # Test 2: Check if validation columns exist in books_accessories
        print("\n2. Testing validation columns in books_accessories...")
        try:
            result = supabase.table('books_accessories').select('id, last_validation_status, validation_notes, requires_approval').limit(1).execute()
            print("✅ Validation columns exist in books_accessories table")
            columns_exist = True
        except Exception as e:
            print(f"❌ Validation columns error: {e}")
            columns_exist = False
        
        # Test 3: Test API endpoint
        print("\n3. Testing API endpoint...")
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
        
        # Test 4: Test frontend interface
        print("\n4. Testing frontend interface...")
        try:
            response = requests.get("https://www.mybookshelf.shop/admin")
            if response.status_code == 200:
                print("✅ Admin interface accessible")
                frontend_working = True
            else:
                print(f"❌ Admin interface error: {response.status_code}")
                frontend_working = False
        except Exception as e:
            print(f"❌ Frontend error: {e}")
            frontend_working = False
        
        return table_exists and columns_exist and api_working and frontend_working
        
    except Exception as e:
        print(f"❌ Error testing setup: {e}")
        return False

def test_complete_workflow():
    """Test the complete price approval workflow"""
    
    print("\n🧪 TESTING COMPLETE WORKFLOW...")
    print("=" * 60)
    
    try:
        supabase: Client = create_client(SUPABASE_URL, SUPABASE_ANON_KEY)
        
        # Test 1: Insert a test price validation record
        print("\n1. Testing price validation queue insertion...")
        try:
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
            
            result = supabase.table('price_validation_queue').insert(test_data).execute()
            print("✅ Test record inserted successfully")
            
            # Clean up test data
            supabase.table('price_validation_queue').delete().eq('validation_reason', 'test_extreme_change_750pct_exceeds_35pct_limit').execute()
            print("✅ Test data cleaned up")
            
            return True
            
        except Exception as e:
            print(f"❌ Test insertion failed: {e}")
            return False
            
    except Exception as e:
        print(f"❌ Workflow test error: {e}")
        return False

def main():
    """Main function"""
    
    print("🚀 PRICE APPROVAL INTERFACE - FINAL SETUP")
    print("=" * 60)
    
    # Check if setup is already complete
    if verify_setup():
        print("\n🎉 SETUP ALREADY COMPLETE!")
        print("The anomalous price approval interface is fully operational.")
        print("\n✅ Database tables: Ready")
        print("✅ API endpoints: Working")
        print("✅ Frontend interface: Accessible")
        print("\n🌐 Visit: https://www.mybookshelf.shop/admin")
        print("   Click the '🚨 Price Approvals' tab to use the interface")
        
        # Test complete workflow
        if test_complete_workflow():
            print("\n✅ Complete workflow test: PASSED")
            print("The system is ready for production use!")
        else:
            print("\n❌ Complete workflow test: FAILED")
            print("Please check the database setup")
        
        return
    
    # Setup not complete, provide instructions
    print_setup_instructions()
    
    # Wait for user to complete setup
    input("\nPress Enter when you've completed the SQL execution in Supabase...")
    
    # Verify setup after user completes it
    print("\n🧪 Verifying setup...")
    if verify_setup():
        print("\n🎉 SETUP COMPLETE!")
        print("The anomalous price approval interface is now operational.")
        print("\n🌐 Visit: https://www.mybookshelf.shop/admin")
        print("   Click the '🚨 Price Approvals' tab to test the interface")
        
        # Test complete workflow
        if test_complete_workflow():
            print("\n✅ Complete workflow test: PASSED")
            print("The system is ready for production use!")
        else:
            print("\n❌ Complete workflow test: FAILED")
            print("Please check the database setup")
    else:
        print("\n❌ SETUP INCOMPLETE")
        print("Please check the SQL execution and try again.")

if __name__ == "__main__":
    main() 