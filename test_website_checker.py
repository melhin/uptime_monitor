from http import HTTPStatus

import pytest

from settings import Endpoint
from website_checker import UPSTATUS, check_site


@pytest.mark.parametrize(
    ("expected_status", "received_status", "expected_up_status"),
    [
        (HTTPStatus.OK, HTTPStatus.OK, UPSTATUS.PASS.value),
        (HTTPStatus.OK, HTTPStatus.FORBIDDEN, UPSTATUS.FAIL.value),
        (HTTPStatus.OK, HTTPStatus.GATEWAY_TIMEOUT, UPSTATUS.FAIL.value),
        (HTTPStatus.CREATED, HTTPStatus.OK, UPSTATUS.FAIL.value),
    ],
)
@pytest.mark.asyncio
async def test_website_checker_basic_status(
    httpx_mock, expected_status, received_status, expected_up_status
):
    endpoint_url = "http://amazing.web.com"
    endpoint = Endpoint(id=1, url=endpoint_url)
    httpx_mock.add_response(method="GET", url=endpoint_url, status_code=received_status)

    data = await check_site(endpoint=endpoint, expected_status=expected_status)
    assert expected_up_status == data.up_status
    assert received_status == data.response_code


@pytest.mark.parametrize(
    ("expected_text", "received_text", "expected_up_status"),
    [
        ("expected", "the eXpEcted is present", UPSTATUS.PASS.value),
        ("expected", "received some thing else", UPSTATUS.MISMATCH.value),
    ],
)
@pytest.mark.asyncio
async def test_website_checker_basic_text(
    httpx_mock, expected_text, received_text, expected_up_status
):
    endpoint_url = "http://amazing.web.com"
    endpoint = Endpoint(id=1, url=endpoint_url)
    httpx_mock.add_response(
        method="GET", url=endpoint_url, status_code=HTTPStatus.OK, text=received_text
    )

    data = await check_site(
        endpoint=endpoint,
        expected_status=HTTPStatus.OK,
        expected_text=expected_text,
    )
    assert expected_up_status == data.up_status
