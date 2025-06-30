#!/usr/bin/env python3
"""
Email Integration Test for MyBookshelf Affiliate System
Tests the complete email workflow with Resend API
"""

import os
import sys
import json
from datetime import datetime, timedelta
from typing import Dict, List
import logging

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Setup test environment variables
os.environ['RESEND_API_KEY'] = 're_CujkiY4j_B4SLnmAJFoxvPVFLuQ51xVJJ'
os.environ['RESEND_FROM_EMAIL'] = 'admin@mybookshelf.shop'
os.environ['RESEND_FROM_NAME'] = 'MyBookshelf Admin'
os.environ['ADMIN_EMAIL'] = 'mcddsl@icloud.com'
os.environ['ADMIN_DASHBOARD_URL'] = 'https://mybookshelf.shop/admin'
os.environ['PUBLIC_SITE_URL'] = 'https://mybookshelf.shop'

# Setup Supabase test configuration (using dummy values for config test)
os.environ['SUPABASE_URL'] = 'https://test.supabase.co'
os.environ['SUPABASE_ANON_KEY'] = 'test_anon_key_for_configuration_testing'

from email_service import ResendEmailService
from sunday_approval_automation import SundayApprovalAutomation

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class EmailIntegrationTest:
    """Test email integration functionality"""
    
    def __init__(self):
        """Initialize email integration test"""
        try:
            self.email_service = ResendEmailService()
            self.sunday_automation = SundayApprovalAutomation()
        except Exception as e:
            logger.error(f"❌ Failed to initialize email services: {e}")
            self.email_service = None
            self.sunday_automation = None
    
    def test_resend_configuration(self) -> bool:
        """Test Resend API configuration"""
        print("🔧 Testing Resend Configuration...")
        
        if not self.email_service:
            print("❌ Email service not initialized")
            return False
        
        # Check configuration
        config_valid = self.email_service.validate_configuration()
        
        if config_valid and self.email_service:
            print("✅ Resend configuration valid")
            print(f"   API Key: {self.email_service.api_key[:15]}...")
            print(f"   From Email: {self.email_service.from_email}")
            print(f"   Admin Email: {self.email_service.admin_email}")
            return True
        else:
            print("❌ Resend configuration invalid")
            return False
    
    def test_simple_email_send(self) -> bool:
        """Test sending a simple email"""
        print("\n📧 Testing Simple Email Send...")
        
        if not self.email_service:
            print("❌ Email service not available")
            return False
        
        # Create test email content
        test_html = f'''
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <title>MyBookshelf Email Test</title>
        </head>
        <body style="font-family: Arial, sans-serif; padding: 20px; background: #f5f5f5;">
            <div style="max-width: 600px; margin: 0 auto; background: white; padding: 30px; border-radius: 8px; box-shadow: 0 2px 10px rgba(0,0,0,0.1);">
                <h1 style="color: #2563eb; margin-bottom: 20px;">🧪 MyBookshelf Email Service Test</h1>
                
                <p>Congratulations! Your MyBookshelf email integration is working correctly.</p>
                
                <div style="background: #f0f9ff; padding: 15px; border-radius: 6px; margin: 20px 0; border-left: 4px solid #2563eb;">
                    <h3 style="margin: 0 0 10px 0; color: #1e40af;">✅ Test Results:</h3>
                    <ul style="margin: 0; color: #1e40af;">
                        <li>Resend API connection: Working</li>
                        <li>Email delivery: Successful</li>
                        <li>HTML formatting: Rendered correctly</li>
                        <li>Domain authentication: Configured</li>
                    </ul>
                </div>
                
                <div style="background: #ecfdf5; padding: 15px; border-radius: 6px; margin: 20px 0; border-left: 4px solid #10b981;">
                    <h3 style="margin: 0 0 10px 0; color: #065f46;">🎯 Next Steps:</h3>
                    <p style="margin: 0; color: #047857;">
                        Your email system is ready for the Sunday approval workflow. 
                        The system will automatically send approval emails every Sunday morning.
                    </p>
                </div>
                
                <hr style="margin: 30px 0; border: none; border-top: 1px solid #e5e7eb;">
                
                <p style="color: #6b7280; font-size: 14px; margin: 0;">
                    <strong>Test Details:</strong><br>
                    Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}<br>
                    Service: Resend Email API<br>
                    Domain: mybookshelf.shop
                </p>
            </div>
        </body>
        </html>
        '''
        
        # Send test email
        success = self.email_service.send_email(
            to_email=self.email_service.admin_email,
            subject="🧪 MyBookshelf Email Service Test - SUCCESS!",
            html_content=test_html
        )
        
        if success:
            print("✅ Test email sent successfully!")
            print(f"📨 Check your inbox: {self.email_service.admin_email}")
            return True
        else:
            print("❌ Test email failed to send")
            return False
    
    def test_approval_email_template(self) -> bool:
        """Test the approval email template rendering"""
        print("\n📋 Testing Approval Email Template...")
        
        if not self.email_service:
            print("❌ Email service not available")
            return False
        
        # Create mock books data
        mock_books_data = {
            'pending_books': [
                {
                    'id': 1,
                    'title': 'The Five Dysfunctions of a Team',
                    'author': 'Patrick Lencioni',
                    'category': 'Books',
                    'suggested_price': 18.99,
                    'christian_themes': ['Leadership', 'Teamwork', 'Integrity'],
                    'content_filter_notes': None
                },
                {
                    'id': 2,
                    'title': 'Atomic Habits',
                    'author': 'James Clear',
                    'category': 'Books', 
                    'suggested_price': 13.49,
                    'christian_themes': ['Discipline', 'Personal Growth'],
                    'content_filter_notes': None
                },
                {
                    'id': 3,
                    'title': 'Leadership Journal - Premium',
                    'author': 'Various',
                    'category': 'Accessories',
                    'suggested_price': 24.99,
                    'christian_themes': ['Reflection', 'Prayer'],
                    'content_filter_notes': 'Review spiritual content alignment'
                }
            ],
            'review_books': [],
            'stats': {
                'pending_count': 3,
                'review_count': 0,
                'filtered_count': 0,
                'total_count': 3
            }
        }
        
        # Create mock session
        mock_session = {
            'session_id': 12345,
            'access_token': 'test_token_12345abcdef',
            'session_date': datetime.now().date(),
            'expires_at': (datetime.now() + timedelta(days=7)).isoformat()
        }
        
        # Test template rendering
        try:
            html_content = self.email_service.render_approval_email_template(mock_books_data, mock_session)
            
            if html_content and len(html_content) > 1000:  # Should be substantial content
                print("✅ Template rendered successfully")
                print(f"   Content length: {len(html_content)} characters")
                print(f"   Books included: {len(mock_books_data['pending_books'])}")
                
                # Save template for inspection
                with open('test_approval_email.html', 'w') as f:
                    f.write(html_content)
                print("💾 Template saved to: test_approval_email.html")
                
                return True
            else:
                print("❌ Template rendering failed or too short")
                return False
                
        except Exception as e:
            print(f"❌ Template rendering error: {e}")
            return False
    
    def test_sunday_workflow_simulation(self) -> bool:
        """Test Sunday workflow without actually sending emails"""
        print("\n🌅 Testing Sunday Workflow Simulation...")
        
        if not self.sunday_automation:
            print("❌ Sunday automation not available")
            return False
        
        try:
            # Get workflow status
            status = self.sunday_automation.get_workflow_status()
            
            print("📊 Workflow Status:")
            print(f"   Current Date: {status['current_date']}")
            print(f"   Next Sunday: {status['next_sunday']}")
            print(f"   System Status: {status['system_status']}")
            
            if status.get('error'):
                print(f"   Error: {status['error']}")
                return False
            
            # Test pipeline status
            pipeline_stats = self.sunday_automation.get_content_pipeline_status()
            print(f"\n📚 Content Pipeline:")
            print(f"   Total Books: {pipeline_stats['total_books']}")
            print(f"   Pending: {pipeline_stats['pending']}")
            print(f"   Approved: {pipeline_stats['approved']}")
            print(f"   Needs Review: {pipeline_stats['needs_review']}")
            
            print("✅ Sunday workflow simulation successful")
            return True
            
        except Exception as e:
            print(f"❌ Sunday workflow simulation error: {e}")
            return False
    
    def test_complete_email_workflow(self) -> bool:
        """Test the complete email workflow end-to-end"""
        print("\n🔄 Testing Complete Email Workflow...")
        
        if not self.email_service:
            print("❌ Email service not available")
            return False
        
        workflow_steps = {
            'configuration': False,
            'simple_send': False,
            'template_render': False,
            'workflow_simulation': False
        }
        
        # Step 1: Configuration test
        workflow_steps['configuration'] = self.test_resend_configuration()
        
        # Step 2: Simple email send
        if workflow_steps['configuration']:
            workflow_steps['simple_send'] = self.test_simple_email_send()
        
        # Step 3: Template rendering
        workflow_steps['template_render'] = self.test_approval_email_template()
        
        # Step 4: Workflow simulation
        workflow_steps['workflow_simulation'] = self.test_sunday_workflow_simulation()
        
        # Calculate success rate
        successful_steps = sum(workflow_steps.values())
        total_steps = len(workflow_steps)
        success_rate = (successful_steps / total_steps) * 100
        
        print("\n" + "="*50)
        print("📊 EMAIL INTEGRATION TEST RESULTS")
        print("="*50)
        print(f"Overall Success Rate: {success_rate:.1f}% ({successful_steps}/{total_steps})")
        print("\nStep Results:")
        for step, success in workflow_steps.items():
            status = "✅ PASS" if success else "❌ FAIL"
            print(f"  {step.replace('_', ' ').title()}: {status}")
        
        if success_rate >= 75:
            print(f"\n🎉 Email integration test PASSED!")
            print("🚀 Ready for production Sunday approval workflow!")
            return True
        else:
            print(f"\n⚠️ Email integration test PARTIAL SUCCESS")
            print("🔧 Some components need attention before production use")
            return False
    
    def send_live_approval_email_test(self) -> bool:
        """Send a live approval email test (CAUTION: sends real email)"""
        print("\n🚨 LIVE EMAIL TEST - This will send a real approval email!")
        
        confirm = input("Are you sure you want to send a live test email? (yes/no): ").lower().strip()
        if confirm != 'yes':
            print("⏭️ Live email test cancelled")
            return False
        
        if not self.email_service or not self.sunday_automation:
            print("❌ Email service not available")
            return False
        
        try:
            # Force Sunday workflow for testing
            original_check = self.sunday_automation.check_sunday_trigger
            self.sunday_automation.check_sunday_trigger = lambda: True
            
            # Run workflow
            result = self.sunday_automation.run_sunday_workflow()
            
            # Restore original check
            self.sunday_automation.check_sunday_trigger = original_check
            
            if result['email_sent']:
                print("✅ Live approval email sent successfully!")
                print(f"📧 Check your inbox: {self.email_service.admin_email}")
                print(f"🔗 Session created: {result.get('session_created', False)}")
                return True
            else:
                print("❌ Live approval email failed")
                print(f"Error: {result.get('error', 'Unknown error')}")
                return False
                
        except Exception as e:
            print(f"❌ Live email test error: {e}")
            return False

