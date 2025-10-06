"""
Learning Cycle model for the AIHE Meta-Framework.

This model represents the iterative learning loops for continuous improvement.
"""

import uuid
from datetime import datetime
from enum import Enum

from sqlalchemy import Column, String, DateTime, Enum as SQLEnum, ForeignKey, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.core.database import Base


class LearningCycleStatus(str, Enum):
    """Learning cycle status enumeration."""
    HYPOTHESIS = "HYPOTHESIS"
    INTERVENTION = "INTERVENTION"
    MEASUREMENT = "MEASUREMENT"
    LEARNING = "LEARNING"
    COMPLETED = "COMPLETED"


class LearningCycle(Base):
    """
    Learning Cycle model representing iterative improvement cycles.
    """
    
    __tablename__ = "learning_cycles"
    
    # Identification
    cycle_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    organisation_id = Column(UUID(as_uuid=True), ForeignKey("organisations.organisation_id"), nullable=False)
    assessment_id = Column(UUID(as_uuid=True), ForeignKey("assessments.assessment_id"), nullable=False)
    cycle_name = Column(String(200), nullable=False)
    
    # Status and Timestamps
    status = Column(SQLEnum(LearningCycleStatus), default=LearningCycleStatus.HYPOTHESIS, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    completed_at = Column(DateTime, nullable=True)
    
    # Content
    hypothesis = Column(Text, nullable=False)
    intervention = Column(Text, nullable=True)
    measurement = Column(Text, nullable=True)
    learning = Column(Text, nullable=True)
    
    # Relationships
    organisation = relationship("Organisation", back_populates="learning_cycles")
    assessment = relationship("Assessment")
    
    def __repr__(self):
        return f"<LearningCycle(id={self.cycle_id}, name='{self.cycle_name}', status={self.status})>"
