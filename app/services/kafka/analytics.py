from app.core.config import KAFKA_LOGGER
from app.core.logging import AppLogger
from app.models.events import ClickEvents
from app.utils.analytics_repository import AnalyticsRepository
from app.utils.serializers import normalize_data
from app.utils.user_geo_details import get_device, get_geo_data

logger = AppLogger(KAFKA_LOGGER).get_logger()


class AnalyticsService:
    @staticmethod
    def process_batch(events):
        records = []
        column_names = [column.name for column in ClickEvents.__table__.columns]
        del column_names[0]
        try:
            for event in events:
                user_agent = event.get("user_agent")
                ip_address = event.get("ip_address")

                user_agent_details = get_device(user_agent=user_agent)
                geo_data_details = get_geo_data(ip_address=ip_address)

                analytics_data = {
                    **event,
                    **user_agent_details,
                    **geo_data_details,
                }
                normalized_data = normalize_data(payload=analytics_data)
                record = {
                    column: normalized_data.get(column)
                    for column in column_names
                }
                records.append(record)
            if records:
                AnalyticsRepository.bulk_save(records)
                print("Saved Records", len(records))
        except Exception as e:
            logger.exception(f"Error processing : {e}")
