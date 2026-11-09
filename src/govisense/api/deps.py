"""
FastAPI Dependencies for GoviSense API (Task 11)
Provides database sessions, user identity, and RBAC authorization dependencies.
"""

from govisense.db.session import get_db, get_db_session
from govisense.api.auth import (
    get_current_user,
    require_farmer,
    require_officer,
    require_admin,
    require_officer_or_admin,
    require_authenticated,
    require_role,
    get_current_farmer,
    get_current_officer,
    get_current_admin,
    RoleChecker,
    decode_token,
    oauth2_scheme,
)

__all__ = [
    "get_db",
    "get_db_session",
    "get_current_user",
    "require_farmer",
    "require_officer",
    "require_admin",
    "require_officer_or_admin",
    "require_authenticated",
    "require_role",
    "get_current_farmer",
    "get_current_officer",
    "get_current_admin",
    "RoleChecker",
    "decode_token",
    "oauth2_scheme",
]
