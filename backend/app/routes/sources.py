from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Source, User
from app.schemas import SourceCreate, SourceUpdate, SourceResponse
from app.auth import get_current_user

router = APIRouter()


@router.get("", response_model=List[SourceResponse])
def list_sources(
    db: Session = Depends(get_db),
):
    """List all sources."""
    sources = db.query(Source).order_by(Source.name).all()
    return sources


@router.get("/{source_id}", response_model=SourceResponse)
def get_source(
    source_id: int,
    db: Session = Depends(get_db),
):
    """Get a source by ID."""
    source = db.query(Source).filter(Source.id == source_id).first()
    if not source:
        raise HTTPException(status_code=404, detail="Source not found")
    return source


@router.post("", response_model=SourceResponse)
def create_source(
    source_data: SourceCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Create a new source."""
    # Check if URL already exists
    existing = db.query(Source).filter(Source.url == source_data.url).first()
    if existing:
        raise HTTPException(status_code=400, detail="Source URL already exists")
    
    source = Source(
        name=source_data.name,
        type=source_data.type,
        url=source_data.url,
        category=source_data.category,
    )
    db.add(source)
    db.commit()
    db.refresh(source)
    
    return source


@router.patch("/{source_id}", response_model=SourceResponse)
def update_source(
    source_id: int,
    source_data: SourceUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Update a source."""
    source = db.query(Source).filter(Source.id == source_id).first()
    if not source:
        raise HTTPException(status_code=404, detail="Source not found")
    
    if source_data.name is not None:
        source.name = source_data.name
    if source_data.url is not None:
        source.url = source_data.url
    if source_data.enabled is not None:
        source.enabled = source_data.enabled
    if source_data.category is not None:
        source.category = source_data.category
    
    db.commit()
    db.refresh(source)
    
    return source


@router.delete("/{source_id}")
def delete_source(
    source_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Delete a source."""
    source = db.query(Source).filter(Source.id == source_id).first()
    if not source:
        raise HTTPException(status_code=404, detail="Source not found")
    
    db.delete(source)
    db.commit()
    
    return {"message": "Source deleted"}

