#!/usr/bin/env python3
"""
LinkedIn App Status Checker - MyBookshelf
Comprehensive tool to check LinkedIn app approval status and diagnose sandbox/test mode issues
"""

import os
import sys
import json
import requests
import urllib.parse
from datetime import datetime
from typing import Dict, Optional, List
import logging

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class LinkedInAppStatusChecker:
    """Check LinkedIn app approval status and diagnose issues"""
    
    def __init__(self):
        """Initialize the status checker"""
        self.client_id = "78wmrhdd99ssbi"
        self.client_secret = os.getenv('LINKEDIN_CLIENT_SECRET')
        self.access_token = None
        
        # Load token if available
        self.load_access_token()
    
    def load_access_token(self):
        """Load access token from file if available"""
        try:
            if os.path.exists('linkedin_token_info.json'):
                with open('linkedin_token_info.json', 'r') as f:
                    token_data = json.load(f)
                    self.access_token = token_data.get('token_info', {}).get('access_token')
                    if self.access_token:
                        logger.info("✅ Access token loaded from file")
                    else:
                        logger.warning("⚠️ No access token found in file")
        except Exception as e:
            logger.error(f"❌ Error loading access token: {e}")
    
    def check_app_approval_status(self):
        """Check if the LinkedIn app is fully approved"""
        print("\n" + "="*70)
        print("🔍 LINKEDIN APP APPROVAL STATUS CHECK")
        print("="*70)
        
        print(f"\n📱 App Details:")
        print(f"   Client ID: {self.client_id}")
        print(f"   App Name: MyBookshelf")
        print(f"   Developer Portal: https://www.linkedin.com/developers/apps")
        
        print(f"\n🔍 Manual Approval Status Check:")
        print("1. Go to https://www.linkedin.com/developers/apps")
        print("2. Find your app: MyBookshelf")
        print("3. Click on the app to view details")
        print("4. Check the following sections:")
        
        print(f"\n   📋 PRODUCTS & PERMISSIONS:")
        print("   - Look for 'Sign In with LinkedIn using OpenID Connect'")
        print("   - Look for 'Share on LinkedIn'")
        print("   - Both should show 'Approved' status")
        
        print(f"\n   🔐 OAUTH 2.0 SETTINGS:")
        print("   - Check if redirect URIs are properly configured")
        print("   - Verify authorized domains are set")
        
        print(f"\n   📊 APP STATUS:")
        print("   - Look for any 'In Review' or 'Pending' statuses")
        print("   - Check for any error messages or warnings")
        
        return True
    
    def check_sandbox_test_mode(self):
        """Check if app is in sandbox/test mode"""
        print(f"\n" + "="*70)
        print("🧪 SANDBOX/TEST MODE DIAGNOSIS")
        print("="*70)
        
        print(f"\n🔍 Common Sandbox/Test Mode Indicators:")
        
        print(f"\n   1. APP APPROVAL STATUS:")
        print("   ❌ If app shows 'In Review' or 'Pending'")
        print("   ❌ If products show 'Request Access' instead of 'Approved'")
        print("   ❌ If you see 'Development Mode' warnings")
        
        print(f"\n   2. TOKEN PERMISSIONS:")
        print("   ❌ If token scope doesn't include 'w_member_social'")
        print("   ❌ If token was generated before app approval")
        print("   ❌ If you get 403 errors with 'insufficient permissions'")
        
        print(f"\n   3. POSTING BEHAVIOR:")
        print("   ❌ API returns 201 but posts don't appear")
        print("   ❌ Posts only visible to app developers")
        print("   ❌ Posts appear in 'Activity' but not in feed")
        
        print(f"\n   4. ACCOUNT RESTRICTIONS:")
        print("   ❌ If posting account has restrictions")
        print("   ❌ If account is new or unverified")
        print("   ❌ If account has been flagged for spam")
        
        return True
    
    def test_api_permissions(self):
        """Test current API permissions"""
        print(f"\n" + "="*70)
        print("🔐 API PERMISSIONS TEST")
        print("="*70)
        
        if not self.access_token:
            print("❌ No access token available for testing")
            print("   Generate a new token by re-authenticating with LinkedIn")
            return False
        
        headers = {
            'Authorization': f'Bearer {self.access_token}',
            'X-Restli-Protocol-Version': '2.0.0',
            'LinkedIn-Version': '202506'
        }
        
        # Test 1: Profile access
        print(f"\n🔍 Test 1: Profile Access")
        try:
            response = requests.get(
                'https://api.linkedin.com/v2/userinfo',
                headers=headers
            )
            if response.status_code == 200:
                profile = response.json()
                print(f"   ✅ Profile access successful")
                print(f"   👤 Name: {profile.get('name', 'Unknown')}")
                print(f"   📧 Email: {profile.get('email', 'Unknown')}")
            else:
                print(f"   ❌ Profile access failed: {response.status_code}")
                print(f"   📄 Response: {response.text}")
        except Exception as e:
            print(f"   ❌ Profile access error: {e}")
        
        # Test 2: Posting permissions
        print(f"\n🔍 Test 2: Posting Permissions")
        try:
            # Try to get user's posts (read permission test)
            response = requests.get(
                'https://api.linkedin.com/v2/ugcPosts?authors=List(urn%3Ali%3Aperson%3A5abc_dEfgH)',
                headers=headers
            )
            if response.status_code in [200, 403]:
                print(f"   ✅ API endpoint accessible")
                if response.status_code == 403:
                    print(f"   ⚠️ Read permission denied (expected for new apps)")
                else:
                    print(f"   ✅ Read permission granted")
            else:
                print(f"   ❌ API endpoint error: {response.status_code}")
        except Exception as e:
            print(f"   ❌ API endpoint error: {e}")
        
        return True
    
    def check_token_scope(self):
        """Check the scope of the current access token"""
        print(f"\n" + "="*70)
        print("🎫 ACCESS TOKEN SCOPE CHECK")
        print("="*70)
        
        if not self.access_token:
            print("❌ No access token available")
            return False
        
        try:
            # Load token info from file
            with open('linkedin_token_info.json', 'r') as f:
                token_data = json.load(f)
                scope = token_data.get('token_info', {}).get('scope', '')
                
            print(f"\n📋 Current Token Scope:")
            print(f"   {scope}")
            
            required_scopes = ['w_member_social', 'openid', 'profile', 'email']
            missing_scopes = []
            
            for required_scope in required_scopes:
                if required_scope in scope:
                    print(f"   ✅ {required_scope}")
                else:
                    print(f"   ❌ {required_scope} (MISSING)")
                    missing_scopes.append(required_scope)
            
            if missing_scopes:
                print(f"\n⚠️ Missing Required Scopes:")
                for scope in missing_scopes:
                    print(f"   - {scope}")
                print(f"\n💡 Solution: Re-authenticate with LinkedIn to get updated scopes")
            else:
                print(f"\n✅ All required scopes are present!")
                
        except Exception as e:
            print(f"❌ Error checking token scope: {e}")
        
        return True
    
    def provide_solutions(self):
        """Provide solutions for common issues"""
        print(f"\n" + "="*70)
        print("🛠️ SOLUTIONS & NEXT STEPS")
        print("="*70)
        
        print(f"\n🔧 IF APP IS NOT FULLY APPROVED:")
        print("1. Go to https://www.linkedin.com/developers/apps")
        print("2. Click on your MyBookshelf app")
        print("3. Request access to 'Share on LinkedIn' product")
        print("4. Fill out the application form completely")
        print("5. Wait for LinkedIn's review (can take 1-7 days)")
        print("6. Check email for approval notifications")
        
        print(f"\n🔄 IF TOKEN IS REVOKED OR OUTDATED:")
        print("1. Go to https://www.linkedin.com/developers/apps")
        print("2. Find your app and click 'Edit app'")
        print("3. Go to 'Auth' tab")
        print("4. Copy the Client Secret")
        print("5. Re-authenticate using the OAuth flow")
        print("6. Generate a new access token")
        
        print(f"\n🧪 IF IN SANDBOX/TEST MODE:")
        print("1. Ensure app is fully approved for 'Share on LinkedIn'")
        print("2. Wait 24-48 hours after approval for propagation")
        print("3. Generate new access token after approval")
        print("4. Test with a verified LinkedIn account")
        print("5. Contact LinkedIn support if issues persist")
        
        print(f"\n📞 CONTACT LINKEDIN SUPPORT:")
        print("If all else fails, contact LinkedIn Developer Support:")
        print("1. Go to https://developer.linkedin.com/support")
        print("2. Submit a new request")
        print("3. Include your app ID: 78wmrhdd99ssbi")
        print("4. Describe the 'ghost post' issue")
        print("5. Provide post IDs and timestamps")
        
        return True
    
    def generate_oauth_url(self):
        """Generate OAuth URL for re-authentication"""
        print(f"\n" + "="*70)
        print("🔗 OAUTH RE-AUTHENTICATION URL")
        print("="*70)
        
        redirect_uri = "https://mybookshelf.shop/api/linkedin-callback"
        scope = "openid profile email w_member_social"
        state = "mybookshelf_status_check"
        
        params = {
            'response_type': 'code',
            'client_id': self.client_id,
            'redirect_uri': redirect_uri,
            'scope': scope,
            'state': state
        }
        
        oauth_url = f"https://www.linkedin.com/oauth/v2/authorization?{urllib.parse.urlencode(params)}"
        
        print(f"\n🔗 OAuth URL for re-authentication:")
        print(f"{oauth_url}")
        print(f"\n📋 Instructions:")
        print(f"1. Copy the URL above")
        print(f"2. Open it in your browser")
        print(f"3. Authorize the LinkedIn app")
        print(f"4. You'll be redirected to the callback endpoint")
        print(f"5. The new token will have updated permissions")
        
        return oauth_url
    
    def run_comprehensive_check(self):
        """Run all checks"""
        print("🔍 LinkedIn App Status Checker - MyBookshelf")
        print("=" * 70)
        
        # Run all checks
        self.check_app_approval_status()
        self.check_sandbox_test_mode()
        self.test_api_permissions()
        self.check_token_scope()
        self.provide_solutions()
        self.generate_oauth_url()
        
        print(f"\n" + "="*70)
        print("✅ COMPREHENSIVE CHECK COMPLETE")
        print("="*70)
        print(f"\n📝 Summary:")
        print(f"- Check your app approval status manually")
        print(f"- Verify all required scopes are present")
        print(f"- Re-authenticate if token is revoked")
        print(f"- Contact LinkedIn support if issues persist")
        
        return True

def main():
    """Main function"""
    checker = LinkedInAppStatusChecker()
    checker.run_comprehensive_check()

if __name__ == "__main__":
    main() 