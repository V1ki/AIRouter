#!/usr/bin/env python3
"""
Initialize database with common AI providers and models
"""
import sys
import os
import uuid
import json

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from app.db.database import SessionLocal, engine
from app.models.provider import ModelProvider, Model, ModelImplementation, FreeQuotaType
from datetime import datetime, timezone

def load_models_config():
    """Load models configuration from JSON file"""
    config_path = os.path.join(os.path.dirname(__file__), '../config/models_config.json')
    try:
        if os.path.exists(config_path):
            with open(config_path, 'r') as f:
                config = json.load(f)
                print(f"Loaded configuration for {len(config.get('providers', {}))} providers and {len(config.get('models', {}))} models")
                return config
        else:
            print(f"Warning: Models config not found at {config_path}")
            return {"providers": {}, "models": {}}
    except Exception as e:
        print(f"Error loading models config: {e}")
        return {"providers": {}, "models": {}}

def init_common_providers():
    """Initialize common AI providers and models"""
    db = SessionLocal()
    
    # Load models configuration
    config = load_models_config()
    
    try:
        # Create providers from config
        providers = {}
        for provider_name, provider_data in config.get('providers', {}).items():
            # Check if provider already exists
            existing_provider = db.query(ModelProvider).filter_by(name=provider_name).first()
            
            if existing_provider:
                print(f"Provider '{provider_name}' already exists, skipping...")
                providers[provider_name] = existing_provider
            else:
                # Map free_quota_type string to enum
                free_quota_type = None
                if provider_data.get('free_quota_type'):
                    free_quota_type_str = provider_data['free_quota_type']
                    free_quota_type = getattr(FreeQuotaType, free_quota_type_str, None)
                
                provider = ModelProvider(
                    name=provider_name,
                    base_url=provider_data['base_url'],
                    description=provider_data['description'],
                    free_quota_type=free_quota_type
                )
                db.add(provider)
                providers[provider_name] = provider
                print(f"Created provider: {provider_name}")
        
        db.flush()
        
        # Create models from config
        models = {}
        for model_name, model_data in config.get('models', {}).items():
            # Check if model already exists
            existing_model = db.query(Model).filter_by(name=model_name).first()
            
            if existing_model:
                print(f"Model '{model_name}' already exists, skipping...")
                models[model_name] = existing_model
            else:
                model = Model(
                    name=model_name,
                    display_name=model_data.get('display_name', model_name),
                    model_type=model_data.get('model_type', 'chat'),
                    capabilities=model_data.get('capabilities', ['text']),
                    is_multimodal=model_data.get('is_multimodal', False)
                )
                db.add(model)
                models[model_name] = model
                print(f"Created model: {model_name}")
        
        db.flush()
        
        # Create model implementations from config
        implementation_count = 0
        for provider_name, provider_data in config.get('providers', {}).items():
            if provider_name not in providers:
                continue
                
            for model_name, impl_data in provider_data.get('models', {}).items():
                if model_name not in models:
                    print(f"Warning: Model '{model_name}' not found in models config, skipping implementation...")
                    continue
                
                # Check if implementation already exists
                existing_impl = db.query(ModelImplementation).filter_by(
                    provider_id=providers[provider_name].id,
                    model_id=models[model_name].id
                ).first()
                
                if existing_impl:
                    print(f"Implementation for '{model_name}' on '{provider_name}' already exists, skipping...")
                else:
                    pricing_info = {
                        "input_price": impl_data['pricing']['input'],
                        "output_price": impl_data['pricing']['output']
                    }
                    
                    implementation = ModelImplementation(
                        provider_id=providers[provider_name].id,
                        model_id=models[model_name].id,
                        provider_model_id=impl_data['provider_model_id'],
                        context_window=impl_data.get('context_window', 4096),
                        pricing_info=pricing_info,
                        is_available=True,
                        sort_order=0
                    )
                    db.add(implementation)
                    implementation_count += 1
                    print(f"Created implementation: {model_name} on {provider_name}")
        
        db.commit()
        print("\nSuccessfully initialized providers and models from config!")
        
        # Print summary
        print(f"\nCreated {len(providers)} providers")
        print(f"Created {len(models)} models")
        print(f"Created {implementation_count} model implementations")
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    init_common_providers()