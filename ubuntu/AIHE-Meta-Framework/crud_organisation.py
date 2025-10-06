"""
CRUD operations for Organisation model.

This module provides Create, Read, Update, Delete operations
for the Organisation entity.
"""

from typing import List, Optional
from uuid import UUID

from sqlalchemy.orm import Session

from app.crud.base import CRUDBase
from app.models.organisation import Organisation
from app.schemas.organisation import OrganisationCreate, OrganisationUpdate


class CRUDOrganisation(CRUDBase[Organisation, OrganisationCreate, OrganisationUpdate]):
    """CRUD operations for Organisation model."""
    
    def get_multi(
        self,
        db: Session,
        *,
        skip: int = 0,
        limit: int = 100,
        active_only: bool = True
    ) -> List[Organisation]:
        """
        Retrieve multiple organisations with optional filtering.
        
        Args:
            db: Database session
            skip: Number of records to skip
            limit: Maximum number of records to return
            active_only: Whether to return only active organisations
            
        Returns:
            List of organisations
        """
        query = db.query(self.model)
        
        if active_only:
            query = query.filter(Organisation.active == True)
            
        return query.offset(skip).limit(limit).all()
    
    def get_by_name(self, db: Session, *, name: str) -> Optional[Organisation]:
        """
        Retrieve organisation by name.
        
        Args:
            db: Database session
            name: Organisation name
            
        Returns:
            Organisation if found, None otherwise
        """
        return db.query(Organisation).filter(Organisation.name == name).first()
    
    def get_by_industry(self, db: Session, *, industry: str) -> List[Organisation]:
        """
        Retrieve organisations by industry.
        
        Args:
            db: Database session
            industry: Industry name
            
        Returns:
            List of organisations in the specified industry
        """
        return db.query(Organisation).filter(
            Organisation.industry == industry,
            Organisation.active == True
        ).all()
    
    def get_by_archetype(self, db: Session, *, archetype: str) -> List[Organisation]:
        """
        Retrieve organisations by archetype.
        
        Args:
            db: Database session
            archetype: Archetype name
            
        Returns:
            List of organisations with the specified archetype
        """
        return db.query(Organisation).filter(
            Organisation.primary_archetype == archetype,
            Organisation.active == True
        ).all()
    
    def remove(self, db: Session, *, id: UUID) -> Organisation:
        """
        Soft delete an organisation (set active=False).
        
        Args:
            db: Database session
            id: Organisation UUID
            
        Returns:
            Deactivated organisation
        """
        obj = db.query(self.model).get(id)
        obj.active = False
        db.add(obj)
        db.commit()
        db.refresh(obj)
        return obj


# Create instance
crud_organisation = CRUDOrganisation(Organisation)
