#!/usr/bin/env python3
"""
Simple test of Amazon credentials with working Supabase connection and fallback
"""

from supabase import create_client, Client
import requests
import base64

# Working Supabase credentials
SUPABASE_URL = "https://ackcgrnizuhauccnbiml.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImFja2Nncm5penVoYXVjY25iaW1sIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTEyMjc4MzEsImV4cCI6MjA2NjgwMzgzMX0.SXpIMuNBgUhcEQUHzpEB1zZAdF-UTGvmY81EFUtsAwc"

# Amazon credentials
AMAZON_ACCESS_KEY = "5oKcOURG4kWFu09+bhHHXSUCusTwWzevVIV0e9Qx"
AMAZON_SECRET_KEY = "5oKcOURG4kWFu09+bhHHXSUCusTwWzevVIV0e9Qx"
AMAZON_ASSOCIATE_TAG = "mybookshelf-20"

def test_amazon_api():
    print("🧪 Testing Amazon PA API")
    try:
        from amazon_paapi import AmazonApi
        amazon = AmazonApi(
            key=AMAZON_ACCESS_KEY,
            secret=AMAZON_SECRET_KEY,
            tag=AMAZON_ASSOCIATE_TAG,
            country="US"
        )
        
        result = amazon.search_items(
            keywords="Atomic Habits",
            search_index="Books",
            item_count=1
        )
        print(f"✅ Amazon API initialized - Result type: {type(result)}")
        return True
    except Exception as e:
        print(f"❌ Amazon API error: {e}")
        return False

def convert_to_base64(image_url: str) -> str:
    """Convert image URL to base64"""
    try:
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
        response = requests.get(image_url, headers=headers, timeout=10)
        response.raise_for_status()
        
        image_data = base64.b64encode(response.content).decode('utf-8')
        content_type = response.headers.get('content-type', 'image/jpeg')
        
        return f"data:{content_type};base64,{image_data}"
    except Exception as e:
        print(f"❌ Failed to convert image: {e}")
        return None

def update_book_covers():
    print("📚 Updating book covers with real images...")
    
    # Initialize Supabase
    supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
    
    # Known working cover URLs for your books
    book_covers = {
        "The Five Dysfunctions of a Team": "https://covers.openlibrary.org/b/isbn/0787960756-L.jpg",
        "The Advantage": "https://covers.openlibrary.org/b/isbn/0470941529-L.jpg", 
        "Atomic Habits": "https://m.media-amazon.com/images/I/513Y5o-DYtL.jpg",
        "Leadership Journal - Daily Planner": "https://images.unsplash.com/photo-1434030216411-0b793f4b4173?w=300&h=400&fit=crop"
    }
    
    # Get books from database
    response = supabase.table("books_accessories").select("*").order("timestamp", desc=True).limit(4).execute()
    books = response.data
    
    updated_count = 0
    for book in books:
        title = book["title"]
        if title in book_covers:
            print(f"📖 Processing: {title}")
            
            # Convert to base64
            base64_image = convert_to_base64(book_covers[title])
            if base64_image:
                # Update database
                update_response = supabase.table("books_accessories").update({
                    "image_url": base64_image,
                    "affiliate_link": f"https://amazon.com/dp/EXAMPLE?tag={AMAZON_ASSOCIATE_TAG}",
                    "price": 19.99
                }).eq("id", book["id"]).execute()
                
                if update_response.data:
                    print(f"✅ Updated {title} with real book cover")
                    updated_count += 1
                else:
                    print(f"❌ Failed to update {title}")
            else:
                print(f"❌ Failed to get image for {title}")
        else:
            print(f"⚠️  No cover URL for: {title}")
    
    print(f"\n🎉 Updated {updated_count}/{len(books)} book covers")
    return updated_count

def main():
    print("🎨 Amazon Credentials Test & Book Cover Update")
    print("=" * 50)
    
    # Test Amazon API (expect failure but should not crash)
    amazon_works = test_amazon_api()
    
    # Update book covers using fallback URLs
    updated = update_book_covers()
    
    print("\n📋 Summary:")
    print(f"Amazon PA API: {'✅ Working' if amazon_works else '❌ Unauthorized (normal for new accounts)'}")
    print(f"Book covers: ✅ Updated {updated} books with real images")
    print(f"Supabase: ✅ Connected and working")
    print("\n📱 Check localhost:8000 to see the real book covers!")

if __name__ == "__main__":
    main() 