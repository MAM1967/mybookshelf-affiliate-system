#!/usr/bin/env python3
"""
Production Automation Setup for MyBookshelf Affiliate System
Sets up environment variables, cron jobs, and monitoring for automated LinkedIn posting
"""

import os
import sys
import subprocess
from datetime import datetime

def setup_environment_variables():
    """Setup production environment variables"""
    print("🔧 Setting up production environment variables...")
    
    # Production environment variables
    env_vars = {
        'SUPABASE_URL': 'https://ackcgrnizuhauccnbiml.supabase.co',
        'SUPABASE_ANON_KEY': 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImFja2Nncm5penVoYXVjY25iaW1sIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTEyMjc4MzEsImV4cCI6MjA2NjgwMzgzMX0.SXpIMuNBgUhcEQUHzpEB1zZAdF-UTGvmY81_A_T8Lrs',
        'RESEND_API_KEY': 're_CujkiY4j_B4SLnmAJFoxvPVFLuQ51xVJJ',
        'RESEND_FROM_EMAIL': 'admin@mybookshelf.shop',
        'RESEND_FROM_NAME': 'MyBookshelf Admin',
        'ADMIN_EMAIL': 'mcddsl@icloud.com',
        'LINKEDIN_CLIENT_ID': os.getenv('LINKEDIN_CLIENT_ID', ''),
        'LINKEDIN_CLIENT_SECRET': os.getenv('LINKEDIN_CLIENT_SECRET', '')
    }
    
    # Create .env file for production
    env_file_path = os.path.join(os.path.dirname(__file__), '..', '.env.production')
    
    with open(env_file_path, 'w') as f:
        for key, value in env_vars.items():
            f.write(f"{key}={value}\n")
    
    print(f"✅ Environment variables saved to: {env_file_path}")
    
    # Set environment variables in current session
    for key, value in env_vars.items():
        os.environ[key] = value
        print(f"  ✅ {key}: Set")
    
    return True

def setup_cron_job():
    """Setup cron job for automated LinkedIn posting"""
    print("\n⏰ Setting up cron job for automated posting...")
    
    # Get the absolute path to the script
    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(script_dir)
    script_path = os.path.join(script_dir, 'scheduled_linkedin_poster_automated.py')
    
    # Create cron command
    cron_command = f"0 9 * * * cd {project_root} && python3 scripts/scheduled_linkedin_poster_automated.py >> /var/log/mybookshelf_linkedin.log 2>&1"
    
    try:
        # Check if cron job already exists
        result = subprocess.run(['crontab', '-l'], capture_output=True, text=True)
        existing_crontab = result.stdout
        
        if 'scheduled_linkedin_poster_automated.py' in existing_crontab:
            print("⚠️  Cron job already exists, updating...")
            # Remove existing entry
            lines = existing_crontab.split('\n')
            lines = [line for line in lines if 'scheduled_linkedin_poster_automated.py' not in line]
            new_crontab = '\n'.join(lines) + '\n' + cron_command + '\n'
        else:
            print("➕ Adding new cron job...")
            new_crontab = existing_crontab + '\n' + cron_command + '\n'
        
        # Write new crontab
        subprocess.run(['crontab', '-'], input=new_crontab, text=True, check=True)
        
        print("✅ Cron job set up successfully!")
        print(f"   Schedule: Daily at 9:00 AM")
        print(f"   Script: {script_path}")
        print(f"   Log: /var/log/mybookshelf_linkedin.log")
        
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to set up cron job: {e}")
        return False

def create_log_directory():
    """Create log directory for automation logs"""
    print("\n📁 Setting up log directory...")
    
    log_dir = "/var/log"
    log_file = os.path.join(log_dir, "mybookshelf_linkedin.log")
    
    try:
        # Create log file if it doesn't exist
        if not os.path.exists(log_file):
            with open(log_file, 'w') as f:
                f.write(f"# MyBookshelf LinkedIn Automation Log\n")
                f.write(f"# Created: {datetime.now().isoformat()}\n\n")
        
        print(f"✅ Log file ready: {log_file}")
        return True
        
    except PermissionError:
        print(f"⚠️  Cannot create log file in {log_dir} (permission denied)")
        print(f"   You may need to run: sudo touch {log_file}")
        return False

def test_automation_setup():
    """Test the automation setup"""
    print("\n🧪 Testing automation setup...")
    
    try:
        # Test environment variables
        required_vars = ['SUPABASE_URL', 'SUPABASE_ANON_KEY', 'RESEND_API_KEY', 'ADMIN_EMAIL']
        missing_vars = []
        
        for var in required_vars:
            if not os.getenv(var):
                missing_vars.append(var)
        
        if missing_vars:
            print(f"❌ Missing environment variables: {', '.join(missing_vars)}")
            return False
        
        print("✅ Environment variables configured")
        
        # Test script execution
        script_path = os.path.join(os.path.dirname(__file__), 'scheduled_linkedin_poster_automated.py')
        result = subprocess.run([sys.executable, script_path, '--check-scheduled'], 
                              capture_output=True, text=True, timeout=30)
        
        if result.returncode == 0:
            print("✅ Script execution test passed")
            return True
        else:
            print(f"❌ Script execution test failed: {result.stderr}")
            return False
            
    except Exception as e:
        print(f"❌ Automation setup test failed: {e}")
        return False

def create_monitoring_script():
    """Create a monitoring script for system health"""
    print("\n🔍 Creating monitoring script...")
    
    monitoring_script = '''#!/usr/bin/env python3
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
'''
    
    script_path = os.path.join(os.path.dirname(__file__), 'health_check.py')
    with open(script_path, 'w') as f:
        f.write(monitoring_script)
    
    # Make executable
    os.chmod(script_path, 0o755)
    
    print(f"✅ Monitoring script created: {script_path}")
    return True

def main():
    """Main setup function"""
    print("🚀 MyBookshelf Production Automation Setup")
    print("=" * 50)
    
    # Setup environment variables
    if not setup_environment_variables():
        print("❌ Failed to setup environment variables")
        sys.exit(1)
    
    # Setup cron job
    if not setup_cron_job():
        print("❌ Failed to setup cron job")
        sys.exit(1)
    
    # Create log directory
    create_log_directory()
    
    # Create monitoring script
    create_monitoring_script()
    
    # Test setup
    if not test_automation_setup():
        print("❌ Automation setup test failed")
        sys.exit(1)
    
    print("\n" + "=" * 50)
    print("✅ PRODUCTION AUTOMATION SETUP COMPLETE!")
    print("=" * 50)
    print("🎯 What's been configured:")
    print("   ✅ Environment variables for production")
    print("   ✅ Daily cron job at 9:00 AM")
    print("   ✅ Log file for monitoring")
    print("   ✅ Health check script")
    print("   ✅ Email notifications for daily reports")
    print("\n📧 You'll receive daily email reports at mcddsl@icloud.com")
    print("📊 Check logs at: /var/log/mybookshelf_linkedin.log")
    print("\n🚀 The system will automatically post to LinkedIn daily!")
    print("=" * 50)

if __name__ == "__main__":
    main() 