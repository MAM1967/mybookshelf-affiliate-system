#!/usr/bin/env python3
"""
Deployment Testing Script
MyBookshelf Affiliate System - CI/CD Pipeline

Purpose: Test live deployments to ensure they're working correctly
Priority: HIGH - Validates deployments before user traffic
T-Shirt Size: XS (1-2 days)

Tests:
1. HTTP status code validation
2. Critical page loading
3. Affiliate link functionality
4. Performance benchmarks

Usage:
    DEPLOYMENT_URL="https://mybookshelf.shop" python test_deployment.py
    python test_deployment.py --url https://staging.mybookshelf.shop
    python test_deployment.py --verbose --performance
"""

import os
import sys
import requests
import time
import json
from datetime import datetime
from urllib.parse import urljoin
from dataclasses import dataclass
from typing import List, Dict, Optional
import argparse

@dataclass
class DeploymentTestResult:
    """Test result for deployment validation"""
    test_name: str
    status: str  # "PASS", "WARN", "FAIL"
    response_time_ms: int
    message: str
    details: Optional[Dict] = None

class DeploymentTester:
    """Test live deployment functionality"""
    
    def __init__(self, base_url: str, verbose: bool = False, performance_test: bool = False):
        self.base_url = base_url.rstrip('/')
        self.verbose = verbose
        self.performance_test = performance_test
        self.test_results: List[DeploymentTestResult] = []
        
        # Configure session
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'MyBookshelf-DeploymentTester/1.0',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8'
        })
    
    def test_homepage_availability(self) -> DeploymentTestResult:
        """Test that homepage is available and responding"""
        url = self.base_url
        start_time = time.time()
        
        try:
            if self.verbose:
                print(f"  🔍 Testing homepage: {url}")
            
            response = self.session.get(url, timeout=10)
            response_time = int((time.time() - start_time) * 1000)
            
            if response.status_code == 200:
                status = "PASS"
                message = f"Available ({response.status_code})"
            elif response.status_code in [301, 302]:
                status = "PASS"
                message = f"Redirecting ({response.status_code})"
            else:
                status = "FAIL"
                message = f"HTTP {response.status_code}"
            
            return DeploymentTestResult(
                test_name="Homepage Availability",
                status=status,
                response_time_ms=response_time,
                message=message,
                details={'url': url, 'status_code': response.status_code}
            )
            
        except requests.exceptions.Timeout:
            return DeploymentTestResult(
                test_name="Homepage Availability",
                status="FAIL",
                response_time_ms=10000,
                message="Request timeout (>10s)",
                details={'url': url}
            )
        except Exception as e:
            return DeploymentTestResult(
                test_name="Homepage Availability",
                status="FAIL",
                response_time_ms=0,
                message=f"Error: {str(e)}",
                details={'url': url}
            )
    
    def test_content_integrity(self) -> DeploymentTestResult:
        """Test that the main page contains expected content"""
        url = self.base_url
        start_time = time.time()
        
        try:
            if self.verbose:
                print(f"  🔍 Testing content integrity: {url}")
            
            response = self.session.get(url, timeout=10)
            response_time = int((time.time() - start_time) * 1000)
            content = response.text.lower()
            
            # Check for key content elements
            required_elements = ['mybookshelf', 'christian', 'leadership', 'books']
            missing_elements = [elem for elem in required_elements if elem not in content]
            
            if response.status_code == 200 and not missing_elements:
                status = "PASS"
                message = "All required content present"
            elif response.status_code == 200:
                status = "WARN"
                message = f"Missing content: {', '.join(missing_elements)}"
            else:
                status = "FAIL"
                message = f"HTTP {response.status_code}"
            
            return DeploymentTestResult(
                test_name="Content Integrity",
                status=status,
                response_time_ms=response_time,
                message=message,
                details={'missing_elements': missing_elements}
            )
            
        except Exception as e:
            return DeploymentTestResult(
                test_name="Content Integrity",
                status="FAIL",
                response_time_ms=0,
                message=f"Error: {str(e)}"
            )
    
    def test_affiliate_links(self) -> DeploymentTestResult:
        """Test that affiliate links are present and correctly formatted"""
        url = self.base_url
        start_time = time.time()
        
        try:
            if self.verbose:
                print(f"  🔍 Testing affiliate links: {url}")
            
            response = self.session.get(url, timeout=10)
            response_time = int((time.time() - start_time) * 1000)
            content = response.text
            
            # Check for affiliate tag
            affiliate_tag = "mybookshelf-20"
            has_affiliate_tag = affiliate_tag in content
            has_amazon_links = "amazon.com" in content.lower()
            
            if has_affiliate_tag and has_amazon_links:
                status = "PASS"
                message = "Affiliate links properly configured"
            elif has_amazon_links and not has_affiliate_tag:
                status = "FAIL"
                message = "Amazon links found but missing affiliate tag"
            elif not has_amazon_links:
                status = "WARN"
                message = "No Amazon links found (may be loading dynamically)"
            else:
                status = "WARN"
                message = "Affiliate tag found but no Amazon links"
            
            return DeploymentTestResult(
                test_name="Affiliate Links",
                status=status,
                response_time_ms=response_time,
                message=message,
                details={'has_affiliate_tag': has_affiliate_tag, 'has_amazon_links': has_amazon_links}
            )
            
        except Exception as e:
            return DeploymentTestResult(
                test_name="Affiliate Links",
                status="FAIL",
                response_time_ms=0,
                message=f"Error: {str(e)}"
            )
    
    def test_performance(self) -> DeploymentTestResult:
        """Test deployment performance"""
        if not self.performance_test:
            return DeploymentTestResult(
                test_name="Performance",
                status="PASS",
                response_time_ms=0,
                message="Skipped (use --performance to enable)"
            )
        
        url = self.base_url
        response_times = []
        
        try:
            if self.verbose:
                print(f"  🔍 Testing performance (3 requests): {url}")
            
            # Make 3 requests to get average response time
            for i in range(3):
                start_time = time.time()
                response = self.session.get(url, timeout=10)
                response_time = int((time.time() - start_time) * 1000)
                response_times.append(response_time)
                
                if self.verbose:
                    print(f"    Request {i+1}: {response_time}ms")
            
            avg_response_time = int(sum(response_times) / len(response_times))
            
            if avg_response_time < 1000:
                status = "PASS"
                message = f"Fast ({avg_response_time}ms avg)"
            elif avg_response_time < 3000:
                status = "PASS"
                message = f"Acceptable ({avg_response_time}ms avg)"
            else:
                status = "WARN"
                message = f"Slow ({avg_response_time}ms avg)"
            
            return DeploymentTestResult(
                test_name="Performance",
                status=status,
                response_time_ms=avg_response_time,
                message=message,
                details={'avg_response_time': avg_response_time, 'all_times': response_times}
            )
            
        except Exception as e:
            return DeploymentTestResult(
                test_name="Performance",
                status="FAIL",
                response_time_ms=0,
                message=f"Error: {str(e)}"
            )
    
    def run_tests(self) -> Dict:
        """Run all deployment tests"""
        print("🚀 MyBookshelf Deployment Testing")
        print("=" * 50)
        print(f"🌐 Target: {self.base_url}")
        print()
        
        # Run all tests
        tests = [
            self.test_homepage_availability,
            self.test_content_integrity,
            self.test_affiliate_links,
            self.test_performance
        ]
        
        for test_func in tests:
            result = test_func()
            self.test_results.append(result)
            
            # Show immediate feedback
            status_icon = "✅" if result.status == "PASS" else "⚠️" if result.status == "WARN" else "❌"
            print(f"{status_icon} {result.test_name:<20} | {result.status:<4} | {result.response_time_ms:>4}ms")
        
        return self.generate_summary()
    
    def generate_summary(self) -> Dict:
        """Generate test summary"""
        total_tests = len(self.test_results)
        passed_tests = sum(1 for r in self.test_results if r.status == "PASS")
        warning_tests = sum(1 for r in self.test_results if r.status == "WARN")
        failed_tests = sum(1 for r in self.test_results if r.status == "FAIL")
        
        # Determine overall status
        if failed_tests > 0:
            overall_status = "FAILED"
        elif warning_tests > 0:
            overall_status = "WARNINGS"
        else:
            overall_status = "PASSED"
        
        valid_times = [r.response_time_ms for r in self.test_results if r.response_time_ms > 0]
        avg_response_time = int(sum(valid_times) / len(valid_times)) if valid_times else 0
        
        summary = {
            'timestamp': datetime.now().isoformat(),
            'deployment_url': self.base_url,
            'overall_status': overall_status,
            'total_tests': total_tests,
            'passed': passed_tests,
            'warnings': warning_tests,
            'failed': failed_tests,
            'avg_response_time_ms': avg_response_time,
            'results': [
                {
                    'test_name': r.test_name,
                    'status': r.status,
                    'response_time_ms': r.response_time_ms,
                    'message': r.message,
                    'details': r.details
                }
                for r in self.test_results
            ]
        }
        
        return summary
    
    def print_detailed_report(self, summary: Dict):
        """Print comprehensive deployment test report"""
        print("\n" + "=" * 60)
        print("📊 DEPLOYMENT TEST REPORT")
        print("=" * 60)
        
        status_icon = "✅" if summary['overall_status'] == 'PASSED' else "⚠️" if summary['overall_status'] == 'WARNINGS' else "❌"
        print(f"{status_icon} Overall Status: {summary['overall_status']}")
        print(f"🌐 Deployment URL: {summary['deployment_url']}")
        print(f"⏱️  Average Response: {summary['avg_response_time_ms']}ms")
        print()
        
        # Results summary
        print("📊 Results Summary:")
        print(f"   ✅ Passed:   {summary['passed']:>2}")
        print(f"   ⚠️  Warnings: {summary['warnings']:>2}")
        print(f"   ❌ Failed:   {summary['failed']:>2}")
        print(f"   📋 Total:    {summary['total_tests']:>2}")
        print()
        
        # Detailed issues
        issues = [r for r in summary['results'] if r['status'] in ['WARN', 'FAIL']]
        if issues:
            print("🔍 Issues Found:")
            for result in issues:
                status_icon = "⚠️" if result['status'] == 'WARN' else "❌"
                print(f"\n{status_icon} {result['test_name']}")
                print(f"   {result['message']}")
        
        # Deployment readiness assessment
        print("\n🚀 Deployment Readiness:")
        if summary['overall_status'] == 'PASSED':
            print("   ✅ Deployment is healthy and ready for traffic")
        elif summary['overall_status'] == 'WARNINGS':
            print("   ⚠️  Deployment has minor issues - monitor closely")
        else:
            print("   ❌ Deployment has critical issues - immediate action required")

