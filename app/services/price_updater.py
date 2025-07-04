"""
Price updater service that periodically fetches and updates model prices
"""

import asyncio
import httpx
import json
from datetime import datetime, timedelta
from typing import Dict, Optional, List
from sqlalchemy.orm import Session
from sqlalchemy import text

from app.db.database import SessionLocal
from app.models.provider import ModelImplementation
import logging

logger = logging.getLogger(__name__)

class PriceUpdaterService:
    """Service to update model prices from various sources"""
    
    def __init__(self):
        self.last_update = None
        self.update_interval = timedelta(hours=24)  # Update daily
        self.price_sources = {
            "openai": "https://openai.com/api/pricing/",
            "anthropic": "https://www.anthropic.com/pricing",
            "google": "https://ai.google.dev/pricing",
            "deepseek": "https://platform.deepseek.com/api-docs/pricing"
        }
        
        # Known prices (fallback when scraping fails)
        self.known_prices = {
            # OpenAI models (USD per 1M tokens)
            "gpt-4o": {"input": 2.50, "output": 10.00},
            "gpt-4o-2024-11-20": {"input": 2.50, "output": 10.00},
            "gpt-4o-mini": {"input": 0.150, "output": 0.600},
            "gpt-4-turbo": {"input": 10.00, "output": 30.00},
            "gpt-3.5-turbo": {"input": 0.50, "output": 1.50},
            
            # Anthropic models
            "claude-3-5-sonnet-20241022": {"input": 3.00, "output": 15.00},
            "claude-3-opus-20240229": {"input": 15.00, "output": 75.00},
            "claude-3-sonnet-20240229": {"input": 3.00, "output": 15.00},
            "claude-3-haiku-20240307": {"input": 0.25, "output": 1.25},
            
            # Google models
            "gemini-1.5-pro": {"input": 1.25, "output": 5.00},
            "gemini-1.5-flash": {"input": 0.075, "output": 0.30},
            "gemini-1.0-pro": {"input": 0.50, "output": 1.50},
            
            # DeepSeek models
            "deepseek-chat": {"input": 0.14, "output": 0.28},
            "deepseek-coder": {"input": 0.14, "output": 0.28},
            
            # Chinese models (prices in USD)
            "qwen-max": {"input": 0.02, "output": 0.06},
            "qwen-plus": {"input": 0.0008, "output": 0.002},
            "qwen-turbo": {"input": 0.0003, "output": 0.0006},
            "glm-4": {"input": 0.1, "output": 0.1},
            "moonshot-v1-128k": {"input": 0.06, "output": 0.06},
        }
    
    async def fetch_openai_prices(self) -> Optional[Dict[str, Dict[str, float]]]:
        """Fetch OpenAI prices from API or documentation"""
        try:
            # OpenAI doesn't have a public pricing API
            # In production, you might scrape their pricing page or use their API
            return self.known_prices
        except Exception as e:
            logger.error(f"Failed to fetch OpenAI prices: {e}")
            return None
    
    async def update_prices_in_db(self, prices: Dict[str, Dict[str, float]]) -> int:
        """Update prices in database"""
        db = SessionLocal()
        updated_count = 0
        
        try:
            for model_id, price_info in prices.items():
                # Update all implementations with this provider model ID
                result = db.execute(text("""
                    UPDATE model_implementations
                    SET pricing_info = jsonb_build_object(
                        'input_price', :input_price,
                        'output_price', :output_price,
                        'last_updated', :last_updated
                    )
                    WHERE provider_model_id = :model_id
                """), {
                    "model_id": model_id,
                    "input_price": price_info["input"],
                    "output_price": price_info["output"],
                    "last_updated": datetime.utcnow().isoformat()
                })
                
                if result.rowcount > 0:
                    updated_count += result.rowcount
                    logger.info(f"Updated price for {model_id}: ${price_info['input']}/{price_info['output']}")
            
            db.commit()
            logger.info(f"Successfully updated {updated_count} model prices")
            
        except Exception as e:
            logger.error(f"Failed to update prices in database: {e}")
            db.rollback()
        finally:
            db.close()
        
        return updated_count
    
    async def check_price_changes(self, new_prices: Dict[str, Dict[str, float]]) -> List[Dict]:
        """Check for significant price changes"""
        db = SessionLocal()
        changes = []
        
        try:
            # Get current prices from database
            results = db.query(ModelImplementation).filter(
                ModelImplementation.provider_model_id.in_(list(new_prices.keys()))
            ).all()
            
            for impl in results:
                if impl.pricing_info and impl.provider_model_id in new_prices:
                    old_input = float(impl.pricing_info.get('input_price', 0))
                    old_output = float(impl.pricing_info.get('output_price', 0))
                    new_input = new_prices[impl.provider_model_id]['input']
                    new_output = new_prices[impl.provider_model_id]['output']
                    
                    # Check if price changed by more than 1%
                    if abs(old_input - new_input) / old_input > 0.01 or \
                       abs(old_output - new_output) / old_output > 0.01:
                        changes.append({
                            'model': impl.provider_model_id,
                            'old_prices': {'input': old_input, 'output': old_output},
                            'new_prices': {'input': new_input, 'output': new_output},
                            'change_percent': {
                                'input': ((new_input - old_input) / old_input) * 100,
                                'output': ((new_output - old_output) / old_output) * 100
                            }
                        })
                        
        except Exception as e:
            logger.error(f"Failed to check price changes: {e}")
        finally:
            db.close()
        
        return changes
    
    async def run_price_update(self):
        """Run a single price update cycle"""
        logger.info("Starting price update cycle")
        
        # Fetch latest prices
        all_prices = await self.fetch_openai_prices()
        
        if not all_prices:
            logger.warning("No prices fetched, using known prices")
            all_prices = self.known_prices
        
        # Check for changes
        changes = await self.check_price_changes(all_prices)
        
        if changes:
            logger.info(f"Detected {len(changes)} price changes:")
            for change in changes:
                logger.info(f"  {change['model']}: "
                          f"Input ${change['old_prices']['input']:.4f} -> ${change['new_prices']['input']:.4f} "
                          f"({change['change_percent']['input']:+.1f}%), "
                          f"Output ${change['old_prices']['output']:.4f} -> ${change['new_prices']['output']:.4f} "
                          f"({change['change_percent']['output']:+.1f}%)")
        
        # Update database
        updated = await self.update_prices_in_db(all_prices)
        
        self.last_update = datetime.utcnow()
        logger.info(f"Price update completed. Updated {updated} prices.")
        
        return {
            'updated_count': updated,
            'changes': changes,
            'last_update': self.last_update
        }
    
    async def start_periodic_updates(self):
        """Start periodic price updates"""
        logger.info("Starting periodic price updater service")
        
        while True:
            try:
                await self.run_price_update()
            except Exception as e:
                logger.error(f"Price update failed: {e}")
            
            # Wait for next update
            await asyncio.sleep(self.update_interval.total_seconds())

# Singleton instance
price_updater = PriceUpdaterService()

# Function to run in background
async def start_price_updater():
    """Start the price updater service"""
    await price_updater.start_periodic_updates()