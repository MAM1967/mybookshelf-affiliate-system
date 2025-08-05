#!/usr/bin/env python3
"""
Scheduled LinkedIn Poster for MyBookshelf Affiliate System
Checks for books scheduled for today and posts them to LinkedIn
"""

import os
import sys
import json
import requests
from datetime import datetime, timedelta
from typing import List, Dict, Optional
import logging

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from supabase.client import create_client, Client
from config import Config

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('scheduled_linkedin_poster.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class ScheduledLinkedInPoster:
    """Handles scheduled LinkedIn posting for approved books"""
    
    def __init__(self):
        """Initialize scheduled poster with credentials"""
        self.supabase: Client = create_client(Config.SUPABASE_URL, Config.SUPABASE_ANON_KEY)
        self.linkedin_client_id = Config.LINKEDIN_CLIENT_ID
        self.linkedin_client_secret = Config.LINKEDIN_CLIENT_SECRET
        self.access_token = None
        self.user_id = None
        
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

    def load_access_token(self) -> bool:
        """Load LinkedIn access token from Supabase database"""
        try:
            # Get the most recent active LinkedIn token from Supabase
            response = self.supabase.table('linkedin_tokens').select(
                'access_token, linkedin_user_id, expires_at, is_active'
            ).eq('is_active', True).order('created_at', desc=True).limit(1).execute()
            
            if response.data and len(response.data) > 0:
                token_data = response.data[0]
                
                # Check if token is expired
                expires_at = datetime.fromisoformat(token_data['expires_at'].replace('Z', '+00:00'))
                if expires_at <= datetime.now().replace(tzinfo=expires_at.tzinfo):
                    logger.warning("❌ Stored LinkedIn token has expired")
                    return False
                
                self.access_token = token_data['access_token']
                self.user_id = token_data['linkedin_user_id']
                
                # Validate token is still valid with LinkedIn
                if self.validate_token():
                    logger.info("✅ LinkedIn access token loaded from database and validated")
                    return True
                else:
                    logger.warning("❌ Stored LinkedIn token is invalid")
                    return False
            else:
                logger.warning("❌ No active LinkedIn token found in database")
                return False
                
        except Exception as e:
            logger.error(f"❌ Error loading LinkedIn token from database: {e}")
            return False

    def validate_token(self) -> bool:
        """Validate LinkedIn access token"""
        try:
            headers = {
                'Authorization': f'Bearer {self.access_token}',
                'Content-Type': 'application/json'
            }
            
            # Use the modern userinfo endpoint instead of deprecated people endpoint
            response = requests.get('https://api.linkedin.com/v2/userinfo', headers=headers)
            
            if response.status_code == 200:
                user_data = response.json()
                # The userinfo endpoint returns 'sub' as the user ID
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
            
            # Query books scheduled for today that are approved and not yet posted
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
            # Determine day of week for content template
            scheduled_date = datetime.fromisoformat(book['scheduled_post_at'].replace('Z', '+00:00'))
            day_name = scheduled_date.strftime('%A')
            
            if day_name not in self.content_templates:
                day_name = 'Tuesday'  # Default to Tuesday template
            
            template = self.content_templates[day_name]
            
            # Select intro and theme
            intro = template['intro'][hash(book['title']) % len(template['intro'])]
            theme = template['themes'][hash(book['author']) % len(template['themes'])]
            
            # Generate main content
            christian_themes = book.get('christian_themes', [])
            if isinstance(christian_themes, str):
                christian_themes = [christian_themes]
            
            leadership_topics = book.get('leadership_topics', [])
            if isinstance(leadership_topics, str):
                leadership_topics = [leadership_topics]
            
            # Build post content
            content_parts = [
                intro,
                "",
                f"📖 \"{book['title']}\" by {book['author']}",
                ""
            ]
            
            # Add focused content based on day
            if day_name == 'Tuesday':
                if christian_themes:
                    theme_text = christian_themes[0] if isinstance(christian_themes, list) else christian_themes
                    content_parts.append(f"This book explores {theme_text.lower()} and how it applies to modern leadership.")
                else:
                    content_parts.append("This leadership book offers timeless wisdom for today's challenges.")
                    
            elif day_name == 'Wednesday':
                if leadership_topics:
                    topic_text = leadership_topics[0] if isinstance(leadership_topics, list) else leadership_topics
                    content_parts.append(f"Learn practical strategies for {topic_text.lower()} that you can implement immediately.")
                else:
                    content_parts.append("Discover actionable strategies and practical implementation techniques.")
                    
            elif day_name == 'Thursday':
                content_parts.append("A comprehensive resource for leaders seeking to grow both professionally and spiritually.")
            
            # Add affiliate link and call to action
            content_parts.extend([
                "",
                f"🔗 Get your copy: {book['affiliate_link']}",
                "",
                "#ChristianLeadership #LeadershipBooks #ProfessionalGrowth #FaithBasedLeadership"
            ])
            
            post_text = "\n".join(content_parts)
            
            return {
                'text': post_text,
                'day': day_name,
                'book_title': book['title'],
                'book_author': book['author']
            }
            
        except Exception as e:
            logger.error(f"❌ Error generating post content: {e}")
            return None

    def post_to_linkedin(self, content: Dict) -> bool:
        """Post content to LinkedIn"""
        try:
            if self.access_token == "dry_run_mode":
                logger.info("🧪 DRY RUN: Would post to LinkedIn")
                logger.info(f"Content preview: {content['text'][:200]}...")
                return True
            
            headers = {
                'Authorization': f'Bearer {self.access_token}',
                'Content-Type': 'application/json',
                'X-Restli-Protocol-Version': '2.0.0'
            }
            
            # LinkedIn API endpoint for creating posts
            url = 'https://api.linkedin.com/v2/ugcPosts'
            
            # Prepare the post data
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
            
            response = requests.post(url, headers=headers, json=post_data)
            
            if response.status_code == 201:
                logger.info(f"✅ Successfully posted to LinkedIn: {content['book_title']}")
                return True
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
                update_data['post_content'] = post_content[:1000]  # Truncate if too long
            
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

    def run_scheduled_posting(self) -> Dict:
        """Run scheduled posting for today"""
        logger.info("🚀 Starting scheduled LinkedIn posting for today")
        
        # Load LinkedIn credentials (skip validation in dry run mode)
        if self.access_token != "dry_run_mode":
            if not self.load_access_token():
                logger.error("❌ Cannot proceed without valid LinkedIn credentials")
                return {'status': 'error', 'reason': 'No valid LinkedIn credentials'}
        
        # Get books scheduled for today
        scheduled_books = self.get_scheduled_books_for_today()
        
        if not scheduled_books:
            logger.info("ℹ️ No books scheduled for posting today")
            return {'status': 'no_books', 'reason': 'No books scheduled for today'}
        
        # Post each scheduled book
        results = []
        for book in scheduled_books:
            logger.info(f"📝 Processing scheduled book: {book['title']} by {book['author']}")
            
            # Generate post content
            content = self.generate_post_content(book)
            if not content:
                logger.error(f"❌ Failed to generate content for {book['title']}")
                self.mark_book_as_posted(book['id'], False, "Content generation failed")
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
                'content_preview': content['text'][:100] + '...'
            })
            
            # Add delay between posts to avoid rate limiting
            if len(scheduled_books) > 1:
                import time
                time.sleep(5)
        
        successful_posts = len([r for r in results if r['success']])
        total_posts = len(results)
        
        logger.info(f"✅ Scheduled posting complete: {successful_posts}/{total_posts} successful")
        
        return {
            'status': 'completed',
            'date': datetime.now().strftime('%Y-%m-%d'),
            'successful_posts': successful_posts,
            'total_posts': total_posts,
            'results': results
        }

