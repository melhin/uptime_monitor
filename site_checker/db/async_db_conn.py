from site_checker import settings
from contextlib import asynccontextmanager
import aiopg


dsn = (
    f"dbname={settings.POSTGRESS_DB} "
    f"user={settings.POSTGRESS_USER} "
    f"password={settings.POSTGRESS_PASSWORD} "
    f"host={settings.POSTGRESS_HOST} "
    f"port={settings.POSTGRESS_PORT}"
)


@asynccontextmanager
async def getconnection():
    async with aiopg.create_pool(dsn, minsize=1, maxsize=10) as connectionpool:
        try:
            yield connectionpool
        finally:
            connectionpool.close()


@asynccontextmanager
async def getcursor(connection):
    async with connection.acquire() as conn:
        async with conn.cursor() as cursor:
            yield cursor
