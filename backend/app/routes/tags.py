from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Tag, ItemTag, Item, User
from app.schemas import TagCreate, TagResponse, TagAssign
from app.auth import get_current_user

router = APIRouter()


@router.get("", response_model=List[TagResponse])
def list_tags(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """List user's tags."""
    tags = db.query(Tag).filter(Tag.user_id == current_user.id).order_by(Tag.name).all()
    return tags


@router.post("", response_model=TagResponse)
def create_tag(
    tag_data: TagCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Create a new tag."""
    # Check if tag name exists for user
    existing = db.query(Tag).filter(
        Tag.user_id == current_user.id,
        Tag.name == tag_data.name,
    ).first()
    
    if existing:
        raise HTTPException(status_code=400, detail="Tag name already exists")
    
    tag = Tag(
        user_id=current_user.id,
        name=tag_data.name,
        color=tag_data.color,
    )
    db.add(tag)
    db.commit()
    db.refresh(tag)
    
    return tag


@router.delete("/{tag_id}")
def delete_tag(
    tag_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Delete a tag and all its associations."""
    tag = db.query(Tag).filter(
        Tag.id == tag_id,
        Tag.user_id == current_user.id,
    ).first()
    
    if not tag:
        raise HTTPException(status_code=404, detail="Tag not found")
    
    # Delete associations first
    db.query(ItemTag).filter(ItemTag.tag_id == tag_id).delete()
    
    # Delete tag
    db.delete(tag)
    db.commit()
    
    return {"message": "Tag deleted"}


@router.post("/items/{item_id}")
def assign_tags_to_item(
    item_id: int,
    tag_data: TagAssign,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Assign tags to an item (replaces existing tags)."""
    # Check item exists
    item = db.query(Item).filter(Item.id == item_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    
    # Verify all tags belong to user
    user_tag_ids = {t.id for t in db.query(Tag).filter(Tag.user_id == current_user.id).all()}
    for tag_id in tag_data.tag_ids:
        if tag_id not in user_tag_ids:
            raise HTTPException(status_code=400, detail=f"Tag {tag_id} not found")
    
    # Remove existing tags for this item from this user
    existing_item_tags = db.query(ItemTag).join(Tag).filter(
        ItemTag.item_id == item_id,
        Tag.user_id == current_user.id,
    ).all()
    for item_tag in existing_item_tags:
        db.delete(item_tag)
    
    # Add new tags
    for tag_id in tag_data.tag_ids:
        item_tag = ItemTag(item_id=item_id, tag_id=tag_id)
        db.add(item_tag)
    
    db.commit()
    
    return {"message": "Tags updated"}


@router.get("/items/{item_id}", response_model=List[TagResponse])
def get_item_tags(
    item_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get tags for an item (user's tags only)."""
    tags = db.query(Tag).join(ItemTag).filter(
        ItemTag.item_id == item_id,
        Tag.user_id == current_user.id,
    ).all()
    return tags

