from typing import Any, Dict, List, Tuple
from sqlalchemy.orm import Session
from datetime import datetime, timezone
from app.models.provider import Model as DBModel, ApiKeyUsage as DBApiKeyUsage, ModelImplementation, ApiKey, FreeQuota, FreeQuotaUsage

class ModelService:
    
    @staticmethod
    def get_models(db: Session) -> List[DBModel]:
        return db.query(DBModel).all()
    
    
    @staticmethod
    def get_model_by_name(db: Session, name: str) -> DBModel:
        return db.query(DBModel).filter(DBModel.name == name).first()
    
    
    @staticmethod
    def save_usage(db: Session, 
                   api_key_id: str,
                   model_implementation_id: str,
                   usage: Dict[str, Any]):
        """
        保存API密钥使用记录到数据库"""
        db_usage = DBApiKeyUsage(
            api_key_id=api_key_id,
            model_implementation_id=model_implementation_id,
            prompt_tokens=usage.get("prompt_tokens"),
            completion_tokens=usage.get("completion_tokens"),
            total_tokens=usage.get("total_tokens"),
            prompt_tokens_details=usage.get("prompt_tokens_details"),
            completion_tokens_details=usage.get("completion_tokens_details"),
            timestamp=datetime.now(timezone.utc)
        )
        db.add(db_usage)
        db.commit()
        
        
    @staticmethod
    def get_usage(db: Session, 
                  model_implementation_id: str,
                  start_date: datetime,
                  end_date: datetime
                  ) -> Tuple[float, float]:
        """
        获取指定模型实现在指定时间范围内的使用记录
        
        参数:
            db: 数据库会话
            model_implementation_id: 模型实现ID
            start_date: 开始时间
            end_date: 结束时间
            
        返回:
            Tuple[float, float]: 总 token 数, 价格
        """
        usages = db.query(DBApiKeyUsage).filter(
            DBApiKeyUsage.model_implementation_id == model_implementation_id,
            DBApiKeyUsage.timestamp >= start_date,
            DBApiKeyUsage.timestamp <= end_date
        ).all()
        
        # 获取模型实现的价格信息
        model_implementation = db.query(ModelImplementation).filter(
            ModelImplementation.id == model_implementation_id
        ).first()
        
        total_tokens = sum(usage.total_tokens for usage in usages)
        total_price = 0.0
        
        if model_implementation and model_implementation.pricing_info:
            pricing_info = model_implementation.pricing_info
            # 获取输入和输出的价格（通常是每1000个token的价格）
            input_price_per_1k = float(pricing_info.get('input_price', 0))
            output_price_per_1k = float(pricing_info.get('output_price', 0))
            
            # 计算总价格
            for usage in usages:
                prompt_cost = (usage.prompt_tokens / 1000) * input_price_per_1k
                completion_cost = (usage.completion_tokens / 1000) * output_price_per_1k
                total_price += prompt_cost + completion_cost
        
        return total_tokens, total_price
    
    
    @staticmethod
    def get_best_implementation(db: Session, model_implementations: List[ModelImplementation]) -> tuple[ModelImplementation, ApiKey]:
        """
        获取最佳模型实现及其对应的API密钥
        
        优先级条件:
        1. 按照sort_order排序（值越小优先级越高）
        2. 如果有免费额度可用，优先使用有免费额度的实现
        3. 如果免费额度都用完，则选择价格最便宜的实现
        
        返回:
            tuple: (best_implementation, best_api_key)
        """
        if not model_implementations:
            return None, None
            
        # 按照sort_order排序（升序）
        sorted_implementations = sorted(model_implementations, key=lambda impl: impl.sort_order)
        
        best_implementation = None
        best_api_key = None
        lowest_price = float('inf')
        
        # 首先检查有没有免费额度可用的实现
        for implementation in sorted_implementations:
            provider = implementation.provider
            
            # 获取该provider的API keys，按sort_order排序
            api_keys = db.query(ApiKey).filter(ApiKey.provider_id == provider.id)\
                        .order_by(ApiKey.sort_order).all()
            
            if not api_keys:
                continue
                
            # 查找该实现相关的免费额度
            free_quota = db.query(FreeQuota).filter(
                (FreeQuota.provider_id == provider.id) & 
                ((FreeQuota.model_implementation_id == implementation.id) | 
                 (FreeQuota.model_implementation_id == None))
            ).first()
            
            # 如果有免费额度配置
            if free_quota:
                for api_key in api_keys:
                    # 检查该API key的免费额度使用情况
                    
                    quota_usage = ModelService.get_usage(db, implementation.id, free_quota.reset_period, datetime.now(timezone.utc))
                    
                    # 如果没有使用记录或者还有剩余额度
                    if not quota_usage or quota_usage.used_amount < free_quota.amount:
                        return implementation, api_key
        
        # 如果没有免费额度可用，选择价格最便宜的实现
        for implementation in sorted_implementations:
            # 从pricing_info中获取价格信息
            pricing_info = implementation.pricing_info or {}
            
            # 获取输入和输出的价格（假设pricing_info中有这些字段）
            # 如果没有价格信息，则使用一个很大的值表示无限大
            input_price = float(pricing_info.get('input_price', 'inf'))
            output_price = float(pricing_info.get('output_price', 'inf'))
            
            # 计算一个简单的价格衡量值（可以根据实际需求调整）
            # 这里我们简单地将输入和输出价格加权平均
            price_measure = (input_price + output_price * 2) / 3  # 输出通常更贵，给予更高权重
            
            provider = implementation.provider
            api_keys = db.query(ApiKey).filter(ApiKey.provider_id == provider.id)\
                        .order_by(ApiKey.sort_order).all()
            
            if api_keys and price_measure < lowest_price:
                lowest_price = price_measure
                best_implementation = implementation
                best_api_key = api_keys[0]  # 选择按sort_order排序的第一个key
        
        # 如果没有合适的实现，返回按sort_order排序的第一个实现和它的第一个API key
        if not best_implementation and sorted_implementations:
            first_impl = sorted_implementations[0]
            provider = first_impl.provider
            api_keys = db.query(ApiKey).filter(ApiKey.provider_id == provider.id)\
                       .order_by(ApiKey.sort_order).all()
            
            if api_keys:
                return first_impl, api_keys[0]
        
        return best_implementation, best_api_key
        
