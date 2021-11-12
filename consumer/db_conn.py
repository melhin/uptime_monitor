import psycopg2

from consumer import settings

dsn = (
    f"dbname={settings.POSTGRESS_DB} "
    f"user={settings.POSTGRESS_USER} "
    f"password={settings.POSTGRESS_PASSWORD} "
    f"host={settings.POSTGRESS_HOST} "
    f"port={settings.POSTGRESS_PORT}"
)

connection = psycopg2.connect(dsn=dsn)
