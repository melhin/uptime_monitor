import json
import logging
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


def consume_db_writer():
    consumer = KafkaConsumer(
        settings.DB_CONSUMER_TOPIC,
        group_id=settings.DB_CONSUMER_GROUP,
        bootstrap_servers=settings.BOOTSTRAP_SERVERS,
        value_deserializer=lambda m: json.loads(m.decode("ascii")),
    )
    logger.info("Start db consuming")

    for message in consumer:
        # message value and key are raw bytes -- decode if necessary!
        # e.g., for unicode: `message.value.decode('utf-8')`
        try:
            write_entries_to_ping(connection=connection, site_response=SiteResponse(**message.value))
        except Exception as exc:  # noqa
            logger.error("Writing failed for %s with exception %s", message.value, exc)
            # The consumer must carry on regardless
