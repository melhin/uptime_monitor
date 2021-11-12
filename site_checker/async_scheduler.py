import asyncio
import json
import logging
import sys
from collections import defaultdict

from aiokafka import AIOKafkaProducer
from apscheduler.schedulers.asyncio import AsyncIOScheduler

from site_checker.entity import Endpoint, Schedule
from site_checker.settings import (BOOTSTRAP_SERVERS, DB_CONSUMER_TOPIC,
                                   POOL_SIZE)
from site_checker.website_checker import check_site

logging.basicConfig(
    level=logging.INFO,
    stream=sys.stdout,
)
logger = logging.getLogger(__name__)

SCHEDULE_ENTRIES = [
    ("1", "http://localhost:8081/", Schedule.EVERY_MINUTE),
    ("2", "http://localhost:8081/second/", Schedule.EVERY_FIVE_MINUTES),
    ("3", "http://localhost:8081/third/", Schedule.EVERY_TEN_MINUTES),
    ("4", "http://localhost:8081/", Schedule.EVERY_HOUR),
    ("5", "http://localhost:8081/first/", Schedule.EVERY_MINUTE),
    ("11", "http://localhost:8081/", Schedule.EVERY_MINUTE),
    ("12", "http://localhost:8081/second/", Schedule.EVERY_FIVE_MINUTES),
    ("13", "http://localhost:8081/third/", Schedule.EVERY_TEN_MINUTES),
    ("14", "http://localhost:8081/", Schedule.EVERY_HOUR),
    ("15", "http://localhost:8081/first/", Schedule.EVERY_MINUTE),
    ("23", "http://localhost:8081/third/", Schedule.EVERY_TEN_MINUTES),
    ("24", "http://localhost:8081/", Schedule.EVERY_HOUR),
    ("25", "http://localhost:8081/first/", Schedule.EVERY_MINUTE),
    ("211", "http://localhost:8081/", Schedule.EVERY_MINUTE),
    ("212", "http://localhost:8081/second/", Schedule.EVERY_FIVE_MINUTES),
    ("213", "http://localhost:8081/third/", Schedule.EVERY_TEN_MINUTES),
]


def get_schedule():
    schedule_map = defaultdict(list)

    for itm in SCHEDULE_ENTRIES:
        schedule_map[itm[2]].append(Endpoint(id=itm[0], url=itm[1]))
    return schedule_map


async def worker(tasks: asyncio.Queue, result_queue: asyncio.Queue, number: int):
    # individual worker task (sometimes called consumer)
    # - sequentially process tasks as they come into the queue
    # and emit the results
    print(f"Worker {number} up")
    while True:
        endpoint = await tasks.get()
        site_response = await check_site(endpoint=endpoint)
        await result_queue.put(site_response)


async def producer(result_queue: asyncio.Queue, number: int):
    producer = AIOKafkaProducer(bootstrap_servers=BOOTSTRAP_SERVERS)
    await producer.start()
    logger.info(f"Producer {number} up")
    while True:
        site_response = await result_queue.get()
        message = json.dumps(dict(site_response)).encode("ascii")
        await producer.send_and_wait(DB_CONSUMER_TOPIC, message)


async def get_jobs(schedule_type: Schedule, tasks: asyncio.Queue):
    schedule_map = get_schedule()
    for endpoint in schedule_map[schedule_type]:
        await tasks.put(endpoint)


async def main():
    logger.info("Creating jobs and scheduler")
    scheduler = AsyncIOScheduler()
    tasks = asyncio.Queue(20)
    result_queue = asyncio.Queue(20)
    scheduler.add_job(
        get_jobs, "interval", seconds=3, args=(Schedule.EVERY_MINUTE, tasks)
    )
    scheduler.add_job(
        get_jobs, "interval", minutes=5, args=(Schedule.EVERY_FIVE_MINUTES, tasks)
    )
    scheduler.add_job(
        get_jobs, "interval", minutes=10, args=(Schedule.EVERY_TEN_MINUTES, tasks)
    )
    scheduler.add_job(get_jobs, "interval", hours=1, args=(Schedule.EVERY_HOUR, tasks))
    scheduler.start()
    workers = [
        asyncio.create_task(worker(tasks, result_queue, number))
        for number in range(POOL_SIZE)
    ]
    producers = [
        asyncio.create_task(producer(result_queue, number))
        for number in range(POOL_SIZE)
    ]
    await asyncio.gather(*workers, *producers)
