#!/usr/bin/env python3
"""
Database Insertion Script for MyBookshelf
Inserts researched items with ASINs into Supabase database
"""

import json
import os
import sys
import time
from typing import Dict, List, Optional
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class DatabaseInserter:
    def __init__(self):
        self.supabase_url = os.getenv('SUPABASE_URL')
        self.supabase_key = os.getenv('SUPABASE_ANON_KEY')
        self.supabase_service_key = os.getenv('SUPABASE_SERVICE_ROLE_KEY')
        
        if not all([self.supabase_url, self.supabase_key]):
            logger.error("❌ Supabase credentials not found in environment variables")
            logger.error("Please set SUPABASE_URL and SUPABASE_ANON_KEY")
            sys.exit(1)
        
        try:
            from supabase.client import create_client, Client
            if not self.supabase_url or not self.supabase_key:
                raise ValueError("Missing Supabase credentials")
            self.supabase: Client = create_client(self.supabase_url, self.supabase_key)
            logger.info("✅ Supabase client initialized")
        except ImportError:
            logger.error("❌ Supabase library not found")
            logger.error("Install with: pip install supabase")
            sys.exit(1)
        except Exception as e:
            logger.error(f"❌ Failed to initialize Supabase: {e}")
            sys.exit(1)
    
    def load_research_data(self, filename: str) -> Dict:
        """Load research data from JSON file"""
        try:
            with open(filename, 'r') as f:
                data = json.load(f)
            logger.info(f"✅ Loaded research data: {data['total_items']} items")
            return data
        except FileNotFoundError:
            logger.error(f"❌ Research file not found: {filename}")
            sys.exit(1)
        except json.JSONDecodeError as e:
            logger.error(f"❌ Invalid JSON: {e}")
            sys.exit(1)
    
    def get_ready_items(self, data: Dict) -> List[Dict]:
        """Get items that are ready for database insertion"""
        ready_items = []
        
        # Get books ready for insertion
        for category, books in data['books'].items():
            for book in books:
                if book['research_status'] == 'found' and book['asin']:
                    ready_items.append({
                        'type': 'book',
                        'data': book
                    })
        
        # Get accessories ready for insertion
        for accessory in data['accessories']:
            if accessory['research_status'] == 'found' and accessory['asin']:
                ready_items.append({
                    'type': 'accessory',
                    'data': accessory
                })
        
        return ready_items
    
    def format_item_for_database(self, item_data: Dict) -> Dict:
        """Format item data for database insertion"""
        item = item_data['data']
        
        # Format for books_accessories table
        db_item = {
            'title': item['title'],
            'author': item.get('author', 'N/A'),  # Accessories might not have authors
            'price': item.get('price', 0.0),
            'affiliate_link': item.get('affiliate_link', ''),
            'image_url': item.get('image_url', ''),
            'category': item_data['type']  # 'book' or 'accessory'
        }
        
        return db_item
    
    def insert_item(self, item: Dict) -> bool:
        """Insert a single item into the database"""
        try:
            result = self.supabase.table('books_accessories').insert(item).execute()
            
            if result.data:
                logger.info(f"✅ Inserted: {item['title']}")
                return True
            else:
                logger.warning(f"⚠️  No data returned for: {item['title']}")
                return False
                
        except Exception as e:
            logger.error(f"❌ Failed to insert {item['title']}: {e}")
            return False
    
    def check_existing_items(self, items: List[Dict]) -> List[Dict]:
        """Check which items already exist in the database"""
        existing_titles = set()
        
        try:
            # Get all existing titles
            result = self.supabase.table('books_accessories').select('title').execute()
            
            for row in result.data:
                existing_titles.add(row['title'].lower())
            
            logger.info(f"📊 Found {len(existing_titles)} existing items in database")
            
        except Exception as e:
            logger.error(f"❌ Failed to check existing items: {e}")
            return items
        
        # Filter out existing items
        new_items = []
        for item in items:
            if item['title'].lower() not in existing_titles:
                new_items.append(item)
            else:
                logger.info(f"⏭️  Skipping existing item: {item['title']}")
        
        return new_items
    
    def insert_all_items(self, research_file: str, dry_run: bool = False) -> Dict:
        """Insert all ready items into the database"""
        data = self.load_research_data(research_file)
        ready_items = self.get_ready_items(data)
        
        if not ready_items:
            logger.warning("⚠️  No items ready for insertion")
            return {
                'total_items': 0,
                'inserted_items': 0,
                'failed_items': 0,
                'skipped_items': 0
            }
        
        logger.info(f"📊 Found {len(ready_items)} items ready for insertion")
        
        # Check for existing items
        new_items = self.check_existing_items(ready_items)
        skipped_count = len(ready_items) - len(new_items)
        
        if dry_run:
            logger.info("🔍 DRY RUN MODE - No items will be inserted")
            for item in new_items:
                logger.info(f"📝 Would insert: {item['title']}")
            
            return {
                'total_items': len(ready_items),
                'inserted_items': 0,
                'failed_items': 0,
                'skipped_items': skipped_count,
                'dry_run': True
            }
        
        # Insert items
        inserted_count = 0
        failed_count = 0
        
        for item_data in new_items:
            db_item = self.format_item_for_database(item_data)
            
            if self.insert_item(db_item):
                inserted_count += 1
            else:
                failed_count += 1
            
            # Rate limiting
            time.sleep(0.5)
        
        return {
            'total_items': len(ready_items),
            'inserted_items': inserted_count,
            'failed_items': failed_count,
            'skipped_items': skipped_count,
            'dry_run': False
        }
    
    def generate_insertion_report(self, results: Dict):
        """Generate a report of the insertion results"""
        print(f"\n📊 DATABASE INSERTION REPORT")
        print(f"{'='*60}")
        print(f"Total Items Ready: {results['total_items']}")
        print(f"Items Inserted: {results['inserted_items']}")
        print(f"Items Failed: {results['failed_items']}")
        print(f"Items Skipped (existing): {results['skipped_items']}")
        
        if results.get('dry_run'):
            print(f"Mode: DRY RUN (no actual insertion)")
        else:
            success_rate = (results['inserted_items'] / results['total_items'] * 100) if results['total_items'] > 0 else 0
            print(f"Success Rate: {success_rate:.1f}%")
        
        if results['inserted_items'] > 0:
            print(f"\n🎉 Successfully added {results['inserted_items']} items to database!")
        elif results['failed_items'] > 0:
            print(f"\n⚠️  {results['failed_items']} items failed to insert")
        else:
            print(f"\nℹ️  No new items to insert")

