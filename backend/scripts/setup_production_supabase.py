#!/usr/bin/env python3
"""
Production Supabase Setup for MyBookshelf Affiliate System
Configures production database with all required schemas and data
"""

import os
import sys
import json
import requests
from datetime import datetime
import subprocess
from typing import Dict, Optional
import logging

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class ProductionSupabaseSetup:
    """Setup production Supabase configuration"""
    
    def __init__(self):
        """Initialize production setup"""
        self.project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        self.scripts_dir = os.path.dirname(os.path.abspath(__file__))
        self.supabase_dir = os.path.join(self.project_root, 'backend', 'supabase')
        
        # Schema files
        self.main_schema_file = os.path.join(self.supabase_dir, 'schema.sql')
        self.admin_schema_file = os.path.join(self.supabase_dir, 'admin_schema.sql')
        
        # Production configuration
        self.production_config = {
            'project_name': 'mybookshelf',
            'region': 'us-east-1',
            'tier': 'free',  # Start with free tier
            'database_password': None  # Will be generated
        }
    
    def check_prerequisites(self) -> bool:
        """Check if all prerequisites are met"""
        print("🔧 Checking Production Setup Prerequisites...")
        
        # Check if schema files exist
        if not os.path.exists(self.main_schema_file):
            print(f"❌ Main schema file not found: {self.main_schema_file}")
            return False
        
        if not os.path.exists(self.admin_schema_file):
            print(f"❌ Admin schema file not found: {self.admin_schema_file}")
            return False
        
        print("✅ Schema files found")
        
        # Check if Supabase CLI is installed
        try:
            result = subprocess.run(['supabase', '--version'], capture_output=True, text=True)
            if result.returncode == 0:
                print(f"✅ Supabase CLI installed: {result.stdout.strip()}")
            else:
                print("⚠️  Supabase CLI not found - manual setup will be required")
                return False
        except FileNotFoundError:
            print("⚠️  Supabase CLI not found - manual setup will be required")
            return False
        
        return True
    
    def display_manual_setup_instructions(self):
        """Display manual setup instructions for Supabase"""
        print("\n" + "="*70)
        print("📋 MANUAL SUPABASE PRODUCTION SETUP INSTRUCTIONS")
        print("="*70)
        
        print("\n🌐 STEP 1: Create Supabase Project")
        print("1. Go to https://supabase.com/dashboard")
        print("2. Click 'New Project'")
        print("3. Organization: Your personal account")
        print("4. Project Name: mybookshelf")
        print("5. Database Password: [Generate strong password]")
        print("6. Region: US East (N. Virginia) for best performance")
        print("7. Pricing Plan: Free (can upgrade later)")
        print("8. Click 'Create new project'")
        
        print("\n🔗 STEP 2: Get Connection Details")
        print("After project creation:")
        print("1. Go to Project Settings → API")
        print("2. Copy the following values:")
        print("   - Project URL (https://[project-id].supabase.co)")
        print("   - Anon/Public key (starts with 'eyJ...')")
        print("   - Service Role key (starts with 'eyJ...')")
        
        print("\n💾 STEP 3: Deploy Database Schema")
        print("1. Go to Project Settings → Database")
        print("2. Scroll down to 'Connection string'")
        print("3. Copy the connection string")
        print("4. Open SQL Editor in Supabase dashboard")
        print("5. Create new query")
        print("6. Copy and paste the following schemas in order:")
        
        # Display schema content for manual copying
        print("\n📋 SCHEMA 1: Main Schema (schema.sql)")
        print("-" * 40)
        try:
            with open(self.main_schema_file, 'r') as f:
                main_schema = f.read()
                print(main_schema)
        except Exception as e:
            print(f"❌ Error reading main schema: {e}")
        
        print("\n📋 SCHEMA 2: Admin Schema (admin_schema.sql)")
        print("-" * 40)
        try:
            with open(self.admin_schema_file, 'r') as f:
                admin_schema = f.read()
                print(admin_schema[:1000] + "...")  # Show first 1000 chars
                print("\n[...continued in file...]")
        except Exception as e:
            print(f"❌ Error reading admin schema: {e}")
        
        print("\n🔑 STEP 4: Configure Environment Variables")
        print("Add these to your production environment:")
        print("SUPABASE_URL=https://[your-project-id].supabase.co")
        print("SUPABASE_ANON_KEY=[your-anon-key]")
        print("SUPABASE_SERVICE_ROLE_KEY=[your-service-role-key]")
        
        print("\n🧪 STEP 5: Test Connection")
        print("Run: python3 test_production_supabase.py")
        
        return True
    
    def create_production_test_script(self):
        """Create a test script for production Supabase connection"""
        test_script_content = '''#!/usr/bin/env python3
"""
Test Production Supabase Connection
"""

import os
import sys
from datetime import datetime

# Add parent directory for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from supabase import create_client, Client
    print("✅ Supabase library imported successfully")
except ImportError:
    print("❌ Supabase library not found. Install with: pip install supabase")
    sys.exit(1)

def test_production_connection():
    """Test production Supabase connection"""
    print("🧪 Testing Production Supabase Connection...")
    print("=" * 50)
    
    # Get environment variables
    supabase_url = os.getenv('SUPABASE_URL')
    supabase_key = os.getenv('SUPABASE_ANON_KEY')
    
    if not supabase_url:
        print("❌ SUPABASE_URL environment variable not set")
        print("Set with: export SUPABASE_URL='https://your-project-id.supabase.co'")
        return False
    
    if not supabase_key:
        print("❌ SUPABASE_ANON_KEY environment variable not set") 
        print("Set with: export SUPABASE_ANON_KEY='your-anon-key'")
        return False
    
    print(f"📊 Testing connection to: {supabase_url}")
    
    try:
        # Create client
        supabase: Client = create_client(supabase_url, supabase_key)
        print("✅ Supabase client created successfully")
        
        # Test database connection with a simple query
        result = supabase.table('books_accessories').select('count').execute()
        print("✅ Database connection successful")
        
        # Test admin tables
        result = supabase.table('pending_books').select('count').execute()
        print("✅ Admin tables accessible")
        
        result = supabase.table('approval_sessions').select('count').execute()
        print("✅ Approval system tables accessible")
        
        # Test admin dashboard view
        result = supabase.rpc('admin_dashboard_summary').execute()
        print("✅ Admin dashboard view working")
        
        print("\\n🎉 All tests passed! Production database is ready.")
        return True
        
    except Exception as e:
        print(f"❌ Connection test failed: {e}")
        print("\\n🔧 Troubleshooting:")
        print("1. Verify project URL is correct")
        print("2. Verify anon key is correct") 
        print("3. Ensure database schemas are deployed")
        print("4. Check project is not paused/suspended")
        return False

if __name__ == "__main__":
    success = test_production_connection()
    sys.exit(0 if success else 1)
'''
        
        test_script_path = os.path.join(self.scripts_dir, 'test_production_supabase.py')
        with open(test_script_path, 'w') as f:
            f.write(test_script_content)
        
        # Make executable
        os.chmod(test_script_path, 0o755)
        print(f"✅ Created production test script: {test_script_path}")
    
    def create_environment_template(self):
        """Create environment variable template for production"""
        env_template = '''# MyBookshelf Environment Variables
# Copy these to your deployment environment (Vercel, etc.)

# Supabase Configuration (REQUIRED)
SUPABASE_URL=https://your-project-id.supabase.co
SUPABASE_ANON_KEY=your-anon-key-here
SUPABASE_SERVICE_ROLE_KEY=your-service-role-key-here

# Email Configuration (Resend)
RESEND_API_KEY=re_CujkiY4j_B4SLnmAJFoxvPVFLuQ51xVJJ
RESEND_FROM_EMAIL=admin@mybookshelf.shop
RESEND_FROM_NAME=MyBookshelf Admin
ADMIN_EMAIL=mcddsl@icloud.com

# Application URLs
ADMIN_DASHBOARD_URL=https://mybookshelf.shop/admin
PUBLIC_SITE_URL=https://mybookshelf.shop

# LinkedIn Configuration (To be configured)
LINKEDIN_CLIENT_ID=78wmrhdd99ssbi
LINKEDIN_CLIENT_SECRET=your-linkedin-client-secret

# Amazon Associate Configuration
AMAZON_ASSOCIATE_ID=mybookshelf-20
AMAZON_ACCESS_KEY=your-amazon-access-key
AMAZON_SECRET_KEY=your-amazon-secret-key

# Optional: ScrapingBee fallback
SCRAPINGBEE_API_KEY=your-scrapingbee-api-key
'''
        
        env_file_path = os.path.join(self.project_root, '.env.template')
        with open(env_file_path, 'w') as f:
            f.write(env_template)
        
        print(f"✅ Created environment template: {env_file_path}")
    
    def create_vercel_deployment_config(self):
        """Create Vercel deployment configuration"""
        vercel_config = {
            "name": "mybookshelf-affiliate-system",
            "version": 2,
            "builds": [
                {
                    "src": "frontend/mini-app/**/*",
                    "use": "@vercel/static"
                }
            ],
            "routes": [
                {
                    "src": "/admin/(.*)",
                    "dest": "/frontend/mini-app/admin.html"
                },
                {
                    "src": "/(.*)",
                    "dest": "/frontend/mini-app/index.html"
                }
            ],
            "env": {
                "SUPABASE_URL": "@supabase-url",
                "SUPABASE_ANON_KEY": "@supabase-anon-key",
                "RESEND_API_KEY": "@resend-api-key",
                "ADMIN_EMAIL": "@admin-email",
                "LINKEDIN_CLIENT_ID": "@linkedin-client-id"
            }
        }
        
        vercel_file_path = os.path.join(self.project_root, 'vercel.json')
        with open(vercel_file_path, 'w') as f:
            json.dump(vercel_config, f, indent=2)
        
        print(f"✅ Created Vercel config: {vercel_file_path}")
    
    def display_next_steps(self):
        """Display next steps after setup"""
        print("\n" + "="*70)
        print("🚀 DEPLOYMENT SETUP NEXT STEPS")
        print("="*70)
        
        print("\n1. ✅ Database Setup:")
        print("   - Follow manual instructions above to create Supabase project")
        print("   - Deploy schemas using SQL Editor")
        print("   - Test connection with: python3 test_production_supabase.py")
        
        print("\n2. 🔧 Environment Configuration:")
        print("   - Update .env.template with your actual values")
        print("   - Add environment variables to Vercel dashboard")
        print("   - Configure domain: mybookshelf.shop")
        
        print("\n3. 🔗 LinkedIn OAuth (Next Phase):")
        print("   - Update LinkedIn app with production redirect URIs")
        print("   - Test OAuth flow with production domain")
        print("   - Configure posting automation")
        
        print("\n4. 📧 Email Integration:")
        print("   - Verify Resend API works with production database")
        print("   - Test Sunday approval workflow")
        print("   - Confirm email delivery to mcddsl@icloud.com")
        
        print("\n5. 🧪 Production Testing:")
        print("   - Run full test suite against production")
        print("   - Validate affiliate links and revenue tracking")
        print("   - Test admin dashboard functionality")
        
        print("\n6. 🎯 Go Live:")
        print("   - Schedule first Sunday approval email")
        print("   - Prepare for first LinkedIn posts (Tue/Wed/Thu)")
        print("   - Monitor system performance and revenue")
        
        print(f"\n💡 Quick Commands:")
        print(f"   Test database: python3 test_production_supabase.py")
        print(f"   Test email: python3 test_email_integration.py")
        print(f"   Full test suite: python3 run_all_tests.py")
    
    def run_setup(self):
        """Run the complete production setup process"""
        print("🚀 MyBookshelf Production Supabase Setup")
        print("=" * 50)
        print(f"📅 Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        # Check prerequisites
        if not self.check_prerequisites():
            print("\n⚠️  Prerequisites not met - proceeding with manual setup instructions")
        
        # Create helper scripts and configs
        print("\n🛠️  Creating Production Setup Files...")
        self.create_production_test_script()
        self.create_environment_template()
        self.create_vercel_deployment_config()
        
        # Display manual setup instructions
        self.display_manual_setup_instructions()
        
        # Display next steps
        self.display_next_steps()
        
        print("\n✅ Production setup preparation complete!")
        print("📋 Follow the manual instructions above to complete database setup")

def main():
    """Main setup execution"""
    setup = ProductionSupabaseSetup()
    setup.run_setup()

if __name__ == "__main__":
    main() 