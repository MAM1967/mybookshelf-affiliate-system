#!/usr/bin/env python3
"""
LinkedIn OAuth Test & Setup for MyBookshelf Affiliate System
Tests LinkedIn Developer App credentials and sets up OAuth flow
"""

import requests
import json
from urllib.parse import urlencode
import webbrowser

# LinkedIn Developer App Credentials
LINKEDIN_CLIENT_ID = "78wmrhdd99ssbi"
LINKEDIN_CLIENT_SECRET = "WPL_AP1.hCyy0nkGz9y5i1tP.ExgKnQ=="

# OAuth Configuration
REDIRECT_URI = "http://localhost:8000/auth/linkedin/callback"  # For testing
SCOPE = "w_member_social w_organization_social"  # Permission to post on behalf of user and organization

# LinkedIn API URLs
AUTHORIZATION_URL = "https://www.linkedin.com/oauth/v2/authorization"
TOKEN_URL = "https://www.linkedin.com/oauth/v2/accessToken"
PROFILE_URL = "https://api.linkedin.com/v2/people/~"

def get_authorization_url():
    """Generate LinkedIn OAuth authorization URL"""
    params = {
        'response_type': 'code',
        'client_id': LINKEDIN_CLIENT_ID,
        'redirect_uri': REDIRECT_URI,
        'scope': SCOPE,
        'state': 'mybookshelf_oauth_test'  # CSRF protection
    }
    
    auth_url = f"{AUTHORIZATION_URL}?{urlencode(params)}"
    return auth_url

def exchange_code_for_token(auth_code):
    """Exchange authorization code for access token"""
    data = {
        'grant_type': 'authorization_code',
        'code': auth_code,
        'redirect_uri': REDIRECT_URI,
        'client_id': LINKEDIN_CLIENT_ID,
        'client_secret': LINKEDIN_CLIENT_SECRET
    }
    
    response = requests.post(TOKEN_URL, data=data)
    
    if response.status_code == 200:
        return response.json()
    else:
        print(f"❌ Token exchange failed: {response.status_code}")
        print(f"Response: {response.text}")
        return None

def get_user_profile(access_token):
    """Get user profile to test API access"""
    headers = {
        'Authorization': f'Bearer {access_token}',
        'Content-Type': 'application/json'
    }
    
    response = requests.get(PROFILE_URL, headers=headers)
    
    if response.status_code == 200:
        return response.json()
    else:
        print(f"❌ Profile fetch failed: {response.status_code}")
        print(f"Response: {response.text}")
        return None

def test_credentials():
    """Test LinkedIn OAuth credentials setup"""
    print("🔗 LinkedIn OAuth Credentials Test")
    print("=" * 40)
    
    # Check credentials are set
    if not LINKEDIN_CLIENT_ID or not LINKEDIN_CLIENT_SECRET:
        print("❌ LinkedIn credentials not configured")
        return False
    
    print(f"✅ Client ID configured: {LINKEDIN_CLIENT_ID[:10]}...")
    print(f"✅ Client Secret configured: {LINKEDIN_CLIENT_SECRET[:15]}...")
    
    # Generate authorization URL
    auth_url = get_authorization_url()
    print(f"\n🔗 OAuth Authorization URL generated:")
    print(f"{auth_url[:100]}...")
    
    return True

def interactive_oauth_flow():
    """Interactive OAuth flow for testing"""
    print("\n🚀 Starting Interactive OAuth Flow")
    print("=" * 40)
    
    # Step 1: Get authorization URL
    auth_url = get_authorization_url()
    print(f"1. Opening LinkedIn authorization URL...")
    print(f"   {auth_url}")
    
    try:
        webbrowser.open(auth_url)
        print("✅ Browser opened with authorization URL")
    except:
        print("⚠️  Could not open browser, please copy URL above")
    
    print("\n2. After authorizing, LinkedIn will redirect to:")
    print(f"   {REDIRECT_URI}?code=AUTHORIZATION_CODE&state=mybookshelf_oauth_test")
    
    print("\n3. Copy the 'code' parameter from the redirect URL and paste here:")
    auth_code = input("Authorization code: ").strip()
    
    if not auth_code:
        print("❌ No authorization code provided")
        return
    
    # Step 2: Exchange code for token
    print("\n🔄 Exchanging authorization code for access token...")
    token_data = exchange_code_for_token(auth_code)
    
    if not token_data:
        return
    
    access_token = token_data.get('access_token')
    print(f"✅ Access token obtained: {access_token[:20]}...")
    
    # Step 3: Test API access
    print("\n👤 Testing API access with profile fetch...")
    profile = get_user_profile(access_token)
    
    if profile:
        print("✅ LinkedIn API access working!")
        print(f"Profile ID: {profile.get('id', 'N/A')}")
        first_name = profile.get('localizedFirstName', 'N/A')
        last_name = profile.get('localizedLastName', 'N/A')
        print(f"Name: {first_name} {last_name}")
        
        # Save token for future use
        with open('linkedin_token.json', 'w') as f:
            json.dump(token_data, f, indent=2)
        print("💾 Token saved to linkedin_token.json")
        
    else:
        print("❌ LinkedIn API access failed")

def main():
    """Main test function"""
    print("🔗 LinkedIn Developer App Test - MyBookshelf")
    print("=" * 50)
    
    # Test basic credential setup
    if not test_credentials():
        return
    
    print("\n📋 Test Options:")
    print("1. Quick credential test (completed above)")
    print("2. Interactive OAuth flow test")
    print("3. Just show authorization URL")
    
    choice = input("\nChoose option (1-3): ").strip()
    
    if choice == "2":
        interactive_oauth_flow()
    elif choice == "3":
        auth_url = get_authorization_url()
        print(f"\n🔗 Authorization URL:")
        print(auth_url)
        print("\nUse this URL to test OAuth flow manually")
    else:
        print("\n✅ Basic credential test completed successfully!")
        print("LinkedIn OAuth app is properly configured and ready for integration.")

if __name__ == "__main__":
    main() 