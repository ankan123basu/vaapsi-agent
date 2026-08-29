"""
Recoup Agent Service — FastAPI Application Entry Point.

Exposes:
- /api/* — Dashboard-consumed REST endpoints
- /webhooks/razorpay — Razorpay webhook ingestion endpoint
- /health — Health check
"""

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.api.routes import router as api_router
from app.webhooks.handler import router as webhook_router
from app.database import init_db


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initialize database on startup, cleanup on shutdown."""
    await init_db()
    yield


app = FastAPI(
    title="Recoup Agent Service",
    description="Autonomous Revenue Recovery Agent — detects, diagnoses, and recovers failed payments.",
    version="0.1.0",
    lifespan=lifespan,
)

# CORS — allow the React dashboard to talk to us
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, lock this to the dashboard URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount route groups
app.include_router(api_router, prefix="/api", tags=["Dashboard API"])
app.include_router(webhook_router, prefix="/webhooks", tags=["Webhooks"])


@app.get("/health", tags=["System"])
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "service": "recoup-agent-service",
        "version": "0.1.0",
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host=settings.agent_service_host,
        port=settings.agent_service_port,
        reload=True,
    )
