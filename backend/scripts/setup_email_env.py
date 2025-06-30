#!/usr/bin/env python3
"""
Email Environment Setup for MyBookshelf Affiliate System
Sets up production environment variables for email integration
"""

import os
import sys

def setup_email_environment():
    """Setup email environment variables for production"""
    
    print("🔧 MyBookshelf Email Environment Setup")
    print("="*50)
    
    # Email configuration
    env_vars = {
        'RESEND_API_KEY': 're_CujkiY4j_B4SLnmAJFoxvPVFLuQ51xVJJ',
        'RESEND_FROM_EMAIL': 'admin@mybookshelf.shop',
        'RESEND_FROM_NAME': 'MyBookshelf Admin',
        'ADMIN_EMAIL': 'mcddsl@icloud.com',
        'ADMIN_DASHBOARD_URL': 'https://mybookshelf.shop/admin',
        'PUBLIC_SITE_URL': 'https://mybookshelf.shop'
    }
    
    # Check if Supabase is configured
    supabase_url = os.getenv('SUPABASE_URL')
    supabase_key = os.getenv('SUPABASE_ANON_KEY')
    
    print("📧 Email Configuration:")
    for key, value in env_vars.items():
        current_value = os.getenv(key)
        if current_value:
            print(f"  ✅ {key}: Already set")
        else:
            os.environ[key] = value
            print(f"  ➕ {key}: Set to {value[:20]}{'...' if len(value) > 20 else ''}")
    
    print("\n💾 Database Configuration:")
    if supabase_url and supabase_key:
        print(f"  ✅ SUPABASE_URL: {supabase_url}")
        print(f"  ✅ SUPABASE_ANON_KEY: Set")
    else:
        print("  ⚠️  SUPABASE_URL: Not set (required for production)")
        print("  ⚠️  SUPABASE_ANON_KEY: Not set (required for production)")
        print("\n🔧 To configure Supabase:")
        print("     export SUPABASE_URL='your_supabase_project_url'")
        print("     export SUPABASE_ANON_KEY='your_supabase_anon_key'")
    
    print("\n🎯 Sunday Workflow Configuration:")
    print("  📅 Trigger: Every Sunday morning")
    print("  📧 Admin Email: mcddsl@icloud.com")
    print("  🔗 Dashboard: https://mybookshelf.shop/admin")
    print("  ⏰ Approval Deadline: Tuesday")
    
    print("\n✅ Email environment setup complete!")
    print("🚀 Run 'python3 test_email_integration.py' to test the configuration")

if __name__ == "__main__":
    setup_email_environment() 