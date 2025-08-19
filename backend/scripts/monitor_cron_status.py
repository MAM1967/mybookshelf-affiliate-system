#!/usr/bin/env python3
"""
Cron Job Status Monitor
Monitors price update activity and alerts on cron job issues
"""

import os
import sys
import json
import requests
from datetime import datetime, timedelta
from supabase import create_client, Client

# Add the parent directory to the path to import config
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import Config

def check_recent_price_updates(hours_back=24):
    """Check for recent price updates in the database"""
    try:
        supabase: Client = create_client(Config.SUPABASE_URL, Config.SUPABASE_ANON_KEY)
        
        # Calculate cutoff time
        cutoff_time = datetime.now() - timedelta(hours=hours_back)
        cutoff_str = cutoff_time.isoformat()
        
        # Query for recent price updates
        response = supabase.table('books_accessories').select(
            'id, title, price, price_updated_at, price_status'
        ).gte('price_updated_at', cutoff_str).order('price_updated_at', desc=True).execute()
        
        if response.data:
            print(f"✅ Found {len(response.data)} price updates in the last {hours_back} hours:")
            for item in response.data[:5]:  # Show first 5
                updated_at = item.get('price_updated_at', 'Unknown')
                title = item.get('title', 'Unknown Title')
                price = item.get('price', 0)
                status = item.get('price_status', 'unknown')
                print(f"   - {title}: ${price} ({status}) - {updated_at}")
            return True, len(response.data)
        else:
            print(f"❌ No price updates found in the last {hours_back} hours")
            return False, 0
            
    except Exception as e:
        print(f"❌ Error checking price updates: {e}")
        return False, 0

def test_api_endpoint():
    """Test the price updater API endpoint"""
    try:
        url = "https://mybookshelf-affiliate-system.vercel.app/api/price-updater"
        headers = {
            "User-Agent": "cron-monitor/1.0",
            "Accept": "application/json"
        }
        
        print("🔍 Testing price updater API endpoint...")
        response = requests.get(url, headers=headers, timeout=30)
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ API endpoint working - Status: {data.get('success', 'Unknown')}")
            print(f"   Message: {data.get('message', 'No message')}")
            
            stats = data.get('stats', {})
            if stats:
                print(f"   Items processed: {stats.get('processedItems', 0)}")
                print(f"   Successful updates: {stats.get('successfulUpdates', 0)}")
                print(f"   Failed updates: {stats.get('failedUpdates', 0)}")
            
            return True
        else:
            print(f"❌ API endpoint returned status {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Error testing API endpoint: {e}")
        return False

def check_github_actions_status():
    """Check GitHub Actions workflow status (if accessible)"""
    try:
        # This would require GitHub API access
        print("🔍 GitHub Actions status check not available (requires API access)")
        return False
    except Exception as e:
        print(f"❌ Error checking GitHub Actions: {e}")
        return False

def generate_status_report():
    """Generate a comprehensive status report"""
    print("=" * 60)
    print("🕐 CRON JOB STATUS REPORT")
    print(f"📅 Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S UTC')}")
    print("=" * 60)
    
    # Check recent price updates
    print("\n📊 PRICE UPDATE STATUS:")
    has_updates, update_count = check_recent_price_updates(24)
    
    # Test API endpoint
    print("\n🔌 API ENDPOINT STATUS:")
    api_working = test_api_endpoint()
    
    # Check GitHub Actions
    print("\n⚙️ GITHUB ACTIONS STATUS:")
    github_working = check_github_actions_status()
    
    # Generate summary
    print("\n" + "=" * 60)
    print("📋 SUMMARY:")
    
    if has_updates:
        print(f"✅ Price updates: {update_count} in last 24 hours")
    else:
        print("❌ No recent price updates detected")
    
    if api_working:
        print("✅ API endpoint: Working")
    else:
        print("❌ API endpoint: Not working")
    
    if github_working:
        print("✅ GitHub Actions: Working")
    else:
        print("❌ GitHub Actions: Status unknown")
    
    # Recommendations
    print("\n💡 RECOMMENDATIONS:")
    
    if not has_updates:
        print("   - Cron job may not be running")
        print("   - Consider setting up external cron service")
        print("   - Check GitHub Actions repository settings")
    
    if not api_working:
        print("   - API endpoint needs investigation")
        print("   - Check Vercel deployment status")
    
    print("=" * 60)

def main():
    """Main function"""
    if len(sys.argv) > 1 and sys.argv[1] == "--help":
        print("Cron Job Status Monitor")
        print("Usage: python monitor_cron_status.py [--help]")
        print("Options:")
        print("  --help    Show this help message")
        return
    
    generate_status_report()

if __name__ == "__main__":
    main()
