#!/usr/bin/env python3
"""
Daily Price Update Automation
Fetches current prices for all items and updates database
Scheduled to run daily at 1 AM
"""

import os
import sys
import logging
import requests
import re
from datetime import datetime, timedelta
from decimal import Decimal, InvalidOperation
from typing import Dict, List, Optional, Tuple
import time
import json

# Configure logging
logging.basicConfig(
    level=logging.INFO, 
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(f'price_update_{datetime.now().strftime("%Y%m%d")}.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Set up environment
os.environ.setdefault('SUPABASE_URL', 'https://ackcgrnizuhauccnbiml.supabase.co')
os.environ.setdefault('SUPABASE_ANON_KEY', 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImFja2Nncm5penVoYXVjY25iaW1sIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTEyMjc4MzEsImV4cCI6MjA2NjgwMzgzMX0.SXpIMuNBgUhcEQUHzpEB1zZAdF-UTGvmY81EFUtsAwc')

class DailyPriceUpdater:
    """Automated daily price updater for MyBookshelf affiliate system"""
    
    def __init__(self):
        """Initialize the price updater"""
        try:
            from supabase import create_client, Client
            self.supabase: Client = create_client(
                os.environ['SUPABASE_URL'],
                os.environ['SUPABASE_ANON_KEY']
            )
            logger.info("✅ Connected to Supabase")
            
            # Price update statistics
            self.stats = {
                'total_items': 0,
                'updated_items': 0,
                'unchanged_items': 0,
                'out_of_stock_items': 0,
                'error_items': 0,
                'price_increases': 0,
                'price_decreases': 0,
                'total_price_change': Decimal('0')
            }
            
        except Exception as e:
            logger.error(f"❌ Failed to connect to Supabase: {e}")
            sys.exit(1)
    
    def get_items_to_update(self, limit_hours: int = 25) -> List[Dict]:
        """Get items that need price updates (not updated in last 24+ hours)"""
        logger.info(f"🔍 Fetching items for price update...")
        
        try:
            # Get items that haven't been checked in the last 25 hours
            # or have never been checked
            cutoff_time = datetime.now() - timedelta(hours=limit_hours)
            
            response = self.supabase.table('books_accessories').select(
                'id, title, affiliate_link, price, price_status, last_price_check, price_fetch_attempts'
            ).filter(
                'price_status', 'neq', 'disabled'  # Skip disabled items
            ).execute()
            
            all_items = response.data
            
            # Filter items that need updates
            items_to_update = []
            for item in all_items:
                should_update = False
                
                # Never been checked
                if not item.get('last_price_check'):
                    should_update = True
                else:
                    # Parse last check time
                    try:
                        last_check = datetime.fromisoformat(item['last_price_check'].replace('Z', '+00:00'))
                        if last_check < cutoff_time:
                            should_update = True
                    except (ValueError, AttributeError):
                        should_update = True  # Invalid date, needs update
                
                # Skip items with too many failed attempts (max 5)
                if item.get('price_fetch_attempts', 0) >= 5:
                    logger.warning(f"   ⚠️ Skipping {item['title']} - too many failed attempts")
                    continue
                
                if should_update:
                    items_to_update.append(item)
            
            logger.info(f"   📊 Found {len(items_to_update)} items needing price updates")
            self.stats['total_items'] = len(items_to_update)
            return items_to_update
            
        except Exception as e:
            logger.error(f"❌ Failed to fetch items: {e}")
            return []
    
    def extract_asin_from_link(self, affiliate_link: str) -> Optional[str]:
        """Extract ASIN from Amazon affiliate link"""
        if not affiliate_link:
            return None
        
        # Multiple patterns to extract ASIN
        patterns = [
            r'/dp/([A-Z0-9]{10})',           # Standard product page
            r'/gp/product/([A-Z0-9]{10})',   # Alternative product page
            r'ASIN=([A-Z0-9]{10})',         # Query parameter
            r'/([A-Z0-9]{10})/?'            # ASIN at end of path
        ]
        
        for pattern in patterns:
            match = re.search(pattern, affiliate_link)
            if match:
                return match.group(1)
        
        return None
    
    def fetch_amazon_price(self, affiliate_link: str, asin: str = None) -> Tuple[Optional[Decimal], str, str]:
        """
        Fetch current price from Amazon
        Returns: (price, status, notes)
        """
        if not asin:
            asin = self.extract_asin_from_link(affiliate_link)
        
        if not asin:
            return None, 'error', 'Could not extract ASIN from link'
        
        try:
            # Amazon product page headers to mimic browser
            headers = {
                'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
                'Accept-Language': 'en-US,en;q=0.9',
                'Accept-Encoding': 'gzip, deflate, br',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                'Connection': 'keep-alive',
                'Upgrade-Insecure-Requests': '1'
            }
            
            # Construct Amazon URL
            amazon_url = f"https://www.amazon.com/dp/{asin}"
            
            logger.info(f"   🔗 Fetching price for ASIN: {asin}")
            
            response = requests.get(amazon_url, headers=headers, timeout=15)
            response.raise_for_status()
            
            # Price extraction patterns (multiple formats)
            price_patterns = [
                r'<span class="a-price-whole">([0-9,]+)</span><span class="a-price-fraction">([0-9]+)</span>',
                r'<span class="a-price a-text-price a-size-medium apb-price-current"><span class="a-offscreen">\$([0-9,]+\.?[0-9]*)</span>',
                r'"priceAmount":([0-9]+\.?[0-9]*)',
                r'<span class="a-price-range">.*?\$([0-9,]+\.?[0-9]*)',
                r'id="apex_desktop".*?<span class="a-offscreen">\$([0-9,]+\.?[0-9]*)</span>',
                r'<span class="a-offscreen">\$([0-9,]+\.?[0-9]*)</span>'
            ]
            
            content = response.text
            
            # Check for out of stock indicators
            out_of_stock_patterns = [
                r'Currently unavailable',
                r'Out of Stock',
                r'Temporarily out of stock',
                r'This item is not available',
                r'Product not available'
            ]
            
            for pattern in out_of_stock_patterns:
                if re.search(pattern, content, re.IGNORECASE):
                    return Decimal('0'), 'out_of_stock', 'Product currently unavailable'
            
            # Try to extract price
            for pattern in price_patterns:
                match = re.search(pattern, content)
                if match:
                    if len(match.groups()) == 2:  # whole and fraction parts
                        price_str = f"{match.group(1).replace(',', '')}.{match.group(2)}"
                    else:
                        price_str = match.group(1).replace(',', '')
                    
                    try:
                        price = Decimal(price_str)
                        if price > 0:
                            logger.info(f"   ✅ Found price: ${price}")
                            return price, 'active', 'Price updated successfully'
                        else:
                            return Decimal('0'), 'out_of_stock', 'Price is zero'
                    except (InvalidOperation, ValueError):
                        continue
            
            # No price found
            return None, 'error', 'Could not parse price from page'
            
        except requests.exceptions.Timeout:
            return None, 'error', 'Request timeout'
        except requests.exceptions.RequestException as e:
            return None, 'error', f'Request failed: {str(e)[:100]}'
        except Exception as e:
            return None, 'error', f'Unexpected error: {str(e)[:100]}'
    
    def update_item_price(self, item: Dict, new_price: Optional[Decimal], status: str, notes: str) -> bool:
        """Update item price and tracking information in database"""
        try:
            item_id = item['id']
            old_price = Decimal(str(item.get('price', 0))) if item.get('price') else Decimal('0')
            
            # Prepare update data
            update_data = {
                'last_price_check': datetime.now().isoformat(),
                'price_status': status,
                'price_source': 'automated',
                'price_fetch_attempts': item.get('price_fetch_attempts', 0) + 1
            }
            
            # Update price if we got a valid price
            if new_price is not None:
                update_data['price'] = float(new_price)
                update_data['price_updated_at'] = datetime.now().isoformat()
                update_data['price_fetch_attempts'] = 0  # Reset attempts on success
            
            # Update the main record
            self.supabase.table('books_accessories').update(update_data).eq('id', item_id).execute()
            
            # Log price change if price actually changed
            if new_price is not None and new_price != old_price:
                price_change = new_price - old_price
                price_change_percent = (price_change / old_price * 100) if old_price > 0 else None
                
                # Insert into price history
                history_data = {
                    'book_id': item_id,
                    'old_price': float(old_price),
                    'new_price': float(new_price),
                    'price_change': float(price_change),
                    'price_change_percent': float(price_change_percent) if price_change_percent else None,
                    'update_source': 'automated',
                    'notes': notes
                }
                
                self.supabase.table('price_history').insert(history_data).execute()
                
                # Update statistics
                if price_change > 0:
                    self.stats['price_increases'] += 1
                elif price_change < 0:
                    self.stats['price_decreases'] += 1
                
                self.stats['total_price_change'] += price_change
                self.stats['updated_items'] += 1
                
                logger.info(f"   📊 Price change: ${old_price} → ${new_price} ({price_change:+.2f})")
            else:
                self.stats['unchanged_items'] += 1
            
            # Update status counters
            if status == 'out_of_stock':
                self.stats['out_of_stock_items'] += 1
            elif status == 'error':
                self.stats['error_items'] += 1
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to update item {item.get('title', 'unknown')}: {e}")
            self.stats['error_items'] += 1
            return False
    
    def process_price_updates(self, items: List[Dict], delay_seconds: float = 2.0) -> None:
        """Process price updates for all items with rate limiting"""
        logger.info(f"🔄 Starting price updates for {len(items)} items...")
        
        for i, item in enumerate(items, 1):
            try:
                logger.info(f"📖 [{i}/{len(items)}] Processing: {item['title'][:50]}...")
                
                # Fetch current price
                new_price, status, notes = self.fetch_amazon_price(item['affiliate_link'])
                
                # Update database
                success = self.update_item_price(item, new_price, status, notes)
                
                if success:
                    logger.info(f"   ✅ Updated successfully")
                else:
                    logger.warning(f"   ⚠️ Update failed")
                
                # Rate limiting to avoid being blocked
                if i < len(items):  # Don't delay after last item
                    time.sleep(delay_seconds)
                    
            except Exception as e:
                logger.error(f"❌ Error processing {item['title']}: {e}")
                self.stats['error_items'] += 1
                continue
    
    def generate_summary_report(self) -> str:
        """Generate a summary report of the price update session"""
        total_processed = self.stats['updated_items'] + self.stats['unchanged_items'] + self.stats['error_items']
        success_rate = (total_processed - self.stats['error_items']) / total_processed * 100 if total_processed > 0 else 0
        
        report = f"""
📊 DAILY PRICE UPDATE SUMMARY - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
{'='*60}

📈 PROCESSING STATS:
   • Total Items Checked: {self.stats['total_items']}
   • Successfully Updated: {self.stats['updated_items']}
   • Unchanged: {self.stats['unchanged_items']}
   • Out of Stock: {self.stats['out_of_stock_items']}
   • Errors: {self.stats['error_items']}
   • Success Rate: {success_rate:.1f}%

💰 PRICE CHANGES:
   • Price Increases: {self.stats['price_increases']}
   • Price Decreases: {self.stats['price_decreases']}
   • Total Price Change: ${self.stats['total_price_change']:+.2f}

⏰ Next Update: {(datetime.now() + timedelta(hours=24)).strftime('%Y-%m-%d at 1:00 AM')}
{'='*60}
"""
        return report
    
    def save_update_report(self) -> str:
        """Save detailed update report to file"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"price_update_report_{timestamp}.json"
        
        report_data = {
            'timestamp': datetime.now().isoformat(),
            'statistics': {
                'total_items': self.stats['total_items'],
                'updated_items': self.stats['updated_items'],
                'unchanged_items': self.stats['unchanged_items'],
                'out_of_stock_items': self.stats['out_of_stock_items'],
                'error_items': self.stats['error_items'],
                'price_increases': self.stats['price_increases'],
                'price_decreases': self.stats['price_decreases'],
                'total_price_change': float(self.stats['total_price_change'])
            }
        }
        
        with open(filename, 'w') as f:
            json.dump(report_data, f, indent=2)
        
        return filename
    
    def run_daily_update(self) -> None:
        """Main function to run the daily price update process"""
        logger.info("🚀 Starting Daily Price Update Process")
        logger.info("=" * 60)
        
        start_time = datetime.now()
        
        try:
            # Get items to update
            items = self.get_items_to_update()
            
            if not items:
                logger.info("ℹ️ No items need price updates at this time")
                return
            
            # Process updates
            self.process_price_updates(items)
            
            # Generate and save report
            report_file = self.save_update_report()
            summary = self.generate_summary_report()
            
            logger.info(summary)
            logger.info(f"📄 Detailed report saved to: {report_file}")
            
            # Calculate total time
            end_time = datetime.now()
            duration = end_time - start_time
            logger.info(f"⏱️ Total execution time: {duration}")
            
        except Exception as e:
            logger.error(f"❌ Daily update process failed: {e}")
            sys.exit(1)

def main():
    """Main execution function"""
    updater = DailyPriceUpdater()
    updater.run_daily_update()

if __name__ == "__main__":
    main() 