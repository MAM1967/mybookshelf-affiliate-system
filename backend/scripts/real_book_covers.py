#!/usr/bin/env python3
"""
Real Book Covers and Data Fetcher with Approved PA API Access
Updates database with actual Amazon book data and images
"""

import os
import sys
import requests
import base64
from io import BytesIO
from PIL import Image
from supabase import create_client, Client

# Amazon PA API using python-amazon-paapi
from amazon_paapi import AmazonApi
from amazon_paapi.helpers import ArgumentsBuilder

# Amazon PA API credentials - Using your actual credentials  
AMAZON_ACCESS_KEY = "AKPAKBWO841751230292"
AMAZON_SECRET_KEY = "5oKcOURG4kWFu09+bhHHXSUCusTwWzevVIV0e9Qx"
AMAZON_PARTNER_TAG = "mybookshelf-20"

# Supabase credentials
SUPABASE_URL = "https://ackcgrnizuhauccnbiml.supabase.co"
SUPABASE_ANON_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImFja2Nncm5penVoYXVjY25iaW1sIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTEyMjc4MzEsImV4cCI6MjA2NjgwMzgzMX0.SXpIMuNBgUhcEQUHzpEB1zZAdF-UTGvmY81EFUtsAwc"

def init_amazon_api():
    """Initialize Amazon PA API client"""
    try:
        amazon = AmazonApi(
            key=AMAZON_ACCESS_KEY,
            secret=AMAZON_SECRET_KEY,
            tag=AMAZON_PARTNER_TAG,
            country="US"
        )
        print("✅ Amazon PA API client initialized successfully")
        return amazon
    except Exception as e:
        print(f"❌ Failed to initialize Amazon PA API: {e}")
        return None

def get_supabase_client():
    """Create and return Supabase client"""
    try:
        client = create_client(SUPABASE_URL, SUPABASE_ANON_KEY)
        print("✅ Supabase client initialized successfully")
        return client
    except Exception as e:
        print(f"❌ Failed to initialize Supabase client: {e}")
        return None

def search_book_on_amazon(amazon, title, author):
    """Search for a book on Amazon and return the best match"""
    try:
        # Search for the book
        search_query = f"{title} {author}"
        print(f"🔍 Searching Amazon for: {search_query}")
        
        results = amazon.search_items(keywords=search_query, item_count=5)
        
        if results and 'Items' in results:
            # Get the first (most relevant) result
            item = results['Items'][0]
            
            # Extract book information
            book_data = {
                'asin': item.get('ASIN', ''),
                'title': item['ItemInfo']['Title']['DisplayValue'] if 'ItemInfo' in item and 'Title' in item['ItemInfo'] else title,
                'author': ', '.join([author['DisplayValue'] for author in item['ItemInfo']['ByLineInfo']['Contributors']]) if 'ItemInfo' in item and 'ByLineInfo' in item['ItemInfo'] and 'Contributors' in item['ItemInfo']['ByLineInfo'] else author,
                'price': float(item['Offers']['Listings'][0]['Price']['Amount']) / 100 if 'Offers' in item and 'Listings' in item['Offers'] and item['Offers']['Listings'] else 0.0,
                'currency': item['Offers']['Listings'][0]['Price']['Currency'] if 'Offers' in item and 'Listings' in item['Offers'] and item['Offers']['Listings'] else 'USD',
                'affiliate_link': item['DetailPageURL'] if 'DetailPageURL' in item else f"https://amazon.com/dp/{item.get('ASIN', '')}?tag={AMAZON_PARTNER_TAG}",
                'image_url': item['Images']['Primary']['Large']['URL'] if 'Images' in item and 'Primary' in item['Images'] and 'Large' in item['Images']['Primary'] else None
            }
            
            print(f"✅ Found book: {book_data['title']} by {book_data['author']} - ${book_data['price']}")
            return book_data
            
    except Exception as e:
        print(f"❌ Amazon search failed: {e}")
    
    return None

