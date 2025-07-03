from fastapi import APIRouter, FastAPI, Header, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from typing import Any, Dict, List, Optional
from openai.types.model import Model

from app.routers import models,chat,responses,management
from app.agents.router import agents_router

app = FastAPI(
    title="AI Router",
    description="A simple API to route requests to different AI models",
    version="0.1",
    base_path="/api"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # For development; in production, specify exact domains
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

v1_router = APIRouter(prefix="/v1", tags=["v1"])

# 包含子路由器，不再需要为每个路由器添加prefix
v1_router.include_router(models.router)
v1_router.include_router(chat.router)
v1_router.include_router(responses.router)
v1_router.include_router(agents_router)
# 将v1_router添加到主应用
app.include_router(v1_router)

# Include management router directly on app (not under /v1)
app.include_router(management.router)
