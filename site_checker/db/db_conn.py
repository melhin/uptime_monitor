from site_checker import settings
from psycopg2.pool import SimpleConnectionPool
from contextlib import contextmanager


dsn = (
    f"dbname={settings.POSTGRESS_DB} "
    f"user={settings.POSTGRESS_USER} "
    f"password={settings.POSTGRESS_PASSWORD} "
    f"host={settings.POSTGRESS_HOST} "
    f"port={settings.POSTGRESS_PORT}"
)


connectionpool = SimpleConnectionPool(1,10,dsn=dsn)


@contextmanager
def getcursor():
    con = connectionpool.getconn()
    try:
        yield con.cursor()
    finally:
        connectionpool.putconn(con)


def create_initial_tables_if_not_exist():
    """This is only for demonstration purposes and ease of use
    In production you would have a different approach to db migration
    """
    with getcursor() as cursor:
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS site_config (
            id  SERIAL PRIMARY KEY,
            url text NULL,
            schedule varchar NOT null,
            created_at timestamp default current_timestamp
        )"""
        )
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS jobs (
            id  SERIAL PRIMARY KEY,
            site_config_id int,
            created_at timestamp default current_timestamp,
            CONSTRAINT fk_jobs FOREIGN KEY(site_config_id) REFERENCES site_config(id) ON DELETE SET NULL
        )"""
        )
        cursor.connection.commit()


def create_initial_schedule_data(instances):
    """
    Only to run from a command prompt
    """
    import random
    from site_checker.entity import Schedule
    from psycopg2.extras import execute_values
    site_config_insert_statement = (
        "INSERT INTO public.site_config "
        "(url, schedule) "
        "VALUES %s;"
    )

    with getcursor() as cursor:
        data = []
        for _ in range(instances):
            data.append(
                (
                    random.choice([
                            "http://localhost:8081/first/",
                            "http://localhost:8081/second/",
                            "http://localhost:8081/third/"
                    ]),
                    random.choice([
                        Schedule.EVERY_MINUTE.value,
                        Schedule.EVERY_FIVE_MINUTES.value,
                        Schedule.EVERY_TEN_MINUTES.value,
                    ]),
                )
            )
        execute_values(cursor, site_config_insert_statement, data)
        cursor.connection.commit()
