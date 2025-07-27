#!/usr/bin/env python3
"""
Create Test Approval Items
Adds sample flagged price changes to test the approval interface
"""

import os
import sys
from supabase import create_client, Client

# Supabase configuration
SUPABASE_URL = "https://ackcgrnizuhauccnbiml.supabase.co"
SUPABASE_ANON_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImFja2Nncm5penVoYXVjY25iaW1sIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTEyMjc4MzEsImV4cCI6MjA2NjgwMzgzMX0.SXpIMuNBgUhcEQUHzpEB1zZAdF-UTGvmY81EFUtsAwc"

def create_test_approval_items():
    """Create test items for the approval interface"""
    
    print("🧪 Creating Test Approval Items...")
    print("=" * 60)
    
    try:
        supabase: Client = create_client(SUPABASE_URL, SUPABASE_ANON_KEY)
        print("✅ Connected to Supabase")
        
        # Get real items from the database
        print("\n1. Getting real items from database...")
        result = supabase.table('books_accessories').select('id, title, price').limit(5).execute()
        
        if not result.data:
            print("❌ No items found in database")
            return False
        
        items = result.data
        print(f"✅ Found {len(items)} items to use for testing")
        
        # Create test approval items
        test_items = []
        
        for i, item in enumerate(items):
            old_price = float(item['price']) if item['price'] else 10.00
            new_price = old_price * (1.5 + i * 0.5)  # Different percentage increases
            percentage_change = ((new_price - old_price) / old_price) * 100
            
            test_item = {
                "item_id": item['id'],
                "old_price": old_price,
                "new_price": new_price,
                "percentage_change": round(percentage_change, 2),
                "validation_reason": f"test_extreme_change_{percentage_change:.1f}pct_exceeds_35pct_limit",
                "validation_layer": "threshold_validation",
                "validation_details": {
                    "priceCategory": "test",
                    "maxChangePercent": 35,
                    "actualChange": percentage_change,
                    "test": True
                },
                "status": "pending",
                "flagged_at": "2025-07-27T23:15:00Z"
            }
            test_items.append(test_item)
        
        # Insert test items
        print(f"\n2. Inserting {len(test_items)} test approval items...")
        for i, test_item in enumerate(test_items):
            try:
                result = supabase.table('price_validation_queue').insert(test_item).execute()
                print(f"   ✅ Added test item {i+1}: {test_item['percentage_change']:.1f}% change")
            except Exception as e:
                print(f"   ❌ Failed to add test item {i+1}: {e}")
        
        print(f"\n✅ Successfully created {len(test_items)} test approval items")
        print("\n🌐 Now visit: https://www.mybookshelf.shop/admin")
        print("   Click the '🚨 Price Approvals' tab to see the test items")
        print("\n📋 You can now:")
        print("   - View the flagged price changes")
        print("   - Approve or reject individual items")
        print("   - Use bulk operations")
        print("   - See the statistics update")
        
        return True
        
    except Exception as e:
        print(f"❌ Error creating test items: {e}")
        return False

def cleanup_test_items():
    """Clean up test items"""
    
    print("\n🧹 Cleaning up test items...")
    
    try:
        supabase: Client = create_client(SUPABASE_URL, SUPABASE_ANON_KEY)
        
        # Delete all test items
        result = supabase.table('price_validation_queue').delete().like('validation_reason', 'test_extreme_change_%').execute()
        
        print("✅ Test items cleaned up")
        return True
        
    except Exception as e:
        print(f"❌ Error cleaning up: {e}")
        return False

def main():
    """Main function"""
    
    print("🚀 CREATE TEST APPROVAL ITEMS")
    print("=" * 60)
    
    # Check if user wants to clean up first
    cleanup = input("Do you want to clean up existing test items first? (y/n): ").lower().strip()
    
    if cleanup == 'y':
        cleanup_test_items()
    
    # Create new test items
    success = create_test_approval_items()
    
    if success:
        print("\n🎉 Test items created successfully!")
        print("The approval interface should now show test items.")
    else:
        print("\n❌ Failed to create test items")
        print("Please check the database connection and try again.")

if __name__ == "__main__":
    main() 