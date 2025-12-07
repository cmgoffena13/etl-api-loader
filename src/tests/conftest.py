import os

# Needs to happen before local imports
os.environ["ENV_STATE"] = "test"

import pytest
import pytest_asyncio
from pytest_httpx import HTTPXMock

from src.processor.client import AsyncProductionHTTPClient
from src.tests.fixtures.test_responses.rest_no_pagination import (
    TEST_SINGLE_REQUEST_RESPONSE,
)
from src.tests.fixtures.test_responses.rest_offset_pagination import (
    TEST_PAGE_1_RESPONSE,
    TEST_PAGE_2_RESPONSE,
    TEST_PAGE_3_RESPONSE,
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
        json=TEST_PAGE_1_RESPONSE,
    )
    httpx_mock.add_response(
        method="GET",
        url="https://api.example.com/items?offset=5&limit=5",
        json=TEST_PAGE_2_RESPONSE,
    )
    httpx_mock.add_response(
        method="GET",
        url="https://api.example.com/items?offset=10&limit=5",
        json=TEST_PAGE_3_RESPONSE,
    )
    httpx_mock.add_response(
        method="GET",
        url="https://api.example.com/items?offset=15&limit=5",
        json=[],
    )
    yield httpx_mock