def main():
    """Main execution function"""
    if len(sys.argv) < 2:
        print("Usage: python3 database_insertion_script.py <research_file.json> [--dry-run]")
        print("Example: python3 database_insertion_script.py asin_research_results_20250704_193941_updated.json")
        print("Example: python3 database_insertion_script.py asin_research_results_20250704_193941_updated.json --dry-run")
        sys.exit(1)
    
    research_file = sys.argv[1]
    dry_run = '--dry-run' in sys.argv
    
    if not os.path.exists(research_file):
        print(f"❌ Research file not found: {research_file}")
        sys.exit(1)
    
    print("🚀 MyBookshelf Database Insertion")
    print("=" * 50)
    
    if dry_run:
        print("🔍 DRY RUN MODE - No items will be inserted")
    
    inserter = DatabaseInserter()
    
    # Insert items
    results = inserter.insert_all_items(research_file, dry_run)
    
    # Generate report
    inserter.generate_insertion_report(results)
    
    if not dry_run and results['inserted_items'] > 0:
        print(f"\n✅ Database insertion complete!")
        print(f"Next steps:")
        print(f"1. Verify items in Supabase dashboard")
        print(f"2. Test LinkedIn posting with new items")
        print(f"3. Monitor affiliate revenue from new items")

if __name__ == "__main__":
    main() 