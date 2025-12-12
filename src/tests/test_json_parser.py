import pytest
from pydantic import ValidationError
from pydantic_extra_types.pendulum_dt import DateTime

from src.pipeline.parse.json import JSONParser
from src.tests.fixtures.test_configs.json_parser_configs import (
    TEST_JSON_PARSER_CONFIG_DEEPLY_NESTED,
    TEST_JSON_PARSER_CONFIG_LIST_ROOT,
    TEST_JSON_PARSER_CONFIG_MAX_LENGTH,
    TEST_JSON_PARSER_CONFIG_MULTIPLE_TABLES,
    TEST_JSON_PARSER_CONFIG_NESTED,
    TEST_JSON_PARSER_CONFIG_SIMPLE,
    TEST_JSON_PARSER_CONFIG_WITH_LISTS,
)
from src.tests.fixtures.test_responses.json_parser_responses import (
    TEST_JSON_PARSER_DEEPLY_NESTED_RESPONSE,
    TEST_JSON_PARSER_LIST_ROOT_RESPONSE,
    TEST_JSON_PARSER_MULTIPLE_TABLES_RESPONSE,
    TEST_JSON_PARSER_NESTED_RESPONSE,
    TEST_JSON_PARSER_SIMPLE_RESPONSE,
    TEST_JSON_PARSER_WITH_LISTS_RESPONSE,
)


@pytest.mark.asyncio
async def test_json_parser_simple_structure():
    endpoint_config = TEST_JSON_PARSER_CONFIG_SIMPLE.endpoints["products"]
    parser = JSONParser(endpoint_config=endpoint_config)

    batch = TEST_JSON_PARSER_SIMPLE_RESPONSE

    table_batches = []
    async for result in parser.parse(batch):
        table_batches = result

    assert len(table_batches) == 1
    assert table_batches[0].data_model.__name__ == "TestProduct"
    assert len(table_batches[0].records) == 2
    assert table_batches[0].records[0]["id"] == 1
    assert table_batches[0].records[0]["name"] == "Product 1"
    assert table_batches[0].records[0]["price"] == 19.99
    assert table_batches[0].records[0]["category"] == "Electronics"
    assert table_batches[0].records[1]["id"] == 2
    assert table_batches[0].records[1]["name"] == "Product 2"


@pytest.mark.asyncio
async def test_json_parser_nested_structure():
    endpoint_config = TEST_JSON_PARSER_CONFIG_NESTED.endpoints["products"]
    parser = JSONParser(endpoint_config=endpoint_config)

    batch = TEST_JSON_PARSER_NESTED_RESPONSE

    table_batches = []
    async for result in parser.parse(batch):
        table_batches = result

    assert len(table_batches) == 1
    assert table_batches[0].data_model.__name__ == "TestProductWithNested"
    assert len(table_batches[0].records) == 2
    assert table_batches[0].records[0]["id"] == 1
    assert table_batches[0].records[0]["dimensions_width"] == 10.5
    assert table_batches[0].records[0]["dimensions_height"] == 20.0
    # DateTime field is now properly parsed into DateTime object
    assert isinstance(table_batches[0].records[0]["meta_created_at"], DateTime)
    assert (
        str(table_batches[0].records[0]["meta_created_at"])
        == "2024-01-01 00:00:00+00:00"
    )
    assert table_batches[0].records[1]["dimensions_width"] == 15.0


@pytest.mark.asyncio
async def test_json_parser_with_lists():
    endpoint_config = TEST_JSON_PARSER_CONFIG_WITH_LISTS.endpoints["products"]
    parser = JSONParser(endpoint_config=endpoint_config)

    batch = TEST_JSON_PARSER_WITH_LISTS_RESPONSE

    table_batches = []
    async for result in parser.parse(batch):
        table_batches = result

    assert len(table_batches) == 1
    assert table_batches[0].data_model.__name__ == "TestProductWithList"
    assert len(table_batches[0].records) == 2
    assert table_batches[0].records[0]["id"] == 1
    assert table_batches[0].records[0]["tags"] == '["electronics", "gadget", "new"]'
    assert table_batches[0].records[0]["images"] == '["image1.jpg", "image2.jpg"]'
    assert table_batches[0].records[1]["tags"] == '["clothing", "fashion"]'


@pytest.mark.asyncio
async def test_json_parser_multiple_tables():
    endpoint_config = TEST_JSON_PARSER_CONFIG_MULTIPLE_TABLES.endpoints["products"]
    parser = JSONParser(endpoint_config=endpoint_config)

    batch = TEST_JSON_PARSER_MULTIPLE_TABLES_RESPONSE

    table_batches = []
    async for result in parser.parse(batch):
        table_batches = result

    assert len(table_batches) == 2

    # Find products and reviews batches
    products_batch = next(
        tb for tb in table_batches if tb.data_model.__name__ == "TestProduct"
    )
    reviews_batch = next(
        tb for tb in table_batches if tb.data_model.__name__ == "TestReview"
    )

    assert len(products_batch.records) == 2
    assert products_batch.records[0]["id"] == 1
    assert products_batch.records[0]["name"] == "Product 1"

    assert len(reviews_batch.records) == 3
    assert reviews_batch.records[0]["product_id"] == 1
    assert reviews_batch.records[0]["reviewer_name"] == "John Doe"
    assert reviews_batch.records[0]["rating"] == 5
    assert reviews_batch.records[1]["product_id"] == 1
    assert reviews_batch.records[1]["reviewer_name"] == "Jane Smith"
    assert reviews_batch.records[2]["product_id"] == 2
    assert reviews_batch.records[2]["reviewer_name"] == "Bob Wilson"


