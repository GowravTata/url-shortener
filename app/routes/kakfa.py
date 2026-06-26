from fastapi import APIRouter, Query

from app.core.logging import AppLogger
from app.services.kafka.admin import kafka_admin

kafka_router = APIRouter(tags=["Kafka"], prefix="/v1/kafka")
logger = AppLogger().get_logger()


@kafka_router.delete(
    "/topics/{topic}",
    summary="Deletes Kafka Topic",
    description="Deletes the kafka topic if exists",
)
async def delete_kafka_topic(
    topic: str,
):
    logger.info(f"Starting to Delete Topic={topic}")
    return kafka_admin.delete_topic(topic=topic)


@kafka_router.post(
    "/topics/",
    summary="Creates Kafka Topic",
    description="Creates Kafka Topic",
)
async def create_kafka_topic(
    topic: str,
    partitions: int = Query(1, ge=1),
    replication_factor: int = Query(1, ge=1, le=9),
):
    logger.info(f"Starting to Create Topic={topic}")
    return kafka_admin.create_topic(
        topic=topic,
        partitions=partitions,
        replication_factor=replication_factor,
    )


@kafka_router.put(
    "/topics/{topic}",
    summary="Purge Kafka Topic",
    description="Purge Kafka Topic",
)
async def purge_kafka_topic(
    topic: str,
):
    logger.info(f"Starting to Purge Topic={topic}")
    return kafka_admin.purge_topic(topic=topic)


@kafka_router.get(
    "/topics/",
    summary="Fetches all Kafka Topics",
    description="Fetches all Kafka Topics",
)
async def fetch_kafka_topics():
    logger.info(f"Starting to Fetch All Topics")
    return kafka_admin.list_topics()
