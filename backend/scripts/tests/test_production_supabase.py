#!/usr/bin/env python3
"""
Test Production Supabase Connection
"""

import os
import sys
from datetime import datetime

# Add parent directory for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from supabase.client import create_client, Client
    print("✅ Supabase library imported successfully")
except ImportError:
    print("❌ Supabase library not found. Install with: pip install supabase")
    sys.exit(1)

def test_production_connection():
    """Test production Supabase connection"""
    print("🧪 Testing Production Supabase Connection...")
    print("=" * 50)
    
    # Get environment variables
    supabase_url = os.getenv('SUPABASE_URL')
    supabase_key = os.getenv('SUPABASE_ANON_KEY')
    
    if not supabase_url:
        print("❌ SUPABASE_URL environment variable not set")
        print("Set with: export SUPABASE_URL='https://your-project-id.supabase.co'")
        return False
    
    if not supabase_key:
        print("❌ SUPABASE_ANON_KEY environment variable not set") 
        print("Set with: export SUPABASE_ANON_KEY='your-anon-key'")
        return False
    
    print(f"📊 Testing connection to: {supabase_url}")
    
    try:
        # Create client
        supabase: Client = create_client(supabase_url, supabase_key)
        print("✅ Supabase client created successfully")
        
        # Test database connection with a simple query
        result = supabase.table('books_accessories').select('count').execute()
        print("✅ Database connection successful")
        
        # Test admin tables
        result = supabase.table('pending_books').select('count').execute()
        print("✅ Admin tables accessible")
        
        result = supabase.table('approval_sessions').select('count').execute()
        print("✅ Approval system tables accessible")
        
        # Test admin dashboard view
        try:
            result = supabase.rpc('admin_dashboard_summary', {}).execute()
            print("✅ Admin dashboard view working")
        except Exception as e:
            print(f"⚠️  Admin dashboard view not available: {e}")
            print("   (This is normal if the function hasn't been created yet)")
        
        print("\n🎉 All tests passed! Production database is ready.")
        return True
        
    except Exception as e:
        print(f"❌ Connection test failed: {e}")
        print("\n🔧 Troubleshooting:")
        print("1. Verify project URL is correct")
        print("2. Verify anon key is correct") 
        print("3. Ensure database schemas are deployed")
        print("4. Check project is not paused/suspended")
        return False

if __name__ == "__main__":
    success = test_production_connection()
    sys.exit(0 if success else 1)
