#!/usr/bin/env python3
"""
Test Daily Price Updater
Tests the price update functionality with a small subset
"""

import os
import sys
from daily_price_updater import DailyPriceUpdater

# Override the default 25-hour limit for testing
class TestPriceUpdater(DailyPriceUpdater):
    """Test version that processes only 3 items for validation"""
    
    def get_items_to_update(self, limit_hours: int = 0) -> list:
        """Override to get just 3 items for testing"""
        try:
            # Get all active items, limit to 3 for testing
            response = self.supabase.table('books_accessories').select(
                'id, title, affiliate_link, price, price_status, last_price_check, price_fetch_attempts'
            ).filter(
                'price_status', 'neq', 'disabled'
            ).limit(3).execute()
            
            items = response.data
            self.stats['total_items'] = len(items)
            
            print(f"📋 TEST MODE: Selected {len(items)} items for testing:")
            for item in items:
                print(f"   • {item['title'][:40]}... (${item.get('price', 'N/A')})")
            
            return items
            
        except Exception as e:
            print(f"❌ Failed to fetch test items: {e}")
            return []

def main():
    """Test the price updater with 3 items"""
    print("🧪 TESTING DAILY PRICE UPDATER")
    print("=" * 50)
    print("This will test price updates on 3 items only")
    print("=" * 50)
    
    # Ask for confirmation
    response = input("\nProceed with test? (y/N): ").strip().lower()
    if response != 'y':
        print("Test cancelled.")
        return
    
    # Run test
    test_updater = TestPriceUpdater()
    test_updater.run_daily_update()

if __name__ == "__main__":
    main() 