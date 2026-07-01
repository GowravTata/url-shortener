from typing import Dict, Literal

from fastapi import APIRouter, Depends, Query, Request
from sqlalchemy.orm import Session

from app.core.config import CREATE, DELETE, INFO, IP, PATCH, USER, USERINFO
from app.core.db import get_db
from app.core.dependencies import get_current_user_id, rate_limit_dependency
from app.core.logging import AppLogger
from app.schemas.url import (BulkCreateRequest, BulkDeleteRequest,
                             BulkPatchRequest, PatchRequest, ShortenRequest)
from app.services.url.bulk_create import shorten_bulk_url
from app.services.url.bulk_delete import delete_bulk_urls
from app.services.url.bulk_patch import patch_bulk_urls
from app.services.url.create import shorten_url
from app.services.url.delete import delete_short_url
from app.services.url.info import get_short_code_info
from app.services.url.patch import patch_short_url
from app.services.url.restore import restore_short_code
from app.services.url.user_urls import get_all_urls

url_router = APIRouter(tags=["URL Management"], prefix="/v1/urls")
logger = AppLogger().get_logger()


@url_router.post(
    "/",
    summary="Creates Short URL",
    description="Convert a Orignal URL into a short one",
    dependencies=[rate_limit_dependency(scope=CREATE, identifier_type=USER)],
)
async def shorten(
    request: Request,
    payload: ShortenRequest,
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_user_id),
) -> Dict:
    """Accept a long URL and return a shortened version with an optional custom alias and expiry."""
    logger.info(f"Shorten request for user_id={user_id}")
    base_url = str(request.base_url).rstrip("/")
    return shorten_url(
        original_url=payload.original_url,
        custom_alias=payload.custom_alias,
        expiry=payload.expiry,
        user_id=user_id,
        db=db,
        base_url=base_url
    )


@url_router.post(
    "/bulk",
    summary="Creates Short URLs in Bulk",
    description="Convert multiple original URLs into short ones",
    dependencies=[rate_limit_dependency(scope=CREATE, identifier_type=USER)],
)
async def shorten_bulk(
    payload: BulkCreateRequest,
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_user_id),
) -> Dict:
    """Accept a list of long URLs and return shortened versions with optional custom aliases and expiry."""
    logger.info(
        f"Bulk shorten request for user_id={user_id} "
        f"count={len(payload.urls)}"
    )
    return shorten_bulk_url(
        payload=payload.urls,
        user_id=user_id,
        db=db,
    )


@url_router.delete(
    "/bulk",
    summary="Deletes Short URLs in Bulk",
    description="Delete Multiple Short Codes",
    dependencies=[rate_limit_dependency(scope=DELETE, identifier_type=USER)],
)
async def delete_bulk(
    payload: BulkDeleteRequest,
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_user_id),
) -> Dict:
    """Accept a list of long URLs and status of deletion."""
    # logger.info(
    #     f"Bulk delete request for user_id={user_id} " f"count={BulkDeleteRequest.dict}"
    # )
    return delete_bulk_urls(
        payload=payload.short_codes,
        user_id=user_id,
        db=db,
    )


@url_router.patch(
    "/bulk",
    summary="Patches the URLs in Bulk",
    description="Patches Multiple Short Codes",
    dependencies=[rate_limit_dependency(scope=PATCH, identifier_type=USER)],
)
async def patch_bulk(
    payload: BulkPatchRequest,
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_user_id),
):
    return patch_bulk_urls(
        payload=payload.short_codes,
        disable=payload.disable,
        expiry=payload.expires_at,
        user_id=user_id,
        db=db,
    )


@url_router.get(
    "/",
    summary="Get URL Related to a User",
    description="Retrieve the Orignal URL for a given user if exists",
    dependencies=[rate_limit_dependency(scope=USERINFO, identifier_type=IP)],
)
async def gets_user_url(
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db),
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    order: Literal["asc", "desc"] = "desc",
    short_code: str | None = None,
    status: str = Query(),
) -> Dict:
    """Return all active short URLs belonging to the authenticated user."""
    logger.info(f"List URLs request for user_id={user_id}")
    return get_all_urls(
        user_id=user_id,
        page=page,
        limit=limit,
        db=db,
        order=order,
        search=short_code,
    )


@url_router.delete(
    "/{short_code}",
    summary="Delete Short URL",
    description="Delete a Short URL and its corresponding Orignal URL "
    "from the database and cache",
    dependencies=[rate_limit_dependency(scope=DELETE, identifier_type=USER)],
)
async def deletes_short_url(
    short_code: str,
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db),
) -> Dict:
    """Soft-delete a short URL owned by the authenticated user and remove it from the cache."""
    logger.info(
        f"Delete short URL request for user_id={user_id} "
        f"short_code={short_code}"
    )
    return delete_short_url(user_id=user_id, short_code=short_code, db=db)


@url_router.get(
    "/{short_code}",
    summary="Get Short URL metadata",
    description="Retrieve information about a short URL, including its "
    "corresponding Orignal URL and expiry date",
    dependencies=[rate_limit_dependency(scope=INFO, identifier_type=IP)],
)
async def gets_short_code_info(
    short_code: str,
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db),
) -> Dict:
    """Return metadata (original URL, expiry, status) for a short URL owned by the authenticated user."""
    logger.info(
        f"Info request for user_id={user_id} " f"short_code={short_code}"
    )
    return get_short_code_info(short_code=short_code, user_id=user_id, db=db)


@url_router.patch(
    "/{short_code}",
    summary="Patch Short Code",
    description="Patch the short code in the database",
    dependencies=[rate_limit_dependency(scope=PATCH, identifier_type=USER)],
)
async def patch_url_short_code(
    payload: PatchRequest,
    short_code: str,
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db),
):
    """Update the expiry date and/or disabled state of an existing short URL."""
    logger.info(
        f"Patch request for user_id={user_id} " f"short_code={short_code}"
    )
    return patch_short_url(
        short_code=short_code,
        expires_at=payload.expires_at,
        disable=payload.disable,
        user_id=user_id,
        db=db,
    )


@url_router.post(
    "/{short_code}/restore",
    summary="API To restore the deleted Short Code",
)
async def restore_url(
    short_code: str,
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db),
):
    logger.info(
        f"Restore request for user_id={user_id} for short code {short_code}"
    )
    return restore_short_code(user_id=user_id, short_code=short_code, db=db)
