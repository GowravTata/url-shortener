from app.core.logging import AppLogger
from app.core.db import get_db
from app.models.url import URLModel
from app.core.config import KAFKA_LOGGER
from datetime import datetime

logger=AppLogger(KAFKA_LOGGER).get_logger()

class ClickCountService:
    @staticmethod
    def process_batch(events):
        try:
            for event in events:
                short_code=event.get("short_code")
                last_accessed=event.get("last_accessed")
                db=next(get_db())
                record = (db.query(URLModel).filter(
                    URLModel.short_code == short_code).first()
                                        )
                if record:
                    record.click_count += 1
                    record.last_accessed = datetime.fromisoformat(last_accessed)
                db.commit()
        except Exception as e:
            logger.exception(f"Error processing : {e}")
        
                
        
