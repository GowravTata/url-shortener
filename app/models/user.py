"""Database model for application users."""

from sqlalchemy import Boolean, Column, DateTime, Integer, Text
from sqlalchemy.sql import func

from app.core.db import Base


class Users(Base):
    """Represents a registered user account."""

    __tablename__ = "users"
    id = Column(
        Integer,
        primary_key=True,
        autoincrement=True,
        index=True)
    email = Column(Text, unique=True, nullable=False)
    password_hash = Column(Text, nullable=False)
    is_active = Column(Boolean, default=False)
    created_at = Column(
        DateTime(
            timezone=True),
        server_default=func.now())
