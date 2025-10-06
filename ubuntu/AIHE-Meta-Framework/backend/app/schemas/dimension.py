"""
Pydantic schemas for Dimension and Subdimension API operations.

These schemas define the data validation and serialization
for dimension and subdimension endpoints.
"""

from typing import List, Optional

from pydantic import BaseModel, Field


class SubdimensionBase(BaseModel):
    """Base schema for subdimension data."""
    
    subdimension_id: str = Field(..., description="Subdimension ID (e.g., 'D1.1')")
    parent_dimension_id: str = Field(..., description="Parent dimension ID (e.g., 'D1')")
    name: str = Field(..., description="Subdimension name")
    description: str = Field(..., description="Detailed description of the subdimension")
    core_question: str = Field(..., description="The main assessment question")
    focus_area: str = Field(..., description="What this subdimension focuses on")


class SubdimensionResponse(SubdimensionBase):
    """Schema for subdimension response."""
    
    class Config:
        from_attributes = True


class DimensionBase(BaseModel):
    """Base schema for dimension data."""
    
    dimension_id: str = Field(..., description="Dimension ID (e.g., 'D1')")
    name: str = Field(..., description="Dimension name")
    description: str = Field(..., description="Detailed description of the dimension")


class DimensionResponse(DimensionBase):
    """Schema for dimension response with subdimensions."""
    
    subdimensions: Optional[List[SubdimensionResponse]] = Field(None, description="List of subdimensions")
    
    class Config:
        from_attributes = True


class DimensionSummary(DimensionBase):
    """Schema for dimension summary (without subdimensions)."""
    
    subdimension_count: Optional[int] = Field(None, description="Number of subdimensions")
    
    class Config:
        from_attributes = True
