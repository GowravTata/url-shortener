from fastapi import APIRouter, Depends, Query
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.core.db import get_db
from app.models.url import URLModel
from app.models.user import Users
from app.services.admin.reset_service import reset_environment
from app.services.admin.seed_service import (create_urls, create_users,
                                             generate_clicks)

admin_router = APIRouter(prefix="/v1/admin", tags=["Admin"])
inspect_router = APIRouter(prefix="/v1/inspect", tags=["Inspect"])


@inspect_router.get("/summary")
def inspect_summary(db: Session = Depends(get_db)):
    total_users = db.query(func.count(Users.id)).scalar()

    total_urls = db.query(func.count(URLModel.id)).scalar()

    active_urls = (
        db.query(func.count(URLModel.id))
        .filter(URLModel.is_active == True)
        .scalar()
    )

    disabled_urls = (
        db.query(func.count(URLModel.id))
        .filter(URLModel.is_disabled == True)
        .scalar()
    )

    total_clicks = db.query(
        func.coalesce(func.sum(URLModel.click_count), 0)
    ).scalar()

    return {
        "users": total_users,
        "urls": total_urls,
        "active_urls": active_urls,
        "disabled_urls": disabled_urls,
        "total_clicks": total_clicks,
    }


@inspect_router.get("/users")
def inspect_users(
    limit: int = 20,
    db: Session = Depends(get_db),
):
    users = db.query(Users).limit(limit).all()
    return [
        {
            "id": user.id,
            "email": user.email,
            "created_at": user.created_at,
        }
        for user in users
    ]


@inspect_router.get("/urls")
def inspect_urls(
    limit: int = 20,
    db: Session = Depends(get_db),
):
    urls = db.query(URLModel).limit(limit).all()
    return [
        {
            "short_code": url.short_code,
            "original_url": url.original_url,
            "click_count": url.click_count,
            "active": url.is_active,
            "disabled": url.is_disabled,
            "expires_at": url.expires_at,
        }
        for url in urls
    ]


@inspect_router.get("/top-clicked")
def top_clicked(
    limit: int = 10,
    db: Session = Depends(get_db),
):
    urls = (
        db.query(URLModel)
        .order_by(URLModel.click_count.desc())
        .limit(limit)
        .all()
    )

    return [
        {
            "short_code": url.short_code,
            "click_count": url.click_count,
            "original_url": url.original_url,
        }
        for url in urls
    ]


@admin_router.post("/reset")
def reset(db: Session = Depends(get_db)):
    return reset_environment(db)


@admin_router.post("/seed/users")
def seed_users(
    count: int = Query(
        default=100,
        ge=1,
        le=100,
        description="Number of users to create (1-100)",
    )
):
    created = create_users(count)
    return {
        "requested": count,
        "created": created,
    }


@admin_router.post("/seed/urls")
def seed_urls(
    count: int = Query(
        default=1000,
        ge=1,
        le=1000,
        description="Number of URLs to create (1-1000)",
    )
):
    created = create_urls(count)
    return {
        "requested": count,
        "created": created,
    }


@admin_router.post("/seed/clicks")
def seed_clicks(
    count: int = Query(
        default=1000,
        ge=1,
        le=1000,
        description="Number of clicks to generate (1-1000)",
    )
):
    generated = generate_clicks(count)
    return {
        "requested": count,
        "generated": generated,
    }


@admin_router.post("/seed/all")
def seed_all(
    users: int = Query(
        default=100,
        ge=1,
        le=100,
        description="Number of users to create (1-100)",
    ),
    urls: int = Query(
        default=1000,
        ge=1,
        le=1000,
        description="Number of URLs to create (1-1000)",
    ),
    clicks: int = Query(
        default=1000,
        ge=1,
        le=1000,
        description="Number of clicks to generate (1-1000)",
    ),
):
    created_users = create_users(users)
    created_urls = create_urls(urls)
    generated_clicks = generate_clicks(clicks)
    return {
        "users_created": created_users,
        "urls_created": created_urls,
        "clicks_generated": generated_clicks,
    }
