from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.core.db import get_db
from app.models.user import Users
from app.models.url import URLModel

admin_router = APIRouter(prefix="/v1/admin/inspect", tags=["Inspect"])


@admin_router.get("/summary")
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


@admin_router.get("/users")
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


@admin_router.get("/urls")
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


@admin_router.get("/top-clicked")
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
