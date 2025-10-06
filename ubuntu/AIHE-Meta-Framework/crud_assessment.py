"""
CRUD operations for Assessment model and related entities.

This module provides Create, Read, Update, Delete operations
for assessments, scores, and context factors.
"""

from typing import List, Optional
from uuid import UUID
from datetime import datetime

from sqlalchemy.orm import Session, joinedload

from app.crud.base import CRUDBase
from app.models.assessment import (
    Assessment, SubdimensionScore, DimensionScore, ContextFactor,
    AssessmentStatus
)
from app.schemas.assessment import (
    AssessmentCreate, AssessmentUpdate, AssessmentCompletion,
    SubdimensionScoreCreate, SubdimensionScoreUpdate,
    ContextFactorCreate
)
from app.core.calculations import (
    AIHECalculationEngine, DynamicWeightingEngine, GapAnalysisEngine
)


class CRUDAssessment(CRUDBase[Assessment, AssessmentCreate, AssessmentUpdate]):
    """CRUD operations for Assessment model."""
    
    def get_with_scores(self, db: Session, *, id: UUID) -> Optional[Assessment]:
        """
        Retrieve assessment with all related scores and context factors.
        
        Args:
            db: Database session
            id: Assessment UUID
            
        Returns:
            Assessment with loaded relationships
        """
        return db.query(Assessment).options(
            joinedload(Assessment.subdimension_scores),
            joinedload(Assessment.dimension_scores),
            joinedload(Assessment.context_factors)
        ).filter(Assessment.assessment_id == id).first()
    
    def get_by_organisation(
        self,
        db: Session,
        *,
        organisation_id: UUID,
        skip: int = 0,
        limit: int = 100
    ) -> List[Assessment]:
        """
        Retrieve assessments for a specific organisation.
        
        Args:
            db: Database session
            organisation_id: Organisation UUID
            skip: Number of records to skip
            limit: Maximum number of records to return
            
        Returns:
            List of assessments for the organisation
        """
        return db.query(Assessment).filter(
            Assessment.organisation_id == organisation_id
        ).offset(skip).limit(limit).all()
    
    def complete_assessment(
        self,
        db: Session,
        *,
        assessment_id: UUID,
        completion_data: AssessmentCompletion,
        organisation_archetype: str = "BALANCED_TRANSFORMER"
    ) -> Assessment:
        """
        Complete an assessment by adding scores and calculating metrics.
        
        Args:
            db: Database session
            assessment_id: Assessment UUID
            completion_data: Completion data with scores and context factors
            organisation_archetype: Organisation archetype for dynamic weighting
            
        Returns:
            Completed assessment with calculated metrics
        """
        # Get the assessment
        assessment = self.get(db, id=assessment_id)
        if not assessment:
            raise ValueError("Assessment not found")
        
        # Create context factors
        context_factors = []
        for factor_data in completion_data.context_factors:
            context_factor = ContextFactor(
                assessment_id=assessment_id,
                **factor_data.dict()
            )
            db.add(context_factor)
            context_factors.append(context_factor)
        
        # Calculate context score
        context_score = AIHECalculationEngine.calculate_context_score(context_factors)
        
        # Calculate dynamic weights
        dynamic_weights = DynamicWeightingEngine.calculate_dynamic_weights(
            archetype=organisation_archetype,
            context_score=context_score
        )
        
        # Create subdimension scores
        subdimension_scores = []
        for score_data in completion_data.subdimension_scores:
            # Calculate gap and priority
            gap, gap_percentage = GapAnalysisEngine.calculate_subdimension_gap(
                score_data.ist_value, score_data.soll_value
            )
            priority_level = GapAnalysisEngine.calculate_priority_level(
                score_data.ist_value, gap
            )
            
            subdimension_score = SubdimensionScore(
                assessment_id=assessment_id,
                gap=gap,
                gap_percentage=gap_percentage,
                priority_level=priority_level,
                **score_data.dict()
            )
            db.add(subdimension_score)
            subdimension_scores.append(subdimension_score)
        
        # Calculate dimension scores (aggregate from subdimensions)
        dimension_scores = []
        dimensions = ['D1', 'D2', 'D3', 'D4', 'D5', 'D6', 'D7', 'D8']
        
        for dim_id in dimensions:
            # Get subdimension scores for this dimension
            dim_subdimensions = [
                score for score in subdimension_scores
                if score.subdimension_id.startswith(dim_id + '.')
            ]
            
            if len(dim_subdimensions) == 2:
                # Calculate averages
                avg_ist = sum(score.ist_value for score in dim_subdimensions) / 2
                avg_soll = sum(score.soll_value for score in dim_subdimensions) / 2
                gap = abs(avg_soll - avg_ist)
                
                dimension_score = DimensionScore(
                    assessment_id=assessment_id,
                    dimension_id=dim_id,
                    ist_value=round(avg_ist, 1),
                    soll_value=round(avg_soll, 1),
                    gap=round(gap, 1),
                    dynamic_weight=dynamic_weights.get(dim_id, 0.125)
                )
                db.add(dimension_score)
                dimension_scores.append(dimension_score)
        
        # Calculate all metrics
        metrics = AIHECalculationEngine.calculate_all_metrics(
            dimension_scores, context_factors
        )
        
        # Update assessment with calculated metrics
        assessment.overall_rgi = metrics['rgi']
        assessment.overall_eqi = metrics['eqi']
        assessment.overall_si = metrics['si']
        assessment.overall_sbs = metrics['sbs']
        assessment.context_score = metrics['context_score']
        assessment.status = AssessmentStatus.COMPLETED
        assessment.completed_at = datetime.utcnow()
        assessment.completion_percentage = 100
        
        db.add(assessment)
        db.commit()
        db.refresh(assessment)
        
        return assessment


