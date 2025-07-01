#!/usr/bin/env python3
"""
Find MyBookshelf Organization ID and Test Organization Posting
Helps identify the correct organization ID and posting approach
"""

import os
import requests
import json
from supabase.client import create_client
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import Config

def find_organization_id():
    """Find the correct organization ID for MyBookshelf"""
    print("🔍 Finding MyBookshelf Organization ID...")
    
    # Initialize Supabase
    supabase = create_client(Config.SUPABASE_URL, Config.SUPABASE_ANON_KEY)
    
    # Get the current token
    result = supabase.table('linkedin_tokens').select('*').eq('is_active', True).execute()
    if not result.data:
        print("❌ No active LinkedIn token found")
        return None
    
    token = result.data[0]
    access_token = token['access_token']
    
    headers = {
        'Authorization': f'Bearer {access_token}',
        'Content-Type': 'application/json',
        'X-Restli-Protocol-Version': '2.0.0'
    }
    
    # Method 1: Try to get user's organizations
    print("\n📋 Method 1: Getting user's organizations...")
    try:
        response = requests.get(
            'https://api.linkedin.com/v2/organizationalEntityAcls?q=roleAssignee',
            headers=headers
        )
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            orgs = response.json()
            print("✅ Organizations found:")
            for org in orgs.get('elements', []):
                org_id = org.get('organizationalTarget', {}).get('~', {}).get('id')
                org_name = org.get('organizationalTarget', {}).get('~', {}).get('localizedName')
                role = org.get('role')
                print(f"   - ID: {org_id}, Name: {org_name}, Role: {role}")
        else:
            print(f"Response: {response.text}")
    except Exception as e:
        print(f"Error: {e}")
    
    # Method 2: Try to get company pages
    print("\n📋 Method 2: Getting company pages...")
    try:
        response = requests.get(
            'https://api.linkedin.com/v2/organizations?q=roleAssignee',
            headers=headers
        )
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            companies = response.json()
            print("✅ Companies found:")
            for company in companies.get('elements', []):
                company_id = company.get('id')
                company_name = company.get('localizedName')
                print(f"   - ID: {company_id}, Name: {company_name}")
        else:
            print(f"Response: {response.text}")
    except Exception as e:
        print(f"Error: {e}")
    
    # Method 3: Try to get user's profile to see if they're associated with MyBookshelf
    print("\n📋 Method 3: Getting user profile...")
    try:
        response = requests.get(
            'https://api.linkedin.com/v2/userinfo',
            headers=headers
        )
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            profile = response.json()
            print(f"✅ User: {profile.get('name')}")
            print(f"   Email: {profile.get('email')}")
            print(f"   ID: {profile.get('sub')}")
        else:
            print(f"Response: {response.text}")
    except Exception as e:
        print(f"Error: {e}")

def test_organization_posting(org_id):
    """Test posting as an organization"""
    print(f"\n🧪 Testing organization posting with ID: {org_id}")
    
    # Initialize Supabase
    supabase = create_client(Config.SUPABASE_URL, Config.SUPABASE_ANON_KEY)
    
    # Get the current token
    result = supabase.table('linkedin_tokens').select('*').eq('is_active', True).execute()
    if not result.data:
        print("❌ No active LinkedIn token found")
        return False
    
    token = result.data[0]
    access_token = token['access_token']
    
    headers = {
        'Authorization': f'Bearer {access_token}',
        'Content-Type': 'application/json',
        'X-Restli-Protocol-Version': '2.0.0'
    }
    
    # Test post data
    test_post = {
        "author": f"urn:li:organization:{org_id}",
        "lifecycleState": "PUBLISHED",
        "specificContent": {
            "com.linkedin.ugc.ShareContent": {
                "shareCommentary": {
                    "text": "🧪 Test post from MyBookshelf automation system"
                },
                "shareMediaCategory": "NONE"
            }
        },
        "visibility": {
            "com.linkedin.ugc.MemberNetworkVisibility": "PUBLIC"
        }
    }
    
    try:
        response = requests.post(
            'https://api.linkedin.com/v2/ugcPosts',
            headers=headers,
            json=test_post,
            timeout=30
        )
        
        print(f"Status: {response.status_code}")
        print(f"Response: {response.text}")
        
        if response.status_code == 201:
            print("✅ Organization posting successful!")
            return True
        else:
            print("❌ Organization posting failed")
            return False
            
    except Exception as e:
        print(f"Error: {e}")
        return False

def main():
    """Main function"""
    print("🔗 MyBookshelf Organization ID Finder")
    print("=" * 50)
    
    # Find organization ID
    find_organization_id()
    
    # Test with different organization IDs
    test_ids = [
        "10198635",  # Current ID in code
        "12345678",  # Example ID
    ]
    
    print(f"\n🧪 Testing organization posting...")
    for org_id in test_ids:
        print(f"\nTesting with organization ID: {org_id}")
        success = test_organization_posting(org_id)
        if success:
            print(f"✅ Found working organization ID: {org_id}")
            break

if __name__ == "__main__":
    main() 