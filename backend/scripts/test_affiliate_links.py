#!/usr/bin/env python3
"""
Affiliate Link Testing Script
MyBookshelf Affiliate System - Testing Infrastructure

Purpose: Validate all Amazon affiliate links to ensure they're working and generating revenue
Priority: HIGH - Broken affiliate links = zero revenue
T-Shirt Size: S (3-5 days)

Tests:
1. HTTP status code validation (200/301/302 acceptable)
2. Affiliate tag preservation (mybookshelf-20)
3. Amazon domain verification
4. Response time monitoring
5. Error detection and reporting

Usage:
    python test_affiliate_links.py              # Test all links
    python test_affiliate_links.py --verbose    # Detailed output
    python test_affiliate_links.py --report     # Generate report file
"""

import os
import sys
import requests
import time
import json
from datetime import datetime
from urllib.parse import urlparse, parse_qs
from dataclasses import dataclass, field
from typing import List, Dict, Optional

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from supabase import create_client, Client
    SUPABASE_AVAILABLE = True
except ImportError:
    print("⚠️  Supabase not installed. Install with: pip install supabase")
    SUPABASE_AVAILABLE = False

@dataclass
class LinkTestResult:
    """Test result for a single affiliate link"""
    id: int
    title: str
    original_url: str
    status_code: int
    final_url: str
    has_affiliate_tag: bool
    affiliate_tag: str
    response_time_ms: int
    is_amazon_domain: bool
    error_message: Optional[str] = None
    warnings: List[str] = field(default_factory=list)

