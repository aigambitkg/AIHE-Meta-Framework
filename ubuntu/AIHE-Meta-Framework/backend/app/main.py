"""
AIHE Meta-Framework Backend Application

This is the main FastAPI application for the AIHE Meta-Framework.
It provides REST API endpoints for the AI Ethics assessment framework.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.api import api_router
from app.core.config import settings

# Create FastAPI application
app = FastAPI(
    title="AIHE Meta-Framework API",
    description="REST API for the AI Ethics assessment framework",
    version="2.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_HOSTS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API router
app.include_router(api_router, prefix="/api/v1")

@app.get("/")
async def root():
    """Root endpoint providing basic API information."""
    return JSONResponse({
        "message": "AIHE Meta-Framework API",
        "version": "2.0.0",
        "status": "running",
        "docs": "/docs"
    })

@app.get("/health")
async def health_check():
    """Health check endpoint for monitoring."""
    return JSONResponse({
        "status": "healthy",
        "version": "2.0.0"
    })

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
