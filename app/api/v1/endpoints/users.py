from datetime import datetime
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, EmailStr
from sqlalchemy.orm import Session

from app.api.v1.deps import get_current_user
from app.core.database import get_db

router = APIRouter()


# Pydantic schemas for user operations
class UserBase(BaseModel):
    """Base user schema."""

    email: str
    full_name: str
    department: str | None = None
    position: str | None = None


class UserCreate(UserBase):
    """Schema for creating a new user."""

    password: str


class UserResponse(UserBase):
    """Schema for user responses."""

    id: int
    created_at: datetime
    is_active: bool = True

    class Config:
        from_attributes = True


class UserUpdate(BaseModel):
    """Schema for updating user information."""

    full_name: str | None = None
    department: str | None = None
    position: str | None = None
    is_active: bool | None = None


# Demo data for demonstration purposes
DEMO_USERS = [
    {
        "id": 1,
        "email": "john.doe@company.com",
        "full_name": "John Doe",
        "department": "Engineering",
        "position": "Senior Software Engineer",
        "created_at": datetime.utcnow(),
        "is_active": True,
    },
    {
        "id": 2,
        "email": "jane.smith@company.com",
        "full_name": "Jane Smith",
        "department": "HR",
        "position": "HR Manager",
        "created_at": datetime.utcnow(),
        "is_active": True,
    },
    {
        "id": 3,
        "email": "bob.wilson@company.com",
        "full_name": "Bob Wilson",
        "department": "Marketing",
        "position": "Marketing Specialist",
        "created_at": datetime.utcnow(),
        "is_active": False,
    },
]


@router.get("/users", response_model=list[UserResponse])
async def get_users(
    skip: int = 0,
    limit: int = 100,
    active_only: bool = False,
    current_user: dict = Depends(get_current_user),
):
    """Get list of users with optional filtering."""
    users = DEMO_USERS

    if active_only:
        users = [user for user in users if user["is_active"]]

    return users[skip : skip + limit]


@router.get("/users/{user_id}", response_model=UserResponse)
async def get_user(user_id: int, current_user: dict = Depends(get_current_user)):
    """Get a specific user by ID."""
    user = next((user for user in DEMO_USERS if user["id"] == user_id), None)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )

    return user


@router.post("/users", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def create_user(user: UserCreate, current_user: dict = Depends(get_current_user)):
    """Create a new user."""
    # Check if user already exists
    if any(u["email"] == user.email for u in DEMO_USERS):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User with this email already exists",
        )

    # Create new user (in a real app, you'd save to database)
    new_user = {
        "id": max(u["id"] for u in DEMO_USERS) + 1,
        "email": user.email,
        "full_name": user.full_name,
        "department": user.department,
        "position": user.position,
        "created_at": datetime.utcnow(),
        "is_active": True,
    }

    # In a real application, you would save to database here
    # DEMO_USERS.append(new_user)

    return new_user


@router.get("/users/me", response_model=UserResponse)
async def get_current_user_info(current_user: dict = Depends(get_current_user)):
    """Get current user information."""
    # In a real app, you'd fetch from database using current_user["user_id"]
    return {
        "id": 1,
        "email": current_user["email"],
        "full_name": "Demo User",
        "department": "IT",
        "position": "Developer",
        "created_at": datetime.utcnow(),
        "is_active": True,
    }
