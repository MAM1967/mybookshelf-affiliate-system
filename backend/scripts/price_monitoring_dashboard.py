#!/usr/bin/env python3
"""
Price Monitoring Dashboard
Displays price tracking status, recent changes, and system health
"""

import os
import sys
import json
from datetime import datetime, timedelta
from decimal import Decimal
from typing import Dict, List, Optional

# Configure environment
os.environ.setdefault('SUPABASE_URL', 'https://ackcgrnizuhauccnbiml.supabase.co')
os.environ.setdefault('SUPABASE_ANON_KEY', 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImFja2Nncm5penVoYXVjY25iaW1sIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTEyMjc4MzEsImV4cCI6MjA2NjgwMzgzMX0.SXpIMuNBgUhcEQUHzpEB1zZAdF-UTGvmY81EFUtsAwc')

class PriceMonitoringDashboard:
    """Dashboard for monitoring price tracking system"""
    
    def __init__(self):
        """Initialize the monitoring dashboard"""
        try:
            from supabase import create_client, Client
            self.supabase: Client = create_client(
                os.environ['SUPABASE_URL'],
                os.environ['SUPABASE_ANON_KEY']
            )
            print("✅ Connected to Supabase")
        except Exception as e:
            print(f"❌ Failed to connect to Supabase: {e}")
            sys.exit(1)
    
    def get_system_overview(self) -> Dict:
        """Get overall system statistics"""
        try:
            # Get all items
            response = self.supabase.table('books_accessories').select(
                'id, title, price, price_status, last_price_check, price_updated_at, price_fetch_attempts'
            ).execute()
            
            items = response.data
            now = datetime.now()
            
            stats = {
                'total_items': len(items),
                'active_items': 0,
                'out_of_stock_items': 0,
                'error_items': 0,
                'never_checked': 0,
                'checked_today': 0,
                'checked_this_week': 0,
                'needs_update': 0,
                'high_error_count': 0
            }
            
            for item in items:
                status = item.get('price_status', 'unknown')
                
                # Count by status
                if status == 'active':
                    stats['active_items'] += 1
                elif status == 'out_of_stock':
                    stats['out_of_stock_items'] += 1
                elif status == 'error':
                    stats['error_items'] += 1
                
                # Check last update time
                last_check = item.get('last_price_check')
                if not last_check:
                    stats['never_checked'] += 1
                    stats['needs_update'] += 1
                else:
                    try:
                        check_time = datetime.fromisoformat(last_check.replace('Z', '+00:00'))
                        
                        # Time-based counts
                        if check_time > now - timedelta(days=1):
                            stats['checked_today'] += 1
                        elif check_time > now - timedelta(days=7):
                            stats['checked_this_week'] += 1
                        else:
                            stats['needs_update'] += 1
                    except (ValueError, AttributeError):
                        stats['never_checked'] += 1
                        stats['needs_update'] += 1
                
                # High error count items
                if item.get('price_fetch_attempts', 0) >= 3:
                    stats['high_error_count'] += 1
            
            return stats
            
        except Exception as e:
            print(f"❌ Failed to get system overview: {e}")
            return {}
    
    def get_recent_price_changes(self, days: int = 7) -> List[Dict]:
        """Get recent price changes from history"""
        try:
            cutoff_date = (datetime.now() - timedelta(days=days)).isoformat()
            
            response = self.supabase.table('price_history').select(
                '*, books_accessories(title)'
            ).filter(
                'updated_at', 'gte', cutoff_date
            ).order('updated_at', desc=True).limit(20).execute()
            
            return response.data
            
        except Exception as e:
            print(f"❌ Failed to get recent price changes: {e}")
            return []
    
    def get_items_needing_attention(self) -> Dict[str, List[Dict]]:
        """Get items that need attention"""
        try:
            response = self.supabase.table('books_accessories').select(
                'id, title, price, price_status, last_price_check, price_fetch_attempts'
            ).execute()
            
            items = response.data
            now = datetime.now()
            
            attention_items = {
                'never_checked': [],
                'high_errors': [],
                'stale_data': [],
                'out_of_stock': []
            }
            
            for item in items:
                # Never checked
                if not item.get('last_price_check'):
                    attention_items['never_checked'].append(item)
                
                # High error count
                if item.get('price_fetch_attempts', 0) >= 3:
                    attention_items['high_errors'].append(item)
                
                # Out of stock
                if item.get('price_status') == 'out_of_stock':
                    attention_items['out_of_stock'].append(item)
                
                # Stale data (not checked in 48+ hours)
                last_check = item.get('last_price_check')
                if last_check:
                    try:
                        check_time = datetime.fromisoformat(last_check.replace('Z', '+00:00'))
                        if check_time < now - timedelta(hours=48):
                            attention_items['stale_data'].append(item)
                    except (ValueError, AttributeError):
                        attention_items['stale_data'].append(item)
            
            return attention_items
            
        except Exception as e:
            print(f"❌ Failed to get attention items: {e}")
            return {}
    
    def display_system_overview(self, stats: Dict) -> None:
        """Display system overview"""
        print("📊 SYSTEM OVERVIEW")
        print("=" * 50)
        print(f"Total Items: {stats.get('total_items', 0)}")
        print(f"Active: {stats.get('active_items', 0)}")
        print(f"Out of Stock: {stats.get('out_of_stock_items', 0)}")
        print(f"Errors: {stats.get('error_items', 0)}")
        print()
        print("📅 UPDATE STATUS:")
        print(f"Checked Today: {stats.get('checked_today', 0)}")
        print(f"Checked This Week: {stats.get('checked_this_week', 0)}")
        print(f"Need Updates: {stats.get('needs_update', 0)}")
        print(f"Never Checked: {stats.get('never_checked', 0)}")
        print(f"High Error Count: {stats.get('high_error_count', 0)}")
        print()
    
    def display_recent_changes(self, changes: List[Dict]) -> None:
        """Display recent price changes"""
        print("💰 RECENT PRICE CHANGES (Last 7 Days)")
        print("=" * 50)
        
        if not changes:
            print("No price changes in the last 7 days")
            return
        
        for change in changes[:10]:  # Show top 10
            book_title = change.get('books_accessories', {}).get('title', 'Unknown')
            old_price = change.get('old_price', 0)
            new_price = change.get('new_price', 0)
            price_change = change.get('price_change', 0)
            updated_at = change.get('updated_at', '')
            
            # Parse date
            try:
                update_time = datetime.fromisoformat(updated_at.replace('Z', '+00:00'))
                time_str = update_time.strftime('%m/%d %H:%M')
            except:
                time_str = updated_at[:16] if updated_at else 'Unknown'
            
            # Format change
            change_symbol = "📈" if price_change > 0 else "📉"
            if price_change > 0:
                change_str = f"+${price_change:.2f}"
            else:
                change_str = f"${price_change:.2f}"
            
            print(f"{change_symbol} {book_title[:35]:35} ${old_price:6.2f} → ${new_price:6.2f} ({change_str:8}) {time_str}")
        
        print()
    
    def display_attention_items(self, attention: Dict[str, List[Dict]]) -> None:
        """Display items needing attention"""
        print("⚠️ ITEMS NEEDING ATTENTION")
        print("=" * 50)
        
        # Never checked
        never_checked = attention.get('never_checked', [])
        if never_checked:
            print(f"🔍 Never Checked ({len(never_checked)}):")
            for item in never_checked[:5]:
                print(f"   • {item['title'][:45]}")
            if len(never_checked) > 5:
                print(f"   ... and {len(never_checked) - 5} more")
            print()
        
        # High errors
        high_errors = attention.get('high_errors', [])
        if high_errors:
            print(f"❌ High Error Count ({len(high_errors)}):")
            for item in high_errors[:5]:
                attempts = item.get('price_fetch_attempts', 0)
                print(f"   • {item['title'][:40]} ({attempts} attempts)")
            if len(high_errors) > 5:
                print(f"   ... and {len(high_errors) - 5} more")
            print()
        
        # Out of stock
        out_of_stock = attention.get('out_of_stock', [])
        if out_of_stock:
            print(f"📦 Out of Stock ({len(out_of_stock)}):")
            for item in out_of_stock[:5]:
                print(f"   • {item['title'][:45]}")
            if len(out_of_stock) > 5:
                print(f"   ... and {len(out_of_stock) - 5} more")
            print()
        
        # Stale data
        stale_data = attention.get('stale_data', [])
        if stale_data:
            print(f"⏰ Stale Data (48+ hours) ({len(stale_data)}):")
            for item in stale_data[:5]:
                last_check = item.get('last_price_check', 'Never')
                try:
                    if last_check != 'Never':
                        check_time = datetime.fromisoformat(last_check.replace('Z', '+00:00'))
                        hours_ago = int((datetime.now() - check_time).total_seconds() / 3600)
                        last_check = f"{hours_ago}h ago"
                except:
                    last_check = "Unknown"
                print(f"   • {item['title'][:35]:35} (Last: {last_check})")
            if len(stale_data) > 5:
                print(f"   ... and {len(stale_data) - 5} more")
            print()
    
    def get_latest_report(self) -> Optional[Dict]:
        """Get the latest price update report"""
        try:
            import glob
            report_files = glob.glob("price_update_report_*.json")
            if not report_files:
                return None
            
            # Get most recent file
            latest_file = max(report_files)
            
            with open(latest_file, 'r') as f:
                return json.load(f)
                
        except Exception as e:
            print(f"⚠️ Could not load latest report: {e}")
            return None
    
    def display_latest_report(self, report: Optional[Dict]) -> None:
        """Display latest update report"""
        print("📄 LATEST UPDATE REPORT")
        print("=" * 50)
        
        if not report:
            print("No recent update reports found")
            return
        
        timestamp = report.get('timestamp', '')
        try:
            report_time = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
            time_str = report_time.strftime('%Y-%m-%d %H:%M:%S')
        except:
            time_str = timestamp
        
        print(f"Report Time: {time_str}")
        
        stats = report.get('statistics', {})
        print(f"Items Processed: {stats.get('total_items', 0)}")
        print(f"Updated: {stats.get('updated_items', 0)}")
        print(f"Unchanged: {stats.get('unchanged_items', 0)}")
        print(f"Errors: {stats.get('error_items', 0)}")
        print(f"Out of Stock: {stats.get('out_of_stock_items', 0)}")
        print(f"Price Increases: {stats.get('price_increases', 0)}")
        print(f"Price Decreases: {stats.get('price_decreases', 0)}")
        
        total_change = stats.get('total_price_change', 0)
        print(f"Total Price Change: ${total_change:+.2f}")
        print()
    
    def run_dashboard(self) -> None:
        """Run the complete monitoring dashboard"""
        print("🚀 PRICE MONITORING DASHBOARD")
        print(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 60)
        print()
        
        # Get all data
        stats = self.get_system_overview()
        changes = self.get_recent_price_changes()
        attention = self.get_items_needing_attention()
        latest_report = self.get_latest_report()
        
        # Display sections
        self.display_system_overview(stats)
        self.display_recent_changes(changes)
        self.display_attention_items(attention)
        self.display_latest_report(latest_report)
        
        print("=" * 60)
        print("💡 Commands:")
        print("   • Run test: python test_price_updater.py")
        print("   • View logs: tail -f price_update.log")
        print("   • Setup cron: python setup_daily_price_cron.py")

def main():
    """Main dashboard function"""
    dashboard = PriceMonitoringDashboard()
    dashboard.run_dashboard()

if __name__ == "__main__":
    main() 