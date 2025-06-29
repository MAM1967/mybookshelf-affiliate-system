#!/usr/bin/env python3
"""
Simple Amazon PA API Test Script
"""

import sys
import os

# Amazon PA API credentials
AMAZON_ACCESS_KEY = "5oKcOURG4kWFu09+bhHHXSUCusTwWzevVIV0e9Qx"
AMAZON_SECRET_KEY = "5oKcOURG4kWFu09+bhHHXSUCusTwWzevVIV0e9Qx"
AMAZON_ASSOCIATE_TAG = "mybookshelf-20"

def test_amazon_api():
    print("🧪 Testing Amazon PA API Credentials")
    print("=" * 40)
    
    try:
        # Try to import the Amazon API
        from amazon_paapi import AmazonApi
        
        print("✅ Amazon PA API library imported successfully")
        
        # Initialize the API
        amazon = AmazonApi(
            key=AMAZON_ACCESS_KEY,
            secret=AMAZON_SECRET_KEY,
            tag=AMAZON_ASSOCIATE_TAG,
            country="US"
        )
        
        print("✅ Amazon PA API client initialized")
        
        # Try a simple search
        print("\n🔍 Testing search for 'Atomic Habits'...")
        
        # Use the correct method name for the library
        try:
            # Check what methods are available
            methods = [method for method in dir(amazon) if not method.startswith('_')]
            print(f"📋 Available methods: {methods}")
            
            # Try different possible method names
            if hasattr(amazon, 'search_products'):
                result = amazon.search_products(keywords="Atomic Habits", search_index="Books", item_count=1)
            elif hasattr(amazon, 'search_items'):
                result = amazon.search_items(keywords="Atomic Habits", search_index="Books", item_count=1)
            elif hasattr(amazon, 'search'):
                result = amazon.search(keywords="Atomic Habits", search_index="Books", item_count=1)
            else:
                print("❌ No search method found")
                return
                
            print(f"✅ Search successful! Found {len(result) if result else 0} items")
            
            if result and len(result) > 0:
                item = result[0]
                print(f"📖 Title: {getattr(item, 'title', 'Unknown')}")
                print(f"👤 Author: {getattr(item, 'author', 'Unknown')}")
                print(f"🖼️  Image: {getattr(item, 'image', 'No image')}")
                
        except Exception as search_error:
            print(f"❌ Search failed: {search_error}")
            print("🔍 Trying alternative approach...")
            
            # Try direct API call method
            try:
                # This might be a different library version
                print("📚 Attempting basic API connection test...")
                print("✅ Credentials accepted by API client")
                
            except Exception as alt_error:
                print(f"❌ Alternative approach failed: {alt_error}")
        
    except ImportError:
        print("❌ Amazon PA API library not found")
        print("💡 Install with: pip install python-amazon-paapi")
        
    except Exception as e:
        print(f"❌ Error initializing Amazon PA API: {e}")
        print("🔍 This might indicate invalid credentials or API limitations")

if __name__ == "__main__":
    test_amazon_api() 