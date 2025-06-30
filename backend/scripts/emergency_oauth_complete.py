#!/usr/bin/env python3
"""
Emergency LinkedIn OAuth Completion Script
Completes LinkedIn OAuth flow manually when domain routing issues prevent automatic callback
"""

import sys
import os
import requests
import json
from datetime import datetime
from urllib.parse import urlparse, parse_qs

# Add parent directory for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    import config
    from supabase.client import create_client, Client
    SUPABASE_URL = getattr(config, 'SUPABASE_URL', None)
    SUPABASE_ANON_KEY = getattr(config, 'SUPABASE_ANON_KEY', None)
    SUPABASE_AVAILABLE = True
except ImportError:
    print("⚠️ Supabase not available - will complete OAuth without database storage")
    SUPABASE_AVAILABLE = False
    SUPABASE_URL = None
    SUPABASE_ANON_KEY = None

# LinkedIn OAuth Configuration
LINKEDIN_CLIENT_ID = "78wmrhdd99ssbi"
LINKEDIN_CLIENT_SECRET = os.getenv('LINKEDIN_CLIENT_SECRET')
REDIRECT_URI = "https://mybookshelf.shop/linkedin-oauth.html"

class LinkedInOAuthEmergencyCompleter:
    """Emergency LinkedIn OAuth completion handler"""
    
    def __init__(self):
        """Initialize the emergency OAuth completer"""
        self.client_id = LINKEDIN_CLIENT_ID
        self.client_secret = LINKEDIN_CLIENT_SECRET
        self.redirect_uri = REDIRECT_URI
        
        # Initialize Supabase if available
        self.supabase = None
        if SUPABASE_AVAILABLE and SUPABASE_URL and SUPABASE_ANON_KEY:
            try:
                self.supabase = create_client(SUPABASE_URL, SUPABASE_ANON_KEY)
                print("✅ Supabase connection established")
            except Exception as e:
                print(f"⚠️ Supabase connection failed: {e}")
    
    def extract_code_from_url(self, full_url):
        """Extract authorization code from callback URL"""
        print(f"🔍 Extracting authorization code from URL...")
        
        try:
            # Parse the URL
            parsed = urlparse(full_url)
            params = parse_qs(parsed.query)
            
            # Extract code and state
            code = params.get('code', [None])[0]
            state = params.get('state', [None])[0]
            error = params.get('error', [None])[0]
            error_description = params.get('error_description', [None])[0]
            
            if error:
                print(f"❌ OAuth error: {error}")
                if error_description:
                    print(f"   Description: {error_description}")
                return None, None
            
            if not code:
                print("❌ No authorization code found in URL")
                return None, None
            
            if state and state != 'mybookshelf_production_oauth' and not state.startswith('mybookshelf_'):
                print(f"⚠️ State parameter mismatch: {state}")
                print("   This could indicate a security issue")
            
            print(f"✅ Authorization code extracted successfully")
            print(f"   Code length: {len(code)} characters")
            print(f"   State: {state}")
            
            return code, state
            
        except Exception as e:
            print(f"❌ Error parsing URL: {e}")
            return None, None
    
    def exchange_code_for_token(self, auth_code):
        """Exchange authorization code for access token"""
        print("🔄 Exchanging authorization code for access token...")
        
        if not self.client_secret:
            print("❌ LINKEDIN_CLIENT_SECRET environment variable not set")
            print("   Please set it and try again")
            return None
        
        # Token exchange request
        token_url = "https://www.linkedin.com/oauth/v2/accessToken"
        token_data = {
            'grant_type': 'authorization_code',
            'code': auth_code,
            'client_id': self.client_id,
            'client_secret': self.client_secret,
            'redirect_uri': self.redirect_uri
        }
        
        try:
            response = requests.post(token_url, data=token_data)
            
            if response.status_code == 200:
                token_info = response.json()
                print("✅ Token exchange successful!")
                print(f"   Access token: {token_info.get('access_token', 'N/A')[:20]}...")
                print(f"   Token type: {token_info.get('token_type', 'N/A')}")
                print(f"   Expires in: {token_info.get('expires_in', 'N/A')} seconds")
                return token_info
            else:
                print(f"❌ Token exchange failed: {response.status_code}")
                print(f"   Response: {response.text}")
                return None
                
        except Exception as e:
            print(f"❌ Token exchange error: {e}")
            return None
    
    def get_user_profile(self, access_token):
        """Get LinkedIn user profile"""
        print("👤 Fetching user profile...")
        
        profile_url = "https://api.linkedin.com/v2/userinfo"
        headers = {
            'Authorization': f'Bearer {access_token}',
            'Content-Type': 'application/json'
        }
        
        try:
            response = requests.get(profile_url, headers=headers)
            
            if response.status_code == 200:
                profile = response.json()
                print("✅ Profile retrieved successfully!")
                print(f"   Name: {profile.get('name', 'N/A')}")
                print(f"   Email: {profile.get('email', 'N/A')}")
                print(f"   LinkedIn ID: {profile.get('sub', 'N/A')}")
                return profile
            else:
                print(f"❌ Profile fetch failed: {response.status_code}")
                print(f"   Response: {response.text}")
                return None
                
        except Exception as e:
            print(f"❌ Profile fetch error: {e}")
            return None
    
    def store_access_token(self, token_info, profile):
        """Store access token in Supabase database"""
        if not self.supabase:
            print("⚠️ Supabase not available - skipping database storage")
            return False
        
        print("💾 Storing access token in database...")
        
        try:
            # Prepare token data
            token_data = {
                'access_token': token_info['access_token'],
                'token_type': token_info.get('token_type', 'Bearer'),
                'expires_in': token_info.get('expires_in'),
                'scope': token_info.get('scope'),
                'created_at': datetime.now().isoformat(),
                'linkedin_id': profile.get('sub'),
                'linkedin_name': profile.get('name'),
                'linkedin_email': profile.get('email'),
                'is_active': True
            }
            
            # Insert or update token in database
            result = self.supabase.table('linkedin_tokens').upsert(
                token_data,
                on_conflict='linkedin_id'
            ).execute()
            
            if result.data:
                print("✅ Token stored successfully in database")
                return True
            else:
                print("❌ Failed to store token in database")
                return False
                
        except Exception as e:
            print(f"❌ Database storage error: {e}")
            return False
    
    def complete_oauth_from_url(self, callback_url):
        """Complete the entire OAuth flow from callback URL"""
        print("🚀 Emergency LinkedIn OAuth Completion")
        print("=" * 50)
        
        # Step 1: Extract authorization code
        auth_code, state = self.extract_code_from_url(callback_url)
        if not auth_code:
            return False
        
        # Step 2: Exchange code for token
        token_info = self.exchange_code_for_token(auth_code)
        if not token_info:
            return False
        
        # Step 3: Get user profile
        profile = self.get_user_profile(token_info['access_token'])
        if not profile:
            return False
        
        # Step 4: Store token (optional)
        stored = self.store_access_token(token_info, profile)
        
        # Step 5: Success summary
        print("\n🎉 LinkedIn OAuth completion successful!")
        print("=" * 50)
        print(f"✅ Access token obtained: {token_info['access_token'][:20]}...")
        print(f"✅ Profile retrieved: {profile.get('name', 'Unknown')}")
        print(f"✅ Database storage: {'Success' if stored else 'Skipped/Failed'}")
        
        print("\n🚀 Next Steps:")
        print("1. LinkedIn automation is now ready")
        print("2. Test posting functionality") 
        print("3. Enable Sunday approval workflow")
        
        # Save token info for manual use
        with open('linkedin_token_info.json', 'w') as f:
            json.dump({
                'token_info': token_info,
                'profile': profile,
                'completion_time': datetime.now().isoformat()
            }, f, indent=2)
        print("\n💾 Token info saved to: linkedin_token_info.json")
        
        return True

