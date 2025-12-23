from typing import Optional, List
from datetime import datetime, timedelta
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import or_, and_

from app.database import get_db
from app.models import Item, ItemType, Favorite, ItemTag, Tag, MenaAnalysis
from app.schemas import ItemResponse, ItemListResponse, ManualItemCreate, TagResponse, NoteResponse
from app.auth import get_current_user, get_optional_user
from app.models import User
from app.services.ingestion import create_item_hash
from app.services.analysis import enqueue_analysis

router = APIRouter()


def item_to_response(item: Item, user: Optional[User] = None) -> ItemResponse:
    """Convert Item model to response with user-specific data."""
    is_favorited = False
    user_tags = []
    user_notes = []
    
    if user:
        # Check if favorited
        for fav in item.favorites:
            if fav.user_id == user.id:
                is_favorited = True
                break
        
        # Get user's tags for this item
        for item_tag in item.item_tags:
            if item_tag.tag.user_id == user.id:
                user_tags.append(TagResponse(
                    id=item_tag.tag.id,
                    name=item_tag.tag.name,
                    color=item_tag.tag.color,
                ))
        
        # Get user's notes for this item
        for note in item.notes:
            if note.user_id == user.id:
                user_notes.append(NoteResponse(
                    id=note.id,
                    body=note.body,
                    created_at=note.created_at,
                    updated_at=note.updated_at,
                ))
    
    return ItemResponse(
        id=item.id,
        type=item.type,
        title=item.title,
        company_name=item.company_name,
        url=item.url,
        source_id=item.source_id,
        source_name=item.source.name if item.source else None,
        published_at=item.published_at,
        summary=item.summary,
        hidden=item.hidden,
        created_at=item.created_at,
        funding_details=item.funding_details,
        company_details=item.company_details,
        mena_analysis=item.mena_analysis,
        is_favorited=is_favorited,
        tags=user_tags,
        notes=user_notes,
    )


@router.get("", response_model=ItemListResponse)
def list_items(
    type: Optional[ItemType] = None,
    q: Optional[str] = None,
    min_score: Optional[int] = Query(None, ge=0, le=100),
    tag: Optional[int] = None,
    date_range: Optional[str] = Query(None, regex="^(24h|7d|30d)$"),
    show_hidden: bool = False,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_optional_user),
):
    """List items with filters."""
    query = db.query(Item).options(
        joinedload(Item.source),
        joinedload(Item.funding_details),
        joinedload(Item.company_details),
        joinedload(Item.mena_analysis),
        joinedload(Item.favorites),
        joinedload(Item.item_tags).joinedload(ItemTag.tag),
        joinedload(Item.notes),
    )
    
    # Filter by type
    if type:
        query = query.filter(Item.type == type)
    
    # Filter hidden
    if not show_hidden:
        query = query.filter(Item.hidden == False)
    
    # Search
    if q:
        search_term = f"%{q}%"
        query = query.filter(
            or_(
                Item.title.ilike(search_term),
                Item.company_name.ilike(search_term),
                Item.summary.ilike(search_term),
            )
        )
    
    # Filter by min score
    if min_score is not None:
        query = query.join(MenaAnalysis).filter(MenaAnalysis.fit_score >= min_score)
    
    # Filter by tag
    if tag and current_user:
        query = query.join(ItemTag).filter(ItemTag.tag_id == tag)
    
    # Filter by date range
    if date_range:
        now = datetime.utcnow()
        if date_range == "24h":
            cutoff = now - timedelta(hours=24)
        elif date_range == "7d":
            cutoff = now - timedelta(days=7)
        elif date_range == "30d":
            cutoff = now - timedelta(days=30)
        query = query.filter(Item.published_at >= cutoff)
    
    # Order by published date
    query = query.order_by(Item.published_at.desc().nullslast(), Item.created_at.desc())
    
    # Get total count
    total = query.count()
    
    # Paginate
    offset = (page - 1) * page_size
    items = query.offset(offset).limit(page_size).all()
    
    # Convert to responses
    item_responses = [item_to_response(item, current_user) for item in items]
    
    total_pages = (total + page_size - 1) // page_size
    
    return ItemListResponse(
        items=item_responses,
        total=total,
        page=page,
        page_size=page_size,
        total_pages=total_pages,
    )


@router.get("/{item_id}", response_model=ItemResponse)
def get_item(
    item_id: int,
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_optional_user),
):
    """Get a single item by ID."""
    item = db.query(Item).options(
        joinedload(Item.source),
        joinedload(Item.funding_details),
        joinedload(Item.company_details),
        joinedload(Item.mena_analysis),
        joinedload(Item.favorites),
        joinedload(Item.item_tags).joinedload(ItemTag.tag),
        joinedload(Item.notes),
    ).filter(Item.id == item_id).first()
    
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    
    return item_to_response(item, current_user)


@router.post("", response_model=ItemResponse)
def create_manual_item(
    item_data: ManualItemCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Create a manual item (user submission)."""
    # Generate hash for dedup
    hash_value = create_item_hash(
        url=item_data.url,
        title=item_data.title,
        published_at=None,
    )
    
    # Check for duplicate
    existing = db.query(Item).filter(Item.hash == hash_value).first()
    if existing:
        raise HTTPException(
            status_code=400,
            detail="This item already exists",
        )
    
    # Create item
    item = Item(
        type=item_data.type,
        title=item_data.title,
        company_name=item_data.company_name,
        url=item_data.url,
        summary=item_data.summary,
        hash=hash_value,
        published_at=datetime.utcnow(),
    )
    db.add(item)
    db.flush()
    
    # Add company details if provided
    if item_data.type == ItemType.COMPANY and item_data.one_liner:
        from app.models import CompanyDetails
        company_details = CompanyDetails(
            item_id=item.id,
            one_liner=item_data.one_liner,
        )
        db.add(company_details)
    
    db.commit()
    db.refresh(item)
    
    # Enqueue analysis
    enqueue_analysis(item.id)
    
    return item_to_response(item, current_user)


@router.patch("/{item_id}/hide")
def hide_item(
    item_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Hide an item from the feed."""
    item = db.query(Item).filter(Item.id == item_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    
    item.hidden = True
    db.commit()
    
    return {"message": "Item hidden"}


@router.patch("/{item_id}/unhide")
def unhide_item(
    item_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Unhide an item."""
    item = db.query(Item).filter(Item.id == item_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    
    item.hidden = False
    db.commit()
    
    return {"message": "Item unhidden"}

