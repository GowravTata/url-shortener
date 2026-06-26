import json
from datetime import datetime

from app.core.config import ANALYTICS_DLQ
from app.core.logging import AppLogger
from app.kafka.producer import kafka_client_obj

logger = AppLogger(name="kafka").get_logger()


def send_to_dlq(event, error):
    payload = {
        "event": event,
        "error": error,
        "failed_at": datetime.utcnow().isoformat(),
    }
    kafka_client_obj.publish_event(
        topic=ANALYTICS_DLQ, value=json.dumps(payload)
    )
    logger.error("event_sent_to_dlq event_id=%s", event.get("event_id"))
