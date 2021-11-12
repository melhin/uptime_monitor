import logging
from datetime import datetime

from consumer.entity import SiteResponse

logger = logging.getLogger(__name__)


def write_entries_to_ping(connection, site_response: SiteResponse):
    logging.info("Writing: ping %s id: %s", site_response.url, site_response.id)
    site_insert_query = (
        "INSERT INTO public.site "
        "(id, url, current_up_status, last_update) "
        "VALUES(%(id)s, %(url)s, %(up_status)s, %(last_update)s) "
        "on conflict on constraint site_pkey do "
        "update set "
        "current_up_status = %(up_status)s, last_update= %(last_update)s;"
    )
    ping_status_insert_query = (
        "INSERT INTO public.ping_status "
        "(site_id, up_status, created_at, response_time, response_code, response_header, response) "
        "VALUES(%(site_id)s, %(up_status)s, %(created_at)s, %(response_time)s, %(response_code)s, %(response_header)s, %(response)s);"
    )
    with connection:
        with connection.cursor() as cursor:
            now = datetime.now()
            site_data = {
                "id": site_response.id,
                "url": site_response.url,
                "up_status": site_response.up_status,
                "last_update": now,
            }
            cursor.execute(site_insert_query, site_data)
            ping_data = {
                "site_id": site_response.id,
                "up_status": site_response.up_status,
                "response_code": site_response.response_code,
                "response_time": site_response.response_time,
                "response_header": site_response.response_headers,
                "response": site_response.response_text,
                "created_at": now,
            }
            cursor.execute(ping_status_insert_query, ping_data)
    logging.info(
        "Finished Writing: ping %s id: %s", site_response.url, site_response.id
    )
