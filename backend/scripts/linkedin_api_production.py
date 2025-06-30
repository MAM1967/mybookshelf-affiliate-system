#!/usr/bin/env python3
"""
LinkedIn API Integration for MyBookshelf Production
Handles token exchange, storage, and posting automation
"""

import os
import sys
import json
import requests
import urllib.parse
from datetime import datetime, timedelta
from typing import Dict, Optional, List
import logging

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
        
        # Initialize Supabase for token storage
        if Config.SUPABASE_URL and Config.SUPABASE_ANON_KEY:
            self.supabase: Client = create_client(Config.SUPABASE_URL, Config.SUPABASE_ANON_KEY)
        else:
            raise ValueError("Missing Supabase configuration")
        
        # LinkedIn API endpoints
        self.auth_url = 'https://www.linkedin.com/oauth/v2/authorization'
        self.token_url = 'https://www.linkedin.com/oauth/v2/accessToken'
        self.profile_url = 'https://api.linkedin.com/v2/userinfo'
        self.posts_url = 'https://api.linkedin.com/v2/ugcPosts'
        
        # Required scopes
        self.scopes = ['openid', 'profile', 'w_member_social', 'email']
    
    def get_authorization_url(self, state: Optional[str] = None) -> str:
        """Generate LinkedIn authorization URL"""
        if not state:
            state = f"mybookshelf_{int(datetime.now().timestamp())}"
        
        params = {
            'response_type': 'code',
            'client_id': self.client_id,
            'redirect_uri': self.redirect_uri,
            'state': state,
            'scope': ' '.join(self.scopes)
        }
        
        auth_url = f"{self.auth_url}?{urllib.parse.urlencode(params)}"
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

def main():
    """Main function for testing and setup"""
    import argparse
    
    parser = argparse.ArgumentParser(description='LinkedIn API Production Integration')
    parser.add_argument('--auth-url', action='store_true', help='Generate authorization URL')
    parser.add_argument('--exchange-token', help='Exchange authorization code for token')
    parser.add_argument('--test-connection', action='store_true', help='Test stored token')
    parser.add_argument('--test-post', help='Create a test post with given text')
    
    args = parser.parse_args()
    
    linkedin = LinkedInAPIProduction()
    
    if args.auth_url:
        auth_url = linkedin.get_authorization_url()
        print(f"🔗 Open this URL to authorize LinkedIn access:")
        print(f"   {auth_url}")
    
    elif args.exchange_token:
        token_info = linkedin.exchange_code_for_token(args.exchange_token)
        if token_info:
            if linkedin.store_access_token(token_info):
                print("✅ Token exchange and storage successful!")
            else:
                print("❌ Token storage failed")
        else:
            print("❌ Token exchange failed")
    
    elif args.test_connection:
        success = linkedin.test_linkedin_connection()
        sys.exit(0 if success else 1)
    
    elif args.test_post:
        success = linkedin.create_text_post(args.test_post)
        if success:
            print("✅ Test post created successfully!")
        else:
            print("❌ Test post failed")
        sys.exit(0 if success else 1)
    
    else:
        print("Use --help to see available options")

if __name__ == "__main__":
    main()
