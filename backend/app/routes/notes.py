from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Note, Item, User
from app.schemas import NoteCreate, NoteUpdate, NoteResponse
from app.auth import get_current_user

router = APIRouter()


@router.get("/items/{item_id}", response_model=List[NoteResponse])
def get_item_notes(
    item_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get user's notes for an item."""
    notes = db.query(Note).filter(
        Note.item_id == item_id,
        Note.user_id == current_user.id,
    ).order_by(Note.created_at.desc()).all()
    return notes


@router.post("/items/{item_id}", response_model=NoteResponse)
def create_note(
    item_id: int,
    note_data: NoteCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Create a note for an item."""
    # Check item exists
    item = db.query(Item).filter(Item.id == item_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    
    note = Note(
        user_id=current_user.id,
        item_id=item_id,
        body=note_data.body,
    )
    db.add(note)
    db.commit()
    db.refresh(note)
    
    return note


@router.patch("/{note_id}", response_model=NoteResponse)
def update_note(
    note_id: int,
    note_data: NoteUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Update a note."""
    note = db.query(Note).filter(
        Note.id == note_id,
        Note.user_id == current_user.id,
    ).first()
    
    if not note:
        raise HTTPException(status_code=404, detail="Note not found")
    
    note.body = note_data.body
    db.commit()
    db.refresh(note)
    
    return note


@router.delete("/{note_id}")
def delete_note(
    note_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Delete a note."""
    note = db.query(Note).filter(
        Note.id == note_id,
        Note.user_id == current_user.id,
    ).first()
    
    if not note:
        raise HTTPException(status_code=404, detail="Note not found")
    
    db.delete(note)
    db.commit()
    
    return {"message": "Note deleted"}

