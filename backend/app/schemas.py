from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, EmailStr, Field
from app.models import SourceType, ItemType


# Auth schemas
class UserCreate(BaseModel):
    email: EmailStr
    password: str = Field(min_length=6)


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class UserResponse(BaseModel):
    id: int
    email: str
    created_at: datetime

    class Config:
        from_attributes = True


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


# Source schemas
class SourceCreate(BaseModel):
    name: str
    type: SourceType = SourceType.RSS
    url: str
    category: Optional[str] = None


class SourceUpdate(BaseModel):
    name: Optional[str] = None
    url: Optional[str] = None
    enabled: Optional[bool] = None
    category: Optional[str] = None


class SourceResponse(BaseModel):
    id: int
    name: str
    type: SourceType
    url: str
    enabled: bool
    category: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True


# Item schemas
class FundingDetailsResponse(BaseModel):
    round_type: Optional[str]
    amount_usd: Optional[float]
    investors: Optional[List[str]]
    geography: Optional[str]

    class Config:
        from_attributes = True


class CompanyDetailsResponse(BaseModel):
    one_liner: Optional[str]
    category: Optional[str]
    stage_hint: Optional[str]
    geography: Optional[str]

    class Config:
        from_attributes = True


class MenaAnalysisResponse(BaseModel):
    fit_score: int
    mena_summary: str
    rubric_json: Optional[dict]
    model_name: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True


class TagResponse(BaseModel):
    id: int
    name: str
    color: Optional[str]

    class Config:
        from_attributes = True


class NoteResponse(BaseModel):
    id: int
    body: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class ItemResponse(BaseModel):
    id: int
    type: ItemType
    title: str
    company_name: Optional[str]
    url: str
    source_id: Optional[int]
    source_name: Optional[str] = None
    published_at: Optional[datetime]
    summary: Optional[str]
    hidden: bool
    created_at: datetime
    funding_details: Optional[FundingDetailsResponse] = None
    company_details: Optional[CompanyDetailsResponse] = None
    mena_analysis: Optional[MenaAnalysisResponse] = None
    is_favorited: bool = False
    tags: List[TagResponse] = []
    notes: List[NoteResponse] = []

    class Config:
        from_attributes = True


class ItemListResponse(BaseModel):
    items: List[ItemResponse]
    total: int
    page: int
    page_size: int
    total_pages: int


class ManualItemCreate(BaseModel):
    type: ItemType
    title: str
    company_name: Optional[str] = None
    url: str
    summary: Optional[str] = None
    one_liner: Optional[str] = None  # For companies


# Favorite schemas
class FavoriteResponse(BaseModel):
    id: int
    item_id: int
    created_at: datetime

    class Config:
        from_attributes = True


# Tag schemas
class TagCreate(BaseModel):
    name: str
    color: Optional[str] = None


class TagAssign(BaseModel):
    tag_ids: List[int]


# Note schemas
class NoteCreate(BaseModel):
    body: str


class NoteUpdate(BaseModel):
    body: str


# Ingest schemas
class IngestRunResponse(BaseModel):
    id: int
    source_id: Optional[int]
    started_at: datetime
    finished_at: Optional[datetime]
    status: str
    items_added: int
    error: Optional[str]

    class Config:
        from_attributes = True


class IngestTriggerResponse(BaseModel):
    message: str
    job_id: Optional[str] = None

