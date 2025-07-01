#!/usr/bin/env python3
"""
LinkedIn API Production Configuration
Generates OAuth URLs and manages LinkedIn API for production deployment
"""

import os
import sys
import json
import requests
import urllib.parse
from datetime import datetime, timedelta
from typing import Dict, Optional, List
import logging
from urllib.parse import urlencode

# Add parent directory for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from supabase.client import create_client, Client
    from config import Config
except ImportError as e:
    print(f"❌ Import error: {e}")
    print("Make sure you're running from the correct directory with proper dependencies")
    sys.exit(1)

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class LinkedInAPIProduction:
    """Production LinkedIn API integration"""
    
    def __init__(self):
        """Initialize LinkedIn API client"""
        self.client_id = os.getenv('LINKEDIN_CLIENT_ID', '78wmrhdd99ssbi')
        self.client_secret = os.getenv('LINKEDIN_CLIENT_SECRET')
        self.redirect_uri = os.getenv('LINKEDIN_REDIRECT_URI', 'https://mybookshelf.shop/api/linkedin-callback')
        
        # Initialize Supabase for token storage (optional for URL generation)
        self.supabase: Optional[Client] = None
        if Config.SUPABASE_URL and Config.SUPABASE_ANON_KEY:
            try:
                self.supabase = create_client(Config.SUPABASE_URL, Config.SUPABASE_ANON_KEY)
            except Exception as e:
                logger.warning(f"⚠️ Supabase initialization failed: {e}")
        else:
            logger.info("ℹ️ Supabase not configured - some features will be limited")
        
        # LinkedIn API endpoints
        self.auth_url = 'https://www.linkedin.com/oauth/v2/authorization'
        self.token_url = 'https://www.linkedin.com/oauth/v2/accessToken'
        self.profile_url = 'https://api.linkedin.com/v2/userinfo'
        self.posts_url = 'https://api.linkedin.com/v2/ugcPosts'
        
        # Required scopes
        self.scopes = ['openid', 'profile', 'w_member_social', 'email', 'rw_organization_admin']
    
    def get_authorization_url(self, state: Optional[str] = None) -> str:
        """Generate LinkedIn authorization URL"""
        if not state:
            state = f"mybookshelf_production_oauth"
        
        params = {
            'response_type': 'code',
            'client_id': self.client_id,
            'redirect_uri': self.redirect_uri,
            'state': state,
            'scope': ' '.join(self.scopes)
        }
        
        auth_url = f"{self.auth_url}?{urlencode(params)}"
        logger.info(f"Generated authorization URL: {auth_url}")
        return auth_url
    
    def exchange_code_for_token(self, authorization_code: str) -> Optional[Dict]:
        """Exchange authorization code for access token"""
        try:
            data = {
                'grant_type': 'authorization_code',
                'code': authorization_code,
                'client_id': self.client_id,
                'client_secret': self.client_secret,
                'redirect_uri': self.redirect_uri
            }
            
            response = requests.post(self.token_url, data=data)
            
            if response.status_code == 200:
                token_data = response.json()
                
                # Calculate expiration time
                expires_in = token_data.get('expires_in', 5184000)  # Default 60 days
                expires_at = datetime.now() + timedelta(seconds=expires_in)
                
                token_info = {
                    'access_token': token_data['access_token'],
                    'expires_in': expires_in,
                    'expires_at': expires_at.isoformat(),
                    'scope': token_data.get('scope', ' '.join(self.scopes)),
                    'token_type': token_data.get('token_type', 'Bearer'),
                    'obtained_at': datetime.now().isoformat()
                }
                
                logger.info("✅ Successfully exchanged authorization code for access token")
                return token_info
            else:
                logger.error(f"❌ Token exchange failed: {response.status_code} - {response.text}")
                return None
                
        except Exception as e:
            logger.error(f"❌ Error exchanging code for token: {e}")
            return None
    
    def store_access_token(self, token_info: Dict, admin_email: str = 'mcddsl@icloud.com') -> bool:
        """Store access token in Supabase"""
        try:
            # First, get user profile to validate token
            profile = self.get_user_profile(token_info['access_token'])
            if not profile:
                logger.error("❌ Failed to validate token - cannot get user profile")
                return False
            
            # Store token in database
            token_record = {
                'admin_email': admin_email,
                'access_token': token_info['access_token'],
                'token_type': token_info['token_type'],
                'expires_at': token_info['expires_at'],
                'scope': token_info['scope'],
                'linkedin_user_id': profile.get('sub'),
                'linkedin_name': profile.get('name'),
                'linkedin_email': profile.get('email'),
                'created_at': datetime.now().isoformat(),
                'is_active': True
            }
            
            # Insert or update token
            result = self.supabase.table('linkedin_tokens').upsert(
                token_record, 
                on_conflict='admin_email'
            ).execute()
            
            if result.data:
                logger.info("✅ Access token stored successfully")
                return True
            else:
                logger.error("❌ Failed to store access token")
                return False
                
        except Exception as e:
            logger.error(f"❌ Error storing access token: {e}")
            return False
    
    def get_stored_token(self, admin_email: str = 'mcddsl@icloud.com') -> Optional[Dict]:
        """Get stored access token from database"""
        try:
            result = self.supabase.table('linkedin_tokens').select('*').eq(
                'admin_email', admin_email
            ).eq('is_active', True).execute()
            
            if result.data:
                token_record = result.data[0]
                
                # Check if token is expired
                expires_at = datetime.fromisoformat(token_record['expires_at'])
                if expires_at <= datetime.now():
                    logger.warning("⚠️ Stored token has expired")
                    return None
                
                return token_record
            else:
                logger.info("ℹ️ No stored token found")
                return None
                
        except Exception as e:
            logger.error(f"❌ Error retrieving stored token: {e}")
            return None
    
    def get_user_profile(self, access_token: str) -> Optional[Dict]:
        """Get LinkedIn user profile"""
        try:
            headers = {
                'Authorization': f'Bearer {access_token}',
                'Content-Type': 'application/json'
            }
            
            response = requests.get(self.profile_url, headers=headers)
            
            if response.status_code == 200:
                profile = response.json()
                logger.info(f"✅ Retrieved profile for: {profile.get('name', 'Unknown')}")
                return profile
            else:
                logger.error(f"❌ Failed to get profile: {response.status_code} - {response.text}")
                return None
                
        except Exception as e:
            logger.error(f"❌ Error getting user profile: {e}")
            return None
    
    def test_linkedin_connection(self) -> bool:
        """Test LinkedIn API connection"""
        print("🧪 Testing LinkedIn API Connection...")
        
        # Get stored token
        token_record = self.get_stored_token()
        if not token_record:
            print("❌ No valid access token found")
            print("Run the OAuth flow first to obtain an access token")
            return False
        
        # Test profile access
        profile = self.get_user_profile(token_record['access_token'])
        if profile:
            print(f"✅ LinkedIn connection successful!")
            print(f"   User: {profile.get('name', 'Unknown')}")
            print(f"   Email: {profile.get('email', 'Unknown')}")
            print(f"   LinkedIn ID: {profile.get('sub', 'Unknown')}")
            return True
        else:
            print("❌ LinkedIn connection failed")
            return False
    
    def create_text_post(self, text: str, access_token: str = None) -> bool:
        """Create a text post on LinkedIn"""
        try:
            if not access_token:
                token_record = self.get_stored_token()
                if not token_record:
                    logger.error("❌ No access token available")
                    return False
                access_token = token_record['access_token']
            
            # Get user profile for author ID
            profile = self.get_user_profile(access_token)
            if not profile:
                logger.error("❌ Cannot get user profile for posting")
                return False
            
            author_id = profile['sub']
            
            # Create post data
            post_data = {
                "author": f"urn:li:person:{author_id}",
                "lifecycleState": "PUBLISHED",
                "specificContent": {
                    "com.linkedin.ugc.ShareContent": {
                        "shareCommentary": {
                            "text": text
                        },
                        "shareMediaCategory": "NONE"
                    }
                },
                "visibility": {
                    "com.linkedin.ugc.MemberNetworkVisibility": "PUBLIC"
                }
            }
            
            headers = {
                'Authorization': f'Bearer {access_token}',
                'Content-Type': 'application/json',
                'X-Restli-Protocol-Version': '2.0.0'
            }
            
            response = requests.post(self.posts_url, json=post_data, headers=headers)
            
            if response.status_code == 201:
                post_id = response.headers.get('x-restli-id')
                logger.info(f"✅ Post created successfully: {post_id}")
                return True
            else:
                logger.error(f"❌ Post creation failed: {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            logger.error(f"❌ Error creating post: {e}")
            return False

def generate_linkedin_oauth_url():
    """Generate LinkedIn OAuth authorization URL for production"""
    
    # Production LinkedIn App Configuration
    client_id = "78wmrhdd99ssbi"
    redirect_uri = "https://mybookshelf.shop/api/linkedin-callback"  # Updated to new API endpoint
    scope = "openid profile w_member_social email rw_organization_admin"
    state = "mybookshelf_production_oauth"
    
    # LinkedIn OAuth 2.0 endpoint
    auth_url = "https://www.linkedin.com/oauth/v2/authorization"
    
    # Build OAuth parameters
    params = {
        'response_type': 'code',
        'client_id': client_id,
        'redirect_uri': redirect_uri,
        'state': state,
        'scope': scope
    }
    
    # Generate full authorization URL
    oauth_url = f"{auth_url}?{urlencode(params)}"
    
    return {
        'oauth_url': oauth_url,
        'client_id': client_id,
        'redirect_uri': redirect_uri,
        'scope': scope,
        'state': state
    }

def main():
    """Main function to generate and display OAuth URL"""
    print("🔗 LinkedIn OAuth Production Configuration")
    print("=" * 50)
    
    config = generate_linkedin_oauth_url()
    
    print(f"📱 Client ID: {config['client_id']}")
    print(f"🔄 Redirect URI: {config['redirect_uri']}")
    print(f"🔐 Scope: {config['scope']}")
    print(f"🔒 State: {config['state']}")
    print()
    print("🚀 OAuth Authorization URL:")
    print("-" * 30)
    print(config['oauth_url'])
    print()
    print("📋 Instructions:")
    print("1. Copy the OAuth URL above")
    print("2. Open it in your browser") 
    print("3. Authorize the LinkedIn app")
    print("4. You'll be redirected to the callback endpoint")
    print("5. The serverless function will handle token exchange")
    print()
    print("🔧 LinkedIn App Redirect URI should be set to:")
    print(f"   {config['redirect_uri']}")

if __name__ == "__main__":
    main()
