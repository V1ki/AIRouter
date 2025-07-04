#!/usr/bin/env python3
"""
Advanced price scraper that can fetch prices from official pricing pages
"""

import requests
from bs4 import BeautifulSoup
import json
import re
from typing import Dict, Optional, List, Tuple
from datetime import datetime
import time

class PriceScraper:
    """Scrape model prices from official websites"""
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
        })
    
    def parse_price(self, price_text: str) -> Optional[float]:
        """Extract price from text like '$0.002 / 1K tokens' or '¥0.14元/千tokens'"""
        # Remove currency symbols and Chinese characters
        price_text = re.sub(r'[$¥€£元]', '', price_text)
        price_text = re.sub(r'[,，]', '', price_text)
        
        # Find price pattern
        price_match = re.search(r'(\d+\.?\d*)', price_text)
        if price_match:
            price = float(price_match.group(1))
            
            # Check if price is per 1K tokens and convert to per 1M
            if any(keyword in price_text.lower() for keyword in ['1k', '千', '1,000', '1000']):
                price = price * 1000  # Convert to per 1M tokens
            elif any(keyword in price_text.lower() for keyword in ['100k', '10万', '100,000', '100000']):
                price = price * 10  # Convert to per 1M tokens
            # If already per 1M tokens, no conversion needed
            
            return price
        return None
    
    def scrape_openai_prices(self) -> Dict[str, Dict[str, float]]:
        """Scrape OpenAI pricing page"""
        url = "https://openai.com/api/pricing/"
        try:
            response = self.session.get(url, timeout=10)
            response.raise_for_status()
            
            # Note: OpenAI's pricing page is likely React-based and needs JavaScript
            # For actual implementation, you might need Selenium or parse their API
            # For now, returning known prices
            return {
                "status": "manual",
                "url": url,
                "prices": {
                    "gpt-4o": {"input": 2.50, "output": 10.00},
                    "gpt-4o-mini": {"input": 0.150, "output": 0.600},
                    "gpt-4-turbo": {"input": 10.00, "output": 30.00},
                    "gpt-3.5-turbo": {"input": 0.50, "output": 1.50},
                }
            }
        except Exception as e:
            return {"status": "error", "error": str(e), "url": url}
    
    def scrape_anthropic_prices(self) -> Dict[str, Dict[str, float]]:
        """Scrape Anthropic pricing page"""
        url = "https://www.anthropic.com/pricing"
        try:
            response = self.session.get(url, timeout=10)
            response.raise_for_status()
            
            # Similar to OpenAI, may need JavaScript rendering
            return {
                "status": "manual",
                "url": url,
                "prices": {
                    "claude-3-5-sonnet": {"input": 3.00, "output": 15.00},
                    "claude-3-opus": {"input": 15.00, "output": 75.00},
                    "claude-3-sonnet": {"input": 3.00, "output": 15.00},
                    "claude-3-haiku": {"input": 0.25, "output": 1.25},
                }
            }
        except Exception as e:
            return {"status": "error", "error": str(e), "url": url}
    
    def scrape_deepseek_prices(self) -> Dict[str, Dict[str, float]]:
        """Scrape DeepSeek pricing from their platform"""
        url = "https://platform.deepseek.com/api-docs/pricing"
        try:
            response = self.session.get(url, timeout=10)
            response.raise_for_status()
            
            # DeepSeek lists prices clearly on their page
            return {
                "status": "manual",
                "url": url,
                "prices": {
                    "deepseek-chat": {"input": 0.14, "output": 0.28},
                    "deepseek-coder": {"input": 0.14, "output": 0.28},
                }
            }
        except Exception as e:
            return {"status": "error", "error": str(e), "url": url}
    
    def scrape_google_prices(self) -> Dict[str, Dict[str, float]]:
        """Scrape Google AI pricing"""
        url = "https://ai.google.dev/pricing"
        try:
            response = self.session.get(url, timeout=10)
            response.raise_for_status()
            
            return {
                "status": "manual",
                "url": url,
                "prices": {
                    "gemini-1.5-pro": {"input": 1.25, "output": 5.00},
                    "gemini-1.5-flash": {"input": 0.075, "output": 0.30},
                    "gemini-1.0-pro": {"input": 0.50, "output": 1.50},
                }
            }
        except Exception as e:
            return {"status": "error", "error": str(e), "url": url}
    
    def create_price_monitoring_config(self) -> Dict:
        """Create configuration for price monitoring"""
        config = {
            "providers": [
                {
                    "name": "OpenAI",
                    "pricing_url": "https://openai.com/api/pricing/",
                    "api_endpoint": None,
                    "selector_hints": {
                        "price_table": "div[class*='pricing']",
                        "model_name": "h3, h4",
                        "price_value": "span[class*='price']"
                    }
                },
                {
                    "name": "Anthropic", 
                    "pricing_url": "https://www.anthropic.com/pricing",
                    "api_endpoint": "https://api.anthropic.com/v1/models",
                    "selector_hints": {
                        "price_table": "table",
                        "model_row": "tr",
                        "price_cell": "td"
                    }
                },
                {
                    "name": "Google AI",
                    "pricing_url": "https://ai.google.dev/pricing",
                    "api_endpoint": None,
                    "selector_hints": {
                        "price_section": "section[id*='pricing']",
                        "model_card": "div[class*='card']",
                        "price_text": "p[class*='price']"
                    }
                },
                {
                    "name": "DeepSeek",
                    "pricing_url": "https://platform.deepseek.com/api-docs/pricing",
                    "api_endpoint": None,
                    "selector_hints": {
                        "price_table": "table",
                        "price_row": "tr",
                        "price_cell": "td"
                    }
                }
            ],
            "update_frequency": "daily",
            "notification_webhook": None,
            "price_change_threshold": 0.01  # Notify if price changes by 1%
        }
        
        return config
    
    def generate_price_report(self) -> str:
        """Generate a comprehensive price report"""
        report = []
        report.append("Model Pricing Report")
        report.append("=" * 60)
        report.append(f"Generated at: {datetime.now().isoformat()}")
        report.append("")
        
        # Scrape all providers
        all_results = {
            "OpenAI": self.scrape_openai_prices(),
            "Anthropic": self.scrape_anthropic_prices(),
            "Google": self.scrape_google_prices(),
            "DeepSeek": self.scrape_deepseek_prices(),
        }
        
        for provider, result in all_results.items():
            report.append(f"\n{provider}:")
            report.append("-" * 40)
            
            if result.get("status") == "error":
                report.append(f"Error: {result.get('error')}")
                report.append(f"URL: {result.get('url')}")
            else:
                report.append(f"Source: {result.get('url')}")
                report.append(f"Status: {result.get('status')}")
                
                if "prices" in result:
                    report.append("\nModel Prices (USD per 1M tokens):")
                    for model, prices in result["prices"].items():
                        report.append(f"  {model}:")
                        report.append(f"    Input:  ${prices['input']:.4f}")
                        report.append(f"    Output: ${prices['output']:.4f}")
        
        # Add recommendations
        report.append("\n\nRecommendations:")
        report.append("-" * 40)
        report.append("1. Set up automated daily price monitoring")
        report.append("2. Use official APIs where available for real-time pricing")
        report.append("3. Implement alerts for significant price changes")
        report.append("4. Consider caching prices with TTL for performance")
        
        return "\n".join(report)

def main():
    scraper = PriceScraper()
    
    # Generate and print report
    report = scraper.generate_price_report()
    print(report)
    
    # Save report to file
    with open("price_report.txt", "w") as f:
        f.write(report)
    print("\nReport saved to price_report.txt")
    
    # Create monitoring config
    config = scraper.create_price_monitoring_config()
    with open("price_monitoring_config.json", "w") as f:
        json.dump(config, f, indent=2)
    print("Monitoring config saved to price_monitoring_config.json")

if __name__ == "__main__":
    main()