import pytest

from src.pipeline.read.rest import RESTReader
from src.pipeline.watermark import commit_watermark, get_watermark
from src.tests.fixtures.test_configs.rest_configs import (
    TEST_REST_CONFIG_NO_PAGINATION,
    TEST_REST_CONFIG_WITH_CURSOR_PAGINATION,
    TEST_REST_CONFIG_WITH_CURSOR_PAGINATION_INCREMENTAL,
    TEST_REST_CONFIG_WITH_NEXT_URL_PAGINATION,
    TEST_REST_CONFIG_WITH_NEXT_URL_PAGINATION_INCREMENTAL,
    TEST_REST_CONFIG_WITH_OFFSET_PAGINATION,
    TEST_REST_CONFIG_WITH_OFFSET_PAGINATION_INCREMENTAL,
    TEST_REST_CONFIG_WITH_QUERY_PAGINATION,
    TEST_REST_CONFIG_WITH_QUERY_PAGINATION_PARAMS,
)


@pytest.mark.asyncio
async def test_rest_reader_no_pagination_single_request(
    mock_rest_no_pagination_response,
    http_client,
    test_db,
):
    _engine, Session = test_db
    reader = RESTReader(
        source=TEST_REST_CONFIG_NO_PAGINATION,
        client=http_client,
        Session=Session,
        source_name="test_api_no_pagination",
        endpoint_name="items",
    )
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
    test_db,
):
    _engine, Session = test_db
    reader = RESTReader(
        source=TEST_REST_CONFIG_WITH_OFFSET_PAGINATION,
        client=http_client,
        Session=Session,
        source_name="test_api_offset_pagination",
        endpoint_name="items",
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
    test_db,
):
    _engine, Session = test_db
    reader = RESTReader(
        source=TEST_REST_CONFIG_WITH_NEXT_URL_PAGINATION,
        client=http_client,
        Session=Session,
        source_name="test_api_next_url_pagination",
        endpoint_name="items",
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


@pytest.mark.asyncio
async def test_rest_reader_with_cursor_pagination(
    mock_rest_cursor_pagination_responses,
    http_client,
    test_db,
):
    _engine, Session = test_db
    reader = RESTReader(
        source=TEST_REST_CONFIG_WITH_CURSOR_PAGINATION,
        client=http_client,
        Session=Session,
        source_name="test_api_cursor_pagination",
        endpoint_name="items",
    )
    reader.batch_size = 10

    batches = []
    url = "https://api.example.com/items"
    endpoint_config = TEST_REST_CONFIG_WITH_CURSOR_PAGINATION.endpoints["items"]
    async for batch in reader.read(url=url, endpoint_config=endpoint_config):
        batches.append(list(batch))

    # With batch_size=10, 12 items total (5+5+2) should yield: 1 batch of 10, then 1 batch of 2
    assert len(batches) == 2
    assert len(batches[0]) == 10
    assert len(batches[1]) == 2
    assert batches[0][0]["id"] == "item_1"
    assert batches[0][9]["id"] == "item_10"
    assert batches[1][0]["id"] == "item_11"
    assert batches[1][1]["id"] == "item_12"

    requests = mock_rest_cursor_pagination_responses.get_requests()
    assert len(requests) == 4
    assert "limit=5" in str(requests[0].url)
    assert "starting_after" not in str(requests[0].url)
    assert "starting_after=item_5" in str(requests[1].url)
    assert "starting_after=item_10" in str(requests[2].url)
    assert "starting_after=item_12" in str(requests[3].url)


@pytest.mark.asyncio
async def test_rest_reader_with_query_pagination_path(
    mock_rest_query_pagination_path_responses,
    http_client,
    test_db,
):
    """Query pagination: rows from DB drive GETs with value in path (path={ip}/geo/lookup)."""
    engine, Session = test_db
    reader = RESTReader(
        source=TEST_REST_CONFIG_WITH_QUERY_PAGINATION,
        client=http_client,
        Session=Session,
        source_name="test_api_query_pagination",
        endpoint_name="geo",
        engine=engine,
    )
    reader.batch_size = 10

    batches = []
    url = "https://api.example.com"
    endpoint_config = TEST_REST_CONFIG_WITH_QUERY_PAGINATION.endpoints["geo"]
    async for batch in reader.read(url=url, endpoint_config=endpoint_config):
        batches.append(list(batch))

    assert len(batches) == 1
    assert len(batches[0]) == 3
    assert batches[0][0]["result"]["ip"] == "1.2.3.4"
    assert batches[0][1]["result"]["ip"] == "5.6.7.8"
    assert batches[0][2]["result"]["ip"] == "9.10.11.12"

    requests = mock_rest_query_pagination_path_responses.get_requests()
    assert len(requests) == 3
    assert str(requests[0].url) == "https://api.example.com/1.2.3.4/geo/lookup"
    assert str(requests[1].url) == "https://api.example.com/5.6.7.8/geo/lookup"
    assert str(requests[2].url) == "https://api.example.com/9.10.11.12/geo/lookup"


@pytest.mark.asyncio
async def test_rest_reader_with_query_pagination_params(
    mock_rest_query_pagination_params_responses,
    http_client,
    test_db,
):
    """Query pagination: rows from DB drive GETs with value in query params (?ip=...)."""
    engine, Session = test_db
    reader = RESTReader(
        source=TEST_REST_CONFIG_WITH_QUERY_PAGINATION_PARAMS,
        client=http_client,
        Session=Session,
        source_name="test_api_query_pagination_params",
        endpoint_name="lookup",
        engine=engine,
    )
    reader.batch_size = 10

    batches = []
    url = "https://api.example.com/lookup"
    endpoint_config = TEST_REST_CONFIG_WITH_QUERY_PAGINATION_PARAMS.endpoints["lookup"]
    async for batch in reader.read(url=url, endpoint_config=endpoint_config):
        batches.append(list(batch))

    assert len(batches) == 1
    assert len(batches[0]) == 3
    assert batches[0][0]["result"]["ip"] == "1.2.3.4"
    assert batches[0][2]["result"]["ip"] == "9.10.11.12"

    requests = mock_rest_query_pagination_params_responses.get_requests()
    assert len(requests) == 3
    assert "ip=1.2.3.4" in str(requests[0].url)
    assert "ip=5.6.7.8" in str(requests[1].url)
    assert "ip=9.10.11.12" in str(requests[2].url)


@pytest.mark.asyncio
async def test_rest_reader_with_offset_pagination_incremental(
    mock_rest_offset_pagination_incremental_first_run,
    mock_rest_offset_pagination_incremental_second_run,
    http_client,
    test_db,
):
    _engine, Session = test_db
    source_name = "test_api_offset_pagination_incremental"
    endpoint_name = "items"

    reader = RESTReader(
        source=TEST_REST_CONFIG_WITH_OFFSET_PAGINATION_INCREMENTAL,
        client=http_client,
        Session=Session,
        source_name=source_name,
        endpoint_name=endpoint_name,
    )
    reader.batch_size = 10

    batches = []
    url = "https://api.example.com/items"
    endpoint_config = TEST_REST_CONFIG_WITH_OFFSET_PAGINATION_INCREMENTAL.endpoints[
        "items"
    ]
    async for batch in reader.read(url=url, endpoint_config=endpoint_config):
        batches.append(list(batch))

    first_run_requests = (
        mock_rest_offset_pagination_incremental_first_run.get_requests()
    )

    # Commit the watermark after successful first run (simulating publish)
    commit_watermark(source_name, endpoint_name, Session)

    watermark = get_watermark(source_name, endpoint_name, Session)
    assert watermark == "12"

    batches = []
    async for batch in reader.read(url=url, endpoint_config=endpoint_config):
        batches.append(list(batch))

    all_requests = mock_rest_offset_pagination_incremental_second_run.get_requests()
    second_run_requests = all_requests[len(first_run_requests) :]
    assert len(second_run_requests) >= 1
    assert "offset=12" in str(second_run_requests[0].url)


@pytest.mark.asyncio
async def test_rest_reader_with_next_url_pagination_incremental(
    mock_rest_next_url_pagination_incremental_first_run,
    mock_rest_next_url_pagination_incremental_second_run,
    http_client,
    test_db,
):
    _engine, Session = test_db
    source_name = "test_api_next_url_pagination_incremental"
    endpoint_name = "items"

    reader = RESTReader(
        source=TEST_REST_CONFIG_WITH_NEXT_URL_PAGINATION_INCREMENTAL,
        client=http_client,
        Session=Session,
        source_name=source_name,
        endpoint_name=endpoint_name,
    )
    reader.batch_size = 10

    batches = []
    url = "https://api.example.com/items"
    endpoint_config = TEST_REST_CONFIG_WITH_NEXT_URL_PAGINATION_INCREMENTAL.endpoints[
        "items"
    ]
    async for batch in reader.read(url=url, endpoint_config=endpoint_config):
        batches.append(list(batch))

    first_run_requests = (
        mock_rest_next_url_pagination_incremental_first_run.get_requests()
    )

    # Commit the watermark after successful first run (simulating publish)
    commit_watermark(source_name, endpoint_name, Session)

    watermark = get_watermark(source_name, endpoint_name, Session)
    assert watermark == "https://api.example.com/items?page=3"

    batches = []
    async for batch in reader.read(url=url, endpoint_config=endpoint_config):
        batches.append(list(batch))

    all_requests = mock_rest_next_url_pagination_incremental_second_run.get_requests()
    second_run_requests = all_requests[len(first_run_requests) :]
    assert len(second_run_requests) == 1
    assert str(second_run_requests[0].url) == "https://api.example.com/items?page=3"


@pytest.mark.asyncio
async def test_rest_reader_with_cursor_pagination_incremental(
    mock_rest_cursor_pagination_incremental_first_run,
    mock_rest_cursor_pagination_incremental_second_run,
    http_client,
    test_db,
):
    _engine, Session = test_db
    source_name = "test_api_cursor_pagination_incremental"
    endpoint_name = "items"

    reader = RESTReader(
        source=TEST_REST_CONFIG_WITH_CURSOR_PAGINATION_INCREMENTAL,
        client=http_client,
        Session=Session,
        source_name=source_name,
        endpoint_name=endpoint_name,
    )
    reader.batch_size = 10

    batches = []
    url = "https://api.example.com/items"
    endpoint_config = TEST_REST_CONFIG_WITH_CURSOR_PAGINATION_INCREMENTAL.endpoints[
        "items"
    ]
    async for batch in reader.read(url=url, endpoint_config=endpoint_config):
        batches.append(list(batch))

    first_run_requests = (
        mock_rest_cursor_pagination_incremental_first_run.get_requests()
    )

    # Commit the watermark after successful first run (simulating publish)
    commit_watermark(source_name, endpoint_name, Session)

    watermark = get_watermark(source_name, endpoint_name, Session)
    assert watermark == "item_12"

    batches = []
    async for batch in reader.read(url=url, endpoint_config=endpoint_config):
        batches.append(list(batch))

    all_requests = mock_rest_cursor_pagination_incremental_second_run.get_requests()
    second_run_requests = all_requests[len(first_run_requests) :]
    assert len(second_run_requests) == 1
    assert "starting_after=item_12" in str(second_run_requests[0].url)
