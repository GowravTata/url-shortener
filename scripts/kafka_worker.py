import sys
import time

from app.core.config import TOPICS
from app.kafka.consumer.analytics_consumer import AnalyticsConsumer
from app.services.kafka.analytics import AnalyticsService

BATCH_SIZE = 100
FLUSH_INTERVAL = 5


def run_worker():
    batch = []
    consumer = AnalyticsConsumer([TOPICS])
    last_flush = 0
    for event in consumer.consume():
        batch.append(event)
        process_flag = (
            len(batch) >= BATCH_SIZE
            or time.time() - last_flush >= FLUSH_INTERVAL
        )
        if process_flag:
            AnalyticsService.process_batch(events=batch)
            batch.clear()
            last_flush = time.time()


if len(sys.argv) > 1:
    arg_value = sys.argv[1]

    # Run only if argument is "True"
    if arg_value.lower() == "true":
        run_worker()
    else:
        print("Worker not started because argument was not True.")
else:
    print("No argument provided. Pass True to run the worker.")
