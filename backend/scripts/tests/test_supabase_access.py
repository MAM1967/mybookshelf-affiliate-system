#!/usr/bin/env python3
"""
Test Supabase Access Patterns
Understand how Supabase handles different operations
"""

import os
import sys
import requests
import json
from supabase import create_client, Client

# Supabase configuration
SUPABASE_URL = "https://ackcgrnizuhauccnbiml.supabase.co"
SUPABASE_ANON_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImFja2Nncm5penVoYXVjY25iaW1sIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTEyMjc4MzEsImV4cCI6MjA2NjgwMzgzMX0.SXpIMuNBgUhcEQUHzpEB1zZAdF-UTGvmY81EFUtsAwc"

def test_existing_table_access():
    """Test access to existing tables"""
    
    print("🧪 Testing Existing Table Access...")
    
    try:
        supabase: Client = create_client(SUPABASE_URL, SUPABASE_ANON_KEY)
        print("✅ Connected to Supabase")
        
        # Test 1: Access existing table
        print("\n1. Testing books_accessories table...")
        try:
            result = supabase.table('books_accessories').select('id, title').limit(1).execute()
            print("✅ books_accessories table accessible")
            print(f"   Sample data: {result.data[0] if result.data else 'No data'}")
        except Exception as e:
            print(f"❌ books_accessories error: {e}")
        
        # Test 2: Access existing table with insert
        print("\n2. Testing insert to existing table...")
        try:
            test_data = {
                "title": "Test Book",
                "author": "Test Author", 
                "price": 9.99,
                "affiliate_link": "https://amazon.com/test",
                "image_url": "https://example.com/test.jpg",
                "category": "test"
            }
            result = supabase.table('books_accessories').insert(test_data).execute()
            print("✅ Insert to books_accessories successful")
            
            # Clean up test data
            if result.data:
                supabase.table('books_accessories').delete().eq('title', 'Test Book').execute()
                print("✅ Test data cleaned up")
        except Exception as e:
            print(f"❌ Insert error: {e}")
        
        return True
        
    except Exception as e:
        print(f"❌ Connection error: {e}")
        return False

def test_nonexistent_table_access():
    """Test access to non-existent tables"""
    
    print("\n🧪 Testing Non-Existent Table Access...")
    
    try:
        supabase: Client = create_client(SUPABASE_URL, SUPABASE_ANON_KEY)
        
        # Test 1: Select from non-existent table
        print("\n1. Testing select from price_validation_queue...")
        try:
            result = supabase.table('price_validation_queue').select('*').limit(1).execute()
            print("✅ price_validation_queue table exists!")
            return True
        except Exception as e:
            print(f"❌ price_validation_queue select error: {e}")
        
        # Test 2: Insert to non-existent table
        print("\n2. Testing insert to price_validation_queue...")
        try:
            test_data = {
                "item_id": 1,
                "old_price": 10.00,
                "new_price": 85.00,
                "percentage_change": 750.0,
                "validation_reason": "test",
                "validation_layer": "test",
                "status": "pending"
            }
            result = supabase.table('price_validation_queue').insert(test_data).execute()
            print("✅ Insert to price_validation_queue successful!")
            return True
        except Exception as e:
            print(f"❌ price_validation_queue insert error: {e}")
        
        return False
        
    except Exception as e:
        print(f"❌ Connection error: {e}")
        return False

def test_rest_api_access():
    """Test REST API access patterns"""
    
    print("\n🧪 Testing REST API Access...")
    
    headers = {
        'apikey': SUPABASE_ANON_KEY,
        'Authorization': f'Bearer {SUPABASE_ANON_KEY}',
        'Content-Type': 'application/json'
    }
    
    # Test 1: Access existing table via REST
    print("\n1. Testing REST access to books_accessories...")
    try:
        response = requests.get(
            f"{SUPABASE_URL}/rest/v1/books_accessories?select=id,title&limit=1",
            headers=headers
        )
        print(f"✅ REST books_accessories status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"   Data: {data}")
    except Exception as e:
        print(f"❌ REST books_accessories error: {e}")
    
    # Test 2: Access non-existent table via REST
    print("\n2. Testing REST access to price_validation_queue...")
    try:
        response = requests.get(
            f"{SUPABASE_URL}/rest/v1/price_validation_queue?select=id&limit=1",
            headers=headers
        )
        print(f"✅ REST price_validation_queue status: {response.status_code}")
        if response.status_code == 200:
            print("✅ Table exists via REST!")
            return True
        elif response.status_code == 404:
            print("❌ Table does not exist via REST")
        else:
            print(f"❌ Unexpected status: {response.status_code}")
            print(f"   Response: {response.text}")
    except Exception as e:
        print(f"❌ REST price_validation_queue error: {e}")
    
    return False

def test_schema_information():
    """Test getting schema information"""
    
    print("\n🧪 Testing Schema Information...")
    
    headers = {
        'apikey': SUPABASE_ANON_KEY,
        'Authorization': f'Bearer {SUPABASE_ANON_KEY}',
        'Content-Type': 'application/json'
    }
    
    try:
        # Get schema information
        response = requests.get(
            f"{SUPABASE_URL}/rest/v1/",
            headers=headers
        )
        
        if response.status_code == 200:
            schema = response.json()
            print("✅ Schema information retrieved")
            
            # Look for price_validation_queue in the schema
            if 'paths' in schema:
                tables = list(schema['paths'].keys())
                print(f"   Available tables: {tables}")
                
                if '/price_validation_queue' in tables:
                    print("✅ price_validation_queue found in schema!")
                    return True
                else:
                    print("❌ price_validation_queue not found in schema")
        else:
            print(f"❌ Schema request failed: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Schema error: {e}")
    
    return False

def main():
    """Main function"""
    
    print("🔍 SUPABASE ACCESS PATTERN ANALYSIS")
    print("=" * 60)
    
    # Test existing table access
    existing_works = test_existing_table_access()
    
    # Test non-existent table access
    nonexistent_works = test_nonexistent_table_access()
    
    # Test REST API access
    rest_works = test_rest_api_access()
    
    # Test schema information
    schema_works = test_schema_information()
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 TEST SUMMARY")
    print("=" * 60)
    print(f"✅ Existing table access: {'Working' if existing_works else 'Failed'}")
    print(f"✅ Non-existent table access: {'Working' if nonexistent_works else 'Failed'}")
    print(f"✅ REST API access: {'Working' if rest_works else 'Failed'}")
    print(f"✅ Schema information: {'Working' if schema_works else 'Failed'}")
    
    if nonexistent_works:
        print("\n🎉 SUCCESS! The table can be accessed.")
        print("The anomalous price approval interface should be operational.")
    else:
        print("\n❌ The table does not exist and cannot be created programmatically.")
        print("Manual setup is required in the Supabase dashboard.")

if __name__ == "__main__":
    main() 