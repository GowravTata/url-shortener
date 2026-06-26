from confluent_kafka import KafkaException
from confluent_kafka.admin import AdminClient, NewTopic

from app.core.config import KAFKA_CONFIG


class KafkaAdmin:

    def __init__(self):
        self.client = AdminClient(KAFKA_CONFIG)

    def create_topic(self, topic, partitions=1, replication_factor=1):
        new_topic = NewTopic(
            topic=topic,
            num_partitions=partitions,
            replication_factor=replication_factor,
        )

        try:
            futures = self.client.create_topics([new_topic])
            futures[topic].result()
            return {
                "success": True,
                "message": f"Topic '{topic}' created successfully.",
            }
        except KafkaException as e:
            return {"success": False, "error": str(e)}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def delete_topic(self, topic):
        try:
            futures = self.client.delete_topics([topic], operation_timeout=30)
            futures[topic].result()

            return {
                "success": True,
                "message": f"Topic '{topic}' deleted successfully.",
            }
        except KafkaException as e:
            return {"success": False, "error": str(e)}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def purge_topic(self, topic):
        delete_response = self.delete_topic(topic)
        if not delete_response["success"]:
            return delete_response
        import time

        time.sleep(2)
        create_response = self.create_topic(topic=topic)
        return create_response

    def list_topics(self):
        try:
            metadata = self.client.list_topics(timeout=10)
            return {"success": True, "topics": list(metadata.topics.keys())}
        except Exception as e:
            return {"success": False, "error": str(e)}


kafka_admin = KafkaAdmin()
