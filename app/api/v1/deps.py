from fastapi import Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.database import get_db


def get_current_user(db: Session = Depends(get_db)):
    """Dependency to get current authenticated user.

    For demo purposes, this is a placeholder. In a real application,
    you would implement JWT token validation here.
    """
    # TODO: Implement actual authentication
    return {"user_id": "demo-user", "email": "demo@example.com"}


def require_admin(current_user: dict = Depends(get_current_user)):
    """Dependency to require admin privileges."""
    # TODO: Implement actual admin check
    if current_user.get("email") != "admin@example.com":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Admin privileges required"
        )
    return current_user
