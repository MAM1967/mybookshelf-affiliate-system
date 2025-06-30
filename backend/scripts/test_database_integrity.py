#!/usr/bin/env python3
"""
Database Integrity Testing Script
MyBookshelf Affiliate System - Testing Infrastructure

Purpose: Validate database structure, data quality, and business rules
Priority: HIGH - Ensures data consistency for revenue generation
T-Shirt Size: S (3-5 days)

Tests:
1. Table structure validation
2. Required field validation
3. Data type validation
4. Business rule validation (prices > 0, valid URLs, etc.)
5. Duplicate detection
6. Referential integrity

Usage:
    python test_database_integrity.py              # Test all aspects
    python test_database_integrity.py --verbose    # Detailed output
    python test_database_integrity.py --report     # Generate report file
"""

import os
import sys
import json
import re
from datetime import datetime
from urllib.parse import urlparse
from dataclasses import dataclass, field
from typing import List, Dict, Optional, Any
from decimal import Decimal

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from supabase import create_client, Client
    SUPABASE_AVAILABLE = True
except ImportError:
    print("⚠️  Supabase not installed. Install with: pip install supabase")
    SUPABASE_AVAILABLE = False

@dataclass
class IntegrityTestResult:
    """Test result for database integrity check"""
    test_name: str
    category: str
    status: str  # "PASS", "WARN", "FAIL"
    message: str
    details: Optional[Dict[str, Any]] = None
    affected_records: List[int] = field(default_factory=list)