def main():
    """Main execution function"""
    poster = ScheduledLinkedInPoster()
    
    # Parse command line arguments
    import argparse
    parser = argparse.ArgumentParser(description='Scheduled LinkedIn Poster for MyBookshelf')
    parser.add_argument('--test', action='store_true', help='Test LinkedIn connection only')
    parser.add_argument('--dry-run', action='store_true', help='Generate content but do not post')
    parser.add_argument('--check-scheduled', action='store_true', help='Check what books are scheduled for today')
    
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
    
    # Run scheduled posting
    if args.dry_run:
        logger.info("🧪 DRY RUN MODE: Content will be generated but not posted")
        poster.access_token = "dry_run_mode"
    
    result = poster.run_scheduled_posting()
    
    # Print summary
    print("\n" + "="*50)
    print("📊 SCHEDULED LINKEDIN POSTING SUMMARY")
    print("="*50)
    print(f"Status: {result['status']}")
    print(f"Date: {result.get('date', 'N/A')}")
    
    if result['status'] == 'completed':
        print(f"Successful Posts: {result['successful_posts']}/{result['total_posts']}")
        print("\nPosted Items:")
        for item in result['results']:
            status = "✅" if item['success'] else "❌"
            scheduled_time = datetime.fromisoformat(item['scheduled_time'].replace('Z', '+00:00'))
            print(f"  {status} {item['title']} by {item['author']} (scheduled: {scheduled_time.strftime('%H:%M')})")
    elif result['status'] == 'no_books':
        print(f"Info: {result['reason']}")
    elif result['status'] == 'error':
        print(f"Error: {result['reason']}")
    
    print("="*50)
    
    # Exit with appropriate code
    if result['status'] == 'error':
        sys.exit(1)
    elif result['status'] == 'no_books':
        sys.exit(0)  # This is not an error, just no work to do
    else:
        sys.exit(0)

if __name__ == "__main__":
    main()
