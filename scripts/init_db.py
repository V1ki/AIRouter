#!/usr/bin/env python3
"""
Database initialization script to create all tables
"""
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.db.database import engine, Base
from app.models.provider import ModelProvider, ApiKey, ApiKeyUsage, Model, ModelImplementation, FreeQuota, FreeQuotaUsage
from app.models.response import Response, MessageItem
from app.agents.models.assistant import Assistant
from app.agents.models.thread import Thread
from app.agents.models.message import Message
from app.agents.models.run import Run
from app.agents.models.run_step import RunStep

def init_database():
    """Create all tables in the database"""
    print("Creating database tables...")
    
    # Create all tables
    Base.metadata.create_all(bind=engine)
    
    print("Database tables created successfully!")
    print("\nCreated tables:")
    for table in Base.metadata.sorted_tables:
        print(f"  - {table.name}")

if __name__ == "__main__":
    init_database()
    
    # Ask if user wants to initialize common providers
    response = input("\nDo you want to initialize common AI providers (OpenAI, Claude, Gemini, etc.)? (yes/no): ")
    if response.lower() == 'yes':
        from init_common_providers import init_common_providers
        init_common_providers()