from src.sources.base import APIConfig, APIEndpointConfig, TableConfig
from src.sources.rickandmorty.models.characters import RickAndMortyCharacters

RICKANDMORTY_CONFIG = APIConfig(
    name="rickandmorty",
    base_url="https://rickandmortyapi.com/graphql",
    type="graphql",
    default_headers={
        "Content-Type": "application/json",
    },
    endpoints={
        "characters": APIEndpointConfig(
            json_entrypoint="data.characters.results",
            body={
                "query": """
                query GetCharacters($page: Int) {
                  characters(page: $page) {
                    info {
                      count
                      pages
                      next
                      prev
                    }
                    results {
                      id
                      name
                      status
                      species
                    }
                  }
                }
                """,
                "variables": {"page": 1},
            },
            tables=[
                TableConfig(data_model=RickAndMortyCharacters),
            ],
        )
    },
)
