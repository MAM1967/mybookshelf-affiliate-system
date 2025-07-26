#!/usr/bin/env python3
"""
Add Real Book Cover Images to Pending Books
Updates pending_books table with real cover images for better approval workflow
"""

import os
import sys
import requests
import base64
from typing import Dict, Optional
from supabase import create_client, Client
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class PendingBookImageUpdater:
    def __init__(self):
        # Supabase configuration
        self.supabase_url = "https://ackcgrnizuhauccnbiml.supabase.co"
        self.supabase_key = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImFja2Nncm5penVoYXVjY25iaW1sIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTEyMjc4MzEsImV4cCI6MjA2NjgwMzgzMX0.SXpIMuNBgUhcEQUHzpEB1zZAdF-UTGvmY81EFUtsAwc"
        
        self.supabase: Client = create_client(self.supabase_url, self.supabase_key)
    
    def get_book_cover_url(self, title: str, author: str) -> Optional[str]:
        """Get book cover URL from various sources"""
        
        # Known working cover URLs for common books
        known_covers = {
            "The 7 Habits of Highly Effective People": "https://m.media-amazon.com/images/I/51S35Y84RCL._SX330_BO1,204,203,200_.jpg",
            "Good to Great": "https://m.media-amazon.com/images/I/512HnRFelOL._SX328_BO1,204,203,200_.jpg",
            "The Maxwell Daily Reader": "https://m.media-amazon.com/images/I/51GRZ0Cz+UL._SX331_BO1,204,203,200_.jpg",
            "The Purpose Driven Life": "https://m.media-amazon.com/images/I/51pzv4r6pKL._SX331_BO1,204,203,200_.jpg",
            "Lead Like Jesus": "https://m.media-amazon.com/images/I/51rQJQkA3lL._SX331_BO1,204,203,200_.jpg",
            "The Servant Leader": "https://m.media-amazon.com/images/I/41sTIY+CzpL._SX332_BO1,204,203,200_.jpg",
            "Praying for Your Future Husband": "https://m.media-amazon.com/images/I/51yLjXKBGIL._SX331_BO1,204,203,200_.jpg",
            "Business by the Book": "https://m.media-amazon.com/images/I/413mNkMhWJL._SX327_BO1,204,203,200_.jpg"
        }
        
        if title in known_covers:
            return known_covers[title]
        
        # Try Open Library covers
        if "stephen" in author.lower() and "covey" in author.lower():
            return "https://covers.openlibrary.org/b/isbn/9780743269513-L.jpg"
        elif "jim" in author.lower() and "collins" in author.lower():
            return "https://covers.openlibrary.org/b/isbn/9780066620992-L.jpg"
        elif "john" in author.lower() and "maxwell" in author.lower():
            return "https://covers.openlibrary.org/b/isbn/9780785260097-L.jpg"
        
        return None
    
    def convert_url_to_base64(self, image_url: str) -> Optional[str]:
        """Download image and convert to base64 data URL"""
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
            response = requests.get(image_url, headers=headers, timeout=10)
            response.raise_for_status()
            
            # Convert to base64
            image_data = base64.b64encode(response.content).decode('utf-8')
            content_type = response.headers.get('content-type', 'image/jpeg')
            
            return f"data:{content_type};base64,{image_data}"
            
        except Exception as e:
            logger.error(f"❌ Failed to convert image: {e}")
            return None
    
    def update_pending_books_with_images(self) -> Dict:
        """Update all pending books with real cover images"""
        logger.info("📚 Updating pending books with real cover images...")
        
        try:
            # Get pending books without images
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
                
                # Skip if already has a valid image
                if current_image and current_image.startswith('data:image'):
                    logger.info(f"⏭️  Already has image: {title}")
                    results['skipped_count'] += 1
                    continue
                
                # Get cover URL
                cover_url = self.get_book_cover_url(title, author)
                
                if cover_url:
                    # Convert to base64
                    base64_image = self.convert_url_to_base64(cover_url)
                    
                    if base64_image:
                        # Update database
                        update_response = self.supabase.table('pending_books').update({
                            'image_url': base64_image
                        }).eq('id', book['id']).execute()
                        
                        if update_response.data:
                            results['updated_count'] += 1
                            results['updated_books'].append({
                                'id': book['id'],
                                'title': title,
                                'author': author
                            })
                            logger.info(f"✅ Updated image for: {title}")
                        else:
                            error_msg = f"Failed to update database for: {title}"
                            results['errors'].append(error_msg)
                            logger.error(f"❌ {error_msg}")
                    else:
                        error_msg = f"Failed to convert image for: {title}"
                        results['errors'].append(error_msg)
                        logger.error(f"❌ {error_msg}")
                else:
                    logger.warning(f"⚠️  No cover found for: {title}")
                    results['skipped_count'] += 1
            
            return results
            
        except Exception as e:
            logger.error(f"❌ Update failed: {e}")
            return {'error': str(e)}
    
    def create_sample_images_for_missing(self) -> Dict:
        """Create generated SVG images for books without covers"""
        logger.info("🎨 Creating sample images for books without covers...")
        
        try:
            # Get pending books without images
            response = self.supabase.table('pending_books').select('*').eq('status', 'pending').execute()
            pending_books = response.data or []
            
            results = {
                'total_checked': len(pending_books),
                'created_count': 0,
                'skipped_count': 0,
                'created_books': []
            }
            
            for book in pending_books:
                title = book['title']
                author = book['author']
                category = book.get('category', 'Books')
                current_image = book.get('image_url', '')
                
                # Skip if already has an image
                if current_image and (current_image.startswith('data:image') or current_image.startswith('http')):
                    results['skipped_count'] += 1
                    continue
                
                # Create SVG image
                bg_color = "#ff9800" if category == "Books" else "#795548"
                title_short = title[:20] + "..." if len(title) > 20 else title
                author_short = author[:15] + "..." if len(author) > 15 else author
                
                svg_content = f'''
                <svg xmlns="http://www.w3.org/2000/svg" width="200" height="280" viewBox="0 0 200 280">
                  <rect width="200" height="280" fill="{bg_color}" rx="12"/>
                  <rect x="15" y="15" width="170" height="250" fill="white" rx="8" opacity="0.95"/>
                  <text x="100" y="80" text-anchor="middle" fill="{bg_color}" font-family="Arial, sans-serif" font-size="14" font-weight="bold">
                    <tspan x="100" dy="0">{title_short.split(' ')[0]}</tspan>
                    <tspan x="100" dy="18">{' '.join(title_short.split(' ')[1:3])}</tspan>
                    <tspan x="100" dy="18">{' '.join(title_short.split(' ')[3:])}</tspan>
                  </text>
                  <text x="100" y="160" text-anchor="middle" fill="#666" font-family="Arial, sans-serif" font-size="11">
                    <tspan x="100" dy="0">by</tspan>
                    <tspan x="100" dy="16">{author_short}</tspan>
                  </text>
                  <text x="100" y="220" text-anchor="middle" fill="{bg_color}" font-family="Arial, sans-serif" font-size="10" font-weight="bold">
                    {category}
                  </text>
                  <rect x="25" y="25" width="150" height="2" fill="{bg_color}" opacity="0.5"/>
                  <rect x="25" y="253" width="150" height="2" fill="{bg_color}" opacity="0.5"/>
                </svg>
                '''
                
                # Convert to base64 data URL
                svg_base64 = base64.b64encode(svg_content.encode('utf-8')).decode('utf-8')
                data_url = f"data:image/svg+xml;base64,{svg_base64}"
                
                # Update database
                update_response = self.supabase.table('pending_books').update({
                    'image_url': data_url
                }).eq('id', book['id']).execute()
                
                if update_response.data:
                    results['created_count'] += 1
                    results['created_books'].append({
                        'id': book['id'],
                        'title': title,
                        'author': author
                    })
                    logger.info(f"🎨 Created image for: {title}")
                else:
                    logger.error(f"❌ Failed to update: {title}")
            
            return results
            
        except Exception as e:
            logger.error(f"❌ Image creation failed: {e}")
            return {'error': str(e)}

