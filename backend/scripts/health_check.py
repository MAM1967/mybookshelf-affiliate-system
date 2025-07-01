#!/usr/bin/env python3
"""
MyBookshelf Automation Health Check
Monitors the LinkedIn automation system and sends alerts if needed
"""

import os
import sys
import requests
from datetime import datetime, timedelta

def check_linkedin_automation_health():
    """Check if LinkedIn automation is working properly"""
    
    # Check if log file exists and has recent activity
    log_file = "/var/log/mybookshelf_linkedin.log"
    
    if not os.path.exists(log_file):
        return False, "Log file not found"
    
    # Check last modification time
    mtime = datetime.fromtimestamp(os.path.getmtime(log_file))
    if mtime < datetime.now() - timedelta(days=1):
        return False, "No recent activity in log file"
    
    # Check for recent successful posts
    with open(log_file, 'r') as f:
        content = f.read()
        if "✅ Successfully posted to LinkedIn" not in content:
            return False, "No successful posts found in recent logs"
    
    return True, "System healthy"

def send_health_alert(message):
    """Send health alert email"""
    try:
        # Use the same email system as the main automation
        from scheduled_linkedin_poster_automated import AutomatedLinkedInPoster
        poster = AutomatedLinkedInPoster()
        
        subject = f"🚨 MyBookshelf Automation Health Alert - {datetime.now().strftime('%Y-%m-%d')}"
        html_content = f"""
        <div style="font-family: Arial, sans-serif; padding: 20px;">
            <h2>🚨 Automation Health Alert</h2>
            <p><strong>Time:</strong> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
            <p><strong>Issue:</strong> {message}</p>
            <p>Please check the automation system immediately.</p>
        </div>
        """
        
        poster.send_email_notification(subject, html_content)
        return True
    except Exception as e:
        print(f"Failed to send health alert: {e}")
        return False

if __name__ == "__main__":
    healthy, message = check_linkedin_automation_health()
    
    if not healthy:
        print(f"❌ Health check failed: {message}")
        send_health_alert(message)
        sys.exit(1)
    else:
        print(f"✅ Health check passed: {message}")
        sys.exit(0)
