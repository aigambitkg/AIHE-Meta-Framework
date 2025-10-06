"""
Schemas package for the AIHE Meta-Framework.

This package contains all Pydantic schemas for API validation and serialization.
"""

from .organisation import (
    Organisation, OrganisationCreate, OrganisationUpdate, OrganisationSummary,
    OrganisationArchetype, OrganisationInDB
)
from .assessment import (
    Assessment, AssessmentCreate, AssessmentUpdate, AssessmentSummary,
    AssessmentCompletion, AssessmentMetrics,
    SubdimensionScore, SubdimensionScoreCreate, SubdimensionScoreUpdate,
    DimensionScore, ContextFactor, ContextFactorCreate
)
from .dimension import (
    DimensionResponse, DimensionSummary, SubdimensionResponse
)

__all__ = [
    # Organisation schemas
    "Organisation",
    "OrganisationCreate",
    "OrganisationUpdate", 
    "OrganisationSummary",
    "OrganisationArchetype",
    "OrganisationInDB",
    
    # Assessment schemas
    "Assessment",
    "AssessmentCreate",
    "AssessmentUpdate",
    "AssessmentSummary",
    "AssessmentCompletion",
    "AssessmentMetrics",
    "SubdimensionScore",
    "SubdimensionScoreCreate",
    "SubdimensionScoreUpdate",
    "DimensionScore",
    "ContextFactor",
    "ContextFactorCreate",
    
    # Dimension schemas
    "DimensionResponse",
    "DimensionSummary",
    "SubdimensionResponse",
]
