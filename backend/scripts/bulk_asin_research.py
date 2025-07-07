#!/usr/bin/env python3
"""
Bulk ASIN Research Script for MyBookshelf
Researches Amazon ASINs for 75 books + 25 accessories
"""

import json
import os
import sys
import time
import requests
from typing import Dict, List, Optional
from urllib.parse import quote_plus
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class AmazonASINResearch:
    def __init__(self):
        self.amazon_access_key = os.getenv('AMAZON_ACCESS_KEY')
        self.amazon_secret_key = os.getenv('AMAZON_SECRET_KEY')
        self.amazon_associate_tag = os.getenv('AMAZON_ASSOCIATE_TAG', 'mybookshelf-20')
        self.use_amazon_api = bool(self.amazon_access_key and self.amazon_secret_key)
        
        # Initialize Amazon API if credentials available
        if self.use_amazon_api:
            try:
                from paapi5_python_sdk import DefaultApi, SearchItemsRequest, SearchItemsResource, PartnerType
                from paapi5_python_sdk.rest import ApiException
                
                self.amazon_api = DefaultApi(
                    access_key=self.amazon_access_key,
                    secret_key=self.amazon_secret_key,
                    host="webservices.amazon.com",
                    region="us-east-1"
                )
                self.SearchItemsRequest = SearchItemsRequest
                self.SearchItemsResource = SearchItemsResource
                self.PartnerType = PartnerType
                self.ApiException = ApiException
                
                logger.info("✅ Amazon PA API initialized")
            except ImportError:
                logger.warning("⚠️ Amazon PA API library not available")
                self.use_amazon_api = False
            except Exception as e:
                logger.warning(f"⚠️ Amazon API setup failed: {e}")
                self.use_amazon_api = False
        else:
            logger.info("ℹ️ Using manual research methods (no Amazon API credentials)")
    
    def load_inventory_data(self) -> Dict:
        """Load the inventory data from JSON file"""
        try:
            with open('../../books_and_accessories_2025.json', 'r') as f:
                data = json.load(f)
            logger.info(f"✅ Loaded inventory: {data['metadata']['total_books']} books, {data['metadata']['total_accessories']} accessories")
            return data
        except FileNotFoundError:
            logger.error("❌ books_and_accessories_2025.json not found")
            sys.exit(1)
        except json.JSONDecodeError as e:
            logger.error(f"❌ Invalid JSON: {e}")
            sys.exit(1)
    
    def search_amazon_api(self, title: str, author: str = "", category: str = "Books") -> Optional[Dict]:
        """Search Amazon using PA API"""
        if not self.use_amazon_api:
            return None
            
        try:
            # Create search query
            search_query = f"{title} {author}".strip()
            
            search_items_request = self.SearchItemsRequest(
                partner_tag=self.amazon_associate_tag,
                partner_type=self.PartnerType.ASSOCIATES,
                keywords=search_query,
                search_index=category,
                item_count=1,
                resources=[
                    self.SearchItemsResource.ITEMINFO_TITLE,
                    self.SearchItemsResource.ITEMINFO_BYLINEINFO,
                    self.SearchItemsResource.OFFERS_LISTINGS_PRICE,
                    self.SearchItemsResource.IMAGES_PRIMARY_LARGE
                ]
            )
            
            response = self.amazon_api.search_items(search_items_request)
            
            if hasattr(response, 'search_result') and response.search_result and hasattr(response.search_result, 'items') and response.search_result.items:
                item = response.search_result.items[0]
                
                # Extract data
                result = {
                    'asin': item.asin,
                    'title': item.item_info.title.display_value if item.item_info and item.item_info.title else title,
                    'author': item.item_info.by_line_info.contributors[0].name if item.item_info and item.item_info.by_line_info and item.item_info.by_line_info.contributors else author,
                    'price': None,
                    'image_url': None,
                    'rating': None,
                    'review_count': None
                }
                
                # Extract price
                if hasattr(item, 'offers') and item.offers and item.offers.listings:
                    result['price'] = float(item.offers.listings[0].price.display_amount)
                
                # Extract image
                if hasattr(item, 'images') and item.images and item.images.primary:
                    result['image_url'] = item.images.primary.large.url
                
                # Extract rating
                if hasattr(item, 'customer_reviews') and item.customer_reviews:
                    result['rating'] = item.customer_reviews.star_rating.value
                    result['review_count'] = item.customer_reviews.count
                
                return result
                
        except self.ApiException as e:
            logger.warning(f"⚠️ Amazon API error for '{title}': {e}")
        except Exception as e:
            logger.warning(f"⚠️ Search failed for '{title}': {e}")
        
        return None
    
    def search_amazon_manual(self, title: str, author: str = "", category: str = "Books") -> Optional[Dict]:
        """Manual Amazon search using web scraping fallback"""
        try:
            # Create search URL
            search_query = f"{title} {author}".strip()
            encoded_query = quote_plus(search_query)
            
            # Use a simple search approach (this is a fallback method)
            # In production, you might want to use a more sophisticated scraping approach
            search_url = f"https://www.amazon.com/s?k={encoded_query}"
            
            logger.info(f"🔍 Manual search: {search_url}")
            
            # For now, return None to indicate manual research needed
            return None
            
        except Exception as e:
            logger.warning(f"⚠️ Manual search failed for '{title}': {e}")
            return None
    
    def generate_affiliate_link(self, asin: str) -> str:
        """Generate Amazon affiliate link"""
        return f"https://amazon.com/dp/{asin}?tag={self.amazon_associate_tag}"
    
    def research_item(self, item: Dict, category: str) -> Dict:
        """Research a single item and return enriched data"""
        title = item.get('title', '')
        author = item.get('author', '')
        
        logger.info(f"🔍 Researching: {title} by {author}")
        
        # Try Amazon API first
        result = self.search_amazon_api(title, author, category)
        
        # Fallback to manual search
        if not result:
            result = self.search_amazon_manual(title, author, category)
        
        # Prepare enriched item data
        enriched_item = {
            'title': title,
            'author': author,
            'category': category,
            'description': item.get('description', ''),
            'christian_themes': item.get('christian_themes', []),
            'leadership_topics': item.get('leadership_topics', []),
            'focus_area': item.get('focus_area', ''),
            'asin': None,
            'price': None,
            'affiliate_link': None,
            'image_url': None,
            'rating': None,
            'review_count': None,
            'research_status': 'pending'
        }
        
        if result:
            enriched_item.update(result)
            enriched_item['affiliate_link'] = self.generate_affiliate_link(result['asin'])
            enriched_item['research_status'] = 'found'
            logger.info(f"✅ Found ASIN: {result['asin']} for {title}")
        else:
            enriched_item['research_status'] = 'manual_research_needed'
            logger.warning(f"⚠️ Manual research needed for: {title}")
        
        return enriched_item
    
    def research_all_items(self) -> Dict:
        """Research all items in the inventory"""
        data = self.load_inventory_data()
        enriched_data = {
            'metadata': data['metadata'],
            'research_date': time.strftime('%Y-%m-%d %H:%M:%S'),
            'total_items': 0,
            'items_found': 0,
            'items_needing_manual_research': 0,
            'books': {},
            'accessories': []
        }
        
        # Research books
        for category, books in data['books'].items():
            enriched_data['books'][category] = []
            
            for book in books:
                enriched_book = self.research_item(book, 'Books')
                enriched_data['books'][category].append(enriched_book)
                enriched_data['total_items'] += 1
                
                if enriched_book['research_status'] == 'found':
                    enriched_data['items_found'] += 1
                else:
                    enriched_data['items_needing_manual_research'] += 1
                
                # Rate limiting
                time.sleep(1)
        
        # Research accessories
        for accessory in data['accessories']:
            enriched_accessory = self.research_item(accessory, 'All')
            enriched_data['accessories'].append(enriched_accessory)
            enriched_data['total_items'] += 1
            
            if enriched_accessory['research_status'] == 'found':
                enriched_data['items_found'] += 1
            else:
                enriched_data['items_needing_manual_research'] += 1
            
            # Rate limiting
            time.sleep(1)
        
        return enriched_data
    
    def save_results(self, data: Dict, filename: str = None):
        """Save research results to JSON file"""
        if not filename:
            timestamp = time.strftime('%Y%m%d_%H%M%S')
            filename = f'asin_research_results_{timestamp}.json'
        
        with open(filename, 'w') as f:
            json.dump(data, f, indent=2)
        
        logger.info(f"✅ Results saved to: {filename}")
        
        # Print summary
        print(f"\n📊 RESEARCH SUMMARY")
        print(f"=" * 50)
        print(f"Total Items: {data['total_items']}")
        print(f"Items Found: {data['items_found']}")
        print(f"Manual Research Needed: {data['items_needing_manual_research']}")
        print(f"Success Rate: {(data['items_found']/data['total_items']*100):.1f}%")
        
        if data['items_needing_manual_research'] > 0:
            print(f"\n⚠️  MANUAL RESEARCH NEEDED FOR:")
            print(f"=" * 50)
            
            # List books needing manual research
            for category, books in data['books'].items():
                for book in books:
                    if book['research_status'] == 'manual_research_needed':
                        print(f"📖 {book['title']} by {book['author']}")
            
            # List accessories needing manual research
            for accessory in data['accessories']:
                if accessory['research_status'] == 'manual_research_needed':
                    print(f"🛍️  {accessory['title']}")

def main():
    """Main execution function"""
    print("🚀 MyBookshelf Bulk ASIN Research")
    print("=" * 50)
    
    researcher = AmazonASINResearch()
    
    print(f"Amazon API Available: {'✅ Yes' if researcher.use_amazon_api else '❌ No'}")
    print(f"Associate Tag: {researcher.amazon_associate_tag}")
    print()
    
    # Research all items
    print("🔍 Starting bulk research...")
    results = researcher.research_all_items()
    
    # Save results
    researcher.save_results(results)
    
    print("\n🎉 Research complete!")
    print("Next steps:")
    print("1. Review the generated JSON file")
    print("2. Manually research items marked as 'manual_research_needed'")
    print("3. Update the JSON with manual research results")
    print("4. Run the database insertion script")

if __name__ == "__main__":
    main() 