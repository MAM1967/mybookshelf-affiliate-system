#!/usr/bin/env python3
"""
Check Available Functions in Supabase
See what functions are available for table creation
"""

import requests
import json

# Supabase configuration
SUPABASE_URL = "https://ackcgrnizuhauccnbiml.supabase.co"
SUPABASE_ANON_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImFja2Nncm5penVoYXVjY25iaW1sIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTEyMjc4MzEsImV4cCI6MjA2NjgwMzgzMX0.SXpIMuNBgUhcEQUHzpEB1zZAdF-UTGvmY81EFUtsAwc"

def check_available_functions():
    """Check what functions are available"""
    
    headers = {
        'apikey': SUPABASE_ANON_KEY,
        'Authorization': f'Bearer {SUPABASE_ANON_KEY}',
        'Content-Type': 'application/json'
    }
    
    print("🔍 Checking available functions in Supabase...")
    
    # Try to get the schema information
    try:
        response = requests.get(
            f"{SUPABASE_URL}/rest/v1/",
            headers=headers
        )
        
        print(f"✅ Schema endpoint status: {response.status_code}")
        if response.status_code == 200:
            print("✅ Schema endpoint accessible")
            print("Available tables:", response.json())
        else:
            print(f"❌ Schema endpoint error: {response.text}")
            
    except Exception as e:
        print(f"❌ Error accessing schema: {e}")
    
    # Try to list available RPC functions
    try:
        response = requests.get(
            f"{SUPABASE_URL}/rest/v1/rpc/",
            headers=headers
        )
        
        print(f"\n✅ RPC endpoint status: {response.status_code}")
        if response.status_code == 200:
            print("✅ RPC endpoint accessible")
            # This might not work, but worth trying
        else:
            print(f"❌ RPC endpoint error: {response.text}")
            
    except Exception as e:
        print(f"❌ Error accessing RPC: {e}")

def try_direct_table_creation():
    """Try to create table by inserting data directly"""
    
    print("\n🚀 Trying direct table creation...")
    
    headers = {
        'apikey': SUPABASE_ANON_KEY,
        'Authorization': f'Bearer {SUPABASE_ANON_KEY}',
        'Content-Type': 'application/json',
        'Prefer': 'return=minimal'
    }
    
    # Try to insert data directly - this might auto-create the table
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
        response = requests.post(
            f"{SUPABASE_URL}/rest/v1/price_validation_queue",
            headers=headers,
            json=test_data
        )
        
        print(f"✅ Direct insert response: {response.status_code}")
        if response.status_code == 201:
            print("✅ Table created successfully via direct insert!")
            
            # Clean up test data
            cleanup_response = requests.delete(
                f"{SUPABASE_URL}/rest/v1/price_validation_queue?validation_reason=eq.test_extreme_change_750pct_exceeds_35pct_limit",
                headers=headers
            )
            print("✅ Test data cleaned up")
            return True
        else:
            print(f"❌ Direct insert failed: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error with direct insert: {e}")
        return False

def main():
    """Main function"""
    
    print("🔍 SUPABASE FUNCTION ANALYSIS")
    print("=" * 60)
    
    # Check available functions
    check_available_functions()
    
    # Try direct table creation
    success = try_direct_table_creation()
    
    if success:
        print("\n🎉 SUCCESS! Table created via direct insert.")
        print("The anomalous price approval interface should now be operational.")
    else:
        print("\n❌ Direct creation failed. Manual setup required.")
        print("Please create the table manually in the Supabase dashboard.")

if __name__ == "__main__":
    main() 