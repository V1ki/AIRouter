#!/usr/bin/env python3
"""Add unique constraint to base_url column in model_providers table."""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import text
from app.db.database import engine

def add_unique_constraint():
    """Add unique constraint to base_url column."""
    with engine.connect() as conn:
        # Check if constraint already exists
        result = conn.execute(text("""
            SELECT COUNT(*) 
            FROM information_schema.table_constraints 
            WHERE table_name = 'model_providers' 
            AND constraint_type = 'UNIQUE' 
            AND constraint_name = 'model_providers_base_url_key'
        """))
        
        if result.scalar() > 0:
            print("Unique constraint on base_url already exists.")
            return
        
        # Check for duplicate base_urls
        result = conn.execute(text("""
            SELECT base_url, COUNT(*) as count 
            FROM model_providers 
            GROUP BY base_url 
            HAVING COUNT(*) > 1
        """))
        
        duplicates = result.fetchall()
        if duplicates:
            print("Found duplicate base_urls:")
            for dup in duplicates:
                print(f"  - {dup.base_url}: {dup.count} occurrences")
            print("\nPlease resolve duplicates before adding unique constraint.")
            return
        
        # Add unique constraint
        conn.execute(text("""
            ALTER TABLE model_providers 
            ADD CONSTRAINT model_providers_base_url_key UNIQUE (base_url)
        """))
        conn.commit()
        
        print("Successfully added unique constraint to base_url column.")

if __name__ == "__main__":
    add_unique_constraint()