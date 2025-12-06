from src.sources.jsonplaceholder.base import JSONPLACEHOLDER_CONFIG
from src.sources.registry import SourceRegistry

MASTER_SOURCE_REGISTRY = SourceRegistry()
MASTER_SOURCE_REGISTRY.add_sources([JSONPLACEHOLDER_CONFIG])
