from src.sources.base import APIConfig, APIEndpointConfig, TableConfig
from src.tests.fixtures.test_models.rest_models import TestItem

TEST_GRAPHQL_CONFIG_NO_PAGINATION = APIConfig(
    name="test_graphql_no_pagination",
    base_url="https://api.example.com/graphql",
    type="graphql",
    endpoints={
        "items": APIEndpointConfig(
            json_entrypoint="data.items",
            body={
                "query": """
                query GetItems {
                  items {
                    id
                    name
                  }
                }
                """,
            },
            tables=[
                TableConfig(data_model=TestItem),
            ],
        )
    },
)