class AffiliateLinkTester:
    """Test all affiliate links for functionality and revenue tracking"""
    
    def __init__(self, verbose: bool = False):
        self.verbose = verbose
        self.supabase: Optional[Client] = None
        self.expected_affiliate_tag = "mybookshelf-20"
        self.test_results: List[LinkTestResult] = []
        
        # Request session with proper headers
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1'
        })
        
        self._setup_supabase()
    
    def _setup_supabase(self):
        """Initialize Supabase connection"""
        if not SUPABASE_AVAILABLE:
            return
            
        try:
            # Try to load from environment variables
            supabase_url = os.getenv('SUPABASE_URL') or os.getenv('NEXT_PUBLIC_SUPABASE_URL')
            supabase_key = os.getenv('SUPABASE_SERVICE_ROLE_KEY') or os.getenv('NEXT_PUBLIC_SUPABASE_ANON_KEY')
            
            if not supabase_url or not supabase_key:
                print("⚠️  Supabase credentials not found in environment variables")
                print("   Set SUPABASE_URL and SUPABASE_SERVICE_ROLE_KEY")
                return
                
            self.supabase = create_client(supabase_url, supabase_key)
            if self.verbose:
                print("✅ Connected to Supabase")
                
        except Exception as e:
            print(f"❌ Failed to connect to Supabase: {e}")
    
    def get_mock_data(self) -> List[Dict]:
        """Fallback mock data when Supabase is unavailable"""
        return [
            {
                'id': 17,
                'title': 'The Five Dysfunctions of a Team',
                'affiliate_link': 'https://amazon.com/dp/EXAMPLE123?tag=mybookshelf-20'
            },
            {
                'id': 18,
                'title': 'The Advantage',
                'affiliate_link': 'https://amazon.com/dp/EXAMPLE124?tag=mybookshelf-20'
            },
            {
                'id': 19,
                'title': 'Atomic Habits',
                'affiliate_link': 'https://amazon.com/dp/EXAMPLE125?tag=mybookshelf-20'
            },
            {
                'id': 20,
                'title': 'Leadership Journal - Daily Planner',
                'affiliate_link': 'https://amazon.com/dp/EXAMPLE456?tag=mybookshelf-20'
            }
        ]
    
    def fetch_affiliate_links(self) -> List[Dict]:
        """Fetch all affiliate links from database"""
        if not self.supabase:
            print("🔄 Using mock data (Supabase not available)")
            return self.get_mock_data()
        
        try:
            response = self.supabase.table('books_accessories').select('id,title,affiliate_link').execute()
            
            if response.data:
                if self.verbose:
                    print(f"✅ Fetched {len(response.data)} affiliate links from database")
                return response.data
            else:
                print("⚠️  No affiliate links found in database, using mock data")
                return self.get_mock_data()
                
        except Exception as e:
            print(f"❌ Error fetching from database: {e}")
            print("🔄 Using mock data as fallback")
            return self.get_mock_data()
    
    def test_single_link(self, item: Dict) -> LinkTestResult:
        """Test a single affiliate link comprehensively"""
        start_time = time.time()
        
        result = LinkTestResult(
            id=item['id'],
            title=item['title'],
            original_url=item['affiliate_link'],
            status_code=0,
            final_url="",
            has_affiliate_tag=False,
            affiliate_tag="",
            response_time_ms=0,
            is_amazon_domain=False,
            warnings=[]
        )
        
        try:
            if self.verbose:
                print(f"  🔍 Testing: {item['title']}")
            
            # Make request with redirect following
            response = self.session.get(
                item['affiliate_link'], 
                allow_redirects=True, 
                timeout=10
            )
            
            # Calculate response time
            response_time = (time.time() - start_time) * 1000
            result.response_time_ms = int(response_time)
            result.status_code = response.status_code
            result.final_url = response.url
            
            # Parse final URL for analysis
            parsed_url = urlparse(result.final_url)
            result.is_amazon_domain = 'amazon.' in parsed_url.netloc.lower()
            
            # Check for affiliate tag in final URL
            query_params = parse_qs(parsed_url.query)
            if 'tag' in query_params:
                result.affiliate_tag = query_params['tag'][0]
                result.has_affiliate_tag = result.affiliate_tag == self.expected_affiliate_tag
            
            # Validate response
            if response.status_code not in [200, 301, 302]:
                result.warnings.append(f"Unexpected status code: {response.status_code}")
            
            if not result.is_amazon_domain:
                result.warnings.append("Final URL is not on Amazon domain")
            
            if not result.has_affiliate_tag:
                if result.affiliate_tag:
                    result.warnings.append(f"Wrong affiliate tag: {result.affiliate_tag} (expected: {self.expected_affiliate_tag})")
                else:
                    result.warnings.append("No affiliate tag found - revenue tracking will fail")
            
            if result.response_time_ms > 5000:
                result.warnings.append(f"Slow response: {result.response_time_ms}ms (>5s)")
            
            # Check for Amazon error pages
            if 'Sorry, we just need to make sure you' in response.text:
                result.warnings.append("Amazon CAPTCHA/bot detection triggered")
            elif 'Page Not Found' in response.text or 'does not exist' in response.text:
                result.warnings.append("Product page not found")
            
        except requests.exceptions.Timeout:
            result.error_message = "Request timeout (>10s)"
        except requests.exceptions.ConnectionError:
            result.error_message = "Connection failed"
        except requests.exceptions.RequestException as e:
            result.error_message = f"Request error: {str(e)}"
        except Exception as e:
            result.error_message = f"Unexpected error: {str(e)}"
        
        return result
    
    def run_tests(self) -> Dict:
        """Run tests on all affiliate links"""
        print("🚀 Starting Affiliate Link Testing")
        print("=" * 50)
        
        # Fetch links
        affiliate_links = self.fetch_affiliate_links()
        print(f"📊 Testing {len(affiliate_links)} affiliate links")
        print()
        
        # Test each link
        for item in affiliate_links:
            result = self.test_single_link(item)
            self.test_results.append(result)
            
            # Show immediate feedback
            status_icon = "✅" if not result.error_message and not result.warnings else "⚠️" if result.warnings else "❌"
            print(f"{status_icon} {result.title[:40]:<40} | {result.status_code:>3} | {result.response_time_ms:>4}ms")
        
        return self.generate_summary()
    
    def generate_summary(self) -> Dict:
        """Generate comprehensive test summary"""
        total_tests = len(self.test_results)
        passed_tests = sum(1 for r in self.test_results if not r.error_message and not r.warnings)
        warning_tests = sum(1 for r in self.test_results if r.warnings and not r.error_message)
        failed_tests = sum(1 for r in self.test_results if r.error_message)
        
        # Revenue tracking analysis
        working_affiliate_tags = sum(1 for r in self.test_results if r.has_affiliate_tag)
        avg_response_time = sum(r.response_time_ms for r in self.test_results) / total_tests if total_tests > 0 else 0
        
        summary = {
            'timestamp': datetime.now().isoformat(),
            'total_links': total_tests,
            'passed': passed_tests,
            'warnings': warning_tests,
            'failed': failed_tests,
            'success_rate': f"{(passed_tests/total_tests)*100:.1f}%" if total_tests > 0 else "0%",
            'revenue_tracking_rate': f"{(working_affiliate_tags/total_tests)*100:.1f}%" if total_tests > 0 else "0%",
            'avg_response_time_ms': int(avg_response_time),
            'results': [self._result_to_dict(r) for r in self.test_results]
        }
        
        return summary
    
    def _result_to_dict(self, result: LinkTestResult) -> Dict:
        """Convert result to dictionary for JSON serialization"""
        return {
            'id': result.id,
            'title': result.title,
            'status_code': result.status_code,
            'response_time_ms': result.response_time_ms,
            'has_affiliate_tag': result.has_affiliate_tag,
            'is_amazon_domain': result.is_amazon_domain,
            'error_message': result.error_message,
            'warnings': result.warnings,
            'final_url': result.final_url[:100] + '...' if len(result.final_url) > 100 else result.final_url
        }
    
    def print_detailed_report(self, summary: Dict):
        """Print comprehensive test report"""
        print("\n" + "=" * 60)
        print("📊 AFFILIATE LINK TEST REPORT")
        print("=" * 60)
        
        print(f"🕐 Test Time: {summary['timestamp']}")
        print(f"📈 Success Rate: {summary['success_rate']}")
        print(f"💰 Revenue Tracking: {summary['revenue_tracking_rate']}")
        print(f"⏱️  Average Response: {summary['avg_response_time_ms']}ms")
        print()
        
        # Summary by status
        print("📊 Results Summary:")
        print(f"   ✅ Passed:   {summary['passed']:>2}")
        print(f"   ⚠️  Warnings: {summary['warnings']:>2}")
        print(f"   ❌ Failed:   {summary['failed']:>2}")
        print(f"   📋 Total:    {summary['total_links']:>2}")
        print()
        
        # Detailed results
        if summary['warnings'] > 0 or summary['failed'] > 0:
            print("🔍 Issues Found:")
            for result_dict in summary['results']:
                if result_dict['error_message'] or result_dict['warnings']:
                    print(f"\n📖 {result_dict['title']}")
                    if result_dict['error_message']:
                        print(f"   ❌ Error: {result_dict['error_message']}")
                    for warning in result_dict['warnings']:
                        print(f"   ⚠️  Warning: {warning}")
        
        # Revenue impact analysis
        print("\n💰 Revenue Impact Analysis:")
        working_links = sum(1 for r in summary['results'] if not r['error_message'])
        broken_links = summary['failed']
        
        if broken_links > 0:
            print(f"   ❌ {broken_links} broken links = 0% revenue potential")
        
        links_without_tracking = sum(1 for r in summary['results'] if not r['has_affiliate_tag'])
        if links_without_tracking > 0:
            print(f"   ⚠️  {links_without_tracking} links without tracking = lost commission")
        
        if working_links == summary['total_links']:
            print("   ✅ All links functional - revenue tracking optimal")
    
    def save_report(self, summary: Dict, filename: Optional[str] = None):
        """Save detailed report to file"""
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"affiliate_link_test_report_{timestamp}.json"
        
        with open(filename, 'w') as f:
            json.dump(summary, f, indent=2)
        
        print(f"💾 Report saved: {filename}")

def main():
    """Main entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Test MyBookshelf affiliate links")
    parser.add_argument('--verbose', '-v', action='store_true', help='Verbose output')
    parser.add_argument('--report', '-r', action='store_true', help='Save detailed report')
    parser.add_argument('--output', '-o', type=str, help='Output filename for report')
    
    args = parser.parse_args()
    
    # Run tests
    tester = AffiliateLinkTester(verbose=args.verbose)
    summary = tester.run_tests()
    
    # Print results
    tester.print_detailed_report(summary)
    
    # Save report if requested
    if args.report:
        tester.save_report(summary, args.output)
    
    # Exit with error code if tests failed
    if summary['failed'] > 0:
        print(f"\n❌ {summary['failed']} tests failed")
        return 1
    elif summary['warnings'] > 0:
        print(f"\n⚠️  {summary['warnings']} tests have warnings")
        return 2
    else:
        print("\n✅ All tests passed!")
        return 0

if __name__ == "__main__":
    exit(main()) 