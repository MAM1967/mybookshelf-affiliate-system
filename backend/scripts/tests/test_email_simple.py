#!/usr/bin/env python3
"""
Simplified Email Integration Test for MyBookshelf Affiliate System
Tests only the core Resend email service functionality
"""

import os
import sys
from datetime import datetime

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Setup email environment variables
os.environ['RESEND_API_KEY'] = 're_CujkiY4j_B4SLnmAJFoxvPVFLuQ51xVJJ'
os.environ['RESEND_FROM_EMAIL'] = 'admin@mybookshelf.shop'
os.environ['RESEND_FROM_NAME'] = 'MyBookshelf Admin'
os.environ['ADMIN_EMAIL'] = 'mcddsl@icloud.com'

# Mock Supabase config to avoid database dependencies
os.environ['SUPABASE_URL'] = 'https://mock.supabase.co'
os.environ['SUPABASE_ANON_KEY'] = 'mock_key'

import requests
import logging

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class SimpleEmailTest:
    """Test core email functionality only"""
    
    def __init__(self):
        self.api_key = os.getenv('RESEND_API_KEY')
        self.from_email = os.getenv('RESEND_FROM_EMAIL')
        self.admin_email = os.getenv('ADMIN_EMAIL')
        self.api_base = "https://api.resend.com"
    
    def test_resend_api_directly(self) -> bool:
        """Test Resend API directly with curl-equivalent request"""
        print("🔧 Testing Resend API Direct Connection...")
        
        try:
            headers = {
                'Authorization': f'Bearer {self.api_key}',
                'Content-Type': 'application/json'
            }
            
            email_data = {
                'from': f'MyBookshelf Admin <{self.from_email}>',
                'to': [self.admin_email],
                'subject': '🧪 MyBookshelf Email Test - SUCCESS!',
                'html': f'''
                <!DOCTYPE html>
                <html>
                <head><meta charset="utf-8"><title>Email Test</title></head>
                <body style="font-family: Arial, sans-serif; padding: 20px;">
                    <h1 style="color: #2563eb;">✅ Email Service Working!</h1>
                    <p>Your MyBookshelf email integration is working correctly.</p>
                    <div style="background: #f0f9ff; padding: 15px; border-radius: 6px; margin: 20px 0;">
                        <h3>Test Results:</h3>
                        <ul>
                            <li>Resend API connection: ✅ Working</li>
                            <li>Email delivery: ✅ Successful</li>
                            <li>Domain authentication: ✅ Configured</li>
                        </ul>
                    </div>
                    <p><strong>Test Time:</strong> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
                </body>
                </html>
                '''
            }
            
            response = requests.post(
                f'{self.api_base}/emails',
                headers=headers,
                json=email_data,
                timeout=10
            )
            
            if response.status_code == 200:
                email_id = response.json().get('id')
                print("✅ Resend API test successful!")
                print(f"   Email ID: {email_id}")
                print(f"   To: {self.admin_email}")
                print(f"   Status: Email sent successfully")
                return True
            else:
                print(f"❌ Resend API test failed: {response.status_code}")
                print(f"   Response: {response.text}")
                return False
                
        except Exception as e:
            print(f"❌ Resend API test error: {e}")
            return False
    
    def test_configuration(self) -> bool:
        """Test email configuration"""
        print("🔧 Testing Email Configuration...")
        
        if not self.api_key:
            print("❌ RESEND_API_KEY not set")
            return False
        
        if not self.admin_email:
            print("❌ ADMIN_EMAIL not set")
            return False
        
        print("✅ Email configuration valid")
        print(f"   API Key: {self.api_key[:15]}...")
        print(f"   From Email: {self.from_email}")
        print(f"   Admin Email: {self.admin_email}")
        return True

def main():
    """Run simplified email tests"""
    print("🧪 MyBookshelf Simplified Email Test")
    print("=" * 50)
    
    tester = SimpleEmailTest()
    
    # Test configuration
    config_ok = tester.test_configuration()
    if not config_ok:
        print("\n❌ Configuration test failed")
        return False
    
    # Test direct API
    api_ok = tester.test_resend_api_directly()
    if not api_ok:
        print("\n❌ API test failed")
        return False
    
    print("\n✅ All email tests passed!")
    print("📧 Check your inbox for the test email")
    return True

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1) 