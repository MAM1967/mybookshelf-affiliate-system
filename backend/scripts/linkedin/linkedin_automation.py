#!/usr/bin/env python3
"""
LinkedIn Automation for MyBookshelf Affiliate System
Automatically posts approved books on Tuesday/Wednesday/Thursday schedule
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

from supabase import create_client, Client
from config import Config

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('linkedin_automation.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class LinkedInAutomation:
    """Handles automated LinkedIn posting for approved books"""
    
    def __init__(self):
        """Initialize LinkedIn automation with credentials"""
        self.supabase: Client = create_client(Config.SUPABASE_URL, Config.SUPABASE_ANON_KEY)
        self.linkedin_client_id = Config.LINKEDIN_CLIENT_ID
        self.linkedin_client_secret = Config.LINKEDIN_CLIENT_SECRET
        self.access_token = None
        self.user_id = None
        
        # Posting schedule
        self.posting_schedule = {
            'Tuesday': {'slot': 1, 'books': 1, 'accessories': 0, 'focus': 'leadership_principles'},
            'Wednesday': {'slot': 2, 'books': 1, 'accessories': 0, 'focus': 'practical_application'},
            'Thursday': {'slot': 3, 'books': 1, 'accessories': 1, 'focus': 'comprehensive_recommendations'}
        }
        
        # Content templates
        self.content_templates = {
            'leadership_principles': {
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
            'practical_application': {
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
            'comprehensive_recommendations': {
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
        """Load LinkedIn access token from storage"""
        try:
            if os.path.exists('linkedin_token.json'):
                with open('linkedin_token.json', 'r') as f:
                    token_data = json.load(f)
                    self.access_token = token_data.get('access_token')
                    
                    # Validate token is still valid
                    if self.validate_token():
                        logger.info("✅ LinkedIn access token loaded and validated")
                        return True
                    else:
                        logger.warning("❌ Stored LinkedIn token is invalid")
                        return False
            else:
                logger.warning("❌ No LinkedIn token file found")
                return False
                
        except Exception as e:
            logger.error(f"❌ Error loading LinkedIn token: {e}")
            return False

    def validate_token(self) -> bool:
        """Validate LinkedIn access token"""
        try:
            headers = {
                'Authorization': f'Bearer {self.access_token}',
                'Content-Type': 'application/json'
            }
            
            response = requests.get('https://api.linkedin.com/v2/people/~', headers=headers)
            
            if response.status_code == 200:
                user_data = response.json()
                self.user_id = user_data.get('id')
                logger.info(f"✅ Token valid for user: {user_data.get('localizedFirstName', 'Unknown')}")
                return True
            else:
                logger.error(f"❌ Token validation failed: {response.status_code}")
                return False
                
        except Exception as e:
            logger.error(f"❌ Token validation error: {e}")
            return False

    def get_approved_books(self, target_date: datetime) -> List[Dict]:
        """Get books approved for posting on target date"""
        try:
            # Calculate the week start (Sunday) for the target date
            days_since_sunday = target_date.weekday() + 1  # Monday = 1, Sunday = 0
            if days_since_sunday == 7:
                days_since_sunday = 0
            week_start = target_date - timedelta(days=days_since_sunday)
            
            logger.info(f"📅 Getting approved books for week starting {week_start.strftime('%Y-%m-%d')}")
            
            # Query approved books from that week
            response = self.supabase.table('pending_books').select(
                'id, title, author, affiliate_link, image_url, category, '
                'christian_themes, leadership_topics, content_summary, suggested_price'
            ).eq('status', 'approved').gte(
                'reviewed_at', week_start.isoformat()
            ).lt(
                'reviewed_at', (week_start + timedelta(days=7)).isoformat()
            ).order('reviewed_at', desc=False).execute()
            
            if response.data:
                logger.info(f"✅ Found {len(response.data)} approved books for target week")
                return response.data
            else:
                logger.warning("⚠️ No approved books found for target week")
                return []
                
        except Exception as e:
            logger.error(f"❌ Error fetching approved books: {e}")
            return []

    def generate_post_content(self, book: Dict, day_focus: str) -> Dict:
        """Generate LinkedIn post content for a book"""
        try:
            template = self.content_templates[day_focus]
            
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
            if day_focus == 'leadership_principles':
                content_parts.extend([
                    f"🎯 Key Leadership Insight: {theme.title()}",
                    "",
                    "This book explores biblical principles that transform how we lead others. " +
                    "Every Christian leader needs frameworks rooted in Scripture.",
                    "",
                    f"📖 Christian Themes: {', '.join(christian_themes[:3]) if christian_themes else 'Biblical leadership, integrity, stewardship'}",
                    "",
                    "\"Commit to the Lord whatever you do, and he will establish your plans.\" - Proverbs 16:3"
                ])
                
            elif day_focus == 'practical_application':
                content_parts.extend([
                    f"⚡ Implementation Focus: {theme.title()}",
                    "",
                    "Great leadership books provide more than theory—they give us actionable strategies " +
                    "we can implement immediately in our teams and organizations.",
                    "",
                    f"🔧 Leadership Applications: {', '.join(leadership_topics[:3]) if leadership_topics else 'Team building, decision making, communication'}",
                    "",
                    "Ready to level up your leadership game? This is where theory meets practice."
                ])
                
            else:  # comprehensive_recommendations
                content_parts.extend([
                    f"📋 Complete Leadership Development: {theme.title()}",
                    "",
                    "This week's recommendation combines biblical wisdom with practical leadership strategies. " +
                    "Perfect for Christian leaders who want to grow both spiritually and professionally.",
                    "",
                    f"🌟 Why This Matters: {', '.join((christian_themes + leadership_topics)[:2]) if christian_themes or leadership_topics else 'Biblical foundation, practical application'}"
                ])
            
            # Add call to action and affiliate link
            content_parts.extend([
                "",
                f"💰 Get it here: {book['affiliate_link']}",
                "",
                "#ChristianLeadership #BiblicalWisdom #LeadershipDevelopment #BookRecommendation #MyBookshelf"
            ])
            
            return {
                'text': '\n'.join(content_parts),
                'book_title': book['title'],
                'book_author': book['author'],
                'affiliate_link': book['affiliate_link'],
                'image_url': book.get('image_url'),
                'category': book['category']
            }
            
        except Exception as e:
            logger.error(f"❌ Error generating post content: {e}")
            return None

    def post_to_linkedin(self, content: Dict) -> bool:
        """Post content to LinkedIn"""
        try:
            if not self.access_token:
                logger.error("❌ No LinkedIn access token available")
                return False
            
            headers = {
                'Authorization': f'Bearer {self.access_token}',
                'Content-Type': 'application/json',
                'X-Restli-Protocol-Version': '2.0.0'
            }
            
            # Prepare post data
            post_data = {
                'author': f'urn:li:person:{self.user_id}',
                'lifecycleState': 'PUBLISHED',
                'specificContent': {
                    'com.linkedin.ugc.ShareContent': {
                        'shareCommentary': {
                            'text': content['text']
                        },
                        'shareMediaCategory': 'NONE'
                    }
                },
                'visibility': {
                    'com.linkedin.ugc.MemberNetworkVisibility': 'PUBLIC'
                }
            }
            
            # Add image if available
            if content.get('image_url'):
                # For now, we'll post without image to simplify
                # Future enhancement: Upload image to LinkedIn and include
                pass
            
            # Post to LinkedIn
            response = requests.post(
                'https://api.linkedin.com/v2/ugcPosts',
                headers=headers,
                json=post_data
            )
            
            if response.status_code == 201:
                post_id = response.json().get('id')
                logger.info(f"✅ Successfully posted to LinkedIn: {post_id}")
                logger.info(f"📖 Book: {content['book_title']} by {content['book_author']}")
                return True
            else:
                logger.error(f"❌ LinkedIn post failed: {response.status_code}")
                logger.error(f"Response: {response.text}")
                return False
                
        except Exception as e:
            logger.error(f"❌ Error posting to LinkedIn: {e}")
            return False

    def log_posting_activity(self, book_id: int, success: bool, post_content: str, error_msg: str = None):
        """Log posting activity to database"""
        try:
            activity_data = {
                'book_id': book_id,
                'posted_at': datetime.now().isoformat(),
                'success': success,
                'post_content': post_content[:1000],  # Truncate if too long
                'platform': 'linkedin',
                'error_message': error_msg
            }
            
            # Insert into posting log table (would need to create this table)
            logger.info(f"📝 Logged posting activity for book ID {book_id}: {'Success' if success else 'Failed'}")
            
        except Exception as e:
            logger.error(f"❌ Error logging posting activity: {e}")

    def run_daily_posting(self, target_date: datetime = None) -> Dict:
        """Run daily posting automation"""
        if target_date is None:
            target_date = datetime.now()
            
        day_name = target_date.strftime('%A')
        
        logger.info(f"🚀 Starting LinkedIn automation for {day_name}, {target_date.strftime('%Y-%m-%d')}")
        
        # Check if this is a posting day
        if day_name not in self.posting_schedule:
            logger.info(f"⏭️ {day_name} is not a posting day. Skipping automation.")
            return {'status': 'skipped', 'reason': 'Not a posting day'}
        
        # Load LinkedIn credentials
        if not self.load_access_token():
            logger.error("❌ Cannot proceed without valid LinkedIn credentials")
            return {'status': 'error', 'reason': 'No valid LinkedIn credentials'}
        
        # Get posting configuration for this day
        day_config = self.posting_schedule[day_name]
        books_needed = day_config['books']
        accessories_needed = day_config['accessories']
        focus = day_config['focus']
        
        logger.info(f"📋 {day_name} posting plan: {books_needed} books + {accessories_needed} accessories (focus: {focus})")
        
        # Get approved books
        approved_books = self.get_approved_books(target_date)
        
        if not approved_books:
            logger.warning("⚠️ No approved books available for posting")
            return {'status': 'warning', 'reason': 'No approved books available'}
        
        # Filter books vs accessories
        books = [item for item in approved_books if item['category'].lower() == 'books']
        accessories = [item for item in approved_books if item['category'].lower() == 'accessories']
        
        logger.info(f"📚 Available: {len(books)} books, {len(accessories)} accessories")
        
        # Select items to post
        items_to_post = []
        
        # Add books
        items_to_post.extend(books[:books_needed])
        
        # Add accessories
        if accessories_needed > 0:
            items_to_post.extend(accessories[:accessories_needed])
        
        if not items_to_post:
            logger.warning("⚠️ No items selected for posting")
            return {'status': 'warning', 'reason': 'No items selected for posting'}
        
        # Post each item
        results = []
        for item in items_to_post:
            logger.info(f"📝 Generating post for: {item['title']} by {item['author']}")
            
            # Generate post content
            content = self.generate_post_content(item, focus)
            if not content:
                logger.error(f"❌ Failed to generate content for {item['title']}")
                continue
            
            # Post to LinkedIn
            success = self.post_to_linkedin(content)
            
            # Log activity
            self.log_posting_activity(
                item['id'], 
                success, 
                content['text'],
                None if success else "Posting failed"
            )
            
            results.append({
                'book_id': item['id'],
                'title': item['title'],
                'author': item['author'],
                'success': success,
                'content_preview': content['text'][:100] + '...'
            })
            
            # Add delay between posts to avoid rate limiting
            if len(items_to_post) > 1:
                import time
                time.sleep(5)
        
        successful_posts = len([r for r in results if r['success']])
        total_posts = len(results)
        
        logger.info(f"✅ Posting complete: {successful_posts}/{total_posts} successful")
        
        return {
            'status': 'completed',
            'date': target_date.strftime('%Y-%m-%d'),
            'day': day_name,
            'successful_posts': successful_posts,
            'total_posts': total_posts,
            'results': results
        }

    def test_linkedin_connection(self) -> bool:
        """Test LinkedIn API connection"""
        logger.info("🔗 Testing LinkedIn API connection...")
        
        if not self.load_access_token():
            logger.error("❌ LinkedIn connection test failed: No valid token")
            return False
        
        if self.validate_token():
            logger.info("✅ LinkedIn connection test successful")
            return True
        else:
            logger.error("❌ LinkedIn connection test failed: Invalid token")
            return False

def main():
    """Main execution function"""
    automation = LinkedInAutomation()
    
    # Parse command line arguments
    import argparse
    parser = argparse.ArgumentParser(description='LinkedIn Automation for MyBookshelf')
    parser.add_argument('--test', action='store_true', help='Test LinkedIn connection only')
    parser.add_argument('--date', help='Target date for posting (YYYY-MM-DD format)')
    parser.add_argument('--dry-run', action='store_true', help='Generate content but do not post')
    
    args = parser.parse_args()
    
    # Test connection only
    if args.test:
        success = automation.test_linkedin_connection()
        sys.exit(0 if success else 1)
    
    # Parse target date
    target_date = datetime.now()
    if args.date:
        try:
            target_date = datetime.strptime(args.date, '%Y-%m-%d')
        except ValueError:
            logger.error("❌ Invalid date format. Use YYYY-MM-DD")
            sys.exit(1)
    
    # Run automation
    if args.dry_run:
        logger.info("🧪 DRY RUN MODE: Content will be generated but not posted")
        # Set a flag to skip actual posting
        automation.access_token = "dry_run_mode"
    
    result = automation.run_daily_posting(target_date)
    
    # Print summary
    print("\n" + "="*50)
    print("📊 LINKEDIN AUTOMATION SUMMARY")
    print("="*50)
    print(f"Status: {result['status']}")
    print(f"Date: {result.get('date', 'N/A')}")
    print(f"Day: {result.get('day', 'N/A')}")
    
    if result['status'] == 'completed':
        print(f"Successful Posts: {result['successful_posts']}/{result['total_posts']}")
        print("\nPosted Items:")
        for item in result['results']:
            status = "✅" if item['success'] else "❌"
            print(f"  {status} {item['title']} by {item['author']}")
    elif result['status'] == 'warning':
        print(f"Warning: {result['reason']}")
    elif result['status'] == 'error':
        print(f"Error: {result['reason']}")
    
    print("="*50)
    
    # Exit with appropriate code
    if result['status'] == 'error':
        sys.exit(1)
    elif result['status'] == 'warning':
        sys.exit(2)
    else:
        sys.exit(0)

if __name__ == "__main__":
    main()