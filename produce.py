import asyncio
import logging
import sys

from site_checker.db.db_conn import (
    create_initial_schedule_data,
    create_initial_tables_if_not_exist,
)
from site_checker.job_consumer import run_job_consumer
from site_checker.scheduler import run_scheduler

logging.basicConfig(
    level=logging.INFO,
    stream=sys.stdout,
)
logger = logging.getLogger(__name__)

if __name__ == "__main__":
    param = str(sys.argv[1]).strip().lower()
    if param == "scheduler":
        logging.info("Starting scheduler")
        create_initial_tables_if_not_exist()
        run_scheduler()
    elif param == "worker":
        logging.info("Starting worker")
        asyncio.run(run_job_consumer())
    if param == "populate_schedule":
        create_initial_schedule_data(100)
    else:
        raise NotImplemented()
