#!/usr/bin/env python3
"""
Database Diagnostic Script
Check admin approval workflow data issues
"""

import os
import sys
from datetime import datetime, timedelta
from typing import Dict, List
from supabase import create_client, Client
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class AdminDataDiagnostic:
    def __init__(self):
        # Supabase configuration
        self.supabase_url = "https://ackcgrnizuhauccnbiml.supabase.co"
        self.supabase_key = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImFja2Nncm5penVoYXVjY25iaW1sIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTEyMjc4MzEsImV4cCI6MjA2NjgwMzgzMX0.SXpIMuNBgUhcEQUHzpEB1zZAdF-UTGvmY81EFUtsAwc"
        
        self.supabase: Client = create_client(self.supabase_url, self.supabase_key)
        
    def check_pending_books(self) -> Dict:
        """Check pending_books table for approval workflow"""
        logger.info("🔍 Checking pending_books table...")
        
        try:
            # Get all pending books
            response = self.supabase.table('pending_books').select('*').execute()
            
            if response.data:
                books = response.data
                
                # Analyze status distribution
                status_counts = {}
                for book in books:
                    status = book.get('status', 'unknown')
                    status_counts[status] = status_counts.get(status, 0) + 1
                
                # Check recent submissions
                now = datetime.now()
                recent_cutoff = now - timedelta(days=7)
                
                recent_books = []
                for book in books:
                    if book.get('submitted_at'):
                        submitted_date = datetime.fromisoformat(book['submitted_at'].replace('Z', '+00:00'))
                        if submitted_date >= recent_cutoff:
                            recent_books.append(book)
                
                return {
                    'total_count': len(books),
                    'status_distribution': status_counts,
                    'recent_count': len(recent_books),
                    'sample_books': books[:5],  # First 5 for inspection
                    'recent_books': recent_books[:5]  # Recent 5 for inspection
                }
            else:
                return {
                    'total_count': 0,
                    'status_distribution': {},
                    'recent_count': 0,
                    'sample_books': [],
                    'recent_books': []
                }
                
        except Exception as e:
            logger.error(f"❌ Error checking pending_books: {e}")
            return {'error': str(e)}
    
    def check_books_accessories(self) -> Dict:
        """Check books_accessories table for live items"""
        logger.info("🔍 Checking books_accessories table...")
        
        try:
            # Get all items
            response = self.supabase.table('books_accessories').select('*').execute()
            
            if response.data:
                items = response.data
                
                # Analyze categories
                category_counts = {}
                for item in items:
                    category = item.get('category', 'unknown')
                    category_counts[category] = category_counts.get(category, 0) + 1
                
                # Check recent additions
                now = datetime.now()
                recent_cutoff = now - timedelta(days=7)
                
                recent_items = []
                for item in items:
                    if item.get('timestamp') or item.get('created_at'):
                        date_field = item.get('timestamp') or item.get('created_at')
                        try:
                            created_date = datetime.fromisoformat(date_field.replace('Z', '+00:00'))
                            if created_date >= recent_cutoff:
                                recent_items.append(item)
                        except:
                            continue
                
                return {
                    'total_count': len(items),
                    'category_distribution': category_counts,
                    'recent_count': len(recent_items),
                    'sample_items': items[:5],  # First 5 for inspection
                    'recent_items': recent_items[:5]  # Recent 5 for inspection
                }
            else:
                return {
                    'total_count': 0,
                    'category_distribution': {},
                    'recent_count': 0,
                    'sample_items': [],
                    'recent_items': []
                }
                
        except Exception as e:
            logger.error(f"❌ Error checking books_accessories: {e}")
            return {'error': str(e)}
    
    def check_workflow_disconnect(self, pending_data: Dict, live_data: Dict) -> Dict:
        """Check for items that bypassed the approval workflow"""
        logger.info("🔍 Checking for workflow bypass...")
        
        analysis = {
            'bypass_suspected': False,
            'potential_bypass_items': [],
            'workflow_integrity': 'unknown'
        }
        
        if 'error' in pending_data or 'error' in live_data:
            analysis['workflow_integrity'] = 'cannot_analyze_due_to_errors'
            return analysis
        
        # If there are many live items but few/no pending items, suggests bypass
        live_count = live_data.get('total_count', 0)
        pending_count = pending_data.get('total_count', 0)
        pending_status = pending_data.get('status_distribution', {})
        truly_pending = pending_status.get('pending', 0)
        
        if live_count > 10 and truly_pending == 0:
            analysis['bypass_suspected'] = True
            analysis['workflow_integrity'] = 'likely_bypassed'
            analysis['potential_bypass_items'] = live_data.get('sample_items', [])
        elif live_count > 0 and pending_count == 0:
            analysis['bypass_suspected'] = True
            analysis['workflow_integrity'] = 'completely_bypassed'
        else:
            analysis['workflow_integrity'] = 'appears_normal'
        
        return analysis
    
    def generate_repair_recommendations(self, pending_data: Dict, live_data: Dict, workflow_analysis: Dict) -> List[str]:
        """Generate recommendations to fix the workflow"""
        recommendations = []
        
        # If workflow was bypassed
        if workflow_analysis.get('bypass_suspected'):
            recommendations.append("🔧 REPAIR NEEDED: Items were added directly to books_accessories, bypassing approval workflow")
            recommendations.append("📋 OPTION 1: Move unapproved items from books_accessories to pending_books for proper approval")
            recommendations.append("📋 OPTION 2: Retroactively mark existing items as 'approved' in pending_books to maintain audit trail")
            recommendations.append("🚫 PREVENTION: Ensure all new items go through pending_books → approval → books_accessories workflow")
        
        # If no pending items
        pending_count = pending_data.get('status_distribution', {}).get('pending', 0)
        if pending_count == 0:
            recommendations.append("📚 NO PENDING ITEMS: Consider running book scraping script to populate approval queue")
            recommendations.append("⏰ WEEKLY WORKFLOW: Ensure Sunday approval emails are being sent with new items")
        
        # If many old approved items not moved to live
        approved_count = pending_data.get('status_distribution', {}).get('approved', 0)
        if approved_count > 0:
            recommendations.append(f"✅ APPROVED ITEMS: {approved_count} approved items should be moved to books_accessories table")
        
        return recommendations
    
    def run_full_diagnostic(self) -> Dict:
        """Run complete diagnostic and generate report"""
        logger.info("🚀 Starting admin data diagnostic...")
        
        # Check both tables
        pending_data = self.check_pending_books()
        live_data = self.check_books_accessories()
        
        # Analyze workflow integrity
        workflow_analysis = self.check_workflow_disconnect(pending_data, live_data)
        
        # Generate repair recommendations
        recommendations = self.generate_repair_recommendations(pending_data, live_data, workflow_analysis)
        
        # Compile full report
        report = {
            'timestamp': datetime.now().isoformat(),
            'pending_books_analysis': pending_data,
            'books_accessories_analysis': live_data,
            'workflow_integrity': workflow_analysis,
            'repair_recommendations': recommendations,
            'summary': {
                'pending_items': pending_data.get('status_distribution', {}).get('pending', 0),
                'live_items': live_data.get('total_count', 0),
                'workflow_status': workflow_analysis.get('workflow_integrity', 'unknown'),
                'requires_repair': workflow_analysis.get('bypass_suspected', False)
            }
        }
        
        return report
    
    def print_diagnostic_report(self, report: Dict):
        """Print formatted diagnostic report"""
        print("\n" + "="*80)
        print("📊 MYBOOKSHELF ADMIN DATA DIAGNOSTIC REPORT")
        print("="*80)
        
        summary = report.get('summary', {})
        print(f"\n📋 SUMMARY:")
        print(f"   • Pending items for approval: {summary.get('pending_items', 0)}")
        print(f"   • Live items on website: {summary.get('live_items', 0)}")
        print(f"   • Workflow status: {summary.get('workflow_status', 'unknown')}")
        print(f"   • Requires repair: {'YES' if summary.get('requires_repair') else 'NO'}")
        
        # Pending books details
        pending = report.get('pending_books_analysis', {})
        if 'error' not in pending:
            print(f"\n📚 PENDING_BOOKS TABLE:")
            print(f"   • Total records: {pending.get('total_count', 0)}")
            status_dist = pending.get('status_distribution', {})
            for status, count in status_dist.items():
                print(f"   • {status}: {count}")
            print(f"   • Recent submissions (7 days): {pending.get('recent_count', 0)}")
        
        # Live items details
        live = report.get('books_accessories_analysis', {})
        if 'error' not in live:
            print(f"\n🌐 BOOKS_ACCESSORIES TABLE (Live Website):")
            print(f"   • Total records: {live.get('total_count', 0)}")
            category_dist = live.get('category_distribution', {})
            for category, count in category_dist.items():
                print(f"   • {category}: {count}")
            print(f"   • Recent additions (7 days): {live.get('recent_count', 0)}")
        
        # Workflow analysis
        workflow = report.get('workflow_integrity', {})
        print(f"\n🔍 WORKFLOW ANALYSIS:")
        print(f"   • Integrity: {workflow.get('workflow_integrity', 'unknown')}")
        print(f"   • Bypass suspected: {'YES' if workflow.get('bypass_suspected') else 'NO'}")
        
        # Recommendations
        recommendations = report.get('repair_recommendations', [])
        if recommendations:
            print(f"\n🔧 REPAIR RECOMMENDATIONS:")
            for i, rec in enumerate(recommendations, 1):
                print(f"   {i}. {rec}")
        
        print("\n" + "="*80)

def main():
    """Run the diagnostic"""
    try:
        diagnostic = AdminDataDiagnostic()
        report = diagnostic.run_full_diagnostic()
        diagnostic.print_diagnostic_report(report)
        
        # Save report to file
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f'admin_data_diagnostic_{timestamp}.json'
        
        import json
        with open(filename, 'w') as f:
            json.dump(report, f, indent=2, default=str)
        
        print(f"\n💾 Full report saved to: {filename}")
        
    except Exception as e:
        logger.error(f"❌ Diagnostic failed: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main()) 