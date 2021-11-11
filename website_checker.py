import datetime
import re
from enum import Enum
from http import HTTPStatus
from typing import Optional

import httpx
from pydantic import BaseModel

import settings


class UPSTATUS(Enum):
    PASS = "status.pass"
    FAIL = "status.fail"
    MISMATCH = "status.mismatch"
    TIMEOUT = "status.timeout"
    ERROR = "status.error"


class SiteResponse(BaseModel):
    response_time: float
    up_status: str
    url: str
    id: int

    response_code: Optional[HTTPStatus] = None
    response_headers: Optional[str] = None
    response_text: Optional[str] = None


def check_response(
    res: httpx.Response,
    expected_status: HTTPStatus,
    expected_text: Optional[str] = None,
):
    if expected_text and not re.search(
        re.escape(expected_text), res.text, re.IGNORECASE
    ):
        return UPSTATUS.MISMATCH
    elif res.status_code != expected_status:
        return UPSTATUS.FAIL
    else:
        return UPSTATUS.PASS


async def check_site(
    endpoint: settings.Endpoint,
    expected_status: Optional[HTTPStatus] = HTTPStatus.OK,
    expected_text: Optional[str] = None,
    timeout: Optional[float] = settings.DEFAULT_TIMEOUT,
) -> SiteResponse:
    """check_site: Is a small utility to retrieve information
    like status code, latency for a given url. Additionally
    there is an option to match a particular text from the body
    It Returns a SiteResponse (just to keep it structured)
    """

    up_status = None
    response_text = None
    response_status_code = None
    response_headers = None
    start = datetime.datetime.now()

    async with httpx.AsyncClient() as client:
        try:
            res = await client.get(endpoint.url, timeout=timeout)
        except httpx.TimeoutException as e:
            up_status = UPSTATUS.TIMEOUT
            response_text = str(e)
        except httpx.RequestError as e:
            up_status = UPSTATUS.ERROR
            response_text = str(e)

    response_time = (datetime.datetime.now() - start).total_seconds()

    # No main failures checking response to determine the rest
    if not up_status:
        up_status = check_response(res, expected_status, expected_text)
        response_text = res.text
        response_headers = str(res.headers)
        response_status_code = res.status_code

    data = SiteResponse(
        response_code=response_status_code,
        response_headers=response_headers,
        response_text=response_text,
        response_time=response_time,
        up_status=up_status.value,
        url=endpoint.url,
        id=endpoint.id,
    )
    return data
