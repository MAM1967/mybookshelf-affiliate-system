#!/usr/bin/env python3
"""
Admin Workflow Repair Script
Fix workflow disconnect between live items and approval process
"""

import os
import sys
from datetime import datetime
from typing import Dict, List
from supabase import create_client, Client
import logging
import json

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class AdminWorkflowRepair:
    def __init__(self):
        # Supabase configuration
        self.supabase_url = "https://ackcgrnizuhauccnbiml.supabase.co"
        self.supabase_key = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImFja2Nncm5penVoYXVjY25iaW1sIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTEyMjc4MzEsImV4cCI6MjA2NjgwMzgzMX0.SXpIMuNBgUhcEQUHzpEB1zZAdF-UTGvmY81EFUtsAwc"
        
        self.supabase: Client = create_client(self.supabase_url, self.supabase_key)
    
    def create_sample_pending_items(self, count: int = 10) -> Dict:
        """Create sample pending items for admin approval testing"""
        logger.info(f"📝 Creating {count} sample pending items...")
        
        sample_items = [
            {
                'title': 'The 7 Habits of Highly Effective People',
                'author': 'Stephen R. Covey',
                'amazon_asin': 'B01069X4H0',
                'suggested_price': 14.99,
                'category': 'Books',
                'content_summary': 'Powerful lessons in personal change and leadership effectiveness.',
                'christian_themes': ['Character', 'Integrity', 'Service'],
                'leadership_topics': ['Personal Development', 'Character Building', 'Effectiveness'],
                'target_audience': 'Christian leaders and professionals',
                'status': 'pending',
                'submitted_by': 'repair_script',
                'passes_content_filter': True,
                'submitted_at': datetime.now().isoformat()
            },
            {
                'title': 'Good to Great',
                'author': 'Jim Collins',
                'amazon_asin': 'B0058DRUV6',
                'suggested_price': 16.99,
                'category': 'Books',
                'content_summary': 'Why some companies make the leap to great and others do not.',
                'christian_themes': ['Excellence', 'Stewardship', 'Humility'],
                'leadership_topics': ['Organizational Leadership', 'Excellence', 'Transformation'],
                'target_audience': 'Christian business leaders',
                'status': 'pending',
                'submitted_by': 'repair_script',
                'passes_content_filter': True,
                'submitted_at': datetime.now().isoformat()
            },
            {
                'title': 'Atomic Habits',
                'author': 'James Clear',
                'amazon_asin': 'B07D23CFGR',
                'suggested_price': 13.99,
                'category': 'Books',
                'content_summary': 'An easy and proven way to build good habits and break bad ones.',
                'christian_themes': ['Discipline', 'Growth', 'Perseverance'],
                'leadership_topics': ['Personal Development', 'Habit Formation', 'Self-Discipline'],
                'target_audience': 'Christian professionals seeking growth',
                'status': 'pending',
                'submitted_by': 'repair_script',
                'passes_content_filter': True,
                'submitted_at': datetime.now().isoformat()
            },
            {
                'title': 'Leadership Journal - Premium Edition',
                'author': 'Various',
                'amazon_asin': 'B08JOURNAL1',
                'suggested_price': 24.99,
                'category': 'Accessories',
                'content_summary': 'High-quality journal for leadership reflection and planning.',
                'christian_themes': ['Reflection', 'Prayer', 'Planning'],
                'leadership_topics': ['Goal Setting', 'Reflection', 'Strategic Planning'],
                'target_audience': 'Christian leaders',
                'status': 'pending',
                'submitted_by': 'repair_script',
                'passes_content_filter': True,
                'submitted_at': datetime.now().isoformat()
            },
            {
                'title': 'The Maxwell Daily Reader',
                'author': 'John C. Maxwell',
                'amazon_asin': 'B001QF6JS8',
                'suggested_price': 12.99,
                'category': 'Books',
                'content_summary': 'Daily leadership wisdom and inspiration for 365 days.',
                'christian_themes': ['Daily Growth', 'Wisdom', 'Leadership'],
                'leadership_topics': ['Daily Development', 'Leadership Principles', 'Personal Growth'],
                'target_audience': 'Christian leaders seeking daily inspiration',
                'status': 'pending',
                'submitted_by': 'repair_script',
                'passes_content_filter': True,
                'submitted_at': datetime.now().isoformat()
            }
        ]
        
        # Add more items to reach the requested count
        additional_books = [
            ('The Purpose Driven Life', 'Rick Warren', 'Faith-based living'),
            ('Lead Like Jesus', 'Ken Blanchard', 'Christian leadership principles'),
            ('The Servant Leader', 'James A. Autry', 'Servant leadership'),
            ('Praying for Your Future Husband', 'Robin Jones Gunn', 'Relationship guidance'),
            ('Business by the Book', 'Larry Burkett', 'Biblical business principles')
        ]
        
        # Add additional books if count > 5
        for i, (title, author, desc) in enumerate(additional_books):
            if len(sample_items) >= count:
                break
            
            sample_items.append({
                'title': title,
                'author': author,
                'amazon_asin': f'B0{i+10:06d}TEST',
                'suggested_price': 13.99 + (i * 0.50),
                'category': 'Books',
                'content_summary': desc,
                'christian_themes': ['Faith', 'Leadership', 'Growth'],
                'leadership_topics': ['Christian Leadership', 'Personal Development'],
                'target_audience': 'Christian professionals',
                'status': 'pending',
                'submitted_by': 'repair_script',
                'passes_content_filter': True,
                'submitted_at': datetime.now().isoformat()
            })
        
        # Trim to requested count
        sample_items = sample_items[:count]
        
        # Insert items
        results = {
            'requested_count': count,
            'created_count': 0,
            'errors': [],
            'created_items': []
        }
        
        for item in sample_items:
            try:
                # Check if item already exists
                existing = self.supabase.table('pending_books').select('id').eq('amazon_asin', item['amazon_asin']).execute()
                
                if existing.data:
                    logger.info(f"⏭️  Skipping existing item: {item['title']}")
                    continue
                
                # Insert new item
                response = self.supabase.table('pending_books').insert(item).execute()
                
                if response.data:
                    results['created_count'] += 1
                    results['created_items'].append({
                        'id': response.data[0]['id'],
                        'title': item['title'],
                        'author': item['author'],
                        'category': item['category']
                    })
                    logger.info(f"✅ Created pending item: {item['title']}")
                else:
                    error_msg = f"Failed to create item: {item['title']}"
                    results['errors'].append(error_msg)
                    logger.error(f"❌ {error_msg}")
                    
            except Exception as e:
                error_msg = f"Error creating item {item['title']}: {str(e)}"
                results['errors'].append(error_msg)
                logger.error(f"❌ {error_msg}")
        
        return results
    
    def retroactively_mark_live_items_approved(self) -> Dict:
        """Create approved entries in pending_books for existing live items"""
        logger.info("🔧 Retroactively marking live items as approved...")
        
        try:
            # Get existing live items
            live_response = self.supabase.table('books_accessories').select('*').execute()
            live_items = live_response.data or []
            
            # Get existing pending items to avoid duplicates
            pending_response = self.supabase.table('pending_books').select('amazon_asin, title, author').execute()
            existing_pending = {(item.get('amazon_asin', ''), item.get('title', ''), item.get('author', '')) 
                              for item in (pending_response.data or [])}
            
            results = {
                'total_live_items': len(live_items),
                'marked_approved': 0,
                'skipped_duplicates': 0,
                'errors': [],
                'approved_items': []
            }
            
            for item in live_items:
                # Create unique identifier
                item_key = (item.get('asin', ''), item.get('title', ''), item.get('author', ''))
                
                # Skip if already exists in pending_books
                if item_key in existing_pending:
                    results['skipped_duplicates'] += 1
                    logger.info(f"⏭️  Skipping existing: {item.get('title', 'Unknown')}")
                    continue
                
                # Create approved entry
                approved_entry = {
                    'title': item.get('title', 'Unknown Title'),
                    'author': item.get('author', 'Unknown Author'),
                    'amazon_asin': item.get('asin', ''),
                    'suggested_price': float(item.get('price', 0)),
                    'category': item.get('category', 'Books'),
                    'content_summary': f"Retroactively approved item from live database",
                    'christian_themes': item.get('christian_themes', []) or ['Faith', 'Leadership'],
                    'leadership_topics': item.get('leadership_topics', []) or ['Leadership', 'Growth'],
                    'target_audience': 'Christian professionals',
                    'status': 'approved',
                    'submitted_by': 'repair_script',
                    'reviewed_by': 'admin',
                    'submitted_at': datetime.now().isoformat(),
                    'reviewed_at': datetime.now().isoformat(),
                    'admin_notes': 'Retroactively approved - was already live',
                    'passes_content_filter': True
                }
                
                try:
                    response = self.supabase.table('pending_books').insert(approved_entry).execute()
                    
                    if response.data:
                        results['marked_approved'] += 1
                        results['approved_items'].append({
                            'id': response.data[0]['id'],
                            'title': approved_entry['title'],
                            'author': approved_entry['author']
                        })
                        logger.info(f"✅ Marked approved: {approved_entry['title']}")
                    else:
                        error_msg = f"Failed to mark approved: {approved_entry['title']}"
                        results['errors'].append(error_msg)
                        logger.error(f"❌ {error_msg}")
                        
                except Exception as e:
                    error_msg = f"Error marking approved {approved_entry['title']}: {str(e)}"
                    results['errors'].append(error_msg)
                    logger.error(f"❌ {error_msg}")
            
            return results
            
        except Exception as e:
            logger.error(f"❌ Retroactive approval failed: {e}")
            return {'error': str(e)}
    
    def clear_existing_pending_books(self) -> Dict:
        """Clear existing pending_books table (use with caution)"""
        logger.info("🗑️  Clearing existing pending_books table...")
        
        try:
            # Get existing count
            existing_response = self.supabase.table('pending_books').select('id').execute()
            existing_count = len(existing_response.data or [])
            
            if existing_count == 0:
                return {'deleted_count': 0, 'message': 'Table already empty'}
            
            # Delete all records
            delete_response = self.supabase.table('pending_books').delete().neq('id', 0).execute()
            
            return {
                'deleted_count': existing_count,
                'message': f'Cleared {existing_count} existing records'
            }
            
        except Exception as e:
            logger.error(f"❌ Clear table failed: {e}")
            return {'error': str(e)}
    
    def print_repair_options(self):
        """Print available repair options"""
        print("\n" + "="*80)
        print("🔧 ADMIN WORKFLOW REPAIR OPTIONS")
        print("="*80)
        print("\n🎯 PROBLEM: 97 items on website, 0 pending items for approval")
        print("🎯 SOLUTION: Choose a repair option:")
        
        print("\n📋 OPTION 1: Create Sample Pending Items")
        print("   • Add 10 new sample books/accessories for approval")
        print("   • Test the admin approval workflow")
        print("   • Good for: Testing and future workflow")
        
        print("\n📋 OPTION 2: Retroactive Audit Trail")
        print("   • Mark all 97 live items as 'approved' in pending_books")
        print("   • Maintains complete audit trail")
        print("   • Good for: Record keeping and compliance")
        
        print("\n📋 OPTION 3: Fresh Start")
        print("   • Clear pending_books table completely")
        print("   • Add new sample items for approval")
        print("   • Good for: Clean slate approach")
        
        print("\n📋 OPTION 4: Combined Approach")
        print("   • Retroactively mark live items as approved")
        print("   • Add new sample items for testing")
        print("   • Good for: Complete solution")
        
        print("\n" + "="*80)

