import json
import logging
import os
import sys

from kafka import KafkaConsumer

from consumer import settings
from consumer.db_conn import connection
from consumer.db_writer import SiteResponse, write_entries_to_ping

logging.basicConfig(
    level=logging.INFO,
    stream=sys.stdout,
)
logger = logging.getLogger(__name__)


def create_kafka_consumer() -> KafkaConsumer:
    additiona_data = {}

    # This is to check if certificates are provided
    # so we can use that mechanism
    if all(
        [
            settings.KAFKA_CA,
            settings.KAFKA_CERT,
            settings.KAFKA_KEY,
        ]
    ):
        cwd = os.getcwd()
        additiona_data = {
            "security_protocol": "SSL",
            "ssl_cafile": os.path.join(cwd, settings.KAFKA_CA),
            "ssl_certfile": os.path.join(cwd, settings.KAFKA_CERT),
            "ssl_keyfile": os.path.join(cwd, settings.KAFKA_KEY),
        }
    return KafkaConsumer(
        settings.DB_CONSUMER_TOPIC,
        group_id=settings.DB_CONSUMER_GROUP,
        bootstrap_servers=settings.BOOTSTRAP_SERVERS,
        value_deserializer=lambda m: json.loads(m.decode("ascii")),
        **additiona_data
    )


def consume_db_writer():
    logger.info("Start db consuming")
    kafka_consumer = create_kafka_consumer()
    for message in kafka_consumer:
        # message value and key are raw bytes -- decode if necessary!
        # e.g., for unicode: `message.value.decode('utf-8')`
        try:
            write_entries_to_ping(
                connection=connection, site_response=SiteResponse(**message.value)
            )
        except Exception as exc:  # noqa
            logger.error("Writing failed for %s with exception %s", message.value, exc)
            # The consumer must carry on regardless
