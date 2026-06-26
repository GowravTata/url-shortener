from sqlalchemy.exc import SQLAlchemyError

from app.core.db import get_db
from app.models.events import ClickEvents


class AnalyticsRepository:
    @staticmethod
    def bulk_save(records: list[dict]):
        db = next(get_db())
        try:
            events = [ClickEvents(**record) for record in records]
            db.bulk_save_objects(events)
            db.commit()
            return events
        except SQLAlchemyError as e:
            db.rollback()
            raise e
        finally:
            db.close()
