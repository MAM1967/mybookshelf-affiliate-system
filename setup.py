#!/usr/bin/env python3
"""
Quick setup script for MyBookshelf Affiliate System
"""

import os
import subprocess
import sys

def main():
    print("🚀 MyBookshelf Affiliate System Setup")
    print("=" * 50)
    
    # Check if we're in the right directory
    if not os.path.exists('backend') or not os.path.exists('frontend'):
        print("❌ Please run this script from the project root directory")
        return 1
    
    # Install Python dependencies
    print("\n📦 Installing Python dependencies...")
    try:
        subprocess.run([sys.executable, '-m', 'pip', 'install', '-r', 'backend/requirements.txt'], 
                      check=True, capture_output=True)
        print("✅ Python dependencies installed successfully")
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install dependencies: {e}")
        return 1
    
    # Create .env file template
    env_path = 'backend/.env'
    if not os.path.exists(env_path):
        print("\n📝 Creating .env template...")
        env_content = """# Supabase Configuration (REQUIRED)
SUPABASE_URL=your_supabase_project_url
SUPABASE_ANON_KEY=your_supabase_anon_key

# Amazon Associate Configuration (Optional for testing)
AMAZON_ACCESS_KEY=your_amazon_access_key
AMAZON_SECRET_KEY=your_amazon_secret_key
AMAZON_ASSOCIATE_ID=mybookshelf-20

# Email for post approval
POST_APPROVAL_EMAIL=your_email@example.com

# Optional: ScrapingBee API (fallback)
SCRAPINGBEE_API_KEY=your_scrapingbee_api_key
"""
        with open(env_path, 'w') as f:
            f.write(env_content)
        print(f"✅ Created {env_path}")
        print("⚠️  Please edit this file with your actual credentials")
    else:
        print(f"✅ {env_path} already exists")
    
    # Run safe database connection test
    print("\n🧪 Testing database connection...")
    try:
        os.chdir('backend')
        # Safe read-only database test
        test_code = '''
from supabase import create_client
SUPABASE_URL = "https://ackcgrnizuhauccnbiml.supabase.co"
SUPABASE_ANON_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImFja2Nncm5penVoYXVjY25iaW1sIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTEyMjc4MzEsImV4cCI6MjA2NjgwMzgzMX0.SXpIMuNBgUhcEQUHzpEB1zZAdF-UTGvmY81EFUtsAwc"
supabase = create_client(SUPABASE_URL, SUPABASE_ANON_KEY)
response = supabase.table("books_accessories").select("id").limit(1).execute()
print("✅ Database connection successful")
'''
        result = subprocess.run([sys.executable, '-c', test_code], capture_output=True, text=True)
        print(result.stdout)
        if result.stderr:
            print(f"⚠️  Connection test warning: {result.stderr}")
    except Exception as e:
        print(f"⚠️  Could not run connection test: {e}")
    
    # Final instructions
    print("\n🎉 Setup Complete!")
    print("\n📋 Next Steps:")
    print("1. Edit backend/.env with your Supabase credentials")
    print("2. Edit frontend/mini-app/index.html with your Supabase credentials")
    print("3. Open frontend/mini-app/index.html in your browser")
    print("4. Configure Amazon PA API for live data")
    print("5. Set up automation workflows as needed")
    
    return 0

if __name__ == "__main__":
    exit(main()) 