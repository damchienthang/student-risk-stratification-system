import hashlib
from enum import Enum
from fastapi import Request
from typing import Optional, Dict, Any

class UserRole(str, Enum):
    ADMIN = "lecturer"
    STUDENT = "student"
    GUEST = "external"

def hash_password(password: str) -> str:
    """Standard SHA256 hashing for passwords."""
    return hashlib.sha256(password.encode()).hexdigest()

def get_current_user(request: Request) -> Optional[Dict[str, Any]]:
    """
    Extract user session from cookie.
    In a real app, this would use JWT and check against the DB.
    """
    session = request.cookies.get("session_v2")
    if not session:
        return None
    try:
        # Format: role:username
        role_str, username = session.split(":", 1)
        return {"role": role_str, "username": username}
    except (ValueError, AttributeError):
        return None

def is_admin(user: Optional[Dict[str, Any]]) -> bool:
    return user is not None and user.get("role") == UserRole.ADMIN

def is_student(user: Optional[Dict[str, Any]]) -> bool:
    return user is not None and user.get("role") == UserRole.STUDENT

def is_guest(user: Optional[Dict[str, Any]]) -> bool:
    """Check if the user is an external/guest user with an account."""
    return user is not None and user.get("role") == UserRole.GUEST
