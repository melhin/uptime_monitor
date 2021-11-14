import asyncio
import json
from contextlib import asynccontextmanager
from unittest.mock import AsyncMock, patch

import pytest
from site_checker import settings
from site_checker.entity import Endpoint
from site_checker.job_consumer import collect_jobs, producer, worker
from site_checker.website_checker import SiteResponse


async def get_all_tasks(tasks: asyncio.Queue):
    task_list = []
    while True:
        try:
            itm = tasks.get_nowait()
        except asyncio.QueueEmpty:
            break
        else:
            task_list.append(itm)
    return task_list


@pytest.mark.asyncio
async def test_collect_jobs():
    """A basic test to check that if the db returns a list
    the number of endpoint tasks put are same
    """

    # given
    job_list = [
        (1, "http://amazing.com", 2),
        (2, "http://amazing1.com", 3),
        (5, "http://amazing2.com", 10),
    ]
    expected_tasks = [Endpoint(id=itm[0], url=itm[1]) for itm in job_list]

    # A context manager to represent db return values
    cursor = AsyncMock()
    cursor.fetchall.return_value = job_list
    cursor.execute.return_value = True

    @asynccontextmanager
    async def mock_db_jobs(connection):
        yield cursor

    with patch("site_checker.job_consumer.getcursor", mock_db_jobs):
        # when
        connection = AsyncMock()
        tasks = asyncio.Queue(20)
        await collect_jobs(connection=connection, tasks=tasks)

        # then
        task_list = await get_all_tasks(tasks)
        assert expected_tasks == task_list

    # Check if delete query was called after the assignment
    # delete is the second execute in the cursor
    assert cursor.execute.call_args_list[-1].args == (
        "delete from jobs where id in %s",
        ((2, 3, 10),),
    )


@pytest.mark.asyncio
async def test_worker():
    # given
    job_list = [
        (1, "http://amazing.com", 2),
        (2, "http://amazing1.com", 3),
        (5, "http://amazing2.com", 10),
    ]
    mock_site_response = SiteResponse(
        response_time=2.0,
        up_status="status.pass",
        url="http://amazing.com",
        id=1,
        response_code=None,
        response_headers=None,
        response_text=None,
    )
    tasks = asyncio.Queue(20)
    kafka_queue = asyncio.Queue(20)
    # Adding task to queue along with poison pill to stop iteration
    for task in [Endpoint(id=itm[0], url=itm[1]) for itm in job_list] + [Exception()]:
        tasks.put_nowait(task)

    # when
    with patch("site_checker.job_consumer.check_site") as mock_check_site:
        mock_check_site.return_value = mock_site_response
        with pytest.raises(Exception, match="attribute 'id'"):
            await worker(tasks=tasks, kafka_queue=kafka_queue, number=1)

        # then
        task_list = await get_all_tasks(kafka_queue)
        assert len(task_list) == 3
        assert task_list[0] == mock_site_response


@pytest.mark.asyncio
async def test_producer():
    # given
    site_responses = [
        SiteResponse(
            response_time=2.0,
            up_status="status.pass",
            url="http://amazing.com",
            id=1,
            response_code=None,
            response_headers=None,
            response_text=None,
        ),
        SiteResponse(
            response_time=2.0,
            up_status="status.fail",
            url="http://amazing1.com",
            id=2,
            response_code=None,
            response_headers=None,
            response_text=None,
        ),
    ]

    # mocking kafka producer so that we can assert later
    kafka_producer = AsyncMock()
    kafka_producer.send_and_wait.return_value = True

    @asynccontextmanager
    async def mock_kafka_connection():
        yield kafka_producer

    kafka_queue = asyncio.Queue(20)
    # Adding task to queue along with poison pill to stop iteration
    for task in site_responses + [Exception()]:
        kafka_queue.put_nowait(task)

    # when
    with patch("site_checker.job_consumer.kafka_connection", mock_kafka_connection):
        with pytest.raises(Exception, match="attribute 'id'"):
            await producer(kafka_queue=kafka_queue, number=1)

    # Check if producer was called with the correct params
    assert len(site_responses) == kafka_producer.send_and_wait.call_count
    assert (
        settings.DB_CONSUMER_TOPIC,
        json.dumps(dict(site_responses[0])).encode("ascii"),
    ) == kafka_producer.send_and_wait.call_args_list[0].args
