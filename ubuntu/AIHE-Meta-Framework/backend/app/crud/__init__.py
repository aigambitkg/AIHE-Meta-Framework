"""
CRUD package for the AIHE Meta-Framework.

This package contains all CRUD (Create, Read, Update, Delete) operations
for the application models.
"""

from .crud_organisation import crud_organisation
from .crud_assessment import crud_assessment, crud_subdimension_score, crud_context_factor

__all__ = [
    "crud_organisation",
    "crud_assessment",
    "crud_subdimension_score", 
    "crud_context_factor",
]
