#!/usr/bin/env python3
"""
Check Existing Items in Database
Checks what items already exist to prevent duplicates during insertion
"""

import os
import sys
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def check_existing_items():
    """Check what items already exist in the database"""
    supabase_url = os.getenv('SUPABASE_URL')
    supabase_key = os.getenv('SUPABASE_ANON_KEY')
    
    if not all([supabase_url, supabase_key]):
        logger.error("❌ Supabase credentials not found in environment variables")
        logger.error("Please set: SUPABASE_URL, SUPABASE_ANON_KEY")
        sys.exit(1)
    
    try:
        from supabase.client import create_client, Client
        supabase: Client = create_client(supabase_url, supabase_key)
        logger.info("✅ Supabase client initialized")
    except Exception as e:
        logger.error(f"❌ Failed to initialize Supabase client: {e}")
        sys.exit(1)
    
    # Get all existing items
    try:
        response = supabase.table('books_accessories').select('*').execute()
        existing_items = response.data
        
        logger.info(f"📊 Found {len(existing_items)} existing items in database")
        
        if existing_items:
            print(f"\n📋 EXISTING ITEMS IN DATABASE:")
            print(f"{'='*60}")
            
            books_count = 0
            accessories_count = 0
            
            for item in existing_items:
                if item.get('category') == 'Books':
                    books_count += 1
                    print(f"📖 {item.get('title', 'N/A')} by {item.get('author', 'N/A')}")
                else:
                    accessories_count += 1
                    print(f"🛍️  {item.get('title', 'N/A')}")
            
            print(f"\n📊 SUMMARY:")
            print(f"{'='*60}")
            print(f"Total Items: {len(existing_items)}")
            print(f"Books: {books_count}")
            print(f"Accessories: {accessories_count}")
            
            # Check for potential duplicates by title
            titles = [item.get('title', '').lower().strip() for item in existing_items]
            unique_titles = set(titles)
            
            if len(titles) != len(unique_titles):
                print(f"\n⚠️  DUPLICATE TITLES FOUND:")
                print(f"{'='*60}")
                seen = set()
                duplicates = []
                for title in titles:
                    if title in seen:
                        duplicates.append(title)
                    else:
                        seen.add(title)
                
                for dup in set(duplicates):
                    print(f"• {dup}")
            
            return existing_items
        else:
            print(f"\n📋 Database is empty - no existing items")
            return []
            
    except Exception as e:
        logger.error(f"❌ Error checking existing items: {e}")
        return []

def check_for_duplicates(scraped_data, existing_items):
    """Check for potential duplicates between scraped data and existing items"""
    print(f"\n🔍 CHECKING FOR POTENTIAL DUPLICATES:")
    print(f"{'='*60}")
    
    existing_titles = [item.get('title', '').lower().strip() for item in existing_items]
    existing_titles_set = set(existing_titles)
    
    potential_duplicates = []
    new_items = []
    
    # Check books
    for category, books in scraped_data['books'].items():
        for book in books:
            if book['scrape_status'] == 'found':
                title = book['title'].lower().strip()
                if title in existing_titles_set:
                    potential_duplicates.append({
                        'title': book['title'],
                        'author': book['author'],
                        'type': 'book',
                        'asin': book.get('asin', 'N/A')
                    })
                else:
                    new_items.append({
                        'title': book['title'],
                        'author': book['author'],
                        'type': 'book',
                        'asin': book.get('asin', 'N/A')
                    })
    
    # Check accessories
    for accessory in scraped_data['accessories']:
        if accessory['scrape_status'] == 'found':
            title = accessory['title'].lower().strip()
            if title in existing_titles_set:
                potential_duplicates.append({
                    'title': accessory['title'],
                    'author': 'N/A',
                    'type': 'accessory',
                    'asin': accessory.get('asin', 'N/A')
                })
            else:
                new_items.append({
                    'title': accessory['title'],
                    'author': 'N/A',
                    'type': 'accessory',
                    'asin': accessory.get('asin', 'N/A')
                })
    
    print(f"✅ New items to insert: {len(new_items)}")
    print(f"⚠️  Potential duplicates: {len(potential_duplicates)}")
    
    if potential_duplicates:
        print(f"\n⚠️  POTENTIAL DUPLICATES (will be skipped):")
        print(f"{'='*60}")
        for dup in potential_duplicates[:10]:  # Show first 10
            print(f"• {dup['title']} ({dup['type']}) - ASIN: {dup['asin']}")
        if len(potential_duplicates) > 10:
            print(f"... and {len(potential_duplicates) - 10} more")
    
    if new_items:
        print(f"\n✅ NEW ITEMS TO INSERT:")
        print(f"{'='*60}")
        for item in new_items[:10]:  # Show first 10
            print(f"• {item['title']} ({item['type']}) - ASIN: {item['asin']}")
        if len(new_items) > 10:
            print(f"... and {len(new_items) - 10} more")
    
    return new_items, potential_duplicates

def main():
    """Main execution function"""
    print("🔍 Checking Existing Items in Database")
    print("=" * 50)
    
    # Check existing items
    existing_items = check_existing_items()
    
    # Load scraped data
    import json
    import glob
    
    scraping_files = glob.glob('amazon_scraping_results_*.json')
    if not scraping_files:
        print("❌ No scraping results files found!")
        sys.exit(1)
    
    latest_file = max(scraping_files, key=os.path.getctime)
    print(f"\n📁 Using scraping results: {latest_file}")
    
    try:
        with open(latest_file, 'r') as f:
            scraped_data = json.load(f)
    except Exception as e:
        print(f"❌ Error loading scraped data: {e}")
        sys.exit(1)
    
    # Check for duplicates
    new_items, duplicates = check_for_duplicates(scraped_data, existing_items)
    
    print(f"\n📊 FINAL SUMMARY:")
    print(f"{'='*60}")
    print(f"Existing items in database: {len(existing_items)}")
    print(f"Items found by scraper: {scraped_data.get('items_found', 0)}")
    print(f"New items to insert: {len(new_items)}")
    print(f"Potential duplicates (will be skipped): {len(duplicates)}")
    
    if len(new_items) > 0:
        print(f"\n✅ Ready to insert {len(new_items)} new items!")
        print(f"Run: python3 insert_simple.py")
    else:
        print(f"\n⚠️  No new items to insert - all items already exist in database")

if __name__ == "__main__":
    main() 