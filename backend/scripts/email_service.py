#!/usr/bin/env python3
"""
Email Service for MyBookshelf Affiliate System
Handles all email communications using Resend API
"""

import os
import sys
import json
import requests
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import logging

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from supabase import create_client, Client
from config import Config

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class ResendEmailService:
    """Email service using Resend API for MyBookshelf communications"""
    
    def __init__(self):
        """Initialize Resend email service"""
        self.api_key = os.getenv('RESEND_API_KEY')
        self.from_email = os.getenv('RESEND_FROM_EMAIL', 'admin@mybookshelf.shop')
        self.from_name = os.getenv('RESEND_FROM_NAME', 'MyBookshelf Admin')
        self.admin_email = os.getenv('ADMIN_EMAIL', 'mcddsl@icloud.com')
        
        # Supabase for data access
        if Config.SUPABASE_URL and Config.SUPABASE_ANON_KEY:
            self.supabase: Client = create_client(Config.SUPABASE_URL, Config.SUPABASE_ANON_KEY)
        else:
            raise ValueError("Missing Supabase configuration")
        
        # Email endpoints
        self.api_base = "https://api.resend.com"
        
        # Domain configuration
        self.admin_dashboard_url = os.getenv('ADMIN_DASHBOARD_URL', 'https://mybookshelf.shop/admin')
        self.public_site_url = os.getenv('PUBLIC_SITE_URL', 'https://mybookshelf.shop')
    
    def validate_configuration(self) -> bool:
        """Validate Resend configuration"""
        if not self.api_key:
            logger.error("❌ RESEND_API_KEY environment variable not set")
            return False
        
        if not self.admin_email:
            logger.error("❌ ADMIN_EMAIL environment variable not set")
            return False
        
        logger.info("✅ Resend email service configuration validated")
        return True
    
    def send_email(self, to_email: str, subject: str, html_content: str, text_content: str = None) -> bool:
        """Send email via Resend API"""
        try:
            headers = {
                'Authorization': f'Bearer {self.api_key}',
                'Content-Type': 'application/json'
            }
            
            email_data = {
                'from': f'{self.from_name} <{self.from_email}>',
                'to': [to_email],
                'subject': subject,
                'html': html_content
            }
            
            # Add text version if provided
            if text_content:
                email_data['text'] = text_content
            
            response = requests.post(
                f'{self.api_base}/emails',
                headers=headers,
                json=email_data
            )
            
            if response.status_code == 200:
                email_id = response.json().get('id')
                logger.info(f"✅ Email sent successfully: {email_id}")
                logger.info(f"📧 To: {to_email} | Subject: {subject}")
                return True
            else:
                logger.error(f"❌ Email send failed: {response.status_code}")
                logger.error(f"Response: {response.text}")
                return False
                
        except Exception as e:
            logger.error(f"❌ Email send error: {e}")
            return False
    
    def get_pending_books_data(self) -> Dict:
        """Get pending books data for email content"""
        try:
            # Get pending books
            pending_response = self.supabase.table('pending_books').select(
                'id, title, author, category, suggested_price, christian_themes, '
                'leadership_topics, content_filter_notes, passes_content_filter, '
                'status, submitted_at'
            ).eq('status', 'pending').order('submitted_at', desc=False).execute()
            
            pending_books = pending_response.data or []
            
            # Get books needing review
            review_response = self.supabase.table('pending_books').select(
                'id, title, author, category, suggested_price, content_filter_notes'
            ).eq('status', 'needs_review').execute()
            
            review_books = review_response.data or []
            
            # Calculate stats
            filtered_count = len([b for b in pending_books if not b.get('passes_content_filter', True)])
            
            return {
                'pending_books': pending_books,
                'review_books': review_books,
                'stats': {
                    'pending_count': len(pending_books),
                    'review_count': len(review_books),
                    'filtered_count': filtered_count,
                    'total_count': len(pending_books) + len(review_books)
                }
            }
            
        except Exception as e:
            logger.error(f"❌ Error fetching books data: {e}")
            return {
                'pending_books': [],
                'review_books': [],
                'stats': {
                    'pending_count': 0,
                    'review_count': 0,
                    'filtered_count': 0,
                    'total_count': 0
                }
            }
    
    def create_approval_session(self) -> Optional[Dict]:
        """Create a new admin approval session"""
        try:
            session_date = datetime.now().date()
            
            # Generate secure access token
            import hashlib
            import secrets
            token_data = f"{self.admin_email}{session_date}{secrets.token_hex(16)}"
            access_token = hashlib.sha256(token_data.encode()).hexdigest()
            
            # Create session in database
            session_data = {
                'session_date': session_date.isoformat(),
                'admin_email': self.admin_email,
                'access_token': access_token,
                'status': 'pending',
                'expires_at': (datetime.now() + timedelta(days=7)).isoformat()
            }
            
            response = self.supabase.table('approval_sessions').insert(session_data).execute()
            
            if response.data:
                session = response.data[0]
                logger.info(f"✅ Created approval session: {session['id']}")
                return {
                    'session_id': session['id'],
                    'access_token': access_token,
                    'session_date': session_date,
                    'expires_at': session['expires_at']
                }
            else:
                logger.error("❌ Failed to create approval session")
                return None
                
        except Exception as e:
            logger.error(f"❌ Error creating approval session: {e}")
            return None
    
    def render_approval_email_template(self, books_data: Dict, session: Dict) -> str:
        """Render the Sunday approval email template"""
        try:
            stats = books_data['stats']
            pending_books = books_data['pending_books']
            
            # Build dashboard URL with session token
            dashboard_url = f"{self.admin_dashboard_url}?token={session['access_token']}"
            
            # Current date formatting
            current_date = datetime.now().strftime('%A, %B %d, %Y')
            
            # Generate book items HTML
            book_items_html = ""
            for book in pending_books[:10]:  # Show up to 10 books
                themes_text = ""
                if book.get('christian_themes'):
                    themes = book['christian_themes']
                    if isinstance(themes, list):
                        themes_text = ', '.join(themes[:3])
                    else:
                        themes_text = str(themes)[:100]
                
                filter_notes = ""
                if book.get('content_filter_notes'):
                    filter_notes = f'<br /><em>⚠️ Review needed: {book["content_filter_notes"]}</em>'
                
                book_items_html += f'''
                <div class="book-item">
                  <strong>{book["title"]}</strong> by {book["author"]}<br />
                  <small>Category: {book["category"]} | Price: ${float(book.get("suggested_price", 0)):.2f}</small>
                  {f'<br />📖 Themes: {themes_text}' if themes_text else ''}
                  {filter_notes}
                </div>
                '''
            
            # Session expiry calculation
            expires_date = datetime.fromisoformat(session['expires_at'].replace('Z', '+00:00'))
            days_left = (expires_date - datetime.now()).days
            
            # Complete HTML email template
            html_template = f'''
<!DOCTYPE html>
<html>
  <head>
    <meta charset="utf-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <title>Weekly Book Approval Required - MyBookshelf</title>
    <style>
      body {{
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
        line-height: 1.6;
        color: #333;
        margin: 0;
        padding: 20px;
        background-color: #f5f5f5;
      }}
      .container {{
        max-width: 600px;
        margin: 0 auto;
        background: white;
        border-radius: 12px;
        overflow: hidden;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.1);
      }}
      .header {{
        background: linear-gradient(135deg, #2563eb 0%, #1d4ed8 100%);
        color: white;
        padding: 30px;
        text-align: center;
      }}
      .header h1 {{
        margin: 0 0 10px 0;
        font-size: 28px;
        font-weight: 600;
      }}
      .header p {{
        margin: 0;
        opacity: 0.9;
        font-size: 16px;
      }}
      .content {{
        padding: 30px;
      }}
      .stats {{
        background: #f8fafc;
        padding: 20px;
        border-radius: 8px;
        margin: 20px 0;
        border-left: 4px solid #2563eb;
      }}
      .stats h3 {{
        margin: 0 0 15px 0;
        color: #1f2937;
        font-size: 18px;
      }}
      .stats ul {{
        margin: 0;
        padding-left: 20px;
      }}
      .stats li {{
        margin-bottom: 8px;
        color: #4b5563;
      }}
      .book-item {{
        background: white;
        padding: 15px;
        margin: 12px 0;
        border-radius: 8px;
        border-left: 4px solid #fbbf24;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
      }}
      .book-item strong {{
        color: #1f2937;
        font-size: 16px;
      }}
      .book-item small {{
        color: #6b7280;
      }}
      .button {{
        display: inline-block;
        background: linear-gradient(135deg, #16a34a 0%, #15803d 100%);
        color: white;
        padding: 15px 30px;
        text-decoration: none;
        border-radius: 8px;
        font-weight: 600;
        font-size: 16px;
        text-align: center;
        margin: 20px 0;
        box-shadow: 0 4px 12px rgba(22, 163, 74, 0.3);
      }}
      .important {{
        background: #fef3c7;
        padding: 15px;
        border-radius: 8px;
        margin: 20px 0;
        border-left: 4px solid #f59e0b;
      }}
      .footer {{
        background: #f8fafc;
        padding: 20px 30px;
        color: #6b7280;
        font-size: 14px;
        border-top: 1px solid #e5e7eb;
      }}
      .business-context {{
        background: #ecfdf5;
        padding: 20px;
        border-radius: 8px;
        margin: 20px 0;
        border-left: 4px solid #10b981;
      }}
      .business-context h3 {{
        margin: 0 0 15px 0;
        color: #065f46;
      }}
      .business-context p {{
        margin: 8px 0;
        color: #047857;
      }}
    </style>
  </head>
  <body>
    <div class="container">
      <div class="header">
        <h1>📚 Weekly Book Approval Required</h1>
        <p>{current_date} - MyBookshelf Admin</p>
      </div>

      <div class="content">
        <p>Good morning! Your weekly book approval session is ready.</p>

        <div class="stats">
          <h3>📊 This Week's Summary</h3>
          <ul>
            <li><strong>{stats["pending_count"]} books</strong> awaiting your approval</li>
            <li><strong>{stats["filtered_count"]} books</strong> passed content filtering</li>
            <li><strong>{stats["review_count"]} books</strong> need special review</li>
          </ul>
        </div>

        <h3>📖 Books & Accessories Pending Your Approval:</h3>
        <p><em>Review each item for Christian leadership relevance and business alignment. Email content and LinkedIn posts will be automatically generated from your approved selections.</em></p>
        
        {book_items_html}

        <div style="text-align: center; margin: 30px 0;">
          <a href="{dashboard_url}" class="button">
            🚀 Start Approval Session
          </a>
        </div>

        <div class="important">
          <strong>⏰ Important:</strong> Please complete your approval by Tuesday to ensure timely content scheduling. This session expires in {days_left} days.
        </div>

        <div class="business-context">
          <h3>🎯 Business Context</h3>
          <p><strong>Goal:</strong> Curate 3 books + 1 accessory for this week's automated posting</p>
          <p><strong>Your Role:</strong> Approve content selections - posts and emails are auto-generated</p>
          <p><strong>Posting Schedule:</strong> Tuesday, Wednesday, Thursday (automatic)</p>
          <p><strong>Revenue Target:</strong> $1-$5 commission this month</p>
        </div>
      </div>

      <div class="footer">
        <p>This email was automatically generated by the MyBookshelf admin system.</p>
        <p>Questions? Reply to this email or check the <a href="{self.public_site_url}">main site</a>.</p>
        <p><strong>Session ID:</strong> {session["session_id"]} | <strong>Expires:</strong> {expires_date.strftime('%B %d, %Y')}</p>
      </div>
    </div>
  </body>
</html>
            '''
            
            return html_template
            
        except Exception as e:
            logger.error(f"❌ Error rendering email template: {e}")
            return ""
    
    def send_sunday_approval_email(self) -> bool:
        """Send the Sunday approval email to admin"""
        try:
            logger.info("📧 Sending Sunday approval email...")
            
            # Validate configuration
            if not self.validate_configuration():
                return False
            
            # Get books data
            books_data = self.get_pending_books_data()
            
            if books_data['stats']['total_count'] == 0:
                logger.info("ℹ️ No pending books found, skipping approval email")
                return True
            
            # Create approval session
            session = self.create_approval_session()
            if not session:
                logger.error("❌ Failed to create approval session")
                return False
            
            # Render email template
            html_content = self.render_approval_email_template(books_data, session)
            if not html_content:
                logger.error("❌ Failed to render email template")
                return False
            
            # Send email
            subject = f"📚 Weekly Book Approval Required - {books_data['stats']['pending_count']} books pending"
            
            success = self.send_email(
                to_email=self.admin_email,
                subject=subject,
                html_content=html_content
            )
            
            if success:
                logger.info(f"✅ Sunday approval email sent successfully to {self.admin_email}")
                logger.info(f"📊 Books pending: {books_data['stats']['pending_count']}")
                logger.info(f"🔗 Dashboard: {self.admin_dashboard_url}?token={session['access_token']}")
                return True
            else:
                logger.error("❌ Failed to send Sunday approval email")
                return False
                
        except Exception as e:
            logger.error(f"❌ Sunday approval email error: {e}")
            return False
    
    def send_approval_reminder(self, session_id: int) -> bool:
        """Send reminder email if approval not completed by Tuesday"""
        try:
            # Get session details
            response = self.supabase.table('approval_sessions').select('*').eq('id', session_id).single().execute()
            
            if not response.data:
                logger.error(f"❌ Session {session_id} not found")
                return False
            
            session = response.data
            
            if session['status'] != 'pending':
                logger.info(f"ℹ️ Session {session_id} already completed, skipping reminder")
                return True
            
            # Check if we're past Tuesday
            session_date = datetime.fromisoformat(session['session_date'])
            tuesday = session_date + timedelta(days=2)  # Sunday + 2 = Tuesday
            
            if datetime.now().date() < tuesday.date():
                logger.info("ℹ️ Not yet Tuesday, reminder not needed")
                return True
            
            # Send reminder email
            reminder_html = f'''
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8" />
    <title>Reminder: Book Approval Needed - MyBookshelf</title>
</head>
<body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333; padding: 20px;">
    <div style="max-width: 600px; margin: 0 auto; background: white; border-radius: 8px; padding: 30px; box-shadow: 0 2px 10px rgba(0,0,0,0.1);">
        <h1 style="color: #f59e0b; margin-bottom: 20px;">⏰ Approval Reminder</h1>
        
        <p>This is a friendly reminder that your weekly book approval is still pending.</p>
        
        <p><strong>Session Date:</strong> {session_date.strftime('%A, %B %d, %Y')}</p>
        <p><strong>Status:</strong> Awaiting your approval</p>
        
        <div style="text-align: center; margin: 30px 0;">
            <a href="{self.admin_dashboard_url}?token={session['access_token']}" 
               style="background: #f59e0b; color: white; padding: 15px 30px; text-decoration: none; border-radius: 6px; font-weight: bold;">
                Complete Approval Now
            </a>
        </div>
        
        <p style="color: #dc2626;"><strong>Important:</strong> Please complete your approval today to ensure Thursday's posting schedule.</p>
        
        <p style="font-size: 14px; color: #6b7280; margin-top: 30px;">
            Questions? Reply to this email or contact support.
        </p>
    </div>
</body>
</html>
            '''
            
            success = self.send_email(
                to_email=self.admin_email,
                subject="⏰ Reminder: Weekly Book Approval Still Needed",
                html_content=reminder_html
            )
            
            if success:
                logger.info(f"✅ Reminder email sent for session {session_id}")
                return True
            else:
                logger.error(f"❌ Failed to send reminder email for session {session_id}")
                return False
                
        except Exception as e:
            logger.error(f"❌ Reminder email error: {e}")
            return False
    
    def test_email_service(self) -> bool:
        """Test email service functionality"""
        logger.info("🧪 Testing email service...")
        
        # Test configuration
        if not self.validate_configuration():
            return False
        
        # Test simple email send
        test_html = '''
        <html>
        <body style="font-family: Arial, sans-serif; padding: 20px;">
            <h2 style="color: #2563eb;">🧪 MyBookshelf Email Service Test</h2>
            <p>This is a test email from the MyBookshelf email service.</p>
            <p><strong>Time:</strong> ''' + datetime.now().strftime('%Y-%m-%d %H:%M:%S') + '''</p>
            <p><strong>Status:</strong> ✅ Email service is working correctly!</p>
        </body>
        </html>
        '''
        
        success = self.send_email(
            to_email=self.admin_email,
            subject="🧪 MyBookshelf Email Service Test",
            html_content=test_html
        )
        
        if success:
            logger.info("✅ Email service test successful!")
            return True
        else:
            logger.error("❌ Email service test failed!")
            return False

def main():
    """Main execution function"""
    import argparse
    
    parser = argparse.ArgumentParser(description='MyBookshelf Email Service')
    parser.add_argument('--test', action='store_true', help='Test email service')
    parser.add_argument('--send-approval', action='store_true', help='Send Sunday approval email')
    parser.add_argument('--reminder', type=int, help='Send reminder for session ID')
    
    args = parser.parse_args()
    
    email_service = ResendEmailService()
    
    if args.test:
        success = email_service.test_email_service()
        sys.exit(0 if success else 1)
    
    elif args.send_approval:
        success = email_service.send_sunday_approval_email()
        sys.exit(0 if success else 1)
    
    elif args.reminder:
        success = email_service.send_approval_reminder(args.reminder)
        sys.exit(0 if success else 1)
    
    else:
        print("Usage: python email_service.py [--test | --send-approval | --reminder SESSION_ID]")
        sys.exit(1)

if __name__ == "__main__":
    main()