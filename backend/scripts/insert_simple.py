#!/usr/bin/env python3
"""
Simple Database Insertion for Scraped Items
Inserts items using only the existing columns in books_accessories table
"""

import json
import os
import sys
import time
import glob
from typing import Dict, List, Optional
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class SimpleInserter:
    def __init__(self):
        self.supabase_url = os.getenv('SUPABASE_URL')
        self.supabase_key = os.getenv('SUPABASE_ANON_KEY')
        
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
    
    def prepare_item_data(self, item: Dict) -> Optional[Dict]:
        """Prepare item data for database insertion (using only existing columns)"""
        if item['scrape_status'] != 'found':
            return None
        
        # Only use columns that exist in the current schema
        return {
            'title': item['title'],
            'author': item['author'],
            'price': item['price'] if item['price'] else 0.0,
            'affiliate_link': item['affiliate_link'] if item['affiliate_link'] else '',
            'image_url': item['image_url'] if item['image_url'] else '',
            'category': item['category']
        }
    
    def insert_items(self, data: Dict) -> Dict:
        """Insert all found items into the database"""
        logger.info("🚀 Starting simple database insertion...")
        
        # First, get existing items to check for duplicates
        try:
            existing_response = self.supabase.table('books_accessories').select('title').execute()
            existing_titles = {item.get('title', '').lower().strip() for item in existing_response.data}
            logger.info(f"📋 Found {len(existing_titles)} existing items to check against")
        except Exception as e:
            logger.error(f"❌ Error getting existing items: {e}")
            existing_titles = set()
        
        results = {
            'total_items': 0,
            'books_inserted': 0,
            'accessories_inserted': 0,
            'duplicates_skipped': 0,
            'errors': [],
            'inserted_items': []
        }
        
        # Insert books
        for category, books in data['books'].items():
            logger.info(f"📚 Processing {len(books)} books in category: {category}")
            
            for book in books:
                results['total_items'] += 1
                
                if book['scrape_status'] == 'found':
                    # Check for duplicates
                    title = book['title'].lower().strip()
                    if title in existing_titles:
                        logger.info(f"⏭️  Skipping duplicate book: {book['title']}")
                        results['duplicates_skipped'] += 1
                        continue
                    
                    book_data = self.prepare_item_data(book)
                    if book_data:
                        try:
                            # Insert new book
                            response = self.supabase.table('books_accessories').insert(book_data).execute()
                            
                            if response.data:
                                results['books_inserted'] += 1
                                results['inserted_items'].append({
                                    'title': book['title'],
                                    'asin': book.get('asin', 'N/A'),
                                    'type': 'book'
                                })
                                logger.info(f"✅ Inserted book: {book['title']}")
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
                # Check for duplicates
                title = accessory['title'].lower().strip()
                if title in existing_titles:
                    logger.info(f"⏭️  Skipping duplicate accessory: {accessory['title']}")
                    results['duplicates_skipped'] += 1
                    continue
                
                accessory_data = self.prepare_item_data(accessory)
                if accessory_data:
                    try:
                        # Insert new accessory
                        response = self.supabase.table('books_accessories').insert(accessory_data).execute()
                        
                        if response.data:
                            results['accessories_inserted'] += 1
                            results['inserted_items'].append({
                                'title': accessory['title'],
                                'asin': accessory.get('asin', 'N/A'),
                                'type': 'accessory'
                            })
                            logger.info(f"✅ Inserted accessory: {accessory['title']}")
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
            filename = f'simple_insertion_report_{timestamp}.json'
        
        with open(filename, 'w') as f:
            json.dump(results, f, indent=2)
        
        logger.info(f"✅ Insertion report saved to: {filename}")
        
        # Print summary
        print(f"\n📊 SIMPLE INSERTION SUMMARY")
        print(f"{'='*50}")
        print(f"Total Items Processed: {results['total_items']}")
        print(f"Books Inserted: {results['books_inserted']}")
        print(f"Accessories Inserted: {results['accessories_inserted']}")
        print(f"Total Inserted: {results['books_inserted'] + results['accessories_inserted']}")
        print(f"Duplicates Skipped: {results['duplicates_skipped']}")
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
    print("🚀 Simple Database Insertion for Scraped Items")
    print("=" * 50)
    
    # Find the most recent scraping results file
    scraping_files = glob.glob('amazon_scraping_results_*.json')
    
    if not scraping_files:
        print("❌ No scraping results files found!")
        print("Please run the Amazon scraper first: python3 amazon_scraper.py")
        sys.exit(1)
    
    # Use the most recent file
    latest_file = max(scraping_files, key=os.path.getctime)
    print(f"📁 Using scraping results: {latest_file}")
    
    # Initialize inserter
    inserter = SimpleInserter()
    
    # Load scraped data
    data = inserter.load_scraped_data(latest_file)
    
    # Check if we have found items
    found_count = data.get('items_found', 0)
    if found_count == 0:
        print("❌ No items found in scraping results!")
        sys.exit(1)
    
    print(f"📊 Found {found_count} items to insert")
    print("⚠️  Note: This will only insert basic fields (title, author, price, affiliate_link, image_url, category)")
    print("   Additional fields like ASIN, rating, etc. will be added after database schema update")
    print()
    
    # Confirm before proceeding
    response = input("Proceed with simple database insertion? (y/N): ").strip().lower()
    if response != 'y':
        print("❌ Insertion cancelled")
        sys.exit(0)
    
    # Insert items
    try:
        results = inserter.insert_items(data)
        inserter.save_insertion_report(results)
        
        print(f"\n🎉 Simple database insertion complete!")
        print(f"Next steps:")
        print(f"1. Run the SQL migration in Supabase dashboard: backend/supabase/add_missing_columns.sql")
        print(f"2. Run the full insertion script to add ASINs and other fields")
        print(f"3. Verify items in your Supabase dashboard")
        
    except KeyboardInterrupt:
        print(f"\n\n⏹️  Insertion interrupted by user")
        print("💾 Partial results may be available")

if __name__ == "__main__":
    main() 