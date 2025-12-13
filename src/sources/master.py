from src.sources.dummyjson.config import DUMMYJSON_CONFIG
from src.sources.jsonplaceholder.config import JSONPLACEHOLDER_CONFIG
from src.sources.polygon.config import POLYGON_CONFIG
from src.sources.registry import SourceRegistry
from src.sources.rickandmorty.config import RICKANDMORTY_CONFIG

MASTER_SOURCE_REGISTRY = SourceRegistry()
MASTER_SOURCE_REGISTRY.add_sources(
    [JSONPLACEHOLDER_CONFIG, DUMMYJSON_CONFIG, RICKANDMORTY_CONFIG]
)
