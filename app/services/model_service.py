from typing import Any, Dict, List
from sqlalchemy.orm import Session
from datetime import datetime, timezone
from app.models.provider import Model as DBModel, ApiKeyUsage as DBApiKeyUsage

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