import pytest

from src.pipeline.read.rest import RESTReader
from src.tests.fixtures.test_configs.rest_configs import (
    TEST_REST_CONFIG_NO_PAGINATION,
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
    async for batch in reader.read(endpoint="items"):
        batches.append(list(batch))
    assert len(batches) == 2
    assert len(batches[0]) == 2
    assert len(batches[1]) == 1
    assert batches[0][0]["id"] == 1
    assert batches[0][1]["id"] == 2
    assert batches[1][0]["id"] == 3


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
    async for batch in reader.read(endpoint="items"):
        batches.append(list(batch))

    assert len(batches) == 3
    assert len(batches[0]) == 5
    assert len(batches[1]) == 5
    assert len(batches[2]) == 2
    assert batches[0][0]["id"] == 1
    assert batches[1][0]["id"] == 6
    assert batches[2][0]["id"] == 11

    requests = mock_rest_offset_pagination_responses.get_requests()
    assert len(requests) == 4
    assert "offset=0" in str(requests[0].url)
    assert "offset=5" in str(requests[1].url)
    assert "offset=10" in str(requests[2].url)
    assert "offset=15" in str(requests[3].url)
