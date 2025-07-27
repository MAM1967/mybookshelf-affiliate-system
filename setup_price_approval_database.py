#!/usr/bin/env python3
"""
Setup Price Approval Database
Complete setup script for the anomalous price approval interface
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
    """Print the manual setup instructions"""
    
    print("🚀 PRICE APPROVAL DATABASE SETUP")
    print("=" * 60)
    print("The anomalous price approval interface is 80% complete!")
    print("We just need to create the database table and columns.")
    print("\n📋 MANUAL SETUP REQUIRED")
    print("=" * 60)
    print("Please follow these steps:")
    print("\n1. Open your web browser and go to:")
    print("   https://supabase.com/dashboard/project/ackcgrnizuhauccnbiml")
    print("\n2. Click on 'SQL Editor' in the left sidebar")
    print("\n3. Copy and paste this SQL into the editor:")
    print("\n" + "=" * 60)
    
    sql_code = """
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
    
    print(sql_code)
    print("=" * 60)
    print("\n4. Click 'Run' to execute the SQL")
    print("\n5. Wait for the execution to complete")
    print("\n6. Come back here and press Enter to verify the setup")
    print("\n" + "=" * 60)

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
        
        # Test 4: Test inserting test data
        print("\n4. Testing data insertion...")
        if table_exists:
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
                print("✅ Test data inserted successfully")
                
                # Clean up test data
                supabase.table('price_validation_queue').delete().eq('validation_reason', 'test_extreme_change_750pct_exceeds_35pct_limit').execute()
                print("✅ Test data cleaned up")
                data_insertion_working = True
                
            except Exception as e:
                print(f"❌ Data insertion error: {e}")
                data_insertion_working = False
        else:
            data_insertion_working = False
        
        # Summary
        print("\n" + "=" * 60)
        print("📊 VERIFICATION SUMMARY")
        print("=" * 60)
        print(f"✅ Price Validation Queue Table: {'Ready' if table_exists else 'Failed'}")
        print(f"✅ Validation Columns: {'Ready' if columns_exist else 'Failed'}")
        print(f"✅ API Endpoint: {'Working' if api_working else 'Failed'}")
        print(f"✅ Data Insertion: {'Working' if data_insertion_working else 'Failed'}")
        
        if table_exists and columns_exist and api_working and data_insertion_working:
            print("\n🎉 SYSTEM FULLY OPERATIONAL!")
            print("=" * 60)
            print("The anomalous price approval interface is now complete!")
            print("\n✅ What's working:")
            print("   - Database table and columns created")
            print("   - API endpoints functional")
            print("   - Data insertion and retrieval working")
            print("   - Admin interface ready")
            print("\n🌐 Next steps:")
            print("   1. Visit: https://www.mybookshelf.shop/admin")
            print("   2. Click the '🚨 Price Approvals' tab")
            print("   3. Test the approval/rejection functionality")
            print("   4. Monitor for flagged price changes")
            print("\n🎯 The system is now ready for production use!")
            
            return True
        else:
            print("\n❌ SETUP INCOMPLETE")
            print("=" * 60)
            print("Some components are not working. Please:")
            print("1. Check the error messages above")
            print("2. Re-run the SQL in Supabase dashboard")
            print("3. Run this script again to verify")
            
            return False
            
    except Exception as e:
        print(f"❌ Verification failed: {e}")
        return False

def main():
    """Main function"""
    
    print_setup_instructions()
    
    # Wait for user to complete manual setup
    input("\nPress Enter when you've completed the SQL execution in Supabase...")
    
    print("\n⏳ Waiting 5 seconds for database changes to propagate...")
    time.sleep(5)
    
    # Verify the setup
    success = verify_setup()
    
    if success:
        print("\n🎉 CONGRATULATIONS!")
        print("The anomalous price approval interface is now fully operational!")
        print("\nYou can now:")
        print("1. Review flagged price changes in the admin interface")
        print("2. Approve or reject extreme price fluctuations")
        print("3. Use bulk operations for efficiency")
        print("4. Monitor validation statistics")
    else:
        print("\n🔧 SETUP NEEDS ATTENTION")
        print("Please check the error messages and try again.")

if __name__ == "__main__":
    main() 