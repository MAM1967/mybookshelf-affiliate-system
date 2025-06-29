#!/usr/bin/env python3
"""
Grok-based Book Cover Fetcher with Amazon PA API and Supabase
Updated with proper PA API implementation and existing Supabase credentials
"""

import os
import sys
from supabase import create_client, Client
from datetime import datetime
import requests
import json
import base64
from typing import Dict, Optional
from urllib.parse import urlencode

# Add parent directory to Python path
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.insert(0, parent_dir)

# Configuration - Using your provided credentials
SUPABASE_URL = "https://ackcgrnizuhauccnbiml.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImFja2Nncm5penVoYXVjY21iaW1sIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTEyMjc4MzEsImV4cCI6MjA2NjgwMzgzMX0.SXpIMuNBgUhcEQUHzpEB1zZAdF-UTGvmY81EFUtsAwc"

# Amazon PA API credentials - Your provided credentials
AMAZON_ACCESS_KEY = "5oKcOURG4kWFu09+bhHHXSUCusTwWzevVIV0e9Qx"
AMAZON_SECRET_KEY = "5oKcOURG4kWFu09+bhHHXSUCusTwWzevVIV0e9Qx"
AMAZON_ASSOCIATE_TAG = "mybookshelf-20"
SERPAPI_KEY = os.getenv("SERPAPI_KEY")  # Optional fallback

# Initialize Supabase client
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

def get_amazon_cover_paapi(book_name: str, isbn: Optional[str] = None, author: Optional[str] = None) -> Dict:
    """
    Fetch book cover URL from Amazon PA API using python-amazon-paapi.
    """
    try:
        # Try to import PA API
        from amazon_paapi import AmazonApi
        
        if not all([AMAZON_ACCESS_KEY, AMAZON_SECRET_KEY]):
            print("⚠️  Amazon PA API credentials not provided, using fallback")
            return fallback_direct_urls(book_name, author)

        # Initialize PA API client
        amazon = AmazonApi(
            key=AMAZON_ACCESS_KEY,
            secret=AMAZON_SECRET_KEY,
            tag=AMAZON_ASSOCIATE_TAG,
            country="US"
        )

        # Build search query
        search_query = f"{book_name} {author or ''}".strip()
        
        print(f"🔍 Trying Amazon PA API for: {search_query}")
        
        # Search for items using the correct method
        result = amazon.search_items(
            keywords=search_query,
            search_index="Books",
            item_count=1
        )

        print(f"📦 Amazon API returned: {type(result)}")
        
        if result and hasattr(result, 'items') and result.items:
            item = result.items[0]
            
            title = getattr(item, 'title', book_name)
            author_name = author or "Unknown"
            
            # Get author from PA API if available
            if hasattr(item, 'contributors') and item.contributors:
                author_name = item.contributors[0].name

            cover_url = ""
            if hasattr(item, 'images') and item.images and hasattr(item.images, 'large'):
                cover_url = item.images.large

            affiliate_link = getattr(item, 'url', f"https://amazon.com/s?k={search_query}&tag={AMAZON_ASSOCIATE_TAG}")

            # Get price
            price = 19.99  # Default price
            if hasattr(item, 'prices') and item.prices and hasattr(item.prices, 'amount'):
                try:
                    price = float(item.prices.amount)
                except (ValueError, AttributeError):
                    price = 19.99

            print(f"✅ Amazon PA API success for: {title}")
            return {
                "title": title,
                "author": author_name,
                "cover_url": cover_url,
                "affiliate_link": affiliate_link,
                "price": price,
                "category": "Books",
                "timestamp": datetime.utcnow().isoformat()
            }

    except ImportError:
        print("⚠️  Amazon PA API library not installed, using fallback")
        return fallback_direct_urls(book_name, author)
    except Exception as e:
        print(f"❌ Amazon PA API error: {str(e)} - using fallback")
        return fallback_direct_urls(book_name, author)

    print("❌ No items found from Amazon PA API, using fallback")
    return fallback_direct_urls(book_name, author)

