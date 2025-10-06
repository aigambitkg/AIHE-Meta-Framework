"""
Organisation model for the AIHE Meta-Framework.

This model represents the main entity in the system - an organisation
that undergoes AI ethics assessments.
"""

import uuid
from datetime import datetime
from enum import Enum
from typing import Optional

from sqlalchemy import Column, String, Integer, DateTime, Boolean, Enum as SQLEnum, Numeric
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.core.database import Base


class OrganisationType(str, Enum):
    """Organisation type enumeration."""
    STARTUP = "STARTUP"
    KMU = "KMU"
    GROSSUNTERNEHMEN = "GROSSUNTERNEHMEN"
    KONZERN = "KONZERN"


class ArchetypeType(str, Enum):
    """Organisation archetype enumeration."""
    CHAOTIC_DOER = "CHAOTIC_DOER"
    CAUTIOUS_CORPORATE = "CAUTIOUS_CORPORATE"
    STAGNANT_ESTABLISHED = "STAGNANT_ESTABLISHED"
    BALANCED_TRANSFORMER = "BALANCED_TRANSFORMER"


class ArchetypeDeterminationMethod(str, Enum):
    """Method used to determine the archetype."""
    AUTO = "AUTO"
    MANUAL = "MANUAL"
    QUICK_SCAN = "QUICK_SCAN"


class SubscriptionTier(str, Enum):
    """Subscription tier enumeration."""
    FREE = "FREE"
    BASIC = "BASIC"
    PROFESSIONAL = "PROFESSIONAL"
    ENTERPRISE = "ENTERPRISE"


class Organisation(Base):
    """
    Organisation model representing companies/entities undergoing AI ethics assessment.
    
    This is the central entity in the AIHE Meta-Framework, containing all
    organisational metadata and relationships to assessments.
    """
    
    __tablename__ = "organisations"
    
    # Identification
    organisation_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(200), nullable=False, index=True)
    legal_name = Column(String(200), nullable=True)
    creation_date = Column(DateTime, default=datetime.utcnow, nullable=False)
    last_modified = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Classification
    organisation_type = Column(SQLEnum(OrganisationType), nullable=False)
    employee_count = Column(Integer, nullable=True)
    industry = Column(String(100), nullable=True)
    country = Column(String(2), nullable=True)  # ISO 3166-1 alpha-2
    region = Column(String(100), nullable=True)
    
    # Archetype
    primary_archetype = Column(SQLEnum(ArchetypeType), nullable=True)
    archetype_confidence_score = Column(Numeric(3, 2), nullable=True)  # 0.0-1.0
    archetype_determined_at = Column(DateTime, nullable=True)
    archetype_determination_method = Column(SQLEnum(ArchetypeDeterminationMethod), nullable=True)
    
    # Status
    active = Column(Boolean, default=True, nullable=False)
    subscription_tier = Column(SQLEnum(SubscriptionTier), default=SubscriptionTier.FREE, nullable=False)
    
    # Relationships
    assessments = relationship("Assessment", back_populates="organisation", cascade="all, delete-orphan")
    learning_cycles = relationship("LearningCycle", back_populates="organisation", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Organisation(id={self.organisation_id}, name='{self.name}', type={self.organisation_type})>"
