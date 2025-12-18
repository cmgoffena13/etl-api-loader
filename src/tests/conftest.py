import os

# Needs to happen before local imports
os.environ["ENV_STATE"] = "test"

import pytest
import pytest_asyncio
from pytest_httpx import HTTPXMock

from src.process.client import AsyncProductionHTTPClient
from src.tests.fixtures.test_responses.graphql_no_pagination import (
    TEST_GRAPHQL_SINGLE_REQUEST_RESPONSE,
)
from src.tests.fixtures.test_responses.rest_cursor_pagination import (
    TEST_REST_CURSOR_PAGINATION_PAGE_1_RESPONSE,
    TEST_REST_CURSOR_PAGINATION_PAGE_2_RESPONSE,
    TEST_REST_CURSOR_PAGINATION_PAGE_3_RESPONSE,
)
from src.tests.fixtures.test_responses.rest_next_url_pagination import (
    TEST_REST_NEXT_URL_PAGINATION_PAGE_1_RESPONSE,
    TEST_REST_NEXT_URL_PAGINATION_PAGE_2_RESPONSE,
    TEST_REST_NEXT_URL_PAGINATION_PAGE_3_RESPONSE,
)
from src.tests.fixtures.test_responses.rest_no_pagination import (
    TEST_SINGLE_REQUEST_RESPONSE,
)
from src.tests.fixtures.test_responses.rest_offset_pagination import (
    TEST_REST_OFFSET_PAGINATION_PAGE_1_RESPONSE,
    TEST_REST_OFFSET_PAGINATION_PAGE_2_RESPONSE,
    TEST_REST_OFFSET_PAGINATION_PAGE_3_RESPONSE,
)


@pytest_asyncio.fixture
async def http_client():
    client = AsyncProductionHTTPClient()
    yield client
    await client.close()


@pytest.fixture
def mock_rest_no_pagination_response(httpx_mock: HTTPXMock):
    httpx_mock.add_response(
        method="GET",
        url="https://api.example.com/items",
        json=TEST_SINGLE_REQUEST_RESPONSE,
    )
    yield httpx_mock


@pytest.fixture
def mock_rest_offset_pagination_responses(httpx_mock: HTTPXMock):
    httpx_mock.add_response(
        method="GET",
        url="https://api.example.com/items?offset=0&limit=5",
        json=TEST_REST_OFFSET_PAGINATION_PAGE_1_RESPONSE,
    )
    httpx_mock.add_response(
        method="GET",
        url="https://api.example.com/items?offset=5&limit=5",
        json=TEST_REST_OFFSET_PAGINATION_PAGE_2_RESPONSE,
    )
    httpx_mock.add_response(
        method="GET",
        url="https://api.example.com/items?offset=10&limit=5",
        json=TEST_REST_OFFSET_PAGINATION_PAGE_3_RESPONSE,
    )
    httpx_mock.add_response(
        method="GET",
        url="https://api.example.com/items?offset=15&limit=5",
        json={"items": []},
    )
    yield httpx_mock


@pytest.fixture
def mock_rest_next_url_pagination_responses(httpx_mock: HTTPXMock):
    httpx_mock.add_response(
        method="GET",
        url="https://api.example.com/items",
        json=TEST_REST_NEXT_URL_PAGINATION_PAGE_1_RESPONSE,
    )
    httpx_mock.add_response(
        method="GET",
        url="https://api.example.com/items?page=2",
        json=TEST_REST_NEXT_URL_PAGINATION_PAGE_2_RESPONSE,
    )
    httpx_mock.add_response(
        method="GET",
        url="https://api.example.com/items?page=3",
        json=TEST_REST_NEXT_URL_PAGINATION_PAGE_3_RESPONSE,
    )
    yield httpx_mock


@pytest.fixture
def mock_rest_cursor_pagination_responses(httpx_mock: HTTPXMock):
    httpx_mock.add_response(
        method="GET",
        url="https://api.example.com/items?limit=5",
        json=TEST_REST_CURSOR_PAGINATION_PAGE_1_RESPONSE,
    )
    httpx_mock.add_response(
        method="GET",
        url="https://api.example.com/items?limit=5&starting_after=item_5",
        json=TEST_REST_CURSOR_PAGINATION_PAGE_2_RESPONSE,
    )
    httpx_mock.add_response(
        method="GET",
        url="https://api.example.com/items?limit=5&starting_after=item_10",
        json=TEST_REST_CURSOR_PAGINATION_PAGE_3_RESPONSE,
    )
    httpx_mock.add_response(
        method="GET",
        url="https://api.example.com/items?limit=5&starting_after=item_12",
        json={"data": []},
    )
    yield httpx_mock


@pytest.fixture
def mock_graphql_no_pagination_response(httpx_mock: HTTPXMock):
    httpx_mock.add_response(
        method="POST",
        url="https://api.example.com/graphql",
        json=TEST_GRAPHQL_SINGLE_REQUEST_RESPONSE,
    )
    yield httpx_mock
