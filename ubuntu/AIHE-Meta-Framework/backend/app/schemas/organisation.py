"""
Pydantic schemas for Organisation-related API operations.

These schemas define the data validation and serialization
for organisation endpoints.
"""

from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, Field, validator

from app.models.organisation import OrganisationType, ArchetypeType, ArchetypeDeterminationMethod, SubscriptionTier


class OrganisationBase(BaseModel):
    """Base schema for organisation data."""
    
    name: str = Field(..., min_length=1, max_length=200, description="Organisation name")
    legal_name: Optional[str] = Field(None, max_length=200, description="Legal name of the organisation")
    organisation_type: OrganisationType = Field(..., description="Type of organisation")
    employee_count: Optional[int] = Field(None, ge=0, description="Number of employees")
    industry: Optional[str] = Field(None, max_length=100, description="Industry sector")
    country: Optional[str] = Field(None, min_length=2, max_length=2, description="ISO 3166-1 alpha-2 country code")
    region: Optional[str] = Field(None, max_length=100, description="Geographic region")
    
    @validator('country')
    def validate_country_code(cls, v):
        if v is not None and len(v) != 2:
            raise ValueError('Country code must be exactly 2 characters (ISO 3166-1 alpha-2)')
        return v.upper() if v else v


class OrganisationCreate(OrganisationBase):
    """Schema for creating a new organisation."""
    
    subscription_tier: Optional[SubscriptionTier] = Field(SubscriptionTier.FREE, description="Subscription tier")


class OrganisationUpdate(BaseModel):
    """Schema for updating an existing organisation."""
    
    name: Optional[str] = Field(None, min_length=1, max_length=200)
    legal_name: Optional[str] = Field(None, max_length=200)
    organisation_type: Optional[OrganisationType] = None
    employee_count: Optional[int] = Field(None, ge=0)
    industry: Optional[str] = Field(None, max_length=100)
    country: Optional[str] = Field(None, min_length=2, max_length=2)
    region: Optional[str] = Field(None, max_length=100)
    primary_archetype: Optional[ArchetypeType] = None
    archetype_confidence_score: Optional[float] = Field(None, ge=0.0, le=1.0)
    archetype_determination_method: Optional[ArchetypeDeterminationMethod] = None
    active: Optional[bool] = None
    subscription_tier: Optional[SubscriptionTier] = None
    
    @validator('country')
    def validate_country_code(cls, v):
        if v is not None and len(v) != 2:
            raise ValueError('Country code must be exactly 2 characters (ISO 3166-1 alpha-2)')
        return v.upper() if v else v


class OrganisationArchetype(BaseModel):
    """Schema for organisation archetype information."""
    
    primary_archetype: Optional[ArchetypeType] = None
    archetype_confidence_score: Optional[float] = Field(None, ge=0.0, le=1.0)
    archetype_determined_at: Optional[datetime] = None
    archetype_determination_method: Optional[ArchetypeDeterminationMethod] = None


class OrganisationInDB(OrganisationBase):
    """Schema for organisation data as stored in database."""
    
    organisation_id: UUID
    creation_date: datetime
    last_modified: datetime
    primary_archetype: Optional[ArchetypeType] = None
    archetype_confidence_score: Optional[float] = None
    archetype_determined_at: Optional[datetime] = None
    archetype_determination_method: Optional[ArchetypeDeterminationMethod] = None
    active: bool
    subscription_tier: SubscriptionTier
    
    class Config:
        from_attributes = True


class Organisation(OrganisationInDB):
    """Schema for organisation response."""
    
    # This can include computed fields or additional data
    assessment_count: Optional[int] = Field(None, description="Number of assessments for this organisation")
    
    class Config:
        from_attributes = True


class OrganisationSummary(BaseModel):
    """Schema for organisation summary (list view)."""
    
    organisation_id: UUID
    name: str
    organisation_type: OrganisationType
    industry: Optional[str] = None
    country: Optional[str] = None
    primary_archetype: Optional[ArchetypeType] = None
    active: bool
    subscription_tier: SubscriptionTier
    creation_date: datetime
    last_modified: datetime
    
    class Config:
        from_attributes = True
