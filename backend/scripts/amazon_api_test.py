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
        from paapi5_python_sdk import DefaultApi, SearchItemsRequest, SearchItemsResource, PartnerType
        from paapi5_python_sdk.rest import ApiException
        
        print("✅ Amazon PA API library imported successfully")
        
        # Initialize the API
        amazon_api = DefaultApi(
            access_key=AMAZON_ACCESS_KEY,
            secret_key=AMAZON_SECRET_KEY,
            host="webservices.amazon.com",
            region="us-east-1"
        )
        
        print("✅ Amazon PA API client initialized")
        
        # Try a simple search
        print("\n🔍 Testing search for 'Atomic Habits'...")
        
        try:
            search_items_request = SearchItemsRequest(
                partner_tag=AMAZON_ASSOCIATE_TAG,
                partner_type=PartnerType.ASSOCIATES,
                keywords="Atomic Habits",
                search_index="Books",
                item_count=1,
                resources=[
                    SearchItemsResource.ITEMINFO_TITLE,
                    SearchItemsResource.ITEMINFO_BYLINEINFO,
                    SearchItemsResource.OFFERS_LISTINGS_PRICE
                ]
            )
            
            response = amazon_api.search_items(search_items_request)
            
            print(f"✅ Search successful!")
            
            if response.search_result and response.search_result.items:
                item = response.search_result.items[0]
                print(f"📖 Title: {item.item_info.title.display_value if item.item_info and item.item_info.title else 'Unknown'}")
                print(f"👤 Author: {item.item_info.by_line_info.contributors[0].name if item.item_info and item.item_info.by_line_info and item.item_info.by_line_info.contributors else 'Unknown'}")
                print(f"🖼️  ASIN: {item.asin}")
                
        except ApiException as api_error:
            print(f"❌ API Error: {api_error}")
            print("🔍 This might indicate invalid credentials or API limitations")
        except Exception as search_error:
            print(f"❌ Search failed: {search_error}")
            print("🔍 This might indicate invalid credentials or API limitations")
        
    except ImportError:
        print("❌ Amazon PA API library not found")
        print("💡 Install with: pip install amazon-paapi5")
        
    except Exception as e:
        print(f"❌ Error initializing Amazon PA API: {e}")
        print("🔍 This might indicate invalid credentials or API limitations")

if __name__ == "__main__":
    test_amazon_api() 