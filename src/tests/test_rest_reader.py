import pytest

from src.pipeline.read.rest import RESTReader
from src.tests.fixtures.test_configs.rest_configs import (
    TEST_REST_CONFIG_NO_PAGINATION,
    TEST_REST_CONFIG_WITH_NEXT_URL_PAGINATION,
    TEST_REST_CONFIG_WITH_OFFSET_PAGINATION,
)


@pytest.mark.asyncio
async def test_rest_reader_no_pagination_single_request(
    mock_rest_no_pagination_response,
    http_client,
):
    reader = RESTReader(source=TEST_REST_CONFIG_NO_PAGINATION, client=http_client)
    reader.batch_size = 2

    batches = []
    url = "https://api.example.com/items"
    endpoint_config = TEST_REST_CONFIG_NO_PAGINATION.endpoints["items"]
    async for batch in reader.read(url=url, endpoint_config=endpoint_config):
        batches.append(list(batch))
    assert len(batches) == 1
    assert len(batches[0]) == 3
    assert batches[0][0]["id"] == 1
    assert batches[0][1]["id"] == 2
    assert batches[0][2]["id"] == 3


@pytest.mark.asyncio
async def test_rest_reader_with_offset_pagination(
    mock_rest_offset_pagination_responses,
    http_client,
):
    reader = RESTReader(
        source=TEST_REST_CONFIG_WITH_OFFSET_PAGINATION, client=http_client
    )
    reader.batch_size = 10

    batches = []
    url = "https://api.example.com/items"
    endpoint_config = TEST_REST_CONFIG_WITH_OFFSET_PAGINATION.endpoints["items"]
    async for batch in reader.read(url=url, endpoint_config=endpoint_config):
        batches.append(list(batch))

    # With batch_size=10, 12 items total (5+5+2) should yield: 1 batch of 10, then 1 batch of 2
    assert len(batches) == 2
    assert len(batches[0]) == 10
    assert len(batches[1]) == 2
    assert batches[0][0]["id"] == 1
    assert batches[0][9]["id"] == 10
    assert batches[1][0]["id"] == 11
    assert batches[1][1]["id"] == 12

    requests = mock_rest_offset_pagination_responses.get_requests()
    assert len(requests) == 4
    assert "offset=0" in str(requests[0].url)
    assert "offset=5" in str(requests[1].url)
    assert "offset=10" in str(requests[2].url)
    assert "offset=15" in str(requests[3].url)


@pytest.mark.asyncio
async def test_rest_reader_with_next_url_pagination(
    mock_rest_next_url_pagination_responses,
    http_client,
):
    reader = RESTReader(
        source=TEST_REST_CONFIG_WITH_NEXT_URL_PAGINATION, client=http_client
    )
    reader.batch_size = 10

    batches = []
    url = "https://api.example.com/items"
    endpoint_config = TEST_REST_CONFIG_WITH_NEXT_URL_PAGINATION.endpoints["items"]
    async for batch in reader.read(url=url, endpoint_config=endpoint_config):
        batches.append(list(batch))

    # With batch_size=10, 12 items total (5+5+2) should yield: 1 batch of 10, then 1 batch of 2
    assert len(batches) == 2
    assert len(batches[0]) == 10
    assert len(batches[1]) == 2
    assert batches[0][0]["id"] == 1
    assert batches[0][9]["id"] == 10
    assert batches[1][0]["id"] == 11
    assert batches[1][1]["id"] == 12

    requests = mock_rest_next_url_pagination_responses.get_requests()
    assert len(requests) == 3
    assert str(requests[0].url) == "https://api.example.com/items"
    assert str(requests[1].url) == "https://api.example.com/items?page=2"
    assert str(requests[2].url) == "https://api.example.com/items?page=3"
