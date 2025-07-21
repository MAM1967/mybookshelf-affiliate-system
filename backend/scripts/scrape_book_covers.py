#!/usr/bin/env python3
"""
Book Cover Scraper for MyBookshelf
Scrapes Amazon and Goodreads for real book cover images
Bypasses PA API restrictions by direct web scraping
"""

import json
import os
import sys
import time
import re
import requests
import base64
from typing import Dict, List, Optional, Tuple
from urllib.parse import quote_plus, urljoin
import logging
from bs4 import BeautifulSoup
import random
from supabase import create_client, Client

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class BookCoverScraper:
    def __init__(self):
        # Supabase configuration
        self.supabase_url = "https://ackcgrnizuhauccnbiml.supabase.co"
        self.supabase_key = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImFja2Nncm5penVoYXVjY25iaW1sIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTEyMjc4MzEsImV4cCI6MjA2NjgwMzgzMX0.SXpIMuNBgUhcEQUHzpEB1zZAdF-UTGvmY81EFUtsAwc"
        self.supabase: Client = create_client(self.supabase_url, self.supabase_key)
        
        self.amazon_associate_tag = "mybookshelf-20"
        
        # Set up session with realistic headers
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
        })
        
        # Rate limiting to be respectful
        self.delay_between_requests = random.uniform(2, 4)  # seconds
        
    def search_amazon_for_book(self, title: str, author: str) -> Optional[Dict]:
        """Search Amazon for a book and extract cover image and details"""
        try:
            # Construct search query
            search_query = f"{title} {author}"
            encoded_query = quote_plus(search_query)
            search_url = f"https://www.amazon.com/s?k={encoded_query}&i=stripbooks"
            
            logger.info(f"🔍 Searching Amazon for: {search_query}")
            
            # Add random delay to be respectful
            time.sleep(random.uniform(1, 3))
            
            # Make request
            response = self.session.get(search_url, timeout=15)
            response.raise_for_status()
            
            # Parse HTML
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Find product containers
            product_elements = soup.select('div[data-component-type="s-search-result"]')
            
            if not product_elements:
                # Try alternative selectors
                product_elements = soup.select('div.s-result-item[data-asin]')
            
            if not product_elements:
                logger.warning(f"No products found for: {search_query}")
                return None
            
            # Process first few results to find best match
            for element in product_elements[:3]:
                book_data = self.extract_book_from_element(element, title, author)
                if book_data:
                    price_display = f"${book_data['price']:.2f}" if book_data['price'] else "Price N/A"
                    logger.info(f"✅ Found: {book_data['title']} by {book_data['author']} - {price_display}")
                    return book_data
            
            logger.warning(f"No suitable matches found for: {search_query}")
            return None
            
        except requests.RequestException as e:
            logger.error(f"❌ Request failed for '{search_query}': {e}")
            return None
        except Exception as e:
            logger.error(f"❌ Amazon scraping failed for '{search_query}': {e}")
            return None
    
    def extract_book_from_element(self, element, original_title: str, original_author: str) -> Optional[Dict]:
        """Extract book information from Amazon product element"""
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
            
            # Extract author
            author_element = element.select_one('.a-row .a-size-base+ .a-size-base')
            if not author_element:
                author_element = element.select_one('[data-cy="title-recipe-review"] .a-size-base')
            
            author = ''
            if author_element:
                author_text = author_element.get_text(strip=True)
                # Clean up author text
                author = re.sub(r'^by\s+', '', author_text, flags=re.IGNORECASE).strip()
            
            # Extract price (with proper cents handling and format preference)
            price = None
            
            # Get all price elements and find the best one
            all_price_elements = element.select('.a-price')
            valid_prices = []
            
            for price_elem in all_price_elements:
                price_text = price_elem.get_text(strip=True)
                
                # Extract all price values from this element
                price_matches = re.findall(r'\$(\d+\.?\d{0,2})', price_text.replace(',', ''))
                
                for price_match in price_matches:
                    try:
                        price_value = float(price_match)
                        
                        # Skip free/promotional prices and unreasonably high prices
                        if 0.01 <= price_value <= 200.00:
                            valid_prices.append(price_value)
                    except ValueError:
                        continue
            
            # Choose the best price (prefer paperback range $5-$30)
            if valid_prices:
                # Sort prices and prefer reasonable book prices
                valid_prices = sorted(set(valid_prices))  # Remove duplicates and sort
                
                # Prefer prices in typical paperback range
                paperback_prices = [p for p in valid_prices if 5.00 <= p <= 30.00]
                if paperback_prices:
                    price = paperback_prices[0]  # Take lowest reasonable price
                else:
                    # Take lowest valid price if no paperback range found
                    price = valid_prices[0]
            
            # Extract image URL
            img_element = element.select_one('img.s-image')
            image_url = ''
            if img_element:
                # Get high resolution image URL
                image_url = img_element.get('src', '')
                
                # Try to get higher resolution version
                if image_url:
                    # Replace size parameters for higher resolution
                    image_url = re.sub(r'_AC_[^.]*_', '_AC_SX679_', image_url)
                    image_url = re.sub(r'_SX\d+_', '_SX679_', image_url)
                    image_url = re.sub(r'_SY\d+_', '_SY679_', image_url)
            
            # Check relevance
            relevance_score = self.calculate_relevance(title, author, original_title, original_author)
            
            if relevance_score < 0.3:  # Minimum relevance threshold
                return None
            
            return {
                'asin': asin,
                'title': title,
                'author': author,
                'price': price,
                'image_url': image_url,
                'affiliate_link': f"https://amazon.com/dp/{asin}?tag={self.amazon_associate_tag}",
                'relevance_score': relevance_score,
                'source': 'amazon'
            }
            
        except Exception as e:
            logger.warning(f"Failed to extract book details: {e}")
            return None
    
    def calculate_relevance(self, found_title: str, found_author: str, 
                          original_title: str, original_author: str) -> float:
        """Calculate how relevant a found book is to the original query"""
        if not found_title:
            return 0.0
        
        title_score = 0.0
        author_score = 0.0
        
        # Normalize strings
        found_title = found_title.lower().strip()
        found_author = found_author.lower().strip()
        original_title = original_title.lower().strip()
        original_author = original_author.lower().strip()
        
        # Title matching
        if original_title in found_title or found_title in original_title:
            title_score = 0.8
        else:
            # Word overlap for title
            original_words = set(original_title.split())
            found_words = set(found_title.split())
            if original_words and found_words:
                overlap = len(original_words.intersection(found_words))
                title_score = overlap / max(len(original_words), len(found_words))
        
        # Author matching
        if found_author and original_author:
            if original_author in found_author or found_author in original_author:
                author_score = 0.8
            else:
                # Word overlap for author
                original_author_words = set(original_author.split())
                found_author_words = set(found_author.split())
                if original_author_words and found_author_words:
                    overlap = len(original_author_words.intersection(found_author_words))
                    author_score = overlap / max(len(original_author_words), len(found_author_words))
        
        # Combined score (title weighted more heavily)
        final_score = (title_score * 0.7) + (author_score * 0.3)
        return final_score
    
    def search_goodreads_for_book(self, title: str, author: str) -> Optional[Dict]:
        """Search Goodreads for book cover as fallback"""
        try:
            search_query = f"{title} {author}"
            encoded_query = quote_plus(search_query)
            search_url = f"https://www.goodreads.com/search?q={encoded_query}"
            
            logger.info(f"🔍 Searching Goodreads for: {search_query}")
            
            # Add delay
            time.sleep(random.uniform(2, 4))
            
            response = self.session.get(search_url, timeout=15)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Find book results
            book_elements = soup.select('.bookTitle')
            
            for i, book_element in enumerate(book_elements[:3]):
                book_url = book_element.get('href', '')
                if book_url:
                    # Get book page to extract cover
                    book_page_url = urljoin('https://www.goodreads.com', book_url)
                    
                    time.sleep(random.uniform(1, 2))
                    book_response = self.session.get(book_page_url, timeout=15)
                    book_soup = BeautifulSoup(book_response.content, 'html.parser')
                    
                    # Extract cover image
                    img_element = book_soup.select_one('#coverImage') or book_soup.select_one('.ResponsiveImage')
                    if img_element:
                        image_url = img_element.get('src', '')
                        if image_url:
                            return {
                                'title': title,
                                'author': author,
                                'image_url': image_url,
                                'source': 'goodreads'
                            }
            
            return None
            
        except Exception as e:
            logger.warning(f"Goodreads search failed for '{search_query}': {e}")
            return None
    
    def download_and_convert_image(self, image_url: str, book_title: str) -> Optional[str]:
        """Download image and convert to base64 data URL"""
        if not image_url:
            return None
        
        try:
            logger.info(f"📥 Downloading cover for: {book_title}")
            
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
                'Referer': 'https://amazon.com/'
            }
            
            response = requests.get(image_url, headers=headers, timeout=20)
            response.raise_for_status()
            
            # Validate image
            if len(response.content) < 1000:  # Too small to be a real image
                logger.warning(f"Image too small for {book_title}")
                return None
            
            # Convert to base64
            image_data = base64.b64encode(response.content).decode('utf-8')
            content_type = response.headers.get('content-type', 'image/jpeg')
            
            # Ensure it's a valid image content type
            if not content_type.startswith('image/'):
                content_type = 'image/jpeg'
            
            data_url = f"data:{content_type};base64,{image_data}"
            
            logger.info(f"✅ Successfully downloaded cover for: {book_title}")
            return data_url
            
        except Exception as e:
            logger.error(f"❌ Failed to download image for {book_title}: {e}")
            return None
    
    def update_pending_books_with_covers(self) -> Dict:
        """Main function to update all pending books with real covers"""
        logger.info("📚 Starting book cover scraping for pending books...")
        
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
            
            logger.info(f"Found {len(pending_books)} pending books to process")
            
            for i, book in enumerate(pending_books, 1):
                title = book['title']
                author = book['author']
                current_image = book.get('image_url', '')
                
                logger.info(f"\n📖 [{i}/{len(pending_books)}] Processing: {title} by {author}")
                
                # Skip if already has a real image (not SVG)
                if current_image and current_image.startswith('data:image/jpeg'):
                    logger.info(f"⏭️  Already has real JPEG image: {title}")
                    results['skipped_count'] += 1
                    continue
                
                # Search for book cover
                book_data = None
                
                # Try Amazon first
                try:
                    book_data = self.search_amazon_for_book(title, author)
                except Exception as e:
                    logger.warning(f"Amazon search failed: {e}")
                
                # Fallback to Goodreads if Amazon fails
                if not book_data or not book_data.get('image_url'):
                    logger.info("🔄 Trying Goodreads as fallback...")
                    try:
                        goodreads_data = self.search_goodreads_for_book(title, author)
                        if goodreads_data:
                            book_data = goodreads_data
                    except Exception as e:
                        logger.warning(f"Goodreads search failed: {e}")
                
                if book_data and book_data.get('image_url'):
                    # Download and convert image
                    base64_image = self.download_and_convert_image(book_data['image_url'], title)
                    
                    if base64_image:
                        # Update database
                        update_data = {
                            'image_url': base64_image
                        }
                        
                        # Add Amazon data if available
                        if book_data.get('source') == 'amazon':
                            if book_data.get('asin'):
                                update_data['amazon_asin'] = book_data['asin']
                            if book_data.get('affiliate_link'):
                                update_data['affiliate_link'] = book_data['affiliate_link']
                            if book_data.get('price'):
                                update_data['suggested_price'] = book_data['price']
                        
                        try:
                            update_response = self.supabase.table('pending_books').update(update_data).eq('id', book['id']).execute()
                            
                            if update_response.data:
                                results['updated_count'] += 1
                                results['updated_books'].append({
                                    'id': book['id'],
                                    'title': title,
                                    'author': author,
                                    'source': book_data.get('source', 'unknown'),
                                    'asin': book_data.get('asin', 'N/A')
                                })
                                logger.info(f"✅ Updated {title} with real cover from {book_data.get('source', 'unknown')}")
                            else:
                                error_msg = f"Failed to update database for: {title}"
                                results['errors'].append(error_msg)
                                logger.error(f"❌ {error_msg}")
                                
                        except Exception as e:
                            error_msg = f"Database update failed for {title}: {e}"
                            results['errors'].append(error_msg)
                            logger.error(f"❌ {error_msg}")
                    else:
                        error_msg = f"Failed to download image for: {title}"
                        results['errors'].append(error_msg)
                        logger.error(f"❌ {error_msg}")
                else:
                    logger.warning(f"⚠️  No cover found for: {title} by {author}")
                    results['skipped_count'] += 1
                
                # Rate limiting between books
                if i < len(pending_books):  # Don't delay after last book
                    delay = random.uniform(3, 6)
                    logger.info(f"⏳ Waiting {delay:.1f}s before next book...")
                    time.sleep(delay)
            
            return results
            
        except Exception as e:
            logger.error(f"❌ Cover scraping failed: {e}")
            return {'error': str(e)}

