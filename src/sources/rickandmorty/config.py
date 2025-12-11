from src.sources.base import APIConfig, APIEndpointConfig
from src.sources.rickandmorty.models.characters import RickAndMortyCharacters

RICKANDMORTY_CONFIG = APIConfig(
    name="rickandmorty",
    base_url="https://rickandmortyapi.com/graphql",
    type="graphql",
    endpoints={
        "characters": APIEndpointConfig(
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
                RickAndMortyCharacters,
            ],
        )
    },
)
