import pytest

from src.pipeline.read.graphql import GraphQLReader
from src.tests.fixtures.test_configs.graphql_configs import (
    TEST_GRAPHQL_CONFIG_NO_PAGINATION,
)


@pytest.mark.asyncio
async def test_graphql_reader_no_pagination_single_request(
    mock_graphql_no_pagination_response,
    http_client,
    test_db,
):
    _engine, Session = test_db
    reader = GraphQLReader(
        source=TEST_GRAPHQL_CONFIG_NO_PAGINATION,
        client=http_client,
        Session=Session,
        source_name="test_graphql_no_pagination",
        endpoint_name="items",
    )
    reader.batch_size = 2

    batches = []
    url = "https://api.example.com/graphql"
    endpoint_config = TEST_GRAPHQL_CONFIG_NO_PAGINATION.endpoints["items"]
    async for batch in reader.read(url=url, endpoint_config=endpoint_config):
        batches.append(list(batch))
    assert len(batches) == 1
    assert len(batches[0]) == 3
    assert batches[0][0]["id"] == 1
    assert batches[0][1]["id"] == 2
    assert batches[0][2]["id"] == 3
