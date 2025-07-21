#!/usr/bin/env python3
"""
Fetch Real Amazon Book Covers using PA API
Uses Amazon Associates credentials to get actual book cover images
"""

import os
import sys
import requests
import base64
import time
from io import BytesIO
from typing import Dict, Optional
from supabase import create_client, Client
import logging

# Amazon PA API using python-amazon-paapi
from amazon_paapi import AmazonApi

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class RealAmazonCoverFetcher:
    def __init__(self):
        # Amazon PA API credentials
        self.amazon_access_key = "AKPAKBWO841751230292"
        self.amazon_secret_key = "5oKcOURG4kWFu09+bhHHXSUCusTwWzevVIV0e9Qx"
        self.amazon_partner_tag = "mybookshelf-20"
        
        # Supabase configuration
        self.supabase_url = "https://ackcgrnizuhauccnbiml.supabase.co"
        self.supabase_key = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImFja2Nncm5penVoYXVjY25iaW1sIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTEyMjc4MzEsImV4cCI6MjA2NjgwMzgzMX0.SXpIMuNBgUhcEQUHzpEB1zZAdF-UTGvmY81EFUtsAwc"
        
        self.supabase: Client = create_client(self.supabase_url, self.supabase_key)
        self.amazon_api = None
        
        # Initialize Amazon API
        self.init_amazon_api()
    
    def init_amazon_api(self):
        """Initialize Amazon PA API client"""
        try:
            self.amazon_api = AmazonApi(
                key=self.amazon_access_key,
                secret=self.amazon_secret_key,
                tag=self.amazon_partner_tag,
                country="US"
            )
            logger.info("✅ Amazon PA API client initialized successfully")
            return True
        except Exception as e:
            logger.error(f"❌ Failed to initialize Amazon PA API: {e}")
            return False
    
    def search_book_on_amazon(self, title: str, author: str) -> Optional[Dict]:
        """Search for a book on Amazon PA API and return the best match"""
        if not self.amazon_api:
            logger.error("❌ Amazon API not initialized")
            return None
        
        try:
            # Create search query
            search_query = f"{title} {author}"
            logger.info(f"🔍 Searching Amazon PA API for: {search_query}")
            
            # Perform search using the correct API format
            response = self.amazon_api.search_items(keywords=search_query, item_count=5)
            
            if not response or 'Items' not in response:
                logger.warning(f"⚠️  No items found for: {search_query}")
                return None
            
            # Get the first (most relevant) result
            item = response['Items'][0]
            
            # Extract book information
            book_data = {
                'asin': item.get('ASIN', ''),
                'title': self.safe_get_nested(item, ['ItemInfo', 'Title', 'DisplayValue'], title),
                'author': self.extract_author(item, author),
                'price': self.extract_price(item),
                'affiliate_link': item.get('DetailPageURL', f"https://amazon.com/dp/{item.get('ASIN', '')}?tag={self.amazon_partner_tag}"),
                'image_url': self.extract_image_url(item)
            }
            
            logger.info(f"✅ Found book: {book_data['title']} by {book_data['author']} - ${book_data['price']}")
            return book_data
            
        except Exception as e:
            error_msg = str(e)
            if "limit" in error_msg.lower():
                logger.error(f"🚫 Amazon API rate limit for '{search_query}': {e}")
                logger.info("💡 Suggestion: Your Amazon Associates account may need approval or has strict limits")
            else:
                logger.error(f"❌ Amazon search failed for '{search_query}': {e}")
            return None
    
    def safe_get_nested(self, data: Dict, keys: list, default: str = "") -> str:
        """Safely get nested dictionary values"""
        try:
            current = data
            for key in keys:
                current = current[key]
            return current if current else default
        except (KeyError, TypeError):
            return default
    
    def extract_author(self, item: Dict, default_author: str) -> str:
        """Extract author information from Amazon item"""
        try:
            contributors = self.safe_get_nested(item, ['ItemInfo', 'ByLineInfo', 'Contributors'])
            if contributors and isinstance(contributors, list):
                authors = [contrib.get('Name', '') for contrib in contributors if contrib.get('Role') == 'Author']
                if authors:
                    return ', '.join(authors)
        except:
            pass
        return default_author
    
    def extract_price(self, item: Dict) -> float:
        """Extract price from Amazon item"""
        try:
            # Try different price fields
            price_paths = [
                ['Offers', 'Listings', 0, 'Price', 'Amount'],
                ['ItemInfo', 'TradeInInfo', 'Price', 'Amount'],
                ['BrowseNodeInfo', 'WebsiteSalesRank', 'SalesRank']
            ]
            
            for path in price_paths:
                amount = self.safe_get_nested(item, path)
                if amount:
                    return float(amount) / 100 if isinstance(amount, int) else float(amount)
        except:
            pass
        return 0.0
    
    def extract_image_url(self, item: Dict) -> Optional[str]:
        """Extract image URL from Amazon item"""
        try:
            # Try different image size options
            image_paths = [
                ['Images', 'Primary', 'Large', 'URL'],
                ['Images', 'Primary', 'Medium', 'URL'],
                ['Images', 'Primary', 'Small', 'URL']
            ]
            
            for path in image_paths:
                url = self.safe_get_nested(item, path)
                if url:
                    return url
        except:
            pass
        return None
    
    def convert_image_to_base64(self, image_url: str) -> Optional[str]:
        """Download image and convert to base64 data URL"""
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
            response = requests.get(image_url, headers=headers, timeout=15)
            response.raise_for_status()
            
            # Convert to base64
            image_data = base64.b64encode(response.content).decode('utf-8')
            content_type = response.headers.get('content-type', 'image/jpeg')
            
            return f"data:{content_type};base64,{image_data}"
            
        except Exception as e:
            logger.error(f"❌ Failed to convert image: {e}")
            return None
    
    def test_amazon_api(self) -> bool:
        """Test Amazon API with a simple query"""
        logger.info("🧪 Testing Amazon PA API connection...")
        
        try:
            # Test with a very simple, well-known book
            response = self.amazon_api.search_items(keywords="Atomic Habits", item_count=1)
            
            if response and 'Items' in response:
                logger.info("✅ Amazon PA API test successful!")
                return True
            else:
                logger.warning("⚠️  Amazon PA API test returned no results")
                return False
                
        except Exception as e:
            error_msg = str(e)
            if "not approved" in error_msg.lower() or "access denied" in error_msg.lower():
                logger.error("🚫 Amazon Associates account not yet approved for PA API access")
                logger.info("💡 Your Amazon Associates account may need approval to use the Product Advertising API")
            elif "limit" in error_msg.lower() or "throttle" in error_msg.lower():
                logger.error("🚫 Amazon PA API rate limits are very strict")
                logger.info("💡 Try again later or contact Amazon about rate limit increases")
            else:
                logger.error(f"❌ Amazon PA API test failed: {e}")
            return False
    
    def update_pending_books_with_real_covers(self) -> Dict:
        """Update all pending books with real Amazon cover images"""
        logger.info("📚 Updating pending books with REAL Amazon covers...")
        
        if not self.amazon_api:
            return {'error': 'Amazon API not initialized'}
        
        # First test the API
        if not self.test_amazon_api():
            return {'error': 'Amazon PA API test failed - see logs for details'}
        
        try:
            # Get pending books
            response = self.supabase.table('pending_books').select('*').eq('status', 'pending').execute()
            pending_books = response.data or []
            
            results = {
                'total_pending': len(pending_books),
                'updated_count': 0,
                'skipped_count': 0,
                'errors': [],
                'updated_books': []
            }
            
            for book in pending_books:
                title = book['title']
                author = book['author']
                current_image = book.get('image_url', '')
                
                logger.info(f"📖 Processing: {title} by {author}")
                
                # Skip if already has a real Amazon image (not generated SVG)
                if current_image and current_image.startswith('data:image/jpeg'):
                    logger.info(f"⏭️  Already has real JPEG image: {title}")
                    results['skipped_count'] += 1
                    continue
                elif current_image and current_image.startswith('data:image/svg'):
                    logger.info(f"🔄 Replacing SVG with real Amazon cover: {title}")
                else:
                    logger.info(f"📷 No image found, fetching from Amazon: {title}")
                
                # Add delay to respect Amazon API rate limits
                time.sleep(2)  # 2 second delay between requests
                
                # Search for book on Amazon
                book_data = self.search_book_on_amazon(title, author)
                
                if book_data and book_data['image_url']:
                    # Convert image to base64
                    base64_image = self.convert_image_to_base64(book_data['image_url'])
                    
                    if base64_image:
                        # Update database with real cover and Amazon data
                        update_data = {
                            'image_url': base64_image,
                            'amazon_asin': book_data['asin'],
                            'affiliate_link': book_data['affiliate_link'],
                            'suggested_price': book_data['price'] if book_data['price'] > 0 else book.get('suggested_price')
                        }
                        
                        update_response = self.supabase.table('pending_books').update(update_data).eq('id', book['id']).execute()
                        
                        if update_response.data:
                            results['updated_count'] += 1
                            results['updated_books'].append({
                                'id': book['id'],
                                'title': title,
                                'author': author,
                                'asin': book_data['asin'],
                                'price': book_data['price']
                            })
                            logger.info(f"✅ Updated with REAL Amazon cover: {title}")
                        else:
                            error_msg = f"Failed to update database for: {title}"
                            results['errors'].append(error_msg)
                            logger.error(f"❌ {error_msg}")
                    else:
                        error_msg = f"Failed to download image for: {title}"
                        results['errors'].append(error_msg)
                        logger.error(f"❌ {error_msg}")
                else:
                    logger.warning(f"⚠️  No Amazon data found for: {title}")
                    results['skipped_count'] += 1
            
            return results
            
        except Exception as e:
            logger.error(f"❌ Update failed: {e}")
            return {'error': str(e)}

