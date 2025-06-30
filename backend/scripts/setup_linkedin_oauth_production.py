#!/usr/bin/env python3
"""
LinkedIn OAuth Production Setup for MyBookshelf Affiliate System
Configures LinkedIn app for production posting automation
"""

import os
import sys
import json
import requests
import urllib.parse
from datetime import datetime
from typing import Dict, Optional
import logging

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class LinkedInOAuthProductionSetup:
    """Setup LinkedIn OAuth for production use"""
    
    def __init__(self):
        """Initialize LinkedIn OAuth setup"""
        self.project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        self.scripts_dir = os.path.dirname(os.path.abspath(__file__))
        
        # LinkedIn app configuration
        self.linkedin_config = {
            'client_id': '78wmrhdd99ssbi',
            'client_secret': None,  # Will be provided by user
            'production_domain': 'https://mybookshelf.shop',
            'redirect_uris': [
                'https://mybookshelf.shop/admin/linkedin-callback',
                'https://mybookshelf.shop/admin/oauth/linkedin',
                'https://www.mybookshelf.shop/admin/linkedin-callback'
            ],
            'scopes': [
                'openid',
                'profile', 
                'w_member_social',
                'email'
            ]
        }
        
        # LinkedIn API endpoints
        self.linkedin_api = {
            'auth_url': 'https://www.linkedin.com/oauth/v2/authorization',
            'token_url': 'https://www.linkedin.com/oauth/v2/accessToken',
            'profile_url': 'https://api.linkedin.com/v2/userinfo',
            'posts_url': 'https://api.linkedin.com/v2/ugcPosts'
        }
    
    def display_app_configuration_instructions(self):
        """Display LinkedIn app configuration instructions"""
        print("\n" + "="*70)
        print("🔗 LINKEDIN APP PRODUCTION CONFIGURATION")
        print("="*70)
        
        print("\n📱 STEP 1: Update LinkedIn Developer App")
        print("1. Go to https://www.linkedin.com/developers/apps")
        print("2. Find your app: MyBookshelf (Client ID: 78wmrhdd99ssbi)")
        print("3. Click 'Edit app'")
        
        print("\n🔄 STEP 2: Update Redirect URIs")
        print("Go to 'Auth' tab and update 'Authorized redirect URLs for your app':")
        for uri in self.linkedin_config['redirect_uris']:
            print(f"   ➕ {uri}")
        
        print("\n✅ STEP 3: Verify Permissions")
        print("Ensure these scopes are enabled:")
        for scope in self.linkedin_config['scopes']:
            print(f"   ✓ {scope}")
        
        print("\n🌐 STEP 4: Update Authorized Domains")
        print("Add these domains to your app:")
        print("   ➕ mybookshelf.shop")
        print("   ➕ www.mybookshelf.shop")
        
        print("\n🔑 STEP 5: Get Client Secret")
        print("1. Go to 'Auth' tab")
        print("2. Copy the 'Client Secret' value")
        print("3. Save it securely - you'll need it for environment variables")
        
        return True
    
    def create_oauth_handler(self):
        """Create OAuth callback handler for production"""
        oauth_handler_content = '''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>LinkedIn OAuth - MyBookshelf Admin</title>
    <style>
        body {
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
            line-height: 1.6;
            color: #333;
            max-width: 600px;
            margin: 50px auto;
            padding: 20px;
            background: #f5f5f5;
        }
        .container {
            background: white;
            padding: 40px;
            border-radius: 12px;
            box-shadow: 0 4px 20px rgba(0, 0, 0, 0.1);
            text-align: center;
        }
        .success {
            color: #16a34a;
            font-size: 24px;
            margin-bottom: 20px;
        }
        .error {
            color: #dc2626;
            font-size: 24px;
            margin-bottom: 20px;
        }
        .loading {
            color: #2563eb;
            font-size: 18px;
            margin-bottom: 20px;
        }
        .button {
            display: inline-block;
            background: linear-gradient(135deg, #2563eb 0%, #1d4ed8 100%);
            color: white;
            padding: 12px 24px;
            text-decoration: none;
            border-radius: 8px;
            font-weight: 600;
            margin: 10px;
        }
        .button:hover {
            transform: translateY(-1px);
            box-shadow: 0 4px 12px rgba(37, 99, 235, 0.3);
        }
        .code {
            background: #f3f4f6;
            padding: 8px 12px;
            border-radius: 4px;
            font-family: monospace;
            margin: 10px 0;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>🔗 LinkedIn OAuth</h1>
        <div id="status" class="loading">
            🔄 Processing LinkedIn authorization...
        </div>
        <div id="content"></div>
    </div>

    <script>
        // Get URL parameters
        const urlParams = new URLSearchParams(window.location.search);
        const code = urlParams.get('code');
        const error = urlParams.get('error');
        const state = urlParams.get('state');
        
        const statusDiv = document.getElementById('status');
        const contentDiv = document.getElementById('content');
        
        if (error) {
            statusDiv.className = 'error';
            statusDiv.innerHTML = '❌ LinkedIn Authorization Failed';
            contentDiv.innerHTML = `
                <p><strong>Error:</strong> ${error}</p>
                <p><strong>Description:</strong> ${urlParams.get('error_description') || 'Unknown error'}</p>
                <a href="/admin" class="button">Return to Admin Dashboard</a>
            `;
        } else if (code) {
            statusDiv.className = 'loading';
            statusDiv.innerHTML = '🔄 Exchanging authorization code for access token...';
            
            // Store the authorization code
            handleAuthorizationCode(code, state);
        } else {
            statusDiv.className = 'error';
            statusDiv.innerHTML = '❌ No authorization code received';
            contentDiv.innerHTML = `
                <p>The LinkedIn authorization process did not complete properly.</p>
                <a href="/admin" class="button">Return to Admin Dashboard</a>
            `;
        }
        
        async function handleAuthorizationCode(authCode, state) {
            try {
                // Store auth code locally for manual processing
                localStorage.setItem('linkedin_auth_code', authCode);
                localStorage.setItem('linkedin_auth_timestamp', Date.now().toString());
                
                statusDiv.className = 'success';
                statusDiv.innerHTML = '✅ LinkedIn Authorization Successful!';
                
                contentDiv.innerHTML = `
                    <p><strong>Authorization Code Received:</strong></p>
                    <div class="code">${authCode.substring(0, 20)}...</div>
                    
                    <h3>🔧 Next Steps:</h3>
                    <ol style="text-align: left;">
                        <li>Copy the authorization code above</li>
                        <li>Run the token exchange script on your server</li>
                        <li>Store the access token securely</li>
                        <li>Test the LinkedIn posting integration</li>
                    </ol>
                    
                    <h3>🚀 Quick Actions:</h3>
                    <a href="/admin" class="button">Go to Admin Dashboard</a>
                    <button class="button" onclick="copyAuthCode()">Copy Auth Code</button>
                `;
                
            } catch (error) {
                statusDiv.className = 'error';
                statusDiv.innerHTML = '❌ Error processing authorization';
                contentDiv.innerHTML = `
                    <p><strong>Error:</strong> ${error.message}</p>
                    <a href="/admin" class="button">Return to Admin Dashboard</a>
                `;
            }
        }
        
        function copyAuthCode() {
            const authCode = localStorage.getItem('linkedin_auth_code');
            if (authCode) {
                navigator.clipboard.writeText(authCode).then(() => {
                    alert('Authorization code copied to clipboard!');
                });
            }
        }
    </script>
</body>
</html>'''
        
        oauth_file_path = os.path.join(self.project_root, 'frontend', 'mini-app', 'linkedin-callback.html')
        
        # Ensure directory exists
        os.makedirs(os.path.dirname(oauth_file_path), exist_ok=True)
        
        with open(oauth_file_path, 'w') as f:
            f.write(oauth_handler_content)
        
        print(f"✅ Created OAuth callback handler: {oauth_file_path}")
    
    def create_linkedin_integration_script(self):
        """Create LinkedIn API integration script"""
        integration_script_content = '''#!/usr/bin/env python3
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
    from supabase import create_client, Client
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
        self.redirect_uri = os.getenv('LINKEDIN_REDIRECT_URI', 'https://mybookshelf.shop/admin/linkedin-callback')
        
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
    
    def get_authorization_url(self, state: str = None) -> str:
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
'''
        
        integration_script_path = os.path.join(self.scripts_dir, 'linkedin_api_production.py')
        with open(integration_script_path, 'w') as f:
            f.write(integration_script_content)
        
        # Make executable
        os.chmod(integration_script_path, 0o755)
        print(f"✅ Created LinkedIn integration script: {integration_script_path}")
    
    def create_linkedin_tokens_table_schema(self):
        """Create SQL schema for LinkedIn tokens storage"""
        schema_content = '''-- LinkedIn Tokens Storage Table
-- Add this to your Supabase database

CREATE TABLE linkedin_tokens (
    id SERIAL PRIMARY KEY,
    admin_email TEXT UNIQUE NOT NULL,
    access_token TEXT NOT NULL,
    token_type TEXT DEFAULT 'Bearer',
    expires_at TIMESTAMP NOT NULL,
    scope TEXT,
    
    -- LinkedIn user info
    linkedin_user_id TEXT,
    linkedin_name TEXT,
    linkedin_email TEXT,
    
    -- Metadata
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    is_active BOOLEAN DEFAULT TRUE,
    
    -- Usage tracking
    last_used_at TIMESTAMP,
    posts_count INTEGER DEFAULT 0
);

-- Create index for performance
CREATE INDEX idx_linkedin_tokens_email ON linkedin_tokens(admin_email);
CREATE INDEX idx_linkedin_tokens_active ON linkedin_tokens(is_active);

-- Function to update timestamp on token updates
CREATE OR REPLACE FUNCTION update_linkedin_token_timestamp()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Trigger for automatic timestamp updates
CREATE TRIGGER linkedin_tokens_updated_at
    BEFORE UPDATE ON linkedin_tokens
    FOR EACH ROW
    EXECUTE FUNCTION update_linkedin_token_timestamp();
'''
        
        schema_file_path = os.path.join(self.project_root, 'backend', 'supabase', 'linkedin_tokens_schema.sql')
        with open(schema_file_path, 'w') as f:
            f.write(schema_content)
        
        print(f"✅ Created LinkedIn tokens schema: {schema_file_path}")
    
    def create_test_oauth_flow_script(self):
        """Create test script for OAuth flow"""
        test_script_content = '''#!/usr/bin/env python3
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
        print("\\n🔗 Step 1: Generating authorization URL...")
        auth_url = linkedin.get_authorization_url()
        
        print(f"✅ Authorization URL generated:")
        print(f"   {auth_url}")
        
        # Step 2: Open browser for user authorization
        print("\\n🌐 Step 2: Opening browser for authorization...")
        try:
            webbrowser.open(auth_url)
            print("✅ Browser opened successfully")
        except Exception as e:
            print(f"⚠️ Could not open browser: {e}")
            print("Please manually open the URL above")
        
        # Step 3: Wait for user to complete authorization
        print("\\n⏳ Step 3: Complete authorization in browser...")
        print("After authorizing, copy the authorization code from the callback page")
        
        auth_code = input("\\nPaste the authorization code here: ").strip()
        
        if not auth_code:
            print("❌ No authorization code provided")
            return False
        
        # Step 4: Exchange code for token
        print("\\n🔄 Step 4: Exchanging code for access token...")
        token_info = linkedin.exchange_code_for_token(auth_code)
        
        if not token_info:
            print("❌ Token exchange failed")
            return False
        
        print("✅ Token exchange successful!")
        
        # Step 5: Store token
        print("\\n💾 Step 5: Storing access token...")
        if linkedin.store_access_token(token_info):
            print("✅ Token stored successfully!")
        else:
            print("❌ Token storage failed")
            return False
        
        # Step 6: Test connection
        print("\\n🧪 Step 6: Testing LinkedIn connection...")
        if linkedin.test_linkedin_connection():
            print("✅ LinkedIn connection test successful!")
        else:
            print("❌ LinkedIn connection test failed")
            return False
        
        # Step 7: Create test post
        test_post = input("\\nEnter a test post message (or press Enter to skip): ").strip()
        if test_post:
            print("\\n📝 Step 7: Creating test post...")
            if linkedin.create_text_post(test_post):
                print("✅ Test post created successfully!")
            else:
                print("❌ Test post failed")
                return False
        
        print("\\n🎉 OAuth flow test completed successfully!")
        print("Your LinkedIn integration is ready for production!")
        return True
        
    except Exception as e:
        print(f"❌ OAuth flow test failed: {e}")
        return False

if __name__ == "__main__":
    success = test_oauth_flow()
    sys.exit(0 if success else 1)
'''
        
        test_script_path = os.path.join(self.scripts_dir, 'test_linkedin_oauth_flow.py')
        with open(test_script_path, 'w') as f:
            f.write(test_script_content)
        
        # Make executable
        os.chmod(test_script_path, 0o755)
        print(f"✅ Created OAuth flow test script: {test_script_path}")
    
    def update_vercel_config_for_linkedin(self):
        """Update Vercel configuration to include LinkedIn OAuth routes"""
        vercel_config_path = os.path.join(self.project_root, 'vercel.json')
        
        try:
            with open(vercel_config_path, 'r') as f:
                config = json.load(f)
            
            # Add LinkedIn OAuth routes
            linkedin_routes = [
                {
                    "src": "/admin/linkedin-callback",
                    "dest": "/frontend/mini-app/linkedin-callback.html"
                },
                {
                    "src": "/admin/oauth/linkedin",
                    "dest": "/frontend/mini-app/linkedin-callback.html"
                }
            ]
            
            # Insert at the beginning so they take precedence
            config['routes'] = linkedin_routes + config.get('routes', [])
            
            # Add LinkedIn environment variables
            config['env']['LINKEDIN_CLIENT_SECRET'] = "@linkedin-client-secret"
            config['env']['LINKEDIN_REDIRECT_URI'] = "@linkedin-redirect-uri"
            
            with open(vercel_config_path, 'w') as f:
                json.dump(config, f, indent=2)
            
            print(f"✅ Updated Vercel config with LinkedIn OAuth routes")
            
        except Exception as e:
            print(f"❌ Error updating Vercel config: {e}")
    
    def display_production_setup_instructions(self):
        """Display complete production setup instructions"""
        print("\n" + "="*70)
        print("🚀 LINKEDIN OAUTH PRODUCTION SETUP COMPLETE")
        print("="*70)
        
        print("\n📋 NEXT STEPS:")
        
        print("\n1. 🔗 Update LinkedIn App Configuration:")
        print("   - Go to https://www.linkedin.com/developers/apps")
        print("   - Edit your MyBookshelf app (Client ID: 78wmrhdd99ssbi)")
        print("   - Add redirect URIs:")
        for uri in self.linkedin_config['redirect_uris']:
            print(f"     ➕ {uri}")
        
        print("\n2. 💾 Add LinkedIn Tokens Table to Database:")
        print("   - Open Supabase SQL Editor")
        print("   - Run the schema in: backend/supabase/linkedin_tokens_schema.sql")
        
        print("\n3. 🔑 Configure Environment Variables:")
        print("   - Add to production environment:")
        print("     LINKEDIN_CLIENT_SECRET=your-linkedin-client-secret")
        print("     LINKEDIN_REDIRECT_URI=https://mybookshelf.shop/admin/linkedin-callback")
        
        print("\n4. 🧪 Test OAuth Flow:")
        print("   - Run: python3 test_linkedin_oauth_flow.py")
        print("   - Complete authorization in browser")
        print("   - Verify token storage and posting")
        
        print("\n5. 🌐 Deploy Frontend Changes:")
        print("   - Commit linkedin-callback.html to repository")
        print("   - Deploy to Vercel (automatic via GitHub)")
        print("   - Verify OAuth callback page loads")
        
        print("\n6. 🤖 Integrate with Automation:")
        print("   - Update LinkedIn automation scripts")
        print("   - Test automated posting workflow")
        print("   - Schedule Tuesday/Wednesday/Thursday posts")
        
        print("\n💡 Quick Commands:")
        print("   Generate auth URL: python3 linkedin_api_production.py --auth-url")
        print("   Exchange token: python3 linkedin_api_production.py --exchange-token CODE")
        print("   Test connection: python3 linkedin_api_production.py --test-connection")
        print("   Test post: python3 linkedin_api_production.py --test-post 'Hello World!'")
    
    def run_setup(self):
        """Run the complete LinkedIn OAuth production setup"""
        print("🔗 MyBookshelf LinkedIn OAuth Production Setup")
        print("=" * 50)
        print(f"📅 Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        # Display app configuration instructions
        self.display_app_configuration_instructions()
        
        # Create production files
        print("\n🛠️  Creating LinkedIn Production Files...")
        self.create_oauth_handler()
        self.create_linkedin_integration_script()
        self.create_linkedin_tokens_table_schema()
        self.create_test_oauth_flow_script()
        self.update_vercel_config_for_linkedin()
        
        # Display next steps
        self.display_production_setup_instructions()
        
        print("\n✅ LinkedIn OAuth production setup complete!")
        print("🔗 Follow the instructions above to complete the integration")

def main():
    """Main setup execution"""
    setup = LinkedInOAuthProductionSetup()
    setup.run_setup()

if __name__ == "__main__":
    main() 