def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(description="Test MyBookshelf deployment")
    parser.add_argument('--url', type=str, help='Deployment URL to test')
    parser.add_argument('--verbose', '-v', action='store_true', help='Verbose output')
    parser.add_argument('--performance', '-p', action='store_true', help='Run performance tests')
    
    args = parser.parse_args()
    
    # Get deployment URL
    deployment_url = args.url or os.getenv('DEPLOYMENT_URL') or os.getenv('STAGING_URL') or os.getenv('PRODUCTION_URL')
    
    if not deployment_url:
        print("❌ No deployment URL provided")
        print("Use: --url https://example.com or set DEPLOYMENT_URL environment variable")
        return 1
    
    # Run tests
    tester = DeploymentTester(deployment_url, verbose=args.verbose, performance_test=args.performance)
    summary = tester.run_tests()
    
    # Print results
    tester.print_detailed_report(summary)
    
    # Save report
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"deployment_test_report_{timestamp}.json"
    with open(filename, 'w') as f:
        json.dump(summary, f, indent=2)
    print(f"\n💾 Report saved: {filename}")
    
    # Exit with appropriate code
    if summary['overall_status'] == 'FAILED':
        print(f"\n❌ Deployment tests failed")
        return 1
    elif summary['overall_status'] == 'WARNINGS':
        print(f"\n⚠️  Deployment tests completed with warnings")
        return 2
    else:
        print(f"\n✅ All deployment tests passed!")
        return 0

if __name__ == "__main__":
    exit(main()) 