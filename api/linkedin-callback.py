#!/usr/bin/env python3
"""
LinkedIn OAuth Callback Handler - Vercel Serverless Function
Processes LinkedIn OAuth callbacks and completes token exchange
"""

import os
import json
import urllib.parse
import requests
from datetime import datetime, timedelta
from typing import Dict, Optional

# Import Supabase
try:
    from supabase.client import create_client, Client
except ImportError:
    # Fallback if supabase not available
    create_client = None
    Client = None

def get_supabase_client():
    """Get Supabase client"""
    supabase_url = os.getenv('SUPABASE_URL')
    supabase_key = os.getenv('SUPABASE_ANON_KEY')
    
    if not supabase_url or not supabase_key:
        return None
    
    if Client is None or create_client is None:
        return None
    
    return create_client(supabase_url, supabase_key)

def exchange_code_for_token(authorization_code: str) -> Optional[Dict]:
    """Exchange authorization code for LinkedIn access token"""
    
    # LinkedIn OAuth configuration
    client_id = os.getenv('LINKEDIN_CLIENT_ID', '78wmrhdd99ssbi')
    client_secret = os.getenv('LINKEDIN_CLIENT_SECRET')
    redirect_uri = 'https://mybookshelf.shop/api/linkedin-callback'
    
    if not client_secret:
        return None
    
    token_url = 'https://www.linkedin.com/oauth/v2/accessToken'
    
    data = {
        'grant_type': 'authorization_code',
        'code': authorization_code,
        'client_id': client_id,
        'client_secret': client_secret,
        'redirect_uri': redirect_uri
    }
    
    try:
        response = requests.post(token_url, data=data)
        
        if response.status_code == 200:
            token_data = response.json()
            
            # Calculate expiration time
            expires_in = token_data.get('expires_in', 5184000)  # Default 60 days
            expires_at = datetime.now() + timedelta(seconds=expires_in)
            
            token_info = {
                'access_token': token_data['access_token'],
                'expires_in': expires_in,
                'expires_at': expires_at.isoformat(),
                'scope': token_data.get('scope', 'openid profile w_member_social email'),
                'token_type': token_data.get('token_type', 'Bearer'),
                'obtained_at': datetime.now().isoformat()
            }
            
            return token_info
        else:
            return None
            
    except Exception as e:
        return None

def get_user_profile(access_token: str) -> Optional[Dict]:
    """Get LinkedIn user profile"""
    profile_url = 'https://api.linkedin.com/v2/userinfo'
    
    headers = {
        'Authorization': f'Bearer {access_token}',
        'Content-Type': 'application/json'
    }
    
    try:
        response = requests.get(profile_url, headers=headers)
        
        if response.status_code == 200:
            return response.json()
        else:
            return None
            
    except Exception as e:
        return None

def store_access_token(token_info: Dict, profile_info: Dict, admin_email: str = 'mcddsl@icloud.com') -> bool:
    """Store access token in Supabase"""
    
    supabase = get_supabase_client()
    if not supabase:
        return False
    
    try:
        # Store token in database
        token_record = {
            'admin_email': admin_email,
            'access_token': token_info['access_token'],
            'token_type': token_info['token_type'],
            'expires_at': token_info['expires_at'],
            'scope': token_info['scope'],
            'linkedin_user_id': profile_info.get('sub'),
            'linkedin_name': profile_info.get('name'),
            'linkedin_email': profile_info.get('email'),
            'created_at': datetime.now().isoformat(),
            'is_active': True
        }
        
        # Insert or update token
        result = supabase.table('linkedin_tokens').upsert(
            token_record, 
            on_conflict='admin_email'
        ).execute()
        
        return bool(result.data)
        
    except Exception as e:
        return False

