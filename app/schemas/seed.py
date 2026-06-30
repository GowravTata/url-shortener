from pydantic import BaseModel, Field


class SeedUsersRequest(BaseModel):
    count: int = Field(
        default=100,
        ge=1,
        le=10000,
        description="Number of users to create",
    )


class SeedUsersResponse(BaseModel):
    requested: int
    created: int
    skipped: int
    message: str