#!/usr/bin/env python3
"""Clean up duplicate providers by keeping only the oldest one."""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import text
from app.db.database import engine

def cleanup_duplicates():
    """Remove duplicate providers keeping only the oldest one."""
    with engine.connect() as conn:
        # Find all duplicate base_urls
        result = conn.execute(text("""
            SELECT base_url, COUNT(*) as count 
            FROM model_providers 
            GROUP BY base_url 
            HAVING COUNT(*) > 1
        """))
        
        duplicates = result.fetchall()
        if not duplicates:
            print("No duplicate providers found.")
            return
        
        print(f"Found {len(duplicates)} duplicate base_urls")
        
        for dup in duplicates:
            base_url = dup.base_url
            
            # Get all providers with this base_url, ordered by creation time
            # Since we don't have a created_at field, we'll use ID order (earlier UUIDs are usually older)
            providers = conn.execute(text("""
                SELECT id, name FROM model_providers 
                WHERE base_url = :base_url 
                ORDER BY id
            """), {"base_url": base_url}).fetchall()
            
            if len(providers) <= 1:
                continue
                
            # Keep the first one, delete the rest
            keep_id = providers[0].id
            keep_name = providers[0].name
            
            print(f"\nProcessing {base_url}:")
            print(f"  Keeping: {keep_name} (ID: {keep_id})")
            
            for provider in providers[1:]:
                print(f"  Deleting: {provider.name} (ID: {provider.id})")
                
                # First, update all references to point to the keeper
                # Update model_implementations
                conn.execute(text("""
                    UPDATE model_implementations 
                    SET provider_id = :keep_id 
                    WHERE provider_id = :old_id
                """), {"keep_id": keep_id, "old_id": provider.id})
                
                # Update api_keys
                conn.execute(text("""
                    UPDATE api_keys 
                    SET provider_id = :keep_id 
                    WHERE provider_id = :old_id
                """), {"keep_id": keep_id, "old_id": provider.id})
                
                # Update free_quotas
                conn.execute(text("""
                    UPDATE free_quotas 
                    SET provider_id = :keep_id 
                    WHERE provider_id = :old_id
                """), {"keep_id": keep_id, "old_id": provider.id})
                
                # Now delete the duplicate provider
                conn.execute(text("""
                    DELETE FROM model_providers WHERE id = :id
                """), {"id": provider.id})
        
        conn.commit()
        print("\nDuplicate providers cleaned up successfully.")

if __name__ == "__main__":
    cleanup_duplicates()