#!/usr/bin/env python3
"""
Automated Test Runner
MyBookshelf Affiliate System - Testing Infrastructure

Purpose: Run all automated tests and provide comprehensive reporting
Priority: HIGH - Ensures system reliability for revenue generation
T-Shirt Size: S (3-5 days)

Features:
1. Run affiliate link tests
2. Run database integrity tests  
3. Unified reporting
4. Exit codes for CI/CD
5. Performance monitoring

Usage:
    python run_all_tests.py                    # Run all tests
    python run_all_tests.py --fast             # Skip slow tests
    python run_all_tests.py --report           # Generate comprehensive report
    python run_all_tests.py --verbose          # Detailed output
"""

import os
import sys
import json
import subprocess
import time
from datetime import datetime
from typing import Dict, List, Optional
from dataclasses import dataclass

@dataclass
class TestSuiteResult:
    """Result from running a test suite"""
    name: str
    exit_code: int
    duration_seconds: float
    output: str
    report_file: Optional[str] = None

class TestRunner:
    """Run all automated tests and generate unified reports"""
    
    def __init__(self, verbose: bool = False, fast_mode: bool = False):
        self.verbose = verbose
        self.fast_mode = fast_mode
        self.start_time = datetime.now()
        self.results: List[TestSuiteResult] = []
        
        # Test suite configurations
        self.test_suites = [
            {
                'name': 'Database Integrity',
                'script': 'test_database_integrity.py',
                'args': ['--report'] if not fast_mode else [],
                'required': True,
                'timeout': 30
            },
            {
                'name': 'Affiliate Links',
                'script': 'test_affiliate_links.py', 
                'args': ['--report'] if not fast_mode else [],
                'required': True,
                'timeout': 60
            },
            {
                'name': 'Admin LinkedIn Integration',
                'script': 'test_admin_linkedin_integration.py',
                'args': [],
                'required': False,
                'timeout': 45
            },
            {
                'name': 'Email Service Integration',
                'script': 'test_email_simple.py',
                'args': [],
                'required': False,
                'timeout': 120
            }
        ]
        
        if verbose:
            for suite in self.test_suites:
                suite['args'].append('--verbose')
    
    def run_test_suite(self, suite_config: Dict) -> TestSuiteResult:
        """Run a single test suite"""
        print(f"🧪 Running {suite_config['name']} Tests...")
        start_time = time.time()
        
        # Build command
        cmd = ['python3', suite_config['script']] + suite_config['args']
        
        try:
            # Run the test
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=suite_config['timeout'],
                cwd=os.path.dirname(os.path.abspath(__file__))
            )
            
            duration = time.time() - start_time
            
            # Show immediate feedback
            if result.returncode == 0:
                print(f"   ✅ {suite_config['name']} - PASSED ({duration:.1f}s)")
            elif result.returncode == 2:
                print(f"   ⚠️  {suite_config['name']} - WARNINGS ({duration:.1f}s)")
            else:
                print(f"   ❌ {suite_config['name']} - FAILED ({duration:.1f}s)")
            
            # Find report file if generated
            report_file = None
            if '--report' in suite_config['args']:
                script_name = suite_config['script'].replace('.py', '')
                timestamp_pattern = datetime.now().strftime("%Y%m%d")
                
                for file in os.listdir('.'):
                    if file.startswith(f"{script_name}_report_") and timestamp_pattern in file:
                        report_file = file
                        break
            
            return TestSuiteResult(
                name=suite_config['name'],
                exit_code=result.returncode,
                duration_seconds=duration,
                output=result.stdout + result.stderr,
                report_file=report_file
            )
            
        except subprocess.TimeoutExpired:
            duration = time.time() - start_time
            print(f"   ⏰ {suite_config['name']} - TIMEOUT ({duration:.1f}s)")
            
            return TestSuiteResult(
                name=suite_config['name'],
                exit_code=124,  # Timeout exit code
                duration_seconds=duration,
                output=f"Test timed out after {suite_config['timeout']} seconds"
            )
            
        except Exception as e:
            duration = time.time() - start_time
            print(f"   ❌ {suite_config['name']} - ERROR ({duration:.1f}s)")
            
            return TestSuiteResult(
                name=suite_config['name'],
                exit_code=1,
                duration_seconds=duration,
                output=f"Error running test: {str(e)}"
            )
    
    def run_all_tests(self) -> Dict:
        """Run all test suites"""
        print("🚀 MyBookshelf Automated Test Suite")
        print("=" * 50)
        print(f"📅 Started: {self.start_time.strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"⚡ Mode: {'Fast' if self.fast_mode else 'Complete'}")
        print()
        
        # Run each test suite
        for suite_config in self.test_suites:
            result = self.run_test_suite(suite_config)
            self.results.append(result)
        
        # Generate summary
        return self.generate_summary()
    
    def generate_summary(self) -> Dict:
        """Generate comprehensive test summary"""
        end_time = datetime.now()
        total_duration = (end_time - self.start_time).total_seconds()
        
        # Categorize results
        passed = sum(1 for r in self.results if r.exit_code == 0)
        warnings = sum(1 for r in self.results if r.exit_code == 2)
        failed = sum(1 for r in self.results if r.exit_code not in [0, 2])
        
        # Determine overall status
        if failed > 0:
            overall_status = "FAILED"
            status_icon = "❌"
        elif warnings > 0:
            overall_status = "WARNINGS"
            status_icon = "⚠️"
        else:
            overall_status = "PASSED"
            status_icon = "✅"
        
        summary = {
            'timestamp': end_time.isoformat(),
            'overall_status': overall_status,
            'total_duration_seconds': total_duration,
            'test_suites': {
                'total': len(self.results),
                'passed': passed,
                'warnings': warnings,
                'failed': failed
            },
            'results': [
                {
                    'name': r.name,
                    'status': 'PASSED' if r.exit_code == 0 else 'WARNINGS' if r.exit_code == 2 else 'FAILED',
                    'exit_code': r.exit_code,
                    'duration_seconds': r.duration_seconds,
                    'report_file': r.report_file
                }
                for r in self.results
            ],
            'environment': {
                'fast_mode': self.fast_mode,
                'verbose': self.verbose,
                'python_version': sys.version.split()[0],
                'working_directory': os.getcwd()
            }
        }
        
        return summary
    
    def print_detailed_report(self, summary: Dict):
        """Print comprehensive test report"""
        print("\n" + "=" * 60)
        print("📊 MYBOOKSHELF TEST SUITE REPORT")
        print("=" * 60)
        
        status_icon = "✅" if summary['overall_status'] == 'PASSED' else "⚠️" if summary['overall_status'] == 'WARNINGS' else "❌"
        print(f"{status_icon} Overall Status: {summary['overall_status']}")
        print(f"⏱️  Total Duration: {summary['total_duration_seconds']:.1f}s")
        print(f"🧪 Test Suites: {summary['test_suites']['total']}")
        print()
        
        # Results breakdown
        print("📊 Results Summary:")
        print(f"   ✅ Passed:   {summary['test_suites']['passed']:>2}")
        print(f"   ⚠️  Warnings: {summary['test_suites']['warnings']:>2}")
        print(f"   ❌ Failed:   {summary['test_suites']['failed']:>2}")
        print()
        
        # Individual test results
        print("🔍 Test Suite Details:")
        for result in summary['results']:
            status_icon = "✅" if result['status'] == 'PASSED' else "⚠️" if result['status'] == 'WARNINGS' else "❌"
            print(f"   {status_icon} {result['name']:<20} | {result['status']:<8} | {result['duration_seconds']:>5.1f}s")
            if result['report_file']:
                print(f"      📄 Report: {result['report_file']}")
        print()
        
        # Environment info
        print("🔧 Environment:")
        print(f"   Python: {summary['environment']['python_version']}")
        print(f"   Mode: {'Fast' if summary['environment']['fast_mode'] else 'Complete'}")
        print(f"   Verbose: {summary['environment']['verbose']}")
        
        # Business impact assessment
        print("\n💼 Business Impact Assessment:")
        if summary['overall_status'] == 'PASSED':
            print("   ✅ All systems operational - Revenue tracking optimal")
        elif summary['overall_status'] == 'WARNINGS':
            print("   ⚠️  Minor issues detected - Revenue may be impacted")
            print("   📋 Review warnings and fix non-critical issues")
        else:
            print("   ❌ Critical issues detected - Revenue generation at risk")
            print("   🚨 Immediate action required before deployment")
        
        # Next steps
        if summary['test_suites']['failed'] > 0:
            print("\n🔧 Immediate Actions Required:")
            for result in summary['results']:
                if result['status'] == 'FAILED':
                    print(f"   • Fix {result['name']} test failures")
            print("   • Re-run tests after fixes")
            print("   • Do not deploy until all tests pass")
        elif summary['test_suites']['warnings'] > 0:
            print("\n📋 Recommended Actions:")
            print("   • Review warning details in individual reports")
            print("   • Fix warnings before next release")
            print("   • Monitor system performance")
    
    def save_unified_report(self, summary: Dict, filename: Optional[str] = None):
        """Save unified test report"""
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"test_suite_report_{timestamp}.json"
        
        # Enhance summary with individual report data
        enhanced_summary = summary.copy()
        enhanced_summary['individual_reports'] = {}
        
        for result in self.results:
            if result.report_file and os.path.exists(result.report_file):
                try:
                    with open(result.report_file, 'r') as f:
                        report_data = json.load(f)
                    enhanced_summary['individual_reports'][result.name] = report_data
                except Exception as e:
                    print(f"⚠️  Could not load {result.report_file}: {e}")
        
        with open(filename, 'w') as f:
            json.dump(enhanced_summary, f, indent=2)
        
        print(f"💾 Unified report saved: {filename}")
        return filename

def main():
    """Main entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Run MyBookshelf automated test suite")
    parser.add_argument('--verbose', '-v', action='store_true', help='Verbose output')
    parser.add_argument('--fast', '-f', action='store_true', help='Skip slow tests')
    parser.add_argument('--report', '-r', action='store_true', help='Save unified report')
    parser.add_argument('--output', '-o', type=str, help='Output filename for unified report')
    
    args = parser.parse_args()
    
    # Run all tests
    runner = TestRunner(verbose=args.verbose, fast_mode=args.fast)
    summary = runner.run_all_tests()
    
    # Print results
    runner.print_detailed_report(summary)
    
    # Save unified report if requested
    if args.report:
        runner.save_unified_report(summary, args.output)
    
    # Exit with appropriate code
    if summary['overall_status'] == 'FAILED':
        print(f"\n❌ Test suite failed")
        return 1
    elif summary['overall_status'] == 'WARNINGS':
        print(f"\n⚠️  Test suite completed with warnings")
        return 2
    else:
        print(f"\n✅ All tests passed!")
        return 0

if __name__ == "__main__":
    exit(main()) 