from fastapi import APIRouter, FastAPI, Header, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from typing import Any, Dict, List, Optional
from openai.types.model import Model
import os

from app.routers import models, chat, responses, management
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

# Health check endpoint
@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "AI Router"}

# Serve frontend static files if they exist
frontend_dist = os.path.join(os.path.dirname(__file__), "..", "frontend", "dist")
if os.path.exists(frontend_dist):
    # Mount static files
    app.mount("/assets", StaticFiles(directory=os.path.join(frontend_dist, "assets")), name="assets")
    
    # Serve index.html for all non-API routes
    @app.get("/{full_path:path}")
    async def serve_frontend(full_path: str):
        # Don't serve frontend for API routes
        if full_path.startswith("api/") or full_path.startswith("v1/"):
            raise HTTPException(status_code=404, detail="Not found")
        
        # Check if requesting a specific file
        file_path = os.path.join(frontend_dist, full_path)
        if os.path.exists(file_path) and os.path.isfile(file_path):
            return FileResponse(file_path)
        
        # Otherwise serve index.html (for SPA routing)
        return FileResponse(os.path.join(frontend_dist, "index.html"))