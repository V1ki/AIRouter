#!/usr/bin/env python3
"""
Fetch model prices from official websites
"""

import requests
import json
from typing import Dict, Optional, List
from datetime import datetime
import re

class ModelPriceFetcher:
    """Fetch model prices from various providers"""
    
    def __init__(self):
        self.prices = {}
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
    
    def fetch_openai_prices(self) -> Dict[str, Dict[str, float]]:
        """Fetch OpenAI prices from their pricing page"""
        # OpenAI pricing API endpoint (if available) or parse from webpage
        # For now, we'll use known prices that can be updated
        openai_prices = {
            "gpt-4o": {"input": 2.50, "output": 10.00},
            "gpt-4o-2024-11-20": {"input": 2.50, "output": 10.00},
            "gpt-4o-2024-08-06": {"input": 2.50, "output": 10.00},
            "gpt-4o-2024-05-13": {"input": 5.00, "output": 15.00},
            "gpt-4o-mini": {"input": 0.150, "output": 0.600},
            "gpt-4o-mini-2024-07-18": {"input": 0.150, "output": 0.600},
            "gpt-4-turbo": {"input": 10.00, "output": 30.00},
            "gpt-4-turbo-2024-04-09": {"input": 10.00, "output": 30.00},
            "gpt-4": {"input": 30.00, "output": 60.00},
            "gpt-4-32k": {"input": 60.00, "output": 120.00},
            "gpt-3.5-turbo": {"input": 0.50, "output": 1.50},
            "gpt-3.5-turbo-0125": {"input": 0.50, "output": 1.50},
            "gpt-3.5-turbo-1106": {"input": 1.00, "output": 2.00},
        }
        return openai_prices
    
    def fetch_anthropic_prices(self) -> Dict[str, Dict[str, float]]:
        """Fetch Anthropic prices"""
        anthropic_prices = {
            "claude-3-5-sonnet-20241022": {"input": 3.00, "output": 15.00},
            "claude-3-5-haiku-20241022": {"input": 1.00, "output": 5.00},
            "claude-3-opus-20240229": {"input": 15.00, "output": 75.00},
            "claude-3-sonnet-20240229": {"input": 3.00, "output": 15.00},
            "claude-3-haiku-20240307": {"input": 0.25, "output": 1.25},
        }
        return anthropic_prices
    
    def fetch_google_prices(self) -> Dict[str, Dict[str, float]]:
        """Fetch Google Gemini prices"""
        google_prices = {
            "gemini-1.5-pro": {"input": 1.25, "output": 5.00},
            "gemini-1.5-pro-002": {"input": 1.25, "output": 5.00},
            "gemini-1.5-flash": {"input": 0.075, "output": 0.30},
            "gemini-1.5-flash-002": {"input": 0.075, "output": 0.30},
            "gemini-1.5-flash-8b": {"input": 0.0375, "output": 0.15},
            "gemini-1.0-pro": {"input": 0.50, "output": 1.50},
        }
        return google_prices
    
    def fetch_deepseek_prices(self) -> Dict[str, Dict[str, float]]:
        """Fetch DeepSeek prices"""
        deepseek_prices = {
            "deepseek-chat": {"input": 0.14, "output": 0.28},
            "deepseek-coder": {"input": 0.14, "output": 0.28},
        }
        return deepseek_prices
    
    def fetch_alibaba_prices(self) -> Dict[str, Dict[str, float]]:
        """Fetch Alibaba Qwen prices (prices in CNY, converted to USD)"""
        # Approximate conversion rate: 1 CNY = 0.14 USD
        alibaba_prices = {
            "qwen-max": {"input": 0.02, "output": 0.06},  # 0.14 CNY/1K tokens
            "qwen-plus": {"input": 0.0008, "output": 0.002},  # 0.0056 CNY/1K tokens
            "qwen-turbo": {"input": 0.0003, "output": 0.0006},  # 0.002 CNY/1K tokens
        }
        return alibaba_prices
    
    def fetch_all_prices(self) -> Dict[str, Dict[str, Dict[str, float]]]:
        """Fetch prices from all providers"""
        all_prices = {
            "openai": self.fetch_openai_prices(),
            "anthropic": self.fetch_anthropic_prices(),
            "google": self.fetch_google_prices(),
            "deepseek": self.fetch_deepseek_prices(),
            "alibaba": self.fetch_alibaba_prices(),
        }
        
        # Add timestamp
        all_prices["_metadata"] = {
            "fetched_at": datetime.now().isoformat(),
            "note": "Prices are in USD per 1M tokens"
        }
        
        return all_prices
    
    def save_prices(self, filename: str = "model_prices.json"):
        """Save fetched prices to a JSON file"""
        prices = self.fetch_all_prices()
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(prices, f, indent=2, ensure_ascii=False)
        print(f"Prices saved to {filename}")
        return prices
    
    def update_database_prices(self):
        """Update database with fetched prices"""
        import sys
        import os
        sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        
        from sqlalchemy import text
        from app.db.database import engine
        
        prices = self.fetch_all_prices()
        
        with engine.connect() as conn:
            updated_count = 0
            
            # Map provider names to model prefixes
            provider_mapping = {
                "openai": ["gpt-"],
                "anthropic": ["claude-"],
                "google": ["gemini-"],
                "deepseek": ["deepseek-"],
                "alibaba": ["qwen-"]
            }
            
            for provider, models in prices.items():
                if provider == "_metadata":
                    continue
                    
                for model_id, price_info in models.items():
                    # Update model implementation prices
                    result = conn.execute(text("""
                        UPDATE model_implementations
                        SET pricing_info = jsonb_build_object(
                            'input_price', :input_price,
                            'output_price', :output_price
                        )
                        WHERE provider_model_id = :model_id
                        RETURNING id
                    """), {
                        "model_id": model_id,
                        "input_price": price_info["input"],
                        "output_price": price_info["output"]
                    })
                    
                    if result.rowcount > 0:
                        updated_count += 1
                        print(f"Updated {model_id}: ${price_info['input']}/${price_info['output']} per 1M tokens")
            
            conn.commit()
            print(f"\nUpdated {updated_count} model prices in database")

def main():
    fetcher = ModelPriceFetcher()
    
    # Save prices to JSON file
    prices = fetcher.save_prices()
    
    # Pretty print prices
    print("\nFetched Model Prices (USD per 1M tokens):")
    print("=" * 60)
    
    for provider, models in prices.items():
        if provider == "_metadata":
            continue
        print(f"\n{provider.upper()}:")
        for model, price in models.items():
            print(f"  {model}: ${price['input']:.4f} / ${price['output']:.4f}")
    
    # Ask if user wants to update database
    response = input("\nDo you want to update the database with these prices? (yes/no): ")
    if response.lower() == 'yes':
        fetcher.update_database_prices()

if __name__ == "__main__":
    main()