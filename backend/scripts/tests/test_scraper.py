#!/usr/bin/env python3
"""
Test Amazon Scraper
Tests the scraper with a few sample items
"""

import json
from amazon_scraper import AmazonScraper

def test_scraper():
    """Test the scraper with sample items"""
    print("🧪 Testing Amazon Scraper")
    print("=" * 40)
    
    # Initialize scraper
    scraper = AmazonScraper()
    
    # Test items
    test_items = [
        {"title": "Atomic Habits", "author": "James Clear", "type": "book"},
        {"title": "The Five Dysfunctions of a Team", "author": "Patrick Lencioni", "type": "book"},
        {"title": "Kindle Paperwhite", "author": "", "type": "accessory"}
    ]
    
    results = []
    
    for item in test_items:
        print(f"\n🔍 Testing: {item['title']}")
        
        if item['type'] == 'book':
            search_query = f"{item['title']} {item['author']}"
            products = scraper.search_amazon(search_query, "Books")
        else:
            search_query = item['title']
            products = scraper.search_amazon(search_query, "All")
        
        if products:
            best_match = scraper.find_best_match(products, item['title'], item['author'])
            if best_match:
                print(f"✅ Found: {best_match['title']}")
                print(f"   ASIN: {best_match['asin']}")
                print(f"   Price: ${best_match['price']}")
                print(f"   Rating: {best_match['rating']}")
                print(f"   Relevance Score: {best_match['relevance_score']}")
                
                results.append({
                    'original': item,
                    'found': best_match,
                    'status': 'found'
                })
            else:
                print(f"⚠️  No good match found")
                results.append({
                    'original': item,
                    'found': None,
                    'status': 'no_match'
                })
        else:
            print(f"❌ No products found")
            results.append({
                'original': item,
                'found': None,
                'status': 'not_found'
            })
    
    # Summary
    print(f"\n📊 TEST SUMMARY")
    print(f"{'='*40}")
    found_count = sum(1 for r in results if r['status'] == 'found')
    print(f"Items Tested: {len(test_items)}")
    print(f"Items Found: {found_count}")
    print(f"Success Rate: {(found_count/len(test_items)*100):.1f}%")
    
    if found_count > 0:
        print(f"\n✅ Scraper is working! Ready for full inventory.")
    else:
        print(f"\n❌ Scraper needs adjustment. Check Amazon's HTML structure.")

if __name__ == "__main__":
    test_scraper() 