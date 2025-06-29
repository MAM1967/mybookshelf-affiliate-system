"""
Configuration settings for MyBookshelf Affiliate System
"""
import os
from typing import Optional

class Config:
    """Configuration class for environment variables and settings"""
    
    # Supabase Configuration
    SUPABASE_URL: Optional[str] = os.getenv('SUPABASE_URL')
    SUPABASE_ANON_KEY: Optional[str] = os.getenv('SUPABASE_ANON_KEY')
    
    # Amazon Associate Configuration
    AMAZON_ACCESS_KEY: Optional[str] = os.getenv('AMAZON_ACCESS_KEY')
    AMAZON_SECRET_KEY: Optional[str] = os.getenv('AMAZON_SECRET_KEY')
    AMAZON_ASSOCIATE_ID: Optional[str] = os.getenv('AMAZON_ASSOCIATE_ID', 'mybookshelf-20')
    
    # ScrapingBee Configuration (fallback)
    SCRAPINGBEE_API_KEY: Optional[str] = os.getenv('SCRAPINGBEE_API_KEY')
    
    # LinkedIn Configuration (for future automation)
    LINKEDIN_CLIENT_ID: Optional[str] = os.getenv('LINKEDIN_CLIENT_ID')
    LINKEDIN_CLIENT_SECRET: Optional[str] = os.getenv('LINKEDIN_CLIENT_SECRET')
    
    # Application Settings
    MAX_BOOKS_PER_WEEK: int = 3
    MAX_ACCESSORIES_PER_WEEK: int = 1
    POST_APPROVAL_EMAIL: Optional[str] = os.getenv('POST_APPROVAL_EMAIL')
    
    @classmethod
    def validate_required_settings(cls) -> bool:
        """Validate that required environment variables are set"""
        required_vars = [
            cls.SUPABASE_URL,
            cls.SUPABASE_ANON_KEY
        ]
        
        missing_vars = [var for var in required_vars if not var]
        
        if missing_vars:
            print("❌ Missing required environment variables:")
            if not cls.SUPABASE_URL:
                print("  - SUPABASE_URL")
            if not cls.SUPABASE_ANON_KEY:
                print("  - SUPABASE_ANON_KEY")
            return False
        
        return True
    
    @classmethod
    def get_example_env_content(cls) -> str:
        """Return example .env file content"""
        return """# Supabase Configuration
SUPABASE_URL=your_supabase_project_url
SUPABASE_ANON_KEY=your_supabase_anon_key

# Amazon Associate Configuration
AMAZON_ACCESS_KEY=your_amazon_access_key
AMAZON_SECRET_KEY=your_amazon_secret_key
AMAZON_ASSOCIATE_ID=your_amazon_associate_tag

# LinkedIn Configuration (for automation)
LINKEDIN_CLIENT_ID=your_linkedin_client_id
LINKEDIN_CLIENT_SECRET=your_linkedin_client_secret

# Email for post approval
POST_APPROVAL_EMAIL=your_email@example.com

# Optional: ScrapingBee API (fallback)
SCRAPINGBEE_API_KEY=your_scrapingbee_api_key
""" 