class CRUDSubdimensionScore(CRUDBase[SubdimensionScore, SubdimensionScoreCreate, SubdimensionScoreUpdate]):
    """CRUD operations for SubdimensionScore model."""
    
    def get_by_assessment(
        self,
        db: Session,
        *,
        assessment_id: UUID
    ) -> List[SubdimensionScore]:
        """
        Retrieve all subdimension scores for an assessment.
        
        Args:
            db: Database session
            assessment_id: Assessment UUID
            
        Returns:
            List of subdimension scores
        """
        return db.query(SubdimensionScore).filter(
            SubdimensionScore.assessment_id == assessment_id
        ).all()
    
    def update_with_calculations(
        self,
        db: Session,
        *,
        db_obj: SubdimensionScore,
        obj_in: SubdimensionScoreUpdate
    ) -> SubdimensionScore:
        """
        Update subdimension score and recalculate derived values.
        
        Args:
            db: Database session
            db_obj: Existing subdimension score
            obj_in: Update data
            
        Returns:
            Updated subdimension score
        """
        # Update the object
        updated_obj = self.update(db, db_obj=db_obj, obj_in=obj_in)
        
        # Recalculate gap and priority if ist/soll values changed
        if obj_in.ist_value is not None or obj_in.soll_value is not None:
            gap, gap_percentage = GapAnalysisEngine.calculate_subdimension_gap(
                float(updated_obj.ist_value), float(updated_obj.soll_value)
            )
            priority_level = GapAnalysisEngine.calculate_priority_level(
                float(updated_obj.ist_value), gap
            )
            
            updated_obj.gap = gap
            updated_obj.gap_percentage = gap_percentage
            updated_obj.priority_level = priority_level
            
            db.add(updated_obj)
            db.commit()
            db.refresh(updated_obj)
        
        return updated_obj


class CRUDContextFactor(CRUDBase[ContextFactor, ContextFactorCreate, dict]):
    """CRUD operations for ContextFactor model."""
    
    def get_by_assessment(
        self,
        db: Session,
        *,
        assessment_id: UUID
    ) -> List[ContextFactor]:
        """
        Retrieve all context factors for an assessment.
        
        Args:
            db: Database session
            assessment_id: Assessment UUID
            
        Returns:
            List of context factors
        """
        return db.query(ContextFactor).filter(
            ContextFactor.assessment_id == assessment_id
        ).all()


# Create instances
crud_assessment = CRUDAssessment(Assessment)
crud_subdimension_score = CRUDSubdimensionScore(SubdimensionScore)
crud_context_factor = CRUDContextFactor(ContextFactor)
