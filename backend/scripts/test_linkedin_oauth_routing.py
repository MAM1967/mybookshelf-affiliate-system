#!/usr/bin/env python3
"""
LinkedIn OAuth Routing Test - MyBookshelf Affiliate System
Tests all domain combinations and OAuth callback routing
"""

import requests
import json
import time
from urllib.parse import urlencode, urlparse, parse_qs
from datetime import datetime
from typing import Dict, List, Tuple, Optional

class LinkedInOAuthRoutingTest:
    """Test LinkedIn OAuth routing across all domain configurations"""
    
    def __init__(self):
        """Initialize routing test"""
        
        # Domain configurations to test
        self.domains = [
            'https://mybookshelf.shop',
            'https://www.mybookshelf.shop'
        ]
        
        # Callback paths to test
        self.callback_paths = [
            '/admin/linkedin-callback',
            '/admin/oauth/linkedin',
            '/auth/linkedin/callback'  # Legacy path for redirect testing
        ]
        
        # LinkedIn OAuth configuration
        self.linkedin_config = {
            'client_id': '78wmrhdd99ssbi',
            'response_type': 'code',
            'scope': 'openid profile w_member_social email',
            'state': 'mybookshelf_routing_test'
        }
        
        # Results storage
        self.test_results = []
        
    def test_callback_route_accessibility(self) -> Dict:
        """Test if callback routes are accessible"""
        results = {
            'test_name': 'Callback Route Accessibility',
            'timestamp': datetime.now().isoformat(),
            'domain_tests': {}
        }
        
        print("🧪 Testing Callback Route Accessibility")
        print("=" * 50)
        
        for domain in self.domains:
            domain_results = {'routes': {}}
            print(f"\n🌐 Testing domain: {domain}")
            
            for path in self.callback_paths:
                url = f"{domain}{path}"
                
                try:
                    # Test HEAD request first
                    response = requests.head(url, timeout=10, allow_redirects=False)
                    
                    route_result = {
                        'url': url,
                        'status_code': response.status_code,
                        'headers': dict(response.headers),
                        'accessible': response.status_code in [200, 301, 302, 307, 308]
                    }
                    
                    # Handle redirects
                    if response.status_code in [301, 302, 307, 308]:
                        redirect_location = response.headers.get('location', 'N/A')
                        route_result['redirect_to'] = redirect_location
                        print(f"   📍 {path}: {response.status_code} → {redirect_location}")
                        
                        # Test the redirect target
                        if redirect_location.startswith('http'):
                            try:
                                redirect_response = requests.head(redirect_location, timeout=10)
                                route_result['redirect_final_status'] = redirect_response.status_code
                                print(f"      Final: {redirect_response.status_code}")
                            except Exception as e:
                                route_result['redirect_error'] = str(e)
                                print(f"      Error: {e}")
                    
                    elif response.status_code == 200:
                        print(f"   ✅ {path}: {response.status_code} OK")
                    elif response.status_code == 404:
                        print(f"   ❌ {path}: {response.status_code} NOT FOUND")
                    else:
                        print(f"   ⚠️  {path}: {response.status_code}")
                        
                except Exception as e:
                    route_result = {
                        'url': url,
                        'error': str(e),
                        'accessible': False
                    }
                    print(f"   💥 {path}: ERROR - {e}")
                
                domain_results['routes'][path] = route_result
            
            results['domain_tests'][domain] = domain_results
        
        self.test_results.append(results)
        return results
    
    def test_oauth_url_generation(self) -> Dict:
        """Test OAuth URL generation for all domain combinations"""
        results = {
            'test_name': 'OAuth URL Generation',
            'timestamp': datetime.now().isoformat(),
            'oauth_urls': {}
        }
        
        print("\n🔗 Testing OAuth URL Generation")
        print("=" * 50)
        
        for domain in self.domains:
            for path in self.callback_paths:
                redirect_uri = f"{domain}{path}"
                
                # Generate OAuth URL
                oauth_params = {
                    **self.linkedin_config,
                    'redirect_uri': redirect_uri
                }
                
                oauth_url = f"https://www.linkedin.com/oauth/v2/authorization?{urlencode(oauth_params)}"
                
                url_result = {
                    'redirect_uri': redirect_uri,
                    'oauth_url': oauth_url,
                    'valid': len(oauth_url) < 2048  # URL length check
                }
                
                results['oauth_urls'][f"{domain}{path}"] = url_result
                print(f"   📍 {redirect_uri}")
                print(f"      OAuth: {oauth_url[:100]}...")
                print(f"      Valid: {'✅' if url_result['valid'] else '❌'}")
        
        self.test_results.append(results)
        return results
    
    def test_callback_page_content(self) -> Dict:
        """Test callback page content for correct handling"""
        results = {
            'test_name': 'Callback Page Content',
            'timestamp': datetime.now().isoformat(),
            'content_tests': {}
        }
        
        print("\n📄 Testing Callback Page Content")
        print("=" * 50)
        
        # Test with mock OAuth parameters
        test_params = {
            'code': 'test_authorization_code_12345',
            'state': 'mybookshelf_routing_test'
        }
        
        for domain in self.domains:
            for path in self.callback_paths:
                url = f"{domain}{path}?{urlencode(test_params)}"
                
                try:
                    response = requests.get(url, timeout=10)
                    
                    content_result = {
                        'url': url,
                        'status_code': response.status_code,
                        'content_type': response.headers.get('content-type', 'unknown'),
                        'has_oauth_handling': False,
                        'has_error_handling': False
                    }
                    
                    if response.status_code == 200:
                        content = response.text.lower()
                        
                        # Check for OAuth-related content
                        oauth_indicators = [
                            'authorization', 'linkedin', 'oauth', 'access_token',
                            'code', 'test_authorization_code_12345'
                        ]
                        
                        error_indicators = [
                            'error', 'failed', 'unauthorized', '404', 'not found'
                        ]
                        
                        content_result['has_oauth_handling'] = any(
                            indicator in content for indicator in oauth_indicators
                        )
                        content_result['has_error_handling'] = any(
                            indicator in content for indicator in error_indicators
                        )
                        
                        print(f"   ✅ {path}: Content loaded")
                        print(f"      OAuth handling: {'✅' if content_result['has_oauth_handling'] else '❌'}")
                        print(f"      Error handling: {'✅' if content_result['has_error_handling'] else '❌'}")
                    
                    else:
                        print(f"   ❌ {path}: {response.status_code}")
                        
                except Exception as e:
                    content_result = {
                        'url': url,
                        'error': str(e)
                    }
                    print(f"   💥 {path}: ERROR - {e}")
                
                results['content_tests'][f"{domain}{path}"] = content_result
        
        self.test_results.append(results)
        return results
    
    def generate_working_oauth_urls(self) -> List[Dict]:
        """Generate working OAuth URLs based on test results"""
        working_urls = []
        
        print("\n🚀 Generating Working OAuth URLs")
        print("=" * 50)
        
        # Find routes that returned 200 or successful redirects
        for result in self.test_results:
            if result['test_name'] == 'Callback Route Accessibility':
                for domain, domain_data in result['domain_tests'].items():
                    for path, route_data in domain_data['routes'].items():
                        
                        is_working = (
                            route_data.get('status_code') == 200 or
                            (route_data.get('status_code') in [301, 302, 307, 308] and
                             route_data.get('redirect_final_status') == 200)
                        )
                        
                        if is_working:
                            redirect_uri = f"{domain}{path}"
                            oauth_params = {
                                **self.linkedin_config,
                                'redirect_uri': redirect_uri
                            }
                            oauth_url = f"https://www.linkedin.com/oauth/v2/authorization?{urlencode(oauth_params)}"
                            
                            working_url = {
                                'redirect_uri': redirect_uri,
                                'oauth_url': oauth_url,
                                'status': route_data.get('status_code'),
                                'notes': 'Direct access' if route_data.get('status_code') == 200 else 'Via redirect'
                            }
                            
                            working_urls.append(working_url)
                            print(f"   ✅ {redirect_uri}")
                            print(f"      OAuth: {oauth_url}")
                            print(f"      Status: {working_url['notes']}")
        
        return working_urls
    
    def save_test_report(self, filename: Optional[str] = None) -> str:
        """Save test results to JSON file"""
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"linkedin_oauth_routing_test_{timestamp}.json"
        
        report = {
            'test_summary': {
                'timestamp': datetime.now().isoformat(),
                'domains_tested': self.domains,
                'paths_tested': self.callback_paths,
                'total_tests': len(self.test_results)
            },
            'test_results': self.test_results,
            'working_oauth_urls': self.generate_working_oauth_urls()
        }
        
        with open(filename, 'w') as f:
            json.dump(report, f, indent=2)
        
        print(f"\n💾 Test report saved: {filename}")
        return filename
    
    def run_full_test_suite(self) -> Dict:
        """Run complete LinkedIn OAuth routing test suite"""
        print("🔗 LinkedIn OAuth Routing Test Suite - MyBookshelf")
        print("=" * 60)
        print(f"Timestamp: {datetime.now().isoformat()}")
        print(f"Testing domains: {', '.join(self.domains)}")
        print(f"Testing paths: {', '.join(self.callback_paths)}")
        
        # Run all tests
        accessibility_results = self.test_callback_route_accessibility()
        oauth_results = self.test_oauth_url_generation()
        content_results = self.test_callback_page_content()
        
        # Generate working URLs
        working_urls = self.generate_working_oauth_urls()
        
        # Save report
        report_file = self.save_test_report()
        
        # Summary
        print(f"\n📊 Test Summary")
        print("=" * 30)
        print(f"Total domains tested: {len(self.domains)}")
        print(f"Total paths tested: {len(self.callback_paths)}")
        print(f"Working OAuth URLs found: {len(working_urls)}")
        print(f"Report file: {report_file}")
        
        if working_urls:
            print(f"\n✅ SUCCESS: Found {len(working_urls)} working OAuth configurations!")
            print("You can use any of these redirect URIs in your LinkedIn app:")
            for url_config in working_urls:
                print(f"   • {url_config['redirect_uri']} ({url_config['notes']})")
        else:
            print(f"\n❌ FAILURE: No working OAuth configurations found!")
            print("Check the routing configuration and try redeploying.")
        
        return {
            'success': len(working_urls) > 0,
            'working_urls': working_urls,
            'report_file': report_file
        }

def main():
    """Main test function"""
    tester = LinkedInOAuthRoutingTest()
    results = tester.run_full_test_suite()
    
    # Exit with appropriate code
    exit_code = 0 if results['success'] else 1
    exit(exit_code)

if __name__ == "__main__":
    main() 