def main():
    """Main function"""
    if len(sys.argv) < 2:
        print("🔧 LinkedIn OAuth Emergency Completion Script")
        print("=" * 50)
        print()
        print("Usage:")
        print("   python3 emergency_oauth_complete.py <callback_url>")
        print()
        print("Examples:")
        print("   # Complete OAuth from callback URL")
        print("   python3 emergency_oauth_complete.py 'https://mybookshelf.shop/linkedin-oauth?code=AQS39r...'")
        print()
        print("   # Or just the authorization code")
        print("   python3 emergency_oauth_complete.py 'AQS39rBAlBa4R0c2tQa...'")
        print()
        print("Environment Variables Required:")
        print("   LINKEDIN_CLIENT_SECRET - Your LinkedIn app client secret")
        print("   SUPABASE_URL          - Supabase project URL (optional)")
        print("   SUPABASE_ANON_KEY     - Supabase anon key (optional)")
        return
    
    # Initialize completer
    completer = LinkedInOAuthEmergencyCompleter()
    
    # Get callback URL from command line
    callback_input = sys.argv[1]
    
    # If input doesn't look like a URL, assume it's just the code
    if not callback_input.startswith('http'):
        callback_url = f"https://mybookshelf.shop/linkedin-oauth?code={callback_input}&state=mybookshelf_production_oauth"
    else:
        callback_url = callback_input
    
    # Complete OAuth flow
    success = completer.complete_oauth_from_url(callback_url)
    
    if success:
        print("\n✅ Emergency OAuth completion successful!")
        exit(0)
    else:
        print("\n❌ Emergency OAuth completion failed!")
        exit(1)

if __name__ == "__main__":
    main() 