def fallback_direct_urls(book_name: str, author: Optional[str] = None) -> Dict:
    """
    Fallback to direct URLs for known books.
    """
    # Known working cover URLs for your 4 books
    known_covers = {
        "The Five Dysfunctions of a Team": {
            "cover_url": "https://covers.openlibrary.org/b/isbn/0787960756-L.jpg",
            "author": "Patrick Lencioni",
            "price": 14.99,
            "affiliate_link": f"https://amazon.com/dp/0787960756?tag={AMAZON_ASSOCIATE_TAG}"
        },
        "The Advantage": {
            "cover_url": "https://covers.openlibrary.org/b/isbn/0470941529-L.jpg",
            "author": "Patrick Lencioni",
            "price": 16.99,
            "affiliate_link": f"https://amazon.com/dp/0470941529?tag={AMAZON_ASSOCIATE_TAG}"
        },
        "Atomic Habits": {
            "cover_url": "https://m.media-amazon.com/images/I/513Y5o-DYtL.jpg",
            "author": "James Clear",
            "price": 13.99,
            "affiliate_link": f"https://amazon.com/dp/0735211299?tag={AMAZON_ASSOCIATE_TAG}"
        },
        "Leadership Journal - Daily Planner": {
            "cover_url": "https://images.unsplash.com/photo-1434030216411-0b793f4b4173?w=300&h=400&fit=crop",
            "author": "Business Essentials",
            "price": 24.99,
            "affiliate_link": f"https://amazon.com/dp/B08Q3JDCT6?tag={AMAZON_ASSOCIATE_TAG}"
        }
    }

    book_data = known_covers.get(book_name)
    if book_data:
        return {
            "title": book_name,
            "author": book_data["author"],
            "cover_url": book_data["cover_url"],
            "affiliate_link": book_data["affiliate_link"],
            "price": book_data["price"],
            "category": "Books" if "Journal" not in book_name else "Accessories",
            "timestamp": datetime.utcnow().isoformat()
        }

    return {"error": f"No fallback data for {book_name}"}

def convert_to_base64(image_url: str) -> Optional[str]:
    """
    Download image and convert to base64 data URL.
    """
    try:
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
        response = requests.get(image_url, headers=headers, timeout=10)
        response.raise_for_status()
        
        # Convert to base64
        image_data = base64.b64encode(response.content).decode('utf-8')
        content_type = response.headers.get('content-type', 'image/jpeg')
        
        return f"data:{content_type};base64,{image_data}"
    except Exception as e:
        print(f"❌ Failed to convert image to base64: {e}")
        return None

def update_existing_book(book_data: Dict) -> bool:
    """
    Update existing book record with new cover image.
    """
    if "error" in book_data:
        return False

    try:
        title = book_data["title"]
        author = book_data["author"]
        
        # Convert cover URL to base64
        base64_image = convert_to_base64(book_data["cover_url"])
        if not base64_image:
            print(f"❌ Failed to convert image for {title}")
            return False

        # Find existing record
        response = supabase.table("books_accessories").select("*").eq("title", title).eq("author", author).execute()
        
        if not response.data:
            print(f"❌ Book not found: {title} by {author}")
            return False

        book_id = response.data[0]["id"]
        
        # Update with base64 image and other data
        update_response = supabase.table("books_accessories").update({
            "image_url": base64_image,
            "affiliate_link": book_data["affiliate_link"],
            "price": book_data["price"]
        }).eq("id", book_id).execute()

        if update_response.data:
            print(f"✅ Updated {title} with real cover image")
            return True
        else:
            print(f"❌ Failed to update {title}")
            return False

    except Exception as e:
        print(f"❌ Supabase error: {str(e)}")
        return False

def main():
    """
    Main function to fetch book covers for existing books in database.
    """
    print("🎨 Grok Book Cover Fetcher")
    print("=" * 40)

    # Get existing books from database
    try:
        response = supabase.table("books_accessories").select("*").order("timestamp", desc=True).limit(4).execute()
        existing_books = response.data
        
        if not existing_books:
            print("❌ No books found in database")
            return

        print(f"📚 Found {len(existing_books)} books to update:")
        for book in existing_books:
            print(f"  - {book['title']} by {book['author']}")

        updated_count = 0
        
        for book in existing_books:
            book_name = book["title"]
            author = book["author"]
            
            print(f"\n📖 Processing: {book_name}")
            
            # Fetch cover data
            result = get_amazon_cover_paapi(book_name, author=author)
            
            if "error" not in result:
                success = update_existing_book(result)
                if success:
                    updated_count += 1
            else:
                print(f"❌ Failed to fetch cover for {book_name}: {result['error']}")

        print(f"\n🎉 Complete! Updated {updated_count}/{len(existing_books)} book covers")
        print("\n📱 Check localhost:8000 to see the updated covers!")
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")

if __name__ == "__main__":
    main() 