"""
FastAPI Dependencies for GoviSense API
Provides database sessions and RBAC authentication dependencies.
"""

from govisense.db.session import get_db
from govisense.api.auth import (
    get_current_user,
    require_farmer,
    require_officer,
    require_role,
    get_current_farmer,
    get_current_officer,
    RoleChecker,
)

__all__ = [
    "get_db",
    "get_current_user",
    "require_farmer",
    "require_officer",
    "require_role",
    "get_current_farmer",
    "get_current_officer",
    "RoleChecker",
]

