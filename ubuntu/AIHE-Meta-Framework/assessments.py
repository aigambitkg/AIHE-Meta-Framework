"""
API routes for assessment management with complete calculation logic.

This module provides CRUD operations for assessments and implements
the full AIHE calculation logic from the 53-page specification.
"""

from typing import List, Dict, Any
from uuid import UUID
from decimal import Decimal

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.calculations import (
    AIHECalculationEngine, DynamicWeightingEngine, GapAnalysisEngine, 
    Archetyp, DimensionScore, ContextFactor
)
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
    Complete an assessment using the full AIHE calculation logic.
    
    This endpoint implements the complete calculation logic from the 53-page specification:
    - EQI (Equilibrium Quality Index): 1 - (Summe aller |Gaps|) / 24.0
    - RGI (Reifegrad-Index): Gewichtete Summe der Ist-Werte / 4.0
    - SI (Spannungsindex): Gewichtete Spannungen zwischen 12 Dimensionspaaren / 6.0
    - SBS (System Balance Score): (EQI + (1-SI) + RGI) / 3
    - Context Score: Gewichtete Summe von 10 Faktoren / 3.0
    - Dynamic weighting with 8 rules
    
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
    
    # Get organisation for archetype and KMU status
    organisation = crud_organisation.get(db, id=assessment.organisation_id)
    archetype = getattr(organisation, 'primary_archetype', 'BALANCED_TRANSFORMER')
    is_kmu = getattr(organisation, 'is_kmu', False)
    
    try:
        # Calculate metrics using the complete specification logic
        calculated_metrics = calculate_aihe_metrics(
            completion_data=completion_data,
            archetype=archetype,
            is_kmu=is_kmu
        )
        
        # Complete the assessment with calculated metrics
        completed_assessment = crud_assessment.complete_assessment_with_metrics(
            db,
            assessment_id=assessment_id,
            completion_data=completion_data,
            calculated_metrics=calculated_metrics
        )
        
        return completed_assessment
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Calculation error: {str(e)}"
        )


@router.post("/calculate", response_model=Dict[str, Any])
def calculate_metrics_preview(
    calculation_data: Dict[str, Any],
    db: Session = Depends(get_db)
):
    """
    Preview calculation of AIHE metrics without saving to database.
    
    This endpoint allows testing the calculation logic with sample data.
    
    Args:
        calculation_data: Dictionary with dimension_scores, context_factors, archetype, is_kmu
        db: Database session
        
    Returns:
        Dictionary with all calculated metrics and analysis
    """
    try:
        # Extract data from request
        dimension_scores_data = calculation_data.get('dimension_scores', [])
        context_factors_data = calculation_data.get('context_factors', [])
        archetype = calculation_data.get('archetype', 'BALANCED_TRANSFORMER')
        is_kmu = calculation_data.get('is_kmu', False)
        
        # Convert to calculation objects
        dimension_scores = []
        for score_data in dimension_scores_data:
            dimension_scores.append(
                DimensionScore(
                    dimension_id=score_data['dimension_id'],
                    ist_value=Decimal(str(score_data['ist_value'])),
                    soll_value=Decimal(str(score_data['soll_value']))
                )
            )
        
        context_factors = []
        for factor_data in context_factors_data:
            context_factors.append(
                ContextFactor(
                    factor_name=factor_data['factor_name'],
                    factor_value=factor_data['factor_value']
                )
            )
        
        # Calculate metrics
        calculated_metrics = calculate_complete_aihe_metrics(
            dimension_scores=dimension_scores,
            context_factors=context_factors,
            archetype=archetype,
            is_kmu=is_kmu
        )
        
        return calculated_metrics
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Calculation error: {str(e)}"
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


