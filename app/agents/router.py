from fastapi import APIRouter

from app.agents.routers import (
    assistants_router,
    threads_router,
    messages_router,
    runs_router
)

# Create main agents router
agents_router = APIRouter(tags=["agents"])

# Include all sub-routers
agents_router.include_router(assistants_router)
agents_router.include_router(threads_router)

# Messages router doesn't have a prefix as it's nested under threads
agents_router.include_router(messages_router)

# Runs router doesn't have a prefix as it's nested under threads
agents_router.include_router(runs_router)