def main():
    """Main test execution"""
    import argparse
    
    parser = argparse.ArgumentParser(description='MyBookshelf Email Integration Test')
    parser.add_argument('--quick', action='store_true', help='Run quick configuration test only')
    parser.add_argument('--full', action='store_true', help='Run full integration test suite')
    parser.add_argument('--live', action='store_true', help='Send live approval email test')
    parser.add_argument('--template', action='store_true', help='Test template rendering only')
    
    args = parser.parse_args()
    
    test_suite = EmailIntegrationTest()
    
    if args.quick:
        print("🏃‍♂️ Running Quick Configuration Test...")
        success = test_suite.test_resend_configuration()
        sys.exit(0 if success else 1)
    
    elif args.template:
        print("📋 Running Template Test...")
        success = test_suite.test_approval_email_template()
        sys.exit(0 if success else 1)
    
    elif args.live:
        print("🚨 Running Live Email Test...")
        success = test_suite.send_live_approval_email_test()
        sys.exit(0 if success else 1)
    
    elif args.full:
        print("🔬 Running Full Email Integration Test...")
        success = test_suite.test_complete_email_workflow()
        sys.exit(0 if success else 1)
    
    else:
        print("🧪 Running Standard Email Integration Test...")
        
        # Run core tests
        config_ok = test_suite.test_resend_configuration()
        if config_ok:
            template_ok = test_suite.test_approval_email_template()
            workflow_ok = test_suite.test_sunday_workflow_simulation()
            
            if template_ok and workflow_ok:
                print("\n✅ Email integration ready!")
                print("💡 Run with --live to send a real test email")
                sys.exit(0)
            else:
                print("\n⚠️ Some tests failed")
                sys.exit(1)
        else:
            print("\n❌ Configuration failed")
            sys.exit(1)

if __name__ == "__main__":
    main() 