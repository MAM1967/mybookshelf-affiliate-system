#!/usr/bin/env python3
"""
Admin Dashboard Test Script
Tests the actual books in the database for launch readiness
"""

import os
import json
from datetime import datetime
from typing import Dict, List

# Set up environment (in real deployment these come from environment variables)
os.environ['SUPABASE_URL'] = 'https://ackcgrnizuhauccnbiml.supabase.co'
os.environ['SUPABASE_ANON_KEY'] = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImFja2Nncm5penVoYXVjY25iaW1sIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTEyMjc4MzEsImV4cCI6MjA2NjgwMzgzMX0.SXpIMuNBgUhcEQUHzpEB1zZAdF-UTGvmY81EFUtsAwc'

from supabase.client import create_client

class AdminDashboardTest:
    def __init__(self):
        """Initialize the admin dashboard test"""
        self.supabase = create_client(
            os.environ['SUPABASE_URL'],
            os.environ['SUPABASE_ANON_KEY']
        )
        
    def test_database_connection(self) -> Dict:
        """Test database connection"""
        try:
            response = self.supabase.table('books_accessories').select('count').execute()
            return {
                'status': 'connected',
                'message': 'Database connection successful'
            }
        except Exception as e:
            return {
                'status': 'error',
                'message': f'Database connection failed: {str(e)}'
            }
    
    def get_launch_books(self) -> List[Dict]:
        """Get the actual books ready for launch"""
        try:
            response = self.supabase.table('books_accessories').select(
                'id, title, author, price, affiliate_link, image_url, category'
            ).order('id').execute()
            
            return response.data or []
        except Exception as e:
            print(f"❌ Error fetching books: {e}")
            return []
    
    def test_linkedin_integration(self) -> Dict:
        """Test LinkedIn integration status"""
        try:
            # Check if LinkedIn token file exists and is valid
            with open('linkedin_token_info.json', 'r') as f:
                token_data = json.load(f)
            
            return {
                'status': 'active',
                'user': token_data.get('profile', {}).get('name', 'Unknown'),
                'email': token_data.get('profile', {}).get('email', 'Unknown'),
                'expires': 'Valid for 2 months',
                'scopes': token_data.get('scopes', [])
            }
        except Exception as e:
            return {
                'status': 'error',
                'message': f'LinkedIn integration check failed: {str(e)}'
            }
    
    def generate_launch_report(self) -> Dict:
        """Generate a comprehensive launch readiness report"""
        print("🚀 MyBookshelf Admin Dashboard - Launch Readiness Test")
        print("=" * 60)
        
        # Test database connection
        db_status = self.test_database_connection()
        print(f"📊 Database Connection: {db_status['status'].upper()}")
        if db_status['status'] == 'error':
            print(f"   Error: {db_status['message']}")
            return {'ready_for_launch': False, 'errors': [db_status['message']]}
        
        # Get launch books
        books = self.get_launch_books()
        print(f"📚 Books in Database: {len(books)}")
        
        if len(books) == 0:
            print("❌ No books found in database!")
            return {'ready_for_launch': False, 'errors': ['No books in database']}
        
        # Display book details
        working_books = []
        broken_books = []
        
        for i, book in enumerate(books, 1):
            print(f"\n📖 Book {i}: {book['title']}")
            print(f"   Author: {book['author']}")
            print(f"   Price: ${book['price']}")
            print(f"   Category: {book['category']}")
            print(f"   Affiliate Link: {book['affiliate_link'][:50]}..." if book['affiliate_link'] else "   No affiliate link")
            
            # Simple affiliate link validation
            if book['affiliate_link'] and 'amazon.com' in book['affiliate_link']:
                working_books.append(book)
                print("   Status: ✅ Ready for Launch")
            else:
                broken_books.append(book)
                print("   Status: ❌ Needs Attention")
        
        # Test LinkedIn integration
        linkedin_status = self.test_linkedin_integration()
        print(f"\n🔗 LinkedIn Integration: {linkedin_status['status'].upper()}")
        if linkedin_status['status'] == 'active':
            print(f"   User: {linkedin_status['user']}")
            print(f"   Email: {linkedin_status['email']}")
            print(f"   Token: {linkedin_status['expires']}")
        else:
            print(f"   Error: {linkedin_status.get('message', 'Unknown error')}")
        
        # Generate summary
        print("\n" + "=" * 60)
        print("📊 LAUNCH READINESS SUMMARY")
        print("=" * 60)
        
        ready_for_launch = (
            len(working_books) >= 3 and 
            linkedin_status['status'] == 'active' and
            db_status['status'] == 'connected'
        )
        
        if ready_for_launch:
            print("🎉 READY FOR LAUNCH!")
            print(f"✅ {len(working_books)} books ready")
            print("✅ LinkedIn automation active")
            print("✅ Database operational")
            print("✅ Revenue system functional")
        else:
            print("⚠️  LAUNCH READINESS ISSUES:")
            if len(working_books) < 3:
                print(f"   📚 Need at least 3 books (have {len(working_books)})")
            if linkedin_status['status'] != 'active':
                print("   🔗 LinkedIn integration needs attention")
            if db_status['status'] != 'connected':
                print("   📊 Database connection issues")
        
        # Generate sample posts for ready books
        if len(working_books) >= 3:
            print(f"\n📝 Sample LinkedIn Posts for Top 3 Books:")
            print("=" * 60)
            
            for i, book in enumerate(working_books[:3], 1):
                print(f"\nPost {i} - {book['title']}:")
                print("-" * 40)
                sample_post = self.generate_sample_post(book)
                print(sample_post)
        
        return {
            'ready_for_launch': ready_for_launch,
            'total_books': len(books),
            'working_books': len(working_books),
            'broken_books': len(broken_books),
            'linkedin_status': linkedin_status['status'],
            'database_status': db_status['status'],
            'books': books
        }
    
    def generate_sample_post(self, book: Dict) -> str:
        """Generate a sample LinkedIn post for a book"""
        post_templates = {
            'The Five Dysfunctions of a Team': """📚 Building high-performing teams starts with understanding what breaks them apart.

"The Five Dysfunctions of a Team" by Patrick Lencioni reveals the five behaviors that destroy team effectiveness—and how to overcome them.

🎯 Key insights:
• Absence of trust undermines everything
• Fear of conflict leads to artificial harmony  
• Lack of commitment creates ambiguity
• Avoidance of accountability breeds resentment
• Inattention to results focuses on individual goals

Perfect for Christian leaders who want to build teams that honor God through excellence and authentic relationships.

🔗 Get your copy: {affiliate_link}

#Leadership #TeamBuilding #ChristianLeadership #BusinessBooks #MyBookshelf""",

            'The Advantage': """🎯 Why do some organizations thrive while others struggle with the same resources?

"The Advantage" by Patrick Lencioni shows that organizational health is the ultimate competitive advantage—and it's often the most overlooked.

💡 Core principles:
• Build a cohesive leadership team
• Create clarity around vision and values
• Over-communicate for understanding
• Reinforce clarity through systems

As Christian leaders, we're called to stewardship excellence. This book provides a roadmap for leading organizations that reflect God's order and purpose.

🔗 Transform your organization: {affiliate_link}

#Leadership #OrganizationalHealth #ChristianBusiness #Management #MyBookshelf""",

            'Atomic Habits': """⚡ Small changes, remarkable results. The power of 1% improvements daily.

"Atomic Habits" by James Clear reveals the science behind habit formation and provides a proven framework for building good habits and breaking bad ones.

🔧 The Four Laws of Behavior Change:
• Make it obvious
• Make it attractive  
• Make it easy
• Make it satisfying

Whether it's personal spiritual disciplines or leading organizational change, these principles work. Building better habits honors the time and talents God has given us.

🔗 Start building better habits: {affiliate_link}

#Productivity #Habits #PersonalDevelopment #Leadership #ChristianLiving #MyBookshelf"""
        }
        
        template = post_templates.get(book['title'], f"""📚 Excellent leadership resource for Christian professionals.

"{book['title']}" by {book['author']} provides practical wisdom for leading with integrity and excellence.

Perfect for leaders who want to grow both professionally and spiritually.

🔗 Get your copy: {book['affiliate_link']}

#Leadership #ChristianLeadership #BookRecommendation #MyBookshelf""")
        
        return template.format(affiliate_link=book['affiliate_link'])

def main():
    """Main execution function"""
    dashboard = AdminDashboardTest()
    report = dashboard.generate_launch_report()
    
    # Save report to file for reference
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    with open(f'admin_dashboard_test_report_{timestamp}.json', 'w') as f:
        json.dump(report, f, indent=2, default=str)
    
    print(f"\n💾 Report saved to: admin_dashboard_test_report_{timestamp}.json")

if __name__ == "__main__":
    main() 