#!/usr/bin/env python3
"""
Test script to verify the cron job endpoint is working
"""

import requests
import json
from datetime import datetime

def test_cron_endpoint():
    """Test the cron job endpoint"""
    
    print(f"🧪 Testing cron job endpoint at {datetime.now()}")
    
    # Test the current endpoint that GitHub Actions is calling
    url = "https://mybookshelf-affiliate-system.vercel.app/api/price-updater-amazon-api-simple"
    
    try:
        print(f"📡 Calling: {url}")
        
        response = requests.get(
            url,
            headers={
                "User-Agent": "github-actions-cron/1.0",
                "Accept": "application/json"
            },
            timeout=60
        )
        
        print(f"📊 Status Code: {response.status_code}")
        print(f"⏱️ Response Time: {response.elapsed.total_seconds():.2f}s")
        
        if response.status_code == 200:
            try:
                data = response.json()
                print("✅ Endpoint working!")
                print(f"📄 Response: {json.dumps(data, indent=2)}")
                return True
            except json.JSONDecodeError:
                print("⚠️ Response is not valid JSON")
                print(f"📄 Raw response: {response.text}")
                return False
        else:
            print(f"❌ Endpoint failed with status {response.status_code}")
            print(f"📄 Response: {response.text}")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Request failed: {e}")
        return False

def test_email_endpoint():
    """Test the new email reporting endpoint"""
    
    print(f"\n🧪 Testing email reporting endpoint at {datetime.now()}")
    
    # Test the new endpoint with email reporting
    url = "https://mybookshelf-affiliate-system.vercel.app/api/price-updater-with-email-report"
    
    try:
        print(f"📡 Calling: {url}")
        
        response = requests.get(
            url,
            headers={
                "User-Agent": "github-actions-cron/1.0",
                "Accept": "application/json"
            },
            timeout=60
        )
        
        print(f"📊 Status Code: {response.status_code}")
        print(f"⏱️ Response Time: {response.elapsed.total_seconds():.2f}s")
        
        if response.status_code == 200:
            try:
                data = response.json()
                print("✅ Email endpoint working!")
                print(f"📄 Response: {json.dumps(data, indent=2)}")
                return True
            except json.JSONDecodeError:
                print("⚠️ Response is not valid JSON")
                print(f"📄 Raw response: {response.text}")
                return False
        else:
            print(f"❌ Email endpoint failed with status {response.status_code}")
            print(f"📄 Response: {response.text}")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Request failed: {e}")
        return False

if __name__ == "__main__":
    print("🚀 Testing Cron Job Endpoints")
    print("=" * 50)
    
    # Test current endpoint
    current_working = test_cron_endpoint()
    
    # Test new email endpoint
    email_working = test_email_endpoint()
    
    print("\n📊 Summary:")
    print(f"Current endpoint: {'✅ Working' if current_working else '❌ Failed'}")
    print(f"Email endpoint: {'✅ Working' if email_working else '❌ Failed'}")
    
    if current_working and email_working:
        print("\n🎉 Both endpoints are working! Cron job should function properly.")
    elif current_working:
        print("\n⚠️ Only current endpoint works. Email reporting not available yet.")
    else:
        print("\n❌ Endpoints are not working. Cron job will fail.") 