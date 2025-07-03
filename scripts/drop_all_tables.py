#!/usr/bin/env python3
"""
Drop all tables in the database
"""
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.db.database import engine, Base
from sqlalchemy import text

def drop_all_tables():
    """Drop all tables in the database"""
    print("Dropping all tables...")
    
    with engine.connect() as conn:
        # Drop all tables in the public schema
        conn.execute(text("DROP SCHEMA public CASCADE"))
        conn.execute(text("CREATE SCHEMA public"))
        conn.commit()
    
    print("All tables dropped successfully!")

if __name__ == "__main__":
    response = input("Are you sure you want to drop all tables? This action cannot be undone. (yes/no): ")
    if response.lower() == 'yes':
        drop_all_tables()
    else:
        print("Operation cancelled.")