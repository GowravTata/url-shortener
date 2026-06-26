"""Database model for shortened URLs."""

from sqlalchemy import (BigInteger, Boolean, Column, DateTime, ForeignKey,
                        Integer, Text)
from sqlalchemy.sql import func

from app.core.db import Base


class URLModel(Base):
    """Stores a shortened URL and its lifecycle metadata."""

    __tablename__ = "urls"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True, index=True)
    original_url = Column(Text, nullable=False)
    short_code = Column(Text, unique=True, nullable=False, index=True)
    created_at = Column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    expires_at = Column(DateTime(timezone=True), nullable=False, index=True)
    last_accessed = Column(DateTime(timezone=True), nullable=True)
    is_disabled = Column(Boolean, default=False, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False, index=True)
    deleted_at = Column(DateTime(timezone=True), nullable=True)
    deleted_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    click_count = Column(BigInteger, default=0)