@pytest.mark.asyncio
async def test_json_parser_list_root():
    endpoint_config = TEST_JSON_PARSER_CONFIG_LIST_ROOT.endpoints["posts"]
    parser = JSONParser(endpoint_config=endpoint_config)

    batch = TEST_JSON_PARSER_LIST_ROOT_RESPONSE

    table_batches = []
    async for result in parser.parse(batch):
        table_batches = result

    assert len(table_batches) == 1
    assert table_batches[0].data_model.__name__ == "TestListItem"
    assert len(table_batches[0].records) == 3
    assert table_batches[0].records[0]["id"] == 1
    assert table_batches[0].records[0]["title"] == "Post 1"
    assert table_batches[0].records[0]["body"] == "Body of post 1"
    assert table_batches[0].records[2]["id"] == 3
    assert table_batches[0].records[2]["title"] == "Post 3"


@pytest.mark.asyncio
async def test_json_parser_multiple_batches():
    endpoint_config = TEST_JSON_PARSER_CONFIG_SIMPLE.endpoints["products"]
    parser = JSONParser(endpoint_config=endpoint_config)

    batch1 = TEST_JSON_PARSER_SIMPLE_RESPONSE
    batch2 = [{"id": 3, "name": "Product 3", "price": 39.99, "category": "Home"}]

    # Parse first batch
    table_batches1 = []
    async for result in parser.parse(batch1):
        table_batches1 = result

    # Copy the records since the TableBatch objects are reused and will be cleared
    batch1_records = [list(tb.records) for tb in table_batches1]

    # Parse second batch (should clear previous records)
    table_batches2 = []
    async for result in parser.parse(batch2):
        table_batches2 = result

    assert len(batch1_records[0]) == 2
    assert len(table_batches2[0].records) == 1
    assert table_batches2[0].records[0]["id"] == 3
    assert table_batches2[0].records[0]["name"] == "Product 3"


@pytest.mark.asyncio
async def test_json_parser_deeply_nested():
    endpoint_config = TEST_JSON_PARSER_CONFIG_DEEPLY_NESTED.endpoints["invoices"]
    parser = JSONParser(endpoint_config=endpoint_config)

    batch = TEST_JSON_PARSER_DEEPLY_NESTED_RESPONSE

    table_batches = []
    async for result in parser.parse(batch):
        table_batches = result

    assert len(table_batches) == 3

    # Find each table batch
    invoices_batch = next(
        tb for tb in table_batches if tb.data_model.__name__ == "TestInvoice"
    )
    line_items_batch = next(
        tb for tb in table_batches if tb.data_model.__name__ == "TestInvoiceLineItem"
    )
    transactions_batch = next(
        tb for tb in table_batches if tb.data_model.__name__ == "TestTransaction"
    )

    # Verify invoices
    assert len(invoices_batch.records) == 2
    assert invoices_batch.records[0]["invoice_id"] == 1
    assert invoices_batch.records[0]["customer_name"] == "John Doe"
    assert invoices_batch.records[0]["total_amount"] == 150.00
    assert invoices_batch.records[1]["invoice_id"] == 2
    assert invoices_batch.records[1]["customer_name"] == "Jane Smith"

    # Verify line items
    assert len(line_items_batch.records) == 3
    assert line_items_batch.records[0]["invoice_id"] == 1
    assert line_items_batch.records[0]["line_item_id"] == 1
    assert line_items_batch.records[0]["product_name"] == "Widget A"
    assert line_items_batch.records[0]["quantity"] == 2
    assert line_items_batch.records[1]["invoice_id"] == 1
    assert line_items_batch.records[1]["line_item_id"] == 2
    assert line_items_batch.records[1]["product_name"] == "Widget B"
    assert line_items_batch.records[2]["invoice_id"] == 2
    assert line_items_batch.records[2]["line_item_id"] == 3
    assert line_items_batch.records[2]["product_name"] == "Widget C"

    # Verify transactions
    assert len(transactions_batch.records) == 4
    assert transactions_batch.records[0]["invoice_id"] == 1
    assert transactions_batch.records[0]["line_item_id"] == 1
    assert transactions_batch.records[0]["txn_id"] == 1
    assert transactions_batch.records[0]["txn_amount"] == 50.00
    assert transactions_batch.records[0]["payment_method"] == "credit_card"
    assert transactions_batch.records[1]["invoice_id"] == 1
    assert transactions_batch.records[1]["line_item_id"] == 1
    assert transactions_batch.records[1]["txn_id"] == 2
    assert transactions_batch.records[2]["invoice_id"] == 1
    assert transactions_batch.records[2]["line_item_id"] == 2
    assert transactions_batch.records[2]["txn_id"] == 3
    assert transactions_batch.records[3]["invoice_id"] == 2
    assert transactions_batch.records[3]["line_item_id"] == 3
    assert transactions_batch.records[3]["txn_id"] == 4
    assert transactions_batch.records[3]["payment_method"] == "bank_transfer"


@pytest.mark.asyncio
async def test_json_parser_max_length_validation_fails():
    """Test that max_length constraint is enforced and validation fails when violated."""
    endpoint_config = TEST_JSON_PARSER_CONFIG_MAX_LENGTH.endpoints["products"]
    parser = JSONParser(endpoint_config=endpoint_config)

    # Data with code longer than max_length=3
    batch = [
        {
            "id": 1,
            "name": "Product 1",
            "code": "ABCD",  # 4 characters, should fail max_length=3
        }
    ]

    with pytest.raises(ValidationError) as exc_info:
        table_batches = []
        async for result in parser.parse(batch):
            table_batches = result

    # Verify the error is about max_length
    errors = exc_info.value.errors()
    assert any(
        error["type"] == "string_too_long" or "max_length" in str(error).lower()
        for error in errors
    )