def generate_success_html(profile_info: Dict) -> str:
    """Generate success page HTML"""
    return f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>LinkedIn OAuth Success - MyBookshelf</title>
    <style>
        body {{
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
            line-height: 1.6;
            color: #333;
            max-width: 600px;
            margin: 50px auto;
            padding: 20px;
            background: #f5f5f5;
        }}
        .container {{
            background: white;
            padding: 40px;
            border-radius: 12px;
            box-shadow: 0 4px 20px rgba(0, 0, 0, 0.1);
            text-align: center;
        }}
        .success {{
            color: #16a34a;
            font-size: 24px;
            margin-bottom: 20px;
        }}
        .button {{
            display: inline-block;
            background: linear-gradient(135deg, #2563eb 0%, #1d4ed8 100%);
            color: white;
            padding: 12px 24px;
            text-decoration: none;
            border-radius: 8px;
            font-weight: 600;
            margin: 10px;
        }}
        .info {{
            background: #f0f9ff;
            border: 1px solid #0ea5e9;
            border-radius: 8px;
            padding: 20px;
            margin: 20px 0;
            text-align: left;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="success">✅ LinkedIn Authorization Successful!</div>
        
        <div class="info">
            <h3>🎉 Connection Complete!</h3>
            <p><strong>Connected Account:</strong> {profile_info.get('name', 'Unknown')}</p>
            <p><strong>Email:</strong> {profile_info.get('email', 'Unknown')}</p>
            <p><strong>LinkedIn ID:</strong> {profile_info.get('sub', 'Unknown')}</p>
            
            <h4>✅ Next Steps Completed:</h4>
            <ul>
                <li>✅ Authorization code received</li>
                <li>✅ Access token obtained</li>
                <li>✅ User profile retrieved</li>
                <li>✅ Token stored securely in database</li>
            </ul>
        </div>
        
        <p>🚀 Your LinkedIn automation is now ready!</p>
        <a href="/admin" class="button">Go to Admin Dashboard</a>
    </div>
</body>
</html>
    """

def generate_error_html(error_message: str) -> str:
    """Generate error page HTML"""
    return f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>LinkedIn OAuth Error - MyBookshelf</title>
    <style>
        body {{
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
            line-height: 1.6;
            color: #333;
            max-width: 600px;
            margin: 50px auto;
            padding: 20px;
            background: #f5f5f5;
        }}
        .container {{
            background: white;
            padding: 40px;
            border-radius: 12px;
            box-shadow: 0 4px 20px rgba(0, 0, 0, 0.1);
            text-align: center;
        }}
        .error {{
            color: #dc2626;
            font-size: 24px;
            margin-bottom: 20px;
        }}
        .button {{
            display: inline-block;
            background: linear-gradient(135deg, #2563eb 0%, #1d4ed8 100%);
            color: white;
            padding: 12px 24px;
            text-decoration: none;
            border-radius: 8px;
            font-weight: 600;
            margin: 10px;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="error">❌ LinkedIn Authorization Failed</div>
        <p><strong>Error:</strong> {error_message}</p>
        <p>Please try the authorization process again.</p>
        <a href="/admin" class="button">Return to Admin Dashboard</a>
    </div>
</body>
</html>
    """

def handler(request):
    """Vercel serverless function handler"""
    
    # Parse query parameters
    query_params = dict(urllib.parse.parse_qsl(request.query_string.decode('utf-8')))
    
    # Check for OAuth error
    if 'error' in query_params:
        error = query_params.get('error', 'unknown_error')
        error_description = query_params.get('error_description', 'No description provided')
        error_message = f"{error}: {error_description}"
        
        return {
            'statusCode': 400,
            'headers': {'Content-Type': 'text/html'},
            'body': generate_error_html(error_message)
        }
    
    # Get authorization code
    authorization_code = query_params.get('code')
    state = query_params.get('state')
    
    if not authorization_code:
        return {
            'statusCode': 400,
            'headers': {'Content-Type': 'text/html'},
            'body': generate_error_html('No authorization code received')
        }
    
    # Validate state parameter
    if state != 'mybookshelf_production_oauth':
        return {
            'statusCode': 400,
            'headers': {'Content-Type': 'text/html'},
            'body': generate_error_html('Invalid state parameter - possible security issue')
        }
    
    # Exchange code for token
    token_info = exchange_code_for_token(authorization_code)
    if not token_info:
        return {
            'statusCode': 500,
            'headers': {'Content-Type': 'text/html'},
            'body': generate_error_html('Failed to exchange authorization code for access token')
        }
    
    # Get user profile
    profile_info = get_user_profile(token_info['access_token'])
    if not profile_info:
        return {
            'statusCode': 500,
            'headers': {'Content-Type': 'text/html'},
            'body': generate_error_html('Failed to retrieve user profile from LinkedIn')
        }
    
    # Store token in database
    if not store_access_token(token_info, profile_info):
        return {
            'statusCode': 500,
            'headers': {'Content-Type': 'text/html'},
            'body': generate_error_html('Failed to store access token in database')
        }
    
    # Return success page
    return {
        'statusCode': 200,
        'headers': {'Content-Type': 'text/html'},
        'body': generate_success_html(profile_info)
    }

# For Vercel runtime
def main(request):
    return handler(request) 