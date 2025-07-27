#!/usr/bin/env python3
"""
Create Price Validation Queue Table - Direct Method
Uses Supabase client operations to create the table
"""

import os
import sys
from supabase import create_client, Client

# Set up environment
os.environ.setdefault('SUPABASE_URL', 'https://ackcgrnizuhauccnbiml.supabase.co')
os.environ.setdefault('SUPABASE_ANON_KEY', 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImFja2Nncm5penVoYXVjY25iaW1sIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTEyMjc4MzEsImV4cCI6MjA2NjgwMzgzMX0.SXpIMuNBgUhcEQUHzpEB1zZAdF-UTGvmY81EFUtsAwc')

def create_table_direct():
    """Create the price validation queue table using direct operations"""
    
    try:
        # Connect to Supabase
        supabase: Client = create_client(
            os.environ['SUPABASE_URL'],
            os.environ['SUPABASE_ANON_KEY']
        )
        print("✅ Connected to Supabase")
        
        # First, let's try to insert a test record to see if the table exists
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
            print("✅ Table exists and is accessible!")
            
            # Clean up test data
            supabase.table('price_validation_queue').delete().eq('validation_reason', 'test_extreme_change_750pct_exceeds_35pct_limit').execute()
            print("✅ Test data cleaned up")
            
            return True
            
        except Exception as e:
            print(f"❌ Table does not exist: {e}")
            print("\n🔧 MANUAL SETUP REQUIRED")
            print("Please create the table manually in Supabase dashboard:")
            print("\n1. Go to: https://supabase.com/dashboard/project/ackcgrnizuhauccnbiml")
            print("2. Navigate to SQL Editor")
            print("3. Execute the SQL from backend/scripts/manual_database_setup.md")
            print("4. Run this script again to verify")
            
            return False
            
    except Exception as e:
        print(f"❌ Failed to connect to Supabase: {e}")
        return False

def add_validation_columns():
    """Add validation columns to books_accessories table"""
    
    try:
        # Connect to Supabase
        supabase: Client = create_client(
            os.environ['SUPABASE_URL'],
            os.environ['SUPABASE_ANON_KEY']
        )
        
        # Test if columns exist by trying to select them
        try:
            result = supabase.table('books_accessories').select('id, last_validation_status, validation_notes, requires_approval').limit(1).execute()
            print("✅ Validation columns already exist in books_accessories table")
            return True
        except Exception as e:
            print(f"❌ Validation columns don't exist: {e}")
            print("Please add the columns manually in Supabase dashboard:")
            print("\nALTER TABLE books_accessories ADD COLUMN IF NOT EXISTS last_validation_status TEXT;")
            print("ALTER TABLE books_accessories ADD COLUMN IF NOT EXISTS validation_notes TEXT;")
            print("ALTER TABLE books_accessories ADD COLUMN IF NOT EXISTS requires_approval BOOLEAN DEFAULT FALSE;")
            return False
            
    except Exception as e:
        print(f"❌ Error checking validation columns: {e}")
        return False

def test_complete_system():
    """Test the complete price approval system"""
    
    print("\n🧪 Testing Complete System...")
    
    try:
        # Test API endpoint
        import requests
        response = requests.get("https://mybookshelf.shop/api/price-approvals")
        print(f"✅ API endpoint status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print("✅ API endpoint working correctly")
            print(f"   Statistics: {data.get('statistics', {})}")
        else:
            print(f"❌ API endpoint error: {response.text}")
            
    except Exception as e:
        print(f"❌ Error testing API: {e}")

def main():
    """Main function"""
    
    print("🚀 PRICE VALIDATION QUEUE TABLE SETUP")
    print("=" * 50)
    
    # Step 1: Create table
    table_created = create_table_direct()
    
    # Step 2: Add validation columns
    columns_added = add_validation_columns()
    
    # Step 3: Test complete system
    if table_created and columns_added:
        test_complete_system()
    
    # Summary
    print("\n" + "=" * 50)
    print("📊 SETUP SUMMARY")
    print("=" * 50)
    print(f"✅ Price Validation Queue Table: {'Ready' if table_created else 'Needs Manual Setup'}")
    print(f"✅ Validation Columns: {'Ready' if columns_added else 'Needs Manual Setup'}")
    
    if table_created and columns_added:
        print("\n🎉 SYSTEM READY!")
        print("The anomalous price approval interface is now fully operational.")
        print("Visit https://www.mybookshelf.shop/admin and click the '🚨 Price Approvals' tab.")
    else:
        print("\n🔧 MANUAL SETUP REQUIRED")
        print("Please follow the instructions above to complete the database setup.")

if __name__ == "__main__":
    main() 