#!/usr/bin/env python3
"""
Final Automated LinkedIn Poster for MyBookshelf Affiliate System
Production-ready with email notifications and error handling
"""

import os
import sys
import json
import requests
from datetime import datetime, timedelta
from typing import List, Dict, Optional
import logging
import time
from supabase.client import create_client

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('final_linkedin_poster.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class FinalLinkedInPoster:
    """Production LinkedIn poster with email notifications"""
    
    def __init__(self):
        """Initialize poster with credentials"""
        # Email configuration
        self.resend_api_key = os.getenv('RESEND_API_KEY', 're_CujkiY4j_B4SLnmAJFoxvPVFLuQ51xVJJ')
        self.from_email = os.getenv('RESEND_FROM_EMAIL', 'admin@mybookshelf.shop')
        self.admin_email = os.getenv('ADMIN_EMAIL', 'mcddsl@icloud.com')
        
        # LinkedIn configuration (will be loaded from database)
        self.access_token = None
        self.user_id = None
        
        # Content templates
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

    def get_scheduled_books(self) -> List[Dict]:
        """Get books from database for scheduled posting"""
        try:
            today = datetime.now()
            day_name = today.strftime('%A')
            
            # Only return books on Tue/Wed/Thu
            if day_name not in ['Tuesday', 'Wednesday', 'Thursday']:
                logger.info(f"ℹ️ No posting scheduled for {day_name}")
                return []
            
            # Get books from database
            supabase_url = os.getenv('SUPABASE_URL')
            supabase_key = os.getenv('SUPABASE_ANON_KEY')
            
            if not supabase_url or not supabase_key:
                logger.error("❌ Supabase credentials not configured")
                return []
            
            supabase = create_client(supabase_url, supabase_key)
            
            # Get all books from database
            result = supabase.table('books_accessories').select('*').execute()
            
            if not result.data:
                logger.warning("⚠️ No books found in database")
                return []
            
            books = result.data
            
            # Select one book for today based on day of week
            # Use hash of day to consistently select same book for same day
            day_hash = hash(day_name)
            selected_index = day_hash % len(books)
            selected_book = books[selected_index]
            
            # Format book data for posting
            scheduled_book = {
                'id': selected_book['id'],
                'title': selected_book['title'],
                'author': selected_book['author'],
                'affiliate_link': selected_book.get('affiliate_link', ''),
                'category': selected_book.get('category', 'Books'),
                'christian_themes': ['Christian Leadership', 'Biblical Principles'],
                'leadership_topics': ['Leadership Development', 'Personal Growth'],
                'content_summary': f"Discover insights from {selected_book['title']} by {selected_book['author']}.",
                'scheduled_post_at': today.isoformat()
            }
            
            logger.info(f"✅ Found 1 book scheduled for {day_name}: {scheduled_book['title']}")
            return [scheduled_book]
            
        except Exception as e:
            logger.error(f"❌ Error getting scheduled books from database: {e}")
            return []

    def generate_post_content(self, book: Dict) -> Dict:
        """Generate LinkedIn post content for a book"""
        try:
            today = datetime.now()
            day_name = today.strftime('%A')
            
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

    def post_to_linkedin(self, content: Dict, dry_run: bool = False) -> bool:
        """Post to LinkedIn using real API"""
        try:
            if dry_run:
                logger.info(f"🧪 DRY RUN: Would post to LinkedIn: {content['book_title']}")
                logger.info(f"📄 Content preview: {content['text'][:100]}...")
                return True
            
            # Get stored access token from database
            supabase_url = os.getenv('SUPABASE_URL')
            supabase_key = os.getenv('SUPABASE_ANON_KEY')
            
            if not supabase_url or not supabase_key:
                logger.error("❌ Supabase credentials not configured")
                return False
            
            supabase = create_client(supabase_url, supabase_key)
            
            # Get active token
            result = supabase.table('linkedin_tokens').select('*').eq('is_active', True).execute()
            
            if not result.data:
                logger.error("❌ No active LinkedIn token found in database")
                logger.info("ℹ️ Please re-authenticate with LinkedIn to get a fresh token")
                return False
            
            token_record = result.data[0]
            access_token = token_record['access_token']
            
            # Check if token is expired
            expires_at_str = token_record['expires_at']
            # Pad milliseconds if needed for fromisoformat
            if '.' in expires_at_str:
                date_part, ms_part = expires_at_str.split('.')
                ms_digits = ms_part.rstrip('Z')
                if len(ms_digits) < 6:
                    ms_digits = ms_digits.ljust(6, '0')
                expires_at_str = f"{date_part}.{ms_digits}"
            expires_at = datetime.fromisoformat(expires_at_str)
            if expires_at <= datetime.now():
                logger.error("❌ LinkedIn token has expired")
                logger.info("ℹ️ Please re-authenticate with LinkedIn to get a fresh token")
                return False
            
            # Prepare LinkedIn post data
            post_data = {
                "author": "urn:li:organization:10198635",
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
            
            # Make API call to LinkedIn
            headers = {
                'Authorization': f'Bearer {access_token}',
                'Content-Type': 'application/json',
                'X-Restli-Protocol-Version': '2.0.0'
            }
            
            logger.info(f"📤 Posting to LinkedIn: {content['book_title']}")
            response = requests.post(
                'https://api.linkedin.com/v2/ugcPosts',
                headers=headers,
                json=post_data,
                timeout=30
            )
            
            if response.status_code == 201:
                post_id = response.json().get('id', 'Unknown')
                logger.info(f"✅ Successfully posted to LinkedIn: {content['book_title']}")
                logger.info(f"📄 Post ID: {post_id}")
                logger.info(f"🔗 Post URL: https://www.linkedin.com/feed/update/{post_id.split(':')[-1]}/")
                return True
            else:
                logger.error(f"❌ LinkedIn API error: {response.status_code} - {response.text}")
                
                # Handle specific error cases
                if response.status_code == 401:
                    logger.error("❌ LinkedIn token is invalid or expired")
                    logger.info("ℹ️ Please re-authenticate with LinkedIn")
                elif response.status_code == 403:
                    logger.error("❌ Insufficient permissions for posting")
                elif response.status_code == 429:
                    logger.error("❌ Rate limit exceeded - too many posts")
                
                return False
                
        except Exception as e:
            logger.error(f"❌ Error posting to LinkedIn: {e}")
            return False

    def run_automated_posting(self, dry_run: bool = False) -> Dict:
        """Run automated posting with comprehensive reporting"""
        start_time = datetime.now()
        logger.info("🚀 Starting automated LinkedIn posting")
        
        # Get books scheduled for today
        scheduled_books = self.get_scheduled_books()
        
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
            success = self.post_to_linkedin(content, dry_run)
            
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
                time.sleep(2)
        
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
    poster = FinalLinkedInPoster()
    
    # Parse command line arguments
    import argparse
    parser = argparse.ArgumentParser(description='Final Automated LinkedIn Poster for MyBookshelf')
    parser.add_argument('--test', action='store_true', help='Test email notifications only')
    parser.add_argument('--dry-run', action='store_true', help='Generate content but do not post')
    parser.add_argument('--no-email', action='store_true', help='Skip email notifications')
    
    args = parser.parse_args()
    
    # Test email notifications only
    if args.test:
        success = poster.send_email_notification(
            "🧪 MyBookshelf Automation Test",
            "<h2>Test Email</h2><p>This is a test of the automated email system.</p>"
        )
        if success:
            logger.info("✅ Email test successful")
            sys.exit(0)
        else:
            logger.error("❌ Email test failed")
            sys.exit(1)
    
    # Run automated posting
    if args.dry_run:
        logger.info("🧪 DRY RUN MODE: Content will be generated but not posted")
    
    result = poster.run_automated_posting(args.dry_run)
    
    # Send daily report email (unless disabled)
    if not args.no_email:
        poster.send_daily_report(result)
    
    # Print summary
    print("\n" + "="*50)
    print("📊 FINAL LINKEDIN POSTING SUMMARY")
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