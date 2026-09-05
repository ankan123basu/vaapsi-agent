"""
Vaapsi (वापसी) Agent Service — FastAPI Application Entry Point.

Exposes:
- /api/* — Dashboard-consumed REST endpoints
- /webhooks/razorpay — Razorpay webhook ingestion endpoint with HMAC-SHA256 & idempotency
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
    title="Vaapsi (वापसी) Agent Service",
    description="Autonomous Revenue Recovery Agent — 8-Node LangGraph StateGraph DAG Engine with Nuisance Suppression, Razorpay APIs & Hinglish Voice Synthesis.",
    version="1.0.0",
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


@app.get("/", tags=["System"])
async def root():
    """Root landing endpoint — returns system status and links to frontend & docs."""
    return {
        "service": "Vaapsi (वापsi) Revenue Recovery Agent Service",
        "status": "running",
        "web_dashboard_url": "http://localhost:5173",
        "api_docs": "http://localhost:8005/docs",
        "health_check": "http://localhost:8005/health",
        "message": "Welcome to Vaapsi API. Open http://localhost:5173 in your browser to access the interactive web dashboard."
    }


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
