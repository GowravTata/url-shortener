from sqlalchemy.orm import Session

from app.utils.dashboard import (click_trend, latest_urls, recent_activity,
                                 summary, top_urls)


def dashboard_analytics(user_id, db: Session):
    return {
        "summary": summary(user_id,db),
        "recent_activity": recent_activity(user_id,db),
        "top_urls": top_urls(user_id,db),
        "latest_urls": latest_urls(user_id,db),
        "click_trend": click_trend(user_id,db),
    }
