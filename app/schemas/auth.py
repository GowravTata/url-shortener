"""Authentication request schemas."""

from typing import AnyStr

from pydantic import BaseModel, ConfigDict, EmailStr


class UserRequest(BaseModel):
    """Request payload for user registration and login."""

    email: EmailStr
    password: AnyStr

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "email": "gowravtata@fastapi.com",
                "password": "secretpassword",
            }
        }
    )
