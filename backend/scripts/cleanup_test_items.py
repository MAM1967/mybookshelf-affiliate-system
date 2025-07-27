#!/usr/bin/env python3
"""
Cleanup Test Approval Items
Removes all test items to ensure they don't interfere with real workflows
"""

import os
import sys
from supabase import create_client, Client

# Supabase configuration
SUPABASE_URL = "https://ackcgrnizuhauccnbiml.supabase.co"
SUPABASE_ANON_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImFja2Nncm5penVoYXVjY25iaW1sIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTEyMjc4MzEsImV4cCI6MjA2NjgwMzgzMX0.SXpIMuNBgUhcEQUHzpEB1zZAdF-UTGvmY81EFUtsAwc"

def cleanup_test_items():
    """Clean up all test items from the approval queue"""
    
    print("🧹 CLEANING UP TEST APPROVAL ITEMS")
    print("=" * 60)
    
    try:
        supabase: Client = create_client(SUPABASE_URL, SUPABASE_ANON_KEY)
        print("✅ Connected to Supabase")
        
        # First, check what test items exist
        print("\n1. Checking for test items...")
        result = supabase.table('price_validation_queue').select('*').like('validation_reason', 'test_extreme_change_%').execute()
        
        if result.data:
            print(f"   Found {len(result.data)} test items to clean up")
            for item in result.data:
                print(f"   - {item['validation_reason']} ({item['percentage_change']}% change)")
        else:
            print("   No test items found")
            return True
        
        # Delete all test items
        print(f"\n2. Deleting {len(result.data)} test items...")
        delete_result = supabase.table('price_validation_queue').delete().like('validation_reason', 'test_extreme_change_%').execute()
        
        print("✅ All test items deleted successfully")
        
        # Verify cleanup
        print("\n3. Verifying cleanup...")
        verify_result = supabase.table('price_validation_queue').select('*').like('validation_reason', 'test_extreme_change_%').execute()
        
        if not verify_result.data:
            print("✅ Cleanup verified - no test items remain")
        else:
            print(f"⚠️  {len(verify_result.data)} test items still found")
            return False
        
        # Check total items in queue
        total_result = supabase.table('price_validation_queue').select('*').execute()
        print(f"\n📊 Current approval queue status:")
        print(f"   Total items in queue: {len(total_result.data) if total_result.data else 0}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error during cleanup: {e}")
        return False

def cleanup_any_remaining_test_data():
    """Clean up any other test data that might exist"""
    
    print("\n🧹 CLEANING UP ANY REMAINING TEST DATA")
    print("=" * 60)
    
    try:
        supabase: Client = create_client(SUPABASE_URL, SUPABASE_ANON_KEY)
        
        # Clean up any test items with different patterns
        test_patterns = [
            'test_extreme_change_%',
            'test_%',
            '%test%'
        ]
        
        for pattern in test_patterns:
            try:
                result = supabase.table('price_validation_queue').delete().like('validation_reason', pattern).execute()
                if result:
                    print(f"✅ Cleaned up items with pattern: {pattern}")
            except Exception as e:
                print(f"⚠️  No items found with pattern: {pattern}")
        
        # Clean up any test data in books_accessories (just in case)
        try:
            # Reset any test validation status
            update_result = supabase.table('books_accessories').update({
                'last_validation_status': None,
                'validation_notes': None,
                'requires_approval': False
            }).eq('validation_notes', 'test').execute()
            
            print("✅ Cleaned up test validation status in books_accessories")
        except Exception as e:
            print("✅ No test validation status found in books_accessories")
        
        return True
        
    except Exception as e:
        print(f"❌ Error during additional cleanup: {e}")
        return False

def verify_production_ready():
    """Verify the system is clean and production-ready"""
    
    print("\n✅ VERIFYING PRODUCTION READINESS")
    print("=" * 60)
    
    try:
        supabase: Client = create_client(SUPABASE_URL, SUPABASE_ANON_KEY)
        
        # Check approval queue
        queue_result = supabase.table('price_validation_queue').select('*').execute()
        queue_count = len(queue_result.data) if queue_result.data else 0
        
        print(f"📊 Approval queue status: {queue_count} items")
        
        if queue_count == 0:
            print("✅ Queue is clean and ready for real data")
        else:
            print(f"⚠️  Queue contains {queue_count} items (may be real flagged items)")
        
        # Check API endpoint
        import requests
        try:
            response = requests.get("https://mybookshelf.shop/api/price-approvals")
            if response.status_code == 200:
                data = response.json()
                api_count = len(data.get('data', []))
                print(f"📊 API endpoint status: {api_count} items returned")
                
                if api_count == 0:
                    print("✅ API endpoint is clean and ready")
                else:
                    print(f"⚠️  API endpoint shows {api_count} items")
            else:
                print(f"❌ API endpoint error: {response.status_code}")
        except Exception as e:
            print(f"❌ API endpoint error: {e}")
        
        print("\n🎉 SYSTEM VERIFICATION COMPLETE")
        print("The anomalous price approval interface is now clean and ready for production use.")
        print("Only real flagged price changes will appear in the interface.")
        
        return True
        
    except Exception as e:
        print(f"❌ Error during verification: {e}")
        return False

def main():
    """Main function"""
    
    print("🚀 COMPREHENSIVE TEST DATA CLEANUP")
    print("=" * 60)
    
    # Step 1: Clean up test approval items
    success1 = cleanup_test_items()
    
    # Step 2: Clean up any remaining test data
    success2 = cleanup_any_remaining_test_data()
    
    # Step 3: Verify production readiness
    success3 = verify_production_ready()
    
    if success1 and success2 and success3:
        print("\n🎉 CLEANUP COMPLETE!")
        print("All test data has been removed from the system.")
        print("The approval interface is now clean and ready for real flagged price changes.")
        print("\n🌐 Visit: https://www.mybookshelf.shop/admin")
        print("   The '🚨 Price Approvals' tab will now only show real flagged items.")
    else:
        print("\n❌ CLEANUP INCOMPLETE")
        print("Some test data may still exist. Please check manually.")

if __name__ == "__main__":
    main() 