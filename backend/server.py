"""
backend/server.py
=================
FinMate AI – Production FastAPI Application Entrypoint
Run with:
    python -m uvicorn backend.server:app --reload --port 8000
"""

from __future__ import annotations
import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from backend.app.core.config import settings
from backend.app.api.router import api_router
from backend.database import init_db
from backend.auth import init_auth_tables

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: ensure SQLite database tables are created
    logger.info("Initializing FinMate AI databases...")
    init_db()
    init_auth_tables()
    logger.info("FinMate AI backend started successfully.")
    yield
    logger.info("FinMate AI backend shutting down.")


app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="Full-stack AI-Powered Personal Finance Assistant REST API",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
)

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API v1 Router
app.include_router(api_router, prefix=settings.API_V1_STR)


@app.get("/", tags=["Health"])
def root():
    return {
        "app": settings.PROJECT_NAME,
        "version": settings.VERSION,
        "status": "online",
        "docs_url": "/docs",
        "api_v1": settings.API_V1_STR,
    }


@app.get("/health", tags=["Health"])
def health_check():
    return {"status": "healthy", "service": "finmate-ai-backend"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("backend.server:app", host="0.0.0.0", port=8000, reload=True)
