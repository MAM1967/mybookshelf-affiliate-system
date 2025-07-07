#!/usr/bin/env python3
"""
Manual ASIN Research Helper
Assists with manual research of Amazon ASINs for books and accessories
"""

import json
import os
import sys
from urllib.parse import quote_plus
from typing import Dict, List, Optional

class ManualASINHelper:
    def __init__(self, research_file: str):
        self.research_file = research_file
        self.data = self.load_research_data()
        self.amazon_associate_tag = "mybookshelf-20"
    
    def load_research_data(self) -> Dict:
        """Load the research data from JSON file"""
        try:
            with open(self.research_file, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            print(f"❌ Research file not found: {self.research_file}")
            sys.exit(1)
        except json.JSONDecodeError as e:
            print(f"❌ Invalid JSON: {e}")
            sys.exit(1)
    
    def generate_amazon_search_url(self, title: str, author: str = "") -> str:
        """Generate Amazon search URL for manual research"""
        search_query = f"{title} {author}".strip()
        encoded_query = quote_plus(search_query)
        return f"https://www.amazon.com/s?k={encoded_query}"
    
    def generate_affiliate_link(self, asin: str) -> str:
        """Generate Amazon affiliate link"""
        return f"https://amazon.com/dp/{asin}?tag={self.amazon_associate_tag}"
    
    def get_items_needing_research(self) -> List[Dict]:
        """Get all items that need manual research"""
        items = []
        
        # Get books needing research
        for category, books in self.data['books'].items():
            for book in books:
                if book['research_status'] == 'manual_research_needed':
                    items.append({
                        'type': 'book',
                        'category': category,
                        'item': book
                    })
        
        # Get accessories needing research
        for accessory in self.data['accessories']:
            if accessory['research_status'] == 'manual_research_needed':
                items.append({
                    'type': 'accessory',
                    'category': 'accessories',
                    'item': accessory
                })
        
        return items
    
    def display_research_item(self, item_data: Dict, index: int, total: int):
        """Display a single item for research"""
        item = item_data['item']
        item_type = item_data['type']
        
        print(f"\n{'='*80}")
        print(f"📋 ITEM {index + 1} OF {total}")
        print(f"{'='*80}")
        
        if item_type == 'book':
            print(f"📖 TITLE: {item['title']}")
            print(f"👤 AUTHOR: {item['author']}")
            print(f"📚 CATEGORY: {item_data['category']}")
            print(f"📝 DESCRIPTION: {item['description']}")
            print(f"🎯 FOCUS AREA: {item['focus_area']}")
        else:
            print(f"🛍️  TITLE: {item['title']}")
            print(f"📝 DESCRIPTION: {item['description']}")
            print(f"🎯 TARGET AUDIENCE: {item.get('target_audience', 'N/A')}")
            print(f"💰 PRICE RANGE: {item.get('price_range', 'N/A')}")
        
        # Generate Amazon search URL
        if item_type == 'book':
            search_url = self.generate_amazon_search_url(item['title'], item['author'])
        else:
            search_url = self.generate_amazon_search_url(item['title'])
        
        print(f"\n🔍 AMAZON SEARCH URL:")
        print(f"{search_url}")
        
        print(f"\n📋 RESEARCH INSTRUCTIONS:")
        print(f"1. Click the Amazon search URL above")
        print(f"2. Find the correct item (usually first result)")
        print(f"3. Copy the ASIN from the product URL")
        print(f"4. Note the current price")
        print(f"5. Copy the main product image URL")
        print(f"6. Note the rating and review count")
        
        return search_url
    
    def update_item_data(self, item_data: Dict, asin: str, price: Optional[float], image_url: Optional[str], rating: Optional[float] = None, review_count: Optional[int] = None):
        """Update item data with research results"""
        item = item_data['item']
        
        # Update the item data
        item['asin'] = asin
        item['price'] = price
        item['affiliate_link'] = self.generate_affiliate_link(asin)
        item['image_url'] = image_url
        item['rating'] = rating
        item['review_count'] = review_count
        item['research_status'] = 'found'
        
        print(f"✅ Updated: {item['title']}")
        print(f"   ASIN: {asin}")
        print(f"   Price: ${price}")
        print(f"   Affiliate Link: {item['affiliate_link']}")
    
    def save_updated_data(self, output_file: str = None):
        """Save the updated research data"""
        if not output_file:
            output_file = self.research_file.replace('.json', '_updated.json')
        
        with open(output_file, 'w') as f:
            json.dump(self.data, f, indent=2)
        
        print(f"\n✅ Updated data saved to: {output_file}")
        
        # Update summary
        total_items = self.data['total_items']
        items_found = sum(1 for item in self.get_items_needing_research() if item['item']['research_status'] == 'found')
        items_needing_research = total_items - items_found
        
        self.data['items_found'] = items_found
        self.data['items_needing_manual_research'] = items_needing_research
        
        print(f"\n📊 UPDATED SUMMARY:")
        print(f"Total Items: {total_items}")
        print(f"Items Found: {items_found}")
        print(f"Items Needing Research: {items_needing_research}")
        print(f"Success Rate: {(items_found/total_items*100):.1f}%")
    
    def interactive_research(self):
        """Interactive research session"""
        items = self.get_items_needing_research()
        
        if not items:
            print("🎉 All items have been researched!")
            return
        
        print(f"🚀 Starting manual research for {len(items)} items")
        print("Press Ctrl+C to save and exit at any time")
        
        try:
            for i, item_data in enumerate(items):
                if item_data['item']['research_status'] == 'found':
                    continue
                
                search_url = self.display_research_item(item_data, i, len(items))
                
                # Get user input
                print(f"\n📝 ENTER RESEARCH DATA:")
                asin = input("ASIN (e.g., B08XXXXX): ").strip()
                
                if not asin:
                    print("⏭️  Skipping this item...")
                    continue
                
                price_str = input("Price (e.g., 29.99): ").strip()
                price = float(price_str) if price_str else None
                
                image_url = input("Image URL: ").strip()
                
                rating_str = input("Rating (e.g., 4.5, optional): ").strip()
                rating = float(rating_str) if rating_str else None
                
                review_count_str = input("Review count (e.g., 1250, optional): ").strip()
                review_count = int(review_count_str) if review_count_str else None
                
                # Update the data
                self.update_item_data(item_data, asin, price, image_url, rating, review_count)
                
                # Save after each item
                self.save_updated_data()
                
                print(f"\n⏭️  Press Enter to continue to next item...")
                input()
        
        except KeyboardInterrupt:
            print(f"\n\n💾 Saving progress...")
            self.save_updated_data()
            print("✅ Progress saved. You can resume later.")
    
    def generate_research_report(self):
        """Generate a research report with all items needing manual research"""
        items = self.get_items_needing_research()
        
        print(f"📋 MANUAL RESEARCH REPORT")
        print(f"{'='*80}")
        print(f"Total items needing research: {len(items)}")
        print(f"Generated: {self.data['research_date']}")
        print()
        
        # Books by category
        book_categories = {}
        accessories = []
        
        for item_data in items:
            if item_data['type'] == 'book':
                category = item_data['category']
                if category not in book_categories:
                    book_categories[category] = []
                book_categories[category].append(item_data['item'])
            else:
                accessories.append(item_data['item'])
        
        # Display books by category
        for category, books in book_categories.items():
            print(f"📚 {category.upper().replace('_', ' ')} ({len(books)} books)")
            print(f"{'-'*60}")
            
            for i, book in enumerate(books, 1):
                search_url = self.generate_amazon_search_url(book['title'], book['author'])
                print(f"{i:2d}. {book['title']} by {book['author']}")
                print(f"    Search: {search_url}")
                print()
        
        # Display accessories
        if accessories:
            print(f"🛍️  ACCESSORIES ({len(accessories)} items)")
            print(f"{'-'*60}")
            
            for i, accessory in enumerate(accessories, 1):
                search_url = self.generate_amazon_search_url(accessory['title'])
                print(f"{i:2d}. {accessory['title']}")
                print(f"    Search: {search_url}")
                print()
        
        print(f"✅ Research report complete!")
        print(f"💡 Use the search URLs above to find ASINs manually")

def main():
    """Main execution function"""
    if len(sys.argv) < 2:
        print("Usage: python3 manual_asin_research_helper.py <research_file.json>")
        print("Example: python3 manual_asin_research_helper.py asin_research_results_20250704_193941.json")
        sys.exit(1)
    
    research_file = sys.argv[1]
    
    if not os.path.exists(research_file):
        print(f"❌ Research file not found: {research_file}")
        sys.exit(1)
    
    helper = ManualASINHelper(research_file)
    
    print("🔍 Manual ASIN Research Helper")
    print("=" * 50)
    
    # Check current status
    items_needing_research = helper.get_items_needing_research()
    total_items = helper.data['total_items']
    items_found = total_items - len(items_needing_research)
    
    print(f"📊 CURRENT STATUS:")
    print(f"Total Items: {total_items}")
    print(f"Items Found: {items_found}")
    print(f"Items Needing Research: {len(items_needing_research)}")
    print(f"Success Rate: {(items_found/total_items*100):.1f}%")
    
    if len(items_needing_research) == 0:
        print("\n🎉 All items have been researched!")
        return
    
    print(f"\n🎯 OPTIONS:")
    print(f"1. Interactive research session")
    print(f"2. Generate research report")
    print(f"3. Exit")
    
    choice = input("\nSelect option (1-3): ").strip()
    
    if choice == "1":
        helper.interactive_research()
    elif choice == "2":
        helper.generate_research_report()
    elif choice == "3":
        print("👋 Goodbye!")
    else:
        print("❌ Invalid choice")

if __name__ == "__main__":
    main() 