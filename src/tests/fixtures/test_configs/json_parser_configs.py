from src.sources.base import APIConfig, APIEndpointConfig, TableConfig
from src.tests.fixtures.test_models.json_parser_models import (
    TestInvoice,
    TestInvoiceLineItem,
    TestListItem,
    TestProduct,
    TestProductWithList,
    TestProductWithNested,
    TestReview,
    TestTransaction,
)

TEST_JSON_PARSER_CONFIG_SIMPLE = APIConfig(
    name="test_json_parser_simple",
    base_url="https://api.example.com/",
    type="rest",
    endpoints={
        "products": APIEndpointConfig(
            json_entrypoint="products",
            tables=[
                TableConfig(
                    data_model=TestProduct,
                    stage_table_name="stage_products",
                    target_table_name="products",
                )
            ],
        )
    },
)

TEST_JSON_PARSER_CONFIG_NESTED = APIConfig(
    name="test_json_parser_nested",
    base_url="https://api.example.com/",
    type="rest",
    endpoints={
        "products": APIEndpointConfig(
            json_entrypoint="products",
            tables=[
                TableConfig(
                    data_model=TestProductWithNested,
                    stage_table_name="stage_products",
                    target_table_name="products",
                )
            ],
        )
    },
)

TEST_JSON_PARSER_CONFIG_WITH_LISTS = APIConfig(
    name="test_json_parser_with_lists",
    base_url="https://api.example.com/",
    type="rest",
    endpoints={
        "products": APIEndpointConfig(
            json_entrypoint="products",
            tables=[
                TableConfig(
                    data_model=TestProductWithList,
                    stage_table_name="stage_products",
                    target_table_name="products",
                )
            ],
        )
    },
)

TEST_JSON_PARSER_CONFIG_MULTIPLE_TABLES = APIConfig(
    name="test_json_parser_multiple_tables",
    base_url="https://api.example.com/",
    type="rest",
    endpoints={
        "products": APIEndpointConfig(
            json_entrypoint="products",
            tables=[
                TableConfig(
                    data_model=TestProduct,
                    stage_table_name="stage_products",
                    target_table_name="products",
                ),
                TableConfig(
                    data_model=TestReview,
                    stage_table_name="stage_reviews",
                    target_table_name="reviews",
                ),
            ],
        )
    },
)

TEST_JSON_PARSER_CONFIG_LIST_ROOT = APIConfig(
    name="test_json_parser_list_root",
    base_url="https://api.example.com/",
    type="rest",
    endpoints={
        "posts": APIEndpointConfig(
            json_entrypoint=None,
            tables=[
                TableConfig(
                    data_model=TestListItem,
                    stage_table_name="stage_posts",
                    target_table_name="posts",
                )
            ],
        )
    },
)

TEST_JSON_PARSER_CONFIG_DEEPLY_NESTED = APIConfig(
    name="test_json_parser_deeply_nested",
    base_url="https://api.example.com/",
    type="rest",
    endpoints={
        "invoices": APIEndpointConfig(
            json_entrypoint=None,
            tables=[
                TableConfig(
                    data_model=TestInvoice,
                    stage_table_name="stage_invoices",
                    target_table_name="invoices",
                ),
                TableConfig(
                    data_model=TestInvoiceLineItem,
                    stage_table_name="stage_invoice_line_items",
                    target_table_name="invoice_line_items",
                ),
                TableConfig(
                    data_model=TestTransaction,
                    stage_table_name="stage_transactions",
                    target_table_name="transactions",
                ),
            ],
        )
    },
)
