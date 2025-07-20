#!/usr/bin/env python3
"""
Migrate from Local Cron to Vercel Cron
Helps transition the price update system to run in the cloud
"""

import subprocess
import requests
import os
import sys
from datetime import datetime

def remove_local_cron():
    """Remove the local cron job for price updates"""
    try:
        print("🔍 Checking current crontab...")
        
        # Get current crontab
        try:
            current_cron = subprocess.check_output(['crontab', '-l'], stderr=subprocess.DEVNULL).decode()
        except subprocess.CalledProcessError:
            print("   ℹ️ No existing crontab found")
            return True
        
        # Check for price updater entries
        lines = current_cron.split('\n')
        price_update_lines = [line for line in lines if 'daily_price_updater.py' in line]
        
        if not price_update_lines:
            print("   ✅ No local price update cron jobs found")
            return True
        
        print(f"   📋 Found {len(price_update_lines)} price update cron job(s):")
        for line in price_update_lines:
            print(f"      {line}")
        
        # Ask for confirmation
        response = input("\nRemove local cron job(s)? (y/N): ").strip().lower()
        if response != 'y':
            print("   ⏭️ Keeping local cron jobs")
            return False
        
        # Remove price updater lines
        filtered_lines = [line for line in lines if 'daily_price_updater.py' not in line and line.strip()]
        new_cron = '\n'.join(filtered_lines) + '\n'
        
        # Update crontab
        process = subprocess.Popen(['crontab', '-'], stdin=subprocess.PIPE)
        process.communicate(new_cron.encode())
        
        if process.returncode == 0:
            print("   ✅ Local cron jobs removed successfully")
            return True
        else:
            print("   ❌ Failed to remove local cron jobs")
            return False
            
    except Exception as e:
        print(f"   ❌ Error managing crontab: {e}")
        return False

def test_vercel_endpoint():
    """Test the Vercel API endpoint"""
    print("\n🧪 Testing Vercel API endpoint...")
    
    # Determine the base URL
    if os.path.exists('vercel.json'):
        base_url = "https://mybookshelf.shop"  # Production
    else:
        print("   ⚠️ vercel.json not found - using localhost")
        base_url = "http://localhost:3000"
    
    endpoint_url = f"{base_url}/api/update-prices"
    
    try:
        print(f"   🔗 Testing: {endpoint_url}")
        
        # Make a test request (this will run actual price updates)
        headers = {'Content-Type': 'application/json'}
        
        # Add auth header if CRON_SECRET is set
        cron_secret = os.environ.get('CRON_SECRET')
        if cron_secret:
            headers['Authorization'] = f'Bearer {cron_secret}'
        
        print("   ⏳ Sending request (this may take several minutes)...")
        
        response = requests.post(endpoint_url, headers=headers, timeout=600)
        
        if response.status_code == 200:
            data = response.json()
            print("   ✅ Endpoint test successful!")
            print(f"      • Status: {data.get('message', 'Success')}")
            
            stats = data.get('statistics', {})
            if stats:
                print(f"      • Items Processed: {stats.get('totalItems', 'N/A')}")
                print(f"      • Updated: {stats.get('updatedItems', 'N/A')}")
                print(f"      • Errors: {stats.get('errors', 'N/A')}")
                print(f"      • Execution Time: {stats.get('executionTime', 'N/A')}")
            
            return True
        else:
            print(f"   ❌ Endpoint test failed: {response.status_code}")
            print(f"      Response: {response.text}")
            return False
            
    except requests.exceptions.Timeout:
        print("   ⚠️ Request timed out (this is normal for large updates)")
        print("   💡 Check Vercel logs to see if the update completed")
        return None
    except Exception as e:
        print(f"   ❌ Test failed: {e}")
        return False

def show_deployment_instructions():
    """Show instructions for deploying to Vercel"""
    print("\n📋 VERCEL DEPLOYMENT INSTRUCTIONS")
    print("=" * 50)
    print("1. Deploy the updated code:")
    print("   vercel --prod")
    print()
    print("2. Verify the cron job is configured:")
    print("   - Go to Vercel Dashboard")
    print("   - Open your project")
    print("   - Go to 'Functions' tab")
    print("   - Look for 'Cron Jobs' section")
    print()
    print("3. Monitor execution:")
    print("   - Check 'Functions' tab for logs")
    print("   - Look for '/api/update-prices' executions")
    print()
    print("4. Optional: Set up authentication:")
    print("   - Add CRON_SECRET environment variable")
    print("   - This prevents unauthorized API calls")
    print()

def show_migration_summary():
    """Show summary of the migration"""
    print("\n📊 MIGRATION SUMMARY")
    print("=" * 50)
    print("LOCAL CRON → VERCEL CRON")
    print()
    print("BEFORE (Local):")
    print("   ❌ Runs only when computer is on")
    print("   ❌ Stops if computer sleeps")
    print("   ❌ Limited reliability")
    print()
    print("AFTER (Cloud):")
    print("   ✅ Runs 24/7 in the cloud")
    print("   ✅ Built-in monitoring & logs")
    print("   ✅ Integrated with existing Vercel stack")
    print("   ✅ Enterprise-grade reliability")
    print()
    print("SCHEDULE:")
    print("   🕐 Daily at 1:00 AM UTC")
    print("   📊 Updates all items not checked in 24+ hours")
    print("   📝 Logs all execution details")
    print()

def main():
    """Main migration function"""
    print("🚀 MIGRATE TO VERCEL CRON")
    print("=" * 50)
    print("This will migrate your price updates from local cron to Vercel cron")
    print("for enterprise-grade reliability in the cloud.")
    print()
    
    # Show current status
    print("📋 MIGRATION STEPS:")
    print("1. Remove local cron job")
    print("2. Test Vercel API endpoint")
    print("3. Deploy to production")
    print("4. Verify cloud execution")
    print()
    
    # Ask for confirmation
    response = input("Proceed with migration? (y/N): ").strip().lower()
    if response != 'y':
        print("Migration cancelled.")
        return
    
    print("\n" + "=" * 50)
    
    # Step 1: Remove local cron
    print("STEP 1: Remove Local Cron Job")
    local_removed = remove_local_cron()
    
    # Step 2: Test endpoint (optional)
    print("\nSTEP 2: Test Vercel Endpoint")
    test_response = input("Test the Vercel endpoint now? (y/N): ").strip().lower()
    
    endpoint_works = True
    if test_response == 'y':
        endpoint_works = test_vercel_endpoint()
    else:
        print("   ⏭️ Skipping endpoint test")
    
    # Step 3: Show deployment instructions
    show_deployment_instructions()
    
    # Step 4: Show summary
    show_migration_summary()
    
    print("🎉 Migration preparation complete!")
    print()
    print("NEXT STEPS:")
    if not local_removed:
        print("   ⚠️ Manual cron cleanup needed")
    if endpoint_works is False:
        print("   ⚠️ Fix endpoint issues before deploying")
    print("   🚀 Run: vercel --prod")
    print("   📊 Monitor: Vercel Dashboard > Functions")
    print("   🔍 Test: python3 price_monitoring_dashboard.py")

if __name__ == "__main__":
    main() 