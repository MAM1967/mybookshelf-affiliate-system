#!/usr/bin/env python3
"""
Integration Test: Admin Approval → LinkedIn Automation
Tests the complete workflow from book approval to automated LinkedIn posting
"""

import os
import sys
import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from supabase import create_client, Client
from config import Config
from linkedin_automation import LinkedInAutomation

class AdminLinkedInIntegrationTest:
    """Test the complete admin approval to LinkedIn posting workflow"""
    
    def __init__(self):
        """Initialize test environment"""
        if not Config.SUPABASE_URL or not Config.SUPABASE_ANON_KEY:
            raise ValueError("Missing required Supabase configuration")
        self.supabase: Client = create_client(Config.SUPABASE_URL, Config.SUPABASE_ANON_KEY)
        self.linkedin_automation = LinkedInAutomation()
        
    def setup_test_data(self) -> List[int]:
        """Create test books in pending_books table"""
        print("📋 Setting up test data...")
        
        test_books = [
            {
                'title': 'The Five Dysfunctions of a Team',
                'author': 'Patrick Lencioni',
                'isbn': '9780787960759',
                'amazon_asin': 'B006960LQW',
                'suggested_price': 18.99,
                'affiliate_link': 'https://amzn.to/3BookshelF1',
                'image_url': 'https://example.com/book1.jpg',
                'category': 'Books',
                'content_summary': 'Explores five common dysfunctions that plague teams and provides tools to overcome them.',
                'christian_themes': ['Leadership', 'Teamwork', 'Integrity'],
                'leadership_topics': ['Team building', 'Communication', 'Trust'],
                'target_audience': 'Christian business leaders',
                'status': 'pending',
                'submitted_by': 'test_system',
                'passes_content_filter': True
            },
            {
                'title': 'Atomic Habits',
                'author': 'James Clear',
                'isbn': '9780735211292',
                'amazon_asin': 'B07D23CFGR',
                'suggested_price': 13.49,
                'affiliate_link': 'https://amzn.to/3BookshelF2',
                'image_url': 'https://example.com/book2.jpg',
                'category': 'Books',
                'content_summary': 'Practical strategies for forming good habits and breaking bad ones.',
                'christian_themes': ['Discipline', 'Stewardship', 'Personal growth'],
                'leadership_topics': ['Self-discipline', 'Goal setting', 'Personal development'],
                'target_audience': 'Leaders seeking personal improvement',
                'status': 'pending',
                'submitted_by': 'test_system',
                'passes_content_filter': True
            },
            {
                'title': 'Leadership Journal - Premium Edition',
                'author': 'Various',
                'amazon_asin': 'B08JOURNAL1',
                'suggested_price': 24.99,
                'affiliate_link': 'https://amzn.to/3BookshelF3',
                'image_url': 'https://example.com/journal1.jpg',
                'category': 'Accessories',
                'content_summary': 'High-quality journal for leadership reflection and goal tracking.',
                'christian_themes': ['Reflection', 'Prayer', 'Planning'],
                'leadership_topics': ['Goal setting', 'Reflection', 'Planning'],
                'target_audience': 'Christian leaders',
                'status': 'pending',
                'submitted_by': 'test_system',
                'passes_content_filter': True
            }
        ]
        
        inserted_ids = []
        
        for book in test_books:
            try:
                response = self.supabase.table('pending_books').insert(book).execute()
                if response.data:
                    book_id = response.data[0]['id']
                    inserted_ids.append(book_id)
                    print(f"✅ Created test book: {book['title']} (ID: {book_id})")
                else:
                    print(f"❌ Failed to create test book: {book['title']}")
            except Exception as e:
                print(f"❌ Error creating test book {book['title']}: {e}")
        
        print(f"📊 Created {len(inserted_ids)} test books")
        return inserted_ids
    
    def simulate_admin_approval(self, book_ids: List[int]) -> int:
        """Simulate admin approving books through the dashboard"""
        print("\n👤 Simulating admin approval process...")
        
        approved_count = 0
        
        for book_id in book_ids:
            try:
                # Simulate admin approval with notes
                admin_notes = f"Approved for Christian leadership content - Test approval {datetime.now().strftime('%H:%M')}"
                
                response = self.supabase.table('pending_books').update({
                    'status': 'approved',
                    'reviewed_by': 'admin_test',
                    'reviewed_at': datetime.now().isoformat(),
                    'admin_notes': admin_notes
                }).eq('id', book_id).execute()
                
                if response.data:
                    book_title = response.data[0]['title']
                    print(f"✅ Approved: {book_title} (ID: {book_id})")
                    approved_count += 1
                else:
                    print(f"❌ Failed to approve book ID: {book_id}")
                    
            except Exception as e:
                print(f"❌ Error approving book {book_id}: {e}")
        
        print(f"📊 Approved {approved_count}/{len(book_ids)} books")
        return approved_count
    
    def test_linkedin_content_generation(self, target_date: Optional[datetime] = None) -> Dict:
        """Test LinkedIn content generation without posting"""
        print("\n📝 Testing LinkedIn content generation...")
        
        if target_date is None:
            target_date = datetime.now()
        
        day_name = target_date.strftime('%A')
        
        # Override to test Tuesday content (most common posting day)
        if day_name not in ['Tuesday', 'Wednesday', 'Thursday']:
            target_date = target_date + timedelta(days=(1 - target_date.weekday()) % 7)  # Next Tuesday
            day_name = 'Tuesday'
        
        print(f"📅 Testing content generation for {day_name}, {target_date.strftime('%Y-%m-%d')}")
        
        # Get approved books
        approved_books = self.linkedin_automation.get_approved_books(target_date)
        
        if not approved_books:
            print("⚠️ No approved books found for content generation test")
            return {'status': 'no_books', 'content': []}
        
        # Generate content for each book
        generated_content = []
        day_config = self.linkedin_automation.posting_schedule[day_name]
        focus = day_config['focus']
        
        print(f"🎯 Content focus: {focus}")
        
        for book in approved_books[:3]:  # Test up to 3 books
            content = self.linkedin_automation.generate_post_content(book, focus)
            if content:
                generated_content.append({
                    'book': book['title'],
                    'author': book['author'],
                    'category': book['category'],
                    'content_preview': content['text'][:200] + '...',
                    'full_content': content['text'],
                    'character_count': len(content['text'])
                })
                print(f"✅ Generated content for: {book['title']} ({len(content['text'])} chars)")
            else:
                print(f"❌ Failed to generate content for: {book['title']}")
        
        return {'status': 'success', 'content': generated_content, 'focus': focus}
    
    def test_admin_dashboard_workflow(self) -> Dict:
        """Test the admin dashboard workflow simulation"""
        print("\n🎛️ Testing Admin Dashboard Workflow...")
        
        # 1. Check dashboard stats
        try:
            pending_response = self.supabase.table('pending_books').select('id, status, title').execute()
            pending_books = pending_response.data or []
            
            stats = {
                'total_books': len(pending_books),
                'pending': len([b for b in pending_books if b['status'] == 'pending']),
                'approved': len([b for b in pending_books if b['status'] == 'approved']),
                'rejected': len([b for b in pending_books if b['status'] == 'rejected']),
                'needs_review': len([b for b in pending_books if b['status'] == 'needs_review'])
            }
            
            print(f"📊 Dashboard Stats:")
            print(f"   Total Books: {stats['total_books']}")
            print(f"   Pending: {stats['pending']}")
            print(f"   Approved: {stats['approved']}")
            print(f"   Rejected: {stats['rejected']}")
            print(f"   Needs Review: {stats['needs_review']}")
            
            return {'status': 'success', 'stats': stats}
            
        except Exception as e:
            print(f"❌ Dashboard workflow test failed: {e}")
            return {'status': 'error', 'error': str(e)}
    
    def test_complete_workflow(self) -> Dict:
        """Test the complete workflow from setup to content generation"""
        print("🚀 Starting Complete Admin → LinkedIn Integration Test")
        print("=" * 60)
        
        workflow_results = {
            'setup': False,
            'approval': False,
            'content_generation': False,
            'dashboard': False,
            'linkedin_connection': False
        }
        
        try:
            # Step 1: Setup test data
            book_ids = self.setup_test_data()
            if book_ids:
                workflow_results['setup'] = True
                print("✅ Test data setup successful")
            else:
                print("❌ Test data setup failed")
                return {'status': 'failed', 'results': workflow_results, 'error': 'Setup failed'}
            
            # Step 2: Test admin dashboard workflow
            dashboard_result = self.test_admin_dashboard_workflow()
            if dashboard_result['status'] == 'success':
                workflow_results['dashboard'] = True
                print("✅ Admin dashboard workflow test successful")
            else:
                print("❌ Admin dashboard workflow test failed")
            
            # Step 3: Simulate admin approval
            approved_count = self.simulate_admin_approval(book_ids)
            if approved_count > 0:
                workflow_results['approval'] = True
                print("✅ Admin approval simulation successful")
            else:
                print("❌ Admin approval simulation failed")
                return {'status': 'failed', 'results': workflow_results, 'error': 'Approval failed'}
            
            # Step 4: Test LinkedIn content generation
            content_result = self.test_linkedin_content_generation()
            if content_result['status'] == 'success' and content_result['content']:
                workflow_results['content_generation'] = True
                print("✅ LinkedIn content generation successful")
                
                # Show sample content
                print("\n📝 Sample Generated Content:")
                for content in content_result['content'][:1]:  # Show first one
                    print(f"   Book: {content['book']}")
                    print(f"   Preview: {content['content_preview']}")
                    print(f"   Length: {content['character_count']} characters")
            else:
                print("❌ LinkedIn content generation failed")
            
            # Step 5: Test LinkedIn connection (optional)
            try:
                linkedin_test = self.linkedin_automation.test_linkedin_connection()
                if linkedin_test:
                    workflow_results['linkedin_connection'] = True
                    print("✅ LinkedIn API connection test successful")
                else:
                    print("⚠️ LinkedIn API connection test failed (expected if no token)")
            except:
                print("⚠️ LinkedIn API connection test skipped (no credentials)")
            
            # Cleanup test data
            self.cleanup_test_data(book_ids)
            
            # Calculate success rate
            successful_steps = sum(workflow_results.values())
            total_steps = len(workflow_results)
            success_rate = (successful_steps / total_steps) * 100
            
            print("\n" + "=" * 60)
            print("📊 INTEGRATION TEST RESULTS")
            print("=" * 60)
            print(f"Overall Success Rate: {success_rate:.1f}% ({successful_steps}/{total_steps})")
            print("\nStep Results:")
            for step, success in workflow_results.items():
                status = "✅ PASS" if success else "❌ FAIL"
                print(f"  {step.replace('_', ' ').title()}: {status}")
            
            return {
                'status': 'completed',
                'success_rate': success_rate,
                'results': workflow_results,
                'approved_books': approved_count,
                'generated_content': len(content_result.get('content', [])),
                'content_samples': content_result.get('content', [])
            }
            
        except Exception as e:
            print(f"❌ Integration test failed with error: {e}")
            return {'status': 'error', 'error': str(e), 'results': workflow_results}
    
    def cleanup_test_data(self, book_ids: List[int]):
        """Clean up test data from database"""
        print(f"\n🧹 Cleaning up test data...")
        
        for book_id in book_ids:
            try:
                self.supabase.table('pending_books').delete().eq('id', book_id).execute()
                print(f"✅ Deleted test book ID: {book_id}")
            except Exception as e:
                print(f"❌ Error deleting test book {book_id}: {e}")
        
        print(f"🧹 Cleanup completed for {len(book_ids)} test books")

def main():
    """Main test execution"""
    test_suite = AdminLinkedInIntegrationTest()
    
    # Run complete workflow test
    results = test_suite.test_complete_workflow()
    
    # Exit with appropriate code
    if results['status'] == 'completed' and results['success_rate'] >= 60:
        print("\n🎉 Integration test PASSED!")
        sys.exit(0)
    elif results['status'] == 'completed':
        print(f"\n⚠️ Integration test PARTIAL SUCCESS ({results['success_rate']:.1f}%)")
        sys.exit(1)
    else:
        print("\n❌ Integration test FAILED!")
        sys.exit(2)

if __name__ == "__main__":
    main() 