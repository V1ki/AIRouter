#!/usr/bin/env python3
"""Fix model prices that were incorrectly multiplied by 1000"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import text
from app.db.database import engine

def fix_model_prices():
    """Fix model prices by dividing by 1000"""
    with engine.connect() as conn:
        # Get all model implementations with pricing info
        result = conn.execute(text("""
            SELECT id, provider_model_id, pricing_info 
            FROM model_implementations 
            WHERE pricing_info IS NOT NULL
        """))
        
        implementations = result.fetchall()
        updated_count = 0
        
        for impl in implementations:
            if impl.pricing_info:
                input_price = impl.pricing_info.get('input_price', 0)
                output_price = impl.pricing_info.get('output_price', 0)
                
                # Check if prices seem to be multiplied by 1000
                # Most model prices should be less than 100 USD per 1M tokens
                if input_price > 100 or output_price > 100:
                    new_input_price = input_price / 1000
                    new_output_price = output_price / 1000
                    
                    print(f"Fixing {impl.provider_model_id}: {input_price}/{output_price} -> {new_input_price}/{new_output_price}")
                    
                    # Update the pricing info
                    conn.execute(text("""
                        UPDATE model_implementations 
                        SET pricing_info = jsonb_build_object(
                            'input_price', :input_price,
                            'output_price', :output_price
                        )
                        WHERE id = :id
                    """), {
                        "id": impl.id,
                        "input_price": new_input_price,
                        "output_price": new_output_price
                    })
                    
                    updated_count += 1
        
        conn.commit()
        
        if updated_count > 0:
            print(f"\nFixed {updated_count} model prices.")
        else:
            print("No prices needed fixing.")

if __name__ == "__main__":
    fix_model_prices()