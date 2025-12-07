from src.sources.dummyjson.base import DUMMYJSON_CONFIG
from src.sources.jsonplaceholder.base import JSONPLACEHOLDER_CONFIG
from src.sources.polygon.base import POLYGON_CONFIG
from src.sources.registry import SourceRegistry

MASTER_SOURCE_REGISTRY = SourceRegistry()
MASTER_SOURCE_REGISTRY.add_sources(
    [JSONPLACEHOLDER_CONFIG, DUMMYJSON_CONFIG, POLYGON_CONFIG]
)