def main():
    """Main function"""
    try:
        fetcher = RealAmazonCoverFetcher()
        
        print("📚 Real Amazon Book Cover Fetcher")
        print("=" * 50)
        print("🔑 Using Your Amazon Associates API Credentials")
        print(f"🏷️  Partner Tag: {fetcher.amazon_partner_tag}")
        print("=" * 50)
        
        if not fetcher.amazon_api:
            print("❌ Amazon API initialization failed. Cannot fetch real covers.")
            return 1
        
        print("\n🚀 Fetching REAL book covers from Amazon...")
        results = fetcher.update_pending_books_with_real_covers()
        
        if 'error' in results:
            print(f"❌ Error: {results['error']}")
            print("\n💡 POSSIBLE SOLUTIONS:")
            print("   1. Your Amazon Associates account may need PA API approval")
            print("   2. Rate limits may be very strict for new accounts")
            print("   3. Contact Amazon Associates support about PA API access")
            return 1
        
        print(f"\n✅ Update completed!")
        print(f"📊 Results:")
        print(f"   • Total pending books: {results['total_pending']}")
        print(f"   • Updated with real covers: {results['updated_count']}")
        print(f"   • Skipped (already had real covers): {results['skipped_count']}")
        print(f"   • Errors: {len(results['errors'])}")
        
        if results['updated_books']:
            print(f"\n📚 Books updated with REAL Amazon covers:")
            for book in results['updated_books']:
                print(f"   ✅ {book['title']} (ASIN: {book['asin']}, Price: ${book['price']:.2f})")
        
        if results['errors']:
            print(f"\n❌ Errors encountered:")
            for error in results['errors']:
                print(f"   • {error}")
        
        print(f"\n🎯 Next steps:")
        print(f"   1. Check your admin dashboard")
        print(f"   2. You should now see REAL Amazon book covers")
        print(f"   3. Book covers are from your Amazon Associates account")
        
        return 0
        
    except Exception as e:
        logger.error(f"❌ Script failed: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main()) 