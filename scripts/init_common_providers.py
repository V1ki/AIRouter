#!/usr/bin/env python3
"""
Initialize database with common AI providers and models
"""
import sys
import os
import uuid

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from app.db.database import SessionLocal, engine
from app.models.provider import ModelProvider, Model, ModelImplementation, FreeQuotaType
from datetime import datetime, timezone

def init_common_providers():
    """Initialize common AI providers and models"""
    db = SessionLocal()
    
    try:
        # Define common providers
        providers_data = [
            {
                "name": "OpenAI",
                "base_url": "https://api.openai.com/v1",
                "description": "OpenAI official API",
                "free_quota_type": None
            },
            {
                "name": "Azure OpenAI",
                "base_url": "https://YOUR-RESOURCE-NAME.openai.azure.com",
                "description": "Microsoft Azure OpenAI Service",
                "free_quota_type": None
            },
            {
                "name": "Google AI",
                "base_url": "https://generativelanguage.googleapis.com/v1beta",
                "description": "Google Gemini API",
                "free_quota_type": None
            },
            {
                "name": "Anthropic",
                "base_url": "https://api.anthropic.com/v1",
                "description": "Anthropic Claude API",
                "free_quota_type": None
            },
            {
                "name": "DeepSeek",
                "base_url": "https://api.deepseek.com/v1",
                "description": "DeepSeek API",
                "free_quota_type": FreeQuotaType.SHARED_TOKENS
            },
            {
                "name": "阿里云百炼",
                "base_url": "https://dashscope.aliyuncs.com/compatible-mode/v1",
                "description": "Alibaba Cloud AI Platform",
                "free_quota_type": FreeQuotaType.PER_MODEL_TOKENS
            },
            {
                "name": "智谱AI",
                "base_url": "https://open.bigmodel.cn/api/paas/v4",
                "description": "Zhipu AI GLM models",
                "free_quota_type": FreeQuotaType.SHARED_TOKENS
            },
            {
                "name": "百度千帆",
                "base_url": "https://aip.baidubce.com/rpc/2.0/ai_custom/v1",
                "description": "Baidu Qianfan Platform",
                "free_quota_type": FreeQuotaType.PER_MODEL_TOKENS
            },
            {
                "name": "讯飞星火",
                "base_url": "https://spark-api-open.xf-yun.com/v1",
                "description": "iFlytek Spark API",
                "free_quota_type": FreeQuotaType.SHARED_TOKENS
            },
            {
                "name": "字节跳动",
                "base_url": "https://ark.cn-beijing.volces.com/api/v3",
                "description": "ByteDance Doubao API",
                "free_quota_type": FreeQuotaType.PER_MODEL_TOKENS
            },
            {
                "name": "硅基流动",
                "base_url": "https://api.siliconflow.cn/v1",
                "description": "SiliconFlow API",
                "free_quota_type": FreeQuotaType.CREDIT
            },
            {
                "name": "Moonshot",
                "base_url": "https://api.moonshot.cn/v1",
                "description": "Moonshot AI Kimi",
                "free_quota_type": FreeQuotaType.SHARED_TOKENS
            }
        ]
        
        # Create providers
        providers = {}
        for provider_data in providers_data:
            # Check if provider with this base_url already exists
            existing_provider = db.query(ModelProvider).filter_by(base_url=provider_data["base_url"]).first()
            if existing_provider:
                print(f"Provider '{provider_data['name']}' with base_url '{provider_data['base_url']}' already exists, skipping...")
                providers[provider_data["name"]] = existing_provider
            else:
                provider = ModelProvider(**provider_data)
                db.add(provider)
                providers[provider_data["name"]] = provider
        
        db.flush()
        
        # Define common models
        models_data = [
            # GPT Models
            {
                "name": "gpt-4o",
                "description": "Most capable GPT-4 Omni model for complex tasks",
                "capabilities": ["chat", "function_calling", "vision"],
                "family": "gpt-4"
            },
            {
                "name": "gpt-4o-mini",
                "description": "Small, affordable, intelligent model for fast tasks",
                "capabilities": ["chat", "function_calling", "vision"],
                "family": "gpt-4"
            },
            {
                "name": "gpt-4-turbo",
                "description": "GPT-4 Turbo with vision capabilities",
                "capabilities": ["chat", "function_calling", "vision"],
                "family": "gpt-4"
            },
            {
                "name": "gpt-3.5-turbo",
                "description": "Fast, inexpensive model for simple tasks",
                "capabilities": ["chat", "function_calling"],
                "family": "gpt-3.5"
            },
            # Claude Models
            {
                "name": "claude-3-opus",
                "description": "Most powerful Claude model for complex tasks",
                "capabilities": ["chat", "vision"],
                "family": "claude-3"
            },
            {
                "name": "claude-3-sonnet",
                "description": "Balanced Claude model for general tasks",
                "capabilities": ["chat", "vision"],
                "family": "claude-3"
            },
            {
                "name": "claude-3-haiku",
                "description": "Fast Claude model for simple tasks",
                "capabilities": ["chat", "vision"],
                "family": "claude-3"
            },
            {
                "name": "claude-3.5-sonnet",
                "description": "Latest Claude 3.5 Sonnet model",
                "capabilities": ["chat", "vision"],
                "family": "claude-3.5"
            },
            # Gemini Models
            {
                "name": "gemini-1.5-pro",
                "description": "Advanced Gemini model with large context window",
                "capabilities": ["chat", "vision", "function_calling"],
                "family": "gemini"
            },
            {
                "name": "gemini-1.5-flash",
                "description": "Fast Gemini model for quick responses",
                "capabilities": ["chat", "vision", "function_calling"],
                "family": "gemini"
            },
            {
                "name": "gemini-2.0-flash-exp",
                "description": "Experimental Gemini 2.0 Flash model",
                "capabilities": ["chat", "vision", "function_calling"],
                "family": "gemini"
            },
            # DeepSeek Models
            {
                "name": "deepseek-chat",
                "description": "DeepSeek chat model",
                "capabilities": ["chat", "function_calling"],
                "family": "deepseek"
            },
            {
                "name": "deepseek-coder",
                "description": "DeepSeek model optimized for coding",
                "capabilities": ["chat", "code"],
                "family": "deepseek"
            },
            # Chinese Models
            {
                "name": "qwen-max",
                "description": "Alibaba Qwen Max model",
                "capabilities": ["chat", "function_calling"],
                "family": "qwen"
            },
            {
                "name": "qwen-plus",
                "description": "Alibaba Qwen Plus model",
                "capabilities": ["chat", "function_calling"],
                "family": "qwen"
            },
            {
                "name": "qwen-turbo",
                "description": "Alibaba Qwen Turbo model",
                "capabilities": ["chat"],
                "family": "qwen"
            },
            {
                "name": "glm-4",
                "description": "Zhipu GLM-4 model",
                "capabilities": ["chat", "function_calling"],
                "family": "glm"
            },
            {
                "name": "glm-4v",
                "description": "Zhipu GLM-4 with vision",
                "capabilities": ["chat", "vision", "function_calling"],
                "family": "glm"
            },
            {
                "name": "moonshot-v1",
                "description": "Moonshot Kimi model",
                "capabilities": ["chat"],
                "family": "moonshot"
            },
            {
                "name": "ernie-4.0",
                "description": "Baidu ERNIE 4.0 model",
                "capabilities": ["chat", "function_calling"],
                "family": "ernie"
            },
            {
                "name": "spark-4.0-ultra",
                "description": "iFlytek Spark 4.0 Ultra model",
                "capabilities": ["chat"],
                "family": "spark"
            },
            {
                "name": "doubao-pro",
                "description": "ByteDance Doubao Pro model",
                "capabilities": ["chat"],
                "family": "doubao"
            }
        ]
        
        # Create models
        models = {}
        for model_data in models_data:
            # Check if model already exists
            existing_model = db.query(Model).filter_by(name=model_data["name"]).first()
            if existing_model:
                print(f"Model '{model_data['name']}' already exists, skipping...")
                models[model_data["name"]] = existing_model
            else:
                model = Model(**model_data)
                db.add(model)
                models[model_data["name"]] = model
        
        db.flush()
        
        # Define model implementations (provider-specific)
        implementations_data = [
            # OpenAI implementations
            {"provider": "OpenAI", "model": "gpt-4o", "provider_model_id": "gpt-4o", "context_window": 128000, 
             "pricing_info": {"input_price": 2500, "output_price": 10000}},  # per 1M tokens
            {"provider": "OpenAI", "model": "gpt-4o-mini", "provider_model_id": "gpt-4o-mini", "context_window": 128000,
             "pricing_info": {"input_price": 150, "output_price": 600}},  # per 1M tokens
            {"provider": "OpenAI", "model": "gpt-4-turbo", "provider_model_id": "gpt-4-turbo", "context_window": 128000,
             "pricing_info": {"input_price": 10000, "output_price": 30000}},  # per 1M tokens
            {"provider": "OpenAI", "model": "gpt-3.5-turbo", "provider_model_id": "gpt-3.5-turbo", "context_window": 16385,
             "pricing_info": {"input_price": 500, "output_price": 1500}},  # per 1M tokens
            
            # Anthropic implementations
            {"provider": "Anthropic", "model": "claude-3-opus", "provider_model_id": "claude-3-opus-20240229", "context_window": 200000,
             "pricing_info": {"input_price": 15000, "output_price": 75000}},  # per 1M tokens
            {"provider": "Anthropic", "model": "claude-3-sonnet", "provider_model_id": "claude-3-sonnet-20240229", "context_window": 200000,
             "pricing_info": {"input_price": 3000, "output_price": 15000}},  # per 1M tokens
            {"provider": "Anthropic", "model": "claude-3-haiku", "provider_model_id": "claude-3-haiku-20240307", "context_window": 200000,
             "pricing_info": {"input_price": 250, "output_price": 1250}},  # per 1M tokens
            {"provider": "Anthropic", "model": "claude-3.5-sonnet", "provider_model_id": "claude-3-5-sonnet-20241022", "context_window": 200000,
             "pricing_info": {"input_price": 3000, "output_price": 15000}},  # per 1M tokens
            
            # Google implementations
            {"provider": "Google AI", "model": "gemini-1.5-pro", "provider_model_id": "gemini-1.5-pro", "context_window": 2097152,
             "pricing_info": {"input_price": 1250, "output_price": 5000}},  # per 1M tokens
            {"provider": "Google AI", "model": "gemini-1.5-flash", "provider_model_id": "gemini-1.5-flash", "context_window": 1048576,
             "pricing_info": {"input_price": 75, "output_price": 300}},  # per 1M tokens
            {"provider": "Google AI", "model": "gemini-2.0-flash-exp", "provider_model_id": "gemini-2.0-flash-exp", "context_window": 1048576,
             "pricing_info": {"input_price": 0, "output_price": 0}},  # Free during experimental phase
            
            # DeepSeek implementations
            {"provider": "DeepSeek", "model": "deepseek-chat", "provider_model_id": "deepseek-chat", "context_window": 128000,
             "pricing_info": {"input_price": 140, "output_price": 280}},  # per 1M tokens
            {"provider": "DeepSeek", "model": "deepseek-coder", "provider_model_id": "deepseek-coder", "context_window": 128000,
             "pricing_info": {"input_price": 140, "output_price": 280}},  # per 1M tokens
            
            # Alibaba implementations
            {"provider": "阿里云百炼", "model": "qwen-max", "provider_model_id": "qwen-max", "context_window": 30000,
             "pricing_info": {"input_price": 20, "output_price": 60}},  # per 1M tokens
            {"provider": "阿里云百炼", "model": "qwen-plus", "provider_model_id": "qwen-plus", "context_window": 130000,
             "pricing_info": {"input_price": 0.8, "output_price": 2}},  # per 1M tokens
            {"provider": "阿里云百炼", "model": "qwen-turbo", "provider_model_id": "qwen-turbo", "context_window": 130000,
             "pricing_info": {"input_price": 0.3, "output_price": 0.6}},  # per 1M tokens
            
            # Zhipu implementations
            {"provider": "智谱AI", "model": "glm-4", "provider_model_id": "glm-4", "context_window": 128000,
             "pricing_info": {"input_price": 100, "output_price": 100}},  # per 1M tokens
            {"provider": "智谱AI", "model": "glm-4v", "provider_model_id": "glm-4v", "context_window": 8192,
             "pricing_info": {"input_price": 100, "output_price": 100}},  # per 1M tokens
            
            # Moonshot implementations
            {"provider": "Moonshot", "model": "moonshot-v1", "provider_model_id": "moonshot-v1-128k", "context_window": 128000,
             "pricing_info": {"input_price": 60, "output_price": 60}},  # per 1M tokens
            
            # SiliconFlow implementations (offering multiple models)
            {"provider": "硅基流动", "model": "qwen-max", "provider_model_id": "Qwen/Qwen2.5-72B-Instruct", "context_window": 32768,
             "pricing_info": {"input_price": 0, "output_price": 0}},  # Often free
            {"provider": "硅基流动", "model": "glm-4", "provider_model_id": "THUDM/glm-4-9b-chat", "context_window": 128000,
             "pricing_info": {"input_price": 0, "output_price": 0}},  # Often free
            {"provider": "硅基流动", "model": "deepseek-chat", "provider_model_id": "deepseek-ai/DeepSeek-V2.5", "context_window": 128000,
             "pricing_info": {"input_price": 0, "output_price": 0}},  # Often free
        ]
        
        # Create implementations
        implementation_count = 0
        for impl_data in implementations_data:
            provider_name = impl_data.pop("provider")
            model_name = impl_data.pop("model")
            
            if provider_name in providers and model_name in models:
                # Check if implementation already exists
                existing_impl = db.query(ModelImplementation).filter_by(
                    provider_id=providers[provider_name].id,
                    model_id=models[model_name].id
                ).first()
                
                if existing_impl:
                    print(f"Implementation for '{model_name}' on '{provider_name}' already exists, skipping...")
                else:
                    implementation = ModelImplementation(
                        provider_id=providers[provider_name].id,
                        model_id=models[model_name].id,
                        is_available=True,
                        sort_order=0,
                        **impl_data
                    )
                    db.add(implementation)
                    implementation_count += 1
        
        db.commit()
        print("Successfully initialized common providers and models!")
        
        # Print summary
        print(f"\nCreated {len(providers)} providers:")
        for name in providers:
            print(f"  - {name}")
        
        print(f"\nCreated {len(models)} models:")
        for name in models:
            print(f"  - {name}")
        
        print(f"\nCreated {implementation_count} model implementations")
        
    except Exception as e:
        print(f"Error: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    init_common_providers()