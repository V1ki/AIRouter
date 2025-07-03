#!/usr/bin/env python3
"""
Test script for management API endpoints
"""
import requests
import json
from datetime import datetime

# Base URL for the API
BASE_URL = "http://localhost:8000/api"

def test_providers():
    print("\n=== Testing Provider Endpoints ===")
    
    # Create a provider
    provider_data = {
        "name": "Test Provider",
        "base_url": "https://api.testprovider.com",
        "description": "A test provider"
    }
    
    print("Creating provider...")
    resp = requests.post(f"{BASE_URL}/providers", json=provider_data)
    if resp.status_code == 200:
        provider = resp.json()
        print(f"Created provider: {provider['id']}")
        
        # Get all providers
        print("Getting all providers...")
        resp = requests.get(f"{BASE_URL}/providers")
        print(f"Found {len(resp.json())} providers")
        
        # Update provider
        print("Updating provider...")
        update_data = {"description": "Updated description"}
        resp = requests.put(f"{BASE_URL}/providers/{provider['id']}", json=update_data)
        if resp.status_code == 200:
            print("Provider updated successfully")
        
        # Delete provider
        print("Deleting provider...")
        resp = requests.delete(f"{BASE_URL}/providers/{provider['id']}")
        if resp.status_code == 200:
            print("Provider deleted successfully")
    else:
        print(f"Failed to create provider: {resp.status_code} - {resp.text}")

def test_models():
    print("\n=== Testing Model Endpoints ===")
    
    # Create a model
    model_data = {
        "name": "test-model",
        "description": "A test model",
        "capabilities": ["text-generation", "chat"],
        "family": "test-family"
    }
    
    print("Creating model...")
    resp = requests.post(f"{BASE_URL}/models", json=model_data)
    if resp.status_code == 200:
        model = resp.json()
        print(f"Created model: {model['id']}")
        
        # Get all models
        print("Getting all models...")
        resp = requests.get(f"{BASE_URL}/models")
        print(f"Found {len(resp.json())} models")
        
        # Delete model
        print("Deleting model...")
        resp = requests.delete(f"{BASE_URL}/models/{model['id']}")
        if resp.status_code == 200:
            print("Model deleted successfully")
    else:
        print(f"Failed to create model: {resp.status_code} - {resp.text}")

def test_usage_stats():
    print("\n=== Testing Usage Statistics Endpoints ===")
    
    # Get usage stats
    print("Getting usage stats...")
    resp = requests.get(f"{BASE_URL}/usage/stats")
    if resp.status_code == 200:
        stats = resp.json()
        print(f"Stats response: {json.dumps(stats, indent=2)}")
    else:
        print(f"Failed to get stats: {resp.status_code} - {resp.text}")
    
    # Get usage records
    print("Getting usage records...")
    resp = requests.get(f"{BASE_URL}/usage")
    if resp.status_code == 200:
        usage = resp.json()
        print(f"Found {len(usage)} usage records")
    else:
        print(f"Failed to get usage: {resp.status_code} - {resp.text}")

if __name__ == "__main__":
    print("Testing Management API Endpoints...")
    print(f"Base URL: {BASE_URL}")
    
    try:
        # Test connection
        resp = requests.get(f"{BASE_URL}/providers")
        print("API is accessible!")
        
        test_providers()
        test_models()
        test_usage_stats()
        
    except requests.exceptions.ConnectionError:
        print("Error: Could not connect to API. Make sure the server is running on port 8000.")
    except Exception as e:
        print(f"Error: {e}")