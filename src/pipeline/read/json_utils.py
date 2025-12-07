from src.sources.base import APIEndpointConfig


def extract_items(data: dict, endpoint_config: APIEndpointConfig) -> list[dict]:
    if endpoint_config.json_entrypoint is not None:
        return data[endpoint_config.json_entrypoint]
    return data if isinstance(data, list) else [data]
