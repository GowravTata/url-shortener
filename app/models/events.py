from sqlalchemy import UUID, Boolean, Column, DateTime, Float, Integer, Text
from sqlalchemy.sql import func

from app.core.db import Base


class ClickEvents(Base):
    """Table for storing the Click Events"""

    __tablename__ = "click_events"
    id = Column(Integer, primary_key=True, autoincrement=True)
    event_id = Column(UUID, nullable=False, unique=True)
    user_id = Column(Integer, nullable=False)
    short_code = Column(Text, nullable=False, index=True)
    clicked_at = Column(DateTime(timezone=True), nullable=False, index=False)
    ip_address = Column(Text, nullable=True)
    country = Column(Text, nullable=True, index=True)
    city = Column(Text, nullable=True)
    browser = Column(Text, nullable=True, index=True)
    os = Column(Text, nullable=True)
    device_type = Column(Text, nullable=True, index=True)
    referer = Column(Text, nullable=True)
    is_bot = Column(Boolean, default=False, nullable=False, index=True)
    cache_hit = Column(Boolean, nullable=False)
    redirect_latency_ms = Column(Float, nullable=False)
    topic = Column(Text, nullable=False)
    partition = Column(Text, nullable=False)
    message_offset = Column(Text, nullable=False)
    message_timestamp = Column(Text, nullable=False)


class ClickArchive(Base):
    __tablename__ = "click_archive"
    id = Column(Integer, primary_key=True, autoincrement=True)
    event_id = Column(UUID, nullable=False, unique=True)
    event_payload = Column(Text, nullable=False)
    topic = Column(Text, nullable=False)
    partition = Column(Text, nullable=False)
    message_offset = Column(Text, nullable=False)
    message_timestamp = Column(Text, nullable=False)
    archived_at = Column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
