import asyncio
import json
import logging

from apscheduler.schedulers.asyncio import AsyncIOScheduler

from site_checker import settings
from site_checker.db.async_db_conn import getconnection, getcursor
from site_checker.db.jobs import JobDB
from site_checker.entity import Endpoint
from site_checker.kafka_conn import connection as kafka_connection
from site_checker.website_checker import check_site

logger = logging.getLogger(__name__)


async def worker(tasks: asyncio.Queue, kafka_queue: asyncio.Queue, number: int):
    """individual worker task calling the website and sending the response
    to the kafka producer queue
    """
    logger.info(f"Worker {number} up")
    while True:
        endpoint = await tasks.get()
        logger.info(f"Got endpoint %s", endpoint.id)
        site_response = await check_site(endpoint=endpoint)
        await kafka_queue.put(site_response)


async def producer(kafka_queue: asyncio.Queue, number: int):
    async with kafka_connection() as kafka_producer:
        logger.info(f"Producer {number} up")
        while True:
            site_response = await kafka_queue.get()
            logger.info(f"Publishing result for  %s", site_response.id)
            message = json.dumps(dict(site_response)).encode("ascii")
            await kafka_producer.send_and_wait(settings.DB_CONSUMER_TOPIC, message)


async def collect_jobs(connection, tasks: asyncio.Queue):
    async with getcursor(connection=connection) as cursor:
        logger.info("Listening on new jobs")

        job_db = JobDB(cursor=cursor)
        queue = []
        jobs = []
        for available_job in await job_db.get_available_jobs():
            endpoint = Endpoint(id=available_job.site_id, url=available_job.url)

            queue.append(endpoint)
            jobs.append(available_job.job_id)
            await tasks.put(endpoint)
            logger.info(
                "Putting %s in for check. job_id: %s",
                endpoint.url,
                available_job.job_id,
            )

        # For now we will assume things don't break inbetween queue sending
        # when that problem arises this will be another worker where messages
        # are send after successful sending of kafka message
        if jobs:
            logger.info("%s jobs will be deleted", len(jobs))
            await job_db.delete_jobs_with_id(jobs)


async def run_job_consumer():
    async with getconnection() as connection:
        logger.info("Creating jobs and scheduler")
        scheduler = AsyncIOScheduler()
        tasks = asyncio.Queue(20)
        kafka_queue = asyncio.Queue(20)

        scheduler.add_job(
            collect_jobs,
            "interval",
            seconds=5,
            args=(
                connection,
                tasks,
            ),
        )
        scheduler.start()

        workers = [
            asyncio.create_task(worker(tasks, kafka_queue, number))
            for number in range(settings.POOL_SIZE)
        ]
        producers = [
            asyncio.create_task(producer(kafka_queue, number))
            for number in range(settings.POOL_SIZE)
        ]
        await asyncio.gather(*workers, *producers)
