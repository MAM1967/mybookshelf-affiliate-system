#!/usr/bin/env python3
"""
Weekly Health Report Generator
MyBookshelf Affiliate System - Monitoring

Purpose: Generate comprehensive weekly health and performance reports
Priority: MEDIUM - Provides insights for system optimization
T-Shirt Size: XS (1-2 days)

Features:
1. Performance trend analysis
2. Affiliate link health summary
3. Database integrity trends
4. Uptime statistics
5. Business impact metrics

Usage:
    python generate_weekly_report.py
    python generate_weekly_report.py --days 14  # Custom period
"""

import os
import json
import glob
from datetime import datetime, timedelta
from dataclasses import dataclass
from typing import List, Dict, Optional
import argparse

@dataclass
class WeeklyMetrics:
    """Weekly health metrics"""
    total_tests: int
    success_rate: float
    avg_response_time: float
    affiliate_link_uptime: float
    critical_issues: int
    warnings: int
    performance_trend: str  # "improving", "stable", "degrading"

class WeeklyReportGenerator:
    """Generate comprehensive weekly health reports"""
    
    def __init__(self, days: int = 7):
        self.days = days
        self.end_date = datetime.now()
        self.start_date = self.end_date - timedelta(days=days)
        
        # Report data
        self.deployment_reports = []
        self.affiliate_reports = []
        self.test_suite_reports = []
        
        self.load_historical_reports()
    
    def load_historical_reports(self):
        """Load all historical reports from the last N days"""
        print(f"📊 Loading reports from {self.start_date.strftime('%Y-%m-%d')} to {self.end_date.strftime('%Y-%m-%d')}")
        
        # Load deployment test reports
        deployment_files = glob.glob("deployment_test_report_*.json")
        for file in deployment_files:
            try:
                file_date = self.extract_date_from_filename(file)
                if self.start_date <= file_date <= self.end_date:
                    with open(file, 'r') as f:
                        report = json.load(f)
                        report['file_date'] = file_date.isoformat()
                        self.deployment_reports.append(report)
            except Exception as e:
                print(f"⚠️  Could not load {file}: {e}")
        
        # Load affiliate link test reports
        affiliate_files = glob.glob("affiliate_link_test_report_*.json")
        for file in affiliate_files:
            try:
                file_date = self.extract_date_from_filename(file)
                if self.start_date <= file_date <= self.end_date:
                    with open(file, 'r') as f:
                        report = json.load(f)
                        report['file_date'] = file_date.isoformat()
                        self.affiliate_reports.append(report)
            except Exception as e:
                print(f"⚠️  Could not load {file}: {e}")
        
        # Load test suite reports
        suite_files = glob.glob("test_suite_report_*.json")
        for file in suite_files:
            try:
                file_date = self.extract_date_from_filename(file)
                if self.start_date <= file_date <= self.end_date:
                    with open(file, 'r') as f:
                        report = json.load(f)
                        report['file_date'] = file_date.isoformat()
                        self.test_suite_reports.append(report)
            except Exception as e:
                print(f"⚠️  Could not load {file}: {e}")
        
        print(f"✅ Loaded {len(self.deployment_reports)} deployment reports")
        print(f"✅ Loaded {len(self.affiliate_reports)} affiliate reports")
        print(f"✅ Loaded {len(self.test_suite_reports)} test suite reports")
    
    def extract_date_from_filename(self, filename: str) -> datetime:
        """Extract date from report filename"""
        # Expected format: report_type_YYYYMMDD_HHMMSS.json
        parts = filename.split('_')
        for part in parts:
            if len(part) == 8 and part.isdigit():
                return datetime.strptime(part, '%Y%m%d')
        
        # Fallback to file modification time
        return datetime.fromtimestamp(os.path.getmtime(filename))
    
    def analyze_deployment_health(self) -> Dict:
        """Analyze deployment health trends"""
        if not self.deployment_reports:
            return {
                'status': 'NO_DATA',
                'message': 'No deployment test data available',
                'metrics': {}
            }
        
        # Calculate metrics
        total_tests = len(self.deployment_reports)
        passed_tests = sum(1 for r in self.deployment_reports if r['overall_status'] == 'PASSED')
        success_rate = (passed_tests / total_tests) * 100
        
        # Response time analysis
        response_times = [r['avg_response_time_ms'] for r in self.deployment_reports if r['avg_response_time_ms'] > 0]
        avg_response_time = sum(response_times) / len(response_times) if response_times else 0
        
        # Performance trend (compare first half vs second half)
        mid_point = len(response_times) // 2
        if len(response_times) >= 4:
            first_half_avg = sum(response_times[:mid_point]) / mid_point
            second_half_avg = sum(response_times[mid_point:]) / (len(response_times) - mid_point)
            
            if second_half_avg < first_half_avg * 0.9:
                trend = "improving"
            elif second_half_avg > first_half_avg * 1.1:
                trend = "degrading"
            else:
                trend = "stable"
        else:
            trend = "insufficient_data"
        
        return {
            'status': 'HEALTHY' if success_rate >= 95 else 'WARNING' if success_rate >= 85 else 'CRITICAL',
            'metrics': {
                'total_tests': total_tests,
                'success_rate': round(success_rate, 1),
                'avg_response_time_ms': round(avg_response_time, 1),
                'performance_trend': trend,
                'fastest_response': min(response_times) if response_times else 0,
                'slowest_response': max(response_times) if response_times else 0
            }
        }
    
    def analyze_affiliate_link_health(self) -> Dict:
        """Analyze affiliate link health trends"""
        if not self.affiliate_reports:
            return {
                'status': 'NO_DATA',
                'message': 'No affiliate link test data available',
                'metrics': {}
            }
        
        # Calculate revenue tracking health
        total_tests = len(self.affiliate_reports)
        revenue_tracking_rates = []
        
        for report in self.affiliate_reports:
            # Extract revenue tracking rate from report
            if 'revenue_tracking_rate' in report:
                rate = float(report['revenue_tracking_rate'].replace('%', ''))
                revenue_tracking_rates.append(rate)
        
        if revenue_tracking_rates:
            avg_revenue_tracking = sum(revenue_tracking_rates) / len(revenue_tracking_rates)
            min_revenue_tracking = min(revenue_tracking_rates)
        else:
            avg_revenue_tracking = 0
            min_revenue_tracking = 0
        
        return {
            'status': 'HEALTHY' if min_revenue_tracking >= 100 else 'WARNING' if min_revenue_tracking >= 95 else 'CRITICAL',
            'metrics': {
                'total_tests': total_tests,
                'avg_revenue_tracking_rate': round(avg_revenue_tracking, 1),
                'min_revenue_tracking_rate': round(min_revenue_tracking, 1),
                'tests_with_issues': sum(1 for r in self.affiliate_reports if r.get('failed', 0) > 0 or r.get('warnings', 0) > 0)
            }
        }
    
    def analyze_overall_system_health(self) -> Dict:
        """Analyze overall system health"""
        deployment_analysis = self.analyze_deployment_health()
        affiliate_analysis = self.analyze_affiliate_link_health()
        
        # Determine overall status
        statuses = [deployment_analysis['status'], affiliate_analysis['status']]
        if 'CRITICAL' in statuses:
            overall_status = 'CRITICAL'
        elif 'WARNING' in statuses:
            overall_status = 'WARNING'  
        elif 'NO_DATA' in statuses:
            overall_status = 'NO_DATA'
        else:
            overall_status = 'HEALTHY'
        
        return {
            'overall_status': overall_status,
            'deployment_health': deployment_analysis,
            'affiliate_link_health': affiliate_analysis,
            'period': {
                'start_date': self.start_date.isoformat(),
                'end_date': self.end_date.isoformat(),
                'days': self.days
            }
        }
    
    def generate_recommendations(self, analysis: Dict) -> List[str]:
        """Generate actionable recommendations based on analysis"""
        recommendations = []
        
        # Deployment recommendations
        deployment = analysis['deployment_health']
        if deployment['status'] == 'CRITICAL':
            recommendations.append("🚨 URGENT: Fix critical deployment issues immediately")
            recommendations.append("• Check error logs and recent deployments")
            recommendations.append("• Verify DNS and SSL configuration")
        elif deployment['status'] == 'WARNING':
            recommendations.append("⚠️  Monitor deployment health closely")
            recommendations.append("• Investigate intermittent failures")
        
        if deployment.get('metrics', {}).get('performance_trend') == 'degrading':
            recommendations.append("📉 Performance is degrading")
            recommendations.append("• Optimize frontend assets and caching")
            recommendations.append("• Consider CDN improvements")
        
        # Affiliate link recommendations
        affiliate = analysis['affiliate_link_health']
        if affiliate['status'] == 'CRITICAL':
            recommendations.append("💰 URGENT: Revenue tracking is broken")
            recommendations.append("• Check affiliate tag configuration")
            recommendations.append("• Verify Amazon affiliate account status")
        elif affiliate['status'] == 'WARNING':
            recommendations.append("💼 Review affiliate link configuration")
            recommendations.append("• Test affiliate links manually")
        
        # General recommendations
        if analysis['overall_status'] == 'HEALTHY':
            recommendations.append("✅ System is healthy - maintain current practices")
            recommendations.append("• Continue regular monitoring")
            recommendations.append("• Plan for capacity growth")
        
        return recommendations
    
    def generate_report(self) -> Dict:
        """Generate comprehensive weekly report"""
        print("🚀 Generating Weekly Health Report")
        print("=" * 50)
        
        analysis = self.analyze_overall_system_health()
        recommendations = self.generate_recommendations(analysis)
        
        # Create comprehensive report
        report = {
            'report_metadata': {
                'generated_at': datetime.now().isoformat(),
                'report_type': 'weekly_health_report',
                'period_days': self.days,
                'data_sources': {
                    'deployment_reports': len(self.deployment_reports),
                    'affiliate_reports': len(self.affiliate_reports),
                    'test_suite_reports': len(self.test_suite_reports)
                }
            },
            'executive_summary': {
                'overall_status': analysis['overall_status'],
                'key_metrics': {
                    'deployment_success_rate': analysis['deployment_health'].get('metrics', {}).get('success_rate', 0),
                    'avg_response_time_ms': analysis['deployment_health'].get('metrics', {}).get('avg_response_time_ms', 0),
                    'revenue_tracking_rate': analysis['affiliate_link_health'].get('metrics', {}).get('avg_revenue_tracking_rate', 0)
                },
                'critical_issues': sum(1 for s in [analysis['deployment_health']['status'], analysis['affiliate_link_health']['status']] if s == 'CRITICAL'),
                'warnings': sum(1 for s in [analysis['deployment_health']['status'], analysis['affiliate_link_health']['status']] if s == 'WARNING')
            },
            'detailed_analysis': analysis,
            'recommendations': recommendations,
            'raw_data_summary': {
                'deployment_tests': len(self.deployment_reports),
                'affiliate_tests': len(self.affiliate_reports),
                'total_monitoring_points': len(self.deployment_reports) + len(self.affiliate_reports)
            }
        }
        
        return report
    
    def print_report_summary(self, report: Dict):
        """Print a human-readable report summary"""
        print("\n" + "=" * 60)
        print("📊 WEEKLY HEALTH REPORT SUMMARY")
        print("=" * 60)
        
        summary = report['executive_summary']
        status_icon = "✅" if summary['overall_status'] == 'HEALTHY' else "⚠️" if summary['overall_status'] == 'WARNING' else "❌"
        
        print(f"{status_icon} Overall Status: {summary['overall_status']}")
        print(f"📅 Period: {self.days} days ({self.start_date.strftime('%Y-%m-%d')} to {self.end_date.strftime('%Y-%m-%d')})")
        print()
        
        # Key metrics
        print("📈 Key Metrics:")
        metrics = summary['key_metrics']
        print(f"   🌐 Deployment Success: {metrics['deployment_success_rate']}%")
        print(f"   ⏱️  Avg Response Time: {metrics['avg_response_time_ms']}ms")
        print(f"   💰 Revenue Tracking: {metrics['revenue_tracking_rate']}%")
        print()
        
        # Issues summary
        if summary['critical_issues'] > 0 or summary['warnings'] > 0:
            print("🔍 Issues Summary:")
            if summary['critical_issues'] > 0:
                print(f"   ❌ Critical Issues: {summary['critical_issues']}")
            if summary['warnings'] > 0:
                print(f"   ⚠️  Warnings: {summary['warnings']}")
            print()
        
        # Recommendations
        if report['recommendations']:
            print("💡 Recommendations:")
            for rec in report['recommendations']:
                print(f"   {rec}")
            print()
        
        # Data coverage
        print("📊 Data Coverage:")
        raw_data = report['raw_data_summary']
        print(f"   🧪 Deployment Tests: {raw_data['deployment_tests']}")
        print(f"   🔗 Affiliate Tests: {raw_data['affiliate_tests']}")
        print(f"   📋 Total Data Points: {raw_data['total_monitoring_points']}")

def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(description="Generate MyBookshelf weekly health report")
    parser.add_argument('--days', type=int, default=7, help='Number of days to analyze (default: 7)')
    
    args = parser.parse_args()
    
    # Generate report
    generator = WeeklyReportGenerator(days=args.days)
    report = generator.generate_report()
    
    # Print summary
    generator.print_report_summary(report)
    
    # Save report
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"weekly_health_report_{timestamp}.json"
    with open(filename, 'w') as f:
        json.dump(report, f, indent=2)
    
    print(f"\n💾 Full report saved: {filename}")
    
    # Exit with status based on overall health
    if report['executive_summary']['overall_status'] == 'CRITICAL':
        print("\n❌ Critical issues detected")
        return 1
    elif report['executive_summary']['overall_status'] == 'WARNING':
        print("\n⚠️  Warnings detected")
        return 2
    else:
        print("\n✅ System is healthy!")
        return 0

if __name__ == "__main__":
    exit(main()) 