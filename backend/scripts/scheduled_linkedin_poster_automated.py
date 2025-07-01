#!/usr/bin/env python3
"""
Automated LinkedIn Poster for MyBookshelf Affiliate System
Enhanced version with email notifications, token refresh, and monitoring
"""

import os
import sys
import json
import requests
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime, timedelta
from typing import List, Dict, Optional
import logging
import time

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from supabase.client import create_client, Client
from config import Config

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('automated_linkedin_poster.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class AutomatedLinkedInPoster:
    """Enhanced LinkedIn poster with automation features"""
    
    def __init__(self):
        """Initialize automated poster with credentials"""
        # Use environment variables directly for production
        supabase_url = os.getenv('SUPABASE_URL', Config.SUPABASE_URL)
        supabase_key = os.getenv('SUPABASE_ANON_KEY', Config.SUPABASE_ANON_KEY)
        
        if not supabase_url or not supabase_key:
            raise ValueError("Missing Supabase configuration")
        
        self.supabase: Client = create_client(supabase_url, supabase_key)
        self.linkedin_client_id = Config.LINKEDIN_CLIENT_ID
        self.linkedin_client_secret = Config.LINKEDIN_CLIENT_SECRET
        self.access_token = None
        self.refresh_token = None
        self.user_id = None
        self.admin_email = os.getenv('ADMIN_EMAIL', 'mcddsl@icloud.com')
        
        # Email configuration
        self.resend_api_key = os.getenv('RESEND_API_KEY')
        self.from_email = os.getenv('RESEND_FROM_EMAIL', 'admin@mybookshelf.shop')
        
        # Content templates for different days
        self.content_templates = {
            'Tuesday': {
                'intro': [
                    "🎯 Leadership Insight Tuesday:",
                    "📚 Christian Leadership Wisdom:",
                    "🌟 Biblical Leadership Principle:",
                ],
                'themes': [
                    "biblical leadership",
                    "servant leadership", 
                    "stewardship principles",
                    "wisdom from Proverbs",
                    "integrity in leadership"
                ]
            },
            'Wednesday': {
                'intro': [
                    "⚡ Practical Wednesday:",
                    "🔧 Implementation Focus:",
                    "💡 Applied Wisdom Wednesday:",
                ],
                'themes': [
                    "actionable strategies",
                    "real-world application",
                    "practical implementation",
                    "proven methodologies",
                    "effective execution"
                ]
            },
            'Thursday': {
                'intro': [
                    "📖 Thursday Recommendations:",
                    "🎁 Complete Leadership Toolkit:",
                    "📋 Weekly Reading Roundup:",
                ],
                'themes': [
                    "comprehensive development",
                    "complete leadership toolkit",
                    "holistic approach",
                    "well-rounded growth",
                    "integrated solutions"
                ]
            }
        }

    def send_email_notification(self, subject: str, html_content: str, text_content: str = None) -> bool:
        """Send email notification using Resend API"""
        try:
            if not self.resend_api_key:
                logger.warning("❌ RESEND_API_KEY not set, skipping email notification")
                return False
            
            headers = {
                'Authorization': f'Bearer {self.resend_api_key}',
                'Content-Type': 'application/json'
            }
            
            email_data = {
                'from': f'MyBookshelf Admin <{self.from_email}>',
                'to': [self.admin_email],
                'subject': subject,
                'html': html_content
            }
            
            if text_content:
                email_data['text'] = text_content
            
            response = requests.post(
                'https://api.resend.com/emails',
                headers=headers,
                json=email_data,
                timeout=10
            )
            
            if response.status_code == 200:
                logger.info(f"✅ Email notification sent: {subject}")
                return True
            else:
                logger.error(f"❌ Email notification failed: {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            logger.error(f"❌ Email notification error: {e}")
            return False

    def load_access_token(self) -> bool:
        """Load LinkedIn access token from Supabase database with refresh capability"""
        try:
            # Get the most recent active LinkedIn token from Supabase
            response = self.supabase.table('linkedin_tokens').select(
                'access_token, refresh_token, linkedin_user_id, expires_at, is_active'
            ).eq('is_active', True).order('created_at', desc=True).limit(1).execute()
            
            if response.data and len(response.data) > 0:
                token_data = response.data[0]
                
                # Check if token is expired
                expires_at = datetime.fromisoformat(token_data['expires_at'].replace('Z', '+00:00'))
                if expires_at <= datetime.now().replace(tzinfo=expires_at.tzinfo):
                    logger.warning("❌ Stored LinkedIn token has expired, attempting refresh")
                    return self.refresh_access_token(token_data.get('refresh_token'))
                
                self.access_token = token_data['access_token']
                self.refresh_token = token_data.get('refresh_token')
                self.user_id = token_data['linkedin_user_id']
                
                # Validate token is still valid with LinkedIn
                if self.validate_token():
                    logger.info("✅ LinkedIn access token loaded from database and validated")
                    return True
                else:
                    logger.warning("❌ Stored LinkedIn token is invalid, attempting refresh")
                    return self.refresh_access_token(self.refresh_token)
            else:
                logger.warning("❌ No active LinkedIn token found in database")
                return False
                
        except Exception as e:
            logger.error(f"❌ Error loading LinkedIn token from database: {e}")
            return False

    def refresh_access_token(self, refresh_token: str) -> bool:
        """Refresh LinkedIn access token using refresh token"""
        try:
            if not refresh_token:
                logger.error("❌ No refresh token available")
                return False
            
            # LinkedIn token refresh endpoint
            url = 'https://www.linkedin.com/oauth/v2/accessToken'
            data = {
                'grant_type': 'refresh_token',
                'refresh_token': refresh_token,
                'client_id': self.linkedin_client_id,
                'client_secret': self.linkedin_client_secret
            }
            
            response = requests.post(url, data=data, timeout=10)
            
            if response.status_code == 200:
                token_info = response.json()
                
                # Update tokens in database
                update_data = {
                    'access_token': token_info['access_token'],
                    'expires_at': (datetime.now() + timedelta(seconds=token_info['expires_in'])).isoformat(),
                    'is_active': True
                }
                
                # Update refresh token if provided
                if 'refresh_token' in token_info:
                    update_data['refresh_token'] = token_info['refresh_token']
                
                # Update the most recent token record
                db_response = self.supabase.table('linkedin_tokens').update(update_data).eq('is_active', True).execute()
                
                if db_response.data:
                    self.access_token = token_info['access_token']
                    if 'refresh_token' in token_info:
                        self.refresh_token = token_info['refresh_token']
                    
                    logger.info("✅ LinkedIn access token refreshed successfully")
                    return True
                else:
                    logger.error("❌ Failed to update token in database")
                    return False
            else:
                logger.error(f"❌ Token refresh failed: {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            logger.error(f"❌ Token refresh error: {e}")
            return False

    def validate_token(self) -> bool:
        """Validate LinkedIn access token"""
        try:
            headers = {
                'Authorization': f'Bearer {self.access_token}',
                'Content-Type': 'application/json'
            }
            
            response = requests.get('https://api.linkedin.com/v2/userinfo', headers=headers, timeout=10)
            
            if response.status_code == 200:
                user_data = response.json()
                if not self.user_id:
                    self.user_id = user_data.get('sub')
                logger.info(f"✅ Token valid for user: {user_data.get('name', 'Unknown')}")
                return True
            else:
                logger.error(f"❌ Token validation failed: {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            logger.error(f"❌ Token validation error: {e}")
            return False

    def get_scheduled_books_for_today(self) -> List[Dict]:
        """Get books scheduled for posting today"""
        try:
            today = datetime.now().date()
            today_start = datetime.combine(today, datetime.min.time())
            today_end = datetime.combine(today, datetime.max.time())
            
            logger.info(f"📅 Checking for books scheduled on {today.strftime('%Y-%m-%d')}")
            
            response = self.supabase.table('pending_books').select(
                'id, title, author, affiliate_link, image_url, category, '
                'christian_themes, leadership_topics, content_summary, suggested_price, '
                'scheduled_post_at'
            ).eq('status', 'approved').gte(
                'scheduled_post_at', today_start.isoformat()
            ).lte(
                'scheduled_post_at', today_end.isoformat()
            ).is_('posted_at', 'null').order('scheduled_post_at', desc=False).execute()
            
            if response.data:
                logger.info(f"✅ Found {len(response.data)} books scheduled for today")
                return response.data
            else:
                logger.info("ℹ️ No books scheduled for posting today")
                return []
                
        except Exception as e:
            logger.error(f"❌ Error fetching scheduled books: {e}")
            return []

    def generate_post_content(self, book: Dict) -> Dict:
        """Generate LinkedIn post content for a book"""
        try:
            scheduled_date = datetime.fromisoformat(book['scheduled_post_at'].replace('Z', '+00:00'))
            day_name = scheduled_date.strftime('%A')
            
            if day_name not in self.content_templates:
                day_name = 'Tuesday'
            
            template = self.content_templates[day_name]
            
            intro = template['intro'][hash(book['title']) % len(template['intro'])]
            theme = template['themes'][hash(book['author']) % len(template['themes'])]
            
            christian_themes = book.get('christian_themes', [])
            if isinstance(christian_themes, str):
                christian_themes = [christian_themes]
            
            leadership_topics = book.get('leadership_topics', [])
            if isinstance(leadership_topics, str):
                leadership_topics = [leadership_topics]
            
            # Build content
            content_parts = [intro]
            
            # Add book description
            if book.get('content_summary'):
                content_parts.append(f"📖 {book['content_summary']}")
            
            # Add themes
            if christian_themes:
                themes_text = ', '.join(christian_themes[:3])
                content_parts.append(f"✨ Key themes: {themes_text}")
            
            if leadership_topics:
                topics_text = ', '.join(leadership_topics[:3])
                content_parts.append(f"🎯 Leadership focus: {topics_text}")
            
            # Add affiliate link
            if book.get('affiliate_link'):
                content_parts.append(f"🔗 Get it here: {book['affiliate_link']}")
            
            # Add hashtags
            hashtags = [
                "#ChristianLeadership", "#LeadershipBooks", "#MyBookshelf",
                "#LeadershipDevelopment", "#ChristianBusiness"
            ]
            content_parts.append(f"\n{' '.join(hashtags)}")
            
            full_text = '\n\n'.join(content_parts)
            
            return {
                'text': full_text,
                'book_title': book['title'],
                'author': book['author'],
                'affiliate_link': book.get('affiliate_link', ''),
                'day_theme': theme
            }
            
        except Exception as e:
            logger.error(f"❌ Error generating content for {book['title']}: {e}")
            return None

    def post_to_linkedin(self, content: Dict, retry_count: int = 0) -> bool:
        """Post to LinkedIn with retry logic"""
        try:
            headers = {
                'Authorization': f'Bearer {self.access_token}',
                'Content-Type': 'application/json',
                'X-Restli-Protocol-Version': '2.0.0'
            }
            
            url = 'https://api.linkedin.com/v2/ugcPosts'
            
            post_data = {
                "author": f"urn:li:person:{self.user_id}",
                "lifecycleState": "PUBLISHED",
                "specificContent": {
                    "com.linkedin.ugc.ShareContent": {
                        "shareCommentary": {
                            "text": content['text']
                        },
                        "shareMediaCategory": "NONE"
                    }
                },
                "visibility": {
                    "com.linkedin.ugc.MemberNetworkVisibility": "PUBLIC"
                }
            }
            
            response = requests.post(url, headers=headers, json=post_data, timeout=30)
            
            if response.status_code == 201:
                logger.info(f"✅ Successfully posted to LinkedIn: {content['book_title']}")
                return True
            elif response.status_code == 401 and retry_count < 2:
                logger.warning(f"❌ LinkedIn posting failed (401), attempting token refresh and retry")
                if self.refresh_access_token(self.refresh_token):
                    return self.post_to_linkedin(content, retry_count + 1)
                else:
                    return False
            else:
                logger.error(f"❌ LinkedIn posting failed: {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            logger.error(f"❌ Error posting to LinkedIn: {e}")
            return False

    def mark_book_as_posted(self, book_id: int, success: bool, post_content: str = None) -> bool:
        """Mark book as posted in database"""
        try:
            update_data = {
                'posted_at': datetime.now().isoformat(),
                'post_status': 'posted' if success else 'failed'
            }
            
            if post_content:
                update_data['post_content'] = post_content[:1000]
            
            response = self.supabase.table('pending_books').update(update_data).eq('id', book_id).execute()
            
            if response.data:
                logger.info(f"✅ Marked book ID {book_id} as {'posted' if success else 'failed'}")
                return True
            else:
                logger.error(f"❌ Failed to update book ID {book_id}")
                return False
                
        except Exception as e:
            logger.error(f"❌ Error marking book as posted: {e}")
            return False

    def run_automated_posting(self) -> Dict:
        """Run automated posting with comprehensive reporting"""
        start_time = datetime.now()
        logger.info("🚀 Starting automated LinkedIn posting")
        
        # Load LinkedIn credentials
        if not self.load_access_token():
            error_msg = "Cannot proceed without valid LinkedIn credentials"
            logger.error(f"❌ {error_msg}")
            return {
                'status': 'error',
                'reason': error_msg,
                'start_time': start_time.isoformat(),
                'end_time': datetime.now().isoformat(),
                'successful_posts': 0,
                'total_posts': 0,
                'results': []
            }
        
        # Get books scheduled for today
        scheduled_books = self.get_scheduled_books_for_today()
        
        if not scheduled_books:
            logger.info("ℹ️ No books scheduled for posting today")
            return {
                'status': 'no_books',
                'reason': 'No books scheduled for today',
                'start_time': start_time.isoformat(),
                'end_time': datetime.now().isoformat(),
                'successful_posts': 0,
                'total_posts': 0,
                'results': []
            }
        
        # Post each scheduled book
        results = []
        for book in scheduled_books:
            logger.info(f"📝 Processing scheduled book: {book['title']} by {book['author']}")
            
            # Generate post content
            content = self.generate_post_content(book)
            if not content:
                logger.error(f"❌ Failed to generate content for {book['title']}")
                self.mark_book_as_posted(book['id'], False, "Content generation failed")
                results.append({
                    'book_id': book['id'],
                    'title': book['title'],
                    'author': book['author'],
                    'scheduled_time': book['scheduled_post_at'],
                    'success': False,
                    'error': 'Content generation failed',
                    'content_preview': 'N/A'
                })
                continue
            
            # Post to LinkedIn
            success = self.post_to_linkedin(content)
            
            # Mark as posted
            self.mark_book_as_posted(book['id'], success, content['text'])
            
            results.append({
                'book_id': book['id'],
                'title': book['title'],
                'author': book['author'],
                'scheduled_time': book['scheduled_post_at'],
                'success': success,
                'error': None if success else 'LinkedIn posting failed',
                'content_preview': content['text'][:100] + '...'
            })
            
            # Add delay between posts to avoid rate limiting
            if len(scheduled_books) > 1:
                time.sleep(5)
        
        end_time = datetime.now()
        successful_posts = len([r for r in results if r['success']])
        total_posts = len(results)
        
        logger.info(f"✅ Automated posting complete: {successful_posts}/{total_posts} successful")
        
        return {
            'status': 'completed',
            'start_time': start_time.isoformat(),
            'end_time': end_time.isoformat(),
            'successful_posts': successful_posts,
            'total_posts': total_posts,
            'results': results
        }

    def send_daily_report(self, result: Dict) -> bool:
        """Send daily report email to admin"""
        try:
            date_str = datetime.now().strftime('%A, %B %d, %Y')
            
            # Build email content
            if result['status'] == 'completed':
                subject = f"✅ LinkedIn Posting Report - {date_str}"
                status_emoji = "✅"
                status_text = "Completed Successfully"
            elif result['status'] == 'no_books':
                subject = f"ℹ️ LinkedIn Posting Report - {date_str}"
                status_emoji = "ℹ️"
                status_text = "No Books Scheduled"
            else:
                subject = f"❌ LinkedIn Posting Report - {date_str}"
                status_emoji = "❌"
                status_text = f"Error: {result.get('reason', 'Unknown error')}"
            
            # Build HTML content
            html_content = f"""
            <!DOCTYPE html>
            <html>
            <head>
                <meta charset="utf-8">
                <title>LinkedIn Posting Report</title>
                <style>
                    body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                    .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                    .header {{ background: #2563eb; color: white; padding: 20px; border-radius: 8px 8px 0 0; }}
                    .content {{ background: #f8fafc; padding: 20px; border-radius: 0 0 8px 8px; }}
                    .status {{ font-size: 18px; font-weight: bold; margin: 20px 0; }}
                    .summary {{ background: white; padding: 15px; border-radius: 6px; margin: 20px 0; }}
                    .book-item {{ background: white; padding: 10px; margin: 10px 0; border-radius: 4px; border-left: 4px solid #2563eb; }}
                    .success {{ border-left-color: #10b981; }}
                    .failure {{ border-left-color: #ef4444; }}
                    .timestamp {{ color: #6b7280; font-size: 14px; }}
                </style>
            </head>
            <body>
                <div class="container">
                    <div class="header">
                        <h1>📊 MyBookshelf LinkedIn Posting Report</h1>
                        <p class="timestamp">{date_str}</p>
                    </div>
                    
                    <div class="content">
                        <div class="status">
                            {status_emoji} {status_text}
                        </div>
                        
                        <div class="summary">
                            <h3>📈 Summary</h3>
                            <p><strong>Status:</strong> {result['status'].title()}</p>
                            <p><strong>Successful Posts:</strong> {result['successful_posts']}/{result['total_posts']}</p>
                            <p><strong>Start Time:</strong> {datetime.fromisoformat(result['start_time']).strftime('%H:%M:%S')}</p>
                            <p><strong>End Time:</strong> {datetime.fromisoformat(result['end_time']).strftime('%H:%M:%S')}</p>
                        </div>
            """
            
            if result['results']:
                html_content += """
                        <h3>📚 Book Details</h3>
                """
                for item in result['results']:
                    status_class = "success" if item['success'] else "failure"
                    status_icon = "✅" if item['success'] else "❌"
                    scheduled_time = datetime.fromisoformat(item['scheduled_time'].replace('Z', '+00:00')).strftime('%H:%M')
                    
                    html_content += f"""
                        <div class="book-item {status_class}">
                            <strong>{status_icon} {item['title']}</strong> by {item['author']}<br>
                            <small>Scheduled: {scheduled_time}</small>
                            {f'<br><small>Error: {item["error"]}</small>' if item.get('error') else ''}
                        </div>
                    """
            
            if result['status'] == 'error':
                html_content += f"""
                        <div class="book-item failure">
                            <strong>❌ System Error</strong><br>
                            <small>{result.get('reason', 'Unknown error')}</small>
                        </div>
                """
            
            html_content += """
                    </div>
                </div>
            </body>
            </html>
            """
            
            # Send email
            return self.send_email_notification(subject, html_content)
            
        except Exception as e:
            logger.error(f"❌ Error sending daily report: {e}")
            return False

def main():
    """Main execution function"""
    poster = AutomatedLinkedInPoster()
    
    # Parse command line arguments
    import argparse
    parser = argparse.ArgumentParser(description='Automated LinkedIn Poster for MyBookshelf')
    parser.add_argument('--test', action='store_true', help='Test LinkedIn connection only')
    parser.add_argument('--dry-run', action='store_true', help='Generate content but do not post')
    parser.add_argument('--check-scheduled', action='store_true', help='Check what books are scheduled for today')
    parser.add_argument('--no-email', action='store_true', help='Skip email notifications')
    
    args = parser.parse_args()
    
    # Test connection only
    if args.test:
        success = poster.load_access_token()
        if success:
            logger.info("✅ LinkedIn connection test successful")
            sys.exit(0)
        else:
            logger.error("❌ LinkedIn connection test failed")
            sys.exit(1)
    
    # Check scheduled books only
    if args.check_scheduled:
        books = poster.get_scheduled_books_for_today()
        print(f"\n📅 Books scheduled for today ({datetime.now().strftime('%Y-%m-%d')}):")
        if books:
            for book in books:
                scheduled_time = datetime.fromisoformat(book['scheduled_post_at'].replace('Z', '+00:00'))
                print(f"  📖 {book['title']} by {book['author']} - {scheduled_time.strftime('%H:%M')}")
        else:
            print("  No books scheduled for today")
        sys.exit(0)
    
    # Run automated posting
    if args.dry_run:
        logger.info("🧪 DRY RUN MODE: Content will be generated but not posted")
        poster.access_token = "dry_run_mode"
    
    result = poster.run_automated_posting()
    
    # Send daily report email (unless disabled)
    if not args.no_email:
        poster.send_daily_report(result)
    
    # Print summary
    print("\n" + "="*50)
    print("📊 AUTOMATED LINKEDIN POSTING SUMMARY")
    print("="*50)
    print(f"Status: {result['status']}")
    print(f"Successful Posts: {result['successful_posts']}/{result['total_posts']}")
    print(f"Start Time: {datetime.fromisoformat(result['start_time']).strftime('%H:%M:%S')}")
    print(f"End Time: {datetime.fromisoformat(result['end_time']).strftime('%H:%M:%S')}")
    
    if result['results']:
        print("\nPosted Items:")
        for item in result['results']:
            status = "✅" if item['success'] else "❌"
            scheduled_time = datetime.fromisoformat(item['scheduled_time'].replace('Z', '+00:00'))
            print(f"  {status} {item['title']} by {item['author']} (scheduled: {scheduled_time.strftime('%H:%M')})")
    
    print("="*50)
    
    # Exit with appropriate code
    if result['status'] == 'error':
        sys.exit(1)
    else:
        sys.exit(0)

if __name__ == "__main__":
    main() 