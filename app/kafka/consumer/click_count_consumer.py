import json

from confluent_kafka import Consumer

from app.core.config import (CLICK_COUNT_CONSUMER, KAFKA_CONFIG, KAFKA_LOGGER,
                             KAFKA_OFFSET)
from app.core.logging import AppLogger
from app.utils.serializers import formatted_time

logger=AppLogger(name=KAFKA_LOGGER).get_logger()

class ClickCountConsumer:
    def __init__(self, topics:list) -> None:
        config=KAFKA_CONFIG
        config["group.id"]=CLICK_COUNT_CONSUMER
        config["auto.offset.reset"]=KAFKA_OFFSET
        
        self.consumer=Consumer(config)
        self.consumer.subscribe(topics=topics)
    
    def consume(self):
        try:
            while True:
                msg=self.consumer.poll(2)
                if msg is not None and msg.error() is None:
                    events=json.loads(msg.value().decode("utf-8"))
                    payload= {"short_code":events.get("short_code"),
                              "last_accessed":events.get("clicked_at")}
                    yield payload
                print(f"{formatted_time()} - INFO - Waiting for messages...")    
        except KeyboardInterrupt:
                    pass
        finally:
            self.consumer.close()