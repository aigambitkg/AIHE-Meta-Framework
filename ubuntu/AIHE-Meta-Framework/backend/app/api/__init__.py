"""
API package for the AIHE Meta-Framework.

This package contains all API routes and endpoints.
"""

from fastapi import APIRouter

from app.api.routes import organisations, assessments, dimensions

# Create main API router
api_router = APIRouter()

# Include route modules
api_router.include_router(
    organisations.router,
    prefix="/organisations",
    tags=["organisations"]
)

api_router.include_router(
    assessments.router,
    prefix="/assessments", 
    tags=["assessments"]
)

api_router.include_router(
    dimensions.router,
    prefix="/dimensions",
    tags=["dimensions"]
)
