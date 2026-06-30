import json

from app.core.config import KAFKA_LOGGER
from app.core.logging import AppLogger
from app.utils.archival_repository import ArchiveRepository

logger = AppLogger(KAFKA_LOGGER).get_logger()


class ArchivalService:
    @staticmethod
    def process_batch(events):
        records = []
        try:
            for event in events:
                event_id = event.get("event_id")
                archive_data = {
                    "event_id": event_id,
                    "event_payload": json.dumps(event),
                    "topic": event.get("topic"),
                    "partition": event.get("partition"),
                    "message_offset": event.get("message_offset"),
                    "message_timestamp": event.get("message_timestamp"),
                }
                records.append(archive_data)
            if records:
                ArchiveRepository.bulk_save(records)
                print("Saved Records", len(records))
        except Exception as e:
            logger.exception(f"Error processing : {e}")
