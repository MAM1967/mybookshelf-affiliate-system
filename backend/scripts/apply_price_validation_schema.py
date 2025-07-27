#!/usr/bin/env python3
"""
Apply Price Validation Queue Schema
Creates the price_validation_queue table and related database objects
"""

import os
import sys
from supabase import create_client, Client

# Set up environment
os.environ.setdefault('SUPABASE_URL', 'https://ackcgrnizuhauccnbiml.supabase.co')
os.environ.setdefault('SUPABASE_ANON_KEY', 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImFja2Nncm5penVoYXVjY25iaW1sIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTEyMjc4MzEsImV4cCI6MjA2NjgwMzgzMX0.SXpIMuNBgUhcEQUHzpEB1zZAdF-UTGvmY81EFUtsAwc')

def apply_schema():
    """Apply the price validation queue schema to the database"""
    
    try:
        # Connect to Supabase
        supabase: Client = create_client(
            os.environ['SUPABASE_URL'],
            os.environ['SUPABASE_ANON_KEY']
        )
        print("✅ Connected to Supabase")
        
        # Read the schema file
        schema_file = "backend/supabase/price_validation_queue_schema.sql"
        with open(schema_file, 'r') as f:
            schema_sql = f.read()
        
        print("📄 Schema file loaded")
        
        # Split the SQL into individual statements
        statements = schema_sql.split(';')
        
        for i, statement in enumerate(statements):
            statement = statement.strip()
            if statement:
                try:
                    # Execute each statement
                    result = supabase.rpc('exec_sql', {'sql': statement}).execute()
                    print(f"✅ Statement {i+1} executed successfully")
                except Exception as e:
                    print(f"⚠️ Statement {i+1} failed (may already exist): {e}")
        
        print("🎉 Schema application completed!")
        
        # Test the new table
        try:
            result = supabase.table('price_validation_queue').select('*').limit(1).execute()
            print("✅ Price validation queue table is accessible")
        except Exception as e:
            print(f"❌ Error accessing price validation queue table: {e}")
            
    except Exception as e:
        print(f"❌ Failed to apply schema: {e}")
        sys.exit(1)

if __name__ == "__main__":
    apply_schema() 