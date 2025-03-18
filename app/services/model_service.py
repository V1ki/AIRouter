from typing import List
from sqlalchemy.orm import Session
from app.models.provider import Model as DBModel

class ModelService:
    
    @staticmethod
    def get_models(db: Session) -> List[DBModel]:
        return db.query(DBModel).all()
    
    
    @staticmethod
    def get_model_by_name(db: Session, name: str) -> DBModel:
        return db.query(DBModel).filter(DBModel.name == name).first()