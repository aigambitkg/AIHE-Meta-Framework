"""
API routes for assessment management.

This module provides CRUD operations for assessments and related entities.
"""

from typing import List
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.crud import crud_assessment, crud_subdimension_score, crud_organisation
from app.schemas.assessment import (
    Assessment, AssessmentCreate, AssessmentUpdate, AssessmentSummary,
    AssessmentCompletion, AssessmentMetrics,
    SubdimensionScore, SubdimensionScoreUpdate
)

router = APIRouter()


@router.get("/", response_model=List[AssessmentSummary])
def get_assessments(
    skip: int = 0,
    limit: int = 100,
    organisation_id: UUID = None,
    db: Session = Depends(get_db)
):
    """
    Retrieve a list of assessments.
    
    Args:
        skip: Number of records to skip (for pagination)
        limit: Maximum number of records to return
        organisation_id: Filter by organisation ID (optional)
        db: Database session
        
    Returns:
        List of assessment summaries
    """
    if organisation_id:
        assessments = crud_assessment.get_by_organisation(
            db, organisation_id=organisation_id, skip=skip, limit=limit
        )
    else:
        assessments = crud_assessment.get_multi(db, skip=skip, limit=limit)
    
    return assessments


@router.get("/{assessment_id}", response_model=Assessment)
def get_assessment(
    assessment_id: UUID,
    db: Session = Depends(get_db)
):
    """
    Retrieve a specific assessment by ID with all related data.
    
    Args:
        assessment_id: UUID of the assessment
        db: Database session
        
    Returns:
        Assessment details with scores and context factors
        
    Raises:
        HTTPException: If assessment not found
    """
    assessment = crud_assessment.get_with_scores(db, id=assessment_id)
    if not assessment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Assessment not found"
        )
    return assessment


@router.post("/", response_model=Assessment, status_code=status.HTTP_201_CREATED)
def create_assessment(
    assessment_in: AssessmentCreate,
    db: Session = Depends(get_db)
):
    """
    Create a new assessment.
    
    Args:
        assessment_in: Assessment data
        db: Database session
        
    Returns:
        Created assessment
        
    Raises:
        HTTPException: If organisation not found
    """
    # Verify organisation exists
    organisation = crud_organisation.get(db, id=assessment_in.organisation_id)
    if not organisation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Organisation not found"
        )
    
    assessment = crud_assessment.create(db, obj_in=assessment_in)
    return assessment


@router.put("/{assessment_id}", response_model=Assessment)
def update_assessment(
    assessment_id: UUID,
    assessment_in: AssessmentUpdate,
    db: Session = Depends(get_db)
):
    """
    Update an existing assessment.
    
    Args:
        assessment_id: UUID of the assessment
        assessment_in: Updated assessment data
        db: Database session
        
    Returns:
        Updated assessment
        
    Raises:
        HTTPException: If assessment not found
    """
    assessment = crud_assessment.get(db, id=assessment_id)
    if not assessment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Assessment not found"
        )
    
    assessment = crud_assessment.update(db, db_obj=assessment, obj_in=assessment_in)
    return assessment


@router.delete("/{assessment_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_assessment(
    assessment_id: UUID,
    db: Session = Depends(get_db)
):
    """
    Delete an assessment.
    
    Args:
        assessment_id: UUID of the assessment
        db: Database session
        
    Raises:
        HTTPException: If assessment not found
    """
    assessment = crud_assessment.get(db, id=assessment_id)
    if not assessment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Assessment not found"
        )
    
    crud_assessment.remove(db, id=assessment_id)


@router.post("/{assessment_id}/complete", response_model=Assessment)
def complete_assessment(
    assessment_id: UUID,
    completion_data: AssessmentCompletion,
    db: Session = Depends(get_db)
):
    """
    Complete an assessment by providing all scores and context factors.
    
    This endpoint calculates all metrics and marks the assessment as completed.
    
    Args:
        assessment_id: UUID of the assessment
        completion_data: Completion data with scores and context factors
        db: Database session
        
    Returns:
        Completed assessment with calculated metrics
        
    Raises:
        HTTPException: If assessment not found or already completed
    """
    assessment = crud_assessment.get(db, id=assessment_id)
    if not assessment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Assessment not found"
        )
    
    if assessment.status == "COMPLETED":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Assessment is already completed"
        )
    
    # Get organisation archetype for dynamic weighting
    organisation = crud_organisation.get(db, id=assessment.organisation_id)
    archetype = organisation.primary_archetype or "BALANCED_TRANSFORMER"
    
    try:
        completed_assessment = crud_assessment.complete_assessment(
            db,
            assessment_id=assessment_id,
            completion_data=completion_data,
            organisation_archetype=archetype
        )
        return completed_assessment
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.get("/{assessment_id}/metrics", response_model=AssessmentMetrics)
def get_assessment_metrics(
    assessment_id: UUID,
    db: Session = Depends(get_db)
):
    """
    Get calculated metrics for an assessment.
    
    Args:
        assessment_id: UUID of the assessment
        db: Database session
        
    Returns:
        Assessment metrics (EQI, RGI, SI, SBS, Context Score)
        
    Raises:
        HTTPException: If assessment not found
    """
    assessment = crud_assessment.get(db, id=assessment_id)
    if not assessment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Assessment not found"
        )
    
    return AssessmentMetrics(
        overall_rgi=assessment.overall_rgi,
        overall_eqi=assessment.overall_eqi,
        overall_si=assessment.overall_si,
        overall_sbs=assessment.overall_sbs,
        context_score=assessment.context_score
    )


@router.get("/{assessment_id}/scores", response_model=List[SubdimensionScore])
def get_assessment_scores(
    assessment_id: UUID,
    db: Session = Depends(get_db)
):
    """
    Get all subdimension scores for an assessment.
    
    Args:
        assessment_id: UUID of the assessment
        db: Database session
        
    Returns:
        List of subdimension scores
        
    Raises:
        HTTPException: If assessment not found
    """
    assessment = crud_assessment.get(db, id=assessment_id)
    if not assessment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Assessment not found"
        )
    
    scores = crud_subdimension_score.get_by_assessment(db, assessment_id=assessment_id)
    return scores


@router.put("/{assessment_id}/scores/{score_id}", response_model=SubdimensionScore)
def update_subdimension_score(
    assessment_id: UUID,
    score_id: UUID,
    score_update: SubdimensionScoreUpdate,
    db: Session = Depends(get_db)
):
    """
    Update a specific subdimension score.
    
    Args:
        assessment_id: UUID of the assessment
        score_id: UUID of the subdimension score
        score_update: Updated score data
        db: Database session
        
    Returns:
        Updated subdimension score
        
    Raises:
        HTTPException: If assessment or score not found
    """
    # Verify assessment exists
    assessment = crud_assessment.get(db, id=assessment_id)
    if not assessment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Assessment not found"
        )
    
    # Get the score
    score = crud_subdimension_score.get(db, id=score_id)
    if not score or score.assessment_id != assessment_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Subdimension score not found"
        )
    
    # Update with recalculations
    updated_score = crud_subdimension_score.update_with_calculations(
        db, db_obj=score, obj_in=score_update
    )
    
    return updated_score