class DatabaseIntegrityTester:
    """Test database integrity and data quality"""
    
    def __init__(self, verbose: bool = False):
        self.verbose = verbose
        self.supabase: Optional[Client] = None
        self.test_results: List[IntegrityTestResult] = []
        self.expected_affiliate_tag = "mybookshelf-20"
        
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
        """Fallback mock data for testing"""
        return [
            {
                'id': 17,
                'title': 'The Five Dysfunctions of a Team',
                'author': 'Patrick Lencioni',
                'price': 19.99,
                'affiliate_link': 'https://amazon.com/dp/EXAMPLE123?tag=mybookshelf-20',
                'image_url': 'https://covers.openlibrary.org/b/isbn/0787960756-L.jpg',
                'category': 'Books',
                'timestamp': '2024-01-01T12:00:00Z'
            },
            {
                'id': 18,
                'title': 'The Advantage',
                'author': 'Patrick Lencioni',
                'price': 19.99,
                'affiliate_link': 'https://amazon.com/dp/EXAMPLE124?tag=mybookshelf-20',
                'image_url': 'https://covers.openlibrary.org/b/isbn/0470941529-L.jpg',
                'category': 'Books',
                'timestamp': '2024-01-02T12:00:00Z'
            },
            {
                'id': 19,
                'title': 'Atomic Habits',
                'author': 'James Clear',
                'price': 19.99,
                'affiliate_link': 'https://amazon.com/dp/EXAMPLE125?tag=mybookshelf-20',
                'image_url': 'https://m.media-amazon.com/images/I/513Y5o-DYtL.jpg',
                'category': 'Books',
                'timestamp': '2024-01-03T12:00:00Z'
            },
            {
                'id': 20,
                'title': 'Leadership Journal - Daily Planner',
                'author': 'Business Essentials',
                'price': 19.99,
                'affiliate_link': 'https://amazon.com/dp/EXAMPLE456?tag=mybookshelf-20',
                'image_url': 'https://images.unsplash.com/photo-1434030216411-0b793f4b4173?w=300&h=400&fit=crop',
                'category': 'Accessories',
                'timestamp': '2024-01-04T12:00:00Z'
            }
        ]
    
    def fetch_all_data(self) -> List[Dict]:
        """Fetch all data from books_accessories table"""
        if not self.supabase:
            if self.verbose:
                print("🔄 Using mock data (Supabase not available)")
            return self.get_mock_data()
        
        try:
            response = self.supabase.table('books_accessories').select('*').execute()
            
            if response.data:
                if self.verbose:
                    print(f"✅ Fetched {len(response.data)} records from database")
                return response.data
            else:
                print("⚠️  No data found in database, using mock data")
                return self.get_mock_data()
                
        except Exception as e:
            print(f"❌ Error fetching from database: {e}")
            print("🔄 Using mock data as fallback")
            return self.get_mock_data()
    
    def test_table_structure(self, data: List[Dict]):
        """Test that all required fields are present"""
        if not data:
            self.test_results.append(IntegrityTestResult(
                test_name="Table Structure",
                category="Schema",
                status="FAIL",
                message="No data found in table"
            ))
            return
        
        required_fields = ['id', 'title', 'author', 'price', 'affiliate_link', 'image_url', 'category', 'timestamp']
        sample_record = data[0]
        
        missing_fields = [field for field in required_fields if field not in sample_record]
        
        if missing_fields:
            self.test_results.append(IntegrityTestResult(
                test_name="Required Fields",
                category="Schema",
                status="FAIL",
                message=f"Missing required fields: {', '.join(missing_fields)}",
                details={"missing_fields": missing_fields, "sample_record": sample_record}
            ))
        else:
            self.test_results.append(IntegrityTestResult(
                test_name="Required Fields",
                category="Schema",
                status="PASS",
                message="All required fields present"
            ))
    
    def test_data_types(self, data: List[Dict]):
        """Test data types for all records"""
        invalid_records = []
        
        for record in data:
            record_errors = []
            record_id = record.get('id', 'Unknown')
            
            # Test ID is integer
            if not isinstance(record.get('id'), int):
                record_errors.append("ID must be integer")
            
            # Test title is non-empty string
            title = record.get('title', '')
            if not isinstance(title, str) or not title.strip():
                record_errors.append("Title must be non-empty string")
            
            # Test author is non-empty string
            author = record.get('author', '')
            if not isinstance(author, str) or not author.strip():
                record_errors.append("Author must be non-empty string")
            
            # Test price is positive number
            price = record.get('price')
            try:
                price_val = float(price) if price is not None else 0
                if price_val <= 0:
                    record_errors.append("Price must be positive")
            except (ValueError, TypeError):
                record_errors.append("Price must be valid number")
            
            # Test affiliate_link is valid URL
            affiliate_link = record.get('affiliate_link', '')
            if not isinstance(affiliate_link, str) or not affiliate_link.startswith(('http://', 'https://')):
                record_errors.append("Affiliate link must be valid URL")
            
            # Test category is valid
            category = record.get('category', '')
            valid_categories = ['Books', 'Accessories']
            if category not in valid_categories:
                record_errors.append(f"Category must be one of: {', '.join(valid_categories)}")
            
            if record_errors:
                invalid_records.append({
                    'id': record_id,
                    'errors': record_errors
                })
        
        if invalid_records:
            self.test_results.append(IntegrityTestResult(
                test_name="Data Types",
                category="Data Quality",
                status="FAIL",
                message=f"{len(invalid_records)} records have data type issues",
                details={"invalid_records": invalid_records},
                affected_records=[r['id'] for r in invalid_records if isinstance(r['id'], int)]
            ))
        else:
            self.test_results.append(IntegrityTestResult(
                test_name="Data Types",
                category="Data Quality",
                status="PASS",
                message="All records have valid data types"
            ))
    
    def test_affiliate_links(self, data: List[Dict]):
        """Test affiliate link integrity"""
        invalid_links = []
        
        for record in data:
            record_id = record.get('id', 'Unknown')
            affiliate_link = record.get('affiliate_link', '')
            link_errors = []
            
            # Test contains affiliate tag
            if self.expected_affiliate_tag not in affiliate_link:
                link_errors.append(f"Missing affiliate tag: {self.expected_affiliate_tag}")
            
            # Test is Amazon domain
            try:
                parsed = urlparse(affiliate_link)
                if 'amazon.' not in parsed.netloc.lower():
                    link_errors.append("Not an Amazon domain")
            except Exception:
                link_errors.append("Invalid URL format")
            
            # Test for placeholder/example URLs
            if any(placeholder in affiliate_link.lower() for placeholder in ['example', 'placeholder', 'test']):
                link_errors.append("Contains placeholder/example URL")
            
            if link_errors:
                invalid_links.append({
                    'id': record_id,
                    'title': record.get('title', 'Unknown'),
                    'link': affiliate_link,
                    'errors': link_errors
                })
        
        if invalid_links:
            status = "WARN" if any("placeholder" in str(link['errors']) for link in invalid_links) else "FAIL"
            self.test_results.append(IntegrityTestResult(
                test_name="Affiliate Links",
                category="Business Rules",
                status=status,
                message=f"{len(invalid_links)} records have affiliate link issues",
                details={"invalid_links": invalid_links},
                affected_records=[r['id'] for r in invalid_links if isinstance(r['id'], int)]
            ))
        else:
            self.test_results.append(IntegrityTestResult(
                test_name="Affiliate Links",
                category="Business Rules",
                status="PASS",
                message="All affiliate links are valid"
            ))
    
    def test_duplicates(self, data: List[Dict]):
        """Test for duplicate records"""
        title_count = {}
        isbn_count = {}
        link_count = {}
        
        for record in data:
            title = record.get('title', '').strip().lower()
            affiliate_link = record.get('affiliate_link', '')
            
            # Count titles
            if title:
                if title not in title_count:
                    title_count[title] = []
                title_count[title].append(record.get('id'))
            
            # Count affiliate links
            if affiliate_link:
                if affiliate_link not in link_count:
                    link_count[affiliate_link] = []
                link_count[affiliate_link].append(record.get('id'))
        
        # Find duplicates
        duplicate_titles = {title: ids for title, ids in title_count.items() if len(ids) > 1}
        duplicate_links = {link: ids for link, ids in link_count.items() if len(ids) > 1}
        
        if duplicate_titles or duplicate_links:
            self.test_results.append(IntegrityTestResult(
                test_name="Duplicates",
                category="Data Quality",
                status="WARN",
                message=f"Found {len(duplicate_titles)} duplicate titles, {len(duplicate_links)} duplicate links",
                details={
                    "duplicate_titles": duplicate_titles,
                    "duplicate_links": duplicate_links
                }
            ))
        else:
            self.test_results.append(IntegrityTestResult(
                test_name="Duplicates",
                category="Data Quality",
                status="PASS",
                message="No duplicate records found"
            ))
    
    def test_business_rules(self, data: List[Dict]):
        """Test business-specific rules"""
        violations = []
        
        for record in data:
            record_id = record.get('id', 'Unknown')
            title = record.get('title', '')
            price = record.get('price', 0)
            category = record.get('category', '')
            
            rule_violations = []
            
            # Business Rule: Prices should be reasonable ($5-$100 for books, $10-$200 for accessories)
            try:
                price_val = float(price)
                if category == 'Books' and not (5 <= price_val <= 100):
                    rule_violations.append(f"Book price ${price_val:.2f} outside reasonable range ($5-$100)")
                elif category == 'Accessories' and not (10 <= price_val <= 200):
                    rule_violations.append(f"Accessory price ${price_val:.2f} outside reasonable range ($10-$200)")
            except (ValueError, TypeError):
                pass  # Already caught in data type test
            
            # Business Rule: Title should not contain certain words
            forbidden_words = ['test', 'example', 'placeholder', 'lorem', 'ipsum']
            if any(word in title.lower() for word in forbidden_words):
                rule_violations.append("Title contains placeholder/test words")
            
            if rule_violations:
                violations.append({
                    'id': record_id,
                    'title': title,
                    'violations': rule_violations
                })
        
        if violations:
            self.test_results.append(IntegrityTestResult(
                test_name="Business Rules",
                category="Business Rules",
                status="WARN",
                message=f"{len(violations)} records violate business rules",
                details={"violations": violations},
                affected_records=[v['id'] for v in violations if isinstance(v['id'], int)]
            ))
        else:
            self.test_results.append(IntegrityTestResult(
                test_name="Business Rules",
                category="Business Rules",
                status="PASS",
                message="All records comply with business rules"
            ))
    
    def run_tests(self) -> Dict:
        """Run all database integrity tests"""
        print("🚀 Starting Database Integrity Testing")
        print("=" * 50)
        
        # Fetch data
        data = self.fetch_all_data()
        print(f"📊 Testing {len(data)} records")
        print()
        
        # Run all tests
        self.test_table_structure(data)
        self.test_data_types(data)
        self.test_affiliate_links(data)
        self.test_duplicates(data)
        self.test_business_rules(data)
        
        return self.generate_summary()
    
    def generate_summary(self) -> Dict:
        """Generate comprehensive test summary"""
        total_tests = len(self.test_results)
        passed_tests = sum(1 for r in self.test_results if r.status == "PASS")
        warning_tests = sum(1 for r in self.test_results if r.status == "WARN")
        failed_tests = sum(1 for r in self.test_results if r.status == "FAIL")
        
        summary = {
            'timestamp': datetime.now().isoformat(),
            'total_tests': total_tests,
            'passed': passed_tests,
            'warnings': warning_tests,
            'failed': failed_tests,
            'success_rate': f"{(passed_tests/total_tests)*100:.1f}%" if total_tests > 0 else "0%",
            'results': [self._result_to_dict(r) for r in self.test_results]
        }
        
        return summary
    
    def _result_to_dict(self, result: IntegrityTestResult) -> Dict:
        """Convert result to dictionary for JSON serialization"""
        return {
            'test_name': result.test_name,
            'category': result.category,
            'status': result.status,
            'message': result.message,
            'details': result.details,
            'affected_records': result.affected_records
        }
    
    def print_detailed_report(self, summary: Dict):
        """Print comprehensive test report"""
        print("\n" + "=" * 60)
        print("📊 DATABASE INTEGRITY TEST REPORT")
        print("=" * 60)
        
        print(f"🕐 Test Time: {summary['timestamp']}")
        print(f"📈 Success Rate: {summary['success_rate']}")
        print()
        
        # Summary by status
        print("📊 Results Summary:")
        print(f"   ✅ Passed:   {summary['passed']:>2}")
        print(f"   ⚠️  Warnings: {summary['warnings']:>2}")
        print(f"   ❌ Failed:   {summary['failed']:>2}")
        print(f"   📋 Total:    {summary['total_tests']:>2}")
        print()
        
        # Results by category
        categories = {}
        for result in summary['results']:
            cat = result['category']
            if cat not in categories:
                categories[cat] = {'pass': 0, 'warn': 0, 'fail': 0}
            categories[cat][result['status'].lower()] += 1
        
        print("📊 Results by Category:")
        for category, counts in categories.items():
            total_cat = sum(counts.values())
            print(f"   {category}:")
            print(f"      ✅ {counts['pass']}/{total_cat} passed")
            if counts['warn'] > 0:
                print(f"      ⚠️  {counts['warn']}/{total_cat} warnings")
            if counts['fail'] > 0:
                print(f"      ❌ {counts['fail']}/{total_cat} failed")
        print()
        
        # Detailed issues
        issues = [r for r in summary['results'] if r['status'] in ['WARN', 'FAIL']]
        if issues:
            print("🔍 Issues Found:")
            for result in issues:
                status_icon = "⚠️" if result['status'] == 'WARN' else "❌"
                print(f"\n{status_icon} {result['test_name']} ({result['category']})")
                print(f"   {result['message']}")
                if result.get('affected_records'):
                    print(f"   Affected records: {result['affected_records']}")
        
        # Data quality assessment
        print("\n💼 Data Quality Assessment:")
        if summary['failed'] == 0:
            if summary['warnings'] == 0:
                print("   ✅ Excellent - All tests passed with no issues")
            else:
                print(f"   📈 Good - Minor issues found ({summary['warnings']} warnings)")
        else:
            print(f"   ❌ Poor - Critical issues found ({summary['failed']} failures)")
    
    def save_report(self, summary: Dict, filename: Optional[str] = None):
        """Save detailed report to file"""
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"database_integrity_report_{timestamp}.json"
        
        with open(filename, 'w') as f:
            json.dump(summary, f, indent=2)
        
        print(f"💾 Report saved: {filename}")

def main():
    """Main entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Test MyBookshelf database integrity")
    parser.add_argument('--verbose', '-v', action='store_true', help='Verbose output')
    parser.add_argument('--report', '-r', action='store_true', help='Save detailed report')
    parser.add_argument('--output', '-o', type=str, help='Output filename for report')
    
    args = parser.parse_args()
    
    # Run tests
    tester = DatabaseIntegrityTester(verbose=args.verbose)
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