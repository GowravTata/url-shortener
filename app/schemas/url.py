"""Schemas for URL creation and partial updates."""

from datetime import datetime
from typing import Annotated, Dict, List, Optional

from pydantic import BaseModel, ConfigDict, Field, HttpUrl, field_validator

from app.core.config import RESERVED_ALIASES


class ShortenRequest(BaseModel):
    """Request payload for creating a short URL."""

    original_url: HttpUrl
    custom_alias: Annotated[
        str | None, "Optional custom alias for the short URL"
    ] = None
    expiry: Annotated[
        datetime | None, "Optional expiration time for the short URL"
    ] = None

    @field_validator("custom_alias")
    @classmethod
    def validate_custom_alias(cls, value):
        if value is None:
            return value
        value = value.lower()
        if value in RESERVED_ALIASES:
            raise ValueError("This alias is reserved and cannot be used")
        return value

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "original_url": "https://www.amazon.com",  # Optional
                "custom_alias": "az",
                "expiry": "2026-04-30T23:59:59",
            }
        }
    )


class PatchRequest(BaseModel):
    """Request payload for updating URL expiry and status."""

    expires_at: Optional[datetime] = None
    disable: Optional[bool] = None
    model_config = ConfigDict(
        json_schema_extra={
            "example": {"expires_at": "2026-12-31T11:59:59", "disable": True}
        }
    )


class BulkCreateRequest(BaseModel):
    urls: List[Dict]
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "urls": [
                    {
                        "custom_alias": "az",
                        "expiry": "2026-12-31T23:59:59",
                        "original_url": "https://www.amazon.com",
                    },
                    {
                        "custom_alias": "flip",
                        "expiry": "2026-12-31T23:59:59",
                        "original_url": "https://www.twitter.com",
                    },
                ]
            }
        }
    )


class BulkDeleteRequest(BaseModel):
    short_codes: List[str] = Field(
        min_length=1,
        max_length=100000,
        description="List of short codes to delete",
        examples=[["az", "flip", "intel"]],
    )

    @field_validator("short_codes")
    @classmethod
    def validate_duplicates(cls, value):
        if len(value) != len(set(value)):
            raise ValueError("Duplicate short codes are not allowed")
        return value


class BulkPatchRequest(BaseModel):
    short_codes: List[str] = Field(examples=[["az", "flip", "intel"]])
    disable: bool | None = Field(default=None, examples=[True])
    expires_at: datetime | None = Field(
        default=None, examples=["2026-05-30T00:00:00"]
    )
