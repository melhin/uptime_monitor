import logging
import sys

from apscheduler.schedulers.blocking import BlockingScheduler

from site_checker.db.db_conn import getcursor
from site_checker.entity import Schedule

logging.basicConfig(
    level=logging.INFO,
    stream=sys.stdout,
)
logger = logging.getLogger(__name__)


def get_and_set_jobs(schedule_type: Schedule):
    """A basic scheduler: Scheduler kicks in at its alotted interval
    at that point all the sites with the corresponding schedule is copied
    to a job table. This is a simple job queue.
    For advanced usage we would need to change the message broker or again
    use the db but in a way that the job result schedules the next job
    """
    insert_statement = (
        "INSERT INTO jobs (site_config_id) "
        "select id from site_config where schedule = %(schedule_type)s"
    )
    with getcursor() as cursor:
        cursor.execute(insert_statement, {"schedule_type": schedule_type.value})
        cursor.connection.commit()


def run_scheduler():
    logger.info("Starting scheduler")
    scheduler = BlockingScheduler()
    scheduler.add_job(
        get_and_set_jobs, "interval", seconds=1, args=(Schedule.EVERY_MINUTE,)
    )
    scheduler.add_job(
        get_and_set_jobs, "interval", seconds=5, args=(Schedule.EVERY_FIVE_MINUTES,)
    )
    scheduler.add_job(
        get_and_set_jobs, "interval", seconds=10, args=(Schedule.EVERY_TEN_MINUTES,)
    )
    scheduler.add_job(
        get_and_set_jobs, "interval", hours=1, args=(Schedule.EVERY_HOUR,)
    )

    try:
        scheduler.start()
    except (KeyboardInterrupt, SystemExit):
        logger.info("Scheduler stopped")


if __name__ == "__main__":
    run_scheduler()
