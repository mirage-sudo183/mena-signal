from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import IngestRun, User
from app.schemas import IngestRunResponse, IngestTriggerResponse
from app.auth import get_current_user
from app.services.ingestion import trigger_ingestion

router = APIRouter()


@router.post("/run", response_model=IngestTriggerResponse)
def trigger_ingest(
    source_id: Optional[int] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Manually trigger ingestion."""
    job_id = trigger_ingestion(source_id)
    return IngestTriggerResponse(
        message="Ingestion job queued",
        job_id=job_id,
    )


@router.get("/runs", response_model=List[IngestRunResponse])
def list_ingest_runs(
    source_id: Optional[int] = None,
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
):
    """List recent ingestion runs."""
    query = db.query(IngestRun).order_by(IngestRun.started_at.desc())
    
    if source_id:
        query = query.filter(IngestRun.source_id == source_id)
    
    runs = query.limit(limit).all()
    return runs

