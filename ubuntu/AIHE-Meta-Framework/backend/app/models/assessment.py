"""
Assessment models for the AIHE Meta-Framework.

These models represent assessments, scores, and related evaluation data.
"""

import uuid
from datetime import datetime, date
from enum import Enum
from typing import List

from sqlalchemy import Column, String, Integer, DateTime, Date, Boolean, Enum as SQLEnum, Numeric, Text, ForeignKey, ARRAY
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.core.database import Base


class AssessmentType(str, Enum):
    """Assessment type enumeration."""
    QUICK_SCAN = "QUICK_SCAN"
    FULL_ASSESSMENT = "FULL_ASSESSMENT"
    FOLLOW_UP = "FOLLOW_UP"


class AssessmentStatus(str, Enum):
    """Assessment status enumeration."""
    DRAFT = "DRAFT"
    IN_PROGRESS = "IN_PROGRESS"
    COMPLETED = "COMPLETED"
    ARCHIVED = "ARCHIVED"


class DataCollectionMethod(str, Enum):
    """Data collection method enumeration."""
    WORKSHOP = "WORKSHOP"
    INTERVIEW = "INTERVIEW"
    SURVEY = "SURVEY"
    DOCUMENT_ANALYSIS = "DOCUMENT_ANALYSIS"


class ConfidenceLevel(str, Enum):
    """Confidence level enumeration."""
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"


class PriorityLevel(str, Enum):
    """Priority level enumeration."""
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


class Assessment(Base):
    """
    Assessment model representing an evaluation of an organisation.
    
    This is the core entity that captures the assessment process and results.
    """
    
    __tablename__ = "assessments"
    
    # Identification
    assessment_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    organisation_id = Column(UUID(as_uuid=True), ForeignKey("organisations.organisation_id"), nullable=False)
    assessment_name = Column(String(200), nullable=False)
    assessment_type = Column(SQLEnum(AssessmentType), nullable=False)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    completed_at = Column(DateTime, nullable=True)
    assessment_period_start = Column(Date, nullable=False)
    assessment_period_end = Column(Date, nullable=False)
    
    # Status
    status = Column(SQLEnum(AssessmentStatus), default=AssessmentStatus.DRAFT, nullable=False)
    completion_percentage = Column(Integer, default=0, nullable=False)
    
    # Methodology
    data_collection_methods = Column(ARRAY(SQLEnum(DataCollectionMethod)), nullable=True)
    participants_count = Column(Integer, nullable=True)
    facilitator_name = Column(String(200), nullable=True)
    
    # Calculated Results (computed fields)
    overall_rgi = Column(Numeric(3, 2), nullable=True)  # 0.0-4.0
    overall_eqi = Column(Numeric(3, 2), nullable=True)  # 0.0-1.0
    overall_si = Column(Numeric(3, 2), nullable=True)   # 0.0-1.0
    overall_sbs = Column(Numeric(3, 2), nullable=True)  # 0.0-1.0
    context_score = Column(Numeric(3, 2), nullable=True)  # 0.0-1.0
    
    # Relationships
    organisation = relationship("Organisation", back_populates="assessments")
    subdimension_scores = relationship("SubdimensionScore", back_populates="assessment", cascade="all, delete-orphan")
    dimension_scores = relationship("DimensionScore", back_populates="assessment", cascade="all, delete-orphan")
    context_factors = relationship("ContextFactor", back_populates="assessment", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Assessment(id={self.assessment_id}, name='{self.assessment_name}', status={self.status})>"


class SubdimensionScore(Base):
    """
    Subdimension score model representing individual subdimension evaluations.
    
    Each assessment has 16 subdimension scores (one for each subdimension).
    """
    
    __tablename__ = "subdimension_scores"
    
    # Identification
    score_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    assessment_id = Column(UUID(as_uuid=True), ForeignKey("assessments.assessment_id"), nullable=False)
    subdimension_id = Column(String(10), ForeignKey("subdimensions.subdimension_id"), nullable=False)
    
    # Evaluation
    ist_value = Column(Numeric(2, 1), nullable=False)  # 1.0-4.0, step 0.1
    soll_value = Column(Numeric(2, 1), nullable=False)  # 1.0-4.0, step 0.1
    gap = Column(Numeric(2, 1), nullable=True)  # Calculated: ABS(soll_value - ist_value)
    gap_percentage = Column(Numeric(5, 2), nullable=True)  # Calculated: gap / 4.0 * 100
    
    # Evidence
    assessment_rationale = Column(Text, nullable=False)
    evidence_documents = Column(ARRAY(String), nullable=True)  # Array of document IDs
    confidence_level = Column(SQLEnum(ConfidenceLevel), nullable=False)
    
    # Prioritization
    priority_level = Column(SQLEnum(PriorityLevel), nullable=True)
    priority_reason = Column(Text, nullable=True)
    
    # Relationships
    assessment = relationship("Assessment", back_populates="subdimension_scores")
    subdimension = relationship("Subdimension", back_populates="subdimension_scores")
    
    def __repr__(self):
        return f"<SubdimensionScore(id={self.score_id}, subdimension={self.subdimension_id}, ist={self.ist_value}, soll={self.soll_value})>"


class DimensionScore(Base):
    """
    Dimension score model representing aggregated dimension evaluations.
    
    These are calculated from the corresponding subdimension scores.
    """
    
    __tablename__ = "dimension_scores"
    
    # Identification
    dimension_score_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    assessment_id = Column(UUID(as_uuid=True), ForeignKey("assessments.assessment_id"), nullable=False)
    dimension_id = Column(String(10), ForeignKey("dimensions.dimension_id"), nullable=False)
    
    # Calculated Values
    ist_value = Column(Numeric(2, 1), nullable=False)  # Average of subdimension ist_values
    soll_value = Column(Numeric(2, 1), nullable=False)  # Average of subdimension soll_values
    gap = Column(Numeric(2, 1), nullable=False)  # Calculated gap
    dynamic_weight = Column(Numeric(3, 2), nullable=False)  # From weighting engine (0.0-1.0)
    
    # Relationships
    assessment = relationship("Assessment", back_populates="dimension_scores")
    dimension = relationship("Dimension", back_populates="dimension_scores")
    
    def __repr__(self):
        return f"<DimensionScore(dimension={self.dimension_id}, ist={self.ist_value}, weight={self.dynamic_weight})>"


class ContextFactor(Base):
    """
    Context factor model for storing contextual assessment information.
    
    These factors influence the dynamic weighting and overall assessment.
    """
    
    __tablename__ = "context_factors"
    
    # Identification
    context_factor_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    assessment_id = Column(UUID(as_uuid=True), ForeignKey("assessments.assessment_id"), nullable=False)
    
    # Factor Details
    factor_name = Column(String(100), nullable=False)
    factor_value = Column(Integer, nullable=False)  # 0-3 scale
    factor_description = Column(Text, nullable=True)
    
    # Relationships
    assessment = relationship("Assessment", back_populates="context_factors")
    
    def __repr__(self):
        return f"<ContextFactor(name='{self.factor_name}', value={self.factor_value})>"