@router.get("/{assessment_id}/recommendations")
def get_assessment_recommendations(
    assessment_id: UUID,
    db: Session = Depends(get_db)
):
    """
    Get recommendations based on gap analysis for a specific assessment.
    
    Args:
        assessment_id: UUID of the assessment
        db: Database session
        
    Returns:
        Dictionary with recommendations and priority analysis
        
    Raises:
        HTTPException: If assessment not found
    """
    assessment = crud_assessment.get_with_scores(db, id=assessment_id)
    if not assessment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Assessment not found"
        )
    
    # Convert assessment scores to DimensionScore objects
    dimension_scores = []
    if hasattr(assessment, 'subdimension_scores') and assessment.subdimension_scores:
        # Group subdimension scores by dimension
        dimension_groups = {}
        for score in assessment.subdimension_scores:
            dim_id = score.subdimension_id[:2]  # Extract D1, D2, etc.
            if dim_id not in dimension_groups:
                dimension_groups[dim_id] = []
            dimension_groups[dim_id].append(score)
        
        # Calculate dimension averages
        for dim_id, scores in dimension_groups.items():
            avg_ist = sum(score.ist_value for score in scores) / len(scores)
            avg_soll = sum(score.soll_value for score in scores) / len(scores)
            
            dimension_scores.append(
                DimensionScore(
                    dimension_id=dim_id,
                    ist_value=Decimal(str(avg_ist)),
                    soll_value=Decimal(str(avg_soll))
                )
            )
    
    # Generate recommendations
    recommendations = GapAnalysisEngine.generate_recommendations(dimension_scores)
    
    return {
        "assessment_id": str(assessment_id),
        "recommendations": recommendations,
        "total_recommendations": len(recommendations),
        "critical_count": len([r for r in recommendations if r["priority"] == "CRITICAL"]),
        "high_count": len([r for r in recommendations if r["priority"] == "HIGH"]),
        "medium_count": len([r for r in recommendations if r["priority"] == "MEDIUM"]),
        "low_count": len([r for r in recommendations if r["priority"] == "LOW"])
    }


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
    Update a specific subdimension score and recalculate metrics.
    
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


def calculate_aihe_metrics(
    completion_data: AssessmentCompletion,
    archetype: str,
    is_kmu: bool
) -> Dict[str, Any]:
    """
    Calculate AIHE metrics from completion data using the full specification.
    
    Args:
        completion_data: Assessment completion data
        archetype: Organisation archetype
        is_kmu: Whether organisation is KMU
        
    Returns:
        Dictionary with all calculated metrics
    """
    # Convert subdimension scores to dimension scores
    dimension_groups = {}
    
    for score in completion_data.subdimension_scores:
        dim_id = score.subdimension_id[:2]  # Extract D1, D2, etc.
        if dim_id not in dimension_groups:
            dimension_groups[dim_id] = []
        dimension_groups[dim_id].append(score)
    
    # Calculate dimension averages
    dimension_scores = []
    for dim_id, scores in dimension_groups.items():
        avg_ist = sum(score.ist_value for score in scores) / len(scores)
        avg_soll = sum(score.soll_value for score in scores) / len(scores)
        
        dimension_scores.append(
            DimensionScore(
                dimension_id=dim_id,
                ist_value=Decimal(str(avg_ist)),
                soll_value=Decimal(str(avg_soll))
            )
        )
    
    # Convert context factors
    context_factors = []
    for factor in completion_data.context_factors:
        context_factors.append(
            ContextFactor(
                factor_name=factor.factor_name,
                factor_value=factor.factor_value
            )
        )
    
    return calculate_complete_aihe_metrics(
        dimension_scores=dimension_scores,
        context_factors=context_factors,
        archetype=archetype,
        is_kmu=is_kmu
    )


