#!/usr/bin/env python3
"""
Test LinkedIn OAuth Flow End-to-End
"""

import os
import sys
import webbrowser
from datetime import datetime

# Add parent directory for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from linkedin_api_production import LinkedInAPIProduction
except ImportError:
    print("❌ Cannot import linkedin_api_production.py")
    print("Make sure the file exists and dependencies are installed")
    sys.exit(1)

def test_oauth_flow():
    """Test the complete OAuth flow"""
    print("🔗 Testing LinkedIn OAuth Flow")
    print("=" * 50)
    
    # Check environment variables
    client_id = os.getenv('LINKEDIN_CLIENT_ID', '78wmrhdd99ssbi')
    client_secret = os.getenv('LINKEDIN_CLIENT_SECRET')
    
    if not client_secret:
        print("❌ LINKEDIN_CLIENT_SECRET environment variable not set")
        print("Set with: export LINKEDIN_CLIENT_SECRET='your-client-secret'")
        return False
    
    print(f"✅ Client ID: {client_id}")
    print(f"✅ Client Secret: {'*' * len(client_secret[:-4])}...")
    
    try:
        linkedin = LinkedInAPIProduction()
        
        # Step 1: Generate authorization URL
        print("\n🔗 Step 1: Generating authorization URL...")
        auth_url = linkedin.get_authorization_url()
        
        print(f"✅ Authorization URL generated:")
        print(f"   {auth_url}")
        
        # Step 2: Open browser for user authorization
        print("\n🌐 Step 2: Opening browser for authorization...")
        try:
            webbrowser.open(auth_url)
            print("✅ Browser opened successfully")
        except Exception as e:
            print(f"⚠️ Could not open browser: {e}")
            print("Please manually open the URL above")
        
        # Step 3: Wait for user to complete authorization
        print("\n⏳ Step 3: Complete authorization in browser...")
        print("After authorizing, copy the authorization code from the callback page")
        
        auth_code = input("\nPaste the authorization code here: ").strip()
        
        if not auth_code:
            print("❌ No authorization code provided")
            return False
        
        # Step 4: Exchange code for token
        print("\n🔄 Step 4: Exchanging code for access token...")
        token_info = linkedin.exchange_code_for_token(auth_code)
        
        if not token_info:
            print("❌ Token exchange failed")
            return False
        
        print("✅ Token exchange successful!")
        
        # Step 5: Store token
        print("\n💾 Step 5: Storing access token...")
        if linkedin.store_access_token(token_info):
            print("✅ Token stored successfully!")
        else:
            print("❌ Token storage failed")
            return False
        
        # Step 6: Test connection
        print("\n🧪 Step 6: Testing LinkedIn connection...")
        if linkedin.test_linkedin_connection():
            print("✅ LinkedIn connection test successful!")
        else:
            print("❌ LinkedIn connection test failed")
            return False
        
        # Step 7: Create test post
        test_post = input("\nEnter a test post message (or press Enter to skip): ").strip()
        if test_post:
            print("\n📝 Step 7: Creating test post...")
            if linkedin.create_text_post(test_post):
                print("✅ Test post created successfully!")
            else:
                print("❌ Test post failed")
                return False
        
        print("\n🎉 OAuth flow test completed successfully!")
        print("Your LinkedIn integration is ready for production!")
        return True
        
    except Exception as e:
        print(f"❌ OAuth flow test failed: {e}")
        return False

if __name__ == "__main__":
    success = test_oauth_flow()
    sys.exit(0 if success else 1)
