import os

from contextlib import asynccontextmanager
from aiokafka import AIOKafkaProducer
from aiokafka.helpers import create_ssl_context
from site_checker import settings
from contextlib import asynccontextmanager


@asynccontextmanager
async def connection():
    additional_data = {}
    if all(
        [
            settings.KAFKA_CA,
            settings.KAFKA_CERT,
            settings.KAFKA_KEY,
        ]
    ):
        cwd = os.getcwd()
        ssl_context = create_ssl_context(
            cafile=os.path.join(cwd, settings.KAFKA_CA),
            certfile=os.path.join(cwd, settings.KAFKA_CERT),
            keyfile=os.path.join(cwd, settings.KAFKA_KEY),
        )
        additional_data = {
            "security_protocol": "SSL",
            "ssl_context": ssl_context,
        }
    producer = AIOKafkaProducer(
        bootstrap_servers=settings.BOOTSTRAP_SERVERS, **additional_data
    )
    await producer.start()
    try:
        yield producer
    finally:
        await producer.stop()
