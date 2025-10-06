"""
API routes for organisation management.

This module provides CRUD operations for organisations.
"""

from typing import List
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.crud import crud_organisation
from app.schemas.organisation import (
    Organisation, OrganisationCreate, OrganisationUpdate, 
    OrganisationSummary, OrganisationArchetype
)

router = APIRouter()


@router.get("/", response_model=List[OrganisationSummary])
def get_organisations(
    skip: int = 0,
    limit: int = 100,
    active_only: bool = True,
    db: Session = Depends(get_db)
):
    """
    Retrieve a list of organisations.
    
    Args:
        skip: Number of records to skip (for pagination)
        limit: Maximum number of records to return
        active_only: Whether to return only active organisations
        db: Database session
        
    Returns:
        List of organisation summaries
    """
    organisations = crud_organisation.get_multi(
        db, skip=skip, limit=limit, active_only=active_only
    )
    return organisations


@router.get("/{organisation_id}", response_model=Organisation)
def get_organisation(
    organisation_id: UUID,
    db: Session = Depends(get_db)
):
    """
    Retrieve a specific organisation by ID.
    
    Args:
        organisation_id: UUID of the organisation
        db: Database session
        
    Returns:
        Organisation details
        
    Raises:
        HTTPException: If organisation not found
    """
    organisation = crud_organisation.get(db, id=organisation_id)
    if not organisation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Organisation not found"
        )
    return organisation


@router.post("/", response_model=Organisation, status_code=status.HTTP_201_CREATED)
def create_organisation(
    organisation_in: OrganisationCreate,
    db: Session = Depends(get_db)
):
    """
    Create a new organisation.
    
    Args:
        organisation_in: Organisation data
        db: Database session
        
    Returns:
        Created organisation
    """
    organisation = crud_organisation.create(db, obj_in=organisation_in)
    return organisation


@router.put("/{organisation_id}", response_model=Organisation)
def update_organisation(
    organisation_id: UUID,
    organisation_in: OrganisationUpdate,
    db: Session = Depends(get_db)
):
    """
    Update an existing organisation.
    
    Args:
        organisation_id: UUID of the organisation
        organisation_in: Updated organisation data
        db: Database session
        
    Returns:
        Updated organisation
        
    Raises:
        HTTPException: If organisation not found
    """
    organisation = crud_organisation.get(db, id=organisation_id)
    if not organisation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Organisation not found"
        )
    
    organisation = crud_organisation.update(db, db_obj=organisation, obj_in=organisation_in)
    return organisation


@router.delete("/{organisation_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_organisation(
    organisation_id: UUID,
    db: Session = Depends(get_db)
):
    """
    Delete an organisation (soft delete - sets active=False).
    
    Args:
        organisation_id: UUID of the organisation
        db: Database session
        
    Raises:
        HTTPException: If organisation not found
    """
    organisation = crud_organisation.get(db, id=organisation_id)
    if not organisation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Organisation not found"
        )
    
    crud_organisation.remove(db, id=organisation_id)


@router.get("/{organisation_id}/archetype", response_model=OrganisationArchetype)
def get_organisation_archetype(
    organisation_id: UUID,
    db: Session = Depends(get_db)
):
    """
    Get the archetype information for an organisation.
    
    Args:
        organisation_id: UUID of the organisation
        db: Database session
        
    Returns:
        Organisation archetype information
        
    Raises:
        HTTPException: If organisation not found
    """
    organisation = crud_organisation.get(db, id=organisation_id)
    if not organisation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Organisation not found"
        )
    
    return OrganisationArchetype(
        primary_archetype=organisation.primary_archetype,
        archetype_confidence_score=organisation.archetype_confidence_score,
        archetype_determined_at=organisation.archetype_determined_at,
        archetype_determination_method=organisation.archetype_determination_method
    )


@router.put("/{organisation_id}/archetype", response_model=OrganisationArchetype)
def update_organisation_archetype(
    organisation_id: UUID,
    archetype_in: OrganisationArchetype,
    db: Session = Depends(get_db)
):
    """
    Update the archetype information for an organisation.
    
    Args:
        organisation_id: UUID of the organisation
        archetype_in: Updated archetype data
        db: Database session
        
    Returns:
        Updated archetype information
        
    Raises:
        HTTPException: If organisation not found
    """
    organisation = crud_organisation.get(db, id=organisation_id)
    if not organisation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Organisation not found"
        )
    
    # Update archetype fields
    update_data = archetype_in.dict(exclude_unset=True)
    organisation = crud_organisation.update(db, db_obj=organisation, obj_in=update_data)
    
    return OrganisationArchetype(
        primary_archetype=organisation.primary_archetype,
        archetype_confidence_score=organisation.archetype_confidence_score,
        archetype_determined_at=organisation.archetype_determined_at,
        archetype_determination_method=organisation.archetype_determination_method
    )
