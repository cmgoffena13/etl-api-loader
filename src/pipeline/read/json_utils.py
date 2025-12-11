from src.sources.base import APIConfig, APIEndpointConfig


def extract_items(
    data: dict, endpoint_config: APIEndpointConfig, source: APIConfig
) -> list[dict]:
    json_entrypoint = (
        endpoint_config.json_entrypoint
        if endpoint_config.json_entrypoint is not None
        else source.json_entrypoint
    )
    if json_entrypoint is not None:
        return data[json_entrypoint]
    return data if isinstance(data, list) else [data]