def main():
    """Main function"""
    try:
        scraper = BookCoverScraper()
        
        print("📚 Book Cover Scraper")
        print("=" * 50)
        print("🕸️  Scraping Amazon & Goodreads for Real Book Covers")
        print("🔄 Bypassing PA API restrictions with direct scraping")
        print("=" * 50)
        
        print("\n🚀 Starting cover scraping...")
        results = scraper.update_pending_books_with_covers()
        
        if 'error' in results:
            print(f"❌ Error: {results['error']}")
            return 1
        
        print(f"\n✅ Cover scraping completed!")
        print(f"📊 Results:")
        print(f"   • Total pending books: {results['total_pending']}")
        print(f"   • Updated with real covers: {results['updated_count']}")
        print(f"   • Skipped (already had covers): {results['skipped_count']}")
        print(f"   • Errors: {len(results['errors'])}")
        
        if results['updated_books']:
            print(f"\n📚 Books updated with REAL covers:")
            for book in results['updated_books']:
                print(f"   ✅ {book['title']} (Source: {book['source']}, ASIN: {book['asin']})")
        
        if results['errors']:
            print(f"\n❌ Errors encountered:")
            for error in results['errors']:
                print(f"   • {error}")
        
        print(f"\n🎯 Next steps:")
        print(f"   1. Check your admin dashboard")
        print(f"   2. You should now see REAL book covers")
        print(f"   3. Book covers scraped from Amazon/Goodreads")
        print(f"   4. No PA API needed!")
        
        return 0
        
    except Exception as e:
        logger.error(f"❌ Script failed: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main()) 