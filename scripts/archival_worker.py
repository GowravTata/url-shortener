import sys
import time

from app.core.config import TOPICS
from app.kafka.consumer.archival_consumer import ArchivalConsumer
from app.services.kafka.archive import ArchivalService

BATCH_SIZE = 100
FLUSH_INTERVAL = 5


def run_worker():
    batch = []
    consumer = ArchivalConsumer([TOPICS])
    last_flush = 0
    for event in consumer.consume():
        batch.append(event)
        process_flag = (
            len(batch) >= BATCH_SIZE
            or time.time() - last_flush >= FLUSH_INTERVAL
        )
        if process_flag:
            ArchivalService.process_batch(events=batch)
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
