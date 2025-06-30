import os
import requests
from supabase import create_client, Client
from datetime import datetime
import json
import logging
from typing import List, Dict, Optional

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class MyBookshelfSystem:
    def __init__(self):
        """Initialize the MyBookshelf system with Supabase connection"""
        self.supabase_url = os.getenv('SUPABASE_URL')
        self.supabase_key = os.getenv('SUPABASE_ANON_KEY')
        self.amazon_access_key = os.getenv('AMAZON_ACCESS_KEY')
        self.amazon_secret_key = os.getenv('AMAZON_SECRET_KEY')
        self.amazon_associate_id = os.getenv('AMAZON_ASSOCIATE_ID', 'mybookshelf-20')
        
        if not all([self.supabase_url, self.supabase_key]):
            raise ValueError("Missing required Supabase environment variables")
        
        self.supabase: Client = create_client(str(self.supabase_url), str(self.supabase_key))
        
        # Amazon PA API setup
        self.use_real_amazon_api = bool(self.amazon_access_key and self.amazon_secret_key)
        if self.use_real_amazon_api:
            try:
                from paapi5_python_sdk import DefaultApi, SearchItemsRequest, SearchItemsResource, PartnerType
                from paapi5_python_sdk.rest import ApiException
                
                # Configure PA API
                self.amazon_api = DefaultApi(
                    access_key=self.amazon_access_key,
                    secret_key=self.amazon_secret_key,
                    host="webservices.amazon.com",
                    region="us-east-1"
                )
                
                self.partner_tag = self.amazon_associate_id
                logger.info("✅ Amazon PA API configured successfully")
                
            except ImportError:
                logger.warning("⚠️  Amazon PA API SDK not available, using mock data")
                self.use_real_amazon_api = False
            except Exception as e:
                logger.warning(f"⚠️  Amazon PA API setup failed: {e}, using mock data")
                self.use_real_amazon_api = False
        else:
            logger.info("ℹ️  Amazon credentials not provided, using mock data")
    
    def fetch_books_from_amazon(self) -> List[Dict]:
        """
        Fetch 3 leadership/productivity/AI books + 1 accessory from Amazon PA API
        Prioritize Christian authors like Patrick Lencioni
        """
        if self.use_real_amazon_api:
            return self._fetch_real_amazon_data()
        else:
            logger.info("📚 Using mock data (configure Amazon credentials for live data)")
            return self._get_mock_data()
    
    def _fetch_real_amazon_data(self) -> List[Dict]:
        """Fetch real data from Amazon PA API"""
        books_and_accessories = []
        
        try:
            from paapi5_python_sdk import SearchItemsRequest, SearchItemsResource, PartnerType
            from paapi5_python_sdk.rest import ApiException
            
            # Define search queries for Christian leadership books
            book_searches = [
                "Patrick Lencioni",
                "Christian leadership", 
                "productivity habits"
            ]
            
            accessory_searches = [
                "leadership journal"
            ]
            
            # Search for books
            for keyword in book_searches:
                try:
                    # Use official paapi5_python_sdk API
                    search_items_request = SearchItemsRequest(
                        partner_tag=self.partner_tag,
                        partner_type=PartnerType.ASSOCIATES,
                        keywords=keyword,
                        search_index="Books",
                        item_count=1,
                        resources=[
                            SearchItemsResource.ITEMINFO_TITLE,
                            SearchItemsResource.ITEMINFO_BYLINEINFO,
                            SearchItemsResource.OFFERS_LISTINGS_PRICE,
                            SearchItemsResource.IMAGES_PRIMARY_MEDIUM
                        ]
                    )
                    
                    response = self.amazon_api.search_items(search_items_request)
                    
                    if response.search_result and response.search_result.items:
                        for item in response.search_result.items[:1]:  # Take first result
                            book_data = self._parse_amazon_item(item, "Books")
                            if book_data:
                                books_and_accessories.append(book_data)
                                
                except ApiException as e:
                    logger.warning(f"Amazon API error for '{keyword}': {e}")
                    continue
                except Exception as e:
                    logger.warning(f"Error searching for '{keyword}': {e}")
                    continue
            
            # Search for accessories
            for keyword in accessory_searches:
                try:
                    search_items_request = SearchItemsRequest(
                        partner_tag=self.partner_tag,
                        partner_type=PartnerType.ASSOCIATES,
                        keywords=keyword,
                        search_index="OfficeProducts", 
                        item_count=1,
                        resources=[
                            SearchItemsResource.ITEMINFO_TITLE,
                            SearchItemsResource.ITEMINFO_BYLINEINFO,
                            SearchItemsResource.OFFERS_LISTINGS_PRICE,
                            SearchItemsResource.IMAGES_PRIMARY_MEDIUM
                        ]
                    )
                    
                    response = self.amazon_api.search_items(search_items_request)
                    
                    if response.search_result and response.search_result.items:
                        for item in response.search_result.items[:1]:
                            accessory_data = self._parse_amazon_item(item, "Accessories")
                            if accessory_data:
                                books_and_accessories.append(accessory_data)
                            
                except ApiException as e:
                    logger.warning(f"Amazon API error for accessory '{keyword}': {e}")
                except Exception as e:
                    logger.warning(f"Error searching for accessory '{keyword}': {e}")
            
            # Filter content and return
            filtered_items = self._filter_content(books_and_accessories)
            
            if not filtered_items:
                logger.warning("No items returned from Amazon API, using mock data")
                return self._get_mock_data()
            
            logger.info(f"✅ Successfully fetched {len(filtered_items)} items from Amazon PA API")
            return filtered_items
            
        except Exception as e:
            logger.error(f"❌ Amazon PA API failed: {e}, falling back to mock data")
            return self._get_mock_data()
    
    def _parse_amazon_item(self, item, category: str) -> Optional[Dict]:
        """Parse Amazon API item response into our format"""
        try:
            # Official paapi5_python_sdk returns item objects with attributes
            title = item.item_info.title.display_value if item.item_info and item.item_info.title else "Unknown Title"
            
            # Get author/brand
            author = "Unknown Author"
            if item.item_info and item.item_info.by_line_info and item.item_info.by_line_info.contributors:
                author = item.item_info.by_line_info.contributors[0].name
            elif item.item_info and item.item_info.by_line_info and item.item_info.by_line_info.brand:
                author = item.item_info.by_line_info.brand.display_value
            
            # Get price
            price = 0.0
            if (item.offers and item.offers.listings and len(item.offers.listings) > 0 
                and item.offers.listings[0].price and item.offers.listings[0].price.display_amount):
                price_str = item.offers.listings[0].price.display_amount.replace('$', '').replace(',', '')
                try:
                    price = float(price_str)
                except ValueError:
                    price = 19.99  # Default price
            else:
                price = 19.99 if category == "Books" else 29.99
            
            # Get image
            image_url = "https://via.placeholder.com/200x300?text=No+Image"
            if item.images and item.images.primary and item.images.primary.medium:
                image_url = item.images.primary.medium.url
            
            # Get ASIN
            asin = item.asin if item.asin else 'EXAMPLE123'
            
            # Generate affiliate link
            affiliate_link = f"https://amazon.com/dp/{asin}?tag={self.partner_tag}"
            
            return {
                'title': title,
                'author': author,
                'category': category,
                'price': price,
                'affiliate_link': affiliate_link,
                'image_url': image_url,
                'asin': asin,
                'last_updated': datetime.now().isoformat(),
                'content_theme': 'Christian Leadership',
                'target_audience': 'Christian Professionals',
                'motivation_level': 'High',
                'relevance_score': 95
            }
            
        except Exception as e:
            logger.warning(f"Error parsing Amazon item: {e}")
            return None
    
    def _search_amazon_products(self, keyword: str, category: str, limit: int = 1) -> List[Dict]:
        """
        Legacy method - kept for compatibility
        """
        if "Patrick Lencioni" in keyword:
            return [{
                'title': 'The Five Dysfunctions of a Team',
                'author': 'Patrick Lencioni',
                'price': 14.99,
                'affiliate_link': f'https://amazon.com/dp/EXAMPLE123?tag={self.amazon_associate_id}',
                'image_url': 'https://images-na.ssl-images-amazon.com/images/I/example.jpg',
                'category': 'Books'
            }]
        elif "journal" in keyword:
            return [{
                'title': 'Leadership Journal - Daily Planner',
                'author': 'Business Essentials',
                'price': 24.99,
                'affiliate_link': f'https://amazon.com/dp/EXAMPLE456?tag={self.amazon_associate_id}',
                'image_url': 'https://images-na.ssl-images-amazon.com/images/I/journal.jpg',
                'category': 'Accessories'
            }]
        return []
    
    def _filter_content(self, items: List[Dict]) -> List[Dict]:
        """Filter out anti-Christian content based on keywords"""
        forbidden_keywords = ['atheism', 'anti-christian', 'secular humanism', 'anti-religion']
        filtered_items = []
        
        for item in items:
            title_lower = item.get('title', '').lower()
            author_lower = item.get('author', '').lower()
            
            # Check if item contains forbidden content
            is_forbidden = any(keyword in title_lower or keyword in author_lower 
                             for keyword in forbidden_keywords)
            
            if not is_forbidden:
                filtered_items.append(item)
            else:
                logger.info(f"🚫 Filtered out item: {item.get('title')} due to content policy")
        
        return filtered_items
    
    def _get_mock_data(self) -> List[Dict]:
        """Provide mock data for development/testing"""
        return [
            {
                'title': 'The Five Dysfunctions of a Team',
                'author': 'Patrick Lencioni',
                'price': 14.99,
                'affiliate_link': f'https://amazon.com/dp/0787960756?tag={self.amazon_associate_id}',
                'image_url': 'https://covers.openlibrary.org/b/isbn/0787960756-M.jpg',
                'category': 'Books'
            },
            {
                'title': 'The Advantage',
                'author': 'Patrick Lencioni',
                'price': 16.99,
                'affiliate_link': f'https://amazon.com/dp/0470941529?tag={self.amazon_associate_id}',
                'image_url': 'https://covers.openlibrary.org/b/isbn/0470941529-M.jpg',
                'category': 'Books'
            },
            {
                'title': 'Atomic Habits',
                'author': 'James Clear',
                'price': 13.99,
                'affiliate_link': f'https://amazon.com/dp/0735211299?tag={self.amazon_associate_id}',
                'image_url': 'https://covers.openlibrary.org/b/isbn/0735211299-M.jpg',
                'category': 'Books'
            },
            {
                'title': 'Leadership Journal - Daily Planner',
                'author': 'Business Essentials',
                'price': 24.99,
                'affiliate_link': f'https://amazon.com/dp/B08Q3JDCT6?tag={self.amazon_associate_id}',
                'image_url': 'https://via.placeholder.com/200x300/28a745/ffffff?text=Leadership+Journal',
                'category': 'Accessories'
            }
        ]
    
    def store_in_supabase(self, items: List[Dict]) -> bool:
        """Store fetched items in Supabase database"""
        try:
            for item in items:
                # Add timestamp
                item['timestamp'] = datetime.now().isoformat()
                
                # Insert into Supabase
                result = self.supabase.table('books_accessories').insert(item).execute()
                
                if result.data:
                    logger.info(f"✅ Successfully stored: {item['title']}")
                else:
                    logger.error(f"❌ Failed to store: {item['title']}")
                    
            return True
            
        except Exception as e:
            logger.error(f"❌ Error storing data in Supabase: {str(e)}")
            return False
    
    def get_latest_recommendations(self, limit: int = 10) -> List[Dict]:
        """Fetch latest recommendations from Supabase"""
        try:
            result = self.supabase.table('books_accessories')\
                                 .select('*')\
                                 .order('timestamp', desc=True)\
                                 .limit(limit)\
                                 .execute()
            
            return result.data if result.data else []
            
        except Exception as e:
            logger.error(f"❌ Error fetching recommendations: {str(e)}")
            return []

    def update_book_image(self, book_title: str, author: str, image_data_url: str) -> bool:
        """Update a book's image in the database"""
        try:
            # Find the book by title and author
            response = self.supabase.table('books_accessories').select('*').eq('title', book_title).eq('author', author).execute()
            
            if not response.data:
                logger.warning(f"Book not found: {book_title} by {author}")
                return False
            
            book_id = response.data[0]['id']
            
            # Update the image
            update_response = self.supabase.table('books_accessories').update({
                'image_url': image_data_url
            }).eq('id', book_id).execute()
            
            if update_response.data:
                logger.info(f"✅ Updated image for: {book_title}")
                return True
            else:
                logger.error(f"❌ Failed to update image for: {book_title}")
                return False
                
        except Exception as e:
            logger.error(f"Error updating book image: {e}")
            return False
    
    def run_weekly_update(self) -> Dict:
        """Main function to run the weekly book and accessory update"""
        logger.info("🚀 Starting weekly MyBookshelf update...")
        
        try:
            # Fetch new books and accessories
            new_items = self.fetch_books_from_amazon()
            
            if not new_items:
                logger.warning("⚠️  No new items fetched")
                return {'success': False, 'message': 'No items fetched'}
            
            # Store in Supabase
            success = self.store_in_supabase(new_items)
            
            if success:
                logger.info("🎉 Weekly update completed successfully")
                return {
                    'success': True, 
                    'message': f'Successfully updated {len(new_items)} items',
                    'items': new_items,
                    'using_real_api': self.use_real_amazon_api
                }
            else:
                return {'success': False, 'message': 'Failed to store items'}
                
        except Exception as e:
            logger.error(f"❌ Error in weekly update: {str(e)}")
            return {'success': False, 'message': f'Error: {str(e)}'}

def main():
    """Main function for running the script"""
    try:
        system = MyBookshelfSystem()
        result = system.run_weekly_update()
        
        if result['success']:
            api_status = "🌐 Live Amazon API" if result.get('using_real_api') else "📝 Mock Data"
            print(f"✅ {result['message']} ({api_status})")
            return 0
        else:
            print(f"❌ {result['message']}")
            return 1
            
    except Exception as e:
        print(f"❌ Fatal error: {str(e)}")
        return 1

if __name__ == "__main__":
    exit(main())
