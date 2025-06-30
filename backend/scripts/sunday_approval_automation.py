#!/usr/bin/env python3
"""
Sunday Approval Automation for MyBookshelf Affiliate System
Manages weekly approval email workflow and scheduling
"""

import os
import sys
import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import logging

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from supabase import create_client, Client
from config import Config
from email_service import ResendEmailService

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('sunday_automation.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class SundayApprovalAutomation:
    """Manages the Sunday approval workflow automation"""
    
    def __init__(self):
        """Initialize Sunday automation"""
        if not Config.SUPABASE_URL or not Config.SUPABASE_ANON_KEY:
            raise ValueError("Missing required Supabase configuration")
        
        self.supabase: Client = create_client(Config.SUPABASE_URL, Config.SUPABASE_ANON_KEY)
        self.email_service = ResendEmailService()
        
        # Configuration
        self.admin_email = os.getenv('ADMIN_EMAIL', 'mcddsl@icloud.com')
        self.approval_deadline_hours = 48  # Admin has 48 hours (Sunday → Tuesday)
        
    def check_sunday_trigger(self) -> bool:
        """Check if today is Sunday and we should trigger approval workflow"""
        today = datetime.now()
        
        # Check if it's Sunday (weekday 6)
        if today.weekday() != 6:  # 0=Monday, 6=Sunday
            logger.info(f"ℹ️ Today is {today.strftime('%A')}, not Sunday. Skipping approval trigger.")
            return False
        
        # Check if we already sent approval email today
        today_date = today.date()
        
        try:
            existing_session = self.supabase.table('approval_sessions').select('id, status').eq(
                'session_date', today_date.isoformat()
            ).execute()
            
            if existing_session.data:
                session = existing_session.data[0]
                logger.info(f"ℹ️ Approval session already exists for today: {session['id']} (status: {session['status']})")
                return False
            
            logger.info("✅ Sunday trigger confirmed - no existing session found")
            return True
            
        except Exception as e:
            logger.error(f"❌ Error checking existing sessions: {e}")
            return False
    
    def get_content_pipeline_status(self) -> Dict:
        """Get status of content pipeline for reporting"""
        try:
            # Get pending books count
            pending_response = self.supabase.table('pending_books').select('id, status, submitted_at').execute()
            books = pending_response.data or []
            
            # Calculate pipeline stats
            now = datetime.now()
            week_ago = now - timedelta(days=7)
            
            stats = {
                'total_books': len(books),
                'pending': len([b for b in books if b['status'] == 'pending']),
                'approved': len([b for b in books if b['status'] == 'approved']),
                'rejected': len([b for b in books if b['status'] == 'rejected']),
                'needs_review': len([b for b in books if b['status'] == 'needs_review']),
                'recent_submissions': len([
                    b for b in books 
                    if datetime.fromisoformat(b['submitted_at'].replace('Z', '+00:00')) > week_ago
                ])
            }
            
            # Get recent approval sessions
            recent_sessions = self.supabase.table('approval_sessions').select(
                'id, session_date, status, books_approved, books_rejected'
            ).gte('session_date', week_ago.date().isoformat()).order('session_date', desc=True).execute()
            
            stats['recent_sessions'] = len(recent_sessions.data or [])
            stats['recent_approved'] = sum(s.get('books_approved', 0) for s in (recent_sessions.data or []))
            
            return stats
            
        except Exception as e:
            logger.error(f"❌ Error getting pipeline status: {e}")
            return {
                'total_books': 0,
                'pending': 0,
                'approved': 0,
                'rejected': 0,
                'needs_review': 0,
                'recent_submissions': 0,
                'recent_sessions': 0,
                'recent_approved': 0
            }
    
    def run_sunday_workflow(self) -> Dict:
        """Run the complete Sunday approval workflow"""
        logger.info("🌅 Starting Sunday Approval Workflow")
        logger.info("=" * 50)
        
        workflow_result = {
            'triggered': False,
            'email_sent': False,
            'session_created': False,
            'pipeline_stats': {},
            'error': None
        }
        
        try:
            # Step 1: Check if we should trigger today
            if not self.check_sunday_trigger():
                workflow_result['triggered'] = False
                return workflow_result
            
            workflow_result['triggered'] = True
            
            # Step 2: Get pipeline status for reporting
            pipeline_stats = self.get_content_pipeline_status()
            workflow_result['pipeline_stats'] = pipeline_stats
            
            logger.info("📊 Content Pipeline Status:")
            logger.info(f"   Total books in system: {pipeline_stats['total_books']}")
            logger.info(f"   Pending approval: {pipeline_stats['pending']}")
            logger.info(f"   Needs review: {pipeline_stats['needs_review']}")
            logger.info(f"   Recent submissions (7 days): {pipeline_stats['recent_submissions']}")
            
            # Step 3: Check if we have content to approve
            if pipeline_stats['pending'] == 0 and pipeline_stats['needs_review'] == 0:
                logger.info("ℹ️ No books pending approval, skipping email workflow")
                workflow_result['email_sent'] = True  # Mark as success since no action needed
                return workflow_result
            
            # Step 4: Send approval email
            logger.info("📧 Sending Sunday approval email...")
            email_success = self.email_service.send_sunday_approval_email()
            
            if email_success:
                workflow_result['email_sent'] = True
                workflow_result['session_created'] = True
                logger.info("✅ Sunday approval email sent successfully")
            else:
                workflow_result['error'] = "Failed to send approval email"
                logger.error("❌ Failed to send Sunday approval email")
                return workflow_result
            
            # Step 5: Log workflow completion
            self.log_workflow_completion(workflow_result)
            
            logger.info("✅ Sunday workflow completed successfully")
            return workflow_result
            
        except Exception as e:
            error_msg = f"Sunday workflow error: {str(e)}"
            workflow_result['error'] = error_msg
            logger.error(f"❌ {error_msg}")
            return workflow_result
    
    def check_approval_reminders(self) -> Dict:
        """Check for pending approvals that need reminders"""
        logger.info("🔔 Checking for approval reminders...")
        
        try:
            # Get pending sessions older than 2 days (Sunday → Tuesday)
            cutoff_date = (datetime.now() - timedelta(days=2)).date()
            
            pending_sessions = self.supabase.table('approval_sessions').select(
                'id, session_date, admin_email, status'
            ).eq('status', 'pending').lte('session_date', cutoff_date.isoformat()).execute()
            
            reminder_results = {
                'sessions_checked': len(pending_sessions.data or []),
                'reminders_sent': 0,
                'errors': []
            }
            
            for session in (pending_sessions.data or []):
                logger.info(f"📧 Sending reminder for session {session['id']} ({session['session_date']})")
                
                success = self.email_service.send_approval_reminder(session['id'])
                if success:
                    reminder_results['reminders_sent'] += 1
                else:
                    reminder_results['errors'].append(f"Failed to send reminder for session {session['id']}")
            
            logger.info(f"✅ Reminder check complete: {reminder_results['reminders_sent']} reminders sent")
            return reminder_results
            
        except Exception as e:
            logger.error(f"❌ Error checking reminders: {e}")
            return {
                'sessions_checked': 0,
                'reminders_sent': 0,
                'errors': [str(e)]
            }
    
    def cleanup_expired_sessions(self) -> Dict:
        """Clean up expired approval sessions"""
        logger.info("🧹 Cleaning up expired sessions...")
        
        try:
            # Find sessions expired for more than 1 day
            cutoff_date = (datetime.now() - timedelta(days=8)).date()  # 7 day expiry + 1 day grace
            
            expired_sessions = self.supabase.table('approval_sessions').select('id, session_date').eq(
                'status', 'pending'
            ).lte('session_date', cutoff_date.isoformat()).execute()
            
            cleanup_results = {
                'sessions_found': len(expired_sessions.data or []),
                'sessions_cleaned': 0,
                'errors': []
            }
            
            for session in (expired_sessions.data or []):
                try:
                    # Update session status to expired
                    self.supabase.table('approval_sessions').update({
                        'status': 'expired'
                    }).eq('id', session['id']).execute()
                    
                    cleanup_results['sessions_cleaned'] += 1
                    logger.info(f"🧹 Marked session {session['id']} as expired ({session['session_date']})")
                    
                except Exception as e:
                    cleanup_results['errors'].append(f"Failed to expire session {session['id']}: {str(e)}")
            
            logger.info(f"✅ Cleanup complete: {cleanup_results['sessions_cleaned']} sessions expired")
            return cleanup_results
            
        except Exception as e:
            logger.error(f"❌ Error during cleanup: {e}")
            return {
                'sessions_found': 0,
                'sessions_cleaned': 0,
                'errors': [str(e)]
            }
    
    def log_workflow_completion(self, workflow_result: Dict):
        """Log workflow completion for monitoring"""
        try:
            log_entry = {
                'workflow_date': datetime.now().date().isoformat(),
                'triggered': workflow_result['triggered'],
                'email_sent': workflow_result['email_sent'],
                'session_created': workflow_result['session_created'],
                'pending_books': workflow_result['pipeline_stats'].get('pending', 0),
                'error_message': workflow_result.get('error'),
                'completed_at': datetime.now().isoformat()
            }
            
            # This would go to a workflow_logs table if we had one
            logger.info(f"📝 Workflow logged: {json.dumps(log_entry, indent=2)}")
            
        except Exception as e:
            logger.error(f"❌ Error logging workflow: {e}")
    
    def get_workflow_status(self) -> Dict:
        """Get current workflow status for monitoring"""
        try:
            # Get recent sessions
            recent_sessions = self.supabase.table('approval_sessions').select(
                'id, session_date, status, started_at, completed_at'
            ).order('session_date', desc=True).limit(5).execute()
            
            # Get pipeline stats
            pipeline_stats = self.get_content_pipeline_status()
            
            # Calculate next Sunday
            today = datetime.now()
            days_until_sunday = (6 - today.weekday()) % 7
            if days_until_sunday == 0 and today.weekday() == 6:
                next_sunday = today.date()
            else:
                next_sunday = (today + timedelta(days=days_until_sunday)).date()
            
            return {
                'current_date': today.date().isoformat(),
                'next_sunday': next_sunday.isoformat(),
                'pipeline_stats': pipeline_stats,
                'recent_sessions': recent_sessions.data or [],
                'system_status': 'operational'
            }
            
        except Exception as e:
            logger.error(f"❌ Error getting workflow status: {e}")
            return {
                'current_date': datetime.now().date().isoformat(),
                'system_status': 'error',
                'error': str(e)
            }

def main():
    """Main execution function"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Sunday Approval Automation')
    parser.add_argument('--run-workflow', action='store_true', help='Run Sunday approval workflow')
    parser.add_argument('--check-reminders', action='store_true', help='Check and send approval reminders')
    parser.add_argument('--cleanup', action='store_true', help='Clean up expired sessions')
    parser.add_argument('--status', action='store_true', help='Show workflow status')
    parser.add_argument('--force', action='store_true', help='Force run workflow regardless of day')
    
    args = parser.parse_args()
    
    automation = SundayApprovalAutomation()
    
    if args.status:
        status = automation.get_workflow_status()
        print("\n📊 SUNDAY APPROVAL WORKFLOW STATUS")
        print("=" * 40)
        print(f"Current Date: {status['current_date']}")
        print(f"Next Sunday: {status['next_sunday']}")
        print(f"System Status: {status['system_status']}")
        
        if status.get('error'):
            print(f"Error: {status['error']}")
        else:
            stats = status['pipeline_stats']
            print(f"\nPipeline Stats:")
            print(f"  Pending Books: {stats['pending']}")
            print(f"  Needs Review: {stats['needs_review']}")
            print(f"  Recent Submissions: {stats['recent_submissions']}")
            
            print(f"\nRecent Sessions: {len(status['recent_sessions'])}")
            for session in status['recent_sessions'][:3]:
                print(f"  {session['session_date']}: {session['status']}")
        
        sys.exit(0)
    
    elif args.run_workflow:
        if args.force:
            # Override Sunday check for testing
            automation.check_sunday_trigger = lambda: True
        
        result = automation.run_sunday_workflow()
        
        print("\n📧 SUNDAY WORKFLOW RESULTS")
        print("=" * 30)
        print(f"Triggered: {'✅' if result['triggered'] else '⏭️'}")
        print(f"Email Sent: {'✅' if result['email_sent'] else '❌'}")
        print(f"Session Created: {'✅' if result['session_created'] else '❌'}")
        
        if result.get('error'):
            print(f"Error: {result['error']}")
            sys.exit(1)
        elif result['triggered']:
            print(f"Pending Books: {result['pipeline_stats'].get('pending', 0)}")
            sys.exit(0)
        else:
            sys.exit(0)
    
    elif args.check_reminders:
        result = automation.check_approval_reminders()
        
        print("\n🔔 REMINDER CHECK RESULTS")
        print("=" * 25)
        print(f"Sessions Checked: {result['sessions_checked']}")
        print(f"Reminders Sent: {result['reminders_sent']}")
        
        if result['errors']:
            print("Errors:")
            for error in result['errors']:
                print(f"  - {error}")
            sys.exit(1)
        else:
            sys.exit(0)
    
    elif args.cleanup:
        result = automation.cleanup_expired_sessions()
        
        print("\n🧹 CLEANUP RESULTS")
        print("=" * 17)
        print(f"Sessions Found: {result['sessions_found']}")
        print(f"Sessions Cleaned: {result['sessions_cleaned']}")
        
        if result['errors']:
            print("Errors:")
            for error in result['errors']:
                print(f"  - {error}")
            sys.exit(1)
        else:
            sys.exit(0)
    
    else:
        print("Usage: python sunday_approval_automation.py [--run-workflow | --check-reminders | --cleanup | --status]")
        print("Use --force with --run-workflow to test regardless of day")
        sys.exit(1)

if __name__ == "__main__":
    main()