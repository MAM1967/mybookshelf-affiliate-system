#!/usr/bin/env python3
"""
Insert Scraped Items into Database
Inserts all successfully scraped items with ASINs into Supabase
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
            logger.error("Please set: SUPABASE_URL, SUPABASE_ANON_KEY")
            sys.exit(1)
        
        # Initialize Supabase client
        try:
            from supabase.client import create_client, Client
            self.supabase: Client = create_client(self.supabase_url, self.supabase_key)
            logger.info("✅ Supabase client initialized")
        except ImportError:
            logger.error("❌ Supabase library not installed. Run: pip install supabase")
            sys.exit(1)
        except Exception as e:
            logger.error(f"❌ Failed to initialize Supabase client: {e}")
            sys.exit(1)
    
    def load_scraped_data(self, filename: str) -> Dict:
        """Load the scraped data from JSON file"""
        try:
            with open(filename, 'r') as f:
                data = json.load(f)
            logger.info(f"✅ Loaded scraped data from: {filename}")
            return data
        except FileNotFoundError:
            logger.error(f"❌ Scraped data file not found: {filename}")
            sys.exit(1)
        except json.JSONDecodeError as e:
            logger.error(f"❌ Invalid JSON in file: {e}")
            sys.exit(1)
    
    def prepare_book_data(self, book: Dict) -> Optional[Dict]:
        """Prepare book data for database insertion"""
        if book['scrape_status'] != 'found':
            return None
        
        # Extract focus area from book data
        focus_area = book.get('focus_area', '')
        if not focus_area and book.get('christian_themes'):
            focus_area = 'Christian Leadership'
        elif not focus_area and book.get('leadership_topics'):
            focus_area = 'Leadership'
        
        return {
            'title': book['title'],
            'author': book['author'],
            'price': book['price'],
            'affiliate_link': book['affiliate_link'],
            'image_url': book['image_url'],
            'category': 'Books',
            'asin': book['asin'],
            'rating': book['rating'],
            'review_count': book['review_count'],
            'description': book.get('description', ''),
            'focus_area': focus_area,
            'christian_themes': book.get('christian_themes', []),
            'leadership_topics': book.get('leadership_topics', []),
            'is_active': True,
            'created_at': time.strftime('%Y-%m-%d %H:%M:%S')
        }
    
    def prepare_accessory_data(self, accessory: Dict) -> Optional[Dict]:
        """Prepare accessory data for database insertion"""
        if accessory['scrape_status'] != 'found':
            return None
        
        return {
            'title': accessory['title'],
            'author': 'N/A',  # Accessories don't have authors
            'price': accessory['price'],
            'affiliate_link': accessory['affiliate_link'],
            'image_url': accessory['image_url'],
            'category': 'accessories',
            'asin': accessory['asin'],
            'rating': accessory['rating'],
            'review_count': accessory['review_count'],
            'description': accessory.get('description', ''),
            'focus_area': accessory.get('accessory_type', ''),
            'christian_themes': [],
            'leadership_topics': [],
            'is_active': True,
            'created_at': time.strftime('%Y-%m-%d %H:%M:%S')
        }
    
    def insert_items(self, data: Dict) -> Dict:
        """Insert all found items into the database"""
        logger.info("🚀 Starting database insertion...")
        
        results = {
            'total_items': 0,
            'books_inserted': 0,
            'accessories_inserted': 0,
            'errors': [],
            'inserted_items': []
        }
        
        # Insert books
        for category, books in data['books'].items():
            logger.info(f"📚 Processing {len(books)} books in category: {category}")
            
            for book in books:
                results['total_items'] += 1
                
                if book['scrape_status'] == 'found':
                    book_data = self.prepare_book_data(book)
                    if book_data:
                        try:
                            # Check if item already exists
                            existing = self.supabase.table('books_accessories').select('id').eq('asin', book['asin']).execute()
                            
                            if existing.data:
                                logger.info(f"⏭️  Skipping existing book: {book['title']}")
                                continue
                            
                            # Insert new book
                            response = self.supabase.table('books_accessories').insert(book_data).execute()
                            
                            if response.data:
                                results['books_inserted'] += 1
                                results['inserted_items'].append({
                                    'title': book['title'],
                                    'asin': book['asin'],
                                    'type': 'book'
                                })
                                logger.info(f"✅ Inserted book: {book['title']} (ASIN: {book['asin']})")
                            else:
                                error_msg = f"Failed to insert book: {book['title']}"
                                results['errors'].append(error_msg)
                                logger.error(f"❌ {error_msg}")
                                
                        except Exception as e:
                            error_msg = f"Error inserting book {book['title']}: {str(e)}"
                            results['errors'].append(error_msg)
                            logger.error(f"❌ {error_msg}")
                else:
                    logger.warning(f"⚠️  Skipping book not found: {book['title']}")
        
        # Insert accessories
        logger.info(f"🛍️  Processing {len(data['accessories'])} accessories")
        
        for accessory in data['accessories']:
            results['total_items'] += 1
            
            if accessory['scrape_status'] == 'found':
                accessory_data = self.prepare_accessory_data(accessory)
                if accessory_data:
                    try:
                        # Check if item already exists
                        existing = self.supabase.table('books_accessories').select('id').eq('asin', accessory['asin']).execute()
                        
                        if existing.data:
                            logger.info(f"⏭️  Skipping existing accessory: {accessory['title']}")
                            continue
                        
                        # Insert new accessory
                        response = self.supabase.table('books_accessories').insert(accessory_data).execute()
                        
                        if response.data:
                            results['accessories_inserted'] += 1
                            results['inserted_items'].append({
                                'title': accessory['title'],
                                'asin': accessory['asin'],
                                'type': 'accessory'
                            })
                            logger.info(f"✅ Inserted accessory: {accessory['title']} (ASIN: {accessory['asin']})")
                        else:
                            error_msg = f"Failed to insert accessory: {accessory['title']}"
                            results['errors'].append(error_msg)
                            logger.error(f"❌ {error_msg}")
                            
                    except Exception as e:
                        error_msg = f"Error inserting accessory {accessory['title']}: {str(e)}"
                        results['errors'].append(error_msg)
                        logger.error(f"❌ {error_msg}")
            else:
                logger.warning(f"⚠️  Skipping accessory not found: {accessory['title']}")
        
        return results
    
    def save_insertion_report(self, results: Dict, filename: str = None):
        """Save insertion results to a report file"""
        if not filename:
            timestamp = time.strftime('%Y%m%d_%H%M%S')
            filename = f'database_insertion_report_{timestamp}.json'
        
        with open(filename, 'w') as f:
            json.dump(results, f, indent=2)
        
        logger.info(f"✅ Insertion report saved to: {filename}")
        
        # Print summary
        print(f"\n📊 DATABASE INSERTION SUMMARY")
        print(f"{'='*50}")
        print(f"Total Items Processed: {results['total_items']}")
        print(f"Books Inserted: {results['books_inserted']}")
        print(f"Accessories Inserted: {results['accessories_inserted']}")
        print(f"Total Inserted: {results['books_inserted'] + results['accessories_inserted']}")
        print(f"Errors: {len(results['errors'])}")
        
        if results['errors']:
            print(f"\n❌ ERRORS:")
            print(f"{'='*50}")
            for error in results['errors'][:5]:  # Show first 5 errors
                print(f"• {error}")
            if len(results['errors']) > 5:
                print(f"... and {len(results['errors']) - 5} more errors")
        
        if results['inserted_items']:
            print(f"\n✅ SUCCESSFULLY INSERTED ITEMS:")
            print(f"{'='*50}")
            for item in results['inserted_items'][:10]:  # Show first 10 items
                print(f"• {item['title']} ({item['type']}) - ASIN: {item['asin']}")
            if len(results['inserted_items']) > 10:
                print(f"... and {len(results['inserted_items']) - 10} more items")

def main():
    """Main execution function"""
    print("🚀 Database Insertion for Scraped Items")
    print("=" * 50)
    
    # Find the most recent scraping results file
    import glob
    scraping_files = glob.glob('amazon_scraping_results_*.json')
    
    if not scraping_files:
        print("❌ No scraping results files found!")
        print("Please run the Amazon scraper first: python3 amazon_scraper.py")
        sys.exit(1)
    
    # Use the most recent file
    latest_file = max(scraping_files, key=os.path.getctime)
    print(f"📁 Using scraping results: {latest_file}")
    
    # Initialize inserter
    inserter = DatabaseInserter()
    
    # Load scraped data
    data = inserter.load_scraped_data(latest_file)
    
    # Check if we have found items
    found_count = data.get('items_found', 0)
    if found_count == 0:
        print("❌ No items found in scraping results!")
        sys.exit(1)
    
    print(f"📊 Found {found_count} items to insert")
    print()
    
    # Confirm before proceeding
    response = input("Proceed with database insertion? (y/N): ").strip().lower()
    if response != 'y':
        print("❌ Insertion cancelled")
        sys.exit(0)
    
    # Insert items
    try:
        results = inserter.insert_items(data)
        inserter.save_insertion_report(results)
        
        print(f"\n🎉 Database insertion complete!")
        print(f"Next steps:")
        print(f"1. Verify items in your Supabase dashboard")
        print(f"2. Test the affiliate links")
        print(f"3. Update your LinkedIn posting schedule")
        
    except KeyboardInterrupt:
        print(f"\n\n⏹️  Insertion interrupted by user")
        print("💾 Partial results may be available")

if __name__ == "__main__":
    main() 