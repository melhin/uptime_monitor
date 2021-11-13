from contextlib import asynccontextmanager
from aiokafka import AIOKafkaProducer
from site_checker import settings
from contextlib import asynccontextmanager


@asynccontextmanager
async def connection():
    producer = AIOKafkaProducer(bootstrap_servers=settings.BOOTSTRAP_SERVERS)
    await producer.start()
    try:
        yield producer
    finally:
        await producer.stop()
