from datetime import datetime
from typing import Optional
from sqlalchemy import (
    Column, String, Integer, Float, Text, Boolean, DateTime, 
    ForeignKey, JSON, Index, Enum as SQLEnum
)
from sqlalchemy.orm import DeclarativeBase, relationship
import enum


class Base(DeclarativeBase):
    pass


class SourceType(str, enum.Enum):
    RSS = "rss"
    API = "api"
    MANUAL = "manual"


class ItemType(str, enum.Enum):
    FUNDING = "funding"
    COMPANY = "company"


class IngestStatus(str, enum.Enum):
    RUNNING = "running"
    SUCCESS = "success"
    FAILED = "failed"


class Source(Base):
    __tablename__ = "sources"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(255), nullable=False)
    type = Column(SQLEnum(SourceType, values_callable=lambda x: [e.value for e in x]), nullable=False, default=SourceType.RSS)
    url = Column(Text, nullable=False)
    enabled = Column(Boolean, default=True)
    category = Column(String(100), nullable=True)  # funding, companies, news
    created_at = Column(DateTime, default=datetime.utcnow)
    
    items = relationship("Item", back_populates="source")
    ingest_runs = relationship("IngestRun", back_populates="source")


class Item(Base):
    __tablename__ = "items"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    type = Column(SQLEnum(ItemType, values_callable=lambda x: [e.value for e in x]), nullable=False)
    title = Column(String(500), nullable=False)
    company_name = Column(String(255), nullable=True)
    url = Column(Text, nullable=False)
    source_id = Column(Integer, ForeignKey("sources.id"), nullable=True)
    published_at = Column(DateTime, nullable=True)
    summary = Column(Text, nullable=True)
    raw_json = Column(JSON, nullable=True)
    hash = Column(String(64), nullable=False, unique=True, index=True)
    hidden = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    source = relationship("Source", back_populates="items")
    funding_details = relationship("FundingDetails", back_populates="item", uselist=False)
    company_details = relationship("CompanyDetails", back_populates="item", uselist=False)
    mena_analysis = relationship("MenaAnalysis", back_populates="item", uselist=False)
    favorites = relationship("Favorite", back_populates="item")
    item_tags = relationship("ItemTag", back_populates="item")
    notes = relationship("Note", back_populates="item")
    
    __table_args__ = (
        Index('ix_items_type_published', 'type', 'published_at'),
        Index('ix_items_company_name', 'company_name'),
    )


class FundingDetails(Base):
    __tablename__ = "funding_details"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    item_id = Column(Integer, ForeignKey("items.id"), unique=True, nullable=False)
    round_type = Column(String(50), nullable=True)  # seed, series_a, etc.
    amount_usd = Column(Float, nullable=True)
    investors = Column(JSON, nullable=True)  # List of investor names
    geography = Column(String(100), nullable=True)
    
    item = relationship("Item", back_populates="funding_details")


class CompanyDetails(Base):
    __tablename__ = "company_details"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    item_id = Column(Integer, ForeignKey("items.id"), unique=True, nullable=False)
    one_liner = Column(Text, nullable=True)
    category = Column(String(100), nullable=True)
    stage_hint = Column(String(50), nullable=True)  # early, growth, etc.
    geography = Column(String(100), nullable=True)
    
    item = relationship("Item", back_populates="company_details")


class MenaAnalysis(Base):
    __tablename__ = "mena_analysis"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    item_id = Column(Integer, ForeignKey("items.id"), unique=True, nullable=False)
    fit_score = Column(Integer, nullable=False)  # 0-100
    mena_summary = Column(Text, nullable=False)
    rubric_json = Column(JSON, nullable=True)  # Breakdown scores
    model_name = Column(String(100), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    item = relationship("Item", back_populates="mena_analysis")


class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    email = Column(String(255), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    favorites = relationship("Favorite", back_populates="user")
    tags = relationship("Tag", back_populates="user")
    notes = relationship("Note", back_populates="user")


class Favorite(Base):
    __tablename__ = "favorites"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    item_id = Column(Integer, ForeignKey("items.id"), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    user = relationship("User", back_populates="favorites")
    item = relationship("Item", back_populates="favorites")
    
    __table_args__ = (
        Index('ix_favorites_user_item', 'user_id', 'item_id', unique=True),
    )


class Tag(Base):
    __tablename__ = "tags"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    name = Column(String(100), nullable=False)
    color = Column(String(7), nullable=True)  # hex color
    created_at = Column(DateTime, default=datetime.utcnow)
    
    user = relationship("User", back_populates="tags")
    item_tags = relationship("ItemTag", back_populates="tag")
    
    __table_args__ = (
        Index('ix_tags_user_name', 'user_id', 'name', unique=True),
    )


class ItemTag(Base):
    __tablename__ = "item_tags"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    item_id = Column(Integer, ForeignKey("items.id"), nullable=False)
    tag_id = Column(Integer, ForeignKey("tags.id"), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    item = relationship("Item", back_populates="item_tags")
    tag = relationship("Tag", back_populates="item_tags")
    
    __table_args__ = (
        Index('ix_item_tags_item_tag', 'item_id', 'tag_id', unique=True),
    )


class Note(Base):
    __tablename__ = "notes"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    item_id = Column(Integer, ForeignKey("items.id"), nullable=False)
    body = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    user = relationship("User", back_populates="notes")
    item = relationship("Item", back_populates="notes")


class IngestRun(Base):
    __tablename__ = "ingest_runs"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    source_id = Column(Integer, ForeignKey("sources.id"), nullable=True)
    started_at = Column(DateTime, default=datetime.utcnow)
    finished_at = Column(DateTime, nullable=True)
    status = Column(SQLEnum(IngestStatus, values_callable=lambda x: [e.value for e in x]), default=IngestStatus.RUNNING)
    items_added = Column(Integer, default=0)
    error = Column(Text, nullable=True)
    
    source = relationship("Source", back_populates="ingest_runs")

