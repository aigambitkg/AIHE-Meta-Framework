"""
Dimension and Subdimension models for the AIHE Meta-Framework.

These models represent the 8 dimensions and 16 subdimensions
that form the core assessment structure.
"""

from sqlalchemy import Column, String, Text, ForeignKey
from sqlalchemy.orm import relationship

from app.core.database import Base


class Dimension(Base):
    """
    Dimension model representing the 8 main assessment dimensions.
    
    These are master data that define the structure of the AIHE framework.
    """
    
    __tablename__ = "dimensions"
    
    dimension_id = Column(String(10), primary_key=True)  # e.g., "D1", "D2", etc.
    name = Column(String(200), nullable=False)
    description = Column(Text, nullable=False)
    
    # Relationships
    subdimensions = relationship("Subdimension", back_populates="dimension", cascade="all, delete-orphan")
    dimension_scores = relationship("DimensionScore", back_populates="dimension")
    
    def __repr__(self):
        return f"<Dimension(id='{self.dimension_id}', name='{self.name}')>"


class Subdimension(Base):
    """
    Subdimension model representing the 16 subdimensions (2 per dimension).
    
    Each subdimension has a specific focus area and assessment criteria.
    """
    
    __tablename__ = "subdimensions"
    
    subdimension_id = Column(String(10), primary_key=True)  # e.g., "D1.1", "D1.2", etc.
    parent_dimension_id = Column(String(10), ForeignKey("dimensions.dimension_id"), nullable=False)
    name = Column(String(200), nullable=False)
    description = Column(Text, nullable=False)
    core_question = Column(Text, nullable=False)  # The main assessment question
    focus_area = Column(Text, nullable=False)  # What this subdimension focuses on
    
    # Relationships
    dimension = relationship("Dimension", back_populates="subdimensions")
    subdimension_scores = relationship("SubdimensionScore", back_populates="subdimension")
    
    def __repr__(self):
        return f"<Subdimension(id='{self.subdimension_id}', name='{self.name}')>"
