from datetime import datetime
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.core.database import get_db

router = APIRouter()


# Pydantic schemas for item operations
class ItemBase(BaseModel):
    """Base item schema."""

    title: str
    description: str | None = None
    category: str
    priority: str = "medium"


class ItemCreate(ItemBase):
    """Schema for creating a new item."""

    pass


class ItemResponse(ItemBase):
    """Schema for item responses."""

    id: int
    created_at: datetime
    updated_at: datetime | None = None
    created_by: str

    class Config:
        from_attributes = True


class ItemUpdate(BaseModel):
    """Schema for updating item information."""

    title: str | None = None
    description: str | None = None
    category: str | None = None
    priority: str | None = None


# Demo data for demonstration purposes
DEMO_ITEMS = [
    {
        "id": 1,
        "title": "Annual Performance Review",
        "description": "Conduct annual performance reviews for all employees",
        "category": "HR Process",
        "priority": "high",
        "created_at": datetime.utcnow(),
        "updated_at": None,
        "created_by": "hr-manager@company.com",
    },
    {
        "id": 2,
        "title": "Employee Onboarding",
        "description": "New employee onboarding process documentation",
        "category": "HR Process",
        "priority": "medium",
        "created_at": datetime.utcnow(),
        "updated_at": None,
        "created_by": "hr-manager@company.com",
    },
    {
        "id": 3,
        "title": "Training Program",
        "description": "Develop leadership training program",
        "category": "Training",
        "priority": "low",
        "created_at": datetime.utcnow(),
        "updated_at": None,
        "created_by": "training@company.com",
    },
]


@router.get("/items", response_model=list[ItemResponse])
async def get_items(
    skip: int = 0,
    limit: int = 100,
    category: str | None = None,
    priority: str | None = None,
):
    """Get list of items with optional filtering."""
    items = DEMO_ITEMS

    if category:
        items = [item for item in items if item["category"] == category]

    if priority:
        items = [item for item in items if item["priority"] == priority]

    return items[skip : skip + limit]


@router.get("/items/{item_id}", response_model=ItemResponse)
async def get_item(item_id: int):
    """Get a specific item by ID."""
    item = next((item for item in DEMO_ITEMS if item["id"] == item_id), None)

    if not item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Item not found"
        )

    return item


@router.post("/items", response_model=ItemResponse, status_code=status.HTTP_201_CREATED)
async def create_item(item: ItemCreate):
    """Create a new item."""
    new_item = {
        "id": max(i["id"] for i in DEMO_ITEMS) + 1,
        "title": item.title,
        "description": item.description,
        "category": item.category,
        "priority": item.priority,
        "created_at": datetime.utcnow(),
        "updated_at": None,
    }

    # In a real application, you would save to database here
    # DEMO_ITEMS.append(new_item)

    return new_item


@router.get("/items/categories", response_model=list[str])
async def get_categories():
    """Get list of available item categories."""
    categories = list({item["category"] for item in DEMO_ITEMS})
    return sorted(categories)


@router.get("/items/priorities", response_model=list[str])
async def get_priorities():
    """Get list of available priority levels."""
    priorities = list({item["priority"] for item in DEMO_ITEMS})
    return sorted(priorities)
