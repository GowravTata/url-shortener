from datetime import datetime, timedelta, timezone

from sqlalchemy import case, func, select
from sqlalchemy.orm import Session

from app.core.config import (CLICK_TREND_LIMIT, DELTA_FOR_ONE_DAY,
                             DELTA_FOR_ONE_MONTH, DELTA_FOR_ONE_WEEK,
                             LATEST_URLS_LIMIT, TOP_URLS_LIMIT)
from app.models.events import ClickEvents
from app.models.url import URLModel


def get_url_summaryies(user_id, db):
    stats = (
        db.query(
            func.count(URLModel.id).label("total_urls"),
            func.sum(case((URLModel.is_active == True, 1), else_=0)).label(
                "active_urls"
            ),
            func.sum(case((URLModel.is_disabled == True, 1), else_=0)).label(
                "disabled_urls"
            ),
            func.sum(case((URLModel.is_active == False, 1), else_=0)).label(
                "expired_urls"
            ),
            func.sum(URLModel.click_count).label("total_clicks"),
        )
        .filter(URLModel.user_id == user_id)
        .one()
    )

    return {
        "total_urls": stats.total_urls or 0,
        "active_urls": stats.active_urls or 0,
        "disabled_urls": stats.disabled_urls or 0,
        "expired_urls": stats.expired_urls or 0,
        "total_clicks": stats.total_clicks or 0,
    }


def get_url_summary(user_id, db):
    stats = (
        db.query(
            func.count(URLModel.id).label("total_urls"),
            func.sum(case((URLModel.is_active == True, 1), else_=0)).label(
                "active_urls"
            ),
            func.sum(
                case(
                    (
                        (
                                (URLModel.is_disabled == True)
                                & (URLModel.is_active == True)
                        ),
                        1,
                    ),
                    else_=0,
                )
            ).label("disabled_urls"),
            func.sum(case((URLModel.is_active == False, 1), else_=0)).label(
                "expired_urls"
            ),
            func.sum(URLModel.click_count).label("total_clicks"),
        )
        .filter(URLModel.user_id == user_id)
        .one()
    )
    return {
        "total_urls": stats.total_urls or 0,
        "active_urls": stats.active_urls or 0,
        "disabled_urls": stats.disabled_urls or 0,
        "expired_urls": stats.expired_urls or 0,
        "total_clicks": stats.total_clicks or 0,
    }


def unique_visitors(user_id, db):
    stmt = select(func.count(func.distinct(ClickEvents.ip_address))).filter(
        URLModel.user_id == user_id
    )
    return db.scalar(stmt)


def summary(user_id, db):
    summary = get_url_summary(user_id, db)
    summary["unique_visitors"] = unique_visitors(user_id, db)
    return summary


def clicks_count_per_day(user_id, db, time_delta_days=1):
    start = datetime.now(timezone.utc).replace(
        hour=0, minute=0, second=0, microsecond=0
    )
    end = start + timedelta(days=time_delta_days)

    stmt = (
        select(func.count())
        .where(ClickEvents.clicked_at >= start, ClickEvents.clicked_at < end)
        .filter(ClickEvents.user_id == user_id)
    )
    return db.scalar(stmt)


def recent_activity(user_id, db):
    return {
        "clicks_today": clicks_count_per_day(
            user_id, db, time_delta_days=DELTA_FOR_ONE_DAY
        ),
        "clicks_last_7_days": clicks_count_per_day(
            user_id, db, time_delta_days=DELTA_FOR_ONE_WEEK
        ),
        "clicks_last_30_days": clicks_count_per_day(
            user_id, db, time_delta_days=DELTA_FOR_ONE_MONTH
        ),
    }


def top_urls(user_id, db):
    query = (
        db.query(URLModel.short_code, URLModel.click_count)
        .filter(URLModel.user_id == user_id)
        .order_by(URLModel.click_count.desc())
        .limit(TOP_URLS_LIMIT)
        .all()
    )
    query_val = [
        {"short_code": short_code, "click_count": click_count}
        for short_code, click_count in query
    ]
    return query_val


def click_trend(user_id, db: Session, click_trend_limit=CLICK_TREND_LIMIT):
    query = (
        db.query(
            func.date(ClickEvents.clicked_at).label("date"),
            func.count(ClickEvents.id).label("click_count"),
        )
        .filter(ClickEvents.user_id == user_id)
        .group_by(func.date(ClickEvents.clicked_at))
        .order_by(func.date(ClickEvents.clicked_at))
        .limit(click_trend_limit)
        .all()
    )

    return [{"date": str(row.date), "clicks": row.click_count} for row in query]


def latest_urls(user_id, db):
    latest_urls_data = (
        db.query(URLModel.short_code, URLModel.created_at, URLModel.click_count)
        .filter(URLModel.user_id == user_id)
        .order_by(URLModel.created_at.desc())
        .limit(LATEST_URLS_LIMIT)
        .all()
    )
    return [
        {
            "short_code": row.short_code,
            "created_at": row.created_at,
            "click_count": row.click_count,
        }
        for row in latest_urls_data
    ]
