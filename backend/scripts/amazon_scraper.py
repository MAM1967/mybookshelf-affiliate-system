#!/usr/bin/env python3
"""
Amazon Scraper for MyBookshelf
Automatically scrapes Amazon search results to find ASINs, prices, and images
"""

import json
import os
import sys
import time
import re
import requests
from typing import Dict, List, Optional
from urllib.parse import quote_plus, urljoin
import logging
from bs4 import BeautifulSoup
import random

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class AmazonScraper:
    def __init__(self):
        self.session = requests.Session()
        self.amazon_associate_tag = "mybookshelf-20"
        
        # Set up headers to mimic a real browser
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
        })
        
        # Rate limiting
        self.delay_between_requests = 2  # seconds
        self.max_retries = 3
        
    def search_amazon(self, query: str, category: str = "Books") -> List[Dict]:
        """Search Amazon and extract product information"""
        try:
            # Construct search URL
            encoded_query = quote_plus(query)
            search_url = f"https://www.amazon.com/s?k={encoded_query}"
            
            if category == "Books":
                search_url += "&i=stripbooks"
            elif category == "All":
                # For accessories, search all categories
                pass
            
            logger.info(f"🔍 Searching: {query}")
            logger.info(f"📎 URL: {search_url}")
            
            # Make request
            response = self.session.get(search_url, timeout=10)
            response.raise_for_status()
            
            # Parse HTML
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Extract products
            products = self.extract_products(soup, query)
            
            logger.info(f"✅ Found {len(products)} products for '{query}'")
            return products
            
        except requests.RequestException as e:
            logger.error(f"❌ Request failed for '{query}': {e}")
            return []
        except Exception as e:
            logger.error(f"❌ Scraping failed for '{query}': {e}")
            return []
    
    def extract_products(self, soup: BeautifulSoup, original_query: str) -> List[Dict]:
        """Extract product information from Amazon search results"""
        products = []
        
        # Look for product containers
        # Amazon uses different selectors, so we'll try multiple approaches
        product_selectors = [
            'div[data-component-type="s-search-result"]',
            'div.s-result-item',
            'div[data-asin]',
            '.s-card-container'
        ]
        
        for selector in product_selectors:
            product_elements = soup.select(selector)
            if product_elements:
                logger.info(f"Found {len(product_elements)} products with selector: {selector}")
                break
        
        if not product_elements:
            logger.warning("No product elements found with any selector")
            return []
        
        for element in product_elements[:5]:  # Limit to first 5 results
            try:
                product = self.extract_single_product(element, original_query)
                if product:
                    products.append(product)
            except Exception as e:
                logger.warning(f"Failed to extract product: {e}")
                continue
        
        return products
    
    def extract_single_product(self, element, original_query: str) -> Optional[Dict]:
        """Extract information from a single product element"""
        try:
            # Extract ASIN
            asin = element.get('data-asin', '')
            if not asin:
                # Try alternative ASIN extraction
                asin_link = element.select_one('a[href*="/dp/"]')
                if asin_link:
                    href = asin_link.get('href', '')
                    asin_match = re.search(r'/dp/([A-Z0-9]{10})', href)
                    if asin_match:
                        asin = asin_match.group(1)
            
            if not asin:
                return None
            
            # Extract title
            title_element = element.select_one('h2 a span') or element.select_one('.a-text-normal')
            title = title_element.get_text(strip=True) if title_element else ''
            
            # Extract price
            price_element = element.select_one('.a-price-whole') or element.select_one('.a-price .a-offscreen')
            price_text = price_element.get_text(strip=True) if price_element else ''
            price = self.extract_price(price_text)
            
            # Extract image URL
            img_element = element.select_one('img.s-image')
            image_url = img_element.get('src', '') if img_element else ''
            
            # Extract rating
            rating_element = element.select_one('i.a-icon-star-small .a-icon-alt')
            rating_text = rating_element.get_text(strip=True) if rating_element else ''
            rating = self.extract_rating(rating_text)
            
            # Extract review count
            review_element = element.select_one('a[href*="customerReviews"] span')
            review_text = review_element.get_text(strip=True) if review_element else ''
            review_count = self.extract_review_count(review_text)
            
            # Extract author (for books)
            author_element = element.select_one('.a-row.a-size-base.a-color-secondary')
            author = author_element.get_text(strip=True) if author_element else ''
            
            # Clean up author text
            if author:
                author = re.sub(r'by\s+', '', author, flags=re.IGNORECASE)
                author = author.strip()
            
            product = {
                'asin': asin,
                'title': title,
                'author': author,
                'price': price,
                'image_url': image_url,
                'rating': rating,
                'review_count': review_count,
                'affiliate_link': f"https://amazon.com/dp/{asin}?tag={self.amazon_associate_tag}",
                'relevance_score': self.calculate_relevance_score(title, author, original_query)
            }
            
            return product
            
        except Exception as e:
            logger.warning(f"Failed to extract product details: {e}")
            return None
    
    def extract_price(self, price_text: str) -> Optional[float]:
        """Extract numeric price from price text"""
        if not price_text:
            return None
        
        # Remove currency symbols and extract number
        price_match = re.search(r'[\$£€]?([\d,]+\.?\d*)', price_text.replace(',', ''))
        if price_match:
            try:
                return float(price_match.group(1))
            except ValueError:
                return None
        return None
    
    def extract_rating(self, rating_text: str) -> Optional[float]:
        """Extract numeric rating from rating text"""
        if not rating_text:
            return None
        
        # Look for patterns like "4.5 out of 5 stars"
        rating_match = re.search(r'(\d+\.?\d*)\s+out\s+of\s+5', rating_text)
        if rating_match:
            try:
                return float(rating_match.group(1))
            except ValueError:
                return None
        return None
    
    def extract_review_count(self, review_text: str) -> Optional[int]:
        """Extract review count from review text"""
        if not review_text:
            return None
        
        # Remove commas and extract number
        review_match = re.search(r'([\d,]+)', review_text.replace(',', ''))
        if review_match:
            try:
                return int(review_match.group(1))
            except ValueError:
                return None
        return None
    
    def calculate_relevance_score(self, title: str, author: str, query: str) -> float:
        """Calculate how relevant a product is to the search query"""
        if not title:
            return 0.0
        
        title_lower = title.lower()
        query_lower = query.lower()
        author_lower = author.lower() if author else ""
        
        score = 0.0
        
        # Check if query words appear in title
        query_words = query_lower.split()
        title_words = title_lower.split()
        
        # Exact title match gets highest score
        if title_lower == query_lower:
            score += 10.0
        
        # Partial title match
        elif query_lower in title_lower:
            score += 8.0
        
        # Word overlap
        matching_words = sum(1 for word in query_words if word in title_words)
        if matching_words > 0:
            score += (matching_words / len(query_words)) * 5.0
        
        # Author match (for books)
        if author and any(word in author_lower for word in query_words):
            score += 3.0
        
        # Penalize very short titles (likely not relevant)
        if len(title_words) < 3:
            score -= 2.0
        
        return max(0.0, score)
    
    def find_best_match(self, products: List[Dict], original_title: str, original_author: str = "") -> Optional[Dict]:
        """Find the best matching product from search results"""
        if not products:
            return None
        
        # Sort by relevance score
        products.sort(key=lambda x: x.get('relevance_score', 0), reverse=True)
        
        # Get the best match
        best_match = products[0]
        
        # Additional validation
        if best_match.get('relevance_score', 0) < 2.0:
            logger.warning(f"Low relevance score ({best_match.get('relevance_score', 0)}) for '{original_title}'")
            return None
        
        return best_match
    
    def scrape_inventory(self, inventory_file: str) -> Dict:
        """Scrape all items in the inventory"""
        # Load inventory
        try:
            with open(inventory_file, 'r') as f:
                data = json.load(f)
        except FileNotFoundError:
            logger.error(f"❌ Inventory file not found: {inventory_file}")
            return {}
        
        logger.info(f"🚀 Starting automated scraping for {data['metadata']['total_books']} books and {data['metadata']['total_accessories']} accessories")
        
        scraped_data = {
            'metadata': data['metadata'],
            'scrape_date': time.strftime('%Y-%m-%d %H:%M:%S'),
            'total_items': 0,
            'items_found': 0,
            'items_not_found': 0,
            'books': {},
            'accessories': []
        }
        
        # Scrape books
        for category, books in data['books'].items():
            scraped_data['books'][category] = []
            
            for book in books:
                scraped_book = self.scrape_book(book)
                scraped_data['books'][category].append(scraped_book)
                scraped_data['total_items'] += 1
                
                if scraped_book['scrape_status'] == 'found':
                    scraped_data['items_found'] += 1
                else:
                    scraped_data['items_not_found'] += 1
                
                # Rate limiting
                time.sleep(self.delay_between_requests + random.uniform(0.5, 1.5))
        
        # Scrape accessories
        for accessory in data['accessories']:
            scraped_accessory = self.scrape_accessory(accessory)
            scraped_data['accessories'].append(scraped_accessory)
            scraped_data['total_items'] += 1
            
            if scraped_accessory['scrape_status'] == 'found':
                scraped_data['items_found'] += 1
            else:
                scraped_data['items_not_found'] += 1
            
            # Rate limiting
            time.sleep(self.delay_between_requests + random.uniform(0.5, 1.5))
        
        return scraped_data
    
    def scrape_book(self, book: Dict) -> Dict:
        """Scrape a single book"""
        title = book['title']
        author = book['author']
        
        # Create search query
        search_query = f"{title} {author}"
        
        # Search Amazon
        products = self.search_amazon(search_query, "Books")
        
        # Find best match
        best_match = self.find_best_match(products, title, author)
        
        # Prepare result
        result = {
            'title': title,
            'author': author,
            'category': 'Books',
            'description': book.get('description', ''),
            'christian_themes': book.get('christian_themes', []),
            'leadership_topics': book.get('leadership_topics', []),
            'focus_area': book.get('focus_area', ''),
            'asin': None,
            'price': None,
            'affiliate_link': None,
            'image_url': None,
            'rating': None,
            'review_count': None,
            'scrape_status': 'not_found'
        }
        
        if best_match:
            result.update({
                'asin': best_match['asin'],
                'price': best_match['price'],
                'affiliate_link': best_match['affiliate_link'],
                'image_url': best_match['image_url'],
                'rating': best_match['rating'],
                'review_count': best_match['review_count'],
                'scrape_status': 'found'
            })
            
            logger.info(f"✅ Found: {title} by {author} (ASIN: {best_match['asin']})")
        else:
            logger.warning(f"⚠️  Not found: {title} by {author}")
        
        return result
    
    def scrape_accessory(self, accessory: Dict) -> Dict:
        """Scrape a single accessory"""
        title = accessory['title']
        
        # Create search query
        search_query = title
        
        # Search Amazon (all categories)
        products = self.search_amazon(search_query, "All")
        
        # Find best match
        best_match = self.find_best_match(products, title)
        
        # Prepare result
        result = {
            'title': title,
            'author': 'N/A',  # Accessories don't have authors
            'category': 'accessories',
            'description': accessory.get('description', ''),
            'accessory_type': accessory.get('accessory_type', ''),
            'target_audience': accessory.get('target_audience', ''),
            'price_range': accessory.get('price_range', ''),
            'asin': None,
            'price': None,
            'affiliate_link': None,
            'image_url': None,
            'rating': None,
            'review_count': None,
            'scrape_status': 'not_found'
        }
        
        if best_match:
            result.update({
                'asin': best_match['asin'],
                'price': best_match['price'],
                'affiliate_link': best_match['affiliate_link'],
                'image_url': best_match['image_url'],
                'rating': best_match['rating'],
                'review_count': best_match['review_count'],
                'scrape_status': 'found'
            })
            
            logger.info(f"✅ Found: {title} (ASIN: {best_match['asin']})")
        else:
            logger.warning(f"⚠️  Not found: {title}")
        
        return result
    
    def save_results(self, data: Dict, filename: str = None):
        """Save scraping results to JSON file"""
        if not filename:
            timestamp = time.strftime('%Y%m%d_%H%M%S')
            filename = f'amazon_scraping_results_{timestamp}.json'
        
        with open(filename, 'w') as f:
            json.dump(data, f, indent=2)
        
        logger.info(f"✅ Results saved to: {filename}")
        
        # Print summary
        print(f"\n📊 SCRAPING SUMMARY")
        print(f"{'='*50}")
        print(f"Total Items: {data['total_items']}")
        print(f"Items Found: {data['items_found']}")
        print(f"Items Not Found: {data['items_not_found']}")
        print(f"Success Rate: {(data['items_found']/data['total_items']*100):.1f}%")
        
        if data['items_not_found'] > 0:
            print(f"\n⚠️  ITEMS NOT FOUND:")
            print(f"{'='*50}")
            
            # List books not found
            for category, books in data['books'].items():
                for book in books:
                    if book['scrape_status'] == 'not_found':
                        print(f"📖 {book['title']} by {book['author']}")
            
            # List accessories not found
            for accessory in data['accessories']:
                if accessory['scrape_status'] == 'not_found':
                    print(f"🛍️  {accessory['title']}")

def main():
    """Main execution function"""
    print("🚀 Amazon Scraper for MyBookshelf")
    print("=" * 50)
    
    # Check if inventory file exists
    inventory_file = '../../books_and_accessories_2025.json'
    if not os.path.exists(inventory_file):
        print(f"❌ Inventory file not found: {inventory_file}")
        sys.exit(1)
    
    # Initialize scraper
    scraper = AmazonScraper()
    
    print("⚠️  IMPORTANT: This scraper respects rate limits and includes delays")
    print("   Estimated time: 5-10 minutes for 100 items")
    print("   You can interrupt with Ctrl+C at any time")
    print()
    
    # Start scraping
    try:
        results = scraper.scrape_inventory(inventory_file)
        scraper.save_results(results)
        
        print(f"\n🎉 Scraping complete!")
        print(f"Next steps:")
        print(f"1. Review the generated JSON file")
        print(f"2. Manually verify any items marked as 'not_found'")
        print(f"3. Run the database insertion script")
        
    except KeyboardInterrupt:
        print(f"\n\n⏹️  Scraping interrupted by user")
        print("💾 Partial results may be available")

if __name__ == "__main__":
    main() 