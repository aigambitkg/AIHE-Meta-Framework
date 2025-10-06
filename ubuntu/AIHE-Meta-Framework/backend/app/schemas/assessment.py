"""
Pydantic schemas for Assessment-related API operations.

These schemas define the data validation and serialization
for assessment endpoints.
"""

from datetime import datetime, date
from typing import List, Optional
from uuid import UUID

from pydantic import BaseModel, Field, validator

from app.models.assessment import (
    AssessmentType, AssessmentStatus, DataCollectionMethod,
    ConfidenceLevel, PriorityLevel
)


class ContextFactorBase(BaseModel):
    """Base schema for context factor data."""
    
    factor_name: str = Field(..., max_length=100, description="Name of the context factor")
    factor_value: int = Field(..., ge=0, le=3, description="Factor value on 0-3 scale")
    factor_description: Optional[str] = Field(None, description="Optional description of the factor")


class ContextFactorCreate(ContextFactorBase):
    """Schema for creating a context factor."""
    pass


class ContextFactor(ContextFactorBase):
    """Schema for context factor response."""
    
    context_factor_id: UUID
    assessment_id: UUID
    
    class Config:
        from_attributes = True


class SubdimensionScoreBase(BaseModel):
    """Base schema for subdimension score data."""
    
    subdimension_id: str = Field(..., description="Subdimension ID (e.g., 'D1.1')")
    ist_value: float = Field(..., ge=1.0, le=4.0, description="Current maturity level")
    soll_value: float = Field(..., ge=1.0, le=4.0, description="Target maturity level")
    assessment_rationale: str = Field(..., min_length=50, description="Assessment rationale (min 50 chars)")
    confidence_level: ConfidenceLevel = Field(..., description="Confidence in the assessment")
    evidence_documents: Optional[List[str]] = Field(None, description="List of evidence document IDs")
    
    @validator('ist_value', 'soll_value')
    def validate_maturity_values(cls, v):
        # Round to nearest 0.1
        return round(v * 10) / 10


class SubdimensionScoreCreate(SubdimensionScoreBase):
    """Schema for creating a subdimension score."""
    pass


class SubdimensionScoreUpdate(BaseModel):
    """Schema for updating a subdimension score."""
    
    ist_value: Optional[float] = Field(None, ge=1.0, le=4.0)
    soll_value: Optional[float] = Field(None, ge=1.0, le=4.0)
    assessment_rationale: Optional[str] = Field(None, min_length=50)
    confidence_level: Optional[ConfidenceLevel] = None
    evidence_documents: Optional[List[str]] = None
    priority_level: Optional[PriorityLevel] = None
    priority_reason: Optional[str] = None
    
    @validator('ist_value', 'soll_value')
    def validate_maturity_values(cls, v):
        if v is not None:
            return round(v * 10) / 10
        return v


class SubdimensionScore(SubdimensionScoreBase):
    """Schema for subdimension score response."""
    
    score_id: UUID
    assessment_id: UUID
    gap: Optional[float] = Field(None, description="Calculated gap (ABS(soll - ist))")
    gap_percentage: Optional[float] = Field(None, description="Gap as percentage")
    priority_level: Optional[PriorityLevel] = Field(None, description="Calculated priority level")
    priority_reason: Optional[str] = Field(None, description="Reason for priority assignment")
    
    class Config:
        from_attributes = True


class DimensionScoreBase(BaseModel):
    """Base schema for dimension score data."""
    
    dimension_id: str = Field(..., description="Dimension ID (e.g., 'D1')")
    ist_value: float = Field(..., ge=1.0, le=4.0, description="Aggregated current maturity")
    soll_value: float = Field(..., ge=1.0, le=4.0, description="Aggregated target maturity")
    dynamic_weight: float = Field(..., ge=0.0, le=1.0, description="Dynamic weight for this dimension")


class DimensionScore(DimensionScoreBase):
    """Schema for dimension score response."""
    
    dimension_score_id: UUID
    assessment_id: UUID
    gap: float = Field(..., description="Calculated gap")
    
    class Config:
        from_attributes = True


class AssessmentMetrics(BaseModel):
    """Schema for calculated assessment metrics."""
    
    overall_rgi: Optional[float] = Field(None, ge=0.0, le=1.0, description="Reifegrad-Index")
    overall_eqi: Optional[float] = Field(None, ge=0.0, le=1.0, description="Equilibrium Quality Index")
    overall_si: Optional[float] = Field(None, ge=0.0, le=1.0, description="Spannungsindex")
    overall_sbs: Optional[float] = Field(None, ge=0.0, le=1.0, description="System Balance Score")
    context_score: Optional[float] = Field(None, ge=0.0, le=1.0, description="Context complexity score")


class AssessmentBase(BaseModel):
    """Base schema for assessment data."""
    
    assessment_name: str = Field(..., min_length=1, max_length=200, description="Assessment name")
    assessment_type: AssessmentType = Field(..., description="Type of assessment")
    assessment_period_start: date = Field(..., description="Assessment period start date")
    assessment_period_end: date = Field(..., description="Assessment period end date")
    data_collection_methods: Optional[List[DataCollectionMethod]] = Field(None, description="Data collection methods used")
    participants_count: Optional[int] = Field(None, ge=0, description="Number of participants")
    facilitator_name: Optional[str] = Field(None, max_length=200, description="Name of the facilitator")
    
    @validator('assessment_period_end')
    def validate_period_end(cls, v, values):
        if 'assessment_period_start' in values and v <= values['assessment_period_start']:
            raise ValueError('Assessment period end must be after start date')
        return v


class AssessmentCreate(AssessmentBase):
    """Schema for creating a new assessment."""
    
    organisation_id: UUID = Field(..., description="ID of the organisation being assessed")


class AssessmentUpdate(BaseModel):
    """Schema for updating an existing assessment."""
    
    assessment_name: Optional[str] = Field(None, min_length=1, max_length=200)
    assessment_type: Optional[AssessmentType] = None
    assessment_period_start: Optional[date] = None
    assessment_period_end: Optional[date] = None
    data_collection_methods: Optional[List[DataCollectionMethod]] = None
    participants_count: Optional[int] = Field(None, ge=0)
    facilitator_name: Optional[str] = Field(None, max_length=200)
    status: Optional[AssessmentStatus] = None
    completion_percentage: Optional[int] = Field(None, ge=0, le=100)


class AssessmentInDB(AssessmentBase):
    """Schema for assessment data as stored in database."""
    
    assessment_id: UUID
    organisation_id: UUID
    created_at: datetime
    completed_at: Optional[datetime] = None
    status: AssessmentStatus
    completion_percentage: int
    
    class Config:
        from_attributes = True


class Assessment(AssessmentInDB, AssessmentMetrics):
    """Schema for full assessment response."""
    
    # Include calculated metrics
    subdimension_scores: Optional[List[SubdimensionScore]] = Field(None, description="Subdimension scores")
    dimension_scores: Optional[List[DimensionScore]] = Field(None, description="Dimension scores")
    context_factors: Optional[List[ContextFactor]] = Field(None, description="Context factors")
    
    class Config:
        from_attributes = True


class AssessmentSummary(BaseModel):
    """Schema for assessment summary (list view)."""
    
    assessment_id: UUID
    assessment_name: str
    assessment_type: AssessmentType
    organisation_id: UUID
    status: AssessmentStatus
    completion_percentage: int
    created_at: datetime
    completed_at: Optional[datetime] = None
    assessment_period_start: date
    assessment_period_end: date
    overall_rgi: Optional[float] = None
    overall_sbs: Optional[float] = None
    
    class Config:
        from_attributes = True


class AssessmentCompletion(BaseModel):
    """Schema for assessment completion request."""
    
    subdimension_scores: List[SubdimensionScoreCreate] = Field(..., description="All 16 subdimension scores")
    context_factors: List[ContextFactorCreate] = Field(..., description="Context factors")
    
    @validator('subdimension_scores')
    def validate_all_subdimensions(cls, v):
        if len(v) != 16:
            raise ValueError('Must provide exactly 16 subdimension scores')
        
        expected_subdimensions = [
            'D1.1', 'D1.2', 'D2.1', 'D2.2', 'D3.1', 'D3.2', 'D4.1', 'D4.2',
            'D5.1', 'D5.2', 'D6.1', 'D6.2', 'D7.1', 'D7.2', 'D8.1', 'D8.2'
        ]
        
        provided_subdimensions = [score.subdimension_id for score in v]
        missing = set(expected_subdimensions) - set(provided_subdimensions)
        
        if missing:
            raise ValueError(f'Missing subdimension scores: {missing}')
        
        return v
