#!/usr/bin/env python3
"""
Test script to verify MyBookshelf system functionality
"""

import os
import sys

# Add backend scripts to path
current_dir = os.path.dirname(os.path.abspath(__file__))
scripts_dir = os.path.join(current_dir, 'scripts')
sys.path.insert(0, current_dir)
sys.path.insert(0, scripts_dir)

# Try to load environment variables
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    print("⚠️  python-dotenv not installed. Install with: pip install python-dotenv")

try:
    from scripts.fetch_books import MyBookshelfSystem
    from config import Config
except ImportError as e:
    print(f"❌ Import error: {e}")
    print("Make sure you have installed the requirements: pip install -r requirements.txt")
    print("And that you're running this from the backend/ directory")
    sys.exit(1)

def test_configuration():
    """Test environment configuration"""
    print("🔧 Testing Configuration...")
    
    if Config.validate_required_settings():
        print("✅ Configuration is valid")
        return True
    else:
        print("❌ Configuration is missing required variables")
        print("\n📝 Create a .env file with these variables:")
        print(Config.get_example_env_content())
        return False

def test_supabase_connection():
    """Test Supabase database connection"""
    print("\n🔗 Testing Supabase Connection...")
    
    try:
        system = MyBookshelfSystem()
        
        # Try to fetch existing data
        recommendations = system.get_latest_recommendations(limit=5)
        print(f"✅ Successfully connected to Supabase")
        print(f"📚 Found {len(recommendations)} existing recommendations")
        
        # Display existing data if any
        if recommendations:
            print("\n📖 Latest recommendations:")
            for item in recommendations:
                print(f"  - {item.get('title')} by {item.get('author')} (${item.get('price')})")
        
        return True
        
    except Exception as e:
        print(f"❌ Supabase connection failed: {e}")
        return False

def test_mock_data_insertion():
    """Test inserting mock data"""
    print("\n📝 Testing Mock Data Insertion...")
    
    try:
        system = MyBookshelfSystem()
        
        # Run weekly update (will use mock data if Amazon API not configured)
        result = system.run_weekly_update()
        
        if result['success']:
            print(f"✅ {result['message']}")
            print(f"📚 Items processed: {len(result.get('items', []))}")
            
            # Show what was added
            for item in result.get('items', []):
                print(f"  - {item['title']} by {item['author']} (${item['price']})")
            
            return True
        else:
            print(f"❌ Mock data insertion failed: {result['message']}")
            return False
            
    except Exception as e:
        print(f"❌ Error during mock data insertion: {e}")
        return False

def main():
    """Main test function"""
    print("🧪 MyBookshelf System Test Suite")
    print("=" * 50)
    
    # Test 1: Configuration
    config_ok = test_configuration()
    
    if not config_ok:
        print("\n⚠️  Skipping connection tests due to configuration issues")
        return 1
    
    # Test 2: Supabase Connection
    connection_ok = test_supabase_connection()
    
    if not connection_ok:
        print("\n⚠️  Skipping data insertion test due to connection issues")
        return 1
    
    # Test 3: Mock Data Insertion
    insertion_ok = test_mock_data_insertion()
    
    # Final Results
    print("\n" + "=" * 50)
    print("🏁 Test Results Summary:")
    print(f"   Configuration: {'✅ Pass' if config_ok else '❌ Fail'}")
    print(f"   Supabase Connection: {'✅ Pass' if connection_ok else '❌ Fail'}")
    print(f"   Data Insertion: {'✅ Pass' if insertion_ok else '❌ Fail'}")
    
    if all([config_ok, connection_ok, insertion_ok]):
        print("\n🎉 All tests passed! Your MyBookshelf system is ready!")
        print("\n📋 Next Steps:")
        print("   1. Open frontend/mini-app/index.html in a browser")
        print("   2. Configure your Supabase credentials in the HTML file")
        print("   3. Set up Amazon PA API credentials for live data")
        print("   4. Configure Pipedream workflows for automation")
        return 0
    else:
        print("\n⚠️  Some tests failed. Please check the issues above.")
        return 1

if __name__ == "__main__":
    exit(main()) 