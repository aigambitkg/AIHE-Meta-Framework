"""
API routes for dimension and subdimension management.

This module provides operations for the 8 dimensions and 16 subdimensions
that form the core assessment structure.
"""

from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.dimension import Dimension, Subdimension
from app.schemas.dimension import DimensionResponse, SubdimensionResponse

router = APIRouter()


@router.get("/", response_model=List[DimensionResponse])
def get_dimensions(db: Session = Depends(get_db)):
    """
    Retrieve all dimensions with their subdimensions.
    
    Args:
        db: Database session
        
    Returns:
        List of dimensions with subdimensions
    """
    dimensions = db.query(Dimension).all()
    return dimensions


@router.get("/{dimension_id}", response_model=DimensionResponse)
def get_dimension(
    dimension_id: str,
    db: Session = Depends(get_db)
):
    """
    Retrieve a specific dimension by ID with its subdimensions.
    
    Args:
        dimension_id: Dimension ID (e.g., 'D1', 'D2', etc.)
        db: Database session
        
    Returns:
        Dimension details with subdimensions
        
    Raises:
        HTTPException: If dimension not found
    """
    dimension = db.query(Dimension).filter(
        Dimension.dimension_id == dimension_id
    ).first()
    
    if not dimension:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Dimension {dimension_id} not found"
        )
    
    return dimension


@router.get("/{dimension_id}/subdimensions", response_model=List[SubdimensionResponse])
def get_subdimensions(
    dimension_id: str,
    db: Session = Depends(get_db)
):
    """
    Retrieve all subdimensions for a specific dimension.
    
    Args:
        dimension_id: Dimension ID (e.g., 'D1', 'D2', etc.)
        db: Database session
        
    Returns:
        List of subdimensions for the dimension
        
    Raises:
        HTTPException: If dimension not found
    """
    # Verify dimension exists
    dimension = db.query(Dimension).filter(
        Dimension.dimension_id == dimension_id
    ).first()
    
    if not dimension:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Dimension {dimension_id} not found"
        )
    
    subdimensions = db.query(Subdimension).filter(
        Subdimension.parent_dimension_id == dimension_id
    ).all()
    
    return subdimensions


@router.get("/subdimensions/", response_model=List[SubdimensionResponse])
def get_all_subdimensions(db: Session = Depends(get_db)):
    """
    Retrieve all subdimensions across all dimensions.
    
    Args:
        db: Database session
        
    Returns:
        List of all subdimensions
    """
    subdimensions = db.query(Subdimension).all()
    return subdimensions


@router.get("/subdimensions/{subdimension_id}", response_model=SubdimensionResponse)
def get_subdimension(
    subdimension_id: str,
    db: Session = Depends(get_db)
):
    """
    Retrieve a specific subdimension by ID.
    
    Args:
        subdimension_id: Subdimension ID (e.g., 'D1.1', 'D1.2', etc.)
        db: Database session
        
    Returns:
        Subdimension details
        
    Raises:
        HTTPException: If subdimension not found
    """
    subdimension = db.query(Subdimension).filter(
        Subdimension.subdimension_id == subdimension_id
    ).first()
    
    if not subdimension:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Subdimension {subdimension_id} not found"
        )
    
    return subdimension
