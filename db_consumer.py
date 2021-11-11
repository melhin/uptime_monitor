import json

from kafka import KafkaConsumer

import settings


def consume_db_writer():
    consumer = KafkaConsumer(
        settings.DB_CONSUMER_TOPIC,
        group_id=settings.DB_CONSUMER_GROUP,
        bootstrap_servers=settings.BOOTSTRAP_SERVERS,
        value_deserializer=lambda m: json.loads(m.decode("ascii")),
    )
    print("Start db consuming")

    for message in consumer:
        # message value and key are raw bytes -- decode if necessary!
        # e.g., for unicode: `message.value.decode('utf-8')`
        print(
            "%s:%d:%d: key=%s value=%s"
            % (
                message.topic,
                message.partition,
                message.offset,
                message.key,
                message.value,
            )
        )


if __name__ == "__main__":
    consume_db_writer()