def download_and_convert_image(image_url):
    """Download image and convert to base64 data URL"""
    try:
        response = requests.get(image_url, timeout=10)
        response.raise_for_status()
        
        # Open and optimize image
        img = Image.open(BytesIO(response.content))
        
        # Convert to RGB if necessary
        if img.mode in ('RGBA', 'P'):
            img = img.convert('RGB')
        
        # Resize to reasonable size (max 400px width)
        if img.width > 400:
            ratio = 400 / img.width
            new_height = int(img.height * ratio)
            img = img.resize((400, new_height), Image.Resampling.LANCZOS)
        
        # Save as JPEG with good quality
        buffer = BytesIO()
        img.save(buffer, format='JPEG', quality=85, optimize=True)
        buffer.seek(0)
        
        # Convert to base64
        base64_data = base64.b64encode(buffer.getvalue()).decode('utf-8')
        data_url = f"data:image/jpeg;base64,{base64_data}"
        
        print(f"✅ Image converted to base64 ({len(base64_data)} chars)")
        return data_url
        
    except Exception as e:
        print(f"❌ Image conversion failed: {e}")
        return None

def update_book_in_database(supabase, book_id, book_data, image_data_url):
    """Update book record in Supabase database"""
    try:
        # Prepare update data
        update_data = {
            'title': book_data['title'],
            'author': book_data['author'],
            'price': book_data['price'],
            'affiliate_link': book_data['affiliate_link'],
            'image_url': image_data_url,
            'category': 'Books'
        }
        
        # Update the record
        response = supabase.table('books_accessories').update(update_data).eq('id', book_id).execute()
        
        if response.data:
            print(f"✅ Updated book ID {book_id} in database")
            return True
        else:
            print(f"❌ Failed to update book ID {book_id}")
            return False
            
    except Exception as e:
        print(f"❌ Database update failed for book ID {book_id}: {e}")
        return False

def main():
    """Main function to fetch and update all book covers"""
    print("🚀 Starting Real Book Cover Fetcher with Approved PA API Access")
    
    # Initialize connections
    supabase = get_supabase_client()
    if not supabase:
        print("❌ Failed to connect to Supabase")
        return
    
    amazon = init_amazon_api()
    if not amazon:
        print("❌ Failed to initialize Amazon API")
        return
    
    # Book information to search for
    books_to_update = [
        {
            'id': 17,
            'title': 'The Five Dysfunctions of a Team',
            'author': 'Patrick Lencioni'
        },
        {
            'id': 18,
            'title': 'The Advantage',
            'author': 'Patrick Lencioni'
        },
        {
            'id': 19,
            'title': 'Atomic Habits',
            'author': 'James Clear'
        },
        {
            'id': 20,
            'title': 'Leadership Journal',
            'author': 'Business Essentials'
        }
    ]
    
    print(f"\n📚 Processing {len(books_to_update)} books...")
    
    success_count = 0
    for book_info in books_to_update:
        print(f"\n📖 Processing: {book_info['title']} by {book_info['author']}")
        
        # Search for book on Amazon
        book_data = search_book_on_amazon(amazon, book_info['title'], book_info['author'])
        
        if book_data and book_data['image_url']:
            # Download and convert image
            image_data_url = download_and_convert_image(book_data['image_url'])
            
            if image_data_url:
                # Update database
                if update_book_in_database(supabase, book_info['id'], book_data, image_data_url):
                    success_count += 1
                    print(f"✅ Successfully updated {book_info['title']}")
                else:
                    print(f"❌ Failed to update {book_info['title']}")
            else:
                print(f"❌ Failed to process image for {book_info['title']}")
        else:
            print(f"❌ Could not find {book_info['title']} on Amazon")
    
    print(f"\n🎉 Completed! Successfully updated {success_count}/{len(books_to_update)} books")
    
    if success_count > 0:
        print("✅ Database now contains real Amazon book covers and data!")
        print("🌐 Refresh your web app to see the changes")

if __name__ == "__main__":
    main() 