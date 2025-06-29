#!/usr/bin/env python3
"""
MyBookshelf Duplicate Prevention System
Prevents duplicate records from being inserted into the database
"""

from supabase import create_client
from typing import Dict, List, Optional
import hashlib
import sys

class DuplicatePreventionSystem:
    def __init__(self, supabase_url: str, supabase_key: str):
        """Initialize the duplicate prevention system"""
        self.supabase = create_client(supabase_url, supabase_key)
        
    def create_record_hash(self, title: str, author: str, category: str) -> str:
        """Create a unique hash for a book/accessory record"""
        # Normalize text for consistent hashing
        normalized_title = title.strip().lower()
        normalized_author = author.strip().lower()
        normalized_category = category.strip().lower()
        
        # Create hash from key fields
        hash_input = f"{normalized_title}|{normalized_author}|{normalized_category}"
        return hashlib.md5(hash_input.encode()).hexdigest()
    
    def check_for_duplicates(self, title: str, author: str, category: str) -> List[Dict]:
        """Check if a record already exists in the database"""
        try:
            # Search for exact matches
            result = self.supabase.table('books_accessories').select('*').filter(
                'title', 'ilike', f'%{title.strip()}%'
            ).filter(
                'author', 'ilike', f'%{author.strip()}%'
            ).filter(
                'category', 'ilike', f'%{category.strip()}%'
            ).execute()
            
            # Also check for close matches (fuzzy matching)
            exact_matches = []
            for record in result.data:
                if (record['title'].strip().lower() == title.strip().lower() and
                    record['author'].strip().lower() == author.strip().lower() and
                    record['category'].strip().lower() == category.strip().lower()):
                    exact_matches.append(record)
            
            return exact_matches
            
        except Exception as e:
            print(f"Error checking for duplicates: {e}")
            return []
    
    def safe_insert(self, record_data: Dict) -> Dict:
        """Safely insert a record, preventing duplicates"""
        title = record_data.get('title', '')
        author = record_data.get('author', '')
        category = record_data.get('category', '')
        
        # Check for existing duplicates
        duplicates = self.check_for_duplicates(title, author, category)
        
        if duplicates:
            return {
                'success': False,
                'error': 'DUPLICATE_FOUND',
                'message': f'Duplicate record already exists: "{title}" by {author}',
                'existing_records': duplicates,
                'duplicate_count': len(duplicates)
            }
        
        # No duplicates found, safe to insert
        try:
            # Add unique hash to the record
            record_hash = self.create_record_hash(title, author, category)
            record_data['record_hash'] = record_hash
            
            result = self.supabase.table('books_accessories').insert(record_data).execute()
            
            return {
                'success': True,
                'message': f'Successfully inserted: "{title}" by {author}',
                'inserted_record': result.data[0] if result.data else None,
                'record_hash': record_hash
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': 'INSERT_FAILED',
                'message': f'Failed to insert record: {str(e)}'
            }
    
    def cleanup_all_duplicates(self) -> Dict:
        """Clean up all duplicate records in the database"""
        try:
            # Get all records
            result = self.supabase.table('books_accessories').select('*').order('id').execute()
            all_records = result.data
            
            # Group by title, author, category
            groups = {}
            for record in all_records:
                key = (record['title'].strip().lower(), 
                      record['author'].strip().lower(), 
                      record['category'].strip().lower())
                if key not in groups:
                    groups[key] = []
                groups[key].append(record)
            
            # Find duplicates
            duplicates_found = 0
            records_deleted = 0
            
            for group_key, records in groups.items():
                if len(records) > 1:
                    duplicates_found += 1
                    # Keep the newest record (highest ID)
                    records_sorted = sorted(records, key=lambda x: x['id'], reverse=True)
                    keep_record = records_sorted[0]
                    delete_records = records_sorted[1:]
                    
                    # Delete duplicates
                    for record in delete_records:
                        try:
                            self.supabase.table('books_accessories').delete().eq('id', record['id']).execute()
                            records_deleted += 1
                        except Exception as e:
                            print(f"Error deleting record ID {record['id']}: {e}")
            
            return {
                'success': True,
                'duplicates_found': duplicates_found,
                'records_deleted': records_deleted,
                'message': f'Cleanup complete: {records_deleted} duplicate records removed'
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'message': 'Failed to cleanup duplicates'
            }
    
    def add_unique_constraints(self) -> Dict:
        """Add database constraints to prevent future duplicates"""
        try:
            # Note: This would typically be done via SQL migration
            # For Supabase, you'd need to run this in the SQL editor:
            sql_constraint = """
            -- Add a unique constraint based on title, author, and category
            ALTER TABLE books_accessories 
            ADD CONSTRAINT unique_book_record 
            UNIQUE (title, author, category);
            
            -- Add a hash column for faster duplicate detection
            ALTER TABLE books_accessories 
            ADD COLUMN IF NOT EXISTS record_hash VARCHAR(32);
            
            -- Create index on hash for performance
            CREATE INDEX IF NOT EXISTS idx_record_hash 
            ON books_accessories(record_hash);
            """
            
            return {
                'success': True,
                'message': 'Database constraints ready',
                'sql_command': sql_constraint,
                'note': 'Run the SQL command in your Supabase SQL editor to add constraints'
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'message': 'Failed to prepare constraints'
            }

# Command-line interface
def main():
    # Database configuration
    SUPABASE_URL = 'https://ackcgrnizuhauccnbiml.supabase.co'
    SUPABASE_ANON_KEY = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImFja2Nncm5penVoYXVjY25iaW1sIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTEyMjc4MzEsImV4cCI6MjA2NjgwMzgzMX0.SXpIMuNBgUhcEQUHzpEB1zZAdF-UTGvmY81EFUtsAwc'
    
    # Initialize system
    dps = DuplicatePreventionSystem(SUPABASE_URL, SUPABASE_ANON_KEY)
    
    if len(sys.argv) < 2:
        print("Usage: python duplicate_prevention.py [check|cleanup|test]")
        sys.exit(1)
    
    command = sys.argv[1].lower()
    
    if command == 'check':
        # Check current database status
        print("🔍 Checking database for duplicates...")
        result = dps.cleanup_all_duplicates()
        print(f"Result: {result}")
        
    elif command == 'cleanup':
        # Run full cleanup
        print("🧹 Running duplicate cleanup...")
        result = dps.cleanup_all_duplicates()
        print(f"✅ Cleanup complete: {result['message']}")
        
    elif command == 'test':
        # Test duplicate prevention
        print("🧪 Testing duplicate prevention...")
        
        test_record = {
            'title': 'The Five Dysfunctions of a Team',
            'author': 'Patrick Lencioni',
            'category': 'Books',
            'price': 14.99,
            'affiliate_link': 'https://example.com',
            'image_url': 'https://example.com/image.jpg'
        }
        
        result = dps.safe_insert(test_record)
        print(f"Test result: {result}")
        
    elif command == 'constraints':
        # Show SQL constraints
        result = dps.add_unique_constraints()
        print("Database Constraints:")
        print(result['sql_command'])
        print(f"\nNote: {result['note']}")
        
    else:
        print("Invalid command. Use: check, cleanup, test, or constraints")

if __name__ == "__main__":
    main() 