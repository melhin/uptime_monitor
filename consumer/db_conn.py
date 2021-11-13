import psycopg2

from consumer import settings


def create_initial_tables_if_not_exist(connection):
    """This is only for demonstration purposes and ease of use
    In production you would have a different approach to db migration
    """
    with connection:
        with connection.cursor() as cursor:
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS site (
                id int NOT null PRIMARY KEY,
                url text NULL,
                current_up_status varchar NOT null,
                last_update timestamp NOT NULL
            )"""
            )
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS ping_status (
                id  SERIAL PRIMARY KEY,
                site_id int,
                up_status varchar NOT NULL,
                created_at timestamp NOT NULL,
                response_time float4 NOT NULL,
                response_code varchar NULL,
                response_header text NULL,
                response text NULL,
                CONSTRAINT fk_site FOREIGN KEY(site_id) REFERENCES site(id) ON DELETE SET NULL
            )"""
            )


dsn = (
    f"dbname={settings.POSTGRESS_DB} "
    f"user={settings.POSTGRESS_USER} "
    f"password={settings.POSTGRESS_PASSWORD} "
    f"host={settings.POSTGRESS_HOST} "
    f"port={settings.POSTGRESS_PORT}"
)

connection = psycopg2.connect(dsn=dsn)
