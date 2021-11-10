from http import HTTPStatus

import pytest
import responses

from website_checker import UPSTATUS, check_site


@pytest.mark.parametrize(
    ("expected_status", "received_status", "expected_up_status"),
    [
        (HTTPStatus.OK, HTTPStatus.OK, UPSTATUS.PASS),
        (HTTPStatus.OK, HTTPStatus.FORBIDDEN, UPSTATUS.FAIL),
        (HTTPStatus.OK, HTTPStatus.GATEWAY_TIMEOUT, UPSTATUS.FAIL),
        (HTTPStatus.CREATED, HTTPStatus.OK, UPSTATUS.FAIL),
    ],
)
@responses.activate
def test_website_checker_basic_status(
    expected_status, received_status, expected_up_status
):
    endpoint_url = "http://amazing.web.com"
    responses.add(responses.GET, endpoint_url, status=received_status)

    data = check_site(endpoint_url=endpoint_url, expected_status=expected_status)
    assert expected_up_status == data.up_status
    assert received_status == data.response_code


@pytest.mark.parametrize(
    ("expected_text", "received_text", "expected_up_status"),
    [
        ("expected", "the eXpEcted is present", UPSTATUS.PASS),
        ("expected", "received some thing else", UPSTATUS.MISMATCH),
    ],
)
@responses.activate
def test_website_checker_basic_text(expected_text, received_text, expected_up_status):
    endpoint_url = "http://amazing.web.com"
    responses.add(responses.GET, endpoint_url, body=received_text, status=HTTPStatus.OK)

    data = check_site(
        endpoint_url=endpoint_url,
        expected_status=HTTPStatus.OK,
        expected_text=expected_text,
    )
    assert expected_up_status == data.up_status