def main():
    """Main function"""
    try:
        updater = PendingBookImageUpdater()
        
        print("🖼️  MyBookshelf Pending Books Image Updater")
        print("=" * 50)
        print("\nOptions:")
        print("1. Add real book cover images")
        print("2. Create generated images for missing covers")
        print("3. Do both (recommended)")
        
        choice = input("\nEnter your choice (1-3): ").strip()
        
        if choice == '1':
            print("\n📚 Adding real book cover images...")
            results = updater.update_pending_books_with_images()
            
        elif choice == '2':
            print("\n🎨 Creating generated images...")
            results = updater.create_sample_images_for_missing()
            
        elif choice == '3':
            print("\n📚 Adding real book cover images...")
            real_results = updater.update_pending_books_with_images()
            
            print("\n🎨 Creating generated images for remaining books...")
            generated_results = updater.create_sample_images_for_missing()
            
            results = {
                'real_images': real_results,
                'generated_images': generated_results
            }
        else:
            print("❌ Invalid choice")
            return 1
        
        print("\n✅ Update completed!")
        print(f"📊 Results: {results}")
        print("\n🎯 Next steps:")
        print("   1. Check your admin dashboard")
        print("   2. You should now see book covers in the approval workflow")
        print("   3. Make approval decisions with visual context!")
        
        return 0
        
    except Exception as e:
        logger.error(f"❌ Script failed: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main()) 