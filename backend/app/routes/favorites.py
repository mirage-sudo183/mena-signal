from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session, joinedload

from app.database import get_db
from app.models import Item, Favorite, ItemTag, User
from app.schemas import ItemResponse, ItemListResponse
from app.auth import get_current_user
from app.routes.items import item_to_response

router = APIRouter()


@router.get("", response_model=ItemListResponse)
def list_favorites(
    tag: Optional[int] = None,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """List user's favorited items."""
    query = db.query(Item).join(Favorite).filter(
        Favorite.user_id == current_user.id
    ).options(
        joinedload(Item.source),
        joinedload(Item.funding_details),
        joinedload(Item.company_details),
        joinedload(Item.mena_analysis),
        joinedload(Item.favorites),
        joinedload(Item.item_tags).joinedload(ItemTag.tag),
        joinedload(Item.notes),
    )
    
    # Filter by tag
    if tag:
        query = query.join(ItemTag).filter(ItemTag.tag_id == tag)
    
    # Order by favorite date
    query = query.order_by(Favorite.created_at.desc())
    
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


@router.post("/{item_id}")
def add_favorite(
    item_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Add an item to favorites."""
    # Check item exists
    item = db.query(Item).filter(Item.id == item_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    
    # Check if already favorited
    existing = db.query(Favorite).filter(
        Favorite.user_id == current_user.id,
        Favorite.item_id == item_id,
    ).first()
    
    if existing:
        return {"message": "Already favorited"}
    
    # Create favorite
    favorite = Favorite(user_id=current_user.id, item_id=item_id)
    db.add(favorite)
    db.commit()
    
    return {"message": "Added to favorites"}


@router.delete("/{item_id}")
def remove_favorite(
    item_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Remove an item from favorites."""
    favorite = db.query(Favorite).filter(
        Favorite.user_id == current_user.id,
        Favorite.item_id == item_id,
    ).first()
    
    if not favorite:
        raise HTTPException(status_code=404, detail="Favorite not found")
    
    db.delete(favorite)
    db.commit()
    
    return {"message": "Removed from favorites"}

