import json

from confluent_kafka import Producer

from app.core.config import KAFKA_CONFIG
from app.core.logging import AppLogger
from app.services.kafka.analytics import normalize_data

logger = AppLogger(name="kafka").get_logger()


class KafkaProducer:
    def __init__(self) -> None:
        self.config = KAFKA_CONFIG
        self.producer = Producer(self.config)

    def acked(self, err, msg):
        if err:
            logger.error(f"Delivery failed: {err}")

    def publish_event(self, topic, key, value):
        try:
            if isinstance(value, dict):
                value = normalize_data(value)
            self.producer.produce(
                key=key,
                topic=topic,
                value=json.dumps(value),
                callback=self.acked,
            )
            self.producer.poll(0)
        except BufferError:
            logger.warning("Producer buffer full → flushing")

        except Exception as e:
            logger.exception(f"Publish error: {e}")


kafka_client_obj = KafkaProducer()