def calculate_complete_aihe_metrics(
    dimension_scores: List[DimensionScore],
    context_factors: List[ContextFactor],
    archetype: str,
    is_kmu: bool
) -> Dict[str, Any]:
    """
    Calculate all AIHE metrics using the complete specification logic.
    
    This function implements the full calculation logic from the 53-page specification
    including all 8 rules for dynamic weighting.
    
    Args:
        dimension_scores: List of dimension scores
        context_factors: List of context factors
        archetype: Organisation archetype
        is_kmu: Whether organisation is KMU
        
    Returns:
        Dictionary with all calculated metrics and analysis
    """
    
    # Step 1: Calculate context score
    context_score = AIHECalculationEngine.calculate_context_score(context_factors)
    
    # Step 2: Calculate dynamic weights using all 8 rules
    try:
        archetyp_enum = Archetyp(archetype)
    except ValueError:
        archetyp_enum = Archetyp.BALANCED_TRANSFORMER
    
    dynamic_weights = DynamicWeightingEngine.calculate_dynamic_weights(
        dimension_scores=dimension_scores,
        context_score=context_score,
        archetyp=archetyp_enum,
        is_kmu=is_kmu
    )
    
    # Step 3: Apply dynamic weights to dimension scores
    for score in dimension_scores:
        if score.dimension_id in dynamic_weights:
            score.dynamic_weight = Decimal(str(dynamic_weights[score.dimension_id]))
    
    # Step 4: Calculate core metrics
    eqi = AIHECalculationEngine.calculate_eqi(dimension_scores)
    rgi = AIHECalculationEngine.calculate_rgi(dimension_scores)
    si = AIHECalculationEngine.calculate_si(dimension_scores)
    sbs = AIHECalculationEngine.calculate_sbs(eqi, si, rgi)
    
    # Step 5: Generate recommendations
    recommendations = GapAnalysisEngine.generate_recommendations(dimension_scores)
    
    # Step 6: Prepare detailed analysis
    dimension_analysis = []
    for score in dimension_scores:
        gap, gap_percent = GapAnalysisEngine.calculate_subdimension_gap(
            float(score.ist_value), float(score.soll_value)
        )
        priority = GapAnalysisEngine.calculate_priority_level(
            float(score.ist_value), gap
        )
        
        dimension_analysis.append({
            "dimension_id": score.dimension_id,
            "ist_value": float(score.ist_value),
            "soll_value": float(score.soll_value),
            "gap": gap,
            "gap_percent": gap_percent,
            "priority": priority,
            "dynamic_weight": float(score.dynamic_weight)
        })
    
    return {
        "core_metrics": {
            "eqi": round(eqi, 3),
            "rgi": round(rgi, 3),
            "si": round(si, 3),
            "sbs": round(sbs, 3),
            "context_score": round(context_score, 3)
        },
        "dynamic_weights": dynamic_weights,
        "dimension_analysis": dimension_analysis,
        "recommendations": recommendations,
        "metadata": {
            "archetype": archetype,
            "is_kmu": is_kmu,
            "total_gap": float(sum(score.gap for score in dimension_scores)),
            "average_ist_value": float(sum(score.ist_value for score in dimension_scores) / len(dimension_scores)),
            "average_soll_value": float(sum(score.soll_value for score in dimension_scores) / len(dimension_scores)),
            "critical_dimensions": [
                score.dimension_id for score in dimension_scores 
                if score.ist_value < Decimal("2.0") and score.gap > Decimal("1.5")
            ],
            "high_priority_dimensions": [
                score.dimension_id for score in dimension_scores 
                if score.ist_value < Decimal("2.5") and score.gap > Decimal("1.0")
            ],
            "calculation_rules_applied": [
                "Rule 1: Tight gaps reinforcement",
                "Rule 2: Large gaps reinforcement", 
                "Rule 3: High tension response (Tech-Culture)",
                "Rule 4: Context complexity adjustment",
                "Rule 5: Above-average dimension dampening",
                "Rule 6: Archetype-specific adjustments",
                "Rule 7: Minimum security (1% minimum weight)",
                "Rule 8: Normalization (sum = 1.0)"
            ]
        }
    }
