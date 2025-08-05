#!/usr/bin/env python3
"""
Check price updates from yesterday (August 4, 2025)
"""

import os
import sys
from supabase import create_client, Client
from datetime import datetime, timedelta

# Set up Supabase connection
url = 'https://ackcgrnizuhauccnbiml.supabase.co'
key = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImFja2Nncm5penVoYXVjY25iaW1sIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTEyMjc4MzEsImV4cCI6MjA2NjgwMzgzMX0.SXpIMuNBgUhcEQUHzpEB1zZAdF-UTGvmY81EFUtsAwc'

supabase: Client = create_client(url, key)

# Check price history for August 4, 2025
yesterday = datetime.now() - timedelta(days=1)
yesterday_str = yesterday.strftime('%Y-%m-%d')

print(f'Checking price updates for {yesterday_str}...')

# Query price history for yesterday with book titles
response = supabase.table('price_history').select('*, books_accessories(title)').gte('updated_at', f'{yesterday_str}T00:00:00').lt('updated_at', f'{yesterday_str}T23:59:59').execute()

print(f'Price history entries for {yesterday_str}: {len(response.data)}')

if response.data:
    print('Recent price changes:')
    for entry in response.data[:10]:  # Show first 10
        book_title = entry.get('books_accessories', {}).get('title', 'Unknown Title')
        old_price = entry.get("old_price", 0)
        new_price = entry.get("new_price", 0)
        change_percent = entry.get("price_change_percent", 0)
        if change_percent is None:
            change_percent = 0
        print(f'- {book_title}: ${old_price} → ${new_price} ({change_percent:.1f}%)')

# Check books_accessories table for last price updates
response2 = supabase.table('books_accessories').select('id, title, price, price_updated_at').not_.is_('price_updated_at', 'null').order('price_updated_at', desc=True).limit(10).execute()

print(f'\nMost recent price updates:')
for item in response2.data:
    updated_at = item.get('price_updated_at', '')
    if updated_at:
        print(f'- {item.get("title", "unknown")}: ${item.get("price", 0)} (updated: {updated_at})')

# Check total items and their status
response3 = supabase.table('books_accessories').select('id, title, price, price_status, last_price_check').execute()

total_items = len(response3.data)
active_items = len([item for item in response3.data if item.get('price_status') == 'active'])
out_of_stock = len([item for item in response3.data if item.get('price_status') == 'out_of_stock'])
error_items = len([item for item in response3.data if item.get('price_status') == 'error'])

print(f'\nDatabase Summary:')
print(f'- Total items: {total_items}')
print(f'- Active items: {active_items}')
print(f'- Out of stock: {out_of_stock}')
print(f'- Error items: {error_items}') 