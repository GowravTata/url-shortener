import json

from confluent_kafka import Consumer

from app.core.config import ANALYTICS_CONSUMER, KAFKA_CONFIG, KAFKA_LOGGER, KAFKA_OFFSET
from app.core.logging import AppLogger
from app.utils.serializers import formatted_time

logger = AppLogger(name=KAFKA_LOGGER).get_logger()


class AnalyticsConsumer:
    def __init__(self, topics: list) -> None:
        config = KAFKA_CONFIG
        config["group.id"] = ANALYTICS_CONSUMER
        config["auto.offset.reset"] = KAFKA_OFFSET

        self.consumer = Consumer(config)
        self.consumer.subscribe(topics=topics)

    def consume(self):
        try:
            while True:
                msg = self.consumer.poll(10.0)
                if msg is not None and msg.error() is None:
                    events = json.loads(msg.value().decode("utf-8"))
                    combined_data = {
                        **events,
                        "topic": msg.topic(),
                        "partition": msg.partition(),
                        "message_offset": msg.offset(),
                        "message_timestamp": msg.timestamp()[0],
                    }
                    yield combined_data
                print(f"{formatted_time()} - INFO - Waiting for messages...")
        except KeyboardInterrupt:
            pass
        finally:
            self.consumer.close()