def main():
    """Interactive repair workflow"""
    try:
        repair = AdminWorkflowRepair()
        repair.print_repair_options()
        
        while True:
            choice = input("\nEnter your choice (1-4) or 'q' to quit: ").strip()
            
            if choice.lower() == 'q':
                print("👋 Repair cancelled")
                return 0
            
            results = {}
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            
            if choice == '1':
                print("\n🔧 Creating sample pending items...")
                results = repair.create_sample_pending_items(10)
                
            elif choice == '2':
                print("\n🔧 Creating retroactive audit trail...")
                results = repair.retroactively_mark_live_items_approved()
                
            elif choice == '3':
                confirm = input("⚠️  This will DELETE all pending_books data. Type 'CONFIRM' to proceed: ")
                if confirm == 'CONFIRM':
                    print("\n🗑️  Clearing existing data...")
                    clear_results = repair.clear_existing_pending_books()
                    print(f"✅ Cleared: {clear_results}")
                    
                    print("\n🔧 Creating sample pending items...")
                    results = repair.create_sample_pending_items(10)
                else:
                    print("❌ Operation cancelled")
                    continue
                    
            elif choice == '4':
                print("\n🔧 Running combined approach...")
                
                # Retroactive approval
                retro_results = repair.retroactively_mark_live_items_approved()
                print(f"✅ Retroactive approval: {retro_results.get('marked_approved', 0)} items")
                
                # Add sample items
                sample_results = repair.create_sample_pending_items(5)
                print(f"✅ Sample items: {sample_results.get('created_count', 0)} items")
                
                results = {
                    'retroactive_results': retro_results,
                    'sample_results': sample_results
                }
                
            else:
                print("❌ Invalid choice. Please enter 1-4 or 'q'")
                continue
            
            # Save results
            filename = f'repair_results_{timestamp}.json'
            with open(filename, 'w') as f:
                json.dump(results, f, indent=2, default=str)
            
            print(f"\n✅ Repair completed! Results saved to: {filename}")
            print("\n🎯 NEXT STEPS:")
            print("   1. Check your admin dashboard - you should now see pending items")
            print("   2. Test the approval workflow")
            print("   3. Verify LinkedIn scheduling works")
            print("   4. Set up proper workflow for future items")
            
            break
        
    except Exception as e:
        logger.error(f"❌ Repair failed: